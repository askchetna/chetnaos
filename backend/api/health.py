"""GET /health — service health."""
from __future__ import annotations

from fastapi import APIRouter, Request

from backend.runtime import get_runtime

router = APIRouter()


@router.get("/health")
async def health(request: Request):
    settings = request.app.state.settings
    rt = get_runtime()
    return {
        "ok": True,
        "status": "ok",
        "service": "ChetnaOS",
        "version": "3.0.0",
        "architecture": "Single Runtime Developmental Cognitive Organism",
        "light_mode": settings.LIGHT_MODE,
        "embeddings_enabled": settings.EMBEDDINGS_ENABLED,
        "model": settings.GROQ_MODEL,
        "llm_available": rt.llm_available if rt else False,
        "cognitive_runtime": rt is not None,
    }
