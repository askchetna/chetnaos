"""
Context builder — cognitive organ signals for the reasoning stage.

Used by CognitiveCycle._build_reasoning_context().
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class ContextBuilder:
    """Assemble cognitive_context dict from organ snapshots."""

    def build(
        self,
        *,
        working_memory: Optional[List[dict]] = None,
        active_goal: Optional[dict] = None,
        beliefs: Optional[List[dict]] = None,
        self_model: Optional[dict] = None,
        curiosity: Optional[dict] = None,
        emotion: Optional[dict] = None,
        agent_tool: Optional[dict] = None,
    ) -> Dict[str, Any]:
        ctx: Dict[str, Any] = {}
        if working_memory:
            ctx["working_memory"] = working_memory
        if active_goal:
            ctx["active_goal"] = active_goal
        if beliefs:
            ctx["beliefs"] = beliefs
        if self_model:
            ctx["self_model"] = self_model
        if curiosity:
            ctx["curiosity"] = curiosity
        if emotion:
            ctx["emotion"] = emotion
        if agent_tool:
            ctx["agent_tool"] = agent_tool
        return ctx
