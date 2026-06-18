"""Shared runtime telemetry meta for Chat and Agent API responses."""
from __future__ import annotations

from typing import Any

# Canonical keys exposed by /api/chat and /api/agent (identical structure).
RUNTIME_META_KEYS: tuple[str, ...] = (
    "cycle",
    "cycle_id",
    "quality",
    "confidence",
    "confidence_level",
    "dharma_score",
    "cycle_score",
    "domain",
    "intent",
    "beliefs_count",
    "health",
    "slept",
    "stage_trace",
    "cycle_trace",
    "reality",
    "simulation",
    "meta_cognition",
    "cognitive_organs",
    "reasoning_integration",
    "memory_influence",
    "belief_influence",
    "goal",
    "goal_progress",
    "belief_changes",
    "contradiction_resolutions",
    "honesty_guard_changes",
    "agent_tool",
)


def honesty_from_result(result: dict) -> list:
    """Extract honesty guard substitutions from ACT stage trace."""
    for entry in result.get("trace", []):
        if entry.get("stage") == "ACT":
            return list(entry.get("honesty_guard") or [])
    return []


def build_runtime_meta(result: dict) -> dict:
    """Build identical runtime meta dict from CognitiveCycle.run() output."""
    ri = result.get("reasoning_integration") or {}
    organs = result.get("cognitive_organs") or {}
    gm = organs.get("goal_manager") or {}
    active_goal = gm.get("active_goal") if isinstance(gm, dict) else None

    meta: dict[str, Any] = {
        "cycle": result.get("cycle"),
        "cycle_id": result.get("cycle_id"),
        "quality": result.get("quality"),
        "confidence": result.get("confidence"),
        "confidence_level": result.get("confidence_level"),
        "dharma_score": result.get("dharma_score"),
        "cycle_score": result.get("cycle_score"),
        "domain": result.get("domain"),
        "intent": result.get("intent"),
        "beliefs_count": result.get("beliefs_count"),
        "health": result.get("health"),
        "slept": result.get("slept"),
        "stage_trace": result.get("stage_trace") or [],
        "cycle_trace": result.get("cycle_trace") or [],
        "reality": result.get("reality") or {},
        "simulation": result.get("simulation") or {},
        "meta_cognition": result.get("meta_cognition") or {},
        "cognitive_organs": organs,
        "reasoning_integration": ri,
        "memory_influence": ri.get("memory_influence") or [],
        "belief_influence": ri.get("belief_influence") or [],
        "goal": active_goal,
        "goal_progress": result.get("goal_progress") or {},
        "belief_changes": result.get("belief_changes") or [],
        "contradiction_resolutions": result.get("contradiction_resolutions") or [],
        "honesty_guard_changes": honesty_from_result(result)
        + (result.get("reasoning_integration") or {}).get("telemetry_guard_changes", []),
        "agent_tool": result.get("agent_tool"),
    }
    return meta
