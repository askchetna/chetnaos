"""
Decision — Selects the final action/response from reasoned output.
"""


class Decision:
    def decide(self, reasoning: dict, reality: dict) -> dict:
        response = reasoning.get("response", "")
        confidence = reality.get("confidence", 0.5)
        passed = reality.get("passed", True)

        # If reality check failed badly, add a caveat
        if not passed and confidence < 0.3:
            response = (
                f"{response}\n\n"
                f"[Note: This response has low confidence ({confidence:.0%}). "
                "Please verify with additional sources.]"
            )
        elif not reality.get("belief_valid", True):
            response = (
                f"{response}\n\n"
                "[Note: This response may conflict with previously established information.]"
            )

        return {
            "stage":      "DECIDE",
            "final":      response,
            "confidence": confidence,
            "caveat":     not passed,
        }
