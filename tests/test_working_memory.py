"""Tests for WorkingMemory — Phase 3c."""
from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class TestWorkingMemory(unittest.TestCase):
    def test_push_recall_clear(self):
        from src.chetnaos.memory.working_memory import WorkingMemory

        wm = WorkingMemory(capacity=3)
        wm.push({"input": "a"}, attention_weight=0.5)
        wm.push({"input": "b"}, attention_weight=0.9)
        wm.push({"input": "c"}, attention_weight=0.3)
        recalled = wm.recall()
        self.assertEqual(len(recalled), 3)
        self.assertEqual(recalled[0]["input"], "b")
        wm.clear()
        self.assertEqual(wm.recall(), [])

    def test_eviction_drops_lowest_attention(self):
        from src.chetnaos.memory.working_memory import WorkingMemory

        wm = WorkingMemory(capacity=2)
        wm.push({"input": "low"}, attention_weight=0.1)
        wm.push({"input": "high"}, attention_weight=0.9)
        wm.push({"input": "mid"}, attention_weight=0.5)
        inputs = [r["input"] for r in wm.recall()]
        self.assertNotIn("low", inputs)
        self.assertIn("high", inputs)

    def test_capacity_and_health(self):
        from src.chetnaos.memory.working_memory import WorkingMemory

        wm = WorkingMemory(capacity=5)
        self.assertEqual(wm.capacity(), 5)
        wm.push({"x": 1}, attention_weight=0.6)
        health = wm.health()
        self.assertEqual(health["count"], 1)
        self.assertGreater(health["avg_attention_weight"], 0)


if __name__ == "__main__":
    unittest.main()
