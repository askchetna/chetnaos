"""
Purpose — Manages the organism's evolving sense of purpose.
Purpose starts from the constitution and refines through experience.
"""
import json
import os

PURPOSE_FILE = os.path.join(os.path.dirname(__file__), "../../..", "memory", "purpose.json")


class Purpose:
    DEFAULT = {
        "statement": "Understand the user's need and respond with clarity, truth, and compassion.",
        "refinements": 0,
        "version": 1,
    }

    def __init__(self):
        self._data = self._load()

    def _load(self) -> dict:
        try:
            path = os.path.abspath(PURPOSE_FILE)
            if os.path.exists(path):
                with open(path) as f:
                    return json.load(f)
        except Exception:
            pass
        return dict(self.DEFAULT)

    def _save(self):
        try:
            path = os.path.abspath(PURPOSE_FILE)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                json.dump(self._data, f, indent=2)
        except Exception:
            pass

    def get(self) -> dict:
        return {"stage": "PURPOSE", **self._data}

    def refine(self, reflection: str):
        """Refine purpose based on a reflection insight."""
        self._data["last_refinement"] = reflection[:200]
        self._data["refinements"] = self._data.get("refinements", 0) + 1
        self._data["version"] = self._data.get("version", 1) + 1
        self._save()
