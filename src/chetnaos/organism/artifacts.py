"""
Artifacts — Tracks outputs created by the organism (documents, code, analyses).
"""
import json, os
from datetime import datetime

ARTIFACTS_FILE = os.path.join(os.path.dirname(__file__), "../../..", "memory", "artifacts.jsonl")


class Artifacts:
    def store(self, output: str, domain: str, intent: str) -> dict:
        if intent in ("calculation", "search", "web_fetch", "statement") and len(output) > 200:
            artifact = {
                "timestamp": datetime.utcnow().isoformat(),
                "domain": domain,
                "intent": intent,
                "text": output[:500],
            }
            self._append(artifact)
            return {"stored": True, "artifact": artifact}
        return {"stored": False}

    def _append(self, artifact: dict):
        try:
            p = os.path.abspath(ARTIFACTS_FILE)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "a") as f:
                f.write(json.dumps(artifact) + "\n")
        except Exception:
            pass
