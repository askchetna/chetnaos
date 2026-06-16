"""
Agent tools — calc, web fetch, web search for agent mode.

Purpose: Shared tool execution used by CognitiveCycle (not a parallel LLM path).
Dependencies: optional LLMRouter for summarization
"""
from __future__ import annotations

import ast
import re
from typing import Any, Dict, Optional

import requests
from bs4 import BeautifulSoup


def safe_calc(expression: str) -> str:
    try:
        expr = re.sub(r"^calc:\s*", "", expression).strip()
        if not re.match(r"^[\d\s\+\-\*\/\*\*\(\)\.]+$", expr):
            return "Error: Only basic math operations (+, -, *, /, **, parentheses) and numbers allowed"
        result = eval(expr, {"__builtins__": {}}, {})  # noqa: S307 — restricted charset
        return f"Result: {result}"
    except Exception as exc:
        return f"Calculation error: {exc}"


def web_fetch(url: str, llm_router: Any = None) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        text = re.sub(r"\s+", " ", soup.get_text()).strip()[:1500]
        if not text:
            return "Could not extract content from the page"
        if llm_router is None:
            return text[:800]
        return llm_router.complete(
            f"Summarize briefly with key points:\n\n{text}",
            max_tokens=300,
            temperature=0.2,
        )
    except Exception as exc:
        return f"Fetch error: {exc}"


def web_search(query: str, llm_router: Any = None) -> str:
    try:
        url = f"https://duckduckgo.com/html/?q={requests.utils.quote(query)}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for result in soup.select(".result__title, .result__snippet")[:6]:
            if result.text.strip():
                results.append(result.text.strip())
        if not results:
            return "No search results found"
        if llm_router is None:
            return "\n".join(results[:6])
        summary_prompt = (
            "Summarize these search results briefly with key points:\n\n"
            + "\n".join(results[:6])
        )
        return llm_router.complete(summary_prompt, max_tokens=300, temperature=0.2)
    except Exception as exc:
        return f"Search error: {exc}"


def run_agent_tool(user_message: str, llm_router: Any = None) -> Optional[Dict[str, str]]:
  """Return tool name + raw result, or None if no tool matched."""
  text = user_message.strip()
  lower = text.lower()

  if "calc:" in lower or "calculate" in lower:
    return {"tool": "calc", "result": safe_calc(text)}

  if "web:" in lower:
    url_match = re.search(r"web:\s*(https?://\S+)", text, re.IGNORECASE)
    if url_match:
      return {"tool": "web", "result": web_fetch(url_match.group(1), llm_router)}
    return {"tool": "web", "result": "Error: Please provide a valid URL after 'web:'"}

  if "search" in lower:
    query_match = re.search(r"search\s+(.+)", text, re.IGNORECASE)
    if query_match:
      return {"tool": "search", "result": web_search(query_match.group(1), llm_router)}
    return {"tool": "search", "result": "Error: Please provide a search query after 'search'"}

  return None
