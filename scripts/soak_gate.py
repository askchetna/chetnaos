"""Stability soak gate — 100-cycle + 500-cycle with pass criteria."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RUNS = [
    ("100-cycle soak", 100, ROOT / "reports" / "soak_100.json"),
    ("500-cycle soak", 500, ROOT / "reports" / "soak_500.json"),
]


def _run_one(label: str, cycles: int, out: Path) -> bool:
    print(f"\n=== {label} ===\n")
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "soak_runner.py"),
            "--cycles", str(cycles),
            "--out", str(out),
        ],
        cwd=str(ROOT),
    )
    if proc.returncode != 0:
        print(f"FAIL: {label} (runner exit {proc.returncode})")
        return False
    if not out.exists():
        print(f"FAIL: {label} — report not written")
        return False
    data = json.loads(out.read_text(encoding="utf-8"))
    if not data.get("passed"):
        print(f"FAIL: {label} — pass criteria not met")
        print(json.dumps(data.get("pass_criteria", {}), indent=2))
        return False
    print(f"PASS: {label} -> {out}")
    return True


def main() -> int:
    print("=== ChetnaOS Stability & Soak Gate ===")
    failed = 0
    for label, cycles, out in RUNS:
        if not _run_one(label, cycles, out):
            failed += 1
    print(f"\n=== Result: {len(RUNS) - failed}/{len(RUNS)} passed ===")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
