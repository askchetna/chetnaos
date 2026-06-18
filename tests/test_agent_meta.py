"""Agent vs Chat runtime meta parity."""
from __future__ import annotations

import unittest
from unittest.mock import patch

from backend.api.meta import RUNTIME_META_KEYS, build_runtime_meta


def _stub_cycle_result() -> dict:
    return {
        "reply": "stub reply",
        "cycle": 42,
        "cycle_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        "stage_trace": ["EXIST", "OBSERVE", "ACT", "REFLECT"],
        "cycle_trace": [
            {
                "cycle_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
                "stage": "ACT",
                "duration_ms": 12.5,
                "confidence": 0.72,
                "memory_used": True,
                "goal_used": False,
            }
        ],
        "quality": "good",
        "confidence": 0.72,
        "confidence_level": "MEDIUM",
        "dharma_score": 80,
        "cycle_score": 75,
        "domain": "technology",
        "intent": "question",
        "beliefs_count": 5,
        "health": "healthy",
        "slept": False,
        "reality": {"passed": True, "confidence": 0.72, "level": "MEDIUM"},
        "simulation": {"plans": [{"plan": "A", "outcome": "ok"}]},
        "meta_cognition": {"why": "test", "was_correct": True, "correctness": 0.8, "can_improve": []},
        "cognitive_organs": {
            "working_memory": {"count": 3, "capacity": 7},
            "goal_manager": {
                "active_goal": {"text": "Launch ChetnaOS publicly"},
                "queue_size": 2,
            },
            "last_cycle_trace": [],
        },
        "reasoning_integration": {
            "used_working_memory": True,
            "used_active_goal": False,
            "used_beliefs": True,
            "used_conversation_context": False,
            "used_cognitive_organs": True,
            "used_agent_tool": True,
            "memory_influence": [{"text": "prior fact", "source": "recall"}],
            "belief_influence": [{"id": 1, "text": "truth", "confidence": 0.9}],
            "telemetry_guard_changes": [],
        },
        "goal_progress": {"health": "active", "actual_progress": 20.0},
        "belief_changes": [],
        "contradiction_resolutions": [],
        "agent_tool": "calc",
        "trace": [{"stage": "ACT", "honesty_guard": []}],
    }


class TestAgentChatMetaParity(unittest.TestCase):
    def test_build_runtime_meta_has_canonical_keys(self):
        meta = build_runtime_meta(_stub_cycle_result())
        self.assertEqual(set(RUNTIME_META_KEYS), set(meta.keys()))

    def test_agent_and_chat_meta_structures_match(self):
        from fastapi.testclient import TestClient
        from backend.app import app

        stub = _stub_cycle_result()

        def fake_run(self, user_input, mode="chat", **kwargs):
            out = dict(stub)
            out["agent_tool"] = "calc" if mode == "agent" else None
            ri = dict(out["reasoning_integration"])
            ri["used_agent_tool"] = mode == "agent"
            out["reasoning_integration"] = ri
            return out

        with patch("src.chetnaos.cycle.cognitive_cycle.CognitiveCycle.run", fake_run):
            client = TestClient(app)
            chat_resp = client.post("/api/chat", json={"text": "hello chat"})
            agent_resp = client.post("/api/agent", json={"text": "calc: 2+2"})

        self.assertEqual(chat_resp.status_code, 200)
        self.assertEqual(agent_resp.status_code, 200)

        chat_meta = chat_resp.json().get("meta") or {}
        agent_meta = agent_resp.json().get("meta") or {}

        self.assertEqual(set(chat_meta.keys()), set(RUNTIME_META_KEYS))
        self.assertEqual(set(agent_meta.keys()), set(RUNTIME_META_KEYS))
        self.assertEqual(set(chat_meta.keys()), set(agent_meta.keys()))

        for key in RUNTIME_META_KEYS:
            self.assertIn(key, chat_meta)
            self.assertIn(key, agent_meta)

        self.assertEqual(chat_meta["cycle_id"], agent_meta["cycle_id"])
        self.assertEqual(chat_meta["stage_trace"], agent_meta["stage_trace"])
        self.assertIsInstance(agent_meta["cycle_trace"], list)
        self.assertEqual(agent_meta["agent_tool"], "calc")
        self.assertIsNone(chat_meta["agent_tool"])


if __name__ == "__main__":
    unittest.main()
