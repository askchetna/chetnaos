"""Tests for response_goal_engine."""
from __future__ import annotations

from src.chetnaos.discourse.response_goal_engine import GOALS, infer_response_goal


def test_debug_intent_maps_debug_goal():
    assert infer_response_goal("debug") == "debug"


def test_decision_maps_decide():
    assert infer_response_goal("decision") == "decide"


def test_comparison_maps_compare():
    assert infer_response_goal("comparison") == "compare"


def test_planning_maps_plan():
    assert infer_response_goal("planning") == "plan"


def test_confusion_dialogue_clarify():
    assert infer_response_goal("learning", dialogue_act="confusion") == "clarify"


def test_frustration_pragmatic_comfort():
    prag = {"hidden_intent": "frustration"}
    assert infer_response_goal("emotional", pragmatics=prag) == "comfort"


def test_urgency_pragmatic_decide():
    prag = {"hidden_intent": "urgency"}
    assert infer_response_goal("casual", pragmatics=prag) == "decide"


def test_teach_mode():
    prag = {"teach_mode": True}
    assert infer_response_goal("learning", pragmatics=prag) == "teach"


def test_all_goals_defined():
    assert len(GOALS) >= 9
