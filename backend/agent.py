"""Backward-compat shim — use backend.api.agent."""
from backend.api.agent import router

__all__ = ["router"]
