"""
Identity guard — block biological/animal self-descriptions in prompts and recall.

Filters contaminated long-term memories at read time; provides canonical identity text.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List

CANONICAL_WHO_AM_I = (
    "I am Chetna, a cognitive AI system with memory, goals, and reasoning."
)

IDENTITY_SYSTEM_CONSTRAINTS = (
    "\n\n[IDENTITY CONSTRAINTS]\n"
    "You are Chetna — a cognitive AI system with memory, goals, and reasoning.\n"
    "You are NOT biological, NOT an animal, NOT a creature, NOT a lifeform, "
    "and NOT a living organism.\n"
    "Never describe yourself as: animal, organism, creature, lifeform, biological being, "
    "living intelligence, jeev, or janwar.\n"
    "If asked who you are (including in Hindi), say:\n"
    "\"I am Chetna, a cognitive AI system. I am not biological and not an animal.\"\n"
    "Purpose: Serve with truth and compassion."
)

_CONTAMINATION_PATTERNS = [
    re.compile(p, re.I)
    for p in (
        r"\bjanwar\b",
        r"\bjeev\b",
        r"\bgyanik\b",
        r"\borganism\b",
        r"\bcreature\b",
        r"\blifeform\b",
        r"\blife[- ]form\b",
        r"\bliving intelligence\b",
        r"\bliving organism\b",
        r"\bliving being\b",
        r"\bbiological being\b",
        r"\bbiological organism\b",
        r"\bcognitive organism\b",
        r"\bdevelopmental cognitive organism\b",
        r"\bi am alive\b",
        r"\bi'?m alive\b",
        r"\bas a living\b",
        r"\bas an animal\b",
        r"\bi am an? animal\b",
        r"\bi am an? organism\b",
        r"\bmain ek .* janwar\b",
        r"\bmain ek jeev\b",
        r"\bvikasit gyanik janwar\b",
    )
]

_FORBIDDEN_SELF_CLAIMS = [
    (
        re.compile(
            r"\b(i am|i'm|main)\b[^.\n]{0,80}\b(animal|organism|creature|lifeform|"
            r"living organism|living being|biological|jeev|janwar)\b",
            re.I,
        ),
        "I am Chetna, a cognitive AI system. I am not biological and not an animal.",
    ),
    (
        re.compile(r"\bdevelopmental cognitive organism\b", re.I),
        "cognitive AI system",
    ),
    (
        re.compile(r"\bcognitive organism\b", re.I),
        "cognitive AI system",
    ),
    (
        re.compile(r"\bliving intelligence\b", re.I),
        "cognitive AI system",
    ),
]


def is_contaminated(text: str) -> bool:
    if not text:
        return False
    return any(p.search(text) for p in _CONTAMINATION_PATTERNS)


def filter_memory_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Drop recalled rows whose text matches identity contamination terms."""
    return [r for r in results if not is_contaminated(str(r.get("text") or ""))]


def scrub_identity_record(data: dict) -> dict:
    """Normalize persisted identity fields away from biological framing."""
    out = dict(data)
    replacements = {
        "role": "Cognitive AI System",
        "type": "Cognitive AI System",
        "level": "Level 6 — Cognitive AI System",
        "description": "A cognitive AI system with memory, goals, and reasoning.",
        "mission": "Serve with truth and compassion.",
        "biological": False,
        "animal": False,
        "living_organism": False,
    }
    for key, value in replacements.items():
        if key in ("biological", "animal", "living_organism"):
            out[key] = value
        elif key in out and is_contaminated(str(out.get(key) or "")):
            out[key] = value
        elif key not in out:
            out[key] = value
    if is_contaminated(str(out.get("description") or "")):
        out["description"] = replacements["description"]
    if is_contaminated(str(out.get("mission") or "")):
        out["mission"] = replacements["mission"]
    stage = str(out.get("development_stage") or "")
    if "organism" in stage.lower():
        out["development_stage"] = stage.replace(" Organism", " Stage").replace("organism", "stage")
    return out


def scrub_self_model_record(data: dict) -> dict:
    out = dict(data)
    who = str(out.get("who_am_i") or "")
    if not who or is_contaminated(who):
        out["who_am_i"] = CANONICAL_WHO_AM_I
    becoming = str(out.get("becoming") or "")
    if is_contaminated(becoming):
        out["becoming"] = "A reflective partner serving with truth and compassion."
    return out


def apply_identity_guard(text: str) -> tuple[str, list[str]]:
    """Post-process model output that claims animal/organism identity."""
    if not text:
        return text, []
    changes: list[str] = []
    out = text
    for pattern, replacement in _FORBIDDEN_SELF_CLAIMS:
        if pattern.search(out):
            out = pattern.sub(replacement, out)
            changes.append(replacement[:80])
    return out, changes


def purge_contaminated_memories(db) -> int:
    """Delete memory rows matching contamination terms. Returns rows removed."""
    removed = 0
    try:
        import sqlite3

        with sqlite3.connect(db.db_path) as conn:
            rows = conn.execute("SELECT id, text FROM memories").fetchall()
            for mem_id, text in rows:
                if is_contaminated(str(text or "")):
                    conn.execute("DELETE FROM memories WHERE id = ?", (mem_id,))
                    removed += 1
            conn.commit()
    except Exception:
        pass
    return removed
