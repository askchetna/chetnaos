"""
ChetnaOS v3 — cognitive organs registry.

Each organ subpackage is a compat shim to the canonical implementation.
"""
from __future__ import annotations

ORGAN_IMPORTS = {
    "perception": ("src.chetnaos.organism.perception", "Perception"),
    "attention": ("src.chetnaos.organism.attention", "Attention"),
    "memory": ("src.chetnaos.organism.memory", "Memory"),
    "prediction": ("src.chetnaos.organism.abstraction", "Abstraction"),
    "imagination": ("src.chetnaos.organism.imagination", "Imagination"),
    "play": ("src.chetnaos.organism.play", "Play"),
    "planning": ("src.chetnaos.organism.planning", "Planning"),
    "decision": ("src.chetnaos.organism.decision", "Decision"),
    "embodiment": ("src.chetnaos.organism.embodiment", "Embodiment"),
    "world_model": ("src.chetnaos.organism.world_model", "WorldModel"),
    "experience": ("src.chetnaos.organism.experience", "Experience"),
    "reality": ("src.chetnaos.organism.reality", "RealityChecker"),
    "evaluation": ("src.chetnaos.organism.meta_cognition", "MetaCognition"),
    "failure_recovery": ("src.chetnaos.organism.homeostasis", "Homeostasis"),
    "reflection": ("src.chetnaos.organism.reflection", "Reflection"),
    "self_question": ("src.chetnaos.organism.workspace_state", "WorkspaceState"),
    "beliefs": ("src.chetnaos.organism.beliefs", "Beliefs"),
    "identity": ("src.chetnaos.organism.identity", "Identity"),
    "purpose": ("src.chetnaos.organism.purpose", "Purpose"),
    "habit": ("src.chetnaos.organism.habit", "Habit"),
    "sleep": ("src.chetnaos.organism.sleep", "Sleep"),
    "curiosity": ("src.chetnaos.cognition.curiosity", "CuriosityDrive"),
    "emotion": ("src.chetnaos.cognition.emotion", "EmotionalState"),
    "self_model": ("src.chetnaos.cognition.self_model", "SelfModel"),
    "goal_manager": ("src.chetnaos.cognition.goal_manager", "GoalManager"),
}

__all__ = ["ORGAN_IMPORTS"]
