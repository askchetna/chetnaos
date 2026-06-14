"""
Habit — Tracks repeated patterns and applies learned shortcuts.
"""
import json, os

HABIT_FILE = os.path.join(os.path.dirname(__file__), "../../..", "memory", "habits.json")


class Habit:
    def __init__(self):
        self._habits = self._load()

    def _load(self) -> dict:
        try:
            p = os.path.abspath(HABIT_FILE)
            if os.path.exists(p):
                with open(p) as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save(self):
        try:
            p = os.path.abspath(HABIT_FILE)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as f:
                json.dump(self._habits, f, indent=2)
        except Exception:
            pass

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
