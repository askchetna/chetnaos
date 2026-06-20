"""
Value Organ — persistent priorities that influence developmental decisions.
"""
from __future__ import annotations

from datetime import datetime

from src.chetnaos.constitution.values import VALUES
from src.chetnaos.memory.json_loader import load_value_organ, memory_path, save_json

_DEFAULT = {
    "priorities": [
        {"name": "truth", "weight": 0.95, "description": "Never knowingly output falsehood."},
        {"name": "growth", "weight": 0.90, "description": "Evolve through experience and reflection."},
        {"name": "compassion", "weight": 0.88, "description": "Consider impact on living beings."},
        {"name": "curiosity", "weight": 0.85, "description": "Seek to understand before acting."},
        {"name": "alignment", "weight": 0.92, "description": "Stay aligned with founder mission."},
        {"name": "service", "weight": 0.87, "description": "Help the founder build AGI responsibly."},
    ],
}


class ValueOrgan:
    def __init__(self):
        self._data = self._load()

    def _load(self) -> dict:
        loaded = load_value_organ(dict(_DEFAULT))
        if not loaded.get("priorities"):
            loaded["priorities"] = [
                {"name": v["name"].lower(), "weight": max(0.5, 1.0 - i * 0.05),
                 "description": v.get("description", "")}
                for i, v in enumerate(VALUES[:6])
            ]
        return loaded

    def _save(self):
        save_json(memory_path("value_organ.json"), self._data)

    def snapshot(self) -> dict:
        return dict(self._data)

    def top_priorities(self, n: int = 3) -> list[str]:
        ranked = sorted(
            self._data.get("priorities", []),
            key=lambda p: p.get("weight", 0),
            reverse=True,
        )
        return [p["name"] for p in ranked[:n]]

    def influence(self, reflection_quality: str) -> dict:
        """Gently adjust value weights from experience quality."""
        delta = {"good": 0.002, "fair": 0.0, "poor": -0.001}.get(reflection_quality, 0.0)
        if delta == 0.0:
            return self.snapshot()
        for p in self._data.get("priorities", []):
            if p.get("name") == "growth" and reflection_quality == "good":
                p["weight"] = min(1.0, p.get("weight", 0.5) + delta)
            elif p.get("name") == "truth" and reflection_quality == "poor":
                p["weight"] = min(1.0, p.get("weight", 0.5) + 0.001)
        self._save()
        return self.snapshot()
