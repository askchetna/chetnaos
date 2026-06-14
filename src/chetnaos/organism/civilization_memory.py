"""
Civilization Memory — The organism's contribution to long-term collective knowledge.
Stores high-quality outputs that survive sleep cycles.
"""
import json, os
from datetime import datetime

CIV_FILE = os.path.join(os.path.dirname(__file__), "../../..", "memory", "civilization.jsonl")


class CivilizationMemory:
    QUALITY_THRESHOLD = 75

    def contribute(self, cycle_score: int, output: str, domain: str) -> dict:
        if cycle_score >= self.QUALITY_THRESHOLD:
            entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "score": cycle_score,
                "domain": domain,
                "text": output[:400],
            }
            self._append(entry)
            return {"contributed": True, "score": cycle_score}
        return {"contributed": False, "score": cycle_score}

    def _append(self, entry: dict):
        try:
            p = os.path.abspath(CIV_FILE)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass
