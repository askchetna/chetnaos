"""
Belief Validator — Checks whether a new output is consistent with core beliefs.
"""


class BeliefValidator:
    def validate(self, text: str, beliefs: list) -> dict:
        if not beliefs:
            return {"valid": True, "conflicts": [], "note": "No beliefs to validate against."}

        conflicts = []
        t = text.lower()
        for belief in beliefs:
            b = belief if isinstance(belief, str) else belief.get("text", "")
            b_lower = b.lower()
            # Flag if output is completely empty of belief topic keywords
            key_words = [w for w in b_lower.split() if len(w) > 5][:3]
            # Simple sentiment inversion check
            for kw in key_words:
                if kw in t:
                    if ("not " + kw) in t or ("never " + kw) in t:
                        conflicts.append(f"Contradicts belief: '{b[:60]}...'")
                        break

        return {
            "valid": len(conflicts) == 0,
            "conflicts": conflicts,
            "note": "Validated against belief store.",
        }
