"""
MemoryStore — unified facade over the vector SQLite memory kernel.

Purpose: One MemoryStore abstraction delegating to memory.db.MemoryDB.
Inputs:  text, query strings, metadata dicts, memory ids
Outputs: row ids, search results, recent entries, statistics
Dependencies: memory.db.MemoryDB
"""
from __future__ import annotations

import logging
import sqlite3
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_store_instance: "MemoryStore | None" = None


class MemoryStore:
    """Single memory kernel. All vector persistence flows through this facade."""

    def __init__(self, db=None):
        if db is None:
            from memory.db import memory_db
            self._db = memory_db
        else:
            self._db = db

    @property
    def db_path(self) -> str:
        return self._db.db_path

    def upsert(self, text: str, meta: Optional[Dict[str, Any]] = None) -> int:
        try:
            row_id = self._db.upsert(text, meta=meta)
            logger.debug("MemoryStore.upsert id=%s category=%s", row_id, (meta or {}).get("category"))
            return row_id
        except Exception as exc:
            logger.error("MemoryStore.upsert failed: %s", exc)
            raise

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        try:
            return self._db.search(query, k=k) or []
        except Exception as exc:
            logger.error("MemoryStore.search failed: %s", exc)
            raise

    def recent(self, n: int = 10) -> List[Dict[str, Any]]:
        """Return entries ordered by created_at timestamp (newest first)."""
        try:
            return self._db.recent(n) or []
        except Exception as exc:
            logger.error("MemoryStore.recent failed: %s", exc)
            raise

    def delete(self, memory_id: int) -> bool:
        try:
            return self._db.delete(memory_id)
        except Exception as exc:
            logger.error("MemoryStore.delete failed for id=%s: %s", memory_id, exc)
            raise

    def statistics(self) -> Dict[str, Any]:
        try:
            return self._db.statistics()
        except Exception as exc:
            logger.error("MemoryStore.statistics failed: %s", exc)
            raise


def get_memory_store() -> MemoryStore:
    """Process-wide MemoryStore singleton."""
    global _store_instance
    if _store_instance is None:
        _store_instance = MemoryStore()
    return _store_instance
