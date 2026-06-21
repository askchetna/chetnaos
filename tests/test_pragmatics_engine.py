"""Tests for pragmatics_engine."""
from __future__ import annotations

from src.chetnaos.discourse.pragmatics_engine import analyze_pragmatics, pragmatic_prefix


def test_frustration_hidden_intent():
    p = analyze_pragmatics("Ye sab mujhse nahi hoga")
    assert p["hidden_intent"] == "frustration"
    assert p["simplify"] is True
    assert p["acknowledge_difficulty"] is True


def test_confusion_simplify():
    p = analyze_pragmatics("Samjha nahi", {"dialogue_act": "confusion"})
    assert p["hidden_intent"] == "confusion"
    assert p["simplify"] is True


def test_agreement_shorten():
    p = analyze_pragmatics("Achha")
    assert p["hidden_intent"] == "agreement"
    assert p["shorten"] is True


def test_urgency():
    p = analyze_pragmatics("This is urgent fix now")
    assert p["hidden_intent"] == "urgency"
    assert p["shorten"] is True


def test_delegation():
    p = analyze_pragmatics("tum kar do yeh kaam")
    assert p["hidden_intent"] == "delegation"


def test_teach_mode():
    p = analyze_pragmatics("teach me step by step")
    assert p["teach_mode"] is True


def test_frustration_prefix():
    p = analyze_pragmatics("bahut mushkil hai")
    prefix = pragmatic_prefix(p)
    assert "simple" in prefix.lower() or "samajh" in prefix.lower()


def test_confusion_prefix():
    p = {"hidden_intent": "confusion"}
    assert "Koi baat nahi" in pragmatic_prefix(p)


def test_no_hidden_for_neutral():
    p = analyze_pragmatics("What is a hash map?")
    assert p["hidden_intent"] is None
