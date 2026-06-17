"""
PHASE 8F.1 — Live memory recall validation.

Runs a real cognitive cycle, captures /api/memory_trace, writes
reports/memory_recall_trace.json
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
OUT = ROOT / "reports" / "memory_recall_trace.json"
BASE = os.getenv("CHETNAOS_BASE", "http://127.0.0.1:8000")

MARKER = "MEMORY_RECALL_TRACE_MARKER_OMEGA"
QUERY = f"What do you know about {MARKER} and launching ChetnaOS publicly?"


def _get(path: str) -> dict:
    with urllib.request.urlopen(f"{BASE}{path}", timeout=120) as r:
        return json.loads(r.read())


def _post(path: str, body: dict) -> dict:
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{BASE}{path}", data=data,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())


def run_direct_cycle() -> dict:
    """Fresh in-process cycle (guarantees updated recall code)."""
    os.environ.setdefault("LIGHT_MODE", "true")
    os.environ.setdefault("EMBEDDINGS_ENABLED", "false")

    from backend.runtime import reset_runtime
    from src.chetnaos.memory.store import get_memory_store

    reset_runtime()
    store = get_memory_store()
    store.upsert(
        f"Q: recall validation\nA: {MARKER} — ChetnaOS public launch revenue AGI consulting",
        meta={"category": "long_term_memory"},
    )

    from backend.runtime import get_runtime
    rt = get_runtime()
    result = rt.process(QUERY, mode="chat")
    trace = getattr(rt._cycle, "_last_memory_trace", {})
    return {
        "mode": "direct",
        "query": QUERY,
        "marker": MARKER,
        "recalled_count": trace.get("memories_selected", []),
        "memory_influence": result.get("reasoning_integration", {}).get("memory_influence", []),
        "trace": trace,
        "db_statistics": store.statistics(),
    }


def run_api_cycle() -> dict:
    """Live server path via HTTP."""
    health = _get("/health")
    chat = _post("/api/chat", {"text": QUERY})
    trace_resp = _get("/api/memory_trace")
    dash = _get("/api/dashboard")
    return {
        "mode": "api",
        "health": health,
        "query": QUERY,
        "chat_memory_influence": chat.get("meta", {}).get("reasoning_integration", {}).get(
            "memory_influence", []
        ),
        "api_memory_trace": trace_resp,
        "dashboard_memory_trace": dash.get("memory_trace", {}),
        "dashboard_memory_influence": dash.get("memory_influence", []),
    }


def main() -> int:
    report = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "phase": "8F.1",
        "root_cause_hypothesis": (
            "LIGHT_MODE disables embeddings; MemoryDB.search() returned [] "
            "before sparse fallback; 858 mem.db rows have null embeddings"
        ),
        "direct": {},
        "api": {},
        "passed": False,
        "pass_reason": "",
    }

    try:
        report["direct"] = run_direct_cycle()
    except Exception as e:
        report["direct"] = {"error": str(e)}

    try:
        report["api"] = run_api_cycle()
    except Exception as e:
        report["api"] = {"error": str(e)}

    d = report.get("direct", {})
    trace = d.get("trace") or {}
    influence = d.get("memory_influence") or []
    selected = trace.get("memories_selected") or []

    passed = (
        len(selected) >= 1
        and len(influence) >= 1
        and trace.get("reached_reasoning")
        and trace.get("memory_influence_nonempty")
    )
    report["passed"] = passed
    if passed:
        report["pass_reason"] = (
            f"Recalled {len(selected)} memories via {trace.get('search_method')}; "
            f"memory_influence count={len(influence)}"
        )
    else:
        report["pass_reason"] = (
            f"selected={len(selected)} influence={len(influence)} "
            f"failure_point={trace.get('failure_point')}"
        )

    report["recall_path"] = {
        "user_input": QUERY,
        "recall_query": trace.get("query"),
        "search_method": trace.get("search_method"),
        "memories_found": len(trace.get("memories_found") or []),
        "memories_selected": len(selected),
        "memories_injected": len(trace.get("memories_injected") or []),
        "memories_used": len(influence),
        "failure_point": trace.get("failure_point"),
    }

    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Report: {OUT}")
    print(json.dumps(report["recall_path"], indent=2))
    print(f"OVERALL: {'PASS' if passed else 'FAIL'} — {report['pass_reason']}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
