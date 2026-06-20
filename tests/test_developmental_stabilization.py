"""Integration tests for developmental stabilization pass."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.chetnaos.cycle.cognitive_cycle import CognitiveCycle
from src.chetnaos.organism.beliefs import Beliefs
from src.chetnaos.organism.development import Development
from src.chetnaos.organism.identity import Identity
from src.chetnaos.organism.memory import Memory
from src.chetnaos.organism.reflection_organ import ReflectionOrgan
from src.chetnaos.organism.relationship import Relationship
from src.chetnaos.organism.sleep import Sleep
from src.chetnaos.reasoning.prompt_builder import PromptBuilder


def _sample_experiences(tmp: Path, n: int = 6) -> None:
    exp_file = tmp / "memory" / "experiences.jsonl"
    exp_file.parent.mkdir(parents=True, exist_ok=True)
    with open(exp_file, "w", encoding="utf-8") as f:
        for i in range(n):
            domain = "research" if i % 2 == 0 else "general"
            f.write(json.dumps({
                "timestamp": "2026-06-19T12:00:00",
                "input": f"question {i}",
                "output": "Important key insight for testing sleep replay.",
                "domain": domain,
                "quality": "good",
            }) + "\n")


def test_sleep_phase5_completes_without_error(tmp_path):
    """Phase 5 must not raise NameError; all side effects run."""
    _sample_experiences(tmp_path)
    sleep_log = tmp_path / "memory" / "sleep_log.jsonl"

    with patch("src.chetnaos.organism.sleep.EXP_FILE", str(tmp_path / "memory" / "experiences.jsonl")), \
         patch("src.chetnaos.organism.sleep.SLEEP_LOG", str(sleep_log)):
        beliefs = Beliefs()
        beliefs._beliefs = [
            {"id": "b1", "text": "anchor belief", "confidence": 0.85, "source": "test"},
            {"id": "b2", "text": "weak belief", "confidence": 0.2, "source": "test"},
        ]
        beliefs._save = MagicMock()
        dev = Development()
        dev._data["recurring_themes"] = []
        rel = Relationship()
        before_strength = rel.founder_strength()
        ident = Identity()
        ro = ReflectionOrgan()
        ro._items = []

        result = Sleep().consolidate(
            beliefs,
            Memory(),
            100,
            identity_module=ident,
            relationship_module=rel,
            development_module=dev,
            reflection_organ=ro,
        )

    assert result["slept"] is True
    assert result["dream_replayed"] >= 1
    assert rel.founder_strength() >= before_strength
    assert len(dev._data.get("recurring_themes", [])) >= 1
    assert len(ro.recent(3)) >= 1
    assert sleep_log.exists()


def test_dashboard_developmental_block_keys():
    cycle = CognitiveCycle()
    snap = cycle.dashboard_snapshot()
    assert "developmental" in snap
    dev = snap["developmental"]
    for key in (
        "curiosity", "consistency", "reflection", "identity_stability",
        "relationship_strength", "development_stage", "current_focus",
        "recurring_themes", "recent_lessons", "self_model", "what_changed",
    ):
        assert key in dev
    for key in ("relationships", "episodic", "temporal_continuity", "reflections", "values"):
        assert key in snap
    assert "identity" in snap


def test_prompt_contains_developmental_blocks():
    cycle = CognitiveCycle()
    ctx = cycle._build_reasoning_context(
        abstr={"domain": "general"},
        att={"priority": "NORMAL", "emotional": False},
        purpose_r={"statement": "build AGI"},
        mode="chat",
    )
    system = PromptBuilder().format_cognitive_context(ctx)

    assert "[IDENTITY]" in system
    assert "[FOUNDER RELATIONSHIP]" in system
    assert "Mangla Prasad Pandey" in system
    assert "[VALUES]" in system
    assert "truth" in system
    assert "growth" in system
    assert "[SELF MODEL]" in system
    assert "Who I am:" in system
    assert "Becoming:" in system
    assert "[RECENT REFLECTION]" in system or ctx.get("recent_reflection") == ""
    assert "[EPISODIC HIGHLIGHT]" in system
    assert "[TEMPORAL CONTINUITY]" in system
    assert "[MEMORY GROUNDING]" in system
    assert "cycle #" not in system.lower()
    assert "cycle_count" not in system.lower()


def test_prompt_grounding_blocks_present_for_leakage_questions():
    ctx = {
        "identity": {"name": "Chetna", "role": "Developmental Cognitive Organism",
                      "mission": "Learn and help founder", "development_stage": "Early Organism"},
        "founder_relationship": {"name": "Mangla Prasad Pandey", "role": "Founder",
                                 "relationship": "Creator", "trust": "high", "attachment": "primary"},
        "self_model": {"who_am_i": "Chetna — organism", "becoming": "reflective partner",
                       "current_focus": "AGI architecture"},
        "temporal": {"today_summary": "research discussion", "yesterday_summary": "UI work",
                     "recent_changes": ["2026-06-18 — good response in research"]},
        "episodic_highlight": {"yesterday_summary": "UI stabilization", "recent_lesson": "consistency improved"},
        "recent_reflection": "I have repeatedly focused on AGI architecture.",
        "recurring_themes": ["research", "general"],
        "values": {"priorities": [{"name": "truth"}, {"name": "growth"},
                                  {"name": "compassion"}, {"name": "alignment"}]},
    }
    system = PromptBuilder().format_cognitive_context(ctx)
    assert "[MEMORY GROUNDING]" in system
    assert "never a place" in system.lower()
    assert "[RECURRING THEMES]" in system
    assert "research" in system


def test_build_reasoning_context_includes_values_and_highlight():
    cycle = CognitiveCycle()
    ctx = cycle._build_reasoning_context(
        abstr={"domain": "research"},
        att={"priority": "NORMAL"},
        purpose_r={"statement": "x"},
        mode="chat",
    )
    assert "values" in ctx
    assert "episodic_highlight" in ctx
    assert "recurring_themes" in ctx
    assert ctx["episodic_highlight"].get("yesterday_summary") is not None
