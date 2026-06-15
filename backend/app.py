"""
ChetnaOS Backend — FastAPI Application v2.0
Developmental Cognitive Architecture — Level 6
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Any, Dict

from .config import get_settings
from .api import setup_kalpavriksha_routes
from .agent import router as agent_router

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

app = FastAPI(
    title="ChetnaOS API",
    description="Developmental Cognitive Architecture v2.0 — Level 6",
    version="2.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

settings = get_settings()
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
    print(f"[ChetnaOS v2.0] Startup — GROQ_MODEL={settings.GROQ_MODEL}")
    rt = get_runtime()
    if rt:
        print(f"[ChetnaOS v2.0] Cognitive Runtime ready — "
              f"LLM={'yes' if rt.llm_available else 'no'}")
    else:
        print("[ChetnaOS v2.0] Running in legacy mode.")


# ── Models ──────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    text: str

class GoalRequest(BaseModel):
    goal: str
    context:     Dict[str, Any] | None = None
    constraints: Dict[str, Any] | None = None


# ── Chat endpoint ────────────────────────────────────────────────────────────
@app.post("/api/chat")
async def api_chat(payload: ChatRequest):
    text = (payload.text or "").strip()
    if not text:
        raise HTTPException(400, "text field required")
    rt = get_runtime()
    if not rt:
        raise HTTPException(503, "Cognitive runtime unavailable.")
    try:
        result = rt.process(text, mode="chat")
        return {
            "reply": result["reply"],
            "meta": {
                "cycle":            result.get("cycle"),
                "quality":          result.get("quality"),
                "confidence":       result.get("confidence"),
                "confidence_level": result.get("confidence_level"),
                "dharma_score":     result.get("dharma_score"),
                "cycle_score":      result.get("cycle_score"),
                "domain":           result.get("domain"),
                "intent":           result.get("intent"),
                "beliefs_count":    result.get("beliefs_count"),
                "health":           result.get("health"),
                "slept":            result.get("slept"),
                "stage_trace":      result.get("stage_trace", []),
                "reality":          result.get("reality", {}),
                "simulation":       result.get("simulation", {}),
                "meta_cognition":   result.get("meta_cognition", {}),
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


# ── Goal endpoint ─────────────────────────────────────────────────────────────
@app.post("/api/goal")
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
            "reply":  result["reply"],
            "plan":   result.get("stage_trace", []),
            "trace":  result.get("trace", []),
            "world":  result.get("reality", {}),
            "meta":   {k: result[k] for k in
                       ("cycle","quality","confidence","dharma_score","cycle_score","domain")
                       if k in result},
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


# ── State endpoint ────────────────────────────────────────────────────────────
@app.get("/api/state")
async def api_state():
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


# ── Dashboard endpoint ────────────────────────────────────────────────────────
@app.get("/api/dashboard")
async def api_dashboard():
    """Full cognitive dashboard snapshot — all modules."""
    rt = get_runtime()
    if not rt:
        return {"available": False, "error": "Runtime unavailable."}
    try:
        snap = rt._cycle.dashboard_snapshot()
        snap["available"] = True
        return snap
    except Exception as e:
        return {"available": False, "error": str(e)}


# ── Health endpoint ───────────────────────────────────────────────────────────
@app.get("/health")
async def health():
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


# ── Legacy /chetna ────────────────────────────────────────────────────────────
@app.post("/chetna")
async def chetna_legacy(payload: ChatRequest):
    text = (payload.text or "").strip()
    if not text:
        raise HTTPException(400, "text required")
    rt = get_runtime()
    if not rt:
        raise HTTPException(503, "Runtime unavailable.")
    try:
        return rt.process(text, mode="chat")
    except Exception as e:
        raise HTTPException(500, str(e))


# ── Kalpavriksha + agent ──────────────────────────────────────────────────────
setup_kalpavriksha_routes(app)
app.include_router(agent_router)

# ── Static files + root ───────────────────────────────────────────────────────
@app.get("/")
async def root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/dashboard")
async def serve_dashboard():
    return FileResponse(os.path.join(FRONTEND_DIR, "dashboard.html"))

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
