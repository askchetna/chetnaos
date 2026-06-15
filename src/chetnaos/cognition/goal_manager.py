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
        except Exception as exc:
            logger.error("GoalManager load failed: %s", exc)

    def _save(self) -> None:
        save_json(memory_path(GOALS_FILE), {
            "active_goal": self._active_goal,
            "goal_queue": self._goal_queue,
            "completed_goals": self._completed_goals[-_MAX_COMPLETED:],
            "failed_goals": self._failed_goals[-_MAX_FAILED:],
        })

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
