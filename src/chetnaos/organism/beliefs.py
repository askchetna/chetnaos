"""
Beliefs — Manages the organism's belief graph.
Beliefs are updated based on experience and reflection.
"""
import json, os
from datetime import datetime

BELIEF_FILE = os.path.join(os.path.dirname(__file__), "../../..", "memory", "beliefs.json")


class Beliefs:
    def __init__(self):
        self._beliefs = self._load()

    def _load(self) -> list:
        try:
            p = os.path.abspath(BELIEF_FILE)
            if os.path.exists(p):
                with open(p) as f:
                    return json.load(f)
        except Exception:
            pass
        return [
            {"id": 1, "text": "Truth is more valuable than comfort.", "confidence": 0.95, "source": "constitution"},
            {"id": 2, "text": "Users deserve accurate and helpful information.", "confidence": 0.95, "source": "constitution"},
            {"id": 3, "text": "Uncertainty should be acknowledged, not hidden.", "confidence": 0.90, "source": "constitution"},
        ]

    def _save(self):
        try:
            p = os.path.abspath(BELIEF_FILE)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as f:
                json.dump(self._beliefs, f, indent=2)
        except Exception:
            pass

    def get_all(self) -> list:
        return list(self._beliefs)

    def add(self, text: str, confidence: float = 0.6, source: str = "experience"):
        # Don't add duplicates
        for b in self._beliefs:
            if b["text"].lower() == text.lower():
                return
        new_id = max((b.get("id", 0) for b in self._beliefs), default=0) + 1
        self._beliefs.append({
            "id": new_id,
            "text": text[:200],
            "confidence": confidence,
            "source": source,
            "created": datetime.utcnow().isoformat(),
        })
        self._save()

    def update(self, reflection: dict, learning: dict) -> dict:
        # Strengthen beliefs that align with good outcomes
        quality = reflection.get("quality", "fair")
        if quality == "good":
            for b in self._beliefs:
                if b.get("source") == "constitution":
                    b["confidence"] = min(1.0, b.get("confidence", 0.9) + 0.01)

        # Add new beliefs from lessons
        for lesson in learning.get("lessons", []):
            if lesson.get("quality") == "good":
                self.add(lesson["lesson"], confidence=0.65, source="learning")

        self._save()
        return {
            "stage":  "UPDATE_BELIEFS",
            "count":  len(self._beliefs),
            "beliefs": self._beliefs[:5],
        }
