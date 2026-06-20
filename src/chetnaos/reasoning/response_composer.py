"""
Response Composer — converts raw cognition output into natural conversational language.

Never exposes organ names, cycle counts, confidence numbers, or debug telemetry.
"""
from __future__ import annotations

import re
from typing import Any, Dict, Optional

_ROBOTIC_REWRITES = [
    (re.compile(r"I updated my knowledge\.?", re.I), "My understanding has shifted a little from that."),
    (re.compile(r"I attempted to learn\.?", re.I), "I'm letting that settle into how I think about things."),
    (re.compile(r"There was no change detected\.?", re.I),
     "Nothing major has changed yet, but my focus remains the same."),
    (re.compile(r"no change detected\.?", re.I),
     "I haven't noticed a major shift — my attention is steady."),
    (re.compile(r"I have updated my beliefs?\.?", re.I), "That refines how I see things, gently."),
    (re.compile(r"belief store updated\.?", re.I), "That adds a quiet note to what I hold true."),
    (re.compile(r"cognitive cycle complete\.?", re.I), ""),
    (re.compile(r"running (the )?cognitive cycle\.?", re.I), ""),
    (re.compile(r"27-stage cognitive cycle\.?", re.I), ""),
]

_INTERNAL_LINE = re.compile(
    r"^\s*(cycle|stage_trace|cycle_trace|cycle_id|confidence|dharma|belief|organ|"
    r"working_memory|goal_progress|meta_cognition|simulation|runtime trace|cognitive)\b",
    re.I,
)


class ResponseComposer:
    @staticmethod
    def sanitize(text: str) -> str:
        t = str(text or "")
        t = "\n".join(line for line in t.split("\n") if not _INTERNAL_LINE.match(line))
        t = re.sub(r"\bcycle\s*#?\d+\b", "", t, flags=re.I)
        t = re.sub(r"\b(cycle|stage)\s+\d+\b", "", t, flags=re.I)
        t = re.sub(r"\b\d{1,3}%\s*(confidence|confident)\b", "", t, flags=re.I)
        t = re.sub(r"confidence[:\s]+[\d.]+%", "", t, flags=re.I)
        t = re.sub(r"\bdharma[:\s]*\d+\/?\d*", "", t, flags=re.I)
        t = re.sub(r"\bbeliefs?\s*(count|store)?[:\s]*\d+", "", t, flags=re.I)
        t = re.sub(r"\b(self[- ]?verdict|quality)[:\s]*\w+", "", t, flags=re.I)
        t = re.sub(r"\[[\w_]+\]", "", t)
        t = re.sub(r"\(\s*\)", "", t)
        t = re.sub(r"\s{2,}", " ", t)
        t = re.sub(r"\n{3,}", "\n\n", t)
        return t.strip()

    @staticmethod
    def rewrite(text: str) -> str:
        t = text
        for pattern, replacement in _ROBOTIC_REWRITES:
            t = pattern.sub(replacement, t)
        return t.strip()

    @classmethod
    def compose(cls, raw: str, meta: Optional[Dict[str, Any]] = None) -> str:
        t = cls.sanitize(raw)
        t = cls.rewrite(t)
        if not t and raw:
            t = cls.rewrite(cls.sanitize(raw)) or str(raw).strip()
        return t
