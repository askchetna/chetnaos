"""
Perception — Structures raw input into a parsed percept.
"""
import re


class Perception:
    INTENT_PATTERNS = {
        "question":    [r'\?$', r'^(what|who|when|where|why|how|is|are|can|could|would|should)'],
        "command":     [r'^(do|make|create|build|write|generate|help|give|show|list|explain)'],
        "calculation": [r'calc:', r'calculate', r'\d+\s*[\+\-\*\/]\s*\d+'],
        "search":      [r'^search\s', r'look up', r'find info'],
        "web_fetch":   [r'^web:\s*https?://'],
        "goal":        [r'^goal:', r'i want to', r'i need to', r'achieve', r'accomplish'],
        "statement":   [r'.+'],
    }

    def perceive(self, raw_input: str) -> dict:
        text = raw_input.strip()
        intent = "statement"
        for name, patterns in self.INTENT_PATTERNS.items():
            for pat in patterns:
                if re.search(pat, text, re.IGNORECASE):
                    intent = name
                    break
            if intent != "statement":
                break

        tokens = text.split()
        return {
            "stage":       "OBSERVE",
            "raw":         text,
            "intent":      intent,
            "length":      len(text),
            "token_count": len(tokens),
            "language":    "en",
            "has_code":    "```" in text or "def " in text or "import " in text,
        }
