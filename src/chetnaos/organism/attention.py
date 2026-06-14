"""
Attention — Identifies what the organism should focus on.
Filters the percept and highlights key concepts.
"""
import re


class Attention:
    STOP_WORDS = set(
        "a an the is are was were be been being have has had do does did "
        "will would could should may might shall can i you we they he she it "
        "this that these those and or but in on at to for of with".split()
    )

    def attend(self, percept: dict) -> dict:
        text = percept.get("raw", "")
        tokens = text.lower().split()
        keywords = [
            t for t in tokens
            if t not in self.STOP_WORDS and len(t) > 2 and t.isalpha()
        ]

        # Urgency heuristics
        urgent = any(w in text.lower() for w in ["urgent", "asap", "immediately", "help", "emergency"])
        emotional = any(w in text.lower() for w in ["sad", "happy", "angry", "scared", "worried", "excited"])

        return {
            "stage":    "ATTEND",
            "focus":    keywords[:8],
            "urgent":   urgent,
            "emotional": emotional,
            "intent":   percept.get("intent", "statement"),
            "priority": "HIGH" if urgent else ("MEDIUM" if emotional else "NORMAL"),
        }
