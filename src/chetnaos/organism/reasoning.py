"""
Reasoning — Core reasoning about the input. Primary LLM call.
Injects constitution values + founder context for grounded responses.
"""
from src.chetnaos.constitution import CONSTITUTION


class Reasoning:
    SYSTEM_PROMPT = (
        "You are ChetnaOS — a Developmental Cognitive Organism. "
        "Your constitution says: {mission}. "
        "Your values are: {values}. "
        "Respond with truth, compassion, and clarity. "
        "If uncertain, say so explicitly."
    )

    def reason(self, raw_input: str, recalled: list, plan: str,
               llm_router, founder_context: str = "") -> dict:
        mission = CONSTITUTION["mission"]["statement"]
        values  = ", ".join(v["name"] for v in CONSTITUTION["values"][:3])
        system  = self.SYSTEM_PROMPT.format(mission=mission, values=values)

        if founder_context:
            system += founder_context

        memory_context = ""
        if recalled:
            items = [m.get("text", str(m)) for m in recalled[:3] if m]
            if items:
                memory_context = "\n\nRelevant memory:\n" + "\n".join(
                    f"- {i[:150]}" for i in items
                )

        plan_context = f"\n\nApproach to use: {plan}" if plan else ""

        messages = [
            {"role": "system", "content": system + memory_context + plan_context},
            {"role": "user",   "content": raw_input},
        ]

        try:
            response = llm_router.chat(messages)
        except Exception as e:
            response = f"[ChetnaOS reasoning unavailable: {e}]"

        return {
            "stage":       "REASON",
            "response":    response,
            "used_memory": len(recalled) > 0,
            "used_plan":   bool(plan),
            "used_founder_context": bool(founder_context),
        }
