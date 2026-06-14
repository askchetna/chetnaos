"""
Relationship — Tracks the organism's ongoing relationship with users/entities.
"""
import json, os

REL_FILE = os.path.join(os.path.dirname(__file__), "../../..", "memory", "relationships.json")


class Relationship:
    def __init__(self):
        self._rels = self._load()

    def _load(self) -> dict:
        try:
            p = os.path.abspath(REL_FILE)
            if os.path.exists(p):
                with open(p) as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save(self):
        try:
            p = os.path.abspath(REL_FILE)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as f:
                json.dump(self._rels, f, indent=2)
        except Exception:
            pass

    def update(self, entity: str = "user") -> dict:
        rel = self._rels.get(entity, {"interactions": 0, "positive": 0})
        rel["interactions"] = rel.get("interactions", 0) + 1
        self._rels[entity] = rel
        self._save()
        return {"entity": entity, "interactions": rel["interactions"]}
