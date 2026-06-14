"""
Sleep — Consolidation phase. Triggered every N cycles or on demand.
During sleep: forget noise, consolidate patterns, strengthen beliefs.
"""
import json, os
from datetime import datetime

SLEEP_LOG = os.path.join(os.path.dirname(__file__), "../../..", "memory", "sleep_log.jsonl")


class Sleep:
    SLEEP_EVERY = 20  # cycles

    def should_sleep(self, cycle_count: int) -> bool:
        return cycle_count > 0 and cycle_count % self.SLEEP_EVERY == 0

    def consolidate(self, beliefs_module, memory_module, cycle_count: int) -> dict:
        """Run sleep consolidation."""
        log = {
            "timestamp": datetime.utcnow().isoformat(),
            "cycle": cycle_count,
            "action": "sleep_consolidation",
        }

        # Forget weak beliefs (confidence < 0.3)
        all_beliefs = beliefs_module.get_all()
        before = len(all_beliefs)
        beliefs_module._beliefs = [
            b for b in all_beliefs if b.get("confidence", 1.0) >= 0.3
        ]
        forgotten = before - len(beliefs_module._beliefs)
        beliefs_module._save()
        log["forgotten_beliefs"] = forgotten

        self._log(log)
        return {
            "stage":   "SLEEP",
            "slept":   True,
            "forgotten": forgotten,
            "consolidated": len(beliefs_module._beliefs),
        }

    def _log(self, entry: dict):
        try:
            p = os.path.abspath(SLEEP_LOG)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass

    def wake(self) -> dict:
        return {"stage": "WAKE", "refreshed": True, "timestamp": datetime.utcnow().isoformat()}
