"""
Skills — Tracks accumulated competencies of the organism.
Each skill has a confidence score (0.0–1.0) that evolves with experience.
Skill Transfer: competence in one domain lifts adjacent domains.
"""
import json, os
from datetime import datetime

SKILLS_FILE = os.path.join(os.path.dirname(__file__), "../../..", "memory", "skills.json")

DEFAULT_SKILLS = {
    "Architecture":   {"score": 0.91, "interactions": 0, "category": "core"},
    "Research":       {"score": 0.83, "interactions": 0, "category": "core"},
    "Philosophy":     {"score": 0.75, "interactions": 0, "category": "core"},
    "Coding":         {"score": 0.72, "interactions": 0, "category": "technical"},
    "Communication":  {"score": 0.68, "interactions": 0, "category": "social"},
    "Business":       {"score": 0.61, "interactions": 0, "category": "applied"},
    "Agriculture":    {"score": 0.62, "interactions": 0, "category": "applied"},
    "Sales":          {"score": 0.38, "interactions": 0, "category": "applied"},
}

# Skill transfer graph: learning X also improves Y by factor
TRANSFER_GRAPH = {
    "Research":      [("Architecture", 0.15), ("Philosophy", 0.20), ("Coding", 0.08)],
    "Architecture":  [("Coding", 0.12), ("Research", 0.10)],
    "Philosophy":    [("Communication", 0.18), ("Research", 0.10)],
    "Coding":        [("Architecture", 0.10), ("Research", 0.05)],
    "Business":      [("Sales", 0.25), ("Communication", 0.12)],
    "Sales":         [("Communication", 0.20), ("Business", 0.10)],
    "Communication": [("Sales", 0.08), ("Philosophy", 0.06)],
    "Agriculture":   [("Research", 0.05), ("Business", 0.04)],
}

DOMAIN_TO_SKILL = {
    "technology":  "Coding",
    "agriculture": "Agriculture",
    "science":     "Research",
    "business":    "Business",
    "health":      "Research",
    "philosophy":  "Philosophy",
    "general":     "Communication",
}


class Skills:
    def __init__(self):
        self._skills = self._load()

    def _load(self) -> dict:
        try:
            p = os.path.abspath(SKILLS_FILE)
            if os.path.exists(p):
                with open(p) as f:
                    return json.load(f)
        except Exception:
            pass
        return {k: dict(v) for k, v in DEFAULT_SKILLS.items()}

    def _save(self):
        try:
            p = os.path.abspath(SKILLS_FILE)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as f:
                json.dump(self._skills, f, indent=2)
        except Exception:
            pass

    def get_all(self) -> dict:
        return {k: dict(v) for k, v in self._skills.items()}

    def get_ranked(self) -> list:
        ranked = sorted(
            [{"name": k, **v} for k, v in self._skills.items()],
            key=lambda x: x["score"], reverse=True
        )
        return ranked

    def practice(self, domain: str, quality: str = "fair"):
        """Called after each cognitive cycle to update skill scores."""
        skill_name = DOMAIN_TO_SKILL.get(domain, "Communication")
        if skill_name not in self._skills:
            return

        delta = {"good": 0.008, "fair": 0.003, "poor": -0.002}.get(quality, 0.002)

        self._skills[skill_name]["score"] = round(
            min(0.99, max(0.01, self._skills[skill_name]["score"] + delta)), 3
        )
        self._skills[skill_name]["interactions"] = self._skills[skill_name].get("interactions", 0) + 1
        self._skills[skill_name]["last_practiced"] = datetime.utcnow().isoformat()

        # Skill Transfer
        for (transfer_skill, factor) in TRANSFER_GRAPH.get(skill_name, []):
            if transfer_skill in self._skills:
                transfer_delta = delta * factor
                self._skills[transfer_skill]["score"] = round(
                    min(0.99, max(0.01, self._skills[transfer_skill]["score"] + transfer_delta)), 3
                )

        self._save()

    def get_transfers(self) -> list:
        """Return active skill transfer paths."""
        transfers = []
        for source, targets in TRANSFER_GRAPH.items():
            for (target, factor) in targets:
                if factor >= 0.12:  # Only show strong transfers
                    transfers.append({"from": source, "to": target, "strength": factor})
        return transfers
