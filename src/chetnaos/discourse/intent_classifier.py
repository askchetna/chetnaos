"""Rule-based conversational intent classifier."""
from __future__ import annotations

import re
from typing import Tuple

INTENTS = (
    "identity",
    "debug",
    "learning",
    "decision",
    "comparison",
    "coding",
    "brainstorm",
    "emotional",
    "philosophical",
    "planning",
    "casual",
)

_RULES: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    ("identity", (
        r"\bwho are you\b", r"\bwhat are you\b", r"\bintroduce yourself\b",
        r"\btum kaun\b", r"\baap kaun\b", r"\bkaun ho\b", r"\babout yourself\b",
        r"\byour identity\b", r"\bwho am i talking to\b", r"\btum janwar\b",
        r"\bmain chetna\b", r"\bself[- ]?describe\b",
    )),
    ("emotional", (
        r"\bsamjha nahi\b", r"\bsamajh nahi\b", r"\bnahi samajh\b", r"\bconfus",
        r"\bfrustrat", r"\bupset\b", r"\bsad\b", r"\bstress", r"\boverwhelm",
        r"\bhelp me cope\b", r"\bfeel (bad|low|anxious)\b", r"\bpareshan\b",
    )),
    ("debug", (
        r"\bwhy .* (disabled|broken|fail|error|not work)", r"\bnot working\b",
        r"\bdebug\b", r"\bbug\b", r"\berror\b", r"\b502\b", r"\b503\b",
        r"\bfix\b", r"\bissue\b", r"\bembedding", r"\btraceback\b",
        r"\bkaam nahi kar\b", r"\bproblem\b",
    )),
    ("comparison", (
        r"\bvs\.?\b", r"\bversus\b", r"\bcompare\b", r"\bdifference between\b",
        r"\bbetter than\b", r"\bwhich (one|is better)\b", r"\btrade[- ]?off\b",
    )),
    ("decision", (
        r"\bshould i\b", r"\bwhich should\b", r"\bdecide\b", r"\bchoose between\b",
        r"\brecommend\b", r"\bwhat do you think i should\b", r"\bkya karu\b",
        r"\boption a\b", r"\boption b\b",
    )),
    ("planning", (
        r"\bplan\b", r"\broadmap\b", r"\bstep by step\b", r"\bhow do i (start|build|launch)\b",
        r"\bstrategy\b", r"\btimeline\b", r"\bnext steps\b", r"\bpriority\b",
    )),
    ("coding", (
        r"\bcode\b", r"\bfunction\b", r"\bclass\b", r"\bapi\b", r"\bbug in\b",
        r"\bpython\b", r"\bjavascript\b", r"\btypescript\b", r"\bimplement\b",
        r"\brefactor\b", r"\bsyntax\b", r"\bcompile\b",
    )),
    ("learning", (
        r"\bwhat is\b", r"\bwhat are\b", r"\bexplain\b", r"\bhow does\b",
        r"\bhow do\b", r"\bwhy does\b", r"\bwhy is\b", r"\bdefine\b",
        r"\bteach me\b", r"\bsamjha\b", r"\bsamjhao\b", r"\bmatlab kya\b",
        r"\bkaise kaam karta\b",
    )),
    ("brainstorm", (
        r"\bbrainstorm\b", r"\bideas for\b", r"\bcreative\b", r"\balternatives\b",
        r"\bwhat if\b", r"\bthink outside\b", r"\bpossibilities\b",
    )),
    ("philosophical", (
        r"\bconscious", r"\bfree will\b", r"\bmeaning of\b", r"\bmoral\b",
        r"\bethics\b", r"\bdharma\b", r"\bsoul\b", r"\bexistence\b",
        r"\bphilosoph", r"\bnature of (mind|reality|truth)\b",
    )),
)


def classify_intent(text: str) -> str:
    """Return one of INTENTS for the user message."""
    q = (text or "").strip().lower()
    if not q:
        return "casual"
    if len(q.split()) <= 3 and q in {"hi", "hello", "hey", "namaste", "thanks", "thank you", "ok", "okay"}:
        return "casual"
    for intent, patterns in _RULES:
        for pat in patterns:
            if re.search(pat, q, re.I):
                return intent
    if q.endswith("?"):
        return "learning"
    return "casual"
