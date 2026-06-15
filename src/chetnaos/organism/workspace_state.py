"""
Workspace State — Tracks what the organism is actively thinking about.
Represents the organism's cognitive "desk" — what's on it right now.
"""
import json, os
from datetime import datetime

WS_FILE = os.path.join(os.path.dirname(__file__), "../../..", "memory", "workspace_state.json")


class WorkspaceState:
    def __init__(self):
        self._ws = self._load()

    def _load(self) -> dict:
        try:
            p = os.path.abspath(WS_FILE)
            if os.path.exists(p):
                with open(p) as f:
                    return json.load(f)
        except Exception:
            pass
        return {
            "current_thought":    "Initializing cognitive workspace…",
            "current_goal":       "Understand user's needs and respond helpfully.",
            "current_hypothesis": "Every interaction is an opportunity to learn.",
            "current_plan":       "Run full cognitive cycle for each input.",
            "active_priority":    80,
            "pending_contradictions": 0,
            "unsolved_questions": [],
            "artifacts":          [],
            "last_updated":       None,
        }

    def _save(self):
        try:
            p = os.path.abspath(WS_FILE)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as f:
                json.dump(self._ws, f, indent=2)
        except Exception:
            pass

    def update(self, user_input: str, plan: str, domain: str,
               quality: str, attention: dict) -> dict:
        urgent = attention.get("urgent", False)
        focus  = attention.get("focus", [])

        self._ws["current_thought"]    = f"Processing: {user_input[:120]}"
        self._ws["current_goal"]       = f"Answer about {domain}: {user_input[:80]}"
        self._ws["current_hypothesis"] = (
            f"Key concepts: {', '.join(focus[:4])}" if focus
            else "No strong hypothesis yet."
        )
        self._ws["current_plan"]       = plan[:150] if plan else "Direct response."
        self._ws["active_priority"]    = 95 if urgent else (85 if quality == "good" else 70)
        self._ws["last_updated"]       = datetime.utcnow().isoformat()
        self._save()
        return self.get()

    def add_artifact(self, name: str, artifact_type: str):
        artifacts = self._ws.get("artifacts", [])
        artifacts.insert(0, {
            "name":      name,
            "type":      artifact_type,
            "created_at": datetime.utcnow().isoformat(),
        })
        self._ws["artifacts"] = artifacts[:10]  # Keep last 10
        self._save()

    def add_question(self, question: str):
        q_list = self._ws.get("unsolved_questions", [])
        if question not in q_list:
            q_list.insert(0, question)
        self._ws["unsolved_questions"] = q_list[:5]
        self._save()

    def set_contradictions(self, count: int):
        self._ws["pending_contradictions"] = count
        self._save()

    def get(self) -> dict:
        return dict(self._ws)
