"""Phase v3.1 gate — thin HTTP shell + v3 package scaffold + runtime validation."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CHECKS = [
    ("backend.app import", [sys.executable, "-c", "from backend.app import app; print(app.version)"]),
    ("v3 runtime shim", [sys.executable, "-c", "from src.chetnaos.runtime import ChetnaRuntime; print(ChetnaRuntime)"]),
    ("v3 cycle shim", [sys.executable, "-c", "from src.chetnaos.cycle import CognitiveCycle; print(CognitiveCycle)"]),
    ("v3 memory_kernel", [sys.executable, "-c", "from src.chetnaos.memory_kernel import MemoryStore; print(MemoryStore)"]),
    ("v3 tools", [sys.executable, "-c", "from src.chetnaos.tools import ToolRouter; print(ToolRouter)"]),
    ("runtime validation (12)", [sys.executable, str(ROOT / "tests" / "test_runtime_validation.py")]),
]


def main() -> int:
    print("=== ChetnaOS v3.1 Gate ===\n")
    failed = 0
    for name, cmd in CHECKS:
        print(f"--- {name} ---")
        proc = subprocess.run(cmd, cwd=str(ROOT))
        if proc.returncode != 0:
            failed += 1
            print(f"FAIL: {name}\n")
        else:
            print(f"PASS: {name}\n")
    print(f"=== Result: {len(CHECKS) - failed}/{len(CHECKS)} passed ===")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
