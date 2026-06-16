"""Tests for BeliefRevisionEngine — Phase 4b."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class _FakeBeliefs:
    def __init__(self, beliefs):
        self._beliefs = beliefs

    def apply_confidence_deltas(self, deltas, reason="evidence_revision"):
        applied = 0
        changes = []
        for b in self._beliefs:
            bid = b.get("id")
            if bid not in deltas:
                continue
            old = float(b.get("confidence", 0.5))
            b["confidence"] = round(max(0.05, min(0.99, old + float(deltas[bid]))), 3)
            changes.append({"belief_id": bid, "old_confidence": old, "new_confidence": b["confidence"], "delta": deltas[bid]})
            applied += 1
        return changes


class TestBeliefRevisionEngine(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.mkdtemp()
        self._state_path = Path(self._tmpdir) / "belief_revision_state.json"
        self._sample_beliefs = [
            {"id": 1, "text": "Truth is more valuable than comfort.", "confidence": 0.95, "source": "constitution"},
            {"id": 2, "text": "Users deserve accurate information.", "confidence": 0.80, "source": "learning"},
        ]

    def _patch_path(self):
        return patch(
            "src.chetnaos.cognition.belief_revision.memory_path",
            lambda _filename: self._state_path,
        )

    def _engine(self):
        from src.chetnaos.cognition.belief_revision import BeliefRevisionEngine
        with self._patch_path():
            return BeliefRevisionEngine()

    def test_evidence_accumulation(self):
        with self._patch_path():
            eng = self._engine()
            r1 = eng.observe(
                beliefs=self._sample_beliefs,
                reflection={"quality": "good"},
                reality={"confidence": 0.8},
                learning={"lessons": [{"lesson": "accuracy matters", "quality": "good"}]},
            )
            self.assertGreater(r1["observed_items"], 0)
            r2 = eng.observe(
                beliefs=self._sample_beliefs,
                reflection={"quality": "fair"},
                reality={"confidence": 0.5},
            )
            self.assertEqual(r2["pending_batches"], 2)

    def test_confidence_update_gradual(self):
        with self._patch_path():
            eng = self._engine()
            fake = _FakeBeliefs([dict(b) for b in self._sample_beliefs])
            eng.observe(
                beliefs=fake._beliefs,
                reflection={"quality": "good"},
                reality={"confidence": 0.9},
            )
            eng.evaluate()
            before = fake._beliefs[0]["confidence"]
            result = eng.revise(fake)
            after = fake._beliefs[0]["confidence"]
            self.assertGreater(result["revisions_applied"], 0)
            self.assertLessEqual(abs(after - before), 0.05)

    def test_beliefs_never_instant_flip(self):
        with self._patch_path():
            eng = self._engine()
            fake = _FakeBeliefs([dict(b) for b in self._sample_beliefs])
            eng.observe(
                beliefs=fake._beliefs,
                reflection={"quality": "poor"},
                reality={"confidence": 0.1},
                external_contradictions=[{
                    "belief_a": "Truth is valuable",
                    "belief_b": "Truth is false",
                    "conflict_score": 80,
                }],
            )
            eng.evaluate()
            before = fake._beliefs[0]["confidence"]
            eng.revise(fake)
            after = fake._beliefs[0]["confidence"]
            self.assertGreaterEqual(after, 0.05)
            self.assertGreater(before - after, 0)
            self.assertLessEqual(before - after, 0.05)

    def test_contradiction_handling(self):
        with self._patch_path():
            eng = self._engine()
            eng.observe(
                beliefs=self._sample_beliefs,
                external_contradictions=[{
                    "belief_a": "easy task",
                    "belief_b": "difficult task",
                    "conflict_score": 60,
                }],
            )
            contras = eng.contradictions()
            self.assertGreater(len(contras), 0)

    def test_belief_history(self):
        with self._patch_path():
            eng = self._engine()
            fake = _FakeBeliefs([dict(b) for b in self._sample_beliefs])
            eng.observe(beliefs=fake._beliefs, reflection={"quality": "good"}, reality={"confidence": 0.8})
            eng.evaluate()
            eng.revise(fake)
            history = eng.history()
            self.assertGreater(len(history), 0)
            self.assertIn("delta", history[-1])

    def test_stability_and_statistics(self):
        with self._patch_path():
            eng = self._engine()
            eng.observe(beliefs=self._sample_beliefs, reflection={"quality": "good"}, reality={"confidence": 0.7})
            eng.evaluate()
            stats = eng.statistics()
            self.assertIn("avg_stability", stats)
            self.assertIn("identity_signal", stats)
            self.assertFalse(stats["identity_signal"].get("touch_identity", True))

    def test_repeated_evidence_stronger_update(self):
        with self._patch_path():
            eng = self._engine()
            fake = _FakeBeliefs([dict(b) for b in self._sample_beliefs])
            for _ in range(3):
                eng.observe(
                    beliefs=fake._beliefs,
                    reflection={"quality": "good"},
                    reality={"confidence": 0.85},
                )
                eng.evaluate()
                eng.revise(fake)
            history = eng.history()
            self.assertGreaterEqual(len(history), 2)

    def test_persistence_round_trip(self):
        with self._patch_path():
            eng1 = self._engine()
            eng1.observe(beliefs=self._sample_beliefs, reflection={"quality": "good"}, reality={"confidence": 0.7})
            eng1.evaluate()
        with self._patch_path():
            eng2 = self._engine()
            stats = eng2.statistics()
            self.assertGreater(stats["pending_evidence_batches"], 0)


if __name__ == "__main__":
    unittest.main()
