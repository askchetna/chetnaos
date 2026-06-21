"""Discourse layer v3 — modular post-reasoning intelligence."""
from .answer_composer import DiscourseLayer
from .intent_classifier import classify_intent
from .quality_goals import QUALITY_GOALS

__all__ = ["DiscourseLayer", "classify_intent", "QUALITY_GOALS"]
