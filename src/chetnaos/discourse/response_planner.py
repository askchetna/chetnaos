"""Backward-compatible planner — delegates to knowledge_planner."""
from __future__ import annotations

from typing import Any, Dict

from .knowledge_planner import build_knowledge_plan
from .response_goal_engine import infer_response_goal


def build_plan(intent: str, raw_response: str, *, verbosity: str = "medium") -> Dict[str, Any]:
    goal = infer_response_goal(intent, dialogue_act="fresh")
    return build_knowledge_plan(
        response_goal=goal,
        intent=intent,
        raw_response=raw_response,
        verbosity=verbosity,
    )
