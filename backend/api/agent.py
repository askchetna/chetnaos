"""
POST /api/agent — agent mode through CognitiveCycle (no parallel Groq path).
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from backend.runtime import get_runtime

router = APIRouter()


@router.post("/api/agent")
async def agent_chat(payload: dict):
    try:
        raw_message = payload.get("text") or payload.get("message") or ""
        user_message = str(raw_message).strip()
        if not user_message:
            return {"reply": "Ask me anything about ChetnaOS.", "tool": "llm"}

        rt = get_runtime()
        if not rt:
            raise HTTPException(503, "Cognitive runtime unavailable.")

        result = rt.process(user_message, mode="agent")
        tool = result.get("agent_tool") or "llm"
        return {
            "reply": result["reply"],
            "tool": tool,
            "meta": {
                "cycle": result.get("cycle"),
                "quality": result.get("quality"),
                "confidence": result.get("confidence"),
                "domain": result.get("domain"),
                "intent": result.get("intent"),
                "stage_trace": result.get("stage_trace", []),
                "cognitive_organs": result.get("cognitive_organs", {}),
                "reasoning_integration": result.get("reasoning_integration", {}),
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse({"error": f"Agent error: {str(e)}"}, status_code=500)
