"""
Executive Controller — orchestration policy for the cognitive cycle.

Purpose: Own stage scheduling, LLM gating, sleep policy, and execution decisions.
Inputs:  CycleStage, runtime context dict, SleepManager
Outputs: should_run, use_llm, skip_reason, health_state
Dependencies: orchestrator.state_machine.CycleStage, orchestrator.sleep_manager.SleepManager

Does NOT execute organism modules — CognitiveCycle remains the dispatcher.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from src.chetnaos.orchestrator.state_machine import CycleStage
from src.chetnaos.orchestrator.sleep_manager import SleepManager

logger = logging.getLogger(__name__)

# Stages emitted by CognitiveCycle.run() in fixed order (behavior contract).
EXECUTION_PIPELINE: List[CycleStage] = [
    CycleStage.EXIST,
    CycleStage.PURPOSE,
    CycleStage.OBSERVE,
    CycleStage.ATTEND,
    CycleStage.RECALL,
    CycleStage.PREDICT,
    CycleStage.IMAGINE,
    CycleStage.PLAY,
    CycleStage.PLAN,
    CycleStage.HABIT,
    CycleStage.ACT,
    CycleStage.WORLD_UPDATE,
    CycleStage.EXPERIENCE,
    CycleStage.REALITY_CHECK,
    CycleStage.EVALUATE,
    CycleStage.FAILURE_RECOVERY,
    CycleStage.REFLECT,
    CycleStage.SELF_QUESTION,
    CycleStage.UPDATE_BELIEFS,
    CycleStage.UPDATE_IDENTITY,
    CycleStage.REFINE_PURPOSE,
    CycleStage.SLEEP,
    CycleStage.FORGET,
    CycleStage.CONSOLIDATE,
    CycleStage.WAKE,
]

# Stages that may invoke the LLM when complexity is "complex".
_LLM_OPTIONAL_STAGES = frozenset({
    CycleStage.IMAGINE,
    CycleStage.PLAN,
})

# Reasoning (ACT) always uses the LLM router.
_LLM_REQUIRED_STAGES = frozenset({
    CycleStage.ACT,
})


class ExecutiveController:
    """Orchestration brain — policy only, no module execution."""

    def __init__(self, sleep_manager: SleepManager | None = None):
        self._sleeper = sleep_manager or SleepManager()
        self._context: Dict[str, Any] = {}
        self._interrupted = False
        self._interrupt_reason: Optional[str] = None
        self._disabled_stages: set[CycleStage] = set()
        self._stages_executed: List[str] = []
        self._last_skip_reason: Optional[str] = None

    @property
    def sleep_manager(self) -> SleepManager:
        return self._sleeper

    def reset_cycle_context(self, mode: str = "chat", user_input: str = "") -> None:
        """Initialize per-cycle context (called at start of run)."""
        self._context = {
            "mode": mode,
            "user_input": user_input,
            "complexity": "simple",
            "cycle_n": 0,
        }
        self._stages_executed = []
        self._last_skip_reason = None

    def update_context(self, **kwargs: Any) -> None:
        self._context.update(kwargs)

    @property
    def context(self) -> Dict[str, Any]:
        return dict(self._context)

    def request_interrupt(self, reason: str) -> None:
        """Signal that remaining stages should be skipped (future homeostasis hook)."""
        self._interrupted = True
        self._interrupt_reason = reason
        logger.warning("Executive interrupt requested: %s", reason)

    def clear_interrupt(self) -> None:
        self._interrupted = False
        self._interrupt_reason = None

    def disable_stage(self, stage: CycleStage) -> None:
        self._disabled_stages.add(stage)

    def enable_stage(self, stage: CycleStage) -> None:
        self._disabled_stages.discard(stage)

    def enable_all_stages(self) -> None:
        self._disabled_stages.clear()

    def should_run(self, stage: CycleStage, context: Dict[str, Any] | None = None) -> bool:
        """Whether the dispatcher should execute this stage."""
        if self._interrupted:
            self._last_skip_reason = self._interrupt_reason or "interrupted"
            return False
        if stage in self._disabled_stages:
            self._last_skip_reason = f"stage_disabled:{stage.value}"
            return False
        # DECIDE is defined in enum but never emitted — executive never schedules it.
        if stage == CycleStage.DECIDE:
            self._last_skip_reason = "stage_not_in_pipeline:DECIDE"
            return False
        self._last_skip_reason = None
        return True

    def skip_reason(self, stage: CycleStage, context: Dict[str, Any] | None = None) -> Optional[str]:
        """Return skip reason if should_run is False, else None."""
        if self.should_run(stage, context):
            return None
        return self._last_skip_reason

    def use_llm(self, stage: CycleStage, context: Dict[str, Any] | None = None) -> bool:
        """LLM gating policy — identical to pre-extraction cognitive_cycle behavior."""
        ctx = context if context is not None else self._context
        if stage in _LLM_REQUIRED_STAGES:
            return True
        if stage in _LLM_OPTIONAL_STAGES:
            return ctx.get("complexity") == "complex"
        return False

    def llm_router_for(self, stage: CycleStage, llm_router: Any, context: Dict[str, Any] | None = None):
        """Return llm_router or None per policy."""
        return llm_router if self.use_llm(stage, context) else None

    def should_sleep_consolidation(self, cycle_n: int) -> bool:
        """Whether full sleep/consolidation path runs (delegates to SleepManager)."""
        return self._sleeper.should_sleep(cycle_n)

    def cycles_until_sleep(self, cycle_n: int) -> int:
        return self._sleeper.cycles_until_sleep(cycle_n)

    def mark_slept(self, cycle_n: int) -> None:
        self._sleeper.mark_slept(cycle_n)

    def should_refine_purpose(self, reflect_quality: str) -> bool:
        return reflect_quality == "good"

    def should_add_workspace_artifact(self, output: str) -> bool:
        return len(output) > 150

    def should_poor_quality_followup(self, reflect_quality: str) -> bool:
        return reflect_quality == "poor"

    def self_question_answer(self, reflect_quality: str) -> str:
        return "yes" if reflect_quality in ("good", "fair") else "needs_improvement"

    def before_stage(self, stage: CycleStage, context: Dict[str, Any] | None = None) -> None:
        logger.debug("Executive before_stage %s", stage.value)

    def after_stage(self, stage: CycleStage, result: Dict[str, Any] | None = None,
                    context: Dict[str, Any] | None = None) -> None:
        self._stages_executed.append(stage.value)
        logger.debug("Executive after_stage %s", stage.value)

    def pipeline_order(self) -> List[str]:
        """Fixed execution pipeline stage names."""
        return [s.value for s in EXECUTION_PIPELINE]

    def health_state(self) -> Dict[str, Any]:
        return {
            "interrupted": self._interrupted,
            "interrupt_reason": self._interrupt_reason,
            "disabled_stages": [s.value for s in self._disabled_stages],
            "stages_executed_last_cycle": list(self._stages_executed),
            "context_snapshot": dict(self._context),
            "sleep_every": self._sleeper._sleep_every,
            "last_sleep_at_cycle": self._sleeper._last_sleep,
            "llm_required_stages": [s.value for s in _LLM_REQUIRED_STAGES],
            "llm_optional_stages": [s.value for s in _LLM_OPTIONAL_STAGES],
            "pipeline_length": len(EXECUTION_PIPELINE),
        }
