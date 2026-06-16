"""Cognitive organ inspection for API meta."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.chetnaos.cycle.cognitive_cycle import CognitiveCycle


def runtime_inspection_snapshot(cycle: "CognitiveCycle") -> dict:
    return cycle._runtime_inspection_snapshot()
