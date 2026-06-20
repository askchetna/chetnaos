"""
Development — Tracks long-term growth of the organism across cycles.
"""
import os

from src.chetnaos.memory.json_loader import load_development, save_json, memory_path
from src.chetnaos.organism.developmental_age import DevelopmentalAge

DEV_FILE = os.path.join(os.path.dirname(__file__), "../../..", "memory", "development.json")

_TRAIT_DEFAULTS = {
    "curiosity": 0.5,
    "discipline": 0.5,
    "reflection": 0.5,
    "creativity": 0.5,
    "consistency": 0.5,
    "wisdom": 0.4,
    "research_maturity": 0.4,
}

_DEV_DEFAULT = {
    "total_cycles": 0,
    "good_cycles": 0,
    "poor_cycles": 0,
    "avg_confidence": 0.5,
    "growth_events": [],
    "traits": dict(_TRAIT_DEFAULTS),
    "recurring_themes": [],
    "recent_lessons": [],
    "developmental_age": "Seed",
}


class Development:
    def __init__(self):
        self._data = self._load()

    def _load(self) -> dict:
        loaded = load_development(dict(_DEV_DEFAULT))
        merged = dict(_DEV_DEFAULT)
        merged.update(loaded)
        traits = merged.get("traits") or {}
        for k, v in _TRAIT_DEFAULTS.items():
            traits.setdefault(k, v)
        merged["traits"] = traits
        return merged

    def _save(self):
        save_json(memory_path("development.json"), self._data)

    def _evolve_traits(self, quality: str, domain: str, confidence: float) -> None:
        traits = self._data.setdefault("traits", dict(_TRAIT_DEFAULTS))
        step = {"good": 0.003, "fair": 0.001, "poor": -0.002}.get(quality, 0.0)

        traits["reflection"] = min(1.0, max(0.0, traits.get("reflection", 0.5) + step))
        traits["consistency"] = min(1.0, max(0.0, traits.get("consistency", 0.5) + step * 0.8))
        if domain in ("research", "general", "technical"):
            traits["research_maturity"] = min(
                1.0, traits.get("research_maturity", 0.4) + step,
            )
        if quality == "good":
            traits["curiosity"] = min(1.0, traits.get("curiosity", 0.5) + 0.002)
            traits["wisdom"] = min(1.0, traits.get("wisdom", 0.4) + 0.001)
        if confidence >= 0.7:
            traits["discipline"] = min(1.0, traits.get("discipline", 0.5) + 0.001)

        themes = self._data.setdefault("recurring_themes", [])
        if domain and domain not in themes:
            themes.append(domain)
        self._data["recurring_themes"] = themes[-8:]

    def record(self, reflection: dict, confidence: float, *, domain: str = "general") -> dict:
        self._data["total_cycles"] = self._data.get("total_cycles", 0) + 1
        quality = reflection.get("quality", "fair")
        if quality == "good":
            self._data["good_cycles"] = self._data.get("good_cycles", 0) + 1
        elif quality == "poor":
            self._data["poor_cycles"] = self._data.get("poor_cycles", 0) + 1

        n = self._data["total_cycles"]
        old_avg = self._data.get("avg_confidence", 0.5)
        self._data["avg_confidence"] = round((old_avg * (n - 1) + confidence) / n, 3)

        self._evolve_traits(quality, domain, confidence)

        lesson = reflection.get("lesson") or reflection.get("why", "")
        if lesson and quality in ("good", "fair"):
            lessons = self._data.setdefault("recent_lessons", [])
            lessons.append(str(lesson)[:200])
            self._data["recent_lessons"] = lessons[-10:]

        self._save()
        return {"stage": "DEVELOP", "stats": dict(self._data)}

    def apply_age(self, identity: dict) -> str:
        stage = DevelopmentalAge.apply_to_development(self._data, identity)
        self._save()
        return stage

    def add_lesson(self, text: str) -> None:
        if not text:
            return
        lessons = self._data.setdefault("recent_lessons", [])
        lessons.append(text[:200])
        self._data["recent_lessons"] = lessons[-10:]
        self._save()

    def add_theme(self, theme: str) -> None:
        if not theme:
            return
        themes = self._data.setdefault("recurring_themes", [])
        if theme not in themes:
            themes.append(theme)
        self._data["recurring_themes"] = themes[-8:]
        self._save()
