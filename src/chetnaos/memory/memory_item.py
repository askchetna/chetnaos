"""Unified memory item schema."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from .source_ranks import COGNITIVE_SOURCE_RANKS

SOURCE_DEFAULT_CONFIDENCE = {
    "founder_context": COGNITIVE_SOURCE_RANKS["founder_context"],
    "working_memory": COGNITIVE_SOURCE_RANKS["working_memory"],
    "long_term_memory": COGNITIVE_SOURCE_RANKS["long_term_memory"],
    "general_knowledge": COGNITIVE_SOURCE_RANKS["general_knowledge"],
    "interaction": COGNITIVE_SOURCE_RANKS["long_term_memory"],
    "episodic": COGNITIVE_SOURCE_RANKS["long_term_memory"],
    "semantic": COGNITIVE_SOURCE_RANKS["long_term_memory"],
    "procedural": COGNITIVE_SOURCE_RANKS["long_term_memory"],
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_memory_item(
    text: str,
    *,
    source: str = "long_term_memory",
    confidence: Optional[float] = None,
    timestamp: Optional[str] = None,
    verification: str = "unverified",
    decay: float = 0.01,
    importance: float = 0.5,
    last_access: Optional[str] = None,
    embedding: Any = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build canonical memory metadata dict for store/search."""
    now = utc_now_iso()
    conf = confidence if confidence is not None else SOURCE_DEFAULT_CONFIDENCE.get(
        source, COGNITIVE_SOURCE_RANKS["long_term_memory"]
    )
    item: Dict[str, Any] = {
        "text": text,
        "confidence": conf,
        "source": source,
        "timestamp": timestamp or now,
        "verification": verification,
        "decay": decay,
        "importance": importance,
        "last_access": last_access or now,
    }
    if embedding is not None:
        item["embedding"] = embedding
    if extra:
        item.update(extra)
    return item


def enrich_search_result(row: Dict[str, Any]) -> Dict[str, Any]:
    """Merge meta fields onto a search/recall row for downstream consumers."""
    meta = row.get("meta") or {}
    if isinstance(meta, dict):
        merged = {**row, **{k: v for k, v in meta.items() if k != "text"}}
        merged.setdefault(
            "confidence",
            SOURCE_DEFAULT_CONFIDENCE.get(
                merged.get("source", "long_term_memory"),
                COGNITIVE_SOURCE_RANKS["long_term_memory"],
            ),
        )
        return merged
    return row
