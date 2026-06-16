"""Conversation context packet for follow-up resolution (reasoning layer, not an organ)."""
from __future__ import annotations

import re
from typing import Any


def _topic_from_messages(messages: list[dict]) -> str:
    for msg in reversed(messages):
        if msg.get("role") != "user":
            continue
        text = (msg.get("content") or "").strip()
        if not text:
            continue
        if len(text) <= 80:
            return text
        return text[:77] + "…"
    return "general"


def build_context_packet(
    *,
    recent_messages: list[dict],
    active_goal: dict | None,
    conversation_summary: str = "",
    relevant_memory: list | None = None,
) -> dict[str, Any]:
    """Context injected before every reasoning call."""
    return {
        "recent_messages": [
            {"role": m.get("role"), "content": (m.get("content") or "")[:2000]}
            for m in (recent_messages or [])[-12:]
        ],
        "active_topic": _topic_from_messages(recent_messages or []),
        "current_goal": active_goal,
        "conversation_summary": (conversation_summary or "")[:2000],
        "relevant_memory": list(relevant_memory or [])[:5],
    }


def merge_summary(existing: str, user: str, assistant: str) -> str:
    """Lightweight rolling summary for long threads."""
    parts = [p for p in [existing, f"User: {user[:120]}", f"Assistant: {assistant[:120]}"] if p]
    text = " | ".join(parts)
    return text[-2000:]


def is_follow_up(text: str) -> bool:
    """Heuristic: short anaphoric questions likely depend on prior turn."""
    t = (text or "").strip().lower()
    if len(t) > 120:
        return False
    patterns = (
        r"^(how|what|why|when|where|who)\s+(does|do|is|are|was|were|it|that|this|they)\b",
        r"^(and|but|so|then)\b",
        r"\b(it|that|this|they|them|those|these)\b",
        r"^(explain|elaborate|continue|more|again)\b",
    )
    return any(re.search(p, t) for p in patterns)
