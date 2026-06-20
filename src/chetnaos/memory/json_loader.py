"""
Validated JSON loader — single entry for organism persistence reads.

Purpose: Wire Pydantic validation into all JSON load paths.
Inputs:  file path, validator callable, default fallback
Outputs: validated Python dict/list structures
Dependencies: validation, schemas
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Callable, TypeVar

from .validation import ValidationResult

logger = logging.getLogger(__name__)

T = TypeVar("T")

MEMORY_ROOT = Path(__file__).resolve().parents[3] / "memory"


def memory_path(filename: str) -> Path:
    return MEMORY_ROOT / filename


def load_validated(
    path: Path | str,
    validator: Callable[[Path], ValidationResult],
    default: T,
    extractor: Callable[[Any], T],
) -> T:
    """
    Load JSON via validator. On failure: log, keep source file, return default.
    """
    source = Path(path)
    if not source.exists():
        return default

    result = validator(source)
    if result.ok and result.data is not None:
        try:
            return extractor(result.data)
        except Exception as exc:
            logger.error("Extractor failed for %s: %s", source, exc)
            return default

    logger.error(
        "JSON validation failed for %s: %s (backup=%s)",
        source,
        result.error,
        result.backup_path,
    )
    return default


def save_json(path: Path | str, data: Any) -> bool:
    """Persist JSON with logged errors (no silent pass)."""
    target = Path(path)
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as exc:
        logger.error("JSON save failed for %s: %s", target, exc)
        return False


# ── Typed loaders (used by organism modules) ─────────────────────────────────

def load_identity(default: dict) -> dict:
    from .validation import validate_identity
    return load_validated(
        memory_path("identity.json"), validate_identity, default,
        lambda m: m.model_dump(),
    )


def load_beliefs(default: list) -> list:
    from .validation import validate_beliefs
    return load_validated(
        memory_path("beliefs.json"), validate_beliefs, default,
        lambda m: [b.model_dump() for b in m.beliefs],
    )


def load_purpose(default: dict) -> dict:
    from .validation import validate_purpose
    return load_validated(
        memory_path("purpose.json"), validate_purpose, default,
        lambda m: m.model_dump(),
    )


def load_skills(default: dict) -> dict:
    from .validation import validate_skills
    return load_validated(
        memory_path("skills.json"), validate_skills, default,
        lambda m: {k: v.model_dump() for k, v in m.skills.items()},
    )


def load_workspace(default: dict) -> dict:
    from .validation import validate_workspace
    return load_validated(
        memory_path("workspace_state.json"), validate_workspace, default,
        lambda m: m.model_dump(),
    )


def load_habits(default: dict) -> dict:
    from .validation import validate_habits
    return load_validated(
        memory_path("habits.json"), validate_habits, default,
        lambda m: dict(m.patterns),
    )


def load_development(default: dict) -> dict:
    from .validation import validate_development
    return load_validated(
        memory_path("development.json"), validate_development, default,
        lambda m: m.model_dump(),
    )


def load_relationships(default: dict) -> dict:
    from .validation import validate_relationships
    return load_validated(
        memory_path("relationships.json"), validate_relationships, default,
        lambda m: {k: v.model_dump() for k, v in m.entities.items()},
    )


def load_training_goals(default: list) -> list:
    from .validation import validate_training_goals
    return load_validated(
        memory_path("training_goals.json"), validate_training_goals, default,
        lambda m: [g.model_dump() for g in m.goals],
    )


def load_contradictions(default: list) -> list:
    from .validation import validate_contradictions
    return load_validated(
        memory_path("contradictions.json"), validate_contradictions, default,
        lambda m: [c.model_dump() for c in m.items],
    )


def load_mem_hierarchy(default: dict) -> dict:
    from .validation import validate_mem_hierarchy
    return load_validated(
        memory_path("mem_hierarchy.json"), validate_mem_hierarchy, default,
        lambda m: m.model_dump(),
    )


def load_self_model(default: dict) -> dict:
    from .validation import validate_self_model
    return load_validated(
        memory_path("self_model.json"), validate_self_model, default,
        lambda m: m.model_dump(),
    )


def load_temporal_continuity(default: dict) -> dict:
    from .validation import validate_temporal_continuity
    return load_validated(
        memory_path("temporal_continuity.json"), validate_temporal_continuity, default,
        lambda m: m.model_dump(),
    )


def load_value_organ(default: dict) -> dict:
    from .validation import validate_value_organ
    return load_validated(
        memory_path("value_organ.json"), validate_value_organ, default,
        lambda m: m.model_dump(),
    )


def load_reflections(default: list) -> list:
    from .validation import validate_reflections
    return load_validated(
        memory_path("reflections.json"), validate_reflections, default,
        lambda m: [r.model_dump() for r in m.reflections],
    )
