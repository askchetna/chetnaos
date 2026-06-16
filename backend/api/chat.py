"""POST /api/chat — organism chat path."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.runtime import get_runtime

router = APIRouter()


class ChatRequest(BaseModel):
    text: str


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
    }


@router.post("/api/chat")
async def api_chat(payload: ChatRequest):
    text = (payload.text or "").strip()
    if not text:
        raise HTTPException(400, "text field required")
    rt = get_runtime()
    if not rt:
        raise HTTPException(503, "Cognitive runtime unavailable.")
    try:
        result = rt.process(text, mode="chat")
        return {"reply": result["reply"], "meta": _chat_meta(result)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


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
