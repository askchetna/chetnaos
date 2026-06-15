"""
Working Memory — bounded attention-weighted active context buffer.

Purpose: Hold volatile cycle context with eviction by lowest attention weight.
Inputs:  item dicts, attention_weight float
Outputs: recalled items, health metrics
Dependencies: optional MemoryHierarchy sync for dashboard compatibility
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

DEFAULT_CAPACITY = 7


@dataclass
class _WMItem:
    content: Dict[str, Any]
    attention_weight: float
    timestamp: float = field(default_factory=time.time)


class WorkingMemory:
    """In-process working memory with attention-weighted eviction."""

    def __init__(self, capacity: int = DEFAULT_CAPACITY, hierarchy=None):
        self._capacity = max(1, capacity)
        self._items: List[_WMItem] = []
        self._hierarchy = hierarchy
        self._evictions = 0

    def capacity(self) -> int:
        return self._capacity

    def push(self, item: dict, attention_weight: float = 0.5) -> None:
        weight = max(0.0, min(1.0, float(attention_weight)))
        self._items.insert(0, _WMItem(content=dict(item), attention_weight=weight))
        while len(self._items) > self._capacity:
            self._evict_lowest()
        if self._hierarchy is not None:
            try:
                self._hierarchy.push_working(item)
            except Exception as exc:
                logger.error("WorkingMemory hierarchy sync failed: %s", exc)

    def recall(self, k: int | None = None) -> List[Dict[str, Any]]:
        """Return active recall window sorted by attention weight (highest first)."""
        limit = k if k is not None else self._capacity
        sorted_items = sorted(
            self._items,
            key=lambda x: (x.attention_weight, x.timestamp),
            reverse=True,
        )
        return [
            {**it.content, "_attention_weight": it.attention_weight}
            for it in sorted_items[:limit]
        ]

    def clear(self) -> None:
        self._items.clear()

    def health(self) -> Dict[str, Any]:
        weights = [it.attention_weight for it in self._items]
        return {
            "capacity": self._capacity,
            "count": len(self._items),
            "utilization": round(len(self._items) / self._capacity, 3),
            "evictions_total": self._evictions,
            "avg_attention_weight": round(sum(weights) / len(weights), 3) if weights else 0.0,
            "max_attention_weight": round(max(weights), 3) if weights else 0.0,
        }

    def snapshot(self) -> Dict[str, Any]:
        """Dashboard-compatible snapshot."""
        return {
            "working_memory": self.recall(),
            "working_count": len(self._items),
            **self.health(),
        }

    def _evict_lowest(self) -> None:
        if not self._items:
            return
        lowest = min(range(len(self._items)), key=lambda i: self._items[i].attention_weight)
        self._items.pop(lowest)
        self._evictions += 1

    # ── Legacy hierarchy delegates (dashboard / sleep paths) ─────────────
    def add_semantic(self, concept: str):
        if self._hierarchy is not None:
            return self._hierarchy.add_semantic(concept)

    def add_dream(self, item: str):
        if self._hierarchy is not None:
            return self._hierarchy.add_dream(item)

    def record_forgetting(self, count: int):
        if self._hierarchy is not None:
            return self._hierarchy.record_forgetting(count)
