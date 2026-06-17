"""
Goal Manager — central motivational system for the cognitive organism.

Purpose: Unify user, intrinsic, training, exploration, and maintenance goals.
Inputs:  signals from CuriosityDrive, SelfModel, Purpose, SelfTrainer, FounderContext
Outputs: active goal, queue, completion statistics
Dependencies: src.chetnaos.memory.json_loader (save_json, memory_path)
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from src.chetnaos.memory.json_loader import memory_path, save_json

logger = logging.getLogger(__name__)

GOALS_FILE = "goal_manager_state.json"
_MAX_COMPLETED = 50
_MAX_FAILED = 50
_MAX_LEARNING_EVENTS = 100
_MAX_OUTCOME_ATTRIBUTION = 20
_CONF_MIN = 0.05
_CONF_MAX = 0.99
_HEALTH_HEALTHY = 5.0
_HEALTH_WARNING = 15.0
_STALLED_STREAK = 3
_MAX_MILESTONES = 7
_MIN_MILESTONES = 3


class GoalType(str, Enum):
    USER = "USER"
    INTRINSIC = "INTRINSIC"
    TRAINING = "TRAINING"
    EXPLORATION = "EXPLORATION"
    MAINTENANCE = "MAINTENANCE"


class GoalManager:
    """Single goal system — queue, priority, persistence via memory/ JSON."""

    def __init__(self):
        self._active_goal: Optional[Dict[str, Any]] = None
        self._goal_queue: List[Dict[str, Any]] = []
        self._completed_goals: List[Dict[str, Any]] = []
        self._failed_goals: List[Dict[str, Any]] = []
        self._learning_events: List[Dict[str, Any]] = []
        self._milestone_pattern_stats: Dict[str, Dict[str, int]] = {}
        self._load()

    def _load(self) -> None:
        path = memory_path(GOALS_FILE)
        if not path.exists():
            return
        try:
            import json
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            self._active_goal = data.get("active_goal")
            self._goal_queue = list(data.get("goal_queue", []))
            self._completed_goals = list(data.get("completed_goals", []))
            self._failed_goals = list(data.get("failed_goals", []))
            self._learning_events = list(data.get("learning_events", []))
            self._milestone_pattern_stats = dict(data.get("milestone_pattern_stats", {}))
            if self._active_goal:
                self._migrate_goal_progress(self._active_goal)
        except Exception as exc:
            logger.error("GoalManager load failed: %s", exc)

    def _save(self) -> None:
        save_json(memory_path(GOALS_FILE), {
            "active_goal": self._active_goal,
            "goal_queue": self._goal_queue,
            "completed_goals": self._completed_goals[-_MAX_COMPLETED:],
            "failed_goals": self._failed_goals[-_MAX_FAILED:],
            "learning_events": self._learning_events[-_MAX_LEARNING_EVENTS:],
            "milestone_pattern_stats": self._milestone_pattern_stats,
        })

    def _migrate_goal_progress(self, goal: Dict[str, Any]) -> None:
        """Ensure developmental progress fields exist on a goal record."""
        goal.setdefault("expected_progress", 20.0)
        goal.setdefault("actual_progress", 0.0)
        goal.setdefault("prediction_error", 0.0)
        goal.setdefault("confidence", 0.5)
        goal.setdefault("next_action", "Continue current plan")
        goal.setdefault("health", "healthy")
        goal.setdefault("negative_error_streak", 0)
        goal.setdefault("outcome_attribution", [])
        goal.setdefault("progress_cycles", 0)
        goal.setdefault("milestones", [])
        goal.setdefault("blocked_reason", "")
        goal.setdefault("recommended_next_step", "")

    def _init_progress_fields(self, goal: Dict[str, Any]) -> None:
        priority = float(goal.get("goal_priority", 50.0))
        self._migrate_goal_progress(goal)
        goal["expected_progress"] = round(min(40.0, priority * 0.35), 1)
        goal["actual_progress"] = 0.0
        goal["prediction_error"] = -goal["expected_progress"]
        goal["confidence"] = round(0.45 + priority / 200.0, 2)
        goal["confidence"] = max(_CONF_MIN, min(_CONF_MAX, goal["confidence"]))
        goal["next_action"] = self._suggest_next_action(goal, "healthy", {})
        goal["health"] = "healthy"
        goal["negative_error_streak"] = 0
        goal["outcome_attribution"] = []
        goal["progress_cycles"] = 0
        goal["milestones"] = self._decompose_goal_into_milestones(goal)
        goal["blocked_reason"] = ""
        goal["recommended_next_step"] = ""

    def _decompose_goal_into_milestones(self, goal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate concrete executable milestones for an active goal."""
        text = (goal.get("text") or "").lower()
        cycle_n = int(goal.get("progress_cycles", 0))
        default_templates = [
            ("Define execution scope", "Scope document or checklist exists"),
            ("Execute first concrete deliverable", "Deliverable artifact exists"),
            ("Review output quality", "Review notes or validation result exists"),
            ("Publish or communicate result", "Announcement/message was sent"),
            ("Collect feedback and update", "At least one feedback item captured"),
        ]
        if "launch" in text and ("public" in text or "product" in text or "chetnaos" in text):
            templates = [
                ("Prepare public demo", "Demo script or run output exists"),
                ("Create launch landing page", "Landing page URL exists"),
                ("Record demo video", "Demo video file or link exists"),
                ("Publish launch announcement", "Announcement post is published"),
                ("Collect first feedback", "At least one external feedback note exists"),
            ]
        elif "client" in text or "consult" in text or "revenue" in text:
            templates = [
                ("Define target customer profile", "Target customer profile document exists"),
                ("Create outreach message draft", "Outreach message draft exists"),
                ("Send first outreach batch", "At least one outreach message sent"),
                ("Run first discovery call", "Discovery call notes exist"),
                ("Submit proposal", "Proposal document or message exists"),
            ]
        elif "train" in text or "improve capability" in text:
            templates = [
                ("Define practice session", "Practice objective is documented"),
                ("Run first focused practice", "Practice output or notes exist"),
                ("Evaluate improvement", "Before/after score recorded"),
            ]
        else:
            templates = default_templates

        templates = templates[:_MAX_MILESTONES]
        if len(templates) < _MIN_MILESTONES:
            templates = default_templates[:_MIN_MILESTONES]

        milestones: List[Dict[str, Any]] = []
        for idx, (title, criteria) in enumerate(templates):
            milestones.append({
                "title": title,
                "status": "active" if idx == 0 else "pending",
                "progress": 0.0,
                "confidence": float(goal.get("confidence", 0.5)),
                "completion_criteria": criteria,
                "created_cycle": cycle_n,
            })
        return milestones

    def _make_goal(
        self,
        text: str,
        goal_type: GoalType | str,
        priority: float,
        origin: str,
    ) -> Dict[str, Any]:
        gtype = goal_type.value if isinstance(goal_type, GoalType) else str(goal_type)
        return {
            "id": str(uuid.uuid4())[:8],
            "text": text[:300],
            "goal_type": gtype,
            "goal_priority": round(max(0.0, min(100.0, float(priority))), 2),
            "goal_origin": origin,
            "status": "queued",
            "created_at": datetime.utcnow().isoformat(),
        }

    def add_goal(
        self,
        text: str,
        goal_type: GoalType | str = GoalType.USER,
        priority: float = 50.0,
        origin: str = "manual",
    ) -> Dict[str, Any]:
        goal = self._make_goal(text, goal_type, priority, origin)
        self._goal_queue.append(goal)
        self._goal_queue.sort(key=lambda g: g["goal_priority"], reverse=True)
        self._save()
        logger.debug("GoalManager added goal %s type=%s", goal["id"], goal["goal_type"])
        return dict(goal)

    def next_goal(self) -> Optional[Dict[str, Any]]:
        """Promote highest-priority queued goal to active."""
        if self._active_goal is not None:
            return dict(self._active_goal)
        if not self._goal_queue:
            return None
        self._active_goal = self._goal_queue.pop(0)
        self._active_goal["status"] = "active"
        self._active_goal["activated_at"] = datetime.utcnow().isoformat()
        self._init_progress_fields(self._active_goal)
        self._save()
        return dict(self._active_goal)

    def complete_goal(self, goal_id: str) -> Optional[Dict[str, Any]]:
        goal = self._pop_goal_by_id(goal_id)
        if goal is None:
            return None
        goal["status"] = "completed"
        goal["completed_at"] = datetime.utcnow().isoformat()
        self._completed_goals.append(goal)
        self._save()
        return goal

    def fail_goal(self, goal_id: str, reason: str = "") -> Optional[Dict[str, Any]]:
        goal = self._pop_goal_by_id(goal_id)
        if goal is None:
            return None
        goal["status"] = "failed"
        goal["failed_at"] = datetime.utcnow().isoformat()
        goal["fail_reason"] = reason[:200]
        self._failed_goals.append(goal)
        self._save()
        return goal

    def _pop_goal_by_id(self, goal_id: str) -> Optional[Dict[str, Any]]:
        if self._active_goal and self._active_goal.get("id") == goal_id:
            goal = self._active_goal
            self._active_goal = None
            return goal
        for i, g in enumerate(self._goal_queue):
            if g.get("id") == goal_id:
                return self._goal_queue.pop(i)
        return None

    def active_goal(self) -> Optional[Dict[str, Any]]:
        return dict(self._active_goal) if self._active_goal else None

    def goal_status(self) -> Dict[str, Any]:
        return {
            "active_goal": self.active_goal(),
            "queue_size": len(self._goal_queue),
            "queue_preview": [g["text"][:60] for g in self._goal_queue[:3]],
            "completed_count": len(self._completed_goals),
            "failed_count": len(self._failed_goals),
        }

    def goal_statistics(self) -> Dict[str, Any]:
        by_type: Dict[str, int] = {}
        for pool in (self._goal_queue, self._completed_goals, self._failed_goals):
            for g in pool:
                t = g.get("goal_type", "UNKNOWN")
                by_type[t] = by_type.get(t, 0) + 1
        if self._active_goal:
            t = self._active_goal.get("goal_type", "UNKNOWN")
            by_type[t] = by_type.get(t, 0) + 1
        return {
            "active": 1 if self._active_goal else 0,
            "queued": len(self._goal_queue),
            "completed": len(self._completed_goals),
            "failed": len(self._failed_goals),
            "by_type": by_type,
            "avg_queue_priority": round(
                sum(g["goal_priority"] for g in self._goal_queue) / max(len(self._goal_queue), 1),
                2,
            ) if self._goal_queue else 0.0,
        }

    def ingest_signals(
        self,
        *,
        purpose: Optional[str] = None,
        training_goals: Optional[List[Dict[str, Any]]] = None,
        curiosity_goals: Optional[List[Dict[str, Any]]] = None,
        self_model_limits: Optional[List[str]] = None,
        founder_context: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Absorb motivational signals into the goal queue.
        Returns count of newly added goals (deduplicated by text).
        """
        existing_texts = {
            g["text"].lower()
            for g in self._goal_queue
            + ([self._active_goal] if self._active_goal else [])
        }
        added = 0

        if purpose and purpose.lower() not in existing_texts:
            self.add_goal(purpose, GoalType.INTRINSIC, priority=60.0, origin="purpose")
            existing_texts.add(purpose.lower())
            added += 1

        for tg in (training_goals or [])[:3]:
            text = f"Train {tg.get('skill', 'skill')}: {tg.get('suggested_training', '')}"
            if text.lower() not in existing_texts:
                self.add_goal(
                    text, GoalType.TRAINING,
                    priority=float(tg.get("priority", 50)),
                    origin="self_trainer",
                )
                existing_texts.add(text.lower())
                added += 1

        for eg in (curiosity_goals or [])[:3]:
            text = f"{eg.get('type', 'explore')}: {eg.get('target', '')}"
            if text.lower() not in existing_texts:
                self.add_goal(
                    text, GoalType.EXPLORATION,
                    priority=float(eg.get("priority", 0.4)) * 100,
                    origin="curiosity",
                )
                existing_texts.add(text.lower())
                added += 1

        for limit in (self_model_limits or [])[:2]:
            text = f"Improve capability: {limit}"
            if text.lower() not in existing_texts:
                self.add_goal(text, GoalType.MAINTENANCE, priority=55.0, origin="self_model")
                existing_texts.add(text.lower())
                added += 1

        if founder_context:
            mission = founder_context.get("primary_mission", "")
            if mission and mission.lower() not in existing_texts:
                self.add_goal(
                    mission, GoalType.MAINTENANCE, priority=70.0, origin="founder_model",
                )
                existing_texts.add(mission.lower())
                added += 1
            for fg in founder_context.get("founder_goals", [])[:2]:
                text = fg.get("goal", "")
                if text and text.lower() not in existing_texts:
                    self.add_goal(
                        text, GoalType.MAINTENANCE,
                        priority=float(fg.get("priority", 65)),
                        origin="founder_model",
                    )
                    existing_texts.add(text.lower())
                    added += 1

        return added

    # ── Prediction error ↔ goal progress loop ─────────────────────────────

    def update_prediction_error_loop(
        self,
        *,
        cycle_id: str = "",
        cycle_n: int = 0,
        reality: Optional[Dict[str, Any]] = None,
        reflection: Optional[Dict[str, Any]] = None,
        evaluation: Optional[Dict[str, Any]] = None,
        decision: Optional[Dict[str, Any]] = None,
        goal_used: bool = False,
        user_input: str = "",
        plan: str = "",
    ) -> Dict[str, Any]:
        """
        Compare expected vs observed goal progress each cycle.
        Updates confidence, health, next action, and outcome attribution.
        """
        if not self._active_goal:
            return {"stage": "GOAL_PROGRESS", "active": False}

        goal = self._active_goal
        self._migrate_goal_progress(goal)
        prev_error = float(goal.get("prediction_error", 0.0))
        prev_actual = float(goal.get("actual_progress", 0.0))
        signals = {
            "reality": reality or {},
            "reflection": reflection or {},
            "evaluation": evaluation or {},
            "decision": decision or {},
            "goal_used": goal_used,
            "user_input": user_input,
            "plan": plan,
        }
        self._update_milestones(goal, signals)

        expected_delta = self._expected_progress_delta(goal)
        actual_delta = self._actual_progress_delta(goal, signals)
        goal["expected_progress"] = round(
            min(100.0, float(goal["expected_progress"]) + expected_delta), 1
        )
        goal["actual_progress"] = self._milestone_progress(goal)
        goal["prediction_error"] = round(
            goal["actual_progress"] - goal["expected_progress"], 1
        )
        goal["progress_cycles"] = int(goal.get("progress_cycles", 0)) + 1

        self._adjust_confidence(goal, goal["prediction_error"], prev_error)
        health = self._classify_health(goal)
        goal["health"] = health
        goal["next_action"] = self._suggest_next_action(goal, health, signals)
        goal["blocked_reason"] = ""
        goal["recommended_next_step"] = ""

        stalled_correction = None
        if health == "stalled":
            stalled_correction = self._stalled_correction(goal, signals)
            goal["stalled_diagnosis"] = stalled_correction["diagnosis"]
            goal["corrective_recommendation"] = stalled_correction["recommendation"]
            goal["blocked_reason"] = stalled_correction["blocked_reason"]
            goal["recommended_next_step"] = stalled_correction["recommendation"]

        if goal["actual_progress"] >= 100.0:
            goal["health"] = "completed"
            goal["next_action"] = "Goal reached — mark complete when verified"

        self._record_outcome_attribution(
            goal,
            prev_error=prev_error,
            prev_actual=prev_actual,
            actual_delta=actual_delta,
            last_action=goal.get("next_action", ""),
            cycle_id=cycle_id,
        )
        self._log_learning_event({
            "timestamp": datetime.utcnow().isoformat(),
            "cycle_id": cycle_id,
            "cycle_n": cycle_n,
            "goal_id": goal.get("id"),
            "goal_text": goal.get("text", "")[:120],
            "expected_progress": goal["expected_progress"],
            "actual_progress": goal["actual_progress"],
            "prediction_error": goal["prediction_error"],
            "confidence": goal["confidence"],
            "health": goal["health"],
            "next_action": goal["next_action"],
            "actual_delta": actual_delta,
        })
        self._save()

        result = {
            "stage": "GOAL_PROGRESS",
            "active": True,
            "goal_id": goal.get("id"),
            "goal_text": goal.get("text", "")[:120],
            "expected_progress": goal["expected_progress"],
            "actual_progress": goal["actual_progress"],
            "prediction_error": goal["prediction_error"],
            "confidence": goal["confidence"],
            "health": goal["health"],
            "next_action": goal["next_action"],
            "milestones": goal.get("milestones", []),
            "blocked_reason": goal.get("blocked_reason", ""),
            "recommended_next_step": goal.get("recommended_next_step", ""),
            "milestone_pattern_stats": self._milestone_pattern_stats,
        }
        if stalled_correction:
            result["stalled_correction"] = stalled_correction
        return result

    def _expected_progress_delta(self, goal: Dict[str, Any]) -> float:
        priority = float(goal.get("goal_priority", 50.0))
        return round(0.3 + priority / 200.0, 2)

    def _actual_progress_delta(self, goal: Dict[str, Any], signals: Dict[str, Any]) -> float:
        reflection = signals.get("reflection") or {}
        reality = signals.get("reality") or {}
        quality = reflection.get("quality", "fair")
        confidence = float(reality.get("confidence", 0.5))
        goal_used = bool(signals.get("goal_used"))

        delta = 0.0
        if quality == "good":
            delta += 1.2
        elif quality == "fair":
            delta += 0.4
        elif quality == "poor":
            delta -= 0.5

        if goal_used:
            delta += 0.6
        else:
            delta -= 0.3

        if confidence >= 0.7:
            delta += 0.3
        elif confidence < 0.45:
            delta -= 0.2

        if signals.get("evaluation", {}).get("passed") is False:
            delta -= 0.4

        return round(delta, 2)

    def _milestone_progress(self, goal: Dict[str, Any]) -> float:
        milestones = list(goal.get("milestones") or [])
        if not milestones:
            return round(float(goal.get("actual_progress", 0.0)), 1)
        total = len(milestones)
        completed = sum(1 for m in milestones if m.get("status") == "completed")
        active = next((m for m in milestones if m.get("status") == "active"), None)
        active_frac = (float(active.get("progress", 0.0)) / 100.0) if active else 0.0
        return round(min(100.0, ((completed + active_frac) / total) * 100.0), 1)

    def _criteria_satisfied(self, criteria: str, signals: Dict[str, Any], milestone: Dict[str, Any]) -> bool:
        corpus = " ".join([
            str(signals.get("user_input", "")).lower(),
            str(signals.get("plan", "")).lower(),
            str((signals.get("decision") or {}).get("action", "")).lower(),
        ])
        c = (criteria or "").lower()
        title = (milestone.get("title") or "").lower()
        # Lightweight observable checks; no autonomous execution.
        if "url exists" in c:
            return ("http://" in corpus) or ("https://" in corpus) or ("url" in corpus)
        if "video" in c:
            return "video" in corpus or ".mp4" in corpus
        if "announcement" in c or "published" in c:
            return "announcement" in corpus or "publish" in corpus or "posted" in corpus
        if "feedback" in c:
            return "feedback" in corpus or "response" in corpus
        if "document" in c or "notes" in c or "draft" in c:
            return "doc" in corpus or "draft" in corpus or "notes" in corpus
        # Fallback: key title tokens observed in current cycle context.
        tokens = [t for t in title.split() if len(t) > 3]
        return bool(tokens) and any(t in corpus for t in tokens)

    def _pattern_key(self, milestone: Dict[str, Any]) -> str:
        text = (milestone.get("title") or "").lower()
        if "demo" in text:
            return "demo"
        if "landing page" in text or "page" in text:
            return "landing_page"
        if "video" in text:
            return "video"
        if "announcement" in text or "publish" in text:
            return "announcement"
        if "feedback" in text:
            return "feedback"
        if "outreach" in text:
            return "outreach"
        if "call" in text:
            return "discovery_call"
        return "generic"

    def _bump_milestone_pattern(self, milestone: Dict[str, Any], field: str) -> None:
        key = self._pattern_key(milestone)
        stats = dict(self._milestone_pattern_stats.get(key, {"completed": 0, "stalled": 0}))
        stats[field] = int(stats.get(field, 0)) + 1
        self._milestone_pattern_stats[key] = stats

    def _update_milestones(self, goal: Dict[str, Any], signals: Dict[str, Any]) -> None:
        milestones = list(goal.get("milestones") or [])
        if not milestones:
            goal["milestones"] = self._decompose_goal_into_milestones(goal)
            milestones = goal["milestones"]

        active_idx = next((i for i, m in enumerate(milestones) if m.get("status") == "active"), None)
        if active_idx is None:
            pending_idx = next((i for i, m in enumerate(milestones) if m.get("status") == "pending"), None)
            if pending_idx is not None:
                milestones[pending_idx]["status"] = "active"
                active_idx = pending_idx
            else:
                return

        m = milestones[active_idx]
        quality = (signals.get("reflection") or {}).get("quality", "fair")
        goal_used = bool(signals.get("goal_used"))
        boost = 10.0 if quality == "good" else 4.0 if quality == "fair" else -2.0
        if goal_used:
            boost += 6.0
        m["progress"] = round(max(0.0, min(100.0, float(m.get("progress", 0.0)) + boost)), 1)
        m["confidence"] = round(max(_CONF_MIN, min(_CONF_MAX, float(m.get("confidence", 0.5)) + (0.03 if boost > 0 else -0.02))), 2)

        if self._criteria_satisfied(str(m.get("completion_criteria", "")), signals, m):
            m["status"] = "completed"
            m["progress"] = 100.0
            m["completed_at"] = datetime.utcnow().isoformat()
            self._bump_milestone_pattern(m, "completed")
            next_pending = next((i for i, x in enumerate(milestones) if x.get("status") == "pending"), None)
            if next_pending is not None:
                milestones[next_pending]["status"] = "active"
        elif goal.get("health") == "stalled" or boost < 0:
            self._bump_milestone_pattern(m, "stalled")

        goal["milestones"] = milestones

    def _adjust_confidence(
        self, goal: Dict[str, Any], error: float, prev_error: float
    ) -> None:
        conf = float(goal.get("confidence", 0.5))
        error_improved = abs(error) < abs(prev_error)
        error_worsened = abs(error) > abs(prev_error) + 2.0

        if error_improved and abs(error) <= _HEALTH_HEALTHY:
            conf += 0.03
        elif error_worsened:
            conf -= 0.04
        elif error < -_HEALTH_WARNING:
            conf -= 0.02

        goal["confidence"] = round(max(_CONF_MIN, min(_CONF_MAX, conf)), 2)

    def _classify_health(self, goal: Dict[str, Any]) -> str:
        error = float(goal.get("prediction_error", 0.0))
        actual = float(goal.get("actual_progress", 0.0))
        streak = int(goal.get("negative_error_streak", 0))

        if actual >= 100.0:
            goal["negative_error_streak"] = 0
            return "completed"

        if error < 0:
            streak += 1
        else:
            streak = 0
        goal["negative_error_streak"] = streak

        if error < -_HEALTH_WARNING or streak >= _STALLED_STREAK:
            return "stalled"
        if error < -_HEALTH_HEALTHY:
            return "warning"
        return "healthy"

    def _suggest_next_action(
        self, goal: Dict[str, Any], health: str, signals: Dict[str, Any]
    ) -> str:
        text = (goal.get("text") or "active goal")[:80]
        plan = (signals.get("plan") or "").strip()
        if health == "stalled":
            blocked = self._current_blocked_milestone(goal)
            if blocked:
                return f"Unblock milestone: {blocked}"
            return f"Unblock progress on: {text}"
        if health == "warning":
            return f"Re-focus execution on: {text}"
        if plan:
            return plan[:120]
        if signals.get("goal_used"):
            return f"Continue aligned work toward: {text}"
        return f"Align next response with: {text}"

    def _stalled_correction(
        self, goal: Dict[str, Any], signals: Dict[str, Any]
    ) -> Dict[str, str]:
        text = goal.get("text", "this goal")
        error = goal.get("prediction_error", 0)
        goal_used = signals.get("goal_used", False)
        quality = (signals.get("reflection") or {}).get("quality", "fair")

        blockers = []
        blocked_ms = self._current_blocked_milestone(goal)
        if not goal_used:
            blockers.append("responses are not consistently using the active goal")
        if quality == "poor":
            blockers.append("recent cycle quality is poor")
        if error < -20:
            blockers.append("progress is far below expectation")
        if blocked_ms:
            blockers.append(f"milestone '{blocked_ms}' is blocked")

        blocker_text = (
            "; ".join(blockers) if blockers else "progress rate is below expected trajectory"
        )
        recommendation = (
            f"Focus next cycle on '{blocked_ms or text[:60]}' and produce one concrete artifact "
            f"that satisfies its completion criteria."
        )
        return {
            "diagnosis": f"What is preventing progress? {blocker_text}.",
            "recommendation": recommendation,
            "blocked_reason": blocker_text,
        }

    def _current_blocked_milestone(self, goal: Dict[str, Any]) -> str:
        active = next((m for m in (goal.get("milestones") or []) if m.get("status") == "active"), None)
        return (active or {}).get("title", "")

    def _record_outcome_attribution(
        self,
        goal: Dict[str, Any],
        *,
        prev_error: float,
        prev_actual: float,
        actual_delta: float,
        last_action: str,
        cycle_id: str,
    ) -> None:
        error_now = float(goal.get("prediction_error", 0.0))
        if actual_delta > 0.5 and error_now > prev_error:
            outcome = "improved"
        elif actual_delta < 0 or error_now < prev_error - 1.0:
            outcome = "worsened"
        else:
            outcome = "neutral"

        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "cycle_id": cycle_id,
            "action": last_action[:160],
            "outcome": outcome,
            "delta_error": round(error_now - prev_error, 2),
            "delta_actual": round(float(goal.get("actual_progress", 0)) - prev_actual, 2),
        }
        attr = list(goal.get("outcome_attribution") or [])
        attr.append(entry)
        goal["outcome_attribution"] = attr[-_MAX_OUTCOME_ATTRIBUTION:]

    def _log_learning_event(self, event: Dict[str, Any]) -> None:
        self._learning_events.append(event)
        self._learning_events = self._learning_events[-_MAX_LEARNING_EVENTS:]

    def goal_progress_summary(self) -> Dict[str, Any]:
        """Dashboard-friendly snapshot of active goal progress loop."""
        goal = self.active_goal()
        if not goal:
            return {"active": False}
        return {
            "active": True,
            "goal": goal.get("text", "")[:120],
            "expected_progress": goal.get("expected_progress"),
            "actual_progress": goal.get("actual_progress"),
            "prediction_error": goal.get("prediction_error"),
            "confidence": goal.get("confidence"),
            "health": goal.get("health"),
            "next_action": goal.get("next_action"),
            "stalled_diagnosis": goal.get("stalled_diagnosis"),
            "corrective_recommendation": goal.get("corrective_recommendation"),
            "blocked_reason": goal.get("blocked_reason", ""),
            "recommended_next_step": goal.get("recommended_next_step", ""),
            "milestones": goal.get("milestones", []),
            "milestone_pattern_stats": self._milestone_pattern_stats,
            "recent_learning": self._learning_events[-3:],
        }
