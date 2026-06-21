"""ChetnaOS v3 — runtime layer."""
from .state_machine import StateMachine, CycleStage, STAGE_ORDER

__all__ = [
    "ChetnaRuntime",
    "get_cycle",
    "StateMachine",
    "CycleStage",
    "STAGE_ORDER",
    "ExecutiveController",
    "EXECUTION_PIPELINE",
]


def __getattr__(name: str):
    if name in ("ChetnaRuntime", "get_cycle"):
        from .runtime import ChetnaRuntime, get_runtime as get_cycle
        return ChetnaRuntime if name == "ChetnaRuntime" else get_cycle
    if name in ("ExecutiveController", "EXECUTION_PIPELINE"):
        from src.chetnaos.cognition.executive import ExecutiveController, EXECUTION_PIPELINE
        return ExecutiveController if name == "ExecutiveController" else EXECUTION_PIPELINE
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
