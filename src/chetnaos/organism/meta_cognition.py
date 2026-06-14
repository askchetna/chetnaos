"""
Meta-Cognition — Self-evaluation after every cycle.
Priority 5 from feedback:
  "Why did I answer this?"
  "Was I correct?"
  "Can I improve?"
  "Store the learning."
"""
import json, os
from datetime import datetime

META_LOG = os.path.join(os.path.dirname(__file__), "../../..", "memory", "meta_cognition.jsonl")


class MetaCognition:
    def evaluate(self, percept: dict, decision: dict, reflection: dict,
                 reality: dict) -> dict:
        intent     = percept.get("intent", "statement")
        quality    = reflection.get("quality", "fair")
        confidence = reality.get("confidence", 0.5)
        dharma     = reflection.get("dharma_score", 70)
        corrections = reflection.get("corrections", [])

        # Q1: Why did I answer this?
        why = f"User intent was '{intent}'. Purpose: serve with truth and compassion."

        # Q2: Was I correct?
        correctness_score = round(confidence * 0.5 + dharma / 100 * 0.5, 2)
        was_correct = correctness_score >= 0.6

        # Q3: Can I improve?
        improvements = []
        if confidence < 0.6:
            improvements.append("Increase confidence — research this domain more.")
        if corrections:
            improvements.append(f"Address: {corrections[0]}")
        if quality == "poor":
            improvements.append("Response quality was poor — review dharma alignment.")
        if not improvements:
            improvements.append("Response was solid. Repeat this pattern.")

        meta = {
            "timestamp":         datetime.utcnow().isoformat(),
            "why_answered":      why,
            "was_correct":       was_correct,
            "correctness_score": correctness_score,
            "improvements":      improvements,
            "quality":           quality,
        }
        self._store(meta)

        return {
            "stage":          "META_COGNITION",
            "why":            why,
            "was_correct":    was_correct,
            "correctness":    correctness_score,
            "can_improve":    improvements,
            "self_verdict":   "good" if was_correct and quality != "poor" else "needs_work",
        }

    def _store(self, entry: dict):
        try:
            p = os.path.abspath(META_LOG)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass
