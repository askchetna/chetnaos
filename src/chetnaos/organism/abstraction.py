"""
Abstraction — Extracts high-level patterns and categories from the input.
"""


class Abstraction:
    DOMAIN_KEYWORDS = {
        "technology":   ["ai", "code", "software", "computer", "algorithm", "data", "api", "model"],
        "agriculture":  ["farm", "crop", "soil", "land", "harvest", "irrigation", "seed", "yield"],
        "science":      ["research", "experiment", "hypothesis", "theory", "evidence", "study"],
        "business":     ["revenue", "profit", "market", "customer", "sales", "roi", "growth"],
        "health":       ["medical", "disease", "treatment", "doctor", "hospital", "health", "diet"],
        "philosophy":   ["meaning", "consciousness", "identity", "purpose", "existence", "belief"],
        "general":      [],
    }

    def abstract(self, percept: dict, attention: dict) -> dict:
        focus = attention.get("focus", [])
        text_lower = " ".join(focus)

        domain = "general"
        domain_score = 0
        for d, keywords in self.DOMAIN_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > domain_score:
                domain = d
                domain_score = score

        return {
            "stage":  "ABSTRACT",
            "domain": domain,
            "complexity": "simple" if percept.get("token_count", 0) < 15 else "complex",
            "abstract_tags": focus[:4],
        }
