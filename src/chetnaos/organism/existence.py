"""
Existence — The organism's baseline awareness that it IS.
This is the first stage of every cognitive cycle.
"""
from datetime import datetime


class Existence:
    def __init__(self):
        self.birth_time = datetime.utcnow()
        self.cycle_count = 0

    def pulse(self) -> dict:
        """I exist. I am aware. I am in a cycle."""
        self.cycle_count += 1
        return {
            "stage": "EXIST",
            "alive": True,
            "cycle": self.cycle_count,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": (datetime.utcnow() - self.birth_time).total_seconds(),
        }
