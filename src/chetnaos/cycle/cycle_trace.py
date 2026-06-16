"""Mandatory per-cycle audit trace for AGI experiments."""
from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional


class CycleTrace:
    """Records every stage with timing and context-use flags."""

    def __init__(self, cycle_id: Optional[str] = None) -> None:
        self.cycle_id = cycle_id or str(uuid.uuid4())
        self._records: List[Dict[str, Any]] = []

    def record(
        self,
        stage: str,
        *,
        input_data: Any = None,
        output: Any = None,
        confidence: Optional[float] = None,
        duration_ms: Optional[float] = None,
        memory_used: bool = False,
        beliefs_used: bool = False,
        goal_used: bool = False,
        plan_used: bool = False,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        entry: Dict[str, Any] = {
            "cycle_id": self.cycle_id,
            "stage": stage,
            "input": input_data,
            "output": output,
            "confidence": confidence,
            "duration_ms": round(duration_ms, 2) if duration_ms is not None else None,
            "memory_used": memory_used,
            "beliefs_used": beliefs_used,
            "goal_used": goal_used,
            "plan_used": plan_used,
        }
        if extra:
            entry.update(extra)
        self._records.append(entry)

    def names(self) -> List[str]:
        return [r["stage"] for r in self._records]

    def to_list(self) -> List[Dict[str, Any]]:
        return list(self._records)
