"""Discourse v3 pipeline orchestrator."""
from __future__ import annotations

import re
from typing import Any, Dict, Optional

from .audience_model import audience_hints, infer_audience
from .context_awareness import (
    analyze_context,
    dedupe_against_history,
    strip_repeated_identity,
)
from .intent_classifier import classify_intent
from .knowledge_planner import build_knowledge_plan
from .language_style_engine import apply_language_style
from .pragmatics_engine import analyze_pragmatics, pragmatic_prefix
from .quality_goals import polish
from .response_goal_engine import infer_response_goal
from .self_monitor import monitor
from .tone_engine import apply_tone
from .verbosity_control import assess_verbosity, max_sentences, should_show_headers

_IDENTITY_FULL = (
    "Main Chetna hoon.\n\n"
    "Ek AI system jo memory, reasoning aur goals ki madad se kaam karta hai.\n\n"
    "Agar tum kisi topic par baat karna chaho, batao."
)

_IDENTITY_BRIEF = "Main Chetna hoon — ek cognitive AI system."

_AGREEMENT_REPLY = "Theek hai. Agla step batao jab ready ho."


def _format_sections(plan: Dict[str, Any]) -> str:
    parts = []
    show = plan.get("use_headers", False)
    for key in plan["schema"]:
        body = (plan["sections"].get(key) or "").strip()
        if not body:
            continue
        if show:
            label = plan["labels"].get(key, key.replace("_", " ").title())
            parts.append(f"{label}\n{body}")
        else:
            parts.append(body)
    return "\n\n".join(parts)


def _truncate(text: str, n: int) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return " ".join(sentences[:n]).strip()


def _identity_reply(user_input: str, ctx_info: Dict[str, Any]) -> str | None:
    q = (user_input or "").lower()
    if not re.search(r"\b(who are you|what are you|tum kaun|kaun ho|introduce)\b", q, re.I):
        return None
    if re.search(r"\b(janwar|jeev|organism|creature)\b", q, re.I):
        return (
            "Nahi — main janwar ya jeev nahi hoon.\n\n"
            "Main Chetna hoon, ek cognitive AI system. Biological nahi hoon."
        )
    if ctx_info.get("identity_already_shared"):
        return _IDENTITY_BRIEF
    return _IDENTITY_FULL


def compose_from_plan(
    user_input: str,
    intent: str,
    raw_response: str,
    plan: Dict[str, Any],
    ctx_info: Dict[str, Any],
    pragmatics: Dict[str, Any],
    response_goal: str,
    verbosity: str,
) -> str:
    act = ctx_info.get("dialogue_act", "fresh")

    prefix = pragmatic_prefix(pragmatics)
    if prefix and response_goal in ("clarify", "comfort"):
        if act in ("confusion", "frustration") or pragmatics.get("hidden_intent") in ("confusion", "frustration"):
            return prefix

    if act == "agreement" or pragmatics.get("hidden_intent") == "agreement":
        return _AGREEMENT_REPLY

    identity_msg = _identity_reply(user_input, ctx_info)
    if identity_msg and intent == "identity":
        return identity_msg

    structured = _format_sections(plan)
    base = structured.strip() or raw_response.strip()

    if plan["sections"].get("code"):
        code = plan["sections"]["code"]
        rest = "\n\n".join(
            plan["sections"].get(k, "")
            for k in ("context", "approach", "caveats")
            if plan["sections"].get(k)
        ).strip()
        base = f"{code}\n\n{rest}".strip() if rest else code

    if prefix:
        base = f"{prefix}\n\n{base}".strip()

    if verbosity == "short" or pragmatics.get("shorten"):
        base = _truncate(base, max_sentences(verbosity, intent))

    if act == "follow_up" and ctx_info.get("has_history"):
        base = _truncate(base, max(4, max_sentences(verbosity, intent)))

    if act == "correction":
        base = f"Theek hai — correction samajh li.\n\n{base}"

    return base


class DiscourseLayer:
    """
    Post-reasoning discourse transform (v3).

    Pipeline: Intent → Context → Audience → Goal → Knowledge → Tone → Style
              → Quality → SelfMonitor → Answer
    Removable: delete this hook in cognitive_cycle without side effects.
    """

    @classmethod
    def transform(
        cls,
        user_input: str,
        raw_response: str,
        conversation_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        # 1 IntentClassifier
        intent = classify_intent(user_input)

        # 2 ContextAwareness
        ctx_info = analyze_context(user_input, conversation_context)
        if ctx_info["dialogue_act"] == "confusion":
            intent = "emotional"
        elif ctx_info["dialogue_act"] == "frustration":
            intent = "emotional"
        elif ctx_info["dialogue_act"] == "correction" and intent == "casual":
            intent = "learning"

        # 3 Pragmatics (hidden intent)
        pragmatics = analyze_pragmatics(user_input, ctx_info)

        # 4 AudienceModel
        audience = infer_audience(
            user_input, intent=intent, conversation_context=conversation_context,
        )
        hints = audience_hints(audience)

        # 5 ResponseGoalEngine
        response_goal = infer_response_goal(
            intent,
            pragmatics=pragmatics,
            dialogue_act=ctx_info["dialogue_act"],
        )

        # Verbosity (adaptive depth)
        verbosity = assess_verbosity(user_input, intent, ctx_info["dialogue_act"], ctx_info)
        if hints.get("verbosity_bias") == "short":
            verbosity = "short"
        elif hints.get("code_first"):
            verbosity = "code_first"
        elif hints.get("verbosity_bias") == "structured" and verbosity == "medium":
            verbosity = "structured"

        # 6 KnowledgePlanner (+ ConversationPatterns labels)
        plan = build_knowledge_plan(
            response_goal=response_goal,
            intent=intent,
            raw_response=raw_response,
            verbosity=verbosity,
            code_first=bool(hints.get("code_first")),
        )
        plan["use_headers"] = should_show_headers(
            intent, verbosity, len([v for v in plan["sections"].values() if v]),
        ) or plan.get("use_headers", False)

        # 7 Answer composition (structure)
        draft = compose_from_plan(
            user_input, intent, raw_response, plan, ctx_info,
            pragmatics, response_goal, verbosity,
        )

        # 8 ToneEngine
        skip_opener = ctx_info["dialogue_act"] in (
            "follow_up", "agreement", "correction", "urgency",
        )
        draft = apply_tone(
            draft, intent,
            dialogue_act=ctx_info["dialogue_act"],
            skip_opener=skip_opener,
        )

        # 9 LanguageStyleEngine (via tone delegate + direct pass for audience)
        draft = apply_language_style(
            draft, intent,
            dialogue_act=ctx_info["dialogue_act"],
            skip_opener=True,
        )

        # Dedupe / identity guard
        if intent != "identity":
            draft = dedupe_against_history(draft, ctx_info.get("prior_assistant") or [])
        draft = strip_repeated_identity(
            draft, ctx_info.get("identity_already_shared", False),
        )

        if not draft.strip() and intent == "identity":
            draft = _identity_reply(user_input, ctx_info) or _IDENTITY_BRIEF

        # 10 QualityGoals
        draft = polish(draft)

        # 11 SelfMonitor
        ms = max_sentences(verbosity, intent)
        if pragmatics.get("shorten"):
            ms = min(ms, 2)
        draft = monitor(
            draft,
            ctx_info=ctx_info,
            pragmatics=pragmatics,
            response_goal=response_goal,
            user_input=user_input,
            max_sentences=ms,
        )

        return draft.strip()
