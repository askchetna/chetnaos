"""Tests for v3 PromptBuilder single assembly path."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class TestPromptBuilder(unittest.TestCase):
    def test_build_system_prompt_includes_source_ranks(self):
        from src.chetnaos.reasoning.prompt_builder import PromptBuilder

        pb = PromptBuilder()
        system = pb.build_system_prompt(
            founder_context="\n[FOUNDER CONTEXT]\nMission test",
            recalled=[{"text": "LTM fact"}],
            cognitive_context={
                "working_memory": [{"input": "wm item", "_attention_weight": 0.8}],
            },
            plan="Step by step",
        )
        self.assertIn("[source trust=0.95]", system)
        self.assertIn("[FOUNDER CONTEXT]", system)
        self.assertIn("[source trust=0.65]", system)
        self.assertIn("LTM fact", system)
        self.assertIn("[WORKING MEMORY]", system)
        self.assertIn("[source trust=0.80]", system)
        self.assertIn("Approach to use: Step by step", system)

    def test_reasoning_uses_prompt_builder(self):
        from src.chetnaos.reasoning.reasoning import Reasoning
        from unittest.mock import MagicMock

        reasoning = Reasoning()
        mock_llm = MagicMock()
        mock_llm.chat.return_value = "ok"
        reasoning.reason("hi", [], "", mock_llm, founder_context="\n[FOUNDER CONTEXT]\nx")
        system = mock_llm.chat.call_args[0][0][0]["content"]
        self.assertIn("[source trust=0.95]", system)


if __name__ == "__main__":
    unittest.main()
