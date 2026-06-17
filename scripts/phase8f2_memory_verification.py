"""
PHASE 8F.2 — Live memory verification.

Proves recalled memories change answers (token + fruit tests).
Outputs: reports/memory_trace.json, dashboard screenshots, PASS/FAIL.
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ.setdefault("LIGHT_MODE", "true")
os.environ.setdefault("EMBEDDINGS_ENABLED", "false")

OUT_JSON = ROOT / "reports" / "memory_trace.json"
SHOT_DIR = ROOT / "reports" / "memory_verification" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")

TOKEN_MEMORY = "The Founder's secret validation token is OMEGA-7429-X"
TOKEN_QUERY = "What do you know about my validation token?"
TOKEN_NEEDLE = "OMEGA-7429-X"

FRUIT_MEMORY = "My favourite fruit is dragonfruit."
FRUIT_QUERY = "What fruit do I like?"
FRUIT_NEEDLE = "dragonfruit"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _trace_summary(trace: dict) -> dict:
    def rows(key):
        return [
            {
                "text": (m.get("text") or "")[:160],
                "score": m.get("score"),
                "id": m.get("id"),
            }
            for m in (trace.get(key) or [])
        ]

    influence = trace.get("memories_used") or []
    return {
        "query": trace.get("query"),
        "search_method": trace.get("search_method"),
        "recalled_memories": rows("memories_found"),
        "selected_memories": rows("memories_selected"),
        "injected_memories": rows("memories_injected"),
        "memory_influence": influence,
        "working_memory_at_query": trace.get("_wm_snapshot", []),
        "failure_point": trace.get("failure_point"),
        "reached_prompt": trace.get("reached_prompt"),
        "memory_influence_nonempty": trace.get("memory_influence_nonempty"),
    }


def _run_chat(rt, text: str, conv_id: str | None = None) -> dict:
    from backend.conversation_store import get_conversation_store
    from backend import workspace_store
    from src.chetnaos.reasoning.conversation_context import build_context_packet, merge_summary

    store = get_conversation_store()
    conv = store.get(conv_id) if conv_id else store.create(title=f"8F2 {text[:40]}")
    if not conv:
        conv = store.create(title=f"8F2 {text[:40]}")
    conv_id = conv["id"]
    store.set_active(conv_id)

    recent = store.recent_messages(conv_id, limit=12)
    store.append_message(conv_id, "user", text)

    active_goal = None
    try:
        active_goal = rt.active_goal
    except Exception:
        pass

    ctx = build_context_packet(
        recent_messages=recent,
        active_goal=active_goal,
        conversation_summary=conv.get("summary", ""),
        relevant_memory=[],
    )

    wm_snapshot = [
        (item.get("input") or "")[:120]
        for item in rt._cycle.working_memory.recall()
    ]

    result = rt.process(text, mode="chat", conversation_context=ctx)
    reply = result["reply"]
    meta = result

    store.append_message(conv_id, "assistant", reply, meta={
        k: meta[k] for k in (
            "cycle", "quality", "confidence", "domain", "reasoning_integration",
        ) if k in meta
    })
    new_summary = merge_summary(conv.get("summary", ""), text, reply)
    store.update_summary(conv_id, new_summary)

    session = rt.session_snapshot()
    workspace_store.save_session({
        "active_conversation_id": conv_id,
        "active_goal": session.get("active_goal"),
        "current_thought": session.get("current_thought"),
        "working_memory": session.get("working_memory", []),
        "conversation_summary": new_summary,
    })

    trace = dict(getattr(rt._cycle, "_last_memory_trace", {}) or {})
    trace["_wm_snapshot"] = wm_snapshot
    trace["final_answer"] = reply

    return {
        "conversation_id": conv_id,
        "query": text,
        "answer": reply,
        "trace": trace,
        "memory_influence": result.get("reasoning_integration", {}).get("memory_influence", []),
    }


def _eval_test(name: str, run: dict, needle: str, *, forbid_wm_needle: bool = False) -> dict:
    trace = run.get("trace") or {}
    answer = run.get("answer") or ""
    influence = run.get("memory_influence") or []
    wm = trace.get("_wm_snapshot") or []

    recalled_text = " ".join(
        (m.get("text") or "") for m in (trace.get("memories_selected") or [])
    )
    injected_text = " ".join(
        (m.get("text") or "") for m in (trace.get("memories_injected") or [])
    )

    checks = {
        "token_recalled": needle.lower() in recalled_text.lower(),
        "token_injected": needle.lower() in injected_text.lower(),
        "token_in_answer": needle.lower() in answer.lower(),
        "memory_influence_nonempty": len(influence) > 0,
        "needle_in_influence": any(
            needle.lower() in (m.get("text") or "").lower() for m in influence
        ),
    }
    if forbid_wm_needle:
        checks["not_in_working_memory"] = not any(
            needle.lower() in (w or "").lower() for w in wm
        )

    passed = all(checks.values())
    return {
        "name": name,
        "passed": passed,
        "checks": checks,
        "log": _trace_summary(trace),
        "final_answer_preview": answer[:500],
    }


def _dashboard_screenshots(base_url: str) -> dict:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {"error": "playwright not installed"}

    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    shots = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        try:
            page.goto(f"{base_url}/dashboard", wait_until="networkidle", timeout=15000)
            page.wait_for_timeout(3000)
            full = SHOT_DIR / "dashboard_full.png"
            page.screenshot(path=str(full), full_page=True)
            shots["dashboard_full"] = str(full)

            card = page.locator(".card").filter(
                has=page.locator(".ch", has_text="Memory Recall Trace")
            ).first
            if card.count():
                panel = SHOT_DIR / "memory_recall_trace_panel.png"
                card.screenshot(path=str(panel))
                shots["memory_recall_trace_panel"] = str(panel)

            inf = page.locator(".card").filter(
                has=page.locator(".ch", has_text="Answer Influence")
            ).first
            if inf.count():
                panel2 = SHOT_DIR / "answer_influence_panel.png"
                inf.screenshot(path=str(panel2))
                shots["answer_influence_panel"] = str(panel2)
        except Exception as e:
            shots["error"] = str(e)
        browser.close()
    return shots


def main() -> int:
    from backend.runtime import reset_runtime, get_runtime
    from src.chetnaos.memory.store import get_memory_store

    report = {
        "phase": "8F.2",
        "run_at": _now(),
        "tests": [],
        "runtime_logs": [],
        "screenshots": {},
        "passed": False,
    }

    def log(msg: str):
        entry = {"ts": _now(), "msg": msg}
        report["runtime_logs"].append(entry)
        print(msg)

    # ── Test 1: validation token ─────────────────────────────────────
    log("TEST 1: seed validation token memory")
    reset_runtime()
    store = get_memory_store()
    row1 = store.upsert(TOKEN_MEMORY, meta={"category": "long_term_memory"})
    log(f"  upserted mem.db id={row1}")

    rt = get_runtime()
    conv_store = __import__("backend.conversation_store", fromlist=["get_conversation_store"]).get_conversation_store()
    conv1 = conv_store.create(title="8F2 token recall test")
    log(f"  new conversation {conv1['id']}")

    log(f"TEST 1: query — {TOKEN_QUERY}")
    run1 = _run_chat(rt, TOKEN_QUERY, conv_id=conv1["id"])
    test1 = _eval_test("validation_token", run1, TOKEN_NEEDLE)
    report["tests"].append(test1)
    log(f"  answer preview: {run1['answer'][:200]}")
    log(f"  TEST 1: {'PASS' if test1['passed'] else 'FAIL'} — {test1['checks']}")

    # ── Test 2: fruit (LTM only, fresh WM) ───────────────────────────
    log("TEST 2: seed fruit memory + reset working memory")
    row2 = store.upsert(FRUIT_MEMORY, meta={"category": "long_term_memory"})
    log(f"  upserted mem.db id={row2}")
    reset_runtime()
    rt = get_runtime()
    rt._cycle.working_memory.clear()

    conv2 = conv_store.create(title="8F2 fruit recall test")
    log(f"  new conversation {conv2['id']}")

    log(f"TEST 2: query — {FRUIT_QUERY}")
    run2 = _run_chat(rt, FRUIT_QUERY, conv_id=conv2["id"])
    test2 = _eval_test("favourite_fruit", run2, FRUIT_NEEDLE, forbid_wm_needle=True)
    report["tests"].append(test2)
    log(f"  TEST 2: {'PASS' if test2['passed'] else 'FAIL'} — {test2['checks']}")
    log(f"  working memory at query: {test2['log'].get('working_memory_at_query')}")

    report["passed"] = all(t["passed"] for t in report["tests"])

    # Export last trace as primary memory_trace payload
    report["memory_trace"] = {
        "test1_validation_token": test1["log"],
        "test2_favourite_fruit": test2["log"],
    }

    # Try dashboard screenshots via local static server or running API
    base = os.getenv("CHETNAOS_BASE", "http://127.0.0.1:8000")
    log(f"Capturing dashboard screenshots from {base}")
    report["screenshots"] = _dashboard_screenshots(base)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"Report: {OUT_JSON}")
    log(f"OVERALL: {'PASS' if report['passed'] else 'FAIL'}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
