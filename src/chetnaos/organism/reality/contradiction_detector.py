"""
Contradiction Detector — Checks output against existing beliefs for contradictions.
"""


class ContradictionDetector:
    def detect(self, text: str, beliefs: list) -> dict:
        contradictions = []
        flags = []
        t = text.lower()

        # Simple negation-based contradiction check
        for belief in beliefs:
            b_text = belief.get("text", "").lower() if isinstance(belief, dict) else str(belief).lower()
            if not b_text:
                continue
            # Look for direct negations of key belief words
            core_words = [w for w in b_text.split() if len(w) > 4]
            for word in core_words[:5]:
                if f"not {word}" in t or f"never {word}" in t or f"no {word}" in t:
                    contradictions.append({
                        "belief": b_text[:100],
                        "conflict": f"Output negates '{word}' from existing belief.",
                    })
                    break

        critical = len(contradictions) >= 2
        if critical:
            flags.append("critical_contradiction_detected")

        return {
            "contradictions": contradictions,
            "critical_contradiction": critical,
            "flags": flags,
        }
