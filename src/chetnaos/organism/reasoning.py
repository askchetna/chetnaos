"""
Reasoning — Core reasoning about the input. Primary LLM call.
Injects constitution values + founder context for grounded responses.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.chetnaos.constitution import CONSTITUTION


class Reasoning:
    SYSTEM_PROMPT = (
        "You are ChetnaOS — a Developmental Cognitive Organism. "
        "Your constitution says: {mission}. "
        "Your values are: {values}. "
        "Respond with truth, compassion, and clarity. "
        "If uncertain, say so explicitly."
    )

    def reason(
        self,
        raw_input: str,
        recalled: list,
        plan: str,
        llm_router,
        founder_context: str = "",
        cognitive_context: Optional[Dict[str, Any]] = None,
    ) -> dict:
        mission = CONSTITUTION["mission"]["statement"]
        values = ", ".join(v["name"] for v in CONSTITUTION["values"][:3])
        system = self.SYSTEM_PROMPT.format(mission=mission, values=values)

        if founder_context:
            system += founder_context

        memory_context = ""
        if recalled:
            items = [m.get("text", str(m)) for m in recalled[:3] if m]
            if items:
                memory_context = "\n\nRelevant long-term memory:\n" + "\n".join(
                    f"- {i[:150]}" for i in items
                )

        cognitive_block = self._format_cognitive_context(cognitive_context or {})
        plan_context = f"\n\nApproach to use: {plan}" if plan else ""

        messages = [
            {
                "role": "system",
                "content": system + memory_context + cognitive_block + plan_context,
            },
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
        parts: List[str] = []

        wm: List[dict] = ctx.get("working_memory") or []
        if wm:
            lines = []
            for item in wm[:5]:
                text = item.get("input") or item.get("text") or str(item)[:120]
                weight = item.get("_attention_weight", item.get("attention_weight"))
                suffix = f" (attention={weight:.2f})" if isinstance(weight, (int, float)) else ""
                lines.append(f"- {text[:120]}{suffix}")
            parts.append("[WORKING MEMORY]\n" + "\n".join(lines))

        goal = ctx.get("active_goal")
        if goal:
            parts.append(
                "[ACTIVE GOAL]\n"
                f"Type: {goal.get('goal_type', 'USER')} | "
                f"Priority: {goal.get('goal_priority', '')}\n"
                f"Goal: {goal.get('text', '')[:200]}"
            )

        beliefs: List[dict] = ctx.get("beliefs") or []
        if beliefs:
            blines = [
                f"- ({b.get('confidence', 0):.2f}) {b.get('text', '')[:100]}"
                for b in beliefs[:5]
            ]
            parts.append(
                "[BELIEF CONFIDENCE]\n"
                "Use high-confidence beliefs as anchors; treat low-confidence as tentative.\n"
                + "\n".join(blines)
            )

        sm = ctx.get("self_model")
        if sm:
            limits = sm.get("known_limits") or []
            parts.append(
                "[SELF MODEL]\n"
                f"Self-confidence: {sm.get('self_confidence', '—')}\n"
                f"Known limits: {', '.join(limits[:4]) if limits else 'none noted'}"
            )

        curiosity = ctx.get("curiosity")
        if curiosity:
            egoals = curiosity.get("exploration_goals") or []
            glines = [
                f"- {g.get('type', 'explore')}: {g.get('target', '')[:80]}"
                for g in egoals[:3]
            ]
            block = f"Novelty: {curiosity.get('novelty_score', '—')}"
            if glines:
                block += "\n" + "\n".join(glines)
            parts.append("[CURIOSITY]\n" + block)

        emotion = ctx.get("emotion")
        if emotion:
            parts.append(
                "[EMOTION STATE]\n"
                f"Valence: {emotion.get('valence', '—')} | "
                f"Arousal: {emotion.get('arousal', '—')} | "
                f"Tone: {emotion.get('interaction_tone', 'neutral')}"
            )

        agent_tool = ctx.get("agent_tool")
        if agent_tool:
            parts.append(
                "[AGENT TOOL RESULT]\n"
                f"Tool: {agent_tool.get('tool', 'unknown')}\n"
                f"Result:\n{agent_tool.get('result', '')[:1200]}"
            )

        if not parts:
            return ""
        return "\n\n" + "\n\n".join(parts)
