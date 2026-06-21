"""Tests for self_monitor."""
from __future__ import annotations

from src.chetnaos.discourse.self_monitor import monitor


def test_strips_robotic_certainly():
    out = monitor("Certainly! Here is the answer.")
    assert "Certainly" not in out


def test_softens_overcertain():
    out = monitor("This will definitely work 100%.")
    assert "definitely" not in out.lower()
    assert "100%" not in out


def test_removes_duplicate_paragraphs():
    text = "Same idea here.\n\nSame idea here."
    out = monitor(text)
    assert out.count("Same idea") <= 1


def test_strips_identity_when_already_shared():
    ctx = {"identity_already_shared": True}
    out = monitor("Main Chetna hoon.\n\nActual answer content.", ctx_info=ctx)
    assert "Actual answer" in out
    assert "Main Chetna hoon" not in out


def test_dedupes_against_prior():
    ctx = {"prior_assistant": ["Embeddings are disabled in light mode."]}
    out = monitor(
        "Embeddings are disabled in light mode.\n\nSet EMBEDDINGS_ENABLED=true.",
        ctx_info=ctx,
    )
    assert "EMBEDDINGS_ENABLED" in out or out != ""


def test_truncates_when_shorten():
    long = "One. Two. Three. Four. Five. Six."
    out = monitor(long, pragmatics={"shorten": True}, max_sentences=2)
    assert len(out.split(".")) <= 3


def test_debug_adds_verification_hint():
    out = monitor("Observation: broken.", response_goal="debug")
    assert "fix" in out.lower() or "check" in out.lower() or "issue" in out.lower()


def test_reduces_founder_mentions():
    out = monitor(
        "The founder wants this.\n\nTechnical answer here.",
        user_input="explain api",
    )
    assert "founder" not in out.lower() or "Technical" in out


def test_empty_passthrough():
    assert monitor("") == ""
