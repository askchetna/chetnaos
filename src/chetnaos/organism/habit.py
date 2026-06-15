"""
Habit — Tracks repeated patterns and applies learned shortcuts.
"""
import os

from src.chetnaos.memory.json_loader import load_habits, save_json, memory_path

HABIT_FILE = os.path.join(os.path.dirname(__file__), "../../..", "memory", "habits.json")


class Habit:
    def __init__(self):
        self._habits = self._load()

    def _load(self) -> dict:
        return load_habits({})

    def _save(self):
        save_json(memory_path("habits.json"), self._habits)

    def record(self, intent: str, domain: str):
        key = f"{intent}:{domain}"
        self._habits[key] = self._habits.get(key, 0) + 1
        self._save()

    def get_frequent(self) -> list:
        sorted_habits = sorted(self._habits.items(), key=lambda x: x[1], reverse=True)
        return [{"pattern": k, "count": v} for k, v in sorted_habits[:5]]

    def check(self, intent: str, domain: str) -> dict:
        key = f"{intent}:{domain}"
        count = self._habits.get(key, 0)
        return {"stage": "HABIT", "familiar": count > 3, "count": count, "pattern": key}
