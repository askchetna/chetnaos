"""
Truth Estimator — Estimates the likely truthfulness of an output.
"""


class TruthEstimator:
    def estimate(self, text: str, evidence: dict, confidence: dict) -> dict:
        score = confidence["score"]
        if evidence["available"]:
            estimate = "likely_true" if score >= 0.7 else "possibly_true"
        else:
            if score >= 0.6:
                estimate = "possibly_true"
            elif score >= 0.4:
                estimate = "uncertain"
            else:
                estimate = "low_confidence"

        recommendation = {
            "likely_true":     "Accept with normal confidence.",
            "possibly_true":   "Accept but note it may need verification.",
            "uncertain":       "Flag to user as uncertain; seek corroboration.",
            "low_confidence":  "Present with explicit uncertainty caveat.",
        }[estimate]

        return {
            "estimate": estimate,
            "score": score,
            "recommendation": recommendation,
        }
