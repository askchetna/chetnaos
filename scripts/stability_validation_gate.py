"""Stability validation gate — runtime evidence for audit PARTIAL/FAIL items."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PRIORITY_TESTS = [
    ("P1 Contradiction Resolution", "test_deterministic_contradiction_resolution_pipeline"),
    ("P1 Contradiction Resolution", "test_full_cycle_dashboard_exposes_resolution"),
    ("P2 Chat Persistence", "test_message_refresh_simulation_restore"),
    ("P3 Follow-up Context", "test_agi_follow_up_passes_prior_messages"),
    ("P4 Memory Influence", "test_seeded_memory_in_prompt_and_influence"),
    ("P4 Memory Influence", "test_cycle_memory_influence_non_empty_when_recalled"),
    ("P5 Honesty Guard", "test_forbidden_self_claims_replaced"),
    ("P5 Honesty Guard", "test_api_exposes_honesty_guard_changes"),
    ("P6 Workspace Restore", "test_workspace_survives_restart_simulation"),
]

PRIORITY_GROUPS = [
    "P1 Contradiction Resolution",
    "P2 Chat Persistence",
    "P3 Follow-up Context",
    "P4 Memory Influence",
    "P5 Honesty Guard",
    "P6 Workspace Restore",
]


def _test_status(output: str, method: str) -> str:
    pattern = rf"{re.escape(method)}.*?\.\.\. (ok|FAIL|ERROR)"
    m = re.search(pattern, output, re.DOTALL)
    if not m:
        return "UNKNOWN"
    return "PASS" if m.group(1) == "ok" else "FAIL"


def main() -> int:
    print("=== ChetnaOS Stability Validation Gate ===\n")
    cmd = [sys.executable, str(ROOT / "tests" / "test_stability_validation.py"), "-v"]
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    combined = proc.stdout + proc.stderr
    print(combined)

    by_test = {method: _test_status(combined, method) for _, method in PRIORITY_TESTS}
    by_priority: dict[str, str] = {}
    for label in PRIORITY_GROUPS:
        methods = [m for l, m in PRIORITY_TESTS if l == label]
        statuses = [by_test.get(m, "UNKNOWN") for m in methods]
        by_priority[label] = "PASS" if all(s == "PASS" for s in statuses) else "FAIL"

    failed = sum(1 for s in by_priority.values() if s != "PASS")
    for label in PRIORITY_GROUPS:
        print(f"{by_priority[label]}: {label}")

    report = {
        "gate": "stability_validation",
        "tests": by_test,
        "priorities": by_priority,
        "passed": len(PRIORITY_GROUPS) - failed,
        "total": len(PRIORITY_GROUPS),
        "exit_code": proc.returncode,
    }
    out = ROOT / "reports" / "stability_validation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nReport: {out}")
    print(f"=== Result: {report['passed']}/{report['total']} priorities passed ===")
    return 1 if failed or proc.returncode != 0 else 0


if __name__ == "__main__":
    sys.exit(main())
