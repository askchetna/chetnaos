"""
Reality Check Layer — Grounds LLM output against evidence and logical consistency.
"""
from .confidence_engine import ConfidenceEngine
from .contradiction_detector import ContradictionDetector
from .evidence_engine import EvidenceEngine
from .truth_estimator import TruthEstimator
from .belief_validator import BeliefValidator
from .source_ranker import SourceRanker


class RealityChecker:
    """Orchestrates all reality-checking sub-modules."""

    def __init__(self):
        self.confidence   = ConfidenceEngine()
        self.contradiction = ContradictionDetector()
        self.evidence     = EvidenceEngine()
        self.truth        = TruthEstimator()
        self.validator    = BeliefValidator()
        self.ranker       = SourceRanker()

    def check(self, output: str, context: dict) -> dict:
        """Run all checks and return a consolidated reality report."""
        ev   = self.evidence.assess(output, context)
        conf = self.confidence.score(output, ev)
        contr = self.contradiction.detect(output, context.get("beliefs", []))
        truth = self.truth.estimate(output, ev, conf)
        valid = self.validator.validate(output, context.get("beliefs", []))
        source = self.ranker.rank_output(output)

        passed = conf["score"] >= 0.4 and not contr["critical_contradiction"]
        return {
            "passed": passed,
            "confidence": conf["score"],
            "confidence_level": conf["level"],
            "evidence_available": ev["available"],
            "truth_estimate": truth["estimate"],
            "contradictions": contr["contradictions"],
            "belief_valid": valid["valid"],
            "source_trust": source["trust_score"],
            "source_reliable": source["reliable"],
            "flags": ev["flags"] + contr["flags"],
            "recommendation": truth["recommendation"],
        }


__all__ = ["RealityChecker", "ConfidenceEngine", "ContradictionDetector",
           "EvidenceEngine", "TruthEstimator", "BeliefValidator", "SourceRanker"]
