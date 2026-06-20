"""
Developmental Age — stage derived from experience quality, not cycle count alone.
"""
from __future__ import annotations

STAGES = [
    "Seed",
    "Early Organism",
    "Growing Organism",
    "Reflective Organism",
    "Autonomous Organism",
    "Wise Organism",
]

_TRAIT_KEYS = (
    "curiosity", "discipline", "reflection", "creativity",
    "consistency", "wisdom", "research_maturity",
)


class DevelopmentalAge:
    @staticmethod
    def compute(development: dict, identity: dict) -> dict:
        total = max(development.get("total_cycles", 0), 1)
        good = development.get("good_cycles", 0)
        quality_ratio = good / total
        traits = development.get("traits") or {}
        trait_avg = (
            sum(float(traits.get(k, 0.5)) for k in _TRAIT_KEYS) / len(_TRAIT_KEYS)
            if traits else 0.5
        )
        stability = float(identity.get("identity_stability", 0.95))
        maturity_score = (quality_ratio * 0.45) + (trait_avg * 0.35) + (stability * 0.2)

        if maturity_score < 0.25:
            stage = "Seed"
        elif maturity_score < 0.40:
            stage = "Early Organism"
        elif maturity_score < 0.55:
            stage = "Growing Organism"
        elif maturity_score < 0.70:
            stage = "Reflective Organism"
        elif maturity_score < 0.85:
            stage = "Autonomous Organism"
        else:
            stage = "Wise Organism"

        return {
            "stage": stage,
            "maturity_score": round(maturity_score, 3),
            "quality_ratio": round(quality_ratio, 3),
            "trait_average": round(trait_avg, 3),
        }

    @staticmethod
    def apply_to_development(development_data: dict, identity: dict) -> str:
        age = DevelopmentalAge.compute(development_data, identity)
        development_data["developmental_age"] = age["stage"]
        return age["stage"]
