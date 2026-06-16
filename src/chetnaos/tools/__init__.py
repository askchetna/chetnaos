"""ChetnaOS v3 — external tools (organism agent path)."""
from .calculator import safe_calc
from .web_search import web_search
from .document_reader import web_fetch
from .tool_router import ToolRouter, run_agent_tool

__all__ = [
    "safe_calc",
    "web_search",
    "web_fetch",
    "ToolRouter",
    "run_agent_tool",
]
