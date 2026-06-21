"""Knowledge ordering — map response goals to section schemas and build plans."""
from __future__ import annotations

import re
from typing import Any, Dict, List

from .conversation_patterns import SECTION_LABELS

# v3 knowledge order (goal-driven)
GOAL_SCHEMAS: Dict[str, List[str]] = {
    "explain": ["definition", "intuition", "example", "applications", "summary"],
    "teach": ["definition", "intuition", "example", "applications", "summary"],
    "debug": ["observation", "cause", "fix", "verification"],
    "compare": ["criteria", "differences", "pros", "cons", "recommendation"],
    "plan": ["objective", "priorities", "steps", "risks", "next_action"],
    "decide": ["goal", "options", "tradeoffs", "recommendation", "reason"],
    "brainstorm": ["ideas", "angles", "next_steps"],
    "comfort": ["acknowledge", "clarify", "perspective", "practical_help"],
    "clarify": ["clarify", "definition", "example", "summary"],
}

# Extend section labels for v3 keys
SECTION_LABELS.update({
    "applications": "Applications",
    "objective": "Objective",
})

_HEADER = re.compile(
    r"^(?:#{1,3}\s*|\*\*)?(?P<label>[A-Za-z][A-Za-z \-/]+?)(?:\*\*)?\s*:?\s*$",
    re.M,
)
_INLINE = re.compile(
    r"^(?P<label>[A-Za-z][A-Za-z \-/]+?)\s*:\s*(?P<body>.+)$",
    re.M,
)
_CODE_BLOCK = re.compile(r"```[\s\S]*?```", re.M)

_ALIASES = {
    "introduction": ("introduction", "identity", "who_am_i"),
    "objective": ("objective", "goal"),
    "goal": ("goal", "objective"),
    "applications": ("applications", "importance", "why_it_matters", "use_cases"),
    "cause": ("cause", "possible_cause", "root_cause"),
    "observation": ("observation", "observed"),
    "clarify": ("clarify", "clarification"),
    "practical_help": ("practical_help", "practical_suggestion"),
    "code": ("code", "implementation"),
}


def schema_for_goal(response_goal: str, intent: str) -> List[str]:
    if intent == "identity":
        return ["introduction", "purpose", "capabilities", "invitation"]
    if intent == "coding":
        return ["code", "context", "approach", "caveats"]
    return list(GOAL_SCHEMAS.get(response_goal, GOAL_SCHEMAS["explain"]))


def _split_paragraphs(text: str) -> List[str]:
    parts = [p.strip() for p in re.split(r"\n\s*\n", text or "") if p.strip()]
    return parts or ([text.strip()] if text and text.strip() else [])


def _extract_labeled_blocks(text: str) -> Dict[str, str]:
    blocks: Dict[str, str] = {}
    matches = list(_HEADER.finditer(text or ""))
    if matches:
        for i, m in enumerate(matches):
            label = m.group("label").strip().lower().replace(" ", "_").replace("-", "_")
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            if body:
                blocks[label] = body
        return blocks
    for m in _INLINE.finditer(text or ""):
        label = m.group("label").strip().lower().replace(" ", "_").replace("-", "_")
        body = m.group("body").strip()
        if body:
            blocks[label] = body
    return blocks


def _map_blocks(blocks: Dict[str, str], schema: List[str]) -> Dict[str, str]:
    rev: Dict[str, str] = {}
    for key, names in _ALIASES.items():
        for n in names:
            rev[n] = key
    out: Dict[str, str] = {}
    for raw_label, body in blocks.items():
        key = rev.get(raw_label, raw_label)
        if key in schema and key not in out:
            out[key] = body
    return out


def _distribute(paragraphs: List[str], schema: List[str]) -> Dict[str, str]:
    if not paragraphs:
        return {}
    out: Dict[str, str] = {}
    if len(paragraphs) == 1:
        out[schema[0]] = paragraphs[0]
        return out
    for i, key in enumerate(schema):
        if i < len(paragraphs):
            out[key] = paragraphs[i]
    if len(paragraphs) > len(schema):
        tail = schema[-1]
        out[tail] = (out.get(tail, "") + "\n\n" + "\n\n".join(paragraphs[len(schema):])).strip()
    return out


def build_knowledge_plan(
    *,
    response_goal: str,
    intent: str,
    raw_response: str,
    verbosity: str = "medium",
    code_first: bool = False,
) -> Dict[str, Any]:
    schema = schema_for_goal(response_goal, intent)
    text = (raw_response or "").strip()
    sections: Dict[str, str] = {}

    if intent == "coding" or code_first:
        codes = [m.group(0).strip() for m in _CODE_BLOCK.finditer(text)]
        if codes:
            sections["code"] = "\n\n".join(codes)
            remainder = _CODE_BLOCK.sub("", text).strip()
            paras = _split_paragraphs(remainder)
            for i, key in enumerate(("context", "approach", "caveats")):
                if i < len(paras):
                    sections[key] = paras[i]
        else:
            sections = _distribute(_split_paragraphs(text), schema)
    else:
        labeled = _extract_labeled_blocks(text)
        sections = _map_blocks(labeled, schema) if labeled else {}
        if not sections:
            sections = _distribute(_split_paragraphs(text), schema)

    filled = len([v for v in sections.values() if v])
    use_headers = verbosity in ("structured", "code_first") and filled >= 2
    if response_goal in ("debug", "plan", "decide", "compare") and filled >= 2:
        use_headers = True

    return {
        "response_goal": response_goal,
        "intent": intent,
        "schema": schema,
        "sections": sections,
        "use_headers": use_headers,
        "verbosity": verbosity,
        "labels": {k: SECTION_LABELS.get(k, k.replace("_", " ").title()) for k in schema},
    }
