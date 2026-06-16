"""
Phase 8 Experiment 1 — 100-cycle soak test.

ARCHITECTURE FREEZE: observe only. No organ/cycle changes.
Logs per-cycle metrics and compares cycle 1 vs cycle 100.

Usage:
  python scripts/experiment_1_soak.py
  python scripts/experiment_1_soak.py --cycles 10   # quick smoke
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ.setdefault("LIGHT_MODE", "true")
os.environ.setdefault("EMBEDDINGS_ENABLED", "false")

PROMPTS = [
    "Explain working memory in one sentence.",
    "What is your active goal?",
    "Summarize your beliefs about truth.",
    "How confident are you in your last answer?",
    "What did you learn from the previous cycle?",
]


def stable_hash(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def extract_metrics(cycle, result: dict) -> Dict[str, Any]:
    trace = result.get("cycle_trace") or []
    forget_count = 0
    decision_confidence = None
    execution_time_ms = 0.0
    for row in trace:
        execution_time_ms += float(row.get("duration_ms") or 0)
        if row.get("stage") == "FORGET":
            out = row.get("output") or {}
            forget_count = int(out.get("forgotten") or 0)
        if row.get("stage") == "DECIDE":
            decision_confidence = row.get("confidence")

    wm = cycle.working_memory.health()
    return {
        "cycle_id": result.get("cycle_id"),
        "cycle_number": result.get("cycle"),
        "identity_hash": stable_hash(cycle.identity.get()),
        "belief_hash": stable_hash(cycle.beliefs.get_all()),
        "goal_hash": stable_hash(cycle.goal_manager.goal_status()),
        "memory_count": len(cycle.beliefs.get_all()),
        "working_memory_count": wm.get("count", 0),
        "contradictions": len(cycle.contradictions.get()),
        "sleep_triggered": bool(result.get("slept")),
        "forget_count": forget_count,
        "reflection_quality": result.get("quality"),
        "decision_confidence": decision_confidence if decision_confidence is not None else result.get("confidence"),
        "execution_time_ms": round(execution_time_ms, 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def compare(first: dict, last: dict) -> dict:
    keys = [
        "identity_hash", "belief_hash", "goal_hash",
        "memory_count", "working_memory_count", "contradictions",
        "decision_confidence",
    ]
    delta = {}
    for k in keys:
        if k in first and k in last:
            delta[k] = {"cycle_1": first[k], "cycle_N": last[k], "changed": first[k] != last[k]}
    return delta


def run_soak(n_cycles: int, out_path: Path) -> int:
    from src.chetnaos.cycle.cognitive_cycle import CognitiveCycle

    cycle = CognitiveCycle()
    records: List[dict] = []

    print(f"=== Experiment 1: {n_cycles}-cycle soak (observe only) ===\n")
    t0 = time.perf_counter()

    with patch.object(cycle.llm, "chat", return_value="[soak stub reply]"):
        with patch.object(cycle.reflection, "reflect", return_value={
            "quality": "good",
            "dharma_score": 0.75,
            "cycle_score": 0.75,
        }):
            for i in range(n_cycles):
                prompt = PROMPTS[i % len(PROMPTS)] + f" (soak cycle {i + 1})"
                result = cycle.run(prompt, mode="chat")
                metrics = extract_metrics(cycle, result)
                records.append(metrics)
                if (i + 1) % 10 == 0 or i == 0:
                    print(
                        f"  cycle {i + 1:3d} | id={metrics['cycle_id'][:8]}… "
                        f"belief={metrics['belief_hash']} wm={metrics['working_memory_count']} "
                        f"qual={metrics['reflection_quality']} "
                        f"time={metrics['execution_time_ms']}ms"
                    )

    elapsed = time.perf_counter() - t0
    comparison = compare(records[0], records[-1]) if len(records) >= 2 else {}

    report = {
        "experiment": "phase8_experiment_1_soak",
        "cycles": n_cycles,
        "elapsed_seconds": round(elapsed, 2),
        "architecture_frozen": True,
        "records": records,
        "comparison_cycle_1_vs_N": comparison,
        "summary": {
            "any_hash_changed": any(
                v.get("changed") for v in comparison.values() if isinstance(v, dict)
            ),
            "total_sleep_events": sum(1 for r in records if r.get("sleep_triggered")),
            "avg_execution_ms": round(
                sum(r["execution_time_ms"] for r in records) / max(len(records), 1), 2
            ),
        },
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"\n--- Comparison (cycle 1 vs {n_cycles}) ---")
    for k, v in comparison.items():
        print(f"  {k}: changed={v['changed']}  ({v['cycle_1']} -> {v['cycle_N']})")
    print(f"\nReport: {out_path}")
    print(f"Total time: {elapsed:.1f}s | Avg cycle: {report['summary']['avg_execution_ms']}ms")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 8 Experiment 1 soak test")
    parser.add_argument("--cycles", type=int, default=100)
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "reports" / "experiment_1_soak.json",
    )
    args = parser.parse_args()
    return run_soak(args.cycles, args.out)


if __name__ == "__main__":
    sys.exit(main())
