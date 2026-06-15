# ------------------------------
# World State Mini Model (v1.0)
# ------------------------------

from datetime import datetime

class WorldState:
    def __init__(self):
        self.state = {
            "time": None,
            "day": None,
            "energy": "stable",
            "news": "none",
            "ai_landscape": "normal"
        }

    def refresh(self):
        now = datetime.now()
        self.state["time"] = now.strftime("%H:%M")
        self.state["day"] = now.strftime("%A")

    def snapshot(self):
        return self.state