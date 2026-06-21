"""Response schemas v2 — section keys and display labels."""
from __future__ import annotations

from typing import Dict, List

PATTERNS: Dict[str, List[str]] = {
    "identity": ["introduction", "purpose", "capabilities", "invitation"],
    "learning": ["definition", "intuition", "example", "applications", "summary"],
    "debug": ["observation", "cause", "fix", "verification"],
    "decision": ["goal", "options", "tradeoffs", "recommendation", "reason"],
    "planning": ["objective", "priorities", "steps", "risks", "next_action"],
    "comparison": ["criteria", "differences", "pros", "cons", "recommendation"],
    "emotional": ["acknowledge", "clarify", "perspective", "practical_help"],
    "coding": ["code", "context", "approach", "caveats"],
    "brainstorm": ["ideas", "angles", "next_steps"],
    "philosophical": ["frame", "exploration", "grounding", "open_question"],
    "casual": ["reply"],
}

SECTION_LABELS: Dict[str, str] = {
    "introduction": "Introduction",
    "purpose": "Purpose",
    "capabilities": "Capabilities",
    "invitation": "Invitation",
    "definition": "Definition",
    "intuition": "Intuition",
    "example": "Example",
    "importance": "Importance",
    "applications": "Applications",
    "objective": "Objective",
    "summary": "Summary",
    "observation": "Observation",
    "cause": "Cause",
    "fix": "Fix",
    "verification": "Verification",
    "goal": "Goal",
    "options": "Options",
    "tradeoffs": "Tradeoffs",
    "recommendation": "Recommendation",
    "reason": "Reason",
    "priorities": "Priorities",
    "steps": "Steps",
    "risks": "Risks",
    "next_action": "Next action",
    "criteria": "Criteria",
    "differences": "Differences",
    "pros": "Pros",
    "cons": "Cons",
    "acknowledge": "Acknowledge",
    "clarify": "Clarify",
    "perspective": "Perspective",
    "practical_help": "Practical help",
    "code": "Code",
    "context": "Context",
    "approach": "Approach",
    "caveats": "Caveats",
    "ideas": "Ideas",
    "angles": "Angles",
    "next_steps": "Next steps",
    "frame": "Frame",
    "exploration": "Exploration",
    "grounding": "Grounding",
    "open_question": "Open question",
    "reply": "Reply",
}


def schema_for(intent: str) -> List[str]:
    return list(PATTERNS.get(intent, PATTERNS["casual"]))
