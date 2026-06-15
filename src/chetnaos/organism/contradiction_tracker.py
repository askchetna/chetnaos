"""
Contradiction Tracker — Finds and tracks logical conflicts between beliefs.
Human brain maintains contradictions — this system surfaces them for reflection.
"""
import json, os
from datetime import datetime

CONTRA_FILE = os.path.join(os.path.dirname(__file__), "../../..", "memory", "contradictions.json")

# Antonym pairs for quick conflict detection
ANTONYM_PAIRS = [
    ("easy", "difficult"), ("easy", "hard"), ("simple", "complex"),
    ("fast", "slow"), ("reliable", "unreliable"), ("possible", "impossible"),
    ("high", "low"), ("strong", "weak"), ("good", "poor"), ("true", "false"),
    ("safe", "dangerous"), ("free", "expensive"), ("open", "closed"),
    ("grow", "shrink"), ("success", "failure"), ("helpful", "harmful"),
]


class ContradictionTracker:
    def __init__(self):
        self._contradictions = self._load()

    def _load(self) -> list:
        try:
            p = os.path.abspath(CONTRA_FILE)
            if os.path.exists(p):
                with open(p) as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def _save(self):
        try:
            p = os.path.abspath(CONTRA_FILE)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as f:
                json.dump(self._contradictions, f, indent=2)
        except Exception:
            pass

    def scan(self, beliefs: list) -> list:
        """Scan belief list for contradictions and update internal list."""
        found = []
        belief_texts = [
            (b.get("id", i), b.get("text", "").lower())
            for i, b in enumerate(beliefs) if b.get("text")
        ]

        for i, (id_a, text_a) in enumerate(belief_texts):
            for j, (id_b, text_b) in enumerate(belief_texts):
                if i >= j:
                    continue
                conflict_score = 0
                conflict_reason = ""
                for (word1, word2) in ANTONYM_PAIRS:
                    if word1 in text_a and word2 in text_b:
                        conflict_score += 25
                        conflict_reason = f"'{word1}' vs '{word2}'"
                        break
                    if word2 in text_a and word1 in text_b:
                        conflict_score += 25
                        conflict_reason = f"'{word2}' vs '{word1}'"
                        break

                if conflict_score >= 25:
                    found.append({
                        "belief_a":       beliefs[i].get("text", "")[:80],
                        "belief_b":       beliefs[j].get("text", "")[:80],
                        "conflict_score": min(99, conflict_score),
                        "reason":         conflict_reason,
                        "status":         "needs_reflection",
                        "detected_at":    datetime.utcnow().isoformat(),
                    })

        # Merge with existing — keep unique pairs
        existing_pairs = {(c["belief_a"][:40], c["belief_b"][:40]) for c in self._contradictions}
        for f in found:
            key = (f["belief_a"][:40], f["belief_b"][:40])
            if key not in existing_pairs:
                self._contradictions.insert(0, f)
                existing_pairs.add(key)

        self._contradictions = self._contradictions[:10]
        self._save()
        return self._contradictions

    def get(self) -> list:
        return list(self._contradictions)

    def count(self) -> int:
        return len(self._contradictions)
