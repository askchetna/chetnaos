"""
Real browser UI validation — chat persistence + Answer Influence panel.

Captures screenshots and console logs to reports/browser_validation/
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports" / "browser_validation"
BASE = "http://127.0.0.1:8000"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")


def api_request(method: str, path: str, body: dict | None = None) -> dict:
    import urllib.request

    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"} if data else {}
    req = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=180) as r:
        raw = r.read()
        return json.loads(raw) if raw else {}


def api_get(path: str) -> dict:
    return api_request("GET", path)


def set_active_conversation(conv_id: str) -> None:
    api_request("POST", "/api/conversations/active", {"conversation_id": conv_id})


def seed_conversation(user_turns: int = 6) -> str:
    """Create conversation with user_turns chat rounds (= 2*user_turns messages)."""
    created = api_request("POST", "/api/conversations", {"title": "Browser validation thread"})
    conv_id = created["conversation"]["id"]

    for i in range(1, user_turns + 1):
        api_request(
            "POST",
            "/api/chat",
            {"text": f"Validation user message {i} for browser soak test", "conversation_id": conv_id},
        )
    set_active_conversation(conv_id)
    return conv_id


def ensure_conv_with_messages(min_messages: int = 10) -> str:
    listing = api_get("/api/conversations")
    for c in listing.get("conversations", []):
        if (c.get("message_count") or 0) >= min_messages:
            set_active_conversation(c["id"])
            return c["id"]
    return seed_conversation(6)


def count_visible_messages(page) -> int:
    return page.locator("#chat-messages .msg-row").count()


def active_sidebar_meta(page) -> str:
    loc = page.locator(".conv-item.active .conv-item-meta")
    if loc.count():
        return loc.first.inner_text()
    return ""


def wait_restore_complete(console_logs: list, timeout_s: float = 20) -> bool:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if any("RESTORE STEP 6 complete" in e.get("text", "") for e in console_logs):
            return True
        time.sleep(0.2)
    return False


def collect_restore_steps(console_logs: list) -> dict:
    steps = {}
    for entry in console_logs:
        text = entry.get("text", "")
        if "RESTORE STEP 1" in text:
            steps["1"] = text
        elif "RESTORE STEP 2" in text:
            steps["2"] = text
        elif "RESTORE STEP 3" in text:
            steps["3"] = text
        elif "RESTORE STEP 4 GET" in text:
            steps["4_get"] = text
        elif text.startswith("RESTORE STEP 4 "):
            steps["4"] = text
        elif "RESTORE STEP 5 renderConversationMessages" in text:
            steps["5_start"] = text
        elif "RESTORE STEP 5 rendered" in text:
            steps["5_done"] = text
        elif "RESTORE STEP 6 complete" in text:
            steps["6"] = text
    return steps


def run_validation() -> int:
    from playwright.sync_api import sync_playwright

    OUT.mkdir(parents=True, exist_ok=True)
    run_id = _now()
    shot_dir = OUT / run_id
    shot_dir.mkdir(parents=True, exist_ok=True)

    report = {
        "run_id": run_id,
        "base_url": BASE,
        "checks": {},
        "console_logs": [],
        "restore_steps_by_phase": {},
        "api_payloads": {},
        "screenshots": {},
        "passed": False,
    }

    def save_report():
        out_json = OUT / f"validation_{run_id}.json"
        out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Report: {out_json}")

    try:
        api_get("/health")
    except Exception as e:
        print(f"FAIL: server not reachable at {BASE}: {e}")
        return 1

    conv1_id = ensure_conv_with_messages(10)
    report["conv1_id"] = conv1_id
    conv1_api = api_get(f"/api/conversations/{conv1_id}")
    report["api_payloads"]["conv1_after_seed"] = {
        "message_count": len(conv1_api.get("conversation", {}).get("messages", [])),
        "title": conv1_api.get("conversation", {}).get("title"),
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 900})
        page = context.new_page()
        console_logs: list[dict] = []

        def on_console(msg):
            entry = {"type": msg.type, "text": msg.text}
            console_logs.append(entry)
            if "RESTORE STEP" in msg.text or "DASHBOARD influence" in msg.text:
                report["console_logs"].append(entry)

        page.on("console", on_console)

        page.goto(f"{BASE}/", wait_until="networkidle")
        page.wait_for_timeout(2500)
        wait_restore_complete(console_logs)
        report["restore_steps_by_phase"]["initial_load"] = collect_restore_steps(console_logs)

        visible_before = count_visible_messages(page)
        sidebar_before = active_sidebar_meta(page)
        p1 = shot_dir / "01_before_refresh.png"
        page.screenshot(path=str(p1), full_page=True)
        report["screenshots"]["before_refresh"] = str(p1)
        report["checks"]["before_refresh_visible"] = visible_before
        report["checks"]["before_refresh_sidebar"] = sidebar_before

        console_logs.clear()
        page.reload(wait_until="networkidle")
        page.wait_for_timeout(2500)
        wait_restore_complete(console_logs)
        report["restore_steps_by_phase"]["after_refresh"] = collect_restore_steps(console_logs)

        visible_after_refresh = count_visible_messages(page)
        sidebar_after_refresh = active_sidebar_meta(page)
        p2 = shot_dir / "02_after_refresh.png"
        page.screenshot(path=str(p2), full_page=True)
        report["screenshots"]["after_refresh"] = str(p2)
        report["checks"]["after_refresh_visible"] = visible_after_refresh
        report["checks"]["after_refresh_sidebar"] = sidebar_after_refresh
        report["checks"]["refresh_persisted"] = visible_after_refresh >= 10

        page.goto(f"{BASE}/dashboard", wait_until="networkidle")
        page.wait_for_timeout(3000)
        p3 = shot_dir / "03_dashboard.png"
        page.screenshot(path=str(p3), full_page=True)
        report["screenshots"]["dashboard"] = str(p3)

        dash_api = api_get("/api/dashboard")
        ws_api = api_get("/api/workspace/session")
        report["api_payloads"]["dashboard"] = {
            "memory_influence": dash_api.get("memory_influence") or [],
            "belief_influence": dash_api.get("belief_influence") or [],
        }
        report["api_payloads"]["workspace_session"] = {
            "memory_influence": ws_api.get("memory_influence") or [],
            "belief_influence": ws_api.get("belief_influence") or [],
            "active_conversation_id": ws_api.get("active_conversation_id"),
        }

        influence_section = page.locator("text=Answer Influence").locator("xpath=ancestor::div[1]")
        panel_text = influence_section.inner_text(timeout=5000) if page.locator("text=Answer Influence").count() else ""
        belief_rows = page.locator("text=Belief #").count()
        memory_rows = page.locator("text=Memory").count()
        report["checks"]["influence_panel"] = {
            "belief_rows_visible": belief_rows,
            "memory_rows_visible": memory_rows,
            "panel_text_sample": panel_text[:600],
            "no_data_shown": "No influence logged yet" in panel_text,
        }

        console_logs.clear()
        page.click("text=Back to Chat")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2500)
        wait_restore_complete(console_logs)
        report["restore_steps_by_phase"]["after_back_to_chat"] = collect_restore_steps(console_logs)

        visible_after_back = count_visible_messages(page)
        sidebar_after_back = active_sidebar_meta(page)
        p4 = shot_dir / "04_after_back_to_chat.png"
        page.screenshot(path=str(p4), full_page=True)
        report["screenshots"]["after_back_to_chat"] = str(p4)
        report["checks"]["after_back_visible"] = visible_after_back
        report["checks"]["after_back_sidebar"] = sidebar_after_back
        report["checks"]["back_to_chat_persisted"] = visible_after_back >= 10

        context.close()
        context2 = browser.new_context(viewport={"width": 1400, "height": 900})
        page2 = context2.new_page()
        console_logs2: list[dict] = []

        def on_console2(msg):
            entry = {"type": msg.type, "text": msg.text}
            console_logs2.append(entry)
            if "RESTORE STEP" in msg.text:
                report["console_logs"].append(entry)

        page2.on("console", on_console2)
        page2.goto(f"{BASE}/", wait_until="networkidle")
        page2.wait_for_timeout(2500)
        wait_restore_complete(console_logs2)
        report["restore_steps_by_phase"]["tab_reopen"] = collect_restore_steps(console_logs2)

        visible_reopen = count_visible_messages(page2)
        sidebar_reopen = active_sidebar_meta(page2)
        p5 = shot_dir / "05_after_tab_reopen.png"
        page2.screenshot(path=str(p5), full_page=True)
        report["screenshots"]["after_tab_reopen"] = str(p5)
        report["checks"]["tab_reopen_visible"] = visible_reopen
        report["checks"]["tab_reopen_sidebar"] = sidebar_reopen
        report["checks"]["tab_reopen_persisted"] = visible_reopen >= 10

        page2.click("text=New Chat")
        page2.wait_for_timeout(1500)
        page2.fill("#msg", "Second conversation unique marker XYZ")
        page2.click("#send")
        page2.wait_for_timeout(10000)
        conv2_visible = count_visible_messages(page2)
        p6 = shot_dir / "06_conversation_2.png"
        page2.screenshot(path=str(p6), full_page=True)
        report["screenshots"]["conversation_2"] = str(p6)
        report["checks"]["conv2_messages"] = conv2_visible

        page2.locator(".conv-item").filter(has_text="Validation user message").first.click()
        page2.wait_for_timeout(2500)
        visible_conv1_switch = count_visible_messages(page2)
        p7 = shot_dir / "07_switched_to_conv1.png"
        page2.screenshot(path=str(p7), full_page=True)
        report["screenshots"]["switched_to_conv1"] = str(p7)
        report["checks"]["switch_to_conv1_visible"] = visible_conv1_switch

        page2.locator(".conv-item").filter(has_text="Second conversation unique marker").first.click()
        page2.wait_for_timeout(2500)
        visible_conv2_switch = count_visible_messages(page2)
        p8 = shot_dir / "08_switched_to_conv2.png"
        page2.screenshot(path=str(p8), full_page=True)
        report["screenshots"]["switched_to_conv2"] = str(p8)
        report["checks"]["switch_to_conv2_visible"] = visible_conv2_switch

        console_logs2.clear()
        page2.reload(wait_until="networkidle")
        page2.wait_for_timeout(2500)
        wait_restore_complete(console_logs2)
        report["restore_steps_by_phase"]["conv2_refresh"] = collect_restore_steps(console_logs2)

        visible_conv2_refresh = count_visible_messages(page2)
        marker_visible = page2.locator("text=Second conversation unique marker XYZ").count() > 0
        p9 = shot_dir / "09_conv2_after_refresh.png"
        page2.screenshot(path=str(p9), full_page=True)
        report["screenshots"]["conv2_after_refresh"] = str(p9)
        report["checks"]["conv2_after_refresh_visible"] = visible_conv2_refresh
        report["checks"]["conv2_marker_visible_after_refresh"] = marker_visible

        page2.goto(f"{BASE}/", wait_until="networkidle")
        page2.fill("#msg", "Influence validation ping unique 999")
        page2.click("#send")
        page2.wait_for_timeout(12000)
        page2.goto(f"{BASE}/dashboard", wait_until="networkidle")
        page2.wait_for_timeout(5000)

        dash2 = api_get("/api/dashboard")
        ws2 = api_get("/api/workspace/session")
        report["api_payloads"]["influence_after_chat_dashboard"] = {
            "memory_influence": dash2.get("memory_influence", []),
            "belief_influence": dash2.get("belief_influence", []),
        }
        report["api_payloads"]["influence_after_chat_workspace"] = {
            "memory_influence": ws2.get("memory_influence", []),
            "belief_influence": ws2.get("belief_influence", []),
        }

        influence_card = page2.locator("text=Answer Influence").locator("xpath=ancestor::div[contains(@class,'card') or contains(@style,'background')][1]")
        influence_text = influence_card.inner_text(timeout=5000) if page2.locator("text=Answer Influence").count() else ""
        belief_ui = page2.locator("text=Belief #").count()
        memory_ui = page2.locator("text=Memory influence").count() + page2.locator("text=Memory:").count()
        report["checks"]["influence_after_chat_panel"] = {
            "belief_rows_visible": belief_ui,
            "memory_rows_visible": memory_ui,
            "panel_text_sample": influence_text[:800],
            "no_data_shown": "No influence logged yet" in influence_text,
        }
        p10 = shot_dir / "10_answer_influence_panel.png"
        page2.screenshot(path=str(p10), full_page=True)
        report["screenshots"]["answer_influence"] = str(p10)

        context2.close()
        browser.close()

    phases = report["restore_steps_by_phase"]
    report["checks"]["all_restore_steps_logged"] = all(
        phase.get("6") for phase in phases.values()
    )
    inf = report["checks"].get("influence_after_chat_panel", {})
    report["passed"] = all([
        report["checks"].get("refresh_persisted"),
        report["checks"].get("back_to_chat_persisted"),
        report["checks"].get("tab_reopen_persisted"),
        report["checks"].get("switch_to_conv1_visible", 0) >= 10,
        report["checks"].get("conv2_marker_visible_after_refresh"),
        report["checks"].get("all_restore_steps_logged"),
        inf.get("belief_rows_visible", 0) >= 1,
        not inf.get("no_data_shown", True),
    ])

    save_report()
    print(json.dumps(report["checks"], indent=2))
    print(f"\nScreenshots: {shot_dir}")
    restore_count = len([e for e in report["console_logs"] if "RESTORE STEP" in e.get("text", "")])
    print(f"Console RESTORE logs: {restore_count}")
    print(f"OVERALL: {'PASS' if report['passed'] else 'FAIL'}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(run_validation())
