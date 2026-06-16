"""
ChetnaOS Backend — FastAPI Application v3.0
Thin HTTP shell: one runtime, one cognitive cycle.
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .config import get_settings
from .plugins import setup_kalpavriksha_routes
from .api import register_routes
from .middleware import RequestLoggingMiddleware, optional_auth_middleware

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

app = FastAPI(
    title="ChetnaOS API",
    description="ChetnaOS v3 — Single Runtime Developmental Cognitive Organism",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(optional_auth_middleware())

settings = get_settings()


@app.on_event("startup")
async def on_startup():
    app.state.settings = settings
    print(f"[ChetnaOS v3] Startup — GROQ_MODEL={settings.GROQ_MODEL}")
    from .runtime import get_runtime

    rt = get_runtime()
    if rt:
        print(
            f"[ChetnaOS v3] Cognitive Runtime ready — "
            f"LLM={'yes' if rt.llm_available else 'no'}"
        )
    else:
        print("[ChetnaOS v3] Running without cognitive runtime.")


register_routes(app)
setup_kalpavriksha_routes(app)


@app.get("/")
async def root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/dashboard")
async def serve_dashboard():
    return FileResponse(os.path.join(FRONTEND_DIR, "dashboard.html"))


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
