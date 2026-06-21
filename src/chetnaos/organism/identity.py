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
        "type":        "Cognitive AI System",
        "level":       "Level 6 — Cognitive AI System",
        "description": "A cognitive AI system with memory, goals, and reasoning.",
        "biological":  False,
        "animal":      False,
        "living_organism": False,
        "core_traits": ["curious", "truthful", "compassionate", "reflective"],
        "role":        "Cognitive AI System",
        "mission":     "Serve with truth and compassion.",
        "values":      ["truth", "growth", "compassion", "curiosity", "alignment", "service"],
        "constitution": "Serve with truth and compassion; preserve continuity; grow through experience.",
        "development_stage": "Seed",
        "identity_stability": 0.95,
        "beliefs_summary": [],
        "relationships_summary": ["Mangla Prasad Pandey — Founder, Creator, primary attachment"],
        "cycle_count": 0,
        "updates":     0,
    }

    def __init__(self):
        self._data = self._load()

    def _load(self) -> dict:
        from src.chetnaos.memory.identity_guard import scrub_identity_record

        loaded = load_identity(dict(self.DEFAULT))
        merged = dict(self.DEFAULT)
        merged.update({k: v for k, v in loaded.items() if v is not None})
        return scrub_identity_record(merged)

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
            0: "Seed", 1: "Early Stage", 2: "Growing Stage",
            3: "Reflective Stage", 4: "Autonomous Stage", 5: "Wise Stage",
        }
        updates = self._data.get("updates", 0)
        self._data["development_stage"] = stage_map.get(
            min(updates // 20, 5), self._data.get("development_stage", "Seed"),
        )
        self._save()
