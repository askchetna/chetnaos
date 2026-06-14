"""
Homeostasis — Keeps the organism in balance and detects system stress.
"""


class Homeostasis:
    def check(self, development: dict, reflection: dict) -> dict:
        stats = development.get("stats", {})
        total = stats.get("total_cycles", 0)
        poor  = stats.get("poor_cycles",  0)
        good  = stats.get("good_cycles",  0)

        stress = 0
        alerts = []
        if total > 10 and poor / max(total, 1) > 0.4:
            stress += 2
            alerts.append("High poor-cycle ratio — review dharma configuration.")
        if stats.get("avg_confidence", 0.5) < 0.35:
            stress += 1
            alerts.append("Average confidence below threshold.")

        health = "healthy" if stress == 0 else ("stressed" if stress == 1 else "critical")
        return {
            "stage":  "HOMEOSTASIS",
            "health": health,
            "stress": stress,
            "alerts": alerts,
        }
