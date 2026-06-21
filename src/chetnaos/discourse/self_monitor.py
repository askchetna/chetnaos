"""Self-monitor — final quality pass before user sees the answer."""
from __future__ import annotations

import re
from typing import Any, Dict, List

_ROBOTIC = re.compile(
    r"\b(certainly!|absolutely!|great question!|as an ai)\s*",
    re.I,
)
_OVERCERTAIN = re.compile(
    r"\b(definitely|100%|guaranteed|certainly will|without doubt)\s*",
    re.I,
)
_FOUNDER = re.compile(r"\b(founder|mangla)\b", re.I)
_JARGON_HEAVY = re.compile(
    r"\b(ontolog|epistemolog|hermeneutic|phenomenolog)\b", re.I,
)
_IDENTITY = re.compile(
    r"^(main chetna hoon|i am chetna)", re.I | re.M,
)
_CONTRADICTION_PAIR = (
    (re.compile(r"\balways\b", re.I), re.compile(r"\bnever\b", re.I)),
    (re.compile(r"\benable\b", re.I), re.compile(r"\bdisabled\b", re.I)),
)


def _word_overlap(a: str, b: str) -> float:
    wa = {w for w in re.findall(r"[a-z0-9]+", a.lower()) if len(w) > 2}
    wb = {w for w in re.findall(r"[a-z0-9]+", b.lower()) if len(w) > 2}
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / min(len(wa), len(wb))


def _truncate_sentences(text: str, max_sentences: int) -> str:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return " ".join(parts[:max_sentences]).strip()


def _strip_duplicate_paragraphs(text: str) -> str:
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    kept: List[str] = []
    for p in paras:
        if any(_word_overlap(p, k) > 0.85 for k in kept):
            continue
        kept.append(p)
    return "\n\n".join(kept)


def _soften_certainty(text: str) -> str:
    def repl(m: re.Match[str]) -> str:
        w = m.group(0).strip().lower()
        if w in ("definitely", "100%", "guaranteed", "without doubt"):
            return "likely "
        return "probably "
    return _OVERCERTAIN.sub(repl, text)


def _reduce_founder_mentions(text: str, user_mentioned_founder: bool) -> str:
    if user_mentioned_founder:
        return text
    lines = [ln for ln in text.splitlines() if not _FOUNDER.search(ln) or len(ln) > 80]
    return "\n".join(lines).strip()


def _check_debug_steps(text: str, response_goal: str) -> str:
    if response_goal != "debug":
        return text
    lower = text.lower()
    if "fix" in lower or "step" in lower or "try" in lower:
        return text
    return text + "\n\nTry the fix above and check if the issue clears."

def monitor(
    text: str,
    *,
    ctx_info: Dict[str, Any] | None = None,
    pragmatics: Dict[str, Any] | None = None,
    response_goal: str = "explain",
    user_input: str = "",
    max_sentences: int | None = None,
) -> str:
    """Improve answer quality; never expose monitor internals."""
    t = str(text or "").strip()
    if not t:
        return t

    t = _ROBOTIC.sub("", t)
    t = _soften_certainty(t)
    t = _JARGON_HEAVY.sub("concept", t)
    t = _strip_duplicate_paragraphs(t)

    ctx = ctx_info or {}
    if ctx.get("identity_already_shared"):
        lines = [ln for ln in t.splitlines() if not _IDENTITY.match(ln.strip())]
        t = "\n".join(lines).strip() or t

    prior: List[str] = ctx.get("prior_assistant") or []
    if prior:
        paras = []
        for p in re.split(r"\n\s*\n", t):
            if any(_word_overlap(p, old) > 0.78 for old in prior):
                continue
            paras.append(p.strip())
        if paras:
            t = "\n\n".join(paras)

    for a, b in _CONTRADICTION_PAIR:
        if a.search(t) and b.search(t):
            t = a.sub("often", t, count=1)

    t = _reduce_founder_mentions(t, bool(_FOUNDER.search(user_input or "")))
    t = _check_debug_steps(t, response_goal)

    prag = pragmatics or {}
    if prag.get("shorten") and max_sentences:
        t = _truncate_sentences(t, max(1, max_sentences - 1))
    elif max_sentences:
        t = _truncate_sentences(t, max_sentences)

    return re.sub(r"\n{3,}", "\n\n", t).strip()
