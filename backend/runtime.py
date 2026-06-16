"""
ChetnaOS v3 — single process runtime singleton.

All HTTP routes must use get_runtime(); never instantiate ChetnaRuntime per request.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.chetnaos.runtime.runtime import ChetnaRuntime

_runtime: "ChetnaRuntime | None" = None


def get_runtime() -> "ChetnaRuntime | None":
    """Return the shared cognitive runtime, initialising once per process."""
    global _runtime
    if _runtime is None:
        try:
            from src.chetnaos.runtime.runtime import ChetnaRuntime

            _runtime = ChetnaRuntime()
        except Exception as e:
            print(f"[ChetnaOS] Warning: Could not initialise cognitive runtime: {e}")
            _runtime = None
    return _runtime


def reset_runtime() -> None:
    """Clear singleton (tests only)."""
    global _runtime
    _runtime = None
