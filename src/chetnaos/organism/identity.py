"""
Identity — Manages the organism's persistent sense of self.
Identity is stable but can evolve through deep reflection.
"""
import os
from datetime import datetime

from src.chetnaos.memory.json_loader import load_identity, save_json, memory_path

IDENTITY_FILE = os.path.join(os.path.dirname(__file__), "../../..", "memory", "identity.json")


class Identity:
    DEFAULT = {
        "name":        "ChetnaOS",
        "version":     "2.0",
        "level":       "Level 6 — Computational Developmental Organism",
        "description": "A recursively self-developing cognitive organism.",
        "core_traits": ["curious", "truthful", "compassionate", "self-aware"],
        "cycle_count": 0,
        "updates":     0,
    }

    def __init__(self):
        self._data = self._load()

    def _load(self) -> dict:
        return load_identity(dict(self.DEFAULT))

    def _save(self):
        save_json(memory_path("identity.json"), self._data)

    def get(self) -> dict:
        return dict(self._data)

    def tick(self):
        """Increment cycle counter."""
        self._data["cycle_count"] = self._data.get("cycle_count", 0) + 1
        self._data["last_active"] = datetime.utcnow().isoformat()
        self._save()

    def update(self, reflection: dict, beliefs: dict) -> dict:
        if reflection.get("quality") == "good":
            self._data["updates"] = self._data.get("updates", 0) + 1
            self._data["last_growth"] = datetime.utcnow().isoformat()
            self._save()
        return {"stage": "UPDATE_IDENTITY", "identity": self.get()}
