"""
World Model — Symbolic model of the current world state.
"""
from datetime import datetime


class WorldModel:
    def __init__(self):
        self._state = {
            "timestamp": None,
            "active_topics": [],
            "known_entities": {},
            "interaction_count": 0,
        }

    def update(self, attention: dict, abstraction: dict) -> dict:
        self._state["timestamp"] = datetime.utcnow().isoformat()
        self._state["active_topics"] = abstraction.get("abstract_tags", [])
        self._state["domain"] = abstraction.get("domain", "general")
        self._state["interaction_count"] += 1

        for entity in attention.get("focus", []):
            self._state["known_entities"][entity] = self._state["known_entities"].get(entity, 0) + 1

        return {"stage": "WORLD_UPDATE", "world": dict(self._state)}

    def snapshot(self) -> dict:
        return dict(self._state)
