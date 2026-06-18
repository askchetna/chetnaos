"""POST /api/chat — organism chat path with conversation persistence."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.api.meta import build_runtime_meta
from backend.conversation_store import get_conversation_store
from backend.runtime import get_runtime
from backend import workspace_store
from src.chetnaos.reasoning.conversation_context import (
    build_context_packet,
    merge_summary,
)

router = APIRouter()
_store = get_conversation_store()


class ChatRequest(BaseModel):
    text: str
    conversation_id: str | None = None


@router.post("/api/chat")
async def api_chat(payload: ChatRequest):
    text = (payload.text or "").strip()
    if not text:
        raise HTTPException(400, "text field required")
    rt = get_runtime()
    if not rt:
        raise HTTPException(503, "Cognitive runtime unavailable.")

    conv_id = payload.conversation_id
    conv = _store.get(conv_id) if conv_id else _store.get_active()
    if not conv:
        conv = _store.create()
        conv_id = conv["id"]
    else:
        conv_id = conv["id"]

    recent = _store.recent_messages(conv_id, limit=12)
    _store.append_message(conv_id, "user", text)

    active_goal = None
    try:
        active_goal = rt.active_goal
    except Exception:
        pass

    context_packet = build_context_packet(
        recent_messages=recent,
        active_goal=active_goal,
        conversation_summary=conv.get("summary", ""),
        relevant_memory=[],
    )

    try:
        result = rt.process(text, mode="chat", conversation_context=context_packet)
        reply = result["reply"]
        meta = build_runtime_meta(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

    _store.append_message(conv_id, "assistant", reply, meta=meta)
    new_summary = merge_summary(conv.get("summary", ""), text, reply)
    _store.update_summary(conv_id, new_summary)

    session = rt.session_snapshot()
    workspace_store.save_session({
        "active_conversation_id": conv_id,
        "active_goal": session.get("active_goal"),
        "current_thought": session.get("current_thought"),
        "working_memory": session.get("working_memory", []),
        "conversation_summary": new_summary,
    })

    return {
        "reply": reply,
        "meta": meta,
        "conversation_id": conv_id,
        "conversation_title": _store.get(conv_id).get("title") if _store.get(conv_id) else None,
    }


@router.post("/chetna")
async def chetna_legacy(payload: ChatRequest):
    text = (payload.text or "").strip()
    if not text:
        raise HTTPException(400, "text required")
    rt = get_runtime()
    if not rt:
        raise HTTPException(503, "Runtime unavailable.")
    try:
        return rt.process(text, mode="chat")
    except Exception as e:
        raise HTTPException(500, str(e))
