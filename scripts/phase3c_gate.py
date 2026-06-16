"""Phase 3c gate: cognitive organs + baseline preservation."""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class TestPhase3cCognitiveOrgans(unittest.TestCase):
    def test_cycle_has_four_organs(self):
        from src.chetnaos.cycle.cognitive_cycle import CognitiveCycle

        cycle = CognitiveCycle()
        self.assertIsNotNone(cycle.working_memory)
        self.assertIsNotNone(cycle.self_model)
        self.assertIsNotNone(cycle.curiosity)
        self.assertIsNotNone(cycle.emotion)
        self.assertIsNotNone(cycle.executive)

    def test_executive_unchanged_pipeline(self):
        from src.chetnaos.cognition.executive import EXECUTION_PIPELINE
        self.assertEqual(len(EXECUTION_PIPELINE), 25)

    def test_memory_still_locked(self):
        from src.chetnaos.memory.locked import LOCKED, MEMORY_ARCHITECTURE_VERSION
        self.assertTrue(LOCKED)
        self.assertEqual(MEMORY_ARCHITECTURE_VERSION, "2.5")

    def test_organ_imports(self):
        from src.chetnaos.memory.working_memory import WorkingMemory
        from src.chetnaos.cognition.self_model import SelfModel
        from src.chetnaos.cognition.curiosity import CuriosityDrive
        from src.chetnaos.cognition.emotion import EmotionalState
        self.assertTrue(callable(WorkingMemory))
        self.assertTrue(callable(SelfModel))
        self.assertTrue(callable(CuriosityDrive))
        self.assertTrue(callable(EmotionalState))


class TestPhase3cApiHealth(unittest.TestCase):
    def test_health_endpoint(self):
        from fastapi.testclient import TestClient
        from backend.app import app

        client = TestClient(app)
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get("ok"))


def main() -> int:
    print("=== Phase 3c Gate ===\n")

    print("--- Phase 3a baseline ---")
    p3a = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "phase3a_gate.py")],
        cwd=str(ROOT),
    )
    if p3a.returncode != 0:
        print("FAIL: Phase 3a baseline regressed")
        return 1

    print("\n--- Cognitive organ tests ---")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for pattern in (
        "test_working_memory.py",
        "test_self_model.py",
        "test_curiosity.py",
        "test_emotion.py",
    ):
        suite.addTests(loader.discover("tests", pattern=pattern))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase3cCognitiveOrgans))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase3cApiHealth))
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    print("\n--- Phase 3c Gate Summary ---")
    ok = result.wasSuccessful()
    print(f"Phase 3a baseline:      {'PASS' if p3a.returncode == 0 else 'FAIL'}")
    print(f"Memory locked:          {'PASS' if ok else 'FAIL'}")
    print(f"Executive intact:       {'PASS' if ok else 'FAIL'}")
    print(f"Cognitive organs:       {'PASS' if ok else 'FAIL'}")
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
