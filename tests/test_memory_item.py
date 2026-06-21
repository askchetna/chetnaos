"""Tests for v3 memory item schema (Phase 7B)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class TestMemoryItem(unittest.TestCase):
    def test_normalize_memory_item_fields(self):
        from src.chetnaos.memory.memory_item import normalize_memory_item

        item = normalize_memory_item(
            "test fact",
            source="working_memory",
            verification="verified",
            importance=0.9,
        )
        for key in (
            "text",
            "confidence",
            "source",
            "timestamp",
            "verification",
            "decay",
            "importance",
            "last_access",
        ):
            self.assertIn(key, item)
        self.assertEqual(item["text"], "test fact")
        self.assertEqual(item["source"], "working_memory")
        self.assertAlmostEqual(item["confidence"], 0.80, places=2)

    def test_memory_store_upsert_normalizes_meta(self):
        from unittest.mock import MagicMock
        from src.chetnaos.memory.store import MemoryStore

        db = MagicMock()
        db.upsert.return_value = 1
        store = MemoryStore(db=db)
        store.upsert("hello", meta={"category": "interaction"})
        meta = db.upsert.call_args.kwargs.get("meta") or db.upsert.call_args[0][1]
        self.assertIn("confidence", meta)
        self.assertIn("source", meta)
        self.assertIn("decay", meta)


if __name__ == "__main__":
    unittest.main()
