"""
POST /api/agent — agent mode through CognitiveCycle (no parallel Groq path).
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from backend.api.meta import build_runtime_meta
from backend.runtime import get_runtime

router = APIRouter()


@router.post("/api/agent")
async def agent_chat(payload: dict):
    try:
        raw_message = payload.get("text") or payload.get("message") or ""
        user_message = str(raw_message).strip()
        if not user_message:
            return {"reply": "Ask me anything about ChetnaOS.", "tool": "llm", "meta": {}}

        rt = get_runtime()
        if not rt:
            raise HTTPException(503, "Cognitive runtime unavailable.")

        result = rt.process(user_message, mode="agent")
        tool = result.get("agent_tool") or "llm"
        return {
            "reply": result["reply"],
            "tool": tool,
            "meta": build_runtime_meta(result),
        }
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse({"error": f"Agent error: {str(e)}"}, status_code=500)
