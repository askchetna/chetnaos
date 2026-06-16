"""Phase v3.2 gate — prompt pipeline, organs, sleep order, dashboard wiring."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CHECKS = [
    ("PromptBuilder", [sys.executable, "-c",
     "from src.chetnaos.reasoning import PromptBuilder; "
     "p=PromptBuilder(); s=p.build_system_prompt(founder_context='[FOUNDER CONTEXT]\\ntest'); "
     "assert '[source trust=0.95]' in s; print('ok')"]),
    ("ContextBuilder", [sys.executable, "-c",
     "from src.chetnaos.reasoning import ContextBuilder; "
     "c=ContextBuilder().build(working_memory=[{'input':'x'}]); "
     "assert c['working_memory']; print('ok')"]),
    ("Organ shims (25)", [sys.executable, "-c",
     "from src.chetnaos.organs import ORGAN_IMPORTS; "
     "from importlib import import_module; "
     "[import_module(f'src.chetnaos.organs.{n}') for n in ORGAN_IMPORTS]; "
     "print(len(ORGAN_IMPORTS))"]),
    ("Sleep pipeline order", [sys.executable, "-c",
     "from src.chetnaos.cognition.executive import EXECUTION_PIPELINE; "
     "from src.chetnaos.runtime.state_machine import CycleStage; "
     "i=[s.value for s in EXECUTION_PIPELINE]; "
     "assert i.index('SLEEP')<i.index('CONSOLIDATE')<i.index('FORGET')<i.index('WAKE'); "
     "print('SLEEP->CONSOLIDATE->FORGET->WAKE')"]),
    ("reasoning integration", [sys.executable, str(ROOT / "tests" / "test_reasoning_integration.py")]),
    ("runtime validation (12)", [sys.executable, str(ROOT / "tests" / "test_runtime_validation.py")]),
    ("phase v3.1 gate", [sys.executable, str(ROOT / "scripts" / "phase_v3_1_gate.py")]),
]


def main() -> int:
    print("=== ChetnaOS v3.2 Gate ===\n")
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
