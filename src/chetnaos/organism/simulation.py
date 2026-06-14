"""
Simulation Engine — Generates Plan A, B, C and predicts their outcomes.
Priority 2 from feedback: divergent scenario planning before commitment.
"""


class SimulationEngine:
    def simulate(self, plan: str, abstraction: dict, llm_router=None) -> dict:
        """Generate 3 alternative plans and predict outcomes for each."""
        domain     = abstraction.get("domain", "general")
        complexity = abstraction.get("complexity", "simple")

        if not llm_router or complexity == "simple":
            return self._default_simulation(plan, domain)

        try:
            prompt = (
                f"Given this planned approach: \"{plan}\"\n"
                f"Domain: {domain}\n\n"
                f"Generate exactly 3 alternative plans with predicted outcomes. "
                f"Format:\n"
                f"Plan A: [approach] | Outcome: [likely result]\n"
                f"Plan B: [approach] | Outcome: [likely result]\n"
                f"Plan C: [approach] | Outcome: [likely result]\n"
                f"Keep each line under 80 characters."
            )
            raw = llm_router.complete(prompt, max_tokens=200)
            plans = self._parse_plans(raw)
            if plans:
                return {
                    "stage":    "SIMULATE",
                    "plans":    plans,
                    "selected": plans[0]["plan"],
                    "basis":    "llm_simulation",
                }
        except Exception:
            pass

        return self._default_simulation(plan, domain)

    def _parse_plans(self, raw: str) -> list:
        plans = []
        for line in raw.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            if "|" in line and any(line.lower().startswith(p) for p in ["plan a", "plan b", "plan c"]):
                parts = line.split("|", 1)
                plan_text = parts[0].split(":", 1)[-1].strip()
                outcome   = parts[1].replace("Outcome:", "").strip() if len(parts) > 1 else "—"
                plans.append({"plan": plan_text, "outcome": outcome})
        return plans[:3]

    def _default_simulation(self, plan: str, domain: str) -> dict:
        return {
            "stage":  "SIMULATE",
            "plans":  [
                {"plan": plan,                             "outcome": "Most likely path."},
                {"plan": f"Simplified {domain} approach",  "outcome": "Faster but less thorough."},
                {"plan": f"Step-by-step {domain} breakdown","outcome": "Clearer but longer."},
            ],
            "selected": plan,
            "basis":    "default",
        }
