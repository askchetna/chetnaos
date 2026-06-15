"""
Founder Context — Deep model of the founder's cognitive environment.
Gap 4: Goals, Habits, Stress, Preferences, Long-term Plans.
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
    # Gap 4 additions
    "founder_goals": [
        {"goal": "Launch ChetnaOS publicly",     "priority": 95, "status": "in_progress"},
        {"goal": "Get first paying AI client",   "priority": 90, "status": "in_progress"},
        {"goal": "Reach AGI research milestone", "priority": 80, "status": "planned"},
        {"goal": "Build ChetnaOS community",     "priority": 70, "status": "planned"},
    ],
    "founder_habits": [
        {"habit": "Daily coding / architecture sessions", "frequency": "daily",   "strength": 0.85},
        {"habit": "Research reading (AGI papers)",         "frequency": "daily",   "strength": 0.75},
        {"habit": "Weekly milestone review",               "frequency": "weekly",  "strength": 0.70},
        {"habit": "Learning from user interactions",       "frequency": "always",  "strength": 0.90},
    ],
    "founder_stress": {
        "level": 0.40,
        "label": "moderate",
        "sources": ["budget constraints", "time pressure", "solo team"],
        "last_updated": None,
    },
    "founder_preferences": {
        "communication_style": "direct and practical",
        "language":            "Hindi/English mix preferred",
        "focus":               "practical over theoretical",
        "learning_style":      "iterative, build-and-test",
        "feedback_style":      "honest, even if hard",
    },
    "long_term_plans": [
        "Build AGI-level cognitive architecture (Level 10)",
        "Monetize ChetnaOS as AI consulting + SaaS platform",
        "Publish research on Developmental Cognitive Organisms",
        "Build a team of AI researchers around ChetnaOS",
        "Reach ₹1 crore/month ARR within 3 years",
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
                existing = json.load(open(p))
                # Merge new default keys in case old file lacks them
                for k, v in DEFAULT_CONTEXT.items():
                    if k not in existing:
                        existing[k] = v
                return existing
        except Exception:
            pass
        return dict(DEFAULT_CONTEXT)

    def _save(self):
        try:
            p = os.path.abspath(CTX_FILE)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            self._data["updated_at"] = datetime.utcnow().isoformat()
            with open(p, "w") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def get_system_context(self) -> str:
        """Compact string injected into every reasoning call."""
        d = self._data
        constraints  = "; ".join(d.get("founder_constraints", []))
        phases        = " → ".join(d.get("known_phases", []))
        goals_top     = "; ".join(g["goal"] for g in d.get("founder_goals", [])[:3])
        prefs         = d.get("founder_preferences", {})
        return (
            f"\n\n[FOUNDER CONTEXT]\n"
            f"Primary Mission: {d.get('primary_mission')}\n"
            f"Current Milestone: {d.get('current_milestone')}\n"
            f"Current Project: {d.get('current_project')}\n"
            f"Active Goals: {goals_top}\n"
            f"Constraints: {constraints}\n"
            f"Known Phases: {phases}\n"
            f"Communication preference: {prefs.get('language','Hindi/English')} — {prefs.get('communication_style','direct')}\n"
            f"When answering, use this context to give specific, grounded responses. "
            f"Avoid generic advice that ignores these real constraints."
        )

    def update_stress(self, level: float, source: str = None):
        self._data["founder_stress"]["level"] = round(min(1, max(0, level)), 2)
        self._data["founder_stress"]["label"] = (
            "low" if level < 0.3 else "moderate" if level < 0.6 else "high"
        )
        self._data["founder_stress"]["last_updated"] = datetime.utcnow().isoformat()
        if source and source not in self._data["founder_stress"]["sources"]:
            self._data["founder_stress"]["sources"].append(source)
        self._save()

    def complete_goal(self, goal_text: str):
        for g in self._data.get("founder_goals", []):
            if goal_text.lower() in g["goal"].lower():
                g["status"] = "completed"
                g["completed_at"] = datetime.utcnow().isoformat()
        self._save()

    def update(self, key: str, value):
        self._data[key] = value
        self._save()

    def get(self) -> dict:
        return dict(self._data)
