"""POST /api/goal — goal-directed cognitive cycle."""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.runtime import get_runtime

router = APIRouter()


class GoalRequest(BaseModel):
    goal: str
    context: Dict[str, Any] | None = None
    constraints: Dict[str, Any] | None = None


@router.post("/api/goal")
async def api_goal(payload: GoalRequest):
    text = (payload.goal or "").strip()
    if not text:
        raise HTTPException(400, "goal field required")
    rt = get_runtime()
    if not rt:
        raise HTTPException(503, "Runtime unavailable.")
    try:
        result = rt.process(text, mode="goal")
        return {
            "reply": result["reply"],
            "plan": result.get("stage_trace", []),
            "trace": result.get("trace", []),
            "world": result.get("reality", {}),
            "meta": {
                **{
                    k: result[k]
                    for k in (
                        "cycle",
                        "quality",
                        "confidence",
                        "dharma_score",
                        "cycle_score",
                        "domain",
                    )
                    if k in result
                },
                "cognitive_organs": result.get("cognitive_organs", {}),
                "reasoning_integration": result.get("reasoning_integration", {}),
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))
