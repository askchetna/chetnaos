"""Tests for GoalManager — Phase 4a."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class TestGoalManager(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.mkdtemp()
        self._goals_path = Path(self._tmpdir) / "goal_manager_state.json"

    def _patch_path(self):
        return patch(
            "src.chetnaos.cognition.goal_manager.memory_path",
            lambda _filename: self._goals_path,
        )

    def _manager(self):
        from src.chetnaos.cognition.goal_manager import GoalManager
        with self._patch_path():
            return GoalManager()

    def test_goal_creation(self):
        with self._patch_path():
            gm = self._manager()
            goal = gm.add_goal("Ship feature X", goal_type="USER", priority=80.0, origin="test")
            self.assertEqual(goal["goal_type"], "USER")
            self.assertEqual(goal["goal_priority"], 80.0)
            self.assertEqual(goal["goal_origin"], "test")
            self.assertEqual(goal["status"], "queued")
            self.assertIn("id", goal)

    def test_priority_queue_ordering(self):
        with self._patch_path():
            gm = self._manager()
            gm.add_goal("Low priority", priority=10.0)
            gm.add_goal("High priority", priority=90.0)
            gm.add_goal("Mid priority", priority=50.0)
            active = gm.next_goal()
            self.assertIsNotNone(active)
            self.assertEqual(active["text"], "High priority")
            status = gm.goal_status()
            self.assertEqual(status["queue_size"], 2)

    def test_next_goal_promotes_active(self):
        with self._patch_path():
            gm = self._manager()
            g = gm.add_goal("First", priority=70.0)
            active = gm.next_goal()
            self.assertEqual(active["id"], g["id"])
            self.assertEqual(active["status"], "active")
            self.assertEqual(gm.active_goal()["text"], "First")
            again = gm.next_goal()
            self.assertIsNotNone(again)
            self.assertEqual(again["id"], g["id"])

    def test_complete_goal(self):
        with self._patch_path():
            gm = self._manager()
            g = gm.add_goal("Finish task", priority=60.0)
            gm.next_goal()
            done = gm.complete_goal(g["id"])
            self.assertIsNotNone(done)
            self.assertEqual(done["status"], "completed")
            self.assertIsNone(gm.active_goal())
            stats = gm.goal_statistics()
            self.assertEqual(stats["completed"], 1)

    def test_fail_goal(self):
        with self._patch_path():
            gm = self._manager()
            g = gm.add_goal("Risky task", priority=60.0)
            gm.next_goal()
            failed = gm.fail_goal(g["id"], reason="timeout")
            self.assertIsNotNone(failed)
            self.assertEqual(failed["status"], "failed")
            self.assertEqual(failed["fail_reason"], "timeout")
            stats = gm.goal_statistics()
            self.assertEqual(stats["failed"], 1)

    def test_goal_statistics(self):
        with self._patch_path():
            gm = self._manager()
            gm.add_goal("A", goal_type="USER", priority=50.0)
            gm.add_goal("B", goal_type="EXPLORATION", priority=40.0)
            gm.next_goal()
            stats = gm.goal_statistics()
            self.assertEqual(stats["active"], 1)
            self.assertEqual(stats["queued"], 1)
            self.assertIn("USER", stats["by_type"])
            self.assertIn("EXPLORATION", stats["by_type"])

    def test_ingest_signals_deduplicates(self):
        with self._patch_path():
            gm = self._manager()
            added = gm.ingest_signals(
                purpose="Grow capabilities",
                training_goals=[{"skill": "reasoning", "suggested_training": "drill", "priority": 55}],
                curiosity_goals=[{"type": "explore", "target": "domain X", "priority": 0.6}],
                self_model_limits=["memory"],
                founder_context={"primary_mission": "Build OpticalOS", "founder_goals": [{"goal": "Launch MVP", "priority": 70}]},
            )
            self.assertGreaterEqual(added, 1)
            added_again = gm.ingest_signals(purpose="Grow capabilities")
            self.assertEqual(added_again, 0)

    def test_persistence_round_trip(self):
        with self._patch_path():
            gm1 = self._manager()
            gm1.add_goal("Persist me", priority=75.0)
            gm1.next_goal()
        with self._patch_path():
            gm2 = self._manager()
            self.assertIsNotNone(gm2.active_goal())
            self.assertEqual(gm2.active_goal()["text"], "Persist me")


if __name__ == "__main__":
    unittest.main()
