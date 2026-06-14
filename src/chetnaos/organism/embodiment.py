"""
Embodiment — The act of outputting the decision into the world.
"""


class Embodiment:
    def act(self, decision: dict, percept: dict) -> dict:
        intent = percept.get("intent", "statement")
        response = decision.get("final", "")

        # Format response based on intent
        if intent == "calculation" and "Result:" not in response:
            formatted = response
        elif intent == "goal":
            formatted = response
        else:
            formatted = response

        return {
            "stage":    "ACT",
            "output":   formatted,
            "intent":   intent,
            "executed": True,
        }
