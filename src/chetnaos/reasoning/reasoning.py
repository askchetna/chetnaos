"""
Reasoning — Core reasoning about the input. Primary LLM call.
Canonical v3 implementation in src/chetnaos/reasoning/reasoning.py.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from .prompt_builder import PromptBuilder


class Reasoning:
    SYSTEM_PROMPT = PromptBuilder.BASE_TEMPLATE

    def __init__(self) -> None:
        self._prompt_builder = PromptBuilder()

    def reason(
        self,
        raw_input: str,
        recalled: list,
        plan: str,
        llm_router,
        founder_context: str = "",
        cognitive_context: Optional[Dict[str, Any]] = None,
    ) -> dict:
        system = self._prompt_builder.build_system_prompt(
            founder_context=founder_context,
            recalled=recalled,
            cognitive_context=cognitive_context,
            plan=plan,
        )

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": raw_input},
        ]

        try:
            response = llm_router.chat(messages)
        except Exception as e:
            response = f"[ChetnaOS reasoning unavailable: {e}]"

        ctx = cognitive_context or {}
        return {
            "stage": "REASON",
            "response": response,
            "used_memory": len(recalled) > 0,
            "used_plan": bool(plan),
            "used_founder_context": bool(founder_context),
            "used_working_memory": bool(ctx.get("working_memory")),
            "used_active_goal": bool(ctx.get("active_goal")),
            "used_beliefs": bool(ctx.get("beliefs")),
            "used_cognitive_organs": bool(
                ctx.get("self_model") or ctx.get("curiosity") or ctx.get("emotion")
            ),
            "used_agent_tool": bool(ctx.get("agent_tool")),
        }

    def _format_cognitive_context(self, ctx: Dict[str, Any]) -> str:
        """Backward-compat delegate for tests and legacy callers."""
        return self._prompt_builder.format_cognitive_context(ctx)
