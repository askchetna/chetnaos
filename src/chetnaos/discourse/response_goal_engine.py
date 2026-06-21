"""Infer primary response goal — controls knowledge ordering."""
from __future__ import annotations

from typing import Any, Dict

GOALS = (
    "explain",
    "teach",
    "debug",
    "compare",
    "plan",
    "brainstorm",
    "comfort",
    "decide",
    "clarify",
)

_INTENT_GOAL = {
    "identity": "explain",
    "debug": "debug",
    "learning": "explain",
    "decision": "decide",
    "comparison": "compare",
    "planning": "plan",
    "brainstorm": "brainstorm",
    "emotional": "comfort",
    "philosophical": "explain",
    "coding": "teach",
    "casual": "explain",
}

_PRAGMATIC_OVERRIDE = {
    "confusion": "clarify",
    "frustration": "comfort",
    "delegation": "plan",
    "urgency": "decide",
    "agreement": "explain",
}


def infer_response_goal(
    intent: str,
    *,
    pragmatics: Dict[str, Any] | None = None,
    dialogue_act: str = "fresh",
) -> str:
    prag = pragmatics or {}
    hidden = prag.get("hidden_intent")
    if hidden and hidden in _PRAGMATIC_OVERRIDE:
        return _PRAGMATIC_OVERRIDE[hidden]
    if dialogue_act == "confusion":
        return "clarify"
    if dialogue_act == "correction":
        return "clarify"
    if dialogue_act == "agreement":
        return "explain"
    if intent == "learning" and prag.get("teach_mode"):
        return "teach"
    return _INTENT_GOAL.get(intent, "explain")
