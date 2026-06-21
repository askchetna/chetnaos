"""Rule-based audience inference for adaptive explanations."""
from __future__ import annotations

import re
from typing import Any, Dict, Optional

AUDIENCES = (
    "beginner",
    "expert",
    "programmer",
    "founder",
    "researcher",
    "casual user",
)

_BEGINNER = (
    r"\b(simple|basic|beginner|eli5|explain like|samjhao simple|easy terms)\b",
    r"\bi('m| am) new to\b",
    r"\bfor dummies\b",
)

_EXPERT = (
    r"\b(technical|deep dive|architecture|implementation detail|edge case)\b",
    r"\bformal(ly)?\b", r"\bnuance\b", r"\btradeoff\b",
)

_PROGRAMMER = (
    r"\b(code|function|class|api|python|javascript|typescript|sql|debug|stack trace)\b",
    r"\b(implement|refactor|compile|syntax)\b",
)

_FOUNDER = (
    r"\b(launch|startup|product|roadmap|go-to-market|gtm|arr|revenue|users)\b",
    r"\b(business|strategy|execution|milestone|fundraising)\b",
    r"\bfounder\b",
)

_RESEARCHER = (
    r"\b(research|paper|hypothesis|experiment|benchmark|ablation|methodology)\b",
    r"\b(agi|cognitive architecture|formal)\b",
)


def infer_audience(
    user_input: str,
    *,
    intent: str = "",
    conversation_context: Optional[Dict[str, Any]] = None,
) -> str:
    q = (user_input or "").lower()
    if intent == "coding":
        return "programmer"
    for pat in _PROGRAMMER:
        if re.search(pat, q, re.I):
            return "programmer"
    for pat in _FOUNDER:
        if re.search(pat, q, re.I):
            return "founder"
    for pat in _RESEARCHER:
        if re.search(pat, q, re.I):
            return "researcher"
    for pat in _BEGINNER:
        if re.search(pat, q, re.I):
            return "beginner"
    for pat in _EXPERT:
        if re.search(pat, q, re.I):
            return "expert"
    if len(q.split()) <= 5 and intent == "casual":
        return "casual user"
    return "casual user"


def audience_hints(audience: str) -> Dict[str, Any]:
    """Hints for style and verbosity — no LLM calls."""
    return {
        "beginner": {
            "verbosity_bias": "short",
            "prefer_examples": True,
            "avoid_jargon": True,
            "code_first": False,
        },
        "expert": {
            "verbosity_bias": "structured",
            "prefer_examples": False,
            "avoid_jargon": False,
            "code_first": False,
        },
        "programmer": {
            "verbosity_bias": "code_first",
            "prefer_examples": True,
            "avoid_jargon": False,
            "code_first": True,
        },
        "founder": {
            "verbosity_bias": "structured",
            "prefer_examples": False,
            "avoid_jargon": True,
            "code_first": False,
            "focus": "strategy_tradeoffs_execution",
        },
        "researcher": {
            "verbosity_bias": "structured",
            "prefer_examples": False,
            "avoid_jargon": False,
            "code_first": False,
        },
        "casual user": {
            "verbosity_bias": "medium",
            "prefer_examples": True,
            "avoid_jargon": True,
            "code_first": False,
        },
    }.get(audience, {
        "verbosity_bias": "medium",
        "prefer_examples": True,
        "avoid_jargon": True,
        "code_first": False,
    })
