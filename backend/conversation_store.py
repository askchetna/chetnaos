"""Persistent conversation storage — JSON layer under memory/."""
from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from typing import Any

import json

from src.chetnaos.memory.json_loader import memory_path, save_json

_STORE_FILE = "conversations.json"
_MAX_CONVERSATIONS = 200
_MAX_MESSAGES_PER_CONV = 500


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _empty_store() -> dict:
    return {"active_id": None, "conversations": []}


def _load() -> dict:
    path = memory_path(_STORE_FILE)
    try:
        if path.exists():
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = _empty_store()
    except Exception:
        data = _empty_store()
    if not isinstance(data, dict):
        return _empty_store()
    data.setdefault("active_id", None)
    data.setdefault("conversations", [])
    return data


def _save(data: dict) -> None:
    data["conversations"] = data.get("conversations", [])[:_MAX_CONVERSATIONS]
    save_json(memory_path(_STORE_FILE), data)


def _title_from_text(text: str) -> str:
    clean = re.sub(r"\s+", " ", (text or "").strip())
    if not clean:
        return "New conversation"
    return (clean[:48] + "…") if len(clean) > 48 else clean


class ConversationStore:
    def list_conversations(self) -> list[dict]:
        data = _load()
        items = sorted(
            data.get("conversations", []),
            key=lambda c: c.get("updated_at", ""),
            reverse=True,
        )
        return [
            {
                "id": c["id"],
                "title": c.get("title", "Untitled"),
                "updated_at": c.get("updated_at"),
                "message_count": len(c.get("messages", [])),
            }
            for c in items
        ]

    def get(self, conv_id: str) -> dict | None:
        for c in _load().get("conversations", []):
            if c.get("id") == conv_id:
                return c
        return None

    def get_active(self) -> dict | None:
        data = _load()
        active_id = data.get("active_id")
        if active_id:
            conv = self.get(active_id)
            if conv:
                return conv
        convs = data.get("conversations", [])
        return convs[0] if convs else None

    def set_active(self, conv_id: str) -> dict | None:
        data = _load()
        conv = self.get(conv_id)
        if not conv:
            return None
        data["active_id"] = conv_id
        _save(data)
        return conv

    def create(self, title: str = "New conversation") -> dict:
        data = _load()
        conv = {
            "id": str(uuid.uuid4()),
            "title": title,
            "summary": "",
            "created_at": _now(),
            "updated_at": _now(),
            "messages": [],
        }
        data["conversations"].insert(0, conv)
        data["active_id"] = conv["id"]
        _save(data)
        return conv

    def delete(self, conv_id: str) -> bool:
        data = _load()
        before = len(data.get("conversations", []))
        data["conversations"] = [
            c for c in data.get("conversations", []) if c.get("id") != conv_id
        ]
        if len(data["conversations"]) == before:
            return False
        if data.get("active_id") == conv_id:
            data["active_id"] = (
                data["conversations"][0]["id"] if data["conversations"] else None
            )
        _save(data)
        return True

    def append_message(
        self,
        conv_id: str,
        role: str,
        content: str,
        meta: dict | None = None,
    ) -> dict | None:
        data = _load()
        for conv in data.get("conversations", []):
            if conv.get("id") != conv_id:
                continue
            conv.setdefault("messages", []).append({
                "role": role,
                "content": content,
                "meta": meta or {},
                "ts": _now(),
            })
            conv["messages"] = conv["messages"][-_MAX_MESSAGES_PER_CONV:]
            conv["updated_at"] = _now()
            if role == "user" and (
                conv.get("title") in ("New conversation", "Untitled", "")
                or len(conv["messages"]) <= 2
            ):
                conv["title"] = _title_from_text(content)
            data["active_id"] = conv_id
            _save(data)
            return conv
        return None

    def update_summary(self, conv_id: str, summary: str) -> None:
        data = _load()
        for conv in data.get("conversations", []):
            if conv.get("id") == conv_id:
                conv["summary"] = (summary or "")[:2000]
                conv["updated_at"] = _now()
                _save(data)
                return

    def recent_messages(self, conv_id: str, limit: int = 12) -> list[dict]:
        conv = self.get(conv_id)
        if not conv:
            return []
        return list(conv.get("messages", []))[-limit:]


_store: ConversationStore | None = None


def get_conversation_store() -> ConversationStore:
    global _store
    if _store is None:
        _store = ConversationStore()
    return _store
