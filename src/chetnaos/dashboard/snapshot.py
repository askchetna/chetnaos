"""Delegate to CognitiveCycle.dashboard_snapshot."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.chetnaos.cycle.cognitive_cycle import CognitiveCycle


def dashboard_snapshot(cycle: "CognitiveCycle") -> dict:
    return cycle.dashboard_snapshot()
