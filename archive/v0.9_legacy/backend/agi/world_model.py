"""
Lightweight wrapper around the existing WorldState mini-model.

The goal is to provide a stable interface for the AGI loop while reusing
the v1.0 world_state implementation.
"""

from __future__ import annotations

from typing import Any, Dict

from backend.world_state import WorldState


class WorldModel:
    """Adapter that exposes WorldState via a small, explicit interface."""

    def __init__(self) -> None:
        self._world = WorldState()

    def refresh(self) -> None:
        """Refresh internal world snapshot (time, day, etc.)."""
        self._world.refresh()

    def snapshot(self) -> Dict[str, Any]:
        """Return a JSON-serialisable snapshot."""
        return self._world.snapshot()


__all__ = ["WorldModel"]


