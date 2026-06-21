"""Benchmark and identity guard — block unsupported or contaminated self-claims."""
from __future__ import annotations

import re
from typing import Any

from src.chetnaos.memory.identity_guard import apply_identity_guard

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
    "Never describe yourself as an animal, organism, creature, lifeform, biological being, "
    "living intelligence, jeev, or janwar. "
    "Use phrasing like 'Designed to…', 'Intended to…', 'Current evidence suggests…' "
    "unless verified benchmark evidence is provided in context.\n"
    "Never state cycle IDs, timestamps, cycle durations, or activated organ counts in your reply. "
    "Runtime telemetry is shown separately in the UI — do not narrate internal execution metrics."
)

_TELEMETRY_NARRATION_PATTERNS = [
    re.compile(r"\b\d+\s+organs?\s+activated\b", re.I),
    re.compile(r"\bactivated\s+\d+\s+organs?\b", re.I),
    re.compile(r"\bactivated\s+organs?\b", re.I),
    re.compile(r"\bcycle\s+duration\b[^.\n]{0,80}", re.I),
    re.compile(r"\bcycle\s+id\s*[:=]\s*[0-9a-f-]{8,}\b", re.I),
    re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I),
    re.compile(
        r"\b(?:at|on)\s+\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}", re.I
    ),
]


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
    out, id_changes = apply_identity_guard(out)
    changes.extend(id_changes)
    return out, changes


def apply_telemetry_narration_guard(
    text: str,
    runtime_meta: dict[str, Any] | None = None,
) -> tuple[str, list[str]]:
    """
    Strip LLM narration of runtime telemetry (cycle IDs, durations, organ counts, timestamps).
    UI panels are the only source of truth for these fields.
    """
    del runtime_meta  # reserved — telemetry is UI-only, never echoed in reply prose
    if not text:
        return text, []
    changes: list[str] = []
    out = text
    for pattern in _TELEMETRY_NARRATION_PATTERNS:
        if pattern.search(out):
            out = pattern.sub("[See Runtime Trace panel for telemetry]", out)
            changes.append("Removed telemetry narration from reply.")
    return out, changes
