"""
Planning — Generates a lightweight action plan before reasoning.
"""


class Planning:
    def plan(self, play_result: dict, abstraction: dict, llm_router=None) -> dict:
        best_approach = play_result.get("best_approach", "Direct response")
        domain = abstraction.get("domain", "general")
        complexity = abstraction.get("complexity", "simple")

        if complexity == "simple" or not llm_router:
            selected_plan = best_approach
        else:
            try:
                prompt = (
                    f"Task domain: {domain}. Best approach: {best_approach}.\n"
                    f"Write a 1-sentence plan for responding to a {complexity} {domain} question:"
                )
                selected_plan = llm_router.complete(prompt, max_tokens=60).strip()
            except Exception:
                selected_plan = best_approach

        return {
            "stage": "PLAN",
            "plan": selected_plan,
            "domain": domain,
            "complexity": complexity,
        }
