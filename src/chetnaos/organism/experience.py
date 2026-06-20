"""
Experience — Records the full cycle as an experience in episodic memory.
"""
from datetime import datetime
import json, os

EXP_FILE = os.path.join(os.path.dirname(__file__), "../../..", "memory", "experiences.jsonl")


class Experience:
    def record(self, cycle_snapshot: dict) -> dict:
        exp = {
            "timestamp": datetime.utcnow().isoformat(),
            "input":      cycle_snapshot.get("input", ""),
            "output":     cycle_snapshot.get("output", ""),
            "confidence": cycle_snapshot.get("confidence", 0.5),
            "domain":     cycle_snapshot.get("domain", "general"),
            "quality":    cycle_snapshot.get("quality", "fair"),
            "cycle":      cycle_snapshot.get("cycle_count", 0),
        }
        self._append(exp)
        return {"stage": "EXPERIENCE", "recorded": True, "experience": exp}

    def _append(self, exp: dict):
        try:
            p = os.path.abspath(EXP_FILE)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "a") as f:
                f.write(json.dumps(exp) + "\n")
        except Exception:
            pass

    def enrich_last(self, fields: dict) -> None:
        """Update the most recent experience entry with post-reflection fields."""
        try:
            p = os.path.abspath(EXP_FILE)
            if not os.path.exists(p):
                return
            with open(p, encoding="utf-8") as f:
                lines = [l.strip() for l in f if l.strip()]
            if not lines:
                return
            last = json.loads(lines[-1])
            last.update(fields)
            lines[-1] = json.dumps(last)
            with open(p, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
        except Exception:
            pass
