"""
Self-Trainer — Autonomous learning goal generation (Gap 6).
Analyzes skill gaps and generates specific training suggestions.

"Current weakness: Sales → Suggested training: 5 sales interactions → Expected: +3%"
"""
import os, json
from datetime import datetime

from src.chetnaos.memory.json_loader import load_training_goals, save_json, memory_path

TRAINER_FILE = os.path.join(os.path.dirname(__file__), "../../..", "memory", "training_goals.json")

# Target mastery levels for each skill
SKILL_TARGETS = {
    "Architecture":  0.96,
    "Research":      0.92,
    "Philosophy":    0.85,
    "Coding":        0.86,
    "Communication": 0.80,
    "Business":      0.76,
    "Agriculture":   0.70,
    "Sales":         0.65,
}

# Domain keywords that improve each skill (for routing suggestions)
SKILL_PRACTICE_DOMAINS = {
    "Architecture":  "system design, cognitive architecture, AI architecture",
    "Research":      "research, analysis, study, investigation",
    "Philosophy":    "ethics, consciousness, meaning, values",
    "Coding":        "programming, debugging, code, algorithm",
    "Communication": "explain, clarify, teach, describe",
    "Business":      "business, strategy, planning, revenue",
    "Agriculture":   "farming, crops, soil, harvest, seeds",
    "Sales":         "sales, clients, pitch, persuasion, revenue",
}


class SelfTrainer:
    def __init__(self):
        self._goals = self._load()

    def _load(self) -> list:
        return load_training_goals([])

    def _save(self):
        save_json(memory_path("training_goals.json"), self._goals)

    def generate_goals(self, skills_all: dict) -> list:
        """
        Analyze skill gaps and return top 3 training suggestions.
        skills_all: {skill_name: {score, interactions, category, ...}}
        """
        suggestions = []
        for skill_name, target in SKILL_TARGETS.items():
            if skill_name not in skills_all:
                continue
            current = skills_all[skill_name]["score"]
            gap     = target - current
            if gap <= 0.03:  # Already near target
                continue

            interactions_needed = max(3, int(gap * 60))
            improvement_pct     = round(gap * 0.35 * 100, 1)  # 35% of gap per training burst
            practice_hint       = SKILL_PRACTICE_DOMAINS.get(skill_name, skill_name.lower())

            suggestions.append({
                "skill":                skill_name,
                "current_pct":          round(current * 100, 1),
                "target_pct":           round(target * 100, 1),
                "gap_pct":              round(gap * 100, 1),
                "priority":             round(gap * 100, 1),
                "suggested_training":   f"{interactions_needed} {skill_name.lower()} interactions",
                "practice_topics":      practice_hint,
                "expected_improvement": f"+{improvement_pct:.1f}%",
                "category":             skills_all[skill_name].get("category", "general"),
            })

        suggestions.sort(key=lambda x: x["gap_pct"], reverse=True)
        top3 = suggestions[:3]

        # Persist so dashboard can show them at any time
        self._goals = top3
        self._save()
        return top3

    def get(self) -> list:
        return list(self._goals)
