"""Tests for CuriosityDrive — Phase 3c."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class TestCuriosityDrive(unittest.TestCase):
    def test_novelty_and_exploration_goals(self):
        from src.chetnaos.cognition.curiosity import CuriosityDrive

        cd = CuriosityDrive()
        score = cd.novelty_score("science", ["Why is the sky blue?"])
        self.assertGreater(score, 0.5)
        goals = cd.exploration_goals(
            domain="science",
            workspace_questions=["Why is the sky blue?"],
            uncertainty=0.6,
        )
        self.assertGreater(len(goals), 0)
        self.assertEqual(goals[0]["type"], "answer_question")

    def test_next_question(self):
        from src.chetnaos.cognition.curiosity import CuriosityDrive

        cd = CuriosityDrive()
        q = cd.next_question(["First question", "Second"])
        self.assertEqual(q, "First question")

    def test_poor_quality_goal(self):
        from src.chetnaos.cognition.curiosity import CuriosityDrive

        cd = CuriosityDrive()
        goals = cd.exploration_goals(
            domain="general", poor_quality=True, uncertainty=0.3,
        )
        types = [g["type"] for g in goals]
        self.assertIn("improve_quality", types)


if __name__ == "__main__":
    unittest.main()
