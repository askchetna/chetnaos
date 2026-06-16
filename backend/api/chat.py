"""POST /api/chat — organism chat path with conversation persistence."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

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


def _honesty_from_result(result: dict) -> list:
    """Extract honesty guard substitutions from ACT stage trace (no cycle change)."""
    for entry in result.get("trace", []):
        if entry.get("stage") == "ACT":
            return list(entry.get("honesty_guard") or [])
    return []


def _chat_meta(result: dict) -> dict:
    return {
        "cycle": result.get("cycle"),
        "quality": result.get("quality"),
        "confidence": result.get("confidence"),
        "confidence_level": result.get("confidence_level"),
        "dharma_score": result.get("dharma_score"),
        "cycle_score": result.get("cycle_score"),
        "domain": result.get("domain"),
        "intent": result.get("intent"),
        "beliefs_count": result.get("beliefs_count"),
        "health": result.get("health"),
        "slept": result.get("slept"),
        "stage_trace": result.get("stage_trace", []),
        "reality": result.get("reality", {}),
        "simulation": result.get("simulation", {}),
        "meta_cognition": result.get("meta_cognition", {}),
        "cognitive_organs": result.get("cognitive_organs", {}),
        "reasoning_integration": result.get("reasoning_integration", {}),
        "belief_changes": result.get("belief_changes", []),
        "contradiction_resolutions": result.get("contradiction_resolutions", []),
        "honesty_guard_changes": _honesty_from_result(result),
    }


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
        meta = _chat_meta(result)
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
