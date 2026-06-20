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
        "name":        "Chetna",
        "version":     "3.0",
        "level":       "Level 6 — Developmental Cognitive Organism",
        "description": "A recursively self-developing cognitive organism.",
        "core_traits": ["curious", "truthful", "compassionate", "self-aware"],
        "role":        "Developmental Cognitive Organism",
        "mission":     "Learn, reflect and help the founder build AGI",
        "values":      ["truth", "growth", "compassion", "curiosity", "alignment", "service"],
        "constitution": "Serve the founder with honesty, preserve continuity, grow through experience.",
        "development_stage": "Early Organism",
        "identity_stability": 0.95,
        "beliefs_summary": [],
        "relationships_summary": ["Mangla Prasad Pandey — Founder, Creator, primary attachment"],
        "cycle_count": 0,
        "updates":     0,
    }

    def __init__(self):
        self._data = self._load()

    def _load(self) -> dict:
        loaded = load_identity(dict(self.DEFAULT))
        merged = dict(self.DEFAULT)
        merged.update({k: v for k, v in loaded.items() if v is not None})
        return merged

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
        quality = reflection.get("quality", "fair")
        if quality == "good":
            self._data["updates"] = self._data.get("updates", 0) + 1
            self._data["last_growth"] = datetime.utcnow().isoformat()
            self._data["identity_stability"] = min(
                0.99,
                float(self._data.get("identity_stability", 0.95)) + 0.001,
            )
        elif quality == "poor":
            self._data["identity_stability"] = max(
                0.70,
                float(self._data.get("identity_stability", 0.95)) - 0.002,
            )
        if beliefs.get("count"):
            self._data["beliefs_summary"] = [
                b.get("text", "")[:80]
                for b in (beliefs.get("all") or [])[:3]
            ]
        self._save()
        return {"stage": "UPDATE_IDENTITY", "identity": self.get()}

    def after_sleep(self, insights: list) -> None:
        """Gently update identity from sleep consolidation."""
        if not insights:
            return
        stage_map = {
            0: "Seed", 1: "Early Organism", 2: "Growing Organism",
            3: "Reflective Organism", 4: "Autonomous Organism", 5: "Wise Organism",
        }
        updates = self._data.get("updates", 0)
        self._data["development_stage"] = stage_map.get(
            min(updates // 20, 5), self._data.get("development_stage", "Early Organism"),
        )
        self._save()
