"""
Memory — Long-term memory interface for the organism.

All vector persistence flows through MemoryStore (no direct memory.db access).
"""
import logging

logger = logging.getLogger(__name__)

try:
    from src.chetnaos.memory.store import get_memory_store
    _store = get_memory_store()
except Exception as exc:
    logger.warning("MemoryStore unavailable: %s", exc)
    _store = None


class Memory:
    def recall(self, query: str, k: int = 5) -> list:
        if _store is None:
            return []
        try:
            return _store.search(query, k=k) or []
        except Exception as exc:
            logger.error("Memory recall failed: %s", exc)
            return []

    def last_trace(self) -> dict:
        if _store is None:
            return {}
        return _store.last_trace

    def store(self, category: str, text: str, metadata: dict = None) -> int | None:
        if _store is None:
            return None
        try:
            meta = {"category": category, **(metadata or {})}
            return _store.upsert(text, meta=meta)
        except Exception as exc:
            logger.error("Memory store failed: %s", exc)
            return None

    def recent(self, n: int = 10) -> list:
        if _store is None:
            return []
        try:
            return _store.recent(n) or []
        except Exception as exc:
            logger.error("Memory recent() failed: %s", exc)
            return []
