"""
Prompt builder — single assembly path for all LLM system prompts.

Constitution + Founder + Identity context + memory + cognitive organs + plan.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.chetnaos.constitution import CONSTITUTION
from src.chetnaos.memory_kernel.source_ranks import COGNITIVE_SOURCE_RANKS
from src.chetnaos.reasoning.honesty_guard import honesty_system_addon


class PromptBuilder:
    """Build system prompts for the reasoning stage."""

    BASE_TEMPLATE = (
        "You are ChetnaOS — a Developmental Cognitive Organism. "
        "Your constitution says: {mission}. "
        "Your values are: {values}. "
        "Respond with truth, compassion, and clarity. "
        "If uncertain, say so explicitly."
    )

    def base_system(self) -> str:
        mission = CONSTITUTION["mission"]["statement"]
        values = ", ".join(v["name"] for v in CONSTITUTION["values"][:3])
        return self.BASE_TEMPLATE.format(mission=mission, values=values)

    def with_founder(self, founder_context: str) -> str:
        base = self.base_system()
        if not founder_context:
            return base
        rank = COGNITIVE_SOURCE_RANKS["founder_context"]
        return base + f"\n\n[source trust={rank:.2f}]" + founder_context

    def with_memory(self, system: str, recalled: List[dict]) -> str:
        if not recalled:
            return system
        items = [m.get("text", str(m)) for m in recalled[:3] if m]
        if not items:
            return system
        rank = COGNITIVE_SOURCE_RANKS["long_term_memory"]
        block = (
            f"\n\n[source trust={rank:.2f}]\n"
            "Relevant long-term memory:\n"
            + "\n".join(f"- {i[:150]}" for i in items)
        )
        return system + block

    def with_cognitive_context(
        self, system: str, cognitive_context: Optional[Dict[str, Any]]
    ) -> str:
        block = self.format_cognitive_context(cognitive_context or {})
        return system + block if block else system

    def with_conversation(
        self, system: str, conversation_context: Optional[Dict[str, Any]]
    ) -> str:
        if not conversation_context:
            return system
        parts: List[str] = []
        topic = conversation_context.get("active_topic")
        if topic:
            parts.append(f"Active topic: {topic}")
        summary = conversation_context.get("conversation_summary")
        if summary:
            parts.append(f"Conversation summary: {summary[:800]}")
        goal = conversation_context.get("current_goal")
        if goal and isinstance(goal, dict):
            parts.append(f"Current goal: {goal.get('text', '')[:200]}")
        rel = conversation_context.get("relevant_memory") or []
        if rel:
            mlines = [
                f"- {(m.get('text') or str(m))[:120]}"
                for m in rel[:3]
            ]
            parts.append("Relevant memory for this thread:\n" + "\n".join(mlines))
        if not parts:
            return system
        return system + "\n\n[CONVERSATION CONTEXT]\n" + "\n".join(parts)

    def with_plan(self, system: str, plan: str) -> str:
        return system + (f"\n\nApproach to use: {plan}" if plan else "")

    def build_system_prompt(
        self,
        *,
        founder_context: str = "",
        recalled: Optional[List[dict]] = None,
        cognitive_context: Optional[Dict[str, Any]] = None,
        conversation_context: Optional[Dict[str, Any]] = None,
        plan: str = "",
    ) -> str:
        """Single entry: everything the LLM sees in the system role."""
        system = self.base_system()
        system = self.with_founder(founder_context)
        system = self.with_memory(system, recalled or [])
        system = self.with_cognitive_context(system, cognitive_context)
        system = self.with_conversation(system, conversation_context)
        system = self.with_plan(system, plan)
        return system + honesty_system_addon()

    def format_cognitive_context(self, ctx: Dict[str, Any]) -> str:
        parts: List[str] = []
        wm_rank = COGNITIVE_SOURCE_RANKS["working_memory"]

        wm: List[dict] = ctx.get("working_memory") or []
        if wm:
            lines = []
            for item in wm[:5]:
                text = item.get("input") or item.get("text") or str(item)[:120]
                weight = item.get("_attention_weight", item.get("attention_weight"))
                suffix = f" (attention={weight:.2f})" if isinstance(weight, (int, float)) else ""
                lines.append(f"- {text[:120]}{suffix}")
            parts.append(
                f"[WORKING MEMORY]\n[source trust={wm_rank:.2f}]\n" + "\n".join(lines)
            )

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
