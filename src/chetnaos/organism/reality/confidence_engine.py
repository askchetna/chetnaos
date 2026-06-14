"""
Confidence Engine — Computes an overall confidence score 0.0–1.0 for an output.
"""


class ConfidenceEngine:
    UNCERTAINTY_PHRASES = [
        "i'm not sure", "i don't know", "unclear", "uncertain",
        "hard to say", "difficult to determine", "no information",
        "cannot confirm", "unverified",
    ]
    CONFIDENT_PHRASES = [
        "definitely", "certainly", "confirmed", "proven", "established",
        "without doubt", "clearly", "obviously", "always", "never",
    ]

    def score(self, text: str, evidence: dict) -> dict:
        t = text.lower()
        base = 0.6

        # Evidence adjustments
        if evidence["available"]:
            base += 0.15
        base -= evidence["speculative_markers"] * 0.05
        base += evidence["factual_markers"] * 0.05
        if evidence["has_numbers"]:
            base += 0.05

        # Phrase adjustments
        uncertain_hits  = sum(1 for p in self.UNCERTAINTY_PHRASES if p in t)
        confident_hits  = sum(1 for p in self.CONFIDENT_PHRASES   if p in t)
        base -= uncertain_hits * 0.08
        base += confident_hits * 0.03

        # Length adjustment: very short = low confidence
        words = len(text.split())
        if words < 10:
            base -= 0.1
        elif words > 50:
            base += 0.05

        score = max(0.05, min(1.0, round(base, 2)))
        if score >= 0.75:
            level = "HIGH"
        elif score >= 0.50:
            level = "MEDIUM"
        elif score >= 0.30:
            level = "LOW"
        else:
            level = "VERY_LOW"

        return {"score": score, "level": level}
