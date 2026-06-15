"""Phase 1 gate: import, memory persistence, API health."""
from __future__ import annotations

import importlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ.setdefault("LIGHT_MODE", "true")
os.environ.setdefault("EMBEDDINGS_ENABLED", "false")


class TestImports(unittest.TestCase):
    """Verify live cognitive kernel imports without the archived v0.9 stack."""

    MODULES = [
        "memory.db",
        "backend.config",
        "backend.app",
        "src.chetnaos.orchestrator.runtime",
        "src.chetnaos.orchestrator.cognitive_cycle",
        "src.chetnaos.organism.memory",
        "src.chetnaos.organism.reality",
        "reflection.reflection_v2",
    ]

    def test_core_modules_import(self):
        for name in self.MODULES:
            with self.subTest(module=name):
                mod = importlib.import_module(name)
                self.assertIsNotNone(mod)


class TestMemoryPersistence(unittest.TestCase):
    """MemoryStore upsert/recent and organism Memory.store must persist rows."""

    def test_memory_db_upsert_and_recent(self):
        from memory.db import MemoryDB

        tmp = tempfile.mkdtemp()
        db_path = os.path.join(tmp, "phase1_test.db")
        try:
            db = MemoryDB(db_path=db_path)
            row_id = db.upsert("phase1 persistence test", meta={"category": "test"})
            self.assertIsInstance(row_id, int)
            self.assertGreater(row_id, 0)

            recent = db.recent(1)
            self.assertEqual(len(recent), 1)
            self.assertEqual(recent[0]["text"], "phase1 persistence test")
            self.assertEqual(recent[0]["meta"]["category"], "test")
        finally:
            del db
            try:
                os.remove(db_path)
                os.rmdir(tmp)
            except OSError:
                pass

    def test_organism_memory_store(self):
        from memory.db import MemoryDB
        import src.chetnaos.organism.memory as mem_mod
        from src.chetnaos.memory.store import MemoryStore

        tmp = tempfile.mkdtemp()
        db_path = os.path.join(tmp, "organism_test.db")
        try:
            store = MemoryStore(db=MemoryDB(db_path=db_path))
            mem_mod._store = store
            mem_mod._HAS_DB = True

            memory = mem_mod.Memory()
            row_id = memory.store("interaction", "Q: test\nA: stored")
            self.assertIsNotNone(row_id)

            recent = memory.recent(1)
            self.assertEqual(len(recent), 1)
            self.assertIn("stored", recent[0]["text"])
        finally:
            del mem_mod._store
            try:
                os.remove(db_path)
                os.rmdir(tmp)
            except OSError:
                pass


class TestApiHealth(unittest.TestCase):
    """FastAPI health endpoint must respond without external services."""

    def test_health_endpoint(self):
        from fastapi.testclient import TestClient
        from backend.app import app

        client = TestClient(app)
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("ok"))
        self.assertEqual(data.get("service"), "ChetnaOS")
        self.assertIn("cognitive_runtime", data)


def run_smoke_if_server_running() -> bool:
    """Optional smoke test when uvicorn is already on :8000."""
    try:
        import urllib.request

        with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False


def main() -> int:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestImports))
    suite.addTests(loader.loadTestsFromTestCase(TestMemoryPersistence))
    suite.addTests(loader.loadTestsFromTestCase(TestApiHealth))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n--- Phase 1 Gate Summary ---")
    print(f"Import test:          {'PASS' if result.wasSuccessful() else 'FAIL'}")
    print(f"Memory persistence:   {'PASS' if result.wasSuccessful() else 'FAIL'}")
    print(f"API health (TestClient): {'PASS' if result.wasSuccessful() else 'FAIL'}")

    if run_smoke_if_server_running():
        print("Live smoke (/health): PASS (server detected on :8000)")
    else:
        print("Live smoke (/health): SKIP (no server on :8000 — start uvicorn to run smoke.ps1)")

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
