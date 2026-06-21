"""GET /api/dashboard — full cognitive dashboard snapshot."""
from __future__ import annotations

import traceback

from fastapi import APIRouter

from backend.runtime import get_runtime

router = APIRouter()


@router.get("/api/dashboard")
async def api_dashboard():
    try:
        rt = get_runtime()
        if not rt:
            return {"available": False, "error": "Runtime unavailable."}
        snap = rt._cycle.dashboard_snapshot()
        snap["available"] = True
        return snap
    except Exception as e:
        traceback.print_exc()
        return {"available": False, "error": str(e)}
