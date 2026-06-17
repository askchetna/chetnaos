"""GET /api/memory_trace — last memory recall diagnostic trace."""
from __future__ import annotations

from fastapi import APIRouter

from backend.runtime import get_runtime

router = APIRouter()


@router.get("/api/memory_trace")
async def api_memory_trace():
    rt = get_runtime()
    if not rt:
        return {"available": False, "error": "Runtime unavailable."}
    trace = getattr(rt._cycle, "_last_memory_trace", {}) or {}
    stats = {}
    try:
        from src.chetnaos.memory.store import get_memory_store
        stats = get_memory_store().statistics()
    except Exception:
        pass
    return {
        "available": True,
        "trace": trace,
        "db_statistics": stats,
    }
