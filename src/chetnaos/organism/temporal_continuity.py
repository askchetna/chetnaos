"""
Temporal Continuity Organ — yesterday, today, tomorrow, recent changes.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from src.chetnaos.memory.json_loader import load_temporal_continuity, memory_path, save_json

_DEFAULT = {
    "yesterday_summary": "",
    "today_summary": "",
    "tomorrow_intentions": [],
    "recent_changes": [],
    "last_session_at": None,
    "days_active": 0,
}


class TemporalContinuity:
    def __init__(self):
        self._data = self._load()
        self._today_key = datetime.utcnow().strftime("%Y-%m-%d")

    def _load(self) -> dict:
        return load_temporal_continuity(dict(_DEFAULT))

    def _save(self):
        save_json(memory_path("temporal_continuity.json"), self._data)

    def tick(
        self,
        *,
        user_input: str,
        domain: str,
        quality: str,
        focus: str = "",
    ) -> dict:
        now = datetime.utcnow()
        today = now.strftime("%Y-%m-%d")
        last = self._data.get("last_session_at")

        if last:
            try:
                last_day = datetime.fromisoformat(last.replace("Z", "")).strftime("%Y-%m-%d")
                if last_day != today:
                    self._data["yesterday_summary"] = self._data.get("today_summary", "")
                    self._data["days_active"] = self._data.get("days_active", 0) + 1
                    self._data["today_summary"] = ""
            except Exception:
                pass

        snippet = f"{domain}: {user_input[:80]}"
        today_sum = self._data.get("today_summary", "")
        self._data["today_summary"] = (today_sum + " · " + snippet).strip(" · ")[:400]

        change = f"{today} — {quality} response in {domain}"
        changes = self._data.get("recent_changes", [])
        if not changes or changes[-1] != change:
            changes.append(change)
        self._data["recent_changes"] = changes[-12:]

        if focus and focus not in self._data.get("tomorrow_intentions", []):
            intents = self._data.get("tomorrow_intentions", [])
            intents.insert(0, focus[:120])
            self._data["tomorrow_intentions"] = intents[:5]

        self._data["last_session_at"] = now.isoformat()
        self._save()
        return self.snapshot()

    def what_changed_since_yesterday(self) -> str:
        y = self._data.get("yesterday_summary", "")
        t = self._data.get("today_summary", "")
        if not y and not t:
            return "Each day is a fresh beginning — continuity is still forming."
        if not y:
            return f"Today so far: {t[:200]}"
        return f"Yesterday: {y[:120]}. Today: {t[:120]}."

    def snapshot(self) -> dict:
        return dict(self._data)
