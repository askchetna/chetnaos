"""
Memory — Long-term memory interface for the organism.

Purpose: Wrap MemoryStore for recall, store, and recent access in the cognitive cycle.
Inputs:  query text, category, metadata dict
Outputs: ranked recall list, stored row id (via upsert), recent entries
Dependencies: src.chetnaos.memory.store.MemoryStore
"""
import logging
import os
import sys

logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

try:
    from src.chetnaos.memory.store import get_memory_store
    _store = get_memory_store()
    _HAS_DB = True
except Exception as exc:
    logger.warning("MemoryStore unavailable, falling back to memory.db: %s", exc)
    _store = None
    _HAS_DB = False
    try:
        from memory.db import memory_db as _db
        _HAS_DB = True
    except Exception as fallback_exc:
        logger.warning("MemoryDB fallback unavailable: %s", fallback_exc)
        _db = None


class Memory:
    def recall(self, query: str, k: int = 5) -> list:
        if not _HAS_DB:
            return []
        try:
            if _store is not None:
                results = _store.search(query, k=k)
            else:
                results = _db.search(query, k=k)
            return results or []
        except Exception as exc:
            logger.error("Memory recall failed: %s", exc)
            return []

    def store(self, category: str, text: str, metadata: dict = None) -> int | None:
        if not _HAS_DB:
            return None
        try:
            meta = {"category": category, **(metadata or {})}
            if _store is not None:
                return _store.upsert(text, meta=meta)
            return _db.upsert(text, meta=meta)
        except Exception as exc:
            logger.error("Memory store failed: %s", exc)
            return None

    def recent(self, n: int = 10) -> list:
        if not _HAS_DB:
            return []
        try:
            if _store is not None:
                return _store.recent(n) or []
            return _db.recent(n) or []
        except Exception as exc:
            logger.error("Memory recent() failed: %s", exc)
            return []
