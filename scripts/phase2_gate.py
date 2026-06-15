"""Phase 2 gate: Phase 1 baseline + unified memory tests."""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _run_phase1_gate() -> bool:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "phase1_gate.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode == 0


def main() -> int:
    print("=== Phase 2 Gate ===\n")

    print("--- Phase 1 baseline ---")
    phase1_ok = _run_phase1_gate()
    if not phase1_ok:
        print("FAIL: Phase 1 baseline regressed")
        return 1

    print("\n--- Phase 2 memory tests ---")
    loader = unittest.TestLoader()
    suite = loader.discover("tests", pattern="test_memory_store.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n--- Phase 2 Gate Summary ---")
    print(f"Phase 1 baseline:     {'PASS' if phase1_ok else 'FAIL'}")
    print(f"Memory store tests:   {'PASS' if result.wasSuccessful() else 'FAIL'}")
    print(f"Import test:          {'PASS' if result.wasSuccessful() else 'FAIL'}")
    print(f"Backward compat:      {'PASS' if result.wasSuccessful() else 'FAIL'}")
    print(f"JSON validation:      {'PASS' if result.wasSuccessful() else 'FAIL'}")
    print(f"Cognitive flow:       {'PASS' if result.wasSuccessful() else 'FAIL'}")

    try:
        import urllib.request
        with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=2) as resp:
            print(f"Live smoke (/health): {'PASS' if resp.status == 200 else 'FAIL'}")
    except Exception:
        print("Live smoke (/health): SKIP (no server on :8000)")

    return 0 if (phase1_ok and result.wasSuccessful()) else 1


if __name__ == "__main__":
    sys.exit(main())
