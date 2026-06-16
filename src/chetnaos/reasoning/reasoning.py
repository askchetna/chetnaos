"""
Reasoning — Core reasoning about the input. Primary LLM call.
Canonical v3 implementation in src/chetnaos/reasoning/reasoning.py.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .honesty_guard import apply_honesty_guard, has_benchmark_evidence
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
        conversation_context: Optional[Dict[str, Any]] = None,
    ) -> dict:
        ctx = cognitive_context or {}
        conv = conversation_context or {}

        system = self._prompt_builder.build_system_prompt(
            founder_context=founder_context,
            recalled=recalled,
            cognitive_context=ctx,
            conversation_context=conv,
            plan=plan,
        )

        messages: List[dict] = [{"role": "system", "content": system}]
        for msg in conv.get("recent_messages") or []:
            role = msg.get("role")
            content = (msg.get("content") or "").strip()
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": raw_input})

        try:
            response = llm_router.chat(messages)
        except Exception as e:
            response = f"[ChetnaOS reasoning unavailable: {e}]"

        benchmark_ok = has_benchmark_evidence(ctx)
        response, honesty_changes = apply_honesty_guard(
            response, benchmark_evidence=benchmark_ok,
        )

        beliefs_used = ctx.get("beliefs") or []
        memory_influence = [
            {
                "text": (m.get("text") or str(m))[:120],
                "source": m.get("source", "recall"),
            }
            for m in (recalled or [])[:5]
        ]
        belief_influence = [
            {
                "id": b.get("id"),
                "text": (b.get("text") or "")[:100],
                "confidence": b.get("confidence"),
            }
            for b in beliefs_used[:5]
        ]

        return {
            "stage": "REASON",
            "response": response,
            "used_memory": len(recalled) > 0,
            "used_plan": bool(plan),
            "used_founder_context": bool(founder_context),
            "used_working_memory": bool(ctx.get("working_memory")),
            "used_active_goal": bool(ctx.get("active_goal")),
            "used_beliefs": bool(beliefs_used),
            "used_conversation_context": bool(conv.get("recent_messages")),
            "used_cognitive_organs": bool(
                ctx.get("self_model") or ctx.get("curiosity") or ctx.get("emotion")
            ),
            "used_agent_tool": bool(ctx.get("agent_tool")),
            "memory_influence": memory_influence,
            "belief_influence": belief_influence,
            "honesty_guard": honesty_changes,
        }

    def _format_cognitive_context(self, ctx: Dict[str, Any]) -> str:
        """Backward-compat delegate for tests and legacy callers."""
        return self._prompt_builder.format_cognitive_context(ctx)
