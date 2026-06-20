"""
Episodic Memory Organ — temporal experience store with day-based recall.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta

from src.chetnaos.organism.experience import EXP_FILE


class EpisodicOrgan:
    def __init__(self, experience_module=None):
        self._experience = experience_module

    def _load_all(self) -> list[dict]:
        try:
            p = os.path.abspath(EXP_FILE)
            if not os.path.exists(p):
                return []
            with open(p, encoding="utf-8") as f:
                return [json.loads(line) for line in f if line.strip()]
        except Exception:
            return []

    def _by_day(self, day_offset: int = 0) -> list[dict]:
        target = (datetime.utcnow() - timedelta(days=day_offset)).strftime("%Y-%m-%d")
        return [
            e for e in self._load_all()
            if (e.get("timestamp") or "").startswith(target)
        ]

    def snapshot(self) -> dict:
        yesterday = self._by_day(1)
        today = self._by_day(0)
        recent = self._load_all()[-10:]
        return {
            "yesterday": {
                "count": len(yesterday),
                "highlights": [self._highlight(e) for e in yesterday[-3:]],
            },
            "today": {
                "count": len(today),
                "highlights": [self._highlight(e) for e in today[-3:]],
            },
            "recent_conversations": [self._highlight(e) for e in recent[-5:]],
            "achievements": [
                self._highlight(e) for e in recent
                if e.get("quality") == "good"
            ][-3:],
            "insights": [
                self._highlight(e) for e in recent
                if e.get("domain") not in (None, "general")
            ][-3:],
        }

    def what_changed_since_yesterday(self) -> str:
        y = self._by_day(1)
        t = self._by_day(0)
        if not y and not t:
            return "No episodic contrast yet — experiences are accumulating."
        parts = []
        if y:
            domains = {e.get("domain", "general") for e in y}
            parts.append(f"Yesterday touched {', '.join(sorted(domains))}.")
        if t:
            parts.append(f"Today: {len(t)} experience(s) so far.")
        return " ".join(parts)

    @staticmethod
    def _highlight(exp: dict) -> dict:
        return {
            "time": (exp.get("timestamp") or "")[:16],
            "domain": exp.get("domain", "general"),
            "input": (exp.get("input") or "")[:80],
            "quality": exp.get("quality", "fair"),
        }
