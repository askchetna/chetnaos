"""Benchmark guard — block unsupported self-claims unless evidence exists."""
from __future__ import annotations

import re
from typing import Any

_FORBIDDEN = [
    (re.compile(r"\bi am conscious\b", re.I), "Designed to model reflective processing; I do not claim consciousness."),
    (re.compile(r"\bi am more self[- ]aware than (gpt|chatgpt|claude|gemini|sota)\b", re.I),
     "Current evidence suggests my self-model is architectural, not demonstrated superiority over other systems."),
    (re.compile(r"\bi am more advanced than (sota|state[- ]of[- ]the[- ]art|gpt|chatgpt)\b", re.I),
     "Intended to integrate memory, beliefs, and a developmental cycle; no benchmark proves superiority over SOTA."),
    (re.compile(r"\bmore (self[- ]aware|conscious|advanced) than\b", re.I),
     "Current evidence suggests comparisons require published benchmarks; none are attached here."),
]

_HONESTY_SYSTEM_BLOCK = (
    "\n\n[HONESTY GUARD]\n"
    "Never claim consciousness, superiority over GPT/SOTA, or unsupported self-awareness. "
    "Use phrasing like 'Designed to…', 'Intended to…', 'Current evidence suggests…' "
    "unless verified benchmark evidence is provided in context."
)


def has_benchmark_evidence(context: dict[str, Any] | None) -> bool:
    if not context:
        return False
    if context.get("benchmark_evidence"):
        return True
    dev = context.get("development") or {}
    return bool(dev.get("benchmark_verified"))


def honesty_system_addon() -> str:
    return _HONESTY_SYSTEM_BLOCK


def apply_honesty_guard(text: str, *, benchmark_evidence: bool = False) -> tuple[str, list[str]]:
    """Return (possibly revised text, list of substitutions made)."""
    if benchmark_evidence or not text:
        return text, []
    changes: list[str] = []
    out = text
    for pattern, replacement in _FORBIDDEN:
        if pattern.search(out):
            out = pattern.sub(replacement, out)
            changes.append(replacement[:80])
    return out, changes
