"""Tests for discourse layer v2."""
from __future__ import annotations

from src.chetnaos.discourse.answer_composer import DiscourseLayer
from src.chetnaos.discourse.context_awareness import (
    analyze_context,
    dedupe_against_history,
    detect_dialogue_act,
)
from src.chetnaos.discourse.intent_classifier import classify_intent
from src.chetnaos.discourse.quality_goals import QUALITY_GOALS
from src.chetnaos.discourse.response_planner import build_plan
from src.chetnaos.discourse.tone_engine import apply_tone
from src.chetnaos.discourse.verbosity_control import assess_verbosity
from src.chetnaos.reasoning.response_composer import ResponseComposer


def test_classify_identity():
    assert classify_intent("Who are you?") == "identity"


def test_classify_debug():
    assert classify_intent("Why are embeddings disabled?") == "debug"


def test_classify_emotional():
    assert classify_intent("Samjha nahi") == "emotional"


def test_quality_goals_defined():
    assert "clarity" in QUALITY_GOALS
    assert "trustworthiness" in QUALITY_GOALS


def test_dialogue_act_confusion():
    assert detect_dialogue_act("Samjha nahi", None) == "confusion"


def test_dialogue_act_follow_up():
    ctx = {"recent_messages": [{"role": "assistant", "content": "Here is the answer."}]}
    assert detect_dialogue_act("tell me more", ctx) == "follow_up"


def test_dialogue_act_agreement():
    assert detect_dialogue_act("thanks", None) == "agreement"


def test_identity_first_vs_repeat():
    raw = "I am ChetnaOS — a Developmental Cognitive Organism."
    first = DiscourseLayer.transform("Who are you?", raw)
    assert "memory, reasoning" in first

    ctx = {"recent_messages": [{"role": "assistant", "content": first}]}
    second = DiscourseLayer.transform("Who are you again?", raw, conversation_context=ctx)
    assert "Main Chetna" in second
    assert second.count("memory, reasoning") <= first.count("memory, reasoning")


def test_no_identity_on_follow_up_learning():
    ctx = {
        "recent_messages": [{
            "role": "assistant",
            "content": "Main Chetna hoon. Ek AI system jo memory, reasoning aur goals ki madad se kaam karta hai.",
        }],
    }
    raw = "Main Chetna hoon. Embeddings map text to vectors for search."
    out = DiscourseLayer.transform("What are embeddings?", raw, conversation_context=ctx)
    assert "Main Chetna hoon" not in out or out.count("Main Chetna") == 0


def test_emotional_samjha_nahi():
    out = DiscourseLayer.transform("Samjha nahi", "Long technical explanation here.")
    assert "Koi baat nahi" in out
    assert "simple" in out.lower()


def test_debug_structured():
    raw = (
        "Observation: Embeddings off.\n\n"
        "Cause: LIGHT_MODE true.\n\n"
        "Fix: Set EMBEDDINGS_ENABLED=true.\n\n"
        "Verification: Check /health."
    )
    out = DiscourseLayer.transform("Why are embeddings disabled?", raw)
    assert "Observation" in out or "Embeddings" in out
    assert "Fix" in out or "EMBEDDINGS" in out


def test_coding_code_first():
    raw = "```python\nprint('hi')\n```\n\nUse this to test output."
    plan = build_plan("coding", raw, verbosity="code_first")
    assert "code" in plan["sections"]
    assert "```" in plan["sections"]["code"]
    out = DiscourseLayer.transform("write python hello world", raw)
    assert "```" in out
    assert out.index("```") < 40


def test_dedupe_history():
    prior = ["Embeddings are disabled because LIGHT_MODE is true."]
    dup = "Embeddings are disabled because LIGHT_MODE is true. Set env var."
    out = dedupe_against_history(dup, prior, threshold=0.5)
    assert out != dup or "Set env" in out


def test_verbosity_short_casual():
    assert assess_verbosity("thanks", "casual", "agreement") == "short"


def test_frustration_pipeline():
    out = DiscourseLayer.transform("Ye sab mujhse nahi hoga", "Long complex answer.")
    assert "simple" in out.lower() or "samajh" in out.lower() or "heavy" in out.lower()


def test_planner_v3_schema_keys():
    plan = build_plan("learning", "A\n\nB\n\nC\n\nD\n\nE", verbosity="structured")
    assert "applications" in plan["schema"]
    assert "introduction" in build_plan("identity", "x")["schema"]


def test_tone_strips_organism():
    raw = "I am a developmental cognitive organism. cycle #12 confidence: 85%"
    out = apply_tone(raw, "identity")
    assert "organism" not in out.lower()
    assert "85%" not in out


def test_discourse_pipeline():
    raw = "cycle #3\nI am a cognitive organism."
    disc = DiscourseLayer.transform("hello", raw)
    final = ResponseComposer.compose(disc)
    assert "organism" not in final.lower()
