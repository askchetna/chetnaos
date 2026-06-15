"""
Memory subsystem health reporting.

Purpose: Report vector store + JSON validation status for the locked memory architecture.
Inputs:  memory/ directory, MemoryStore singleton
Outputs: health dict suitable for dashboards and gate tests
Dependencies: validation, store, locked
"""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from .locked import LOCKED, MEMORY_ARCHITECTURE_VERSION
from .store import get_memory_store
from .validation import VALIDATORS, validate_all_memory_json

logger = logging.getLogger(__name__)

MEMORY_DIR = Path(__file__).resolve().parents[3] / "memory"


def report(memory_dir: Path | None = None) -> Dict[str, Any]:
    """Full memory health snapshot."""
    root = memory_dir or MEMORY_DIR
    json_results = validate_all_memory_json(root)

    json_files = {}
    valid_count = 0
    for filename, result in json_results.items():
        json_files[filename] = {
            "ok": result.ok,
            "error": result.error,
            "backup_path": result.backup_path,
            "exists": (root / filename).exists(),
        }
        if result.ok:
            valid_count += 1

    vector_stats: Dict[str, Any] = {}
    vector_ok = False
    try:
        store = get_memory_store()
        vector_stats = store.statistics()
        vector_ok = True
    except Exception as exc:
        logger.error("MemoryStore statistics failed: %s", exc)
        vector_stats = {"error": str(exc)}

    total_json = len(VALIDATORS)
    overall = (
        LOCKED
        and vector_ok
        and valid_count == total_json
    )

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "architecture_version": MEMORY_ARCHITECTURE_VERSION,
        "locked": LOCKED,
        "overall_healthy": overall,
        "vector_store": {
            "ok": vector_ok,
            "statistics": vector_stats,
        },
        "json_validation": {
            "total_schemas": total_json,
            "valid_count": valid_count,
            "invalid_count": total_json - valid_count,
            "files": json_files,
        },
        "coverage": list(VALIDATORS.keys()),
    }
