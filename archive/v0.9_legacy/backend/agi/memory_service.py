"""
High-level memory service for AGI v0.9.

Wraps the existing Smriti event log and the vector-memory DB so callers
do not need to know about storage details.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.memory import Smriti
from memory.db import memory_db


class MemoryService:
    def __init__(self) -> None:
        self._smriti = Smriti()
        # memory_db is already a global singleton from memory.db

    def record_interaction(
        self,
        role: str,
        content: Any,
        mode: str = "chat",
        tags: Optional[List[str]] = None,
    ) -> None:
        """Store a lightweight interaction event in Smriti."""
        ts = datetime.utcnow()
        payload: Dict[str, Any] = {
            "role": role,
            "content": content,
            "mode": mode,
            "tags": tags or [],
        }
        self._smriti.store_event("interaction", payload, ts)

    def record_correction(
        self,
        before: Any,
        after: Any,
        reason: str,
        tags: Optional[List[str]] = None,
    ) -> None:
        """Store a self-correction event."""
        ts = datetime.utcnow()
        payload: Dict[str, Any] = {
            "before": before,
            "after": after,
            "reason": reason,
            "tags": tags or [],
        }
        self._smriti.store_event("correction", payload, ts)

    def record_world_update(self, world_state: Dict[str, Any]) -> None:
        """Store a snapshot of the world state."""
        ts = datetime.utcnow()
        self._smriti.store_event("world_state", world_state, ts)

    def recall_for_goal(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve semantically-related memories for the given query.

        Uses the embedding-backed memory_db.
        """
        try:
            return memory_db.search(query, k=k)
        except Exception:
            # If embeddings are not available, degrade gracefully.
            return []


_GLOBAL_MEMORY_SERVICE: Optional[MemoryService] = None


def get_memory_service() -> MemoryService:
    global _GLOBAL_MEMORY_SERVICE
    if _GLOBAL_MEMORY_SERVICE is None:
        _GLOBAL_MEMORY_SERVICE = MemoryService()
    return _GLOBAL_MEMORY_SERVICE


__all__ = ["MemoryService", "get_memory_service"]


