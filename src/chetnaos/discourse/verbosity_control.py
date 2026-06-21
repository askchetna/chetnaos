"""Adaptive verbosity — short vs structured answers."""
from __future__ import annotations

import re
from typing import Any, Dict

_STRUCTURED_INTENTS = frozenset({
    "debug", "learning", "decision", "comparison", "planning",
})

_COMPLEX_HINTS = (
    r"\bin detail\b", r"\bstep by step\b", r"\bcomprehensive\b",
    r"\bexplain (everything|fully|all)\b", r"\bdeep dive\b",
    r"\bcompare\b", r"\bpros and cons\b",
)

_SIMPLE_HINTS = (
    r"^(hi|hello|hey|thanks|ok|okay|yes|no)\.?$",
    r"^(haan|nahi|theek)\.?$",
)


def assess_verbosity(
    user_input: str,
    intent: str,
    dialogue_act: str,
    ctx: Dict[str, Any] | None = None,
) -> str:
    """
    Return verbosity level: short | medium | structured | code_first.
    """
    q = (user_input or "").strip().lower()

    if intent == "coding":
        return "code_first"
    if intent == "identity":
        return "short"
    if dialogue_act == "agreement":
        return "short"
    if dialogue_act == "confusion":
        return "medium"
    if intent == "debug":
        return "structured"
    if intent == "casual" and len(q.split()) <= 4:
        return "short"

    for pat in _SIMPLE_HINTS:
        if re.search(pat, q, re.I):
            return "short"

    for pat in _COMPLEX_HINTS:
        if re.search(pat, q, re.I):
            return "structured"

    if intent in _STRUCTURED_INTENTS:
        word_count = len(q.split())
        if word_count >= 12 or q.count("?") >= 2:
            return "structured"
        return "medium"

    if len(q.split()) <= 8 and "?" in q:
        return "short"

    return "medium"


def max_sentences(verbosity: str, intent: str) -> int:
    if verbosity == "short":
        return 3 if intent == "emotional" else 2
    if verbosity == "structured":
        return 24
    if verbosity == "code_first":
        return 20
    return 8


def should_show_headers(intent: str, verbosity: str, section_count: int) -> bool:
    if verbosity == "short":
        return False
    if intent == "debug":
        return section_count >= 2
    if verbosity == "structured" and intent in _STRUCTURED_INTENTS:
        return section_count >= 2
    return False
