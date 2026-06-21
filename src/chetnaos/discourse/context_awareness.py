"""Conversational turn analysis — follow-ups, corrections, memory dedupe."""
from __future__ import annotations

import re
from typing import Any, Dict, List

_IDENTITY_MARKERS = (
    "main chetna", "i am chetna", "cognitive ai system",
    "memory, reasoning", "goals ki madad",
)

_FOLLOW_UP = (
    r"^(and|also|what about|tell me more|continue|go on|phir|aur|uske baad)\b",
    r"\b(more detail|elaborate|expand on)\b",
    r"^(why\?|how\?|ok but)\b",
)

_CORRECTION = (
    r"\b(no|nahi|galat|wrong|incorrect|not what i meant|actually)\b",
    r"\b(that('s| is) wrong|you misunderstood|correction)\b",
)

_CONFUSION = (
    r"\b(samjha nahi|samajh nahi|nahi samajh|confus|don't understand|didn't get)\b",
)

_FRUSTRATION = (
    r"\b(mujhse nahi hoga|nahi ho paega|too hard|impossible|frustrated|fed up)\b",
    r"\b(bahut mushkil|give up|ye sab)\b",
)

_URGENCY = (
    r"\b(urgent|asap|jaldi|immediately|deadline|production down)\b",
)

_AGREEMENT = (
    r"^(yes|yeah|yep|ok|okay|thanks|thank you|theek|samajh gaya|got it|perfect|great)\.?$",
    r"\b(sounds good|makes sense|understood)\b",
)


def _prior_assistant_texts(conversation_context: Dict[str, Any] | None) -> List[str]:
    if not conversation_context:
        return []
    texts: List[str] = []
    for msg in conversation_context.get("recent_messages") or []:
        if msg.get("role") == "assistant":
            content = (msg.get("content") or "").strip()
            if content:
                texts.append(content)
    return texts


def identity_already_shared(conversation_context: Dict[str, Any] | None) -> bool:
    for text in _prior_assistant_texts(conversation_context):
        lower = text.lower()
        if any(m in lower for m in _IDENTITY_MARKERS):
            return True
    return False


def detect_dialogue_act(user_input: str, conversation_context: Dict[str, Any] | None) -> str:
    """Return: fresh | follow_up | correction | confusion | agreement | frustration | urgency."""
    q = (user_input or "").strip().lower()
    if not q:
        return "fresh"
    for pat in _URGENCY:
        if re.search(pat, q, re.I):
            return "urgency"
    for pat in _AGREEMENT:
        if re.search(pat, q, re.I):
            return "agreement"
    for pat in _FRUSTRATION:
        if re.search(pat, q, re.I):
            return "frustration"
    for pat in _CONFUSION:
        if re.search(pat, q, re.I):
            return "confusion"
    for pat in _CORRECTION:
        if re.search(pat, q, re.I):
            return "correction"
    prior = _prior_assistant_texts(conversation_context)
    if prior:
        for pat in _FOLLOW_UP:
            if re.search(pat, q, re.I):
                return "follow_up"
        if len(q.split()) <= 6 and q.endswith("?"):
            return "follow_up"
    return "fresh"


def _word_set(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 2}


def _overlap(a: str, b: str) -> float:
    wa, wb = _word_set(a), _word_set(b)
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / min(len(wa), len(wb))


def dedupe_against_history(text: str, prior_assistant: List[str], *, threshold: float = 0.72) -> str:
    """Drop paragraphs that largely repeat prior assistant turns."""
    if not text or not prior_assistant:
        return text
    kept: List[str] = []
    for para in re.split(r"\n\s*\n", text.strip()):
        p = para.strip()
        if not p:
            continue
        if any(_overlap(p, old) >= threshold for old in prior_assistant):
            continue
        kept.append(p)
    return "\n\n".join(kept) if kept else text.strip()


def strip_repeated_identity(text: str, already_shared: bool) -> str:
    if not already_shared:
        return text
    lines = []
    for line in text.splitlines():
        lower = line.lower().strip()
        if any(m in lower for m in _IDENTITY_MARKERS) and len(lower) < 120:
            continue
        if re.match(r"^(main chetna hoon|i am chetna)\.?$", lower, re.I):
            continue
        lines.append(line)
    out = "\n".join(lines).strip()
    return re.sub(r"\n{3,}", "\n\n", out)


def analyze_context(user_input: str, conversation_context: Dict[str, Any] | None) -> Dict[str, Any]:
    prior = _prior_assistant_texts(conversation_context)
    return {
        "dialogue_act": detect_dialogue_act(user_input, conversation_context),
        "prior_assistant": prior,
        "identity_already_shared": identity_already_shared(conversation_context),
        "has_history": bool(prior),
    }
