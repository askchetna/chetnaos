"""
Memory — Long-term memory interface for the organism.
Wraps the SQLite memory store.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

try:
    from memory.db import memory_db as _db
    _HAS_DB = True
except Exception:
    _HAS_DB = False


class Memory:
    def recall(self, query: str, k: int = 5) -> list:
        if not _HAS_DB:
            return []
        try:
            results = _db.search(query, k=k)
            return results or []
        except Exception:
            return []

    def store(self, category: str, text: str, metadata: dict = None):
        if not _HAS_DB:
            return
        try:
            _db.add(text, metadata={"category": category, **(metadata or {})})
        except Exception:
            pass

    def recent(self, n: int = 10) -> list:
        if not _HAS_DB:
            return []
        try:
            return _db.recent(n) or []
        except Exception:
            return []
