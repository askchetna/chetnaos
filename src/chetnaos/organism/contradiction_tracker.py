"""
Contradiction Tracker (Enhanced) — Finds conflicts between:
  1. Beliefs vs Beliefs (antonym pairs)
  2. Beliefs vs Recent Memories
  3. Beliefs vs Founder Context (mission/goal contradictions)
Gap 2 from feedback.
"""
import json, os
from datetime import datetime

CONTRA_FILE = os.path.join(os.path.dirname(__file__), "../../..", "memory", "contradictions.json")

ANTONYM_PAIRS = [
    ("easy", "difficult"), ("easy", "hard"), ("simple", "complex"),
    ("fast", "slow"), ("reliable", "unreliable"), ("possible", "impossible"),
    ("high", "low"), ("strong", "weak"), ("good", "poor"), ("true", "false"),
    ("safe", "dangerous"), ("free", "expensive"), ("open", "closed"),
    ("grow", "shrink"), ("success", "failure"), ("helpful", "harmful"),
    ("clear", "confusing"), ("effective", "ineffective"), ("consistent", "inconsistent"),
]

# Phrases that contradict a growth/mission mindset
FOUNDER_CONFLICT_PHRASES = [
    "impossible", "can't be done", "will never work", "too difficult",
    "not worth trying", "give up", "hopeless", "no solution",
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

    def _add_if_new(self, item: dict):
        key = (item["belief_a"][:40], item["belief_b"][:40])
        existing = {(c["belief_a"][:40], c["belief_b"][:40]) for c in self._contradictions}
        if key not in existing:
            self._contradictions.insert(0, item)

    def scan(self, beliefs: list) -> list:
        """Belief-vs-Belief contradiction scan."""
        belief_texts = [
            (i, b.get("text", "").lower())
            for i, b in enumerate(beliefs) if b.get("text")
        ]
        for i, (idx_a, text_a) in enumerate(belief_texts):
            for j, (idx_b, text_b) in enumerate(belief_texts):
                if i >= j:
                    continue
                for (w1, w2) in ANTONYM_PAIRS:
                    if (w1 in text_a and w2 in text_b) or (w2 in text_a and w1 in text_b):
                        self._add_if_new({
                            "type":           "belief_vs_belief",
                            "belief_a":       beliefs[idx_a].get("text", "")[:80],
                            "belief_b":       beliefs[idx_b].get("text", "")[:80],
                            "conflict_score": 60,
                            "reason":         f"'{w1}' vs '{w2}'",
                            "status":         "needs_reflection",
                            "detected_at":    datetime.utcnow().isoformat(),
                        })
                        break

        self._contradictions = self._contradictions[:12]
        self._save()
        return self._contradictions

    def scan_memory(self, beliefs: list, recent_memories: list) -> list:
        """Gap 2: Belief-vs-Memory contradiction scan."""
        belief_texts = [(b.get("text", "").lower(), b.get("text", "")) for b in beliefs if b.get("text")]
        for mem in recent_memories[:10]:
            mem_text = (mem.get("text") or mem.get("content") or "").lower()
            if not mem_text:
                continue
            for (btext_lower, btext_orig) in belief_texts:
                for (w1, w2) in ANTONYM_PAIRS:
                    if (w1 in btext_lower and w2 in mem_text) or (w2 in btext_lower and w1 in mem_text):
                        self._add_if_new({
                            "type":           "belief_vs_memory",
                            "belief_a":       btext_orig[:80],
                            "belief_b":       mem_text[:80],
                            "conflict_score": 45,
                            "reason":         f"Belief conflicts with recent memory: '{w1}' vs '{w2}'",
                            "status":         "needs_reflection",
                            "detected_at":    datetime.utcnow().isoformat(),
                        })
                        break

        self._contradictions = self._contradictions[:12]
        self._save()
        return self._contradictions

    def scan_founder(self, beliefs: list, founder_mission: str) -> list:
        """Gap 2: Belief-vs-Founder-Mission contradiction scan."""
        mission_lower = founder_mission.lower()
        for b in beliefs:
            text = b.get("text", "").lower()
            for phrase in FOUNDER_CONFLICT_PHRASES:
                if phrase in text:
                    self._add_if_new({
                        "type":           "belief_vs_founder_mission",
                        "belief_a":       b.get("text", "")[:80],
                        "belief_b":       f"Founder mission: {founder_mission[:60]}",
                        "conflict_score": 70,
                        "reason":         f"Belief contains '{phrase}' — conflicts with growth mission",
                        "status":         "critical",
                        "detected_at":    datetime.utcnow().isoformat(),
                    })

        self._contradictions = self._contradictions[:12]
        self._save()
        return self._contradictions

    def get(self) -> list:
        return list(self._contradictions)

    def count(self) -> int:
        return len(self._contradictions)
