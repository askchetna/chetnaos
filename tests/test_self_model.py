"""Tests for SelfModel — Phase 3c."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class TestSelfModel(unittest.TestCase):
    def test_update_and_capability_map(self):
        from src.chetnaos.cognition.self_model import SelfModel

        sm = SelfModel()
        sm.update(
            skills={"Coding": {"score": 0.8}, "Sales": {"score": 0.3}},
            development={"total_cycles": 10, "good_cycles": 7},
            meta_cognition={"correctness": 75},
            reality_confidence=0.7,
        )
        caps = sm.capability_map()
        self.assertAlmostEqual(caps["Coding"], 0.8)
        self.assertIn("Sales", sm.known_limits())
        self.assertGreater(sm.self_confidence(), 0)

    def test_snapshot(self):
        from src.chetnaos.cognition.self_model import SelfModel

        sm = SelfModel()
        sm.update(skills={"Research": {"score": 0.9}})
        snap = sm.snapshot()
        self.assertIn("capability_map", snap)
        self.assertIn("self_confidence", snap)


if __name__ == "__main__":
    unittest.main()
