"""Tests for cognitive integration wiring — reasoning context."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class TestReasoningIntegration(unittest.TestCase):
    def test_reasoning_includes_working_memory_and_goal(self):
        from src.chetnaos.reasoning.reasoning import Reasoning

        reasoning = Reasoning()
        mock_llm = MagicMock()
        mock_llm.chat.return_value = "integrated reply"

        cognitive_context = {
            "working_memory": [{"input": "prior task", "_attention_weight": 0.9}],
            "active_goal": {
                "text": "Ship feature",
                "goal_type": "USER",
                "goal_priority": 90.0,
            },
            "beliefs": [{"text": "Truth matters", "confidence": 0.95}],
            "self_model": {"self_confidence": 0.7, "known_limits": ["memory"]},
            "curiosity": {"novelty_score": 0.6, "exploration_goals": [{"type": "explore", "target": "domain"}]},
            "emotion": {"valence": 0.5, "arousal": 0.3, "interaction_tone": "neutral_clear"},
        }

        result = reasoning.reason(
            "hello",
            [],
            "Direct response",
            mock_llm,
            cognitive_context=cognitive_context,
        )

        self.assertEqual(result["response"], "integrated reply")
        self.assertTrue(result["used_working_memory"])
        self.assertTrue(result["used_active_goal"])
        self.assertTrue(result["used_beliefs"])
        self.assertTrue(result["used_cognitive_organs"])

        system_content = mock_llm.chat.call_args[0][0][0]["content"]
        self.assertIn("[WORKING MEMORY]", system_content)
        self.assertIn("[ACTIVE GOAL]", system_content)
        self.assertIn("[BELIEF CONFIDENCE]", system_content)
        self.assertIn("[SELF MODEL]", system_content)

    def test_build_reasoning_context_wires_working_memory_recall(self):
        from src.chetnaos.cycle.cognitive_cycle import CognitiveCycle

        cycle = CognitiveCycle()
        cycle.working_memory.push({"input": "context item"}, attention_weight=0.8)
        ctx = cycle._build_reasoning_context(
            abstr={"domain": "general"},
            att={"priority": "NORMAL", "emotional": False},
            purpose_r={"statement": "test purpose"},
            mode="chat",
        )
        self.assertGreater(len(ctx["working_memory"]), 0)
        self.assertIn("input", ctx["working_memory"][0])


if __name__ == "__main__":
    unittest.main()
