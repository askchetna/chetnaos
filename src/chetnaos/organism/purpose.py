"""
Purpose — Manages the organism's evolving sense of purpose.
Purpose starts from the constitution and refines through experience.
"""
import os

from src.chetnaos.memory.json_loader import load_purpose, save_json, memory_path

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
        return load_purpose(dict(self.DEFAULT))

    def _save(self):
        save_json(memory_path("purpose.json"), self._data)

    def get(self) -> dict:
        return {"stage": "PURPOSE", **self._data}

    def refine(self, reflection: str):
        """Refine purpose based on a reflection insight."""
        self._data["last_refinement"] = reflection[:200]
        self._data["refinements"] = self._data.get("refinements", 0) + 1
        self._data["version"] = self._data.get("version", 1) + 1
        self._save()
