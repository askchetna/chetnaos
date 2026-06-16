"""ChetnaOS v3 HTTP API — thin shell over single runtime."""
from __future__ import annotations

from fastapi import FastAPI

from .chat import router as chat_router
from .goal import router as goal_router
from .state import router as state_router
from .dashboard import router as dashboard_router
from .health import router as health_router
from .agent import router as agent_router
from .conversations import router as conversations_router
from .workspace import router as workspace_router


def register_routes(app: FastAPI) -> None:
    app.include_router(chat_router)
    app.include_router(goal_router)
    app.include_router(state_router)
    app.include_router(dashboard_router)
    app.include_router(health_router)
    app.include_router(agent_router)
    app.include_router(conversations_router)
    app.include_router(workspace_router)
