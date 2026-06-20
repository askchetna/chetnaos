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
        temporal: Optional[dict] = None,
        episodic: Optional[dict] = None,
        identity: Optional[dict] = None,
        founder_relationship: Optional[dict] = None,
        values: Optional[dict] = None,
        recent_reflection: Optional[str] = None,
        episodic_highlight: Optional[dict] = None,
        recurring_themes: Optional[List[str]] = None,
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
        if temporal:
            ctx["temporal"] = temporal
        if episodic:
            ctx["episodic"] = episodic
        if identity:
            ctx["identity"] = identity
        if founder_relationship:
            ctx["founder_relationship"] = founder_relationship
        if values:
            ctx["values"] = values
        if recent_reflection:
            ctx["recent_reflection"] = recent_reflection
        if episodic_highlight:
            ctx["episodic_highlight"] = episodic_highlight
        if recurring_themes:
            ctx["recurring_themes"] = recurring_themes
        return ctx
