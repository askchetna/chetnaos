from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Goal(BaseModel):
    """High-level goal specification for the AGI loop."""

    text: str = Field(..., description="Natural-language description of the goal.")
    context: Dict[str, Any] = Field(
        default_factory=dict, description="Optional structured context."
    )
    constraints: Dict[str, Any] = Field(
        default_factory=dict, description="Resource / policy constraints."
    )


class StepReflection(BaseModel):
    """Outcome of running a decision through the Dharma / reflection filters."""

    score: int
    dharma_ok: bool
    corrections: List[str] = Field(default_factory=list)


class LoopStep(BaseModel):
    """One step in the recursive loop: input, output, reflection, and world snapshot."""

    index: int
    user_input: str
    system_output: Dict[str, Any]
    reflection: Optional[StepReflection] = None
    world_state: Dict[str, Any] = Field(default_factory=dict)


class LoopResult(BaseModel):
    """Final outcome of a loop run, with trace for debugging/evaluation."""

    goal: Goal
    steps: List[LoopStep] = Field(default_factory=list)
    terminated_reason: str
    final_world_state: Dict[str, Any] = Field(default_factory=dict)


__all__ = [
    "Goal",
    "StepReflection",
    "LoopStep",
    "LoopResult",
]


