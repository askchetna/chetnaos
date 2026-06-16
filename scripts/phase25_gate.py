"""Phase 2.5 gate: locked memory architecture + full validation coverage."""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class TestPhase25MemoryLock(unittest.TestCase):
    def test_architecture_locked(self):
        from src.chetnaos.memory.locked import LOCKED, MEMORY_ARCHITECTURE_VERSION
        self.assertTrue(LOCKED)
        self.assertEqual(MEMORY_ARCHITECTURE_VERSION, "2.5")

    def test_single_memory_store_singleton(self):
        from src.chetnaos.memory.store import get_memory_store
        a = get_memory_store()
        b = get_memory_store()
        self.assertIs(a, b)

    def test_schema_coverage_complete(self):
        from src.chetnaos.memory.validation import VALIDATORS
        expected = {
            "identity.json", "beliefs.json", "purpose.json", "skills.json",
            "workspace_state.json", "habits.json", "development.json",
            "relationships.json", "training_goals.json", "contradictions.json",
            "mem_hierarchy.json",
        }
        self.assertEqual(set(VALIDATORS.keys()), expected)


class TestPhase25HealthReport(unittest.TestCase):
    def test_health_report_all_json_valid(self):
        from src.chetnaos.memory.health import report
        health = report()
        self.assertTrue(health["locked"])
        self.assertEqual(health["architecture_version"], "2.5")
        self.assertTrue(health["vector_store"]["ok"])
        self.assertEqual(health["json_validation"]["invalid_count"], 0)
        self.assertTrue(health["overall_healthy"])

    def test_health_report_lists_all_files(self):
        from src.chetnaos.memory.health import report
        health = report()
        for filename in health["coverage"]:
            with self.subTest(file=filename):
                self.assertTrue(health["json_validation"]["files"][filename]["ok"])


class TestPhase25WiredValidation(unittest.TestCase):
    def test_organism_modules_load_via_json_loader(self):
        from src.chetnaos.organism.identity import Identity
        from src.chetnaos.organism.beliefs import Beliefs
        from src.chetnaos.organism.habit import Habit
        from src.chetnaos.organism.development import Development
        from src.chetnaos.organism.relationship import Relationship
        from src.chetnaos.organism.self_trainer import SelfTrainer
        from src.chetnaos.organism.contradiction_tracker import ContradictionTracker
        from src.chetnaos.organism.memory_hierarchy import MemoryHierarchy

        self.assertEqual(Identity().get()["name"], "ChetnaOS")
        self.assertGreater(len(Beliefs().get_all()), 0)
        self.assertIsInstance(Habit()._habits, dict)
        self.assertIn("total_cycles", Development()._data)
        self.assertIn("user", Relationship()._rels)
        self.assertIsInstance(SelfTrainer().get(), list)
        self.assertIsInstance(ContradictionTracker().get(), list)
        self.assertIn("semantic_concepts", MemoryHierarchy()._state)

    def test_cognitive_cycle_still_instantiates(self):
        from src.chetnaos.cycle.cognitive_cycle import CognitiveCycle
        cycle = CognitiveCycle()
        self.assertIsNotNone(cycle.memory)
        self.assertIsNotNone(cycle.beliefs)
        self.assertIsNotNone(cycle.identity)


def main() -> int:
    print("=== Phase 2.5 Gate ===\n")

    print("--- Phase 2 baseline ---")
    p2 = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "phase2_gate.py")],
        cwd=str(ROOT),
    )
    if p2.returncode != 0:
        print("FAIL: Phase 2 baseline regressed")
        return 1

    print("\n--- Phase 2.5 tests ---")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestPhase25MemoryLock))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase25HealthReport))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase25WiredValidation))
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    print("\n--- Phase 2.5 Gate Summary ---")
    ok = result.wasSuccessful()
    print(f"Architecture locked:    {'PASS' if ok else 'FAIL'}")
    print(f"Schema coverage:        {'PASS' if ok else 'FAIL'}")
    print(f"Health report:          {'PASS' if ok else 'FAIL'}")
    print(f"Wired validation:       {'PASS' if ok else 'FAIL'}")
    print(f"Cognitive kernel:       {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
