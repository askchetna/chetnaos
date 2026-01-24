"""
ChetnaOS Backend - Unified FastAPI Application
Run with: python -m uvicorn backend.app:app --reload
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Any, Dict

from .chetna_core import ChetnaCore
from .api import setup_kalpavriksha_routes
from .agent import router as agent_router
from .agi.goal_agent import execute_goal
from .config import get_settings

app = FastAPI(
    title="ChetnaOS API",
    description="Conscious Runtime + Kalpavriksha Intelligence Suite",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global settings & core initialization
settings = get_settings()
core = ChetnaCore()


@app.on_event("startup")
async def on_startup() -> None:
    """
    Lightweight startup hook to attach settings and log LIGHT_MODE status.
    Keeps boot fast while making runtime mode visible in logs.
    """
    app.state.settings = settings
    print(
        f"[ChetnaOS] Startup - LIGHT_MODE={settings.LIGHT_MODE}, "
        f"EMBEDDINGS_ENABLED={settings.EMBEDDINGS_ENABLED}, "
        f"GROQ_MODEL={settings.GROQ_MODEL}"
    )


class ChatRequest(BaseModel):
    text: str


class GoalRequest(BaseModel):
    goal: str
    context: Dict[str, Any] | None = None
    constraints: Dict[str, Any] | None = None


@app.post("/api/chat")
async def api_chat(payload: ChatRequest):
    """
    Primary chat endpoint for ChetnaOS UI.
    Returns a simple {"reply": "..."} structure for the frontend.
    """
    try:
        text = payload.text
        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="Text field is required")

        result = core.process(text)

        # If core already returns a reply string, pass it through; otherwise stringify.
        if isinstance(result, dict) and isinstance(result.get("reply"), str):
            return {"reply": result["reply"]}
        return {"reply": str(result)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/goal")
async def api_goal(payload: GoalRequest):
    """
    Goal-oriented AGI endpoint.

    Returns a primary reply plus an optional plan/trace/world bundle for
    advanced clients and evaluation tools.
    """
    text = (payload.goal or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Goal field is required")

    try:
        result = execute_goal(
            {
                "goal": text,
                "context": payload.context or {},
                "constraints": payload.constraints or {},
            }
        )

        # High-level summary for UI
        final_step = result.steps[-1] if result.steps else None
        reply = (
            final_step.system_output.get("filtered")
            if final_step and isinstance(final_step.system_output, dict)
            else None
        ) or (final_step.system_output if final_step else "") or result.goal.text

        return {
            "reply": reply,
            "terminated_reason": result.terminated_reason,
            "plan": [s.system_output for s in result.steps],
            "trace": [s.dict() for s in result.steps],
            "world": result.final_world_state,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chetna")
async def chetna_route(payload: ChatRequest):
    """Legacy ChetnaOS conscious runtime endpoint (kept for backwards compatibility)."""
    try:
        text = payload.text
        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="Text field is required")
        return core.process(text)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint (must always work, even in LIGHT_MODE)."""
    return {
        "ok": True,
        "status": "ok",
        "service": "ChetnaOS",
        "light_mode": settings.LIGHT_MODE,
        "embeddings_enabled": settings.EMBEDDINGS_ENABLED,
        "model": settings.GROQ_MODEL,
    }


setup_kalpavriksha_routes(app)
app.include_router(agent_router)


#if __name__ == "__main__":
    #import uvicorn
    #uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
