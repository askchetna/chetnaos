"""
Prompt builder — single assembly path for all LLM system prompts.

Constitution + Founder + Identity context + memory + cognitive organs + plan.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.chetnaos.constitution import CONSTITUTION
from src.chetnaos.memory.source_ranks import COGNITIVE_SOURCE_RANKS
from src.chetnaos.memory.identity_guard import IDENTITY_SYSTEM_CONSTRAINTS, filter_memory_results
from src.chetnaos.reasoning.honesty_guard import honesty_system_addon


class PromptBuilder:
    """Build system prompts for the reasoning stage."""

    BASE_TEMPLATE = (
        "You are Chetna, a cognitive AI system with memory, goals, and reasoning. "
        "You are not biological, not an animal, and not a living organism. "
        "Your purpose: Serve with truth and compassion. "
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
        safe = filter_memory_results(recalled)
        items = [m.get("text", str(m)) for m in safe[:3] if m]
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
        return system + honesty_system_addon() + IDENTITY_SYSTEM_CONSTRAINTS

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
            who = (sm.get("who_am_i") or "")[:120]
            becoming = (sm.get("becoming") or "")[:120]
            focus = (sm.get("current_focus") or "")[:100]
            limits = sm.get("known_limits") or []
            limit_line = f"\nKnown limits: {', '.join(limits[:3])}" if limits else ""
            parts.append(
                "[SELF MODEL]\n"
                f"Who I am: {who or '—'}\n"
                f"Becoming: {becoming or '—'}\n"
                f"Current focus: {focus or '—'}"
                f"{limit_line}"
            )

        values = ctx.get("values")
        if values:
            vlines = values.get("priorities") or values.get("top") or []
            if isinstance(vlines, list) and vlines:
                if isinstance(vlines[0], dict):
                    names = [p.get("name", "") for p in vlines[:4] if p.get("name")]
                else:
                    names = [str(v) for v in vlines[:4]]
                if names:
                    parts.append("[VALUES]\n" + "\n".join(names))

        reflection = ctx.get("recent_reflection")
        if reflection:
            parts.append(f"[RECENT REFLECTION]\n{str(reflection)[:200]}")

        highlight = ctx.get("episodic_highlight")
        if highlight:
            y = (highlight.get("yesterday_summary") or "—")[:150]
            lesson = (highlight.get("recent_lesson") or "—")[:150]
            parts.append(
                "[EPISODIC HIGHLIGHT]\n"
                f"Yesterday: {y}\n"
                f"Recent lesson: {lesson}"
            )

        themes = ctx.get("recurring_themes")
        if themes:
            parts.append(
                "[RECURRING THEMES]\n" + ", ".join(str(t) for t in themes[:5])
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

        temporal = ctx.get("temporal")
        if temporal:
            recent = temporal.get("recent_changes") or []
            recent_str = recent[-2:] if isinstance(recent, list) else recent
            parts.append(
                "[TEMPORAL CONTINUITY]\n"
                f"Today: {(temporal.get('today_summary') or '—')[:120]}\n"
                f"Yesterday: {(temporal.get('yesterday_summary') or '—')[:120]}\n"
                f"Recent changes: {recent_str}\n"
                f"Next intentions: {(temporal.get('tomorrow_intentions') or ['—'])[0] if temporal.get('tomorrow_intentions') else '—'}"
            )

        episodic = ctx.get("episodic")
        if episodic and not ctx.get("episodic_highlight"):
            today_h = episodic.get("today", {}).get("highlights") or []
            yest_h = episodic.get("yesterday", {}).get("highlights") or []
            lines = []
            for h in yest_h[:2]:
                inp = (h.get("input") or h.get("domain") or "general")[:60]
                lines.append(f"Yesterday: {inp}")
            for h in today_h[:1]:
                inp = (h.get("input") or h.get("domain") or "general")[:60]
                lines.append(f"Today: {inp}")
            if lines:
                parts.append("[EPISODIC MEMORY]\n" + "\n".join(lines))

        identity = ctx.get("identity")
        if identity:
            parts.append(
                "[IDENTITY]\n"
                f"Name: {identity.get('name', 'Chetna')}\n"
                f"Type: {identity.get('type', identity.get('role', 'Cognitive AI System'))}\n"
                f"Biological: {identity.get('biological', False)} | "
                f"Animal: {identity.get('animal', False)} | "
                f"Living organism: {identity.get('living_organism', False)}\n"
                f"Purpose: {identity.get('mission', 'Serve with truth and compassion.')[:120]}\n"
                f"Stage: {identity.get('development_stage', 'Seed')}"
            )

        founder = ctx.get("founder_relationship")
        if founder:
            parts.append(
                "[FOUNDER RELATIONSHIP]\n"
                f"{founder.get('name', '')} — {founder.get('role', 'Founder')}, "
                f"{founder.get('relationship', 'Creator')}\n"
                f"Trust: {founder.get('trust', 'high')} | "
                f"Attachment: {founder.get('attachment', 'primary')}"
            )

        if any(
            ctx.get(k)
            for k in (
                "identity", "founder_relationship", "self_model", "temporal",
                "episodic_highlight", "recent_reflection", "recurring_themes",
            )
        ):
            parts.append(
                "[MEMORY GROUNDING]\n"
                "For who you are, what changed, becoming, recent learning, or recurring "
                "themes — answer only from memory blocks above. "
                "You are a cognitive AI system — never describe yourself as an animal, "
                "organism, creature, lifeform, jeev, or janwar. "
                "The founder is a person (Creator), never a place. "
                "If memory is empty, say continuity is still forming — do not invent history."
            )

        if not parts:
            return ""
        return "\n\n" + "\n\n".join(parts)
