"""Pragmatics — hidden intent beyond literal user text."""
from __future__ import annotations

import re
from typing import Any, Dict

_FRUSTRATION = (
    r"\b(mujhse nahi hoga|nahi ho paega|can't do this|too hard|impossible)\b",
    r"\b(bahut mushkil|overwhelmed|give up|fed up|frustrated)\b",
    r"\b(ye sab|this is too much)\b",
)

_DELEGATION = (
    r"\b(tum kar do|you do it|handle it for me|take over)\b",
    r"\b(kya tum kar sakte|can you just)\b",
)

_URGENCY = (
    r"\b(urgent|asap|jaldi|immediately|right now|deadline)\b",
    r"\b(blocker|production down|critical)\b",
)

_SIMPLIFY = (
    r"\b(simple|simpler|short mein|easy|bas itna)\b",
    r"\bsamjha nahi|samajh nahi|confus",
)

_AGREEMENT_SHORT = (
    r"^(achha|accha|theek|ok|okay|haan|yes|thanks|samajh gaya)\.?$",
)


def analyze_pragmatics(user_input: str, ctx_info: Dict[str, Any] | None = None) -> Dict[str, Any]:
    q = (user_input or "").strip().lower()
    act = (ctx_info or {}).get("dialogue_act", "fresh")

    result: Dict[str, Any] = {
        "hidden_intent": None,
        "simplify": False,
        "shorten": False,
        "acknowledge_difficulty": False,
        "teach_mode": False,
    }

    if act == "agreement" or any(re.search(p, q, re.I) for p in _AGREEMENT_SHORT):
        result["hidden_intent"] = "agreement"
        result["shorten"] = True
        return result

    if act == "confusion" or any(re.search(p, q, re.I) for p in _SIMPLIFY):
        result["hidden_intent"] = "confusion"
        result["simplify"] = True
        return result

    if any(re.search(p, q, re.I) for p in _FRUSTRATION):
        result["hidden_intent"] = "frustration"
        result["simplify"] = True
        result["acknowledge_difficulty"] = True
        result["shorten"] = False
        return result

    if any(re.search(p, q, re.I) for p in _DELEGATION):
        result["hidden_intent"] = "delegation"
        return result

    if any(re.search(p, q, re.I) for p in _URGENCY):
        result["hidden_intent"] = "urgency"
        result["shorten"] = True
        return result

    if re.search(r"\b(teach|step by step|guide me)\b", q, re.I):
        result["teach_mode"] = True

    return result


def pragmatic_prefix(pragmatics: Dict[str, Any]) -> str:
    if pragmatics.get("hidden_intent") == "frustration":
        return "Samajh sakti hoon — yeh thoda heavy lag sakta hai. Chalo simple steps mein dekhte hain."
    if pragmatics.get("hidden_intent") == "confusion":
        return "Koi baat nahi. Main aur simple tareeke se samjhata hoon."
    if pragmatics.get("hidden_intent") == "urgency":
        return "Theek hai — pehle seedha actionable part."
    return ""
