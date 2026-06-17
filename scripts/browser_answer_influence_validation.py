"""
Focused browser validation — Answer Influence panel (UI proof required).

Steps:
  1. Send chat message via browser UI
  2. Open dashboard
  3. Verify memory influence count (DOM)
  4. Verify belief influence count (DOM)
  5. Verify panel populated (not empty-state)
  6. Capture API payloads for comparison
  7. Screenshot Answer Influence card

PASS requires browser UI evidence — API counts alone are insufficient.
"""
from __future__ import annotations

import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports" / "browser_validation"
BASE = "http://127.0.0.1:8000"
CHAT_MSG = "Answer Influence browser validation marker ALPHA-2026"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")


def api_get(path: str) -> dict:
    import urllib.request

    with urllib.request.urlopen(f"{BASE}{path}", timeout=180) as r:
        raw = r.read()
        return json.loads(raw) if raw else {}


def count_influence_rows(panel_text: str) -> tuple[int, int]:
    """Count Memory and Belief rows inside Answer Influence card text."""
    memory = len(re.findall(r"\bMemory\b", panel_text))
    belief = len(re.findall(r"Belief #\d+", panel_text))
    return memory, belief


def run() -> int:
    from playwright.sync_api import sync_playwright

    OUT.mkdir(parents=True, exist_ok=True)
    run_id = _now()
    shot_dir = OUT / run_id
    shot_dir.mkdir(parents=True, exist_ok=True)

    report: dict = {
        "run_id": run_id,
        "test": "answer_influence",
        "chat_message": CHAT_MSG,
        "api_payloads": {},
        "ui": {},
        "console_logs": [],
        "screenshots": {},
        "passed": False,
        "pass_reason": "",
    }

    def save():
        path = OUT / f"answer_influence_{run_id}.json"
        path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Report: {path}")

    try:
        api_get("/health")
    except Exception as e:
        print(f"FAIL: server not reachable at {BASE}: {e}")
        return 1

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        console_logs: list[dict] = []

        def on_console(msg):
            entry = {"type": msg.type, "text": msg.text}
            if "DASHBOARD influence" in msg.text:
                console_logs.append(entry)
                report["console_logs"].append(entry)

        page.on("console", on_console)

        # 1. Send chat message via browser UI
        page.goto(f"{BASE}/", wait_until="networkidle")
        page.wait_for_timeout(2000)
        page.fill("#msg", CHAT_MSG)
        page.click("#send")
        page.wait_for_timeout(15000)

        chat_shot = shot_dir / "01_after_chat.png"
        page.screenshot(path=str(chat_shot), full_page=True)
        report["screenshots"]["after_chat"] = str(chat_shot)
        report["ui"]["chat_sent"] = page.locator(f"text={CHAT_MSG}").count() > 0

        # 2. Open dashboard
        page.goto(f"{BASE}/dashboard", wait_until="networkidle")
        page.wait_for_timeout(4000)

        # 6. API payloads (for evidence, not pass criteria)
        dash = api_get("/api/dashboard")
        ws = api_get("/api/workspace/session")
        report["api_payloads"]["GET /api/dashboard"] = {
            "memory_influence_count": len(dash.get("memory_influence") or []),
            "belief_influence_count": len(dash.get("belief_influence") or []),
            "memory_influence": dash.get("memory_influence") or [],
            "belief_influence": dash.get("belief_influence") or [],
        }
        report["api_payloads"]["GET /api/workspace/session"] = {
            "memory_influence_count": len(ws.get("memory_influence") or []),
            "belief_influence_count": len(ws.get("belief_influence") or []),
            "memory_influence": ws.get("memory_influence") or [],
            "belief_influence": ws.get("belief_influence") or [],
            "active_conversation_id": ws.get("active_conversation_id"),
        }

        # Locate Answer Influence card (filter by card header, not loose text match)
        card = page.locator(".card").filter(
            has=page.locator(".ch", has_text="Answer Influence")
        ).first
        if not card.count():
            report["pass_reason"] = "Answer Influence card not found in DOM"
            save()
            browser.close()
            print(json.dumps(report, indent=2))
            print(f"OVERALL: FAIL — {report['pass_reason']}")
            return 1

        panel_text = card.inner_text(timeout=5000)
        memory_ui, belief_ui = count_influence_rows(panel_text)
        no_data = "No influence logged yet" in panel_text

        report["ui"] = {
            **report.get("ui", {}),
            "panel_text": panel_text,
            "memory_influence_count": memory_ui,
            "belief_influence_count": belief_ui,
            "no_data_shown": no_data,
            "panel_populated": not no_data and (memory_ui + belief_ui) > 0,
        }

        # 7. Screenshot
        full_shot = shot_dir / "02_dashboard_full.png"
        page.screenshot(path=str(full_shot), full_page=True)
        report["screenshots"]["dashboard_full"] = str(full_shot)

        card_shot = shot_dir / "03_answer_influence_panel.png"
        card.screenshot(path=str(card_shot))
        report["screenshots"]["answer_influence_panel"] = str(card_shot)

        browser.close()

    api_mem = report["api_payloads"]["GET /api/dashboard"]["memory_influence_count"]
    api_bel = report["api_payloads"]["GET /api/dashboard"]["belief_influence_count"]
    ui_mem = report["ui"]["memory_influence_count"]
    ui_bel = report["ui"]["belief_influence_count"]
    populated = report["ui"]["panel_populated"]

    # PASS: UI must show influence rows; API-only is never sufficient
    ui_has_influence = ui_mem > 0 or ui_bel > 0
    report["passed"] = bool(populated and ui_has_influence and not report["ui"]["no_data_shown"])

    if report["passed"]:
        report["pass_reason"] = (
            f"UI shows {ui_mem} memory + {ui_bel} belief rows "
            f"(API: {api_mem} memory, {api_bel} belief)"
        )
    else:
        reasons = []
        if report["ui"]["no_data_shown"]:
            reasons.append("panel shows empty-state message")
        if not ui_has_influence:
            reasons.append(f"UI counts are memory={ui_mem}, belief={ui_bel}")
        if api_mem + api_bel > 0 and not ui_has_influence:
            reasons.append("API has data but UI does not — render bug")
        report["pass_reason"] = "; ".join(reasons) or "panel not populated"

    save()
    print("\n=== Answer Influence Browser Validation ===")
    print(f"Chat message: {CHAT_MSG}")
    print(f"UI memory influence count:  {ui_mem}")
    print(f"UI belief influence count:  {ui_bel}")
    print(f"Panel populated:            {populated}")
    print(f"API memory count:           {api_mem}")
    print(f"API belief count:           {api_bel}")
    print(f"\nAPI payload (/api/dashboard):")
    print(json.dumps(report["api_payloads"]["GET /api/dashboard"], indent=2))
    print(f"\nScreenshot: {report['screenshots']['answer_influence_panel']}")
    print(f"\nOVERALL: {'PASS' if report['passed'] else 'FAIL'} — {report['pass_reason']}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(run())
