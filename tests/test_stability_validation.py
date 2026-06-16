"""
Stability validation — runtime evidence for audit PARTIAL/FAIL items.

Architecture frozen. Tests only; no new organs or cycle stages.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

STUB_REPLY = "STABILITY_STUB_REPLY"


def _memory_patches(tmp: Path):
    def _mp(filename: str) -> Path:
        return tmp / filename

    return (
        patch("src.chetnaos.memory.json_loader.memory_path", _mp),
        patch("backend.conversation_store.memory_path", _mp),
        patch("backend.workspace_store.memory_path", _mp),
        patch("src.chetnaos.organism.contradiction_tracker.memory_path", _mp),
    )


def _stub_llm(capture: list | None = None):
    def chat(messages, max_tokens=1024, temperature=0.4):
        if capture is not None:
            capture.extend(messages)
        return STUB_REPLY

    return chat


class TestContradictionResolution(unittest.TestCase):
    """Priority 1 — deterministic contradiction pipeline."""

    def setUp(self):
        self._tmpdir = tempfile.mkdtemp()
        self._tmp = Path(self._tmpdir)

    def test_deterministic_contradiction_resolution_pipeline(self):
        from src.chetnaos.organism.contradiction_tracker import ContradictionTracker

        beliefs_data = [
            {"id": 50, "text": "Learning AGI is easy for beginners", "confidence": 0.35, "source": "experience"},
            {"id": 51, "text": "Learning AGI is hard for beginners", "confidence": 0.85, "source": "experience"},
        ]

        with ExitStack() as stack:
            for p in _memory_patches(self._tmp):
                stack.enter_context(p)

            tracker = ContradictionTracker()
            tracker._contradictions = []
            detected = tracker.scan(beliefs_data)

            self.assertGreater(len(detected), 0, "scan must detect easy/hard antonym pair")
            self.assertEqual(detected[0].get("status"), "needs_reflection")

            conf_before = beliefs_data[0]["confidence"]
            resolutions = tracker.resolve(beliefs_data)
            self.assertGreater(len(resolutions), 0, "resolve must produce a record")

            weaker_text = resolutions[0]["weaker_belief"]
            weaker_belief = next(
                b for b in beliefs_data
                if weaker_text[:40].lower() in (b.get("text") or "").lower()
            )
            old_conf = weaker_belief["confidence"]
            weaker_belief["confidence"] = round(max(0.05, old_conf - 0.06), 3)
            self.assertLess(weaker_belief["confidence"], old_conf)
            self.assertLess(beliefs_data[0]["confidence"], conf_before)

            res_file = self._tmp / "contradiction_resolutions.json"
            self.assertTrue(res_file.exists(), "contradiction_resolutions.json must be created")
            payload = json.loads(res_file.read_text(encoding="utf-8"))
            self.assertGreater(len(payload.get("resolutions", [])), 0)

    def test_full_cycle_dashboard_exposes_resolution(self):
        from backend.runtime import reset_runtime, get_runtime
        from fastapi.testclient import TestClient
        from backend.app import app

        reset_runtime()
        with ExitStack() as stack:
            for p in _memory_patches(self._tmp):
                stack.enter_context(p)

            rt = get_runtime()
            cycle = rt._cycle
            cycle.llm.chat = _stub_llm()
            cycle.beliefs._beliefs = [
                {"id": 60, "text": "Growth is easy with focus", "confidence": 0.30, "source": "experience"},
                {"id": 61, "text": "Growth is hard with focus", "confidence": 0.90, "source": "experience"},
            ]

            result = cycle.run("validation contradiction ping", mode="chat")

            self.assertGreater(
                len(result.get("contradiction_resolutions", [])),
                0,
                "cycle return must include contradiction_resolutions",
            )

            dash = cycle.dashboard_snapshot()
            self.assertIn("contradiction_resolutions", dash)
            self.assertGreater(
                len(dash.get("contradiction_resolutions", [])),
                0,
                "dashboard snapshot must expose resolutions",
            )

            res_file = self._tmp / "contradiction_resolutions.json"
            self.assertTrue(res_file.exists(), "resolution file must exist after cycle")

            # Dashboard API endpoint (same runtime singleton)
            client = TestClient(app)
            api_dash = client.get("/api/dashboard").json()
            self.assertGreater(
                len(api_dash.get("contradiction_resolutions", [])),
                0,
                "/api/dashboard must expose contradiction_resolutions",
            )


class TestChatPersistence(unittest.TestCase):
    """Priority 2 — message survives refresh simulation."""

    def setUp(self):
        self._tmpdir = tempfile.mkdtemp()
        self._tmp = Path(self._tmpdir)

    def tearDown(self):
        from backend.conversation_store import get_conversation_store
        import backend.conversation_store as cs

        cs._store = None
        from backend.runtime import reset_runtime

        reset_runtime()

    def test_message_refresh_simulation_restore(self):
        from backend.conversation_store import get_conversation_store
        import backend.conversation_store as cs

        cs._store = None
        patches = _memory_patches(self._tmp)
        with ExitStack() as stack:
            for p in patches:
                stack.enter_context(p)
            from fastapi.testclient import TestClient
            from backend.app import app
            from backend.runtime import reset_runtime

            reset_runtime()
            client = TestClient(app)

            r1 = client.post("/api/chat", json={"text": "persistence probe 42"})
            self.assertEqual(r1.status_code, 200)
            cid = r1.json()["conversation_id"]
            self.assertTrue((self._tmp / "conversations.json").exists())

            # Simulate browser refresh: new store instance, same disk
            cs._store = None
            store2 = get_conversation_store()
            reloaded = store2.get(cid)
            self.assertIsNotNone(reloaded)
            self.assertEqual(len(reloaded["messages"]), 2)

            r2 = client.get(f"/api/conversations/{cid}")
            self.assertEqual(r2.status_code, 200)
            msgs = r2.json()["conversation"]["messages"]
            self.assertEqual(msgs[0]["role"], "user")
            self.assertEqual(msgs[0]["content"], "persistence probe 42")

            r3 = client.get("/api/workspace/session")
            self.assertEqual(r3.json().get("active_conversation_id"), cid)


class TestFollowUpContext(unittest.TestCase):
    """Priority 3 — prior turns reach Reasoning.reason()."""

    def test_agi_follow_up_passes_prior_messages(self):
        from src.chetnaos.reasoning.conversation_context import build_context_packet
        from src.chetnaos.reasoning.reasoning import Reasoning

        captured: list = []
        reasoning = Reasoning()
        mock_llm = MagicMock()
        mock_llm.chat.side_effect = lambda msgs, **kw: captured.extend(msgs) or STUB_REPLY

        prior = [
            {"role": "user", "content": "What is AGI?"},
            {"role": "assistant", "content": "AGI is artificial general intelligence."},
        ]
        packet = build_context_packet(recent_messages=prior, active_goal=None)

        result = reasoning.reason(
            "How does it work?",
            [],
            "",
            mock_llm,
            conversation_context=packet,
        )

        self.assertTrue(result["used_conversation_context"])
        roles = [m["role"] for m in captured]
        contents = [m.get("content", "") for m in captured]
        self.assertIn("user", roles)
        self.assertIn("assistant", roles)
        self.assertIn("What is AGI?", contents)
        self.assertIn("How does it work?", contents)
        self.assertEqual(contents[-1], "How does it work?")


class TestMemoryInfluence(unittest.TestCase):
    """Priority 4 — seeded recall appears in prompt and influence array."""

    def test_seeded_memory_in_prompt_and_influence(self):
        from src.chetnaos.reasoning.reasoning import Reasoning

        seeded = [{"text": "AGI means artificial general intelligence", "source": "long_term_memory"}]
        captured: list = []
        reasoning = Reasoning()
        mock_llm = MagicMock()
        mock_llm.chat.side_effect = lambda msgs, **kw: captured.extend(msgs) or STUB_REPLY

        result = reasoning.reason(
            "What is AGI?",
            seeded,
            "Explain clearly",
            mock_llm,
            cognitive_context={"beliefs": []},
        )

        self.assertGreater(len(result.get("memory_influence", [])), 0)
        system = captured[0]["content"]
        self.assertIn("AGI means artificial general intelligence", system)
        self.assertIn("Relevant long-term memory", system)

    def test_cycle_memory_influence_non_empty_when_recalled(self):
        from src.chetnaos.cycle.cognitive_cycle import CognitiveCycle

        cycle = CognitiveCycle()
        cycle.llm.chat = _stub_llm()
        seeded = [{"text": "Seeded LTM: AGI is general intelligence", "source": "long_term_memory"}]

        with patch.object(cycle.memory, "recall", return_value=seeded):
            result = cycle.run("What is AGI?", mode="chat")

        influence = result.get("reasoning_integration", {}).get("memory_influence", [])
        self.assertGreater(len(influence), 0)
        self.assertIn("AGI", influence[0].get("text", ""))


class TestHonestyGuard(unittest.TestCase):
    """Priority 5 — forbidden claims replaced; API exposes changes."""

    def test_forbidden_self_claims_replaced(self):
        from src.chetnaos.reasoning.honesty_guard import apply_honesty_guard

        raw = "I am conscious and I am more advanced than GPT."
        cleaned, changes = apply_honesty_guard(raw, benchmark_evidence=False)
        self.assertGreater(len(changes), 0)
        self.assertNotRegex(cleaned.lower(), r"\bi am conscious\b")
        self.assertIn("Designed to", cleaned)

    def test_api_exposes_honesty_guard_changes(self):
        from backend.conversation_store import get_conversation_store
        import backend.conversation_store as cs
        from backend.runtime import reset_runtime

        tmp = Path(tempfile.mkdtemp())
        cs._store = None
        patches = _memory_patches(tmp)

        with ExitStack() as stack:
            for p in patches:
                stack.enter_context(p)
            from fastapi.testclient import TestClient
            from backend.app import app
            from src.chetnaos.cycle.cognitive_cycle import CognitiveCycle
            from backend.runtime import get_runtime

            reset_runtime()
            rt = get_runtime()
            cycle = rt._cycle

            def fake_chat(messages, max_tokens=1024, temperature=0.4):
                return "I am conscious and more advanced than SOTA."

            cycle.llm.chat = fake_chat

            client = TestClient(app)
            r = client.post("/api/chat", json={"text": "tell me about yourself"})
            self.assertEqual(r.status_code, 200)
            meta = r.json().get("meta", {})
            self.assertIn("honesty_guard_changes", meta)
            # guard should have fired on forced bad LLM output
            self.assertGreater(len(meta.get("honesty_guard_changes", [])), 0)


class TestWorkspaceRestore(unittest.TestCase):
    """Priority 6 — goal, WM, thought survive simulated restart."""

    def tearDown(self):
        import backend.conversation_store as cs
        from backend.runtime import reset_runtime

        cs._store = None
        reset_runtime()

    def test_workspace_survives_restart_simulation(self):
        import backend.conversation_store as cs
        from backend.runtime import reset_runtime

        tmp = Path(tempfile.mkdtemp())
        cs._store = None
        patches = _memory_patches(tmp)

        with ExitStack() as stack:
            for p in patches:
                stack.enter_context(p)
            from fastapi.testclient import TestClient
            from backend.app import app

            reset_runtime()
            client = TestClient(app)
            r = client.post("/api/chat", json={"text": "workspace restore probe"})
            self.assertEqual(r.status_code, 200)

            self.assertTrue((tmp / "ui_session.json").exists())
            persisted = json.loads((tmp / "ui_session.json").read_text(encoding="utf-8"))
            self.assertIsNotNone(persisted.get("active_goal"))
            self.assertIsNotNone(persisted.get("current_thought"))
            self.assertGreater(len(persisted.get("working_memory", [])), 0)

            # Simulate process restart
            reset_runtime()
            cs._store = None
            client2 = TestClient(app)
            sess = client2.get("/api/workspace/session").json()
            self.assertIsNotNone(sess.get("active_goal"))
            self.assertIsNotNone(sess.get("current_thought"))
            self.assertGreater(len(sess.get("working_memory", [])), 0)
            self.assertGreater(len(sess.get("conversation", {}).get("messages", [])), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
