"""Tests for ExecutiveController — Phase 3a."""
from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ.setdefault("LIGHT_MODE", "true")
os.environ.setdefault("EMBEDDINGS_ENABLED", "false")


class TestExecutivePipelineOrder(unittest.TestCase):
    def test_pipeline_matches_cognitive_cycle_contract(self):
        from src.chetnaos.cognition.executive import EXECUTION_PIPELINE, ExecutiveController
        from src.chetnaos.orchestrator.state_machine import CycleStage

        exec_ctrl = ExecutiveController()
        names = exec_ctrl.pipeline_order()
        self.assertEqual(len(names), 25)
        self.assertEqual(names[0], CycleStage.EXIST.value)
        self.assertEqual(names[-1], CycleStage.WAKE.value)
        self.assertIn(CycleStage.ACT.value, names)
        self.assertIn(CycleStage.REALITY_CHECK.value, names)
        self.assertNotIn(CycleStage.DECIDE.value, names)
        self.assertEqual(names, [s.value for s in EXECUTION_PIPELINE])


class TestExecutiveLlmPolicy(unittest.TestCase):
    def test_act_always_uses_llm(self):
        from src.chetnaos.cognition.executive import ExecutiveController
        from src.chetnaos.orchestrator.state_machine import CycleStage

        ex = ExecutiveController()
        ex.update_context(complexity="simple")
        self.assertTrue(ex.use_llm(CycleStage.ACT))

    def test_imagine_plan_complex_only(self):
        from src.chetnaos.cognition.executive import ExecutiveController
        from src.chetnaos.orchestrator.state_machine import CycleStage

        ex = ExecutiveController()
        ex.update_context(complexity="simple")
        self.assertFalse(ex.use_llm(CycleStage.IMAGINE))
        self.assertFalse(ex.use_llm(CycleStage.PLAN))

        ex.update_context(complexity="complex")
        self.assertTrue(ex.use_llm(CycleStage.IMAGINE))
        self.assertTrue(ex.use_llm(CycleStage.PLAN))

    def test_llm_router_for_returns_none_when_gated(self):
        from src.chetnaos.cognition.executive import ExecutiveController
        from src.chetnaos.orchestrator.state_machine import CycleStage

        ex = ExecutiveController()
        router = MagicMock()
        ex.update_context(complexity="simple")
        self.assertIsNone(ex.llm_router_for(CycleStage.IMAGINE, router))
        self.assertIs(ex.llm_router_for(CycleStage.ACT, router), router)


class TestExecutiveSkipAndInterrupt(unittest.TestCase):
    def test_decide_stage_not_in_pipeline(self):
        from src.chetnaos.cognition.executive import ExecutiveController
        from src.chetnaos.orchestrator.state_machine import CycleStage

        ex = ExecutiveController()
        self.assertFalse(ex.should_run(CycleStage.DECIDE))
        self.assertIsNotNone(ex.skip_reason(CycleStage.DECIDE))

    def test_disabled_stage_skipped(self):
        from src.chetnaos.cognition.executive import ExecutiveController
        from src.chetnaos.orchestrator.state_machine import CycleStage

        ex = ExecutiveController()
        ex.disable_stage(CycleStage.PLAY)
        self.assertFalse(ex.should_run(CycleStage.PLAY))
        self.assertIn("stage_disabled", ex.skip_reason(CycleStage.PLAY))

    def test_interrupt_skips_stages(self):
        from src.chetnaos.cognition.executive import ExecutiveController
        from src.chetnaos.orchestrator.state_machine import CycleStage

        ex = ExecutiveController()
        ex.request_interrupt("homeostasis_critical")
        self.assertFalse(ex.should_run(CycleStage.REFLECT))
        self.assertEqual(ex.skip_reason(CycleStage.REFLECT), "homeostasis_critical")


class TestExecutiveSleepPolicy(unittest.TestCase):
    def test_sleep_consolidation_delegates_to_sleep_manager(self):
        from src.chetnaos.cognition.executive import ExecutiveController
        from src.chetnaos.orchestrator.sleep_manager import SleepManager

        sleeper = SleepManager(sleep_every=5)
        ex = ExecutiveController(sleep_manager=sleeper)
        self.assertFalse(ex.should_sleep_consolidation(1))
        self.assertTrue(ex.should_sleep_consolidation(5))
        ex.mark_slept(5)
        self.assertEqual(ex.cycles_until_sleep(6), 4)


class TestExecutiveHealth(unittest.TestCase):
    def test_health_state_fields(self):
        from src.chetnaos.cognition.executive import ExecutiveController

        ex = ExecutiveController()
        ex.reset_cycle_context(mode="chat", user_input="hi")
        ex.update_context(complexity="simple", cycle_n=1)
        health = ex.health_state()
        self.assertFalse(health["interrupted"])
        self.assertEqual(health["pipeline_length"], 25)
        self.assertIn("ACT", health["llm_required_stages"])
        self.assertEqual(health["context_snapshot"]["mode"], "chat")


class TestExecutiveIntegration(unittest.TestCase):
    def test_cognitive_cycle_has_executive(self):
        from src.chetnaos.orchestrator.cognitive_cycle import CognitiveCycle

        cycle = CognitiveCycle()
        self.assertIsNotNone(cycle.executive)
        self.assertIs(cycle.executive.sleep_manager, cycle.sleeper)

    def test_executive_policy_helpers(self):
        from src.chetnaos.cognition.executive import ExecutiveController

        ex = ExecutiveController()
        self.assertTrue(ex.should_refine_purpose("good"))
        self.assertFalse(ex.should_refine_purpose("fair"))
        self.assertTrue(ex.should_add_workspace_artifact("x" * 151))
        self.assertFalse(ex.should_add_workspace_artifact("short"))
        self.assertTrue(ex.should_poor_quality_followup("poor"))
        self.assertEqual(ex.self_question_answer("good"), "yes")
        self.assertEqual(ex.self_question_answer("poor"), "needs_improvement")


if __name__ == "__main__":
    unittest.main()
