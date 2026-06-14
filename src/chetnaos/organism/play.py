"""
Play — Explores alternative framings of the problem.
Divergent thinking stage — no commitment yet.
"""


class Play:
    def explore(self, attention: dict, imagination: dict) -> dict:
        possibilities = imagination.get("possibilities", [])
        focus = attention.get("focus", [])

        # Score each possibility by how well it fits the intent
        intent = attention.get("intent", "statement")
        intent_weights = {
            "question":    ["explain", "answer", "clarify"],
            "command":     ["step", "build", "create", "generate"],
            "calculation": ["compute", "calculate", "result"],
            "goal":        ["plan", "approach", "achieve"],
            "statement":   ["respond", "discuss", "engage"],
        }
        keywords = intent_weights.get(intent, ["respond"])

        scored = []
        for p in possibilities:
            score = sum(1 for kw in keywords if kw in p.lower())
            scored.append({"text": p, "fit_score": score})

        scored.sort(key=lambda x: x["fit_score"], reverse=True)
        best = scored[0]["text"] if scored else (possibilities[0] if possibilities else "Direct response")

        return {
            "stage": "PLAY",
            "explored": scored,
            "best_approach": best,
        }
