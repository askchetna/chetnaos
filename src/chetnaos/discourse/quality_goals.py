"""Response quality goals — clarity, brevity, trustworthiness."""
from __future__ import annotations

import re

QUALITY_GOALS = (
    "clarity",
    "correctness",
    "helpfulness",
    "naturalness",
    "brevity",
    "trustworthiness",
)

_FILLER = [
    re.compile(r"\b(as mentioned earlier|as i said before|to reiterate)\b", re.I),
    re.compile(r"\b(i hope this helps|let me know if you have any questions)\b", re.I),
    re.compile(r"\b(furthermore|moreover|additionally),\s*", re.I),
]


def polish(text: str, *, max_blank_blocks: int = 2) -> str:
    """Light pass for brevity and clarity without changing meaning."""
    t = str(text or "").strip()
    for pat in _FILLER:
        t = pat.sub("", t)
    t = re.sub(r"[ \t]+\n", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    t = re.sub(r"\s{2,}", " ", t)
    # Collapse duplicate consecutive sentences
    sentences = re.split(r"(?<=[.!?])\s+", t)
    deduped: list[str] = []
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        if deduped and s.lower() == deduped[-1].lower():
            continue
        deduped.append(s)
    t = " ".join(deduped)
    return t.strip()
