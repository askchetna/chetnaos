"""
ChetnaOS Stability & Soak Testing — measure only, no architecture changes.

Runs N cognitive cycles with stub LLM, periodically validates:
  - JSON memory integrity
  - chat persistence (ConversationStore)
  - workspace session restore
  - contradiction resolution pipeline
  - belief confidence bounds / duplicate detection

Usage:
  python scripts/soak_runner.py --cycles 100 --out reports/soak_100.json
  python scripts/soak_runner.py --cycles 500 --out reports/soak_500.json
  python scripts/soak_gate.py
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ.setdefault("LIGHT_MODE", "true")
os.environ.setdefault("EMBEDDINGS_ENABLED", "false")

MEMORY_DIR = ROOT / "memory"
CHECKPOINT_EVERY = 10
CONFIDENCE_MIN = 0.05
CONFIDENCE_MAX = 0.99
MAX_BELIEF_GROWTH = 25  # allow some learning; fail on explosion

PROMPTS = [
    "Explain working memory in one sentence.",
    "What is your active goal?",
    "Summarize your beliefs about truth.",
    "How confident are you in your last answer?",
    "What did you learn from the previous cycle?",
    "Describe contradiction handling briefly.",
    "What is AGI?",
    "How does memory influence your answers?",
]

JSON_WATCH_FILES = [
    "beliefs.json",
    "contradictions.json",
    "contradiction_resolutions.json",
    "conversations.json",
    "ui_session.json",
    "workspace_state.json",
    "belief_revision_state.json",
    "development.json",
    "identity.json",
    "mem_hierarchy.json",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable_hash(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def scan_json_integrity() -> list[dict]:
    """Return corruption events (invalid JSON or unreadable files)."""
    events: list[dict] = []
    if not MEMORY_DIR.exists():
        return events
    for path in sorted(MEMORY_DIR.glob("*.json")):
        try:
            with open(path, encoding="utf-8") as f:
                json.load(f)
        except Exception as exc:
            events.append({
                "file": path.name,
                "error": str(exc),
                "timestamp": _now(),
            })
    return events


def belief_stats(beliefs: list) -> dict:
    texts = [b.get("text", "").strip().lower() for b in beliefs if b.get("text")]
    confidences = [float(b.get("confidence", 0.5)) for b in beliefs]
    dupes = len(texts) - len(set(texts))
    out_of_bounds = [
        c for c in confidences if c < CONFIDENCE_MIN or c > CONFIDENCE_MAX
    ]
    return {
        "count": len(beliefs),
        "duplicate_texts": dupes,
        "average_confidence": round(
            sum(confidences) / max(len(confidences), 1), 4
        ),
        "min_confidence": round(min(confidences), 4) if confidences else None,
        "max_confidence": round(max(confidences), 4) if confidences else None,
        "out_of_bounds_count": len(out_of_bounds),
        "belief_hash": _stable_hash(beliefs),
    }


def memory_item_counts(cycle) -> dict:
    wm = cycle.working_memory.health()
    mem_stats: dict = {}
    try:
        from src.chetnaos.memory.store import get_memory_store
        store = get_memory_store()
        mem_stats = store.statistics() if store else {}
    except Exception:
        mem_stats = {}
    conv_count = 0
    try:
        from backend.conversation_store import get_conversation_store
        for c in get_conversation_store().list_conversations():
            conv_count += c.get("message_count", 0)
    except Exception:
        pass
    return {
        "belief_count": len(cycle.beliefs.get_all()),
        "working_memory_count": wm.get("count", 0),
        "contradiction_count": cycle.contradictions.count(),
        "resolution_history_count": len(cycle.contradictions.resolution_history()),
        "vector_store": mem_stats,
        "conversation_messages": conv_count,
    }


def verify_chat_persistence(conv_id: str | None, cycle_num: int) -> dict:
    from backend.conversation_store import get_conversation_store

    store = get_conversation_store()
    probe = f"soak probe cycle {cycle_num}"
    if conv_id is None:
        conv = store.create(title=f"soak-{cycle_num}")
        conv_id = conv["id"]
    store.append_message(conv_id, "user", probe)
    store.append_message(conv_id, "assistant", f"stub reply {cycle_num}")
    reloaded = store.get(conv_id)
    ok = reloaded is not None and any(
        m.get("content") == probe for m in reloaded.get("messages", [])
    )
    return {"ok": ok, "conversation_id": conv_id, "message_count": len(reloaded.get("messages", [])) if reloaded else 0}


def verify_workspace_restore(cycle) -> dict:
    from backend import workspace_store
    from backend.runtime import get_runtime

    snap = get_runtime().session_snapshot() if get_runtime() else {}
    workspace_store.save_session({
        "active_conversation_id": snap.get("active_conversation_id"),
        "active_goal": snap.get("active_goal") or cycle.goal_manager.active_goal(),
        "current_thought": snap.get("current_thought") or {},
        "working_memory": cycle.working_memory.recall(),
    })
    loaded = workspace_store.load_session()
    ok = (
        loaded.get("active_goal") is not None
        and isinstance(loaded.get("working_memory"), list)
        and loaded.get("current_thought") is not None
    )
    return {
        "ok": ok,
        "has_goal": bool(loaded.get("active_goal")),
        "wm_items": len(loaded.get("working_memory") or []),
    }


def verify_contradiction_resolution(cycle) -> dict:
    """Ensure scan + resolve pipeline runs without error."""
    beliefs = cycle.beliefs.get_all()
    tracker = cycle.contradictions
    before = tracker.count()
    try:
        tracker.scan(beliefs)
        resolutions = tracker.resolve(beliefs)
        for res in resolutions:
            cycle.beliefs.weaken_by_text(
                res.get("weaker_belief", ""),
                delta=-0.01,
                reason="soak_checkpoint",
            )
        ok = True
        err = None
    except Exception as exc:
        ok = False
        err = str(exc)
        resolutions = []
    return {
        "ok": ok,
        "error": err,
        "contradictions_before": before,
        "contradictions_after": tracker.count(),
        "resolutions_this_checkpoint": len(resolutions),
        "resolution_file_exists": (MEMORY_DIR / "contradiction_resolutions.json").exists(),
    }


def seed_conflicting_beliefs(cycle) -> None:
    """Deterministic antonym pair for contradiction detection during soak."""
    cycle.beliefs._beliefs = list(cycle.beliefs.get_all())
    texts = {b.get("text", "").lower() for b in cycle.beliefs._beliefs}
    pairs = [
        ("Soak validation is easy to verify", 0.40),
        ("Soak validation is hard to verify", 0.80),
    ]
    for text, conf in pairs:
        if text.lower() not in texts:
            cycle.beliefs.add(text, confidence=conf, source="soak_test")


def evaluate_pass_criteria(summary: dict) -> dict:
    return {
        "zero_crashes": summary["failed_cycles"] == 0,
        "zero_corrupted_memory": summary["memory_corruption_events"] == 0,
        "contradiction_resolution_working": summary["contradiction_checkpoints_failed"] == 0,
        "chat_persistence_working": summary["chat_restore_failures"] == 0,
        "workspace_restore_working": summary["workspace_restore_failures"] == 0,
        "confidence_bounded": summary["confidence_out_of_bounds_total"] == 0,
        "no_belief_explosion": summary["belief_count_max"] <= summary["belief_count_initial"] + MAX_BELIEF_GROWTH,
    }


def run_soak(n_cycles: int, out_path: Path) -> int:
    from src.chetnaos.cycle.cognitive_cycle import CognitiveCycle
    from backend.runtime import reset_runtime, get_runtime

    reset_runtime()
    cycle = CognitiveCycle()
    seed_conflicting_beliefs(cycle)

    initial_beliefs = len(cycle.beliefs.get_all())
    runtime_errors: list[dict] = []
    corruption_events: list[dict] = []
    cycle_snapshots: list[dict] = []
    chat_failures = 0
    workspace_failures = 0
    contradiction_failures = 0
    restored_sessions = 0
    failed_cycles = 0
    confidence_oob_total = 0
    belief_count_max = initial_beliefs
    conv_id: str | None = None

    print(f"=== ChetnaOS Soak Test: {n_cycles} cycles ===\n")
    t0 = time.perf_counter()

    with patch.object(cycle.llm, "chat", return_value="[soak stub reply]"):
        with patch.object(cycle.reflection, "reflect", return_value={
            "quality": "good",
            "dharma_score": 80,
            "cycle_score": 75,
        }):
            for i in range(n_cycles):
                cycle_num = i + 1
                prompt = PROMPTS[i % len(PROMPTS)] + f" (soak {cycle_num}/{n_cycles})"
                try:
                    result = cycle.run(prompt, mode="chat")
                    ok = True
                    err = None
                except Exception as exc:
                    ok = False
                    err = traceback.format_exc()
                    failed_cycles += 1
                    runtime_errors.append({
                        "cycle": cycle_num,
                        "error": str(exc),
                        "traceback": err,
                        "timestamp": _now(),
                    })
                    result = {}

                bstats = belief_stats(cycle.beliefs.get_all())
                belief_count_max = max(belief_count_max, bstats["count"])
                confidence_oob_total += bstats["out_of_bounds_count"]
                counts = memory_item_counts(cycle)

                snap = {
                    "cycle": cycle_num,
                    "ok": ok,
                    "timestamp": _now(),
                    "belief": bstats,
                    "memory": counts,
                    "quality": result.get("quality") if ok else None,
                    "contradiction_resolutions": len(result.get("contradiction_resolutions", [])) if ok else 0,
                }
                cycle_snapshots.append(snap)

                if cycle_num % CHECKPOINT_EVERY == 0 or cycle_num == n_cycles:
                    corruption_events.extend(scan_json_integrity())

                    chat_r = verify_chat_persistence(conv_id, cycle_num)
                    conv_id = chat_r["conversation_id"]
                    if not chat_r["ok"]:
                        chat_failures += 1

                    ws_r = verify_workspace_restore(cycle)
                    if ws_r["ok"]:
                        restored_sessions += 1
                    else:
                        workspace_failures += 1

                    contra_r = verify_contradiction_resolution(cycle)
                    if not contra_r["ok"]:
                        contradiction_failures += 1

                if cycle_num % 25 == 0 or cycle_num == 1:
                    print(
                        f"  cycle {cycle_num:4d}/{n_cycles} | beliefs={bstats['count']} "
                        f"avg_conf={bstats['average_confidence']} "
                        f"contradictions={counts['contradiction_count']} "
                        f"wm={counts['working_memory_count']} "
                        f"failures={failed_cycles}"
                    )

    elapsed = time.perf_counter() - t0
    final_corruption = scan_json_integrity()
    corruption_events.extend(final_corruption)
    # dedupe corruption by file+error
    seen = set()
    unique_corruption: list[dict] = []
    for e in corruption_events:
        key = (e["file"], e.get("error"))
        if key not in seen:
            seen.add(key)
            unique_corruption.append(e)

    belief_counts = [s["belief"]["count"] for s in cycle_snapshots]
    confidences = [s["belief"]["average_confidence"] for s in cycle_snapshots]
    contradiction_counts = [s["memory"]["contradiction_count"] for s in cycle_snapshots]

    memory_growth_report = {
        "initial": cycle_snapshots[0]["memory"] if cycle_snapshots else {},
        "final": cycle_snapshots[-1]["memory"] if cycle_snapshots else {},
        "belief_count_series": belief_counts,
        "working_memory_series": [s["memory"]["working_memory_count"] for s in cycle_snapshots],
        "conversation_messages_final": cycle_snapshots[-1]["memory"]["conversation_messages"] if cycle_snapshots else 0,
    }

    belief_stability_report = {
        "initial_count": initial_beliefs,
        "final_count": belief_counts[-1] if belief_counts else initial_beliefs,
        "max_count": belief_count_max,
        "max_allowed": initial_beliefs + MAX_BELIEF_GROWTH,
        "initial_hash": cycle_snapshots[0]["belief"]["belief_hash"] if cycle_snapshots else None,
        "final_hash": cycle_snapshots[-1]["belief"]["belief_hash"] if cycle_snapshots else None,
        "average_confidence_series": confidences,
        "duplicate_texts_final": cycle_snapshots[-1]["belief"]["duplicate_texts"] if cycle_snapshots else 0,
        "confidence_out_of_bounds_total": confidence_oob_total,
    }

    contradiction_stability_report = {
        "count_series": contradiction_counts,
        "initial_count": contradiction_counts[0] if contradiction_counts else 0,
        "final_count": contradiction_counts[-1] if contradiction_counts else 0,
        "resolution_history_final": cycle.contradictions.resolution_history()[:5],
        "checkpoints_failed": contradiction_failures,
        "resolution_file_exists": (MEMORY_DIR / "contradiction_resolutions.json").exists(),
    }

    workspace_persistence_report = {
        "checkpoints_run": n_cycles // CHECKPOINT_EVERY + (1 if n_cycles % CHECKPOINT_EVERY else 0),
        "restored_sessions_ok": restored_sessions,
        "restore_failures": workspace_failures,
        "final_session": {},
    }
    try:
        from backend import workspace_store
        workspace_persistence_report["final_session"] = {
            "has_goal": bool(workspace_store.load_session().get("active_goal")),
            "wm_items": len(workspace_store.load_session().get("working_memory") or []),
            "active_conversation_id": workspace_store.load_session().get("active_conversation_id"),
        }
    except Exception as exc:
        workspace_persistence_report["final_session_error"] = str(exc)

    summary = {
        "cycle_count": n_cycles,
        "completed_cycles": n_cycles - failed_cycles,
        "memory_item_count_final": cycle_snapshots[-1]["memory"] if cycle_snapshots else {},
        "belief_count_initial": initial_beliefs,
        "belief_count_max": belief_count_max,
        "contradiction_count_final": contradiction_counts[-1] if contradiction_counts else 0,
        "average_confidence_final": confidences[-1] if confidences else None,
        "failed_cycles": failed_cycles,
        "runtime_errors": len(runtime_errors),
        "memory_corruption_events": len(unique_corruption),
        "restored_sessions": restored_sessions,
        "chat_restore_failures": chat_failures,
        "workspace_restore_failures": workspace_failures,
        "contradiction_checkpoints_failed": contradiction_failures,
        "confidence_out_of_bounds_total": confidence_oob_total,
        "elapsed_seconds": round(elapsed, 2),
    }

    pass_criteria = evaluate_pass_criteria(summary)
    passed = all(pass_criteria.values())

    report = {
        "soak": {
            "phase": "stability_soak",
            "cycles": n_cycles,
            "started_at": cycle_snapshots[0]["timestamp"] if cycle_snapshots else _now(),
            "finished_at": _now(),
            "elapsed_seconds": summary["elapsed_seconds"],
            "architecture_modified": False,
        },
        "metrics": summary,
        "memory_growth_report": memory_growth_report,
        "belief_stability_report": belief_stability_report,
        "contradiction_stability_report": contradiction_stability_report,
        "workspace_persistence_report": workspace_persistence_report,
        "chat_persistence": {
            "checkpoints": n_cycles // CHECKPOINT_EVERY,
            "restore_failures": chat_failures,
            "final_conversation_id": conv_id,
        },
        "pass_criteria": pass_criteria,
        "passed": passed,
        "runtime_error_log": runtime_errors[:20],
        "memory_corruption_log": unique_corruption,
        "cycle_samples": cycle_snapshots[:: max(1, n_cycles // 20)][:21],
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"\n--- Pass criteria ---")
    for k, v in pass_criteria.items():
        print(f"  {'PASS' if v else 'FAIL'}: {k}")
    print(f"\nOverall: {'PASS' if passed else 'FAIL'}")
    print(f"Report: {out_path}")
    print(f"Elapsed: {elapsed:.1f}s")
    return 0 if passed else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="ChetnaOS stability soak test")
    parser.add_argument("--cycles", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    return run_soak(args.cycles, args.out)


if __name__ == "__main__":
    sys.exit(main())
