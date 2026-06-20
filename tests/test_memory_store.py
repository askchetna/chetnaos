"""Phase 2 memory subsystem tests."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ.setdefault("LIGHT_MODE", "true")
os.environ.setdefault("EMBEDDINGS_ENABLED", "false")

MEMORY_DIR = ROOT / "memory"


class TestMemoryStore(unittest.TestCase):
    def test_upsert_search_recent_delete_statistics(self):
        from memory.db import MemoryDB
        from src.chetnaos.memory.store import MemoryStore

        tmp = tempfile.mkdtemp()
        db_path = os.path.join(tmp, "store_test.db")
        try:
            store = MemoryStore(db=MemoryDB(db_path=db_path))
            row_id = store.upsert("hello organism", meta={"category": "test"})
            self.assertGreater(row_id, 0)

            recent = store.recent(5)
            self.assertEqual(len(recent), 1)
            self.assertEqual(recent[0]["text"], "hello organism")
            self.assertIn("created_at", recent[0])

            stats = store.statistics()
            self.assertEqual(stats["total"], 1)
            self.assertEqual(stats["with_embedding"], 0)

            # search uses sparse fallback when embeddings disabled
            hits = store.search("hello organism")
            self.assertGreaterEqual(len(hits), 1)
            self.assertIn("hello", hits[0]["text"].lower())

            self.assertTrue(store.delete(row_id))
            self.assertEqual(store.statistics()["total"], 0)
        finally:
            try:
                os.remove(db_path)
                os.rmdir(tmp)
            except OSError:
                pass

    def test_recent_orders_by_timestamp(self):
        from memory.db import MemoryDB
        from src.chetnaos.memory.store import MemoryStore
        import sqlite3

        tmp = tempfile.mkdtemp()
        db_path = os.path.join(tmp, "ts_test.db")
        try:
            db = MemoryDB(db_path=db_path)
            store = MemoryStore(db=db)
            with sqlite3.connect(db_path) as conn:
                conn.execute(
                    "INSERT INTO memories (text, meta, created_at) VALUES (?, ?, ?)",
                    ("older", "{}", "2020-01-01 00:00:00"),
                )
                conn.execute(
                    "INSERT INTO memories (text, meta, created_at) VALUES (?, ?, ?)",
                    ("newer", "{}", "2026-01-01 00:00:00"),
                )
                conn.commit()
            recent = store.recent(2)
            self.assertEqual(recent[0]["text"], "newer")
            self.assertEqual(recent[1]["text"], "older")
        finally:
            try:
                os.remove(db_path)
                os.rmdir(tmp)
            except OSError:
                pass


class TestBackwardCompatibility(unittest.TestCase):
    def test_memory_db_singleton_unchanged(self):
        from memory.db import memory_db
        self.assertTrue(hasattr(memory_db, "upsert"))
        self.assertTrue(hasattr(memory_db, "search"))
        self.assertTrue(hasattr(memory_db, "recent"))
        self.assertTrue(hasattr(memory_db, "delete"))
        self.assertTrue(hasattr(memory_db, "statistics"))

    def test_organism_memory_api(self):
        from memory.db import MemoryDB
        import src.chetnaos.organism.memory as mem_mod
        from src.chetnaos.memory.store import MemoryStore

        tmp = tempfile.mkdtemp()
        db_path = os.path.join(tmp, "compat_test.db")
        try:
            store = MemoryStore(db=MemoryDB(db_path=db_path))
            mem_mod._store = store
            mem_mod._HAS_DB = True

            memory = mem_mod.Memory()
            row_id = memory.store("interaction", "backward compat test")
            self.assertIsNotNone(row_id)
            self.assertEqual(len(memory.recent(1)), 1)
        finally:
            try:
                os.remove(db_path)
                os.rmdir(tmp)
            except OSError:
                pass

    def test_backend_agent_memory_import(self):
        from memory.db import memory_db as agent_db
        self.assertIsNotNone(agent_db)


class TestJsonValidation(unittest.TestCase):
    def test_live_identity_valid(self):
        from src.chetnaos.memory.validation import validate_identity
        result = validate_identity(MEMORY_DIR / "identity.json")
        self.assertTrue(result.ok, result.error)

    def test_live_beliefs_valid(self):
        from src.chetnaos.memory.validation import validate_beliefs
        result = validate_beliefs(MEMORY_DIR / "beliefs.json")
        self.assertTrue(result.ok, result.error)

    def test_live_purpose_valid(self):
        from src.chetnaos.memory.validation import validate_purpose
        result = validate_purpose(MEMORY_DIR / "purpose.json")
        self.assertTrue(result.ok, result.error)

    def test_live_skills_valid(self):
        from src.chetnaos.memory.validation import validate_skills
        result = validate_skills(MEMORY_DIR / "skills.json")
        self.assertTrue(result.ok, result.error)

    def test_live_workspace_valid(self):
        from src.chetnaos.memory.validation import validate_workspace
        result = validate_workspace(MEMORY_DIR / "workspace_state.json")
        self.assertTrue(result.ok, result.error)

    def test_live_habits_valid(self):
        from src.chetnaos.memory.validation import validate_habits
        result = validate_habits(MEMORY_DIR / "habits.json")
        self.assertTrue(result.ok, result.error)

    def test_live_development_valid(self):
        from src.chetnaos.memory.validation import validate_development
        result = validate_development(MEMORY_DIR / "development.json")
        self.assertTrue(result.ok, result.error)

    def test_live_relationships_valid(self):
        from src.chetnaos.memory.validation import validate_relationships
        result = validate_relationships(MEMORY_DIR / "relationships.json")
        self.assertTrue(result.ok, result.error)

    def test_live_training_goals_valid(self):
        from src.chetnaos.memory.validation import validate_training_goals
        result = validate_training_goals(MEMORY_DIR / "training_goals.json")
        self.assertTrue(result.ok, result.error)

    def test_live_contradictions_valid(self):
        from src.chetnaos.memory.validation import validate_contradictions
        result = validate_contradictions(MEMORY_DIR / "contradictions.json")
        self.assertTrue(result.ok, result.error)

    def test_live_mem_hierarchy_valid(self):
        from src.chetnaos.memory.validation import validate_mem_hierarchy
        result = validate_mem_hierarchy(MEMORY_DIR / "mem_hierarchy.json")
        self.assertTrue(result.ok, result.error)

    def test_memory_health_report(self):
        from src.chetnaos.memory.health import report
        health = report()
        self.assertTrue(health["locked"])
        self.assertTrue(health["overall_healthy"])
        self.assertEqual(health["json_validation"]["valid_count"], 15)

    def test_corrupt_json_backed_up_not_destroyed(self):
        from src.chetnaos.memory.validation import validate_identity, BACKUP_DIR

        tmp = tempfile.mkdtemp()
        bad_file = Path(tmp) / "bad_identity.json"
        original = BACKUP_DIR
        try:
            import src.chetnaos.memory.validation as val_mod
            val_mod.BACKUP_DIR = Path(tmp) / "backups"

            bad_file.write_text("{not valid json", encoding="utf-8")
            before = bad_file.read_text(encoding="utf-8")
            result = validate_identity(bad_file)
            self.assertFalse(result.ok)
            self.assertIsNotNone(result.backup_path)
            self.assertEqual(bad_file.read_text(encoding="utf-8"), before)
        finally:
            import src.chetnaos.memory.validation as val_mod
            val_mod.BACKUP_DIR = original


class TestMemoryFacades(unittest.TestCase):
    def test_facades_wrap_existing_modules(self):
        from src.chetnaos.memory.episodic import EpisodicMemory
        from src.chetnaos.memory.semantic import SemanticMemory
        from src.chetnaos.memory.procedural import ProceduralMemory
        from src.chetnaos.memory.working_memory import WorkingMemory

        ep = EpisodicMemory()
        self.assertTrue(callable(ep.record))

        sem = SemanticMemory()
        self.assertIsInstance(sem.get_all_beliefs(), list)

        proc = ProceduralMemory()
        self.assertIsInstance(proc.get_skills(), dict)

        wm = WorkingMemory()
        wm.push({"input": "test"})
        snap = wm.snapshot()
        self.assertGreaterEqual(snap["working_count"], 1)


class TestCognitiveFlow(unittest.TestCase):
    def test_cognitive_cycle_instantiates_with_memory(self):
        from src.chetnaos.cycle.cognitive_cycle import CognitiveCycle

        cycle = CognitiveCycle()
        self.assertIsNotNone(cycle.memory)
        self.assertTrue(callable(cycle.memory.store))
        self.assertTrue(callable(cycle.memory.recall))


if __name__ == "__main__":
    unittest.main()
