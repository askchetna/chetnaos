"""GET /api/state — lightweight runtime snapshot."""
from __future__ import annotations

import traceback

from fastapi import APIRouter

from backend.runtime import get_runtime

router = APIRouter()


@router.get("/api/state")
async def api_state():
    try:
        rt = get_runtime()
        if not rt:
            return {"error": "Runtime unavailable", "available": False}
        return {
            "available": True,
            "identity": rt.identity,
            "beliefs": rt.beliefs[:5],
            "world": rt.world,
            "development": rt.development,
            "llm": rt.llm_available,
            "cognitive_organs": rt.cognitive_organs,
        }
    except Exception as e:
        traceback.print_exc()
        return {
            "error": str(e),
            "available": False,
        }
