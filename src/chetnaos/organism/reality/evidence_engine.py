"""
Evidence Engine — Determines whether evidence exists for a claim.
"""
import re


class EvidenceEngine:
    FACTUAL_MARKERS = [
        "according to", "research shows", "studies indicate", "data shows",
        "proven", "established", "confirmed", "documented", "source:",
        "published", "peer-reviewed", "statistics show",
    ]
    SPECULATIVE_MARKERS = [
        "i think", "i believe", "maybe", "perhaps", "possibly", "might be",
        "could be", "seems like", "appears to", "i guess", "probably",
        "speculative", "hypothetical", "unverified",
    ]

    def assess(self, text: str, context: dict) -> dict:
        t = text.lower()
        factual   = sum(1 for m in self.FACTUAL_MARKERS  if m in t)
        speculate = sum(1 for m in self.SPECULATIVE_MARKERS if m in t)
        has_numbers = bool(re.search(r'\d+\.?\d*\s*(%|percent|km|kg|million|billion|crore)', t))
        available = factual > 0 or has_numbers
        flags = []
        if speculate > 2:
            flags.append("high_speculation")
        if factual == 0 and not has_numbers:
            flags.append("no_evidence_markers")
        return {
            "available": available,
            "factual_markers": factual,
            "speculative_markers": speculate,
            "has_numbers": has_numbers,
            "flags": flags,
        }
