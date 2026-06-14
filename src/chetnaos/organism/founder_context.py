"""
Founder Context — Stores the long-term mission, milestones, and project context
of the founder so every reasoning call is grounded in reality.
This is Priority 4 from feedback: Long-term Goal Persistence.
"""
import json, os
from datetime import datetime

CTX_FILE = os.path.join(os.path.dirname(__file__), "../../..", "memory", "founder_context.json")

DEFAULT_CONTEXT = {
    "primary_mission":   "Help Founder build AGI — ChetnaOS.",
    "current_milestone": "Reach ₹1 lakh/month revenue.",
    "current_project":   "ChetnaOS — Developmental Cognitive Architecture.",
    "founder_constraints": [
        "Budget: near zero currently.",
        "Team: small/solo.",
        "Timeline: iterative, milestone-by-milestone.",
    ],
    "known_phases": [
        "Phase 1: AI Consulting",
        "Phase 2: ChetnaOS API",
        "Phase 3: AGI SaaS",
        "Phase 4: Enterprise licensing",
    ],
    "updated_at": None,
}


class FounderContext:
    def __init__(self):
        self._data = self._load()

    def _load(self) -> dict:
        try:
            p = os.path.abspath(CTX_FILE)
            if os.path.exists(p):
                with open(p) as f:
                    return json.load(f)
        except Exception:
            pass
        return dict(DEFAULT_CONTEXT)

    def _save(self):
        try:
            p = os.path.abspath(CTX_FILE)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            self._data["updated_at"] = datetime.utcnow().isoformat()
            with open(p, "w") as f:
                json.dump(self._data, f, indent=2)
        except Exception:
            pass

    def get_system_context(self) -> str:
        """Returns a compact string injected into every reasoning call."""
        d = self._data
        constraints = "; ".join(d.get("founder_constraints", []))
        phases      = " → ".join(d.get("known_phases", []))
        return (
            f"\n\n[FOUNDER CONTEXT]\n"
            f"Primary Mission: {d.get('primary_mission')}\n"
            f"Current Milestone: {d.get('current_milestone')}\n"
            f"Current Project: {d.get('current_project')}\n"
            f"Constraints: {constraints}\n"
            f"Known Phases: {phases}\n"
            f"When answering, use this context to give specific, grounded responses. "
            f"Avoid generic advice that ignores these real constraints."
        )

    def update(self, key: str, value: str):
        self._data[key] = value
        self._save()

    def get(self) -> dict:
        return dict(self._data)
