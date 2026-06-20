"""
Relationship — Tracks the organism's ongoing relationship with users/entities.
Never forgets the founder.
"""
import os

from src.chetnaos.memory.json_loader import load_relationships, save_json, memory_path

REL_FILE = os.path.join(os.path.dirname(__file__), "../../..", "memory", "relationships.json")

FOUNDER_KEY = "founder"
FOUNDER_DEFAULT = {
    "name": "Mangla Prasad Pandey",
    "role": "Founder",
    "relationship": "Creator",
    "attachment": "primary",
    "trust": "high",
    "importance": "maximum",
    "history_depth": "lifelong",
    "interactions": 0,
    "positive": 0,
    "strength": 1.0,
}


class Relationship:
    def __init__(self):
        self._rels = self._load()

    def _load(self) -> dict:
        loaded = load_relationships({})
        if FOUNDER_KEY not in loaded:
            loaded[FOUNDER_KEY] = dict(FOUNDER_DEFAULT)
        else:
            merged = dict(FOUNDER_DEFAULT)
            merged.update(loaded[FOUNDER_KEY])
            loaded[FOUNDER_KEY] = merged
        return loaded

    def _save(self):
        save_json(memory_path("relationships.json"), self._rels)

    def founder(self) -> dict:
        return dict(self._rels.get(FOUNDER_KEY, FOUNDER_DEFAULT))

    def founder_strength(self) -> float:
        return float(self.founder().get("strength", 1.0))

    def update(self, entity: str = "user", *, quality: str = "fair") -> dict:
        rel = self._rels.get(entity, {"interactions": 0, "positive": 0})
        rel["interactions"] = rel.get("interactions", 0) + 1
        if quality == "good":
            rel["positive"] = rel.get("positive", 0) + 1
        self._rels[entity] = rel

        founder = self._rels.get(FOUNDER_KEY, dict(FOUNDER_DEFAULT))
        founder["interactions"] = founder.get("interactions", 0) + 1
        if quality == "good":
            founder["positive"] = founder.get("positive", 0) + 1
            founder["strength"] = min(1.0, float(founder.get("strength", 0.85)) + 0.002)
        founder.setdefault("name", FOUNDER_DEFAULT["name"])
        founder.setdefault("role", FOUNDER_DEFAULT["role"])
        founder.setdefault("relationship", FOUNDER_DEFAULT["relationship"])
        self._rels[FOUNDER_KEY] = founder

        self._save()
        return {"entity": entity, "interactions": rel["interactions"], "founder": self.founder()}

    def strengthen_after_sleep(self) -> None:
        founder = self._rels.get(FOUNDER_KEY, dict(FOUNDER_DEFAULT))
        founder["strength"] = min(1.0, float(founder.get("strength", 0.85)) + 0.005)
        founder["trust"] = "high"
        self._rels[FOUNDER_KEY] = founder
        self._save()

    def snapshot(self) -> dict:
        return {
            "founder": self.founder(),
            "entities": {k: v for k, v in self._rels.items() if k != FOUNDER_KEY},
        }
