"""GET /api/debug/embeddings — embedding subsystem diagnostics."""
from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/api/debug/embeddings")
async def debug_embeddings(request: Request):
    from memory.db import (
        is_embedding_model_loaded,
        memory_db,
    )
    from memory.embedding_config import get_embeddings_enabled, get_light_mode

    stats = memory_db.statistics()
    settings = getattr(request.app.state, "settings", None)

    return {
        "light_mode": get_light_mode(),
        "embeddings_enabled": get_embeddings_enabled(),
        "settings_light_mode": getattr(settings, "LIGHT_MODE", None),
        "settings_embeddings_enabled": getattr(settings, "EMBEDDINGS_ENABLED", None),
        "total_memories": stats.get("total", 0),
        "with_embedding": stats.get("with_embedding", 0),
        "without_embedding": stats.get("without_embedding", 0),
        "embedding_model_loaded": is_embedding_model_loaded(),
        "db_path": stats.get("db_path"),
    }
