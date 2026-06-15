"""
Recursive self-reflection loop controller for AGI v0.9.

This module coordinates:
  - ChetnaCore (reasoning + Dharma + world mini-model)
  - Reflection V2 scoring
  - Memory service logging

The HTTP layer (e.g. /api/goal) can call run_loop() and return LoopResult.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from backend.chetna_core import ChetnaCore
from reflection.reflection_v2 import evaluate_decision

from .memory_service import get_memory_service
from .types import Goal, LoopResult, LoopStep, StepReflection


def _build_core() -> ChetnaCore:
    """Factory wrapper in case we later want shared or configurable cores."""
    return ChetnaCore()


def run_loop(
    goal: Goal,
    max_steps: int = 6,
    max_reflections: int = 2,
    user_input_override: Optional[str] = None,
) -> LoopResult:
    """
    Execute a bounded recursive loop toward a goal.

    For v0.9 this is intentionally conservative: each iteration uses ChetnaCore
    once, runs reflection on the output, and may stop early on low Dharma score.
    """
    core = _build_core()
    memory = get_memory_service()

    steps: list[LoopStep] = []
    terminated_reason = "max_steps_reached"

    # Initial "user input" is the goal text, unless overridden.
    current_input = user_input_override or goal.text

    for idx in range(max_steps):
        # Run core
        system_output: Dict[str, Any] = core.process(current_input)
        world_state = system_output.get("world_state") or {}

        # Memory logging
        memory.record_interaction("user", current_input, mode="goal")
        memory.record_interaction("assistant", system_output, mode="goal")
        memory.record_world_update(world_state)

        # Reflection
        reflection_raw = evaluate_decision(
            decision=system_output,
            context={
                "risk_level": goal.context.get("risk_level", "medium"),
                "intent": goal.context.get("intent", "analysis"),
                "requires_grounding": goal.context.get("requires_grounding", False),
                "requires_memory_window": goal.context.get(
                    "requires_memory_window", False
                ),
            },
        )
        reflection = StepReflection(
            score=reflection_raw["score"],
            dharma_ok=reflection_raw["dharma_ok"],
            corrections=list(reflection_raw.get("corrections") or []),
        )

        step = LoopStep(
            index=idx,
            user_input=current_input,
            system_output=system_output,
            reflection=reflection,
            world_state=world_state,
        )
        steps.append(step)

        # If Dharma says no, or score too low, stop and let caller decide.
        if not reflection.dharma_ok or reflection.score < 60:
            terminated_reason = "dharma_block_or_low_score"
            # Persist correction info for analysis
            if reflection.corrections:
                memory.record_correction(
                    before=system_output,
                    after=None,
                    reason="; ".join(reflection.corrections),
                )
            break

        # If we have reached a reasonable reflection budget, stop cleanly.
        if idx + 1 >= max_reflections:
            terminated_reason = "reflection_budget_exhausted"
            break

        # Simple heuristic: feed back filtered field (if present) as next input.
        current_input = system_output.get("filtered") or current_input

    final_world_state: Dict[str, Any] = (
        steps[-1].world_state if steps else core.world.snapshot()
    )

    return LoopResult(
        goal=goal,
        steps=steps,
        terminated_reason=terminated_reason,
        final_world_state=final_world_state,
    )


__all__ = ["run_loop"]


