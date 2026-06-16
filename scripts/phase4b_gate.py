"""Phase 4b gate: BeliefRevisionEngine + baseline preservation."""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class TestPhase4bBeliefRevision(unittest.TestCase):
    def test_cycle_has_belief_revision(self):
        from src.chetnaos.cycle.cognitive_cycle import CognitiveCycle

        cycle = CognitiveCycle()
        self.assertIsNotNone(cycle.belief_revision)
        self.assertIsNotNone(cycle.goal_manager)
        self.assertIsNotNone(cycle.executive)

    def test_belief_revision_imports(self):
        from src.chetnaos.cognition.belief_revision import BeliefRevisionEngine

        self.assertTrue(callable(BeliefRevisionEngine))

    def test_belief_revision_api_surface(self):
        from src.chetnaos.cognition.belief_revision import BeliefRevisionEngine

        eng = BeliefRevisionEngine()
        for method in (
            "observe",
            "evaluate",
            "revise",
            "confidence",
            "contradictions",
            "history",
            "statistics",
        ):
            self.assertTrue(callable(getattr(eng, method)))

    def test_goal_manager_intact(self):
        from src.chetnaos.cognition.goal_manager import GoalManager, GoalType

        gm = GoalManager()
        goal = gm.add_goal("test", goal_type=GoalType.USER, priority=50.0)
        self.assertIn("id", goal)

    def test_executive_unchanged_pipeline(self):
        from src.chetnaos.cognition.executive import EXECUTION_PIPELINE

        self.assertEqual(len(EXECUTION_PIPELINE), 25)

    def test_memory_still_locked(self):
        from src.chetnaos.memory.locked import LOCKED, MEMORY_ARCHITECTURE_VERSION

        self.assertTrue(LOCKED)
        self.assertEqual(MEMORY_ARCHITECTURE_VERSION, "2.5")

    def test_dashboard_exposes_belief_revision(self):
        from src.chetnaos.cycle.cognitive_cycle import CognitiveCycle

        snap = CognitiveCycle().dashboard_snapshot()
        organs = snap.get("cognitive_organs", {})
        self.assertIn("belief_revision", organs)
        self.assertIn("goal_manager", organs)


class TestPhase4bApiHealth(unittest.TestCase):
    def test_health_endpoint(self):
        from fastapi.testclient import TestClient
        from backend.app import app

        client = TestClient(app)
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get("ok"))


def main() -> int:
    print("=== Phase 4b Gate ===\n")

    print("--- Phase 4a baseline ---")
    p4a = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "phase4a_gate.py")],
        cwd=str(ROOT),
    )
    if p4a.returncode != 0:
        print("FAIL: Phase 4a baseline regressed")
        return 1

    print("\n--- BeliefRevision tests ---")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.discover("tests", pattern="test_belief_revision.py"))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase4bBeliefRevision))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase4bApiHealth))
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    print("\n--- Phase 4b Gate Summary ---")
    ok = result.wasSuccessful()
    print(f"Phase 4a baseline:        {'PASS' if p4a.returncode == 0 else 'FAIL'}")
    print(f"Memory locked:            {'PASS' if ok else 'FAIL'}")
    print(f"Executive locked:         {'PASS' if ok else 'FAIL'}")
    print(f"GoalManager intact:       {'PASS' if ok else 'FAIL'}")
    print(f"BeliefRevision imports:   {'PASS' if ok else 'FAIL'}")
    print(f"Pipeline unchanged:       {'PASS' if ok else 'FAIL'}")
    print(f"Cognitive cycle:          {'PASS' if ok else 'FAIL'}")
    print(f"API health:               {'PASS' if ok else 'FAIL'}")

    try:
        import urllib.request

        with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=2) as resp:
            print(f"Live smoke (/health):     {'PASS' if resp.status == 200 else 'FAIL'}")
    except Exception:
        print("Live smoke (/health):     SKIP (no server on :8000)")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
