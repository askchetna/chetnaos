"""
JSON validation with backup on corruption.

Purpose: Validate memory JSON files without destroying invalid data.
Inputs:  file path, pydantic schema class
Outputs: validated data or ValidationResult with backup path
Dependencies: schemas, pathlib
"""
from __future__ import annotations

import json
import logging
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Type, TypeVar

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

BACKUP_DIR = Path(__file__).resolve().parents[3] / "memory" / ".validation_backups"


@dataclass
class ValidationResult:
    ok: bool
    data: Any | None
    error: str | None = None
    backup_path: str | None = None
    source_path: str | None = None


def _backup_file(source: Path) -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    dest = BACKUP_DIR / f"{source.stem}_{stamp}{source.suffix}"
    shutil.copy2(source, dest)
    logger.warning("Backed up corrupt file %s -> %s", source, dest)
    return dest


def load_json_file(path: Path) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def validate_json_file(
    path: Path,
    model: Type[T],
    *,
    list_root: bool = False,
    dict_root: bool = False,
) -> ValidationResult:
    """
    Load and validate a JSON file.

    On validation failure: backup original, do NOT overwrite, return ok=False.
    """
    source = path.resolve()
    if not source.exists():
        return ValidationResult(ok=False, data=None, error="file not found", source_path=str(source))

    try:
        raw = load_json_file(source)
    except json.JSONDecodeError as exc:
        backup = _backup_file(source)
        return ValidationResult(
            ok=False,
            data=None,
            error=f"JSON decode error: {exc}",
            backup_path=str(backup),
            source_path=str(source),
        )

    try:
        if list_root and hasattr(model, "from_list"):
            validated = model.from_list(raw)  # type: ignore[attr-defined]
        elif dict_root and hasattr(model, "from_dict"):
            validated = model.from_dict(raw)  # type: ignore[attr-defined]
        else:
            validated = model.model_validate(raw)
        return ValidationResult(ok=True, data=validated, source_path=str(source))
    except ValidationError as exc:
        backup = _backup_file(source)
        return ValidationResult(
            ok=False,
            data=None,
            error=str(exc),
            backup_path=str(backup),
            source_path=str(source),
        )


def validate_identity(path: Path) -> ValidationResult:
    from .schemas import IdentitySchema
    return validate_json_file(path, IdentitySchema)


def validate_beliefs(path: Path) -> ValidationResult:
    from .schemas import BeliefsSchema
    return validate_json_file(path, BeliefsSchema, list_root=True)


def validate_purpose(path: Path) -> ValidationResult:
    from .schemas import PurposeSchema
    return validate_json_file(path, PurposeSchema)


def validate_skills(path: Path) -> ValidationResult:
    from .schemas import SkillsSchema
    return validate_json_file(path, SkillsSchema, dict_root=True)


def validate_workspace(path: Path) -> ValidationResult:
    from .schemas import WorkspaceSchema
    return validate_json_file(path, WorkspaceSchema)


def validate_habits(path: Path) -> ValidationResult:
    from .schemas import HabitsSchema
    return validate_json_file(path, HabitsSchema, dict_root=True)


def validate_development(path: Path) -> ValidationResult:
    from .schemas import DevelopmentSchema
    return validate_json_file(path, DevelopmentSchema)


def validate_relationships(path: Path) -> ValidationResult:
    from .schemas import RelationshipsSchema
    return validate_json_file(path, RelationshipsSchema, dict_root=True)


def validate_training_goals(path: Path) -> ValidationResult:
    from .schemas import TrainingGoalsSchema
    return validate_json_file(path, TrainingGoalsSchema, list_root=True)


def validate_contradictions(path: Path) -> ValidationResult:
    from .schemas import ContradictionsSchema
    return validate_json_file(path, ContradictionsSchema, list_root=True)


def validate_mem_hierarchy(path: Path) -> ValidationResult:
    from .schemas import MemHierarchySchema
    return validate_json_file(path, MemHierarchySchema)


# All JSON files under memory/ with schema coverage
VALIDATORS = {
    "identity.json": validate_identity,
    "beliefs.json": validate_beliefs,
    "purpose.json": validate_purpose,
    "skills.json": validate_skills,
    "workspace_state.json": validate_workspace,
    "habits.json": validate_habits,
    "development.json": validate_development,
    "relationships.json": validate_relationships,
    "training_goals.json": validate_training_goals,
    "contradictions.json": validate_contradictions,
    "mem_hierarchy.json": validate_mem_hierarchy,
}


def validate_all_memory_json(memory_dir: Path | None = None) -> dict[str, ValidationResult]:
    """Run all validators against the memory/ directory."""
    root = memory_dir or Path(__file__).resolve().parents[3] / "memory"
    results: dict[str, ValidationResult] = {}
    for filename, validator in VALIDATORS.items():
        path = root / filename
        if path.exists():
            results[filename] = validator(path)
        else:
            results[filename] = ValidationResult(
                ok=False, data=None, error="file not found", source_path=str(path)
            )
    return results
