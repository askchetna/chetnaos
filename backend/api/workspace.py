"""Refresh-safe workspace session API."""
from __future__ import annotations

from fastapi import APIRouter

from backend.conversation_store import get_conversation_store
from backend.runtime import get_runtime
from backend import workspace_store

router = APIRouter()


@router.get("/api/workspace/session")
async def get_workspace_session():
    persisted = workspace_store.load_session()
    conv_store = get_conversation_store()
    active_conv = conv_store.get_active()
    rt = get_runtime()
    live = rt.session_snapshot() if rt else {}
    return {
        "active_conversation_id": (
            persisted.get("active_conversation_id")
            or (active_conv["id"] if active_conv else None)
        ),
        "active_goal": live.get("active_goal") or persisted.get("active_goal"),
        "current_thought": live.get("current_thought") or persisted.get("current_thought"),
        "working_memory": live.get("working_memory") or persisted.get("working_memory", []),
        "conversation": active_conv,
        "memory_influence": live.get("memory_influence", []),
        "belief_influence": live.get("belief_influence", []),
        "updated_at": persisted.get("updated_at"),
    }
