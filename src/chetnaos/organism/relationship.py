"""
Relationship — Tracks the organism's ongoing relationship with users/entities.
"""
import os

from src.chetnaos.memory.json_loader import load_relationships, save_json, memory_path

REL_FILE = os.path.join(os.path.dirname(__file__), "../../..", "memory", "relationships.json")


class Relationship:
    def __init__(self):
        self._rels = self._load()

    def _load(self) -> dict:
        return load_relationships({})

    def _save(self):
        save_json(memory_path("relationships.json"), self._rels)

    def update(self, entity: str = "user") -> dict:
        rel = self._rels.get(entity, {"interactions": 0, "positive": 0})
        rel["interactions"] = rel.get("interactions", 0) + 1
        self._rels[entity] = rel
        self._save()
        return {"entity": entity, "interactions": rel["interactions"]}
