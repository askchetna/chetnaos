"""Single stage result wrapper."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class StageResult:
    stage: str
    result: Dict[str, Any] = field(default_factory=dict)
    skipped: bool = False
    skip_reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"stage": self.stage, **self.result}
        if self.skipped:
            out["skipped"] = True
            out["skip_reason"] = self.skip_reason
        return out
