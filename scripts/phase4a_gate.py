"""Phase 4a gate: GoalManager + baseline preservation."""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class TestPhase4aGoalManager(unittest.TestCase):
    def test_cycle_has_goal_manager(self):
        from src.chetnaos.cycle.cognitive_cycle import CognitiveCycle

        cycle = CognitiveCycle()
        self.assertIsNotNone(cycle.goal_manager)
        self.assertIsNotNone(cycle.executive)
        self.assertIsNotNone(cycle.working_memory)
        self.assertIsNotNone(cycle.self_model)
        self.assertIsNotNone(cycle.curiosity)
        self.assertIsNotNone(cycle.emotion)

    def test_goal_manager_imports(self):
        from src.chetnaos.cognition.goal_manager import GoalManager, GoalType

        self.assertTrue(callable(GoalManager))
        self.assertEqual(GoalType.USER.value, "USER")
        self.assertEqual(GoalType.INTRINSIC.value, "INTRINSIC")
        self.assertEqual(GoalType.TRAINING.value, "TRAINING")
        self.assertEqual(GoalType.EXPLORATION.value, "EXPLORATION")
        self.assertEqual(GoalType.MAINTENANCE.value, "MAINTENANCE")

    def test_goal_manager_api_surface(self):
        from src.chetnaos.cognition.goal_manager import GoalManager

        gm = GoalManager()
        for method in (
            "add_goal",
            "next_goal",
            "complete_goal",
            "fail_goal",
            "active_goal",
            "goal_status",
            "goal_statistics",
            "ingest_signals",
        ):
            self.assertTrue(callable(getattr(gm, method)))

    def test_executive_unchanged_pipeline(self):
        from src.chetnaos.cognition.executive import EXECUTION_PIPELINE

        self.assertEqual(len(EXECUTION_PIPELINE), 25)

    def test_memory_still_locked(self):
        from src.chetnaos.memory.locked import LOCKED, MEMORY_ARCHITECTURE_VERSION

        self.assertTrue(LOCKED)
        self.assertEqual(MEMORY_ARCHITECTURE_VERSION, "2.5")

    def test_dashboard_exposes_goal_manager(self):
        from src.chetnaos.cycle.cognitive_cycle import CognitiveCycle

        snap = CognitiveCycle().dashboard_snapshot()
        organs = snap.get("cognitive_organs", {})
        self.assertIn("goal_manager", organs)


class TestPhase4aApiHealth(unittest.TestCase):
    def test_health_endpoint(self):
        from fastapi.testclient import TestClient
        from backend.app import app

        client = TestClient(app)
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get("ok"))


def main() -> int:
    print("=== Phase 4a Gate ===\n")

    print("--- Phase 3c baseline ---")
    p3c = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "phase3c_gate.py")],
        cwd=str(ROOT),
    )
    if p3c.returncode != 0:
        print("FAIL: Phase 3c baseline regressed")
        return 1

    print("\n--- GoalManager tests ---")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.discover("tests", pattern="test_goal_manager.py"))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase4aGoalManager))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase4aApiHealth))
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    print("\n--- Phase 4a Gate Summary ---")
    ok = result.wasSuccessful()
    print(f"Phase 3c baseline:      {'PASS' if p3c.returncode == 0 else 'FAIL'}")
    print(f"Memory locked:          {'PASS' if ok else 'FAIL'}")
    print(f"Executive intact:       {'PASS' if ok else 'FAIL'}")
    print(f"GoalManager imports:    {'PASS' if ok else 'FAIL'}")
    print(f"Cognitive cycle:        {'PASS' if ok else 'FAIL'}")
    print(f"API health:             {'PASS' if ok else 'FAIL'}")

    try:
        import urllib.request

        with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=2) as resp:
            print(f"Live smoke (/health):   {'PASS' if resp.status == 200 else 'FAIL'}")
    except Exception:
        print("Live smoke (/health):   SKIP (no server on :8000)")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
