"""Phase 3a gate: ExecutiveController extraction + baseline preservation."""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class TestPhase3aImports(unittest.TestCase):
    def test_executive_imports(self):
        from src.chetnaos.cognition.executive import ExecutiveController, EXECUTION_PIPELINE
        from src.chetnaos.cognition import ExecutiveController as EC2
        self.assertTrue(callable(ExecutiveController))
        self.assertEqual(ExecutiveController, EC2)
        self.assertEqual(len(EXECUTION_PIPELINE), 25)

    def test_cognitive_cycle_imports(self):
        from src.chetnaos.cycle.cognitive_cycle import CognitiveCycle
        cycle = CognitiveCycle()
        self.assertIsNotNone(cycle.executive)

    def test_memory_still_locked(self):
        from src.chetnaos.memory.locked import LOCKED, MEMORY_ARCHITECTURE_VERSION
        self.assertTrue(LOCKED)
        self.assertEqual(MEMORY_ARCHITECTURE_VERSION, "2.5")


class TestPhase3aPipeline(unittest.TestCase):
    def test_pipeline_core_stages_present(self):
        from src.chetnaos.cognition.executive import ExecutiveController
        pipeline = ExecutiveController().pipeline_order()
        for stage in (
            "OBSERVE", "ATTEND", "RECALL", "ACT", "REALITY_CHECK",
            "EVALUATE", "FAILURE_RECOVERY", "REFLECT", "UPDATE_BELIEFS",
            "SLEEP",
        ):
            self.assertIn(stage, pipeline)


class TestPhase3aApiHealth(unittest.TestCase):
    def test_health_endpoint(self):
        from fastapi.testclient import TestClient
        from backend.app import app

        client = TestClient(app)
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get("ok"))


def main() -> int:
    print("=== Phase 3a Gate ===\n")

    print("--- Phase 2.5 baseline ---")
    p25 = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "phase25_gate.py")],
        cwd=str(ROOT),
    )
    if p25.returncode != 0:
        print("FAIL: Phase 2.5 baseline regressed")
        return 1

    print("\n--- Executive controller tests ---")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.discover("tests", pattern="test_executive_controller.py"))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase3aImports))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase3aPipeline))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase3aApiHealth))
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    print("\n--- Phase 3a Gate Summary ---")
    ok = result.wasSuccessful()
    print(f"Phase 2.5 baseline:     {'PASS' if p25.returncode == 0 else 'FAIL'}")
    print(f"Executive imports:      {'PASS' if ok else 'FAIL'}")
    print(f"Cognitive cycle:        {'PASS' if ok else 'FAIL'}")
    print(f"Memory compatibility:   {'PASS' if ok else 'FAIL'}")
    print(f"Pipeline order:         {'PASS' if ok else 'FAIL'}")
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
