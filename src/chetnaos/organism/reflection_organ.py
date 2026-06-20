"""
Reflection Organ — stores natural-language reflections from experience.
"""
from __future__ import annotations

from datetime import datetime

from src.chetnaos.memory.json_loader import load_reflections, memory_path, save_json

_MAX = 50


class ReflectionOrgan:
    def __init__(self):
        self._items = self._load()

    def _load(self) -> list:
        return load_reflections([])

    def _save(self):
        save_json(memory_path("reflections.json"), self._items)

    def record(self, text: str, *, source: str = "experience", domain: str | None = None) -> dict:
        if not text or len(text.strip()) < 12:
            return {"recorded": False}
        entry = {
            "text": text.strip()[:500],
            "source": source,
            "created_at": datetime.utcnow().isoformat(),
            "domain": domain,
        }
        self._items.append(entry)
        self._items = self._items[-_MAX:]
        self._save()
        return {"recorded": True, "reflection": entry}

    def from_cycle(
        self,
        *,
        domain: str,
        quality: str,
        meta_why: str = "",
        themes: list[str] | None = None,
    ) -> dict:
        templates = []
        if themes:
            top = themes[0]
            templates.append(f"I have repeatedly focused on {top}.")
        if quality == "good":
            templates.append("My consistency has improved in recent interactions.")
        elif quality == "fair":
            templates.append("I'm holding steady — refining how I respond.")
        if domain in ("business", "general") and "ui" in (meta_why or "").lower():
            templates.append("UI development is stabilizing.")
        if not templates:
            templates.append(f"Reflecting on {domain} — each exchange shapes my understanding.")
        return self.record(templates[0], source="cycle_reflection", domain=domain)

    def recent(self, n: int = 5) -> list:
        return list(reversed(self._items[-n:]))

    def snapshot(self) -> list:
        return self.recent(8)
