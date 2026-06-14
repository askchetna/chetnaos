"""
Development — Tracks long-term growth of the organism across cycles.
"""
import json, os

DEV_FILE = os.path.join(os.path.dirname(__file__), "../../..", "memory", "development.json")


class Development:
    def __init__(self):
        self._data = self._load()

    def _load(self) -> dict:
        try:
            p = os.path.abspath(DEV_FILE)
            if os.path.exists(p):
                with open(p) as f:
                    return json.load(f)
        except Exception:
            pass
        return {"total_cycles": 0, "good_cycles": 0, "poor_cycles": 0, "avg_confidence": 0.5, "growth_events": []}

    def _save(self):
        try:
            p = os.path.abspath(DEV_FILE)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as f:
                json.dump(self._data, f, indent=2)
        except Exception:
            pass

    def record(self, reflection: dict, confidence: float) -> dict:
        self._data["total_cycles"] = self._data.get("total_cycles", 0) + 1
        quality = reflection.get("quality", "fair")
        if quality == "good":
            self._data["good_cycles"] = self._data.get("good_cycles", 0) + 1
        elif quality == "poor":
            self._data["poor_cycles"] = self._data.get("poor_cycles", 0) + 1

        n = self._data["total_cycles"]
        old_avg = self._data.get("avg_confidence", 0.5)
        self._data["avg_confidence"] = round((old_avg * (n - 1) + confidence) / n, 3)
        self._save()
        return {"stage": "DEVELOP", "stats": dict(self._data)}
