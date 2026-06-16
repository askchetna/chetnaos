"""UI session persistence — survives browser refresh."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import json

from src.chetnaos.memory.json_loader import memory_path, save_json

_SESSION_FILE = "ui_session.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _empty() -> dict:
    return {
        "active_conversation_id": None,
        "active_goal": None,
        "current_thought": None,
        "working_memory": [],
        "conversation_summary": "",
        "updated_at": None,
    }


def load_session() -> dict:
    path = memory_path(_SESSION_FILE)
    try:
        if path.exists():
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = _empty()
    except Exception:
        data = _empty()
    if not isinstance(data, dict):
        return _empty()
    return {**_empty(), **data}


def save_session(patch: dict[str, Any]) -> dict:
    data = {**load_session(), **patch, "updated_at": _now()}
    save_json(memory_path(_SESSION_FILE), data)
    return data
