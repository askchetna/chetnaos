"""One-shot E2E integration validation — capture live subsystem data."""
import json
import urllib.request

BASE = "http://127.0.0.1:8000"

INTEGRATION_PROMPT = """End-to-end integration validation. Store and process:

- Goal: launch ChetnaOS publicly
- Revenue target: ₹1 lakh/month
- Focus domains: AGI research, AI consulting, software development, business growth

Tasks: store in memory, activate goals, explain beliefs/memories/contradictions/confidence,
create 7-day action plan, connect to long-term goals, persist conversation context."""


def post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{BASE}{path}", data=data,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())


def get(path):
    with urllib.request.urlopen(f"{BASE}{path}", timeout=60) as r:
        return json.loads(r.read())


def main():
    chat = post("/api/chat", {"text": INTEGRATION_PROMPT})
    dash = get("/api/dashboard")
    ws = get("/api/workspace/session")
    convs = get("/api/conversations")

    out = {
        "chat_reply_preview": (chat.get("reply") or "")[:2000],
        "chat_meta": chat.get("meta", {}),
        "conversation_id": chat.get("conversation_id"),
        "dashboard": {
            "memory_influence": dash.get("memory_influence", []),
            "belief_influence": dash.get("belief_influence", []),
            "contradictions": dash.get("contradictions", []),
            "beliefs_count": dash.get("beliefs", {}).get("count"),
            "cognitive_organs": dash.get("cognitive_organs", {}),
            "workspace": dash.get("workspace", {}),
            "memory": dash.get("memory", {}),
            "training_goals": dash.get("training_goals", []),
            "development": dash.get("development", {}),
        },
        "workspace_session": ws,
        "conversation_count": len(convs.get("conversations", [])),
        "active_conv_messages": len(
            (ws.get("conversation") or {}).get("messages", [])
        ),
    }
    path = "reports/integration_validation_live.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(path)
    print(json.dumps({
        "confidence": chat.get("meta", {}).get("confidence"),
        "belief_influence_count": len(dash.get("belief_influence", [])),
        "memory_influence_count": len(dash.get("memory_influence", [])),
        "contradiction_count": len(dash.get("contradictions", [])),
        "working_memory": dash.get("cognitive_organs", {}).get("working_memory", {}),
        "active_goal": dash.get("cognitive_organs", {}).get("goal_manager", {}).get("active_goal"),
    }, indent=2))


if __name__ == "__main__":
    main()
