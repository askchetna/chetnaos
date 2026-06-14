"""
Imagination — Generates possible responses/approaches before committing.
Uses LLM to brainstorm.
"""


class Imagination:
    def imagine(self, attention: dict, llm_router=None) -> dict:
        focus = attention.get("focus", [])
        intent = attention.get("intent", "statement")

        possibilities = []
        if llm_router and focus:
            try:
                prompt = (
                    f"Given a user message about: {', '.join(focus[:5])}\n"
                    f"Intent: {intent}\n"
                    f"List 3 distinct ways to approach responding (one line each):"
                )
                result = llm_router.complete(prompt, max_tokens=150)
                possibilities = [
                    line.strip().lstrip("123.-) ")
                    for line in result.strip().split("\n")
                    if line.strip()
                ][:3]
            except Exception:
                pass

        if not possibilities:
            possibilities = [
                f"Direct answer about {focus[0] if focus else 'the topic'}",
                "Clarifying question to understand better",
                "Step-by-step explanation",
            ]

        return {
            "stage": "IMAGINE",
            "possibilities": possibilities,
            "count": len(possibilities),
        }
