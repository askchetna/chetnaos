"""Tests for audience_model."""
from __future__ import annotations

from src.chetnaos.discourse.audience_model import audience_hints, infer_audience


def test_programmer_from_code_intent():
    assert infer_audience("fix this python function", intent="coding") == "programmer"


def test_programmer_from_keywords():
    assert infer_audience("how do I refactor this API endpoint") == "programmer"


def test_founder_from_startup():
    assert infer_audience("What's our go-to-market strategy for launch?") == "founder"


def test_researcher_from_paper():
    assert infer_audience("design a benchmark experiment for AGI") == "researcher"


def test_beginner_from_eli5():
    assert infer_audience("explain embeddings in simple terms for beginners") == "beginner"


def test_expert_from_technical():
    assert infer_audience("give me the technical architecture deep dive") == "expert"


def test_casual_default():
    assert infer_audience("hello there", intent="casual") == "casual user"


def test_founder_hints_strategy():
    hints = audience_hints("founder")
    assert hints.get("focus") == "strategy_tradeoffs_execution"


def test_programmer_code_first_hint():
    assert audience_hints("programmer")["code_first"] is True
