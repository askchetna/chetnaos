"""Phase 8 Experiment 1 gate — 10-cycle smoke (full 100 via experiment_1_soak.py)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    print("=== Phase 8 Experiment 1 Gate (10-cycle smoke) ===\n")
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "experiment_1_soak.py"), "--cycles", "10"],
        cwd=str(ROOT),
    )
    if proc.returncode != 0:
        print("FAIL")
        return 1
    report = ROOT / "reports" / "experiment_1_soak.json"
    if not report.exists():
        print("FAIL: report not written")
        return 1
    print("PASS: experiment_1_soak.json written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
