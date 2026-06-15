"""
Agent API — routes agent mode through the cognitive organism.

Tools execute inside CognitiveCycle; reasoning synthesizes the final reply.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api")


@router.post("/agent")
async def agent_chat(payload: dict, request: Request):
    try:
        raw_message = payload.get("text") or payload.get("message") or ""
        user_message = str(raw_message).strip()
        if not user_message:
            return {"reply": "Ask me anything about ChetnaOS.", "tool": "llm"}

        from src.chetnaos.orchestrator.runtime import ChetnaRuntime

        rt = ChetnaRuntime()
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
