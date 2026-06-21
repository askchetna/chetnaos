"""Tests for knowledge_planner."""
from __future__ import annotations

from src.chetnaos.discourse.knowledge_planner import (
    GOAL_SCHEMAS,
    build_knowledge_plan,
    schema_for_goal,
)


def test_explain_schema_has_applications():
    schema = schema_for_goal("explain", "learning")
    assert "applications" in schema
    assert schema.index("definition") < schema.index("summary")


def test_debug_schema_order():
    schema = schema_for_goal("debug", "debug")
    assert schema == ["observation", "cause", "fix", "verification"]


def test_plan_schema_objective():
    schema = schema_for_goal("plan", "planning")
    assert schema[0] == "objective"


def test_identity_schema():
    schema = schema_for_goal("explain", "identity")
    assert schema[0] == "introduction"


def test_build_plan_distributes_paragraphs():
    raw = "One.\n\nTwo.\n\nThree.\n\nFour.\n\nFive."
    plan = build_knowledge_plan(
        response_goal="explain", intent="learning", raw_response=raw, verbosity="structured",
    )
    assert len(plan["sections"]) >= 3


def test_build_plan_labeled_debug():
    raw = "Observation: Off.\nCause: Config.\nFix: Enable.\nVerification: /health."
    plan = build_knowledge_plan(
        response_goal="debug", intent="debug", raw_response=raw, verbosity="structured",
    )
    assert plan["sections"].get("observation") or plan["sections"].get("cause")


def test_coding_code_first():
    raw = "```python\nx=1\n```\n\nRun this."
    plan = build_knowledge_plan(
        response_goal="teach", intent="coding", raw_response=raw,
        verbosity="code_first", code_first=True,
    )
    assert "```" in plan["sections"].get("code", "")


def test_use_headers_debug():
    raw = "A\n\nB\n\nC\n\nD"
    plan = build_knowledge_plan(
        response_goal="debug", intent="debug", raw_response=raw, verbosity="structured",
    )
    assert plan["use_headers"] is True


def test_goal_schemas_cover_primary_goals():
    for g in ("explain", "debug", "decide", "plan", "compare"):
        assert g in GOAL_SCHEMAS
