"""Phase 7 gate — post-7D2 validation."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CHECKS = [
    ("DECIDE in pipeline", [sys.executable, "-c",
     "from src.chetnaos.cognition.executive import EXECUTION_PIPELINE; "
     "from src.chetnaos.runtime.state_machine import CycleStage; "
     "vals=[s.value for s in EXECUTION_PIPELINE]; "
     "assert 'DECIDE' in vals; "
     "assert vals.index('REALITY_CHECK')<vals.index('DECIDE')<vals.index('EVALUATE'); "
     "print('DECIDE wired')"]),
    ("Canonical cycle import", [sys.executable, "-c",
     "from src.chetnaos.cycle.cognitive_cycle import CognitiveCycle; print(CognitiveCycle)"]),
    ("Canonical runtime import", [sys.executable, "-c",
     "from src.chetnaos.runtime.runtime import ChetnaRuntime; print(ChetnaRuntime)"]),
    ("No orchestrator shims (batch1)", [sys.executable, "-c",
     "import importlib.util\n"
     "try:\n"
     "    p = importlib.util.find_spec('src.chetnaos.orchestrator.cognitive_cycle')\n"
     "except ModuleNotFoundError:\n"
     "    p = None\n"
     "assert p is None or p.origin is None\n"
     "from pathlib import Path\n"
     "root = Path('src/chetnaos/orchestrator')\n"
     "gone = ['cognitive_cycle.py', 'runtime.py', 'state_machine.py', 'sleep_manager.py', 'llm_router.py']\n"
     "assert all(not (root / f).exists() for f in gone)\n"
     "print('batch1 shims removed')"]),
    ("Memory item schema", [sys.executable, str(ROOT / "tests" / "test_memory_item.py")]),
    ("reasoning integration", [sys.executable, str(ROOT / "tests" / "test_reasoning_integration.py")]),
    ("7D2 batch2 shims removed", [sys.executable, "-c",
     "from pathlib import Path; "
     "assert not Path('src/chetnaos/organism/reasoning.py').exists(); "
     "assert not Path('src/chetnaos/orchestrator/agent_tools.py').exists(); "
     "from src.chetnaos.reasoning.reasoning import Reasoning; print(Reasoning)"]),
    ("runtime validation (12)", [sys.executable, str(ROOT / "tests" / "test_runtime_validation.py")]),
]


def main() -> int:
    print("=== ChetnaOS Phase 7 Gate ===\n")
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
