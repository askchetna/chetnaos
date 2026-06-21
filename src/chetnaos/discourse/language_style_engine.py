"""LanguageStyleEngine — natural Hinglish, anti-robotic, anti-repetition."""
from __future__ import annotations

import re
from typing import Any, Dict

_FORBIDDEN = [
    (re.compile(r"\bdevelopmental cognitive organism\b", re.I), "cognitive AI system"),
    (re.compile(r"\bcognitive organism\b", re.I), "cognitive AI system"),
    (re.compile(r"\bliving intelligence\b", re.I), "cognitive AI system"),
    (re.compile(r"\bliving organism\b", re.I), "system"),
    (re.compile(r"\bbiological (being|organism)\b", re.I), "AI system"),
    (re.compile(r"\borganism\b", re.I), "system"),
    (re.compile(r"\bentity\b", re.I), "system"),
    (re.compile(r"\bjeev\b", re.I), "system"),
    (re.compile(r"\bjanwar\b", re.I), "system"),
]

_ROBOTIC = [
    (re.compile(r"\bAs an AI language model\b", re.I), "Main Chetna hoon"),
    (re.compile(r"\bI cannot\b", re.I), "Shayad abhi yeh nahi ho payega"),
    (re.compile(r"\bPlease note that\b", re.I), "Zarur —"),
    (re.compile(r"\bIt is important to note\b", re.I), "Zarur —"),
    (re.compile(r"\bIn conclusion\b", re.I), "Short mein —"),
    (re.compile(r"\bTo summarize\b", re.I), "Summary —"),
]

_TELEMETRY = [
    re.compile(r"\bcycle\s*#?\d+\b", re.I),
    re.compile(r"\bcycle_id\b", re.I),
    re.compile(r"\b\d{1,3}%\s*confidence\b", re.I),
    re.compile(r"\bconfidence[:\s]+[\d.]+%", re.I),
    re.compile(r"\borgans?\s+activated\b", re.I),
]

# Light Hinglish openers — one per reply max, not on follow-ups/agreement.
_OPENERS: Dict[str, str] = {
    "learning": "Achha sawal hai.",
    "debug": "Dekhte hain.",
    "emotional": "Koi baat nahi.",
    "decision": "Theek hai — options dekhte hain.",
    "planning": "Plan clear rakhte hain.",
    "comparison": "Compare karte hain.",
}

_DEVANAGARI = re.compile(r"[\u0900-\u097F]")


def _strip_telemetry(text: str) -> str:
    t = str(text or "")
    for pat in _TELEMETRY:
        t = pat.sub("", t)
    return t.strip()


def _hinglish_balance(text: str) -> str:
    """Avoid overly Hindi (long Devanagari runs) or overly formal English."""
    t = text
    # Trim excessive Devanagari paragraphs (>60% devanagari chars → simplify note)
    for para in t.split("\n\n"):
        if not para.strip():
            continue
        dev = len(_DEVANAGARI.findall(para))
        if dev and dev / max(len(para), 1) > 0.6:
            t = t.replace(para, para[:200] + ("…" if len(para) > 200 else ""))
    # Soften stiff formal openers
    t = re.sub(r"\bFurthermore\b", "Ek aur point —", t)
    t = re.sub(r"\bHowever\b", "Par", t, count=2)
    return t


def apply_language_style(
    text: str,
    intent: str,
    *,
    dialogue_act: str = "fresh",
    skip_opener: bool = False,
) -> str:
    t = _strip_telemetry(str(text or ""))
    for pat, repl in _FORBIDDEN + _ROBOTIC:
        t = pat.sub(repl, t)
    t = _hinglish_balance(t)
    t = re.sub(r"\n{3,}", "\n\n", t).strip()

    if not skip_opener and dialogue_act in ("fresh", "follow_up"):
        opener = _OPENERS.get(intent, "")
        if opener and opener.lower() not in t.lower()[:40]:
            if intent in ("learning", "debug", "emotional") and dialogue_act == "fresh":
                t = f"{opener}\n\n{t}" if t else opener

    emojis = re.findall(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]", t)
    if len(emojis) > 1:
        for e in emojis[1:]:
            t = t.replace(e, "", 1)

    return t.strip()
