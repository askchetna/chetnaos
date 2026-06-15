"""
Goal-oriented agent built on top of the AGI v0.9 loop.

This module exposes a single entrypoint execute_goal() that higher layers
such as FastAPI routes can call.
"""

from __future__ import annotations

from typing import Any, Dict

from .loop import run_loop
from .types import Goal, LoopResult


def execute_goal(payload: Dict[str, Any]) -> LoopResult:
    """
    Execute a high-level goal request.

    Expected payload shape from HTTP layer:
        {
          "goal": "string",
          "context": {...},      # optional
          "constraints": {...}   # optional
        }
    """
    goal = Goal(
        text=str(payload.get("goal") or ""),
        context=payload.get("context") or {},
        constraints=payload.get("constraints") or {},
    )
    return run_loop(goal)


__all__ = ["execute_goal"]


