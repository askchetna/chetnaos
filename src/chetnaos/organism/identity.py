"""
Identity — Manages the organism's persistent sense of self.
Identity is stable but can evolve through deep reflection.
"""
import json, os
from datetime import datetime

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
        try:
            p = os.path.abspath(IDENTITY_FILE)
            if os.path.exists(p):
                with open(p) as f:
                    return json.load(f)
        except Exception:
            pass
        return dict(self.DEFAULT)

    def _save(self):
        try:
            p = os.path.abspath(IDENTITY_FILE)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as f:
                json.dump(self._data, f, indent=2)
        except Exception:
            pass

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
