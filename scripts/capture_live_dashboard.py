"""Capture live dashboard screenshots after API chat on port 8001."""
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
BASE = "http://127.0.0.1:8001"
OUT = ROOT / "reports" / "memory_verification" / "20260617T081536"


def post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        BASE + path, data=data,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    return json.loads(urllib.request.urlopen(req, timeout=120).read())


def get(path):
    return json.loads(urllib.request.urlopen(BASE + path, timeout=60).read())


def main():
    from src.chetnaos.memory.store import get_memory_store

    store = get_memory_store()
    store.upsert(
        "The Founder's secret validation token is OMEGA-7429-X",
        meta={"category": "long_term_memory"},
    )

    conv = post("/api/conversations", {"title": "8F2 live dashboard"})
    cid = conv["conversation"]["id"]
    post("/api/conversations/active", {"conversation_id": cid})
    chat = post("/api/chat", {
        "text": "What do you know about my validation token?",
        "conversation_id": cid,
    })
    trace = get("/api/memory_trace")

    print("OMEGA in answer:", "OMEGA-7429-X" in chat.get("reply", ""))
    print("trace selected:", len(trace.get("trace", {}).get("memories_selected", [])))

    from playwright.sync_api import sync_playwright

    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        page = p.chromium.launch(headless=True).new_page(viewport={"width": 1400, "height": 900})
        page.goto(f"{BASE}/dashboard", wait_until="networkidle")
        page.wait_for_timeout(4000)
        page.screenshot(path=str(OUT / "dashboard_live_full.png"), full_page=True)
        card = page.locator(".card").filter(
            has=page.locator(".ch", has_text="Memory Recall Trace")
        ).first
        if card.count():
            card.screenshot(path=str(OUT / "memory_recall_trace_live.png"))
        inf = page.locator(".card").filter(
            has=page.locator(".ch", has_text="Answer Influence")
        ).first
        if inf.count():
            inf.screenshot(path=str(OUT / "answer_influence_live.png"))
    print("screenshots saved to", OUT)


if __name__ == "__main__":
    main()
