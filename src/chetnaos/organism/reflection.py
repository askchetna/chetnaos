"""
Reflection — Evaluates how well the cycle performed.
"""
from reflection.reflection_v2 import evaluate_decision


class Reflection:
    def reflect(self, decision: dict, reality: dict, context: dict) -> dict:
        output_text = decision.get("final", "")
        dharma_result = evaluate_decision(
            decision={"text": output_text, "rationale": output_text},
            context={
                "risk_level": context.get("risk_level", "low"),
                "intent": context.get("intent", "statement"),
                "requires_grounding": False,
            }
        )

        confidence = reality.get("confidence", 0.5)
        cycle_score = round(
            (dharma_result["score"] / 100 * 0.6 + confidence * 0.4) * 100
        )

        return {
            "stage":       "REFLECT",
            "dharma_score": dharma_result["score"],
            "dharma_ok":    dharma_result["dharma_ok"],
            "cycle_score":  cycle_score,
            "corrections":  dharma_result.get("corrections", []),
            "quality":      "good" if cycle_score >= 70 else ("fair" if cycle_score >= 50 else "poor"),
        }
