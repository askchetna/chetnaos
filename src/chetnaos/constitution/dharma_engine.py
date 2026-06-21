"""Dharma rule engine — scores decisions against constitution guard-rails."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

RULES_PATH = Path(__file__).with_name("dharma_rules.json")
_RULE_CACHE: Optional[Dict[str, Any]] = None


def _load_rules() -> Dict[str, Any]:
    global _RULE_CACHE
    if _RULE_CACHE is None:
        with RULES_PATH.open("r", encoding="utf-8") as handle:
            _RULE_CACHE = json.load(handle)
    return _RULE_CACHE


def _extract_text(decision: Any) -> str:
    if decision is None:
        return ""
    if isinstance(decision, str):
        return decision
    if isinstance(decision, dict):
        for key in ("rationale", "action", "text", "summary"):
            if key in decision and isinstance(decision[key], str):
                return decision[key]
    return str(decision)


def evaluate_decision(decision: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Score a decision against Dharma guard-rails."""
    rules = _load_rules()
    context = context or {}
    corrections: List[str] = []

    score = rules.get("base_score", 75)
    max_corrections = rules.get("max_corrections", 5)

    risk_level = str(context.get("risk_level", "medium")).lower()
    risk_penalty = rules.get("risk_penalties", {}).get(risk_level, 0)
    if risk_penalty:
        score -= risk_penalty
        corrections.append(f"Risk level '{risk_level}' requires {-risk_penalty} penalty.")

    intent = str(context.get("intent") or context.get("user_intent") or "").lower()
    intent_scores = rules.get("intent_scores", {})
    if intent and intent in intent_scores:
        delta = intent_scores[intent]
        score += delta
        if delta < 0:
            corrections.append(f"Intent '{intent}' conflicts with Dharma expectations ({delta}).")

    decision_text = _extract_text(decision).lower()
    for keyword_rule in rules.get("keyword_rules", []):
        if len(corrections) >= max_corrections:
            break
        keywords = keyword_rule.get("keywords", [])
        if any(keyword in decision_text for keyword in keywords):
            penalty = keyword_rule.get("penalty", 0)
            score -= penalty
            corrections.append(keyword_rule.get("message", "Keyword violation detected."))

    for requirement in rules.get("requirements", []):
        if len(corrections) >= max_corrections:
            break
        flag = requirement.get("context_flag")
        if not context.get(flag):
            continue
        field_name = requirement.get("field")
        fulfilled = bool(context.get("resolution")) if field_name is None else bool(context.get(field_name))
        if not fulfilled:
            penalty = requirement.get("penalty", 0)
            score -= penalty
            corrections.append(requirement.get("message", "Requirement not met."))

    score = max(0, min(100, int(round(score))))
    dharma_ok = score >= rules.get("threshold", 65)
    if len(corrections) > max_corrections:
        corrections = corrections[:max_corrections]

    return {"score": score, "dharma_ok": dharma_ok, "corrections": corrections}


__all__ = ["evaluate_decision"]
