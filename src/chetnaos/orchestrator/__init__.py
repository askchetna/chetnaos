"""
ChetnaOS Orchestrator — Coordinates the full 27-stage cognitive cycle.
"""
__all__ = ["ChetnaRuntime"]


def __getattr__(name: str):
    if name == "ChetnaRuntime":
        from .runtime import ChetnaRuntime
        return ChetnaRuntime
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
