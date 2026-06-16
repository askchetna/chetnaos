"""Tests for DECIDE stage + CycleTrace (Phase 7C)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class TestDecideAndTrace(unittest.TestCase):
    def test_decide_stage_in_trace(self):
        from src.chetnaos.cycle.cognitive_cycle import CognitiveCycle

        cycle = CognitiveCycle()
        with patch.object(cycle.llm, "chat", return_value="stub reply"):
            with patch.object(cycle.reflection, "reflect", return_value={
                "quality": "good",
                "dharma_score": 0.8,
                "cycle_score": 0.8,
            }):
                result = cycle.run("decide stage validation", mode="chat")

        self.assertIn("DECIDE", result.get("stage_trace", []))
        self.assertIn("cycle_id", result)
        trace = result.get("cycle_trace") or []
        self.assertTrue(any(t.get("stage") == "DECIDE" for t in trace))
        decide_rows = [t for t in trace if t.get("stage") == "DECIDE"]
        self.assertTrue(decide_rows[0].get("duration_ms") is not None)

    def test_embodiment_produces_final_output(self):
        from src.chetnaos.organs.embodiment import Embodiment
        from src.chetnaos.organs.decision import Decision

        dec = Decision().decide({"response": "hello"}, {"confidence": 0.9, "passed": True})
        emb = Embodiment().act(dec, {"intent": "statement"})
        self.assertEqual(emb["output"], "hello")
        self.assertTrue(emb.get("executed"))


if __name__ == "__main__":
    unittest.main()
