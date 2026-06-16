"""Route agent-mode user input to calculator, web search, or LLM reasoning."""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from .calculator import safe_calc
from .document_reader import web_fetch
from .web_search import web_search


class ToolRouter:
    """Detect tool intent from user message."""

    @staticmethod
    def detect(message: str) -> Tuple[Optional[str], str]:
        text = (message or "").strip()
        lower = text.lower()
        if lower.startswith("calc:") or (
            len(text) < 80 and any(c in text for c in "+-*/") and any(c.isdigit() for c in text)
        ):
            expr = text.replace("calc:", "").strip() if lower.startswith("calc:") else text
            return "calc", expr
        if lower.startswith("fetch:") or lower.startswith("http"):
            url = text.replace("fetch:", "").strip() if lower.startswith("fetch:") else text
            return "fetch", url
        if lower.startswith("search:"):
            return "search", text.replace("search:", "").strip()
        return None, text


def run_agent_tool(
    message: str,
    llm_router: Any = None,
) -> Dict[str, Any]:
    """Execute detected tool; mirrors CognitiveCycle.run_agent_tool."""
    from .agent_tools import run_agent_tool as _run

    return _run(message, llm_router=llm_router)
