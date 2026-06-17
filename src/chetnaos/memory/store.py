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

from src.chetnaos.memory_kernel.memory_item import enrich_search_result, normalize_memory_item

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
        self._last_trace: Dict[str, Any] = {}

    @property
    def last_trace(self) -> Dict[str, Any]:
        return dict(self._last_trace)

    @property
    def db_path(self) -> str:
        return self._db.db_path

    def upsert(self, text: str, meta: Optional[Dict[str, Any]] = None) -> int:
        try:
            category = (meta or {}).get("category", "long_term_memory")
            normalized = normalize_memory_item(
                text,
                source=category if category in (
                    "founder_context", "working_memory", "long_term_memory", "general_knowledge"
                ) else "long_term_memory",
                extra=meta,
            )
            row_id = self._db.upsert(text, meta=normalized)
            logger.debug("MemoryStore.upsert id=%s source=%s", row_id, normalized.get("source"))
            return row_id
        except Exception as exc:
            logger.error("MemoryStore.upsert failed: %s", exc)
            raise

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        try:
            if hasattr(self._db, "search_with_trace"):
                rows, trace = self._db.search_with_trace(query, k=k)
                self._last_trace = trace
            else:
                rows = self._db.search(query, k=k) or []
                self._last_trace = {"query": query, "memories_selected": rows}
            return [enrich_search_result(r) for r in rows]
        except Exception as exc:
            logger.error("MemoryStore.search failed: %s", exc)
            raise

    def recent(self, n: int = 10) -> List[Dict[str, Any]]:
        """Return entries ordered by created_at timestamp (newest first)."""
        try:
            rows = self._db.recent(n) or []
            return [enrich_search_result(r) for r in rows]
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
