"""
ChetnaOS Backend — FastAPI Application
Powered by the Developmental Cognitive Architecture v2.0
Run: python -m uvicorn backend.app:app --reload
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Any, Dict

from .config import get_settings
from .api import setup_kalpavriksha_routes
from .agent import router as agent_router

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

app = FastAPI(
    title="ChetnaOS API",
    description="Developmental Cognitive Architecture v2.0 — Level 6 Computational Developmental Organism",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

settings = get_settings()

# ── Lazy-load the cognitive runtime (heavy, singleton) ──
_runtime = None

def get_runtime():
    global _runtime
    if _runtime is None:
        try:
            from src.chetnaos.orchestrator.runtime import ChetnaRuntime
            _runtime = ChetnaRuntime()
        except Exception as e:
            print(f"[ChetnaOS] Warning: Could not initialise cognitive runtime: {e}")
            _runtime = None
    return _runtime


@app.on_event("startup")
async def on_startup():
    app.state.settings = settings
    print(
        f"[ChetnaOS v2.0] Startup — LIGHT_MODE={settings.LIGHT_MODE}, "
        f"GROQ_MODEL={settings.GROQ_MODEL}"
    )
    # Pre-warm the runtime
    rt = get_runtime()
    if rt:
        print(f"[ChetnaOS v2.0] Cognitive Runtime ready — "
              f"LLM={'✓' if rt.llm_available else '✗ (GROQ_API_KEY missing)'}")
    else:
        print("[ChetnaOS v2.0] Running in legacy mode (runtime unavailable).")


# ── Request/Response models ──────────────────────────────────────────────────

class ChatRequest(BaseModel):
    text: str

class GoalRequest(BaseModel):
    goal: str
    context: Dict[str, Any] | None = None
    constraints: Dict[str, Any] | None = None


# ── Core endpoints ───────────────────────────────────────────────────────────

@app.post("/api/chat")
async def api_chat(payload: ChatRequest):
    """Primary chat endpoint — runs the full 27-stage cognitive cycle."""
    text = (payload.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text field is required")

    rt = get_runtime()
    if not rt:
        raise HTTPException(status_code=503,
                            detail="Cognitive runtime unavailable. Check server logs.")

    try:
        result = rt.process(text, mode="chat")
        return {
            "reply":      result["reply"],
            "meta": {
                "cycle":           result.get("cycle"),
                "quality":         result.get("quality"),
                "confidence":      result.get("confidence"),
                "confidence_level": result.get("confidence_level"),
                "dharma_score":    result.get("dharma_score"),
                "cycle_score":     result.get("cycle_score"),
                "domain":          result.get("domain"),
                "intent":          result.get("intent"),
                "beliefs_count":   result.get("beliefs_count"),
                "health":          result.get("health"),
                "slept":           result.get("slept"),
                "stage_trace":     result.get("stage_trace", []),
                "reality":         result.get("reality", {}),
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/goal")
async def api_goal(payload: GoalRequest):
    """Goal mode — runs cognitive cycle with goal framing."""
    text = (payload.goal or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Goal field is required")

    rt = get_runtime()
    if not rt:
        raise HTTPException(status_code=503,
                            detail="Cognitive runtime unavailable.")

    try:
        result = rt.process(text, mode="goal")
        return {
            "reply":            result["reply"],
            "terminated_reason": "cognitive_cycle_complete",
            "plan":             result.get("stage_trace", []),
            "trace":            result.get("trace", []),
            "world":            result.get("reality", {}),
            "meta":             {k: result[k] for k in
                                  ("cycle","quality","confidence","dharma_score","cycle_score","domain") if k in result},
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/state")
async def api_state():
    """Returns live cognitive state: identity, beliefs, world, development."""
    rt = get_runtime()
    if not rt:
        return {"error": "Runtime unavailable", "available": False}
    return {
        "available":   True,
        "identity":    rt.identity,
        "beliefs":     rt.beliefs[:5],
        "world":       rt.world,
        "development": rt.development,
        "llm":         rt.llm_available,
    }


@app.get("/health")
async def health_check():
    rt = get_runtime()
    return {
        "ok":                True,
        "status":            "ok",
        "service":           "ChetnaOS",
        "version":           "2.0.0",
        "architecture":      "Developmental Cognitive Organism — Level 6",
        "light_mode":        settings.LIGHT_MODE,
        "embeddings_enabled": settings.EMBEDDINGS_ENABLED,
        "model":             settings.GROQ_MODEL,
        "llm_available":     rt.llm_available if rt else False,
        "cognitive_runtime": rt is not None,
    }


# ── Legacy /chetna endpoint ──────────────────────────────────────────────────

@app.post("/chetna")
async def chetna_route(payload: ChatRequest):
    text = (payload.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text field is required")
    rt = get_runtime()
    if not rt:
        raise HTTPException(status_code=503, detail="Runtime unavailable.")
    try:
        return rt.process(text, mode="chat")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Kalpavriksha + agent routes ──────────────────────────────────────────────
setup_kalpavriksha_routes(app)
app.include_router(agent_router)

# ── Static files + root ──────────────────────────────────────────────────────
@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
