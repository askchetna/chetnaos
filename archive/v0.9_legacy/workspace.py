"""
Workspace — Short-term working memory for the current cognitive cycle.
Holds all intermediate state as the cycle progresses.
"""
from datetime import datetime


class Workspace:
    def __init__(self):
        self.reset()

    def reset(self):
        self._state = {
            "cycle_id": None,
            "input":    None,
            "percept":  None,
            "attention": None,
            "recalled": [],
            "predictions": [],
            "imagined":  [],
            "plan":      None,
            "decision":  None,
            "response":  None,
            "reality":   None,
            "reflection": None,
            "created_at": datetime.utcnow().isoformat(),
        }

    def set(self, key: str, value):
        self._state[key] = value

    def get(self, key: str, default=None):
        return self._state.get(key, default)

    def snapshot(self) -> dict:
        return dict(self._state)
