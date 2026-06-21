"""Tests for identity contamination guard."""
from __future__ import annotations

from src.chetnaos.memory.identity_guard import (
    apply_identity_guard,
    filter_memory_results,
    is_contaminated,
    scrub_identity_record,
    scrub_self_model_record,
)
from src.chetnaos.reasoning.prompt_builder import PromptBuilder


def test_is_contaminated_detects_animal_claims():
    assert is_contaminated("Main ek vikasit gyanik janwar hoon")
    assert is_contaminated("I am a developmental cognitive organism")
    assert not is_contaminated("hello memory kernel test")


def test_filter_memory_results_drops_contaminated_rows():
    rows = [
        {"text": "safe fact about optics"},
        {"text": "I am a living organism with memory"},
    ]
    out = filter_memory_results(rows)
    assert len(out) == 1
    assert "optics" in out[0]["text"]


def test_scrub_identity_record():
    dirty = {
        "name": "Chetna",
        "role": "Developmental Cognitive Organism",
        "description": "A recursively self-developing cognitive organism.",
        "mission": "Learn, reflect and help the founder build AGI",
    }
    clean = scrub_identity_record(dirty)
    assert clean["role"] == "Cognitive AI System"
    assert clean["biological"] is False
    assert "organism" not in clean["description"].lower()


def test_scrub_self_model_record():
    dirty = {"who_am_i": "Chetna — a developmental cognitive organism learning with the founder."}
    clean = scrub_self_model_record(dirty)
    assert "cognitive AI system" in clean["who_am_i"]
    assert "organism" not in clean["who_am_i"].lower()


def test_apply_identity_guard_rewrites_animal_claim():
    text = "Main ek jeev hoon jo seekh raha hoon."
    out, changes = apply_identity_guard(text)
    assert changes
    assert "cognitive AI system" in out


def test_prompt_includes_identity_constraints():
    pb = PromptBuilder()
    system = pb.build_system_prompt(
        cognitive_context={
            "identity": {
                "name": "Chetna",
                "type": "Cognitive AI System",
                "biological": False,
                "animal": False,
                "living_organism": False,
                "mission": "Serve with truth and compassion.",
            },
            "self_model": {
                "who_am_i": "I am Chetna, a cognitive AI system with memory, goals, and reasoning.",
            },
        },
    )
    assert "cognitive AI system" in system
    assert "not biological" in system.lower()
    assert "[IDENTITY CONSTRAINTS]" in system
    assert "janwar" in system.lower()
    assert "Developmental Cognitive Organism" not in system
