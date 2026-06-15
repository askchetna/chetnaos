"""Runtime Validation Gate — prove integrated wiring (12 tests)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    print("=== Runtime Validation Gate ===\n")
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tests" / "test_runtime_validation.py")],
        cwd=str(ROOT),
    )
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
