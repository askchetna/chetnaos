"""
Belief Revision Engine — gradual belief evolution from evidence.

Purpose: Transform experience into evidence-driven confidence updates.
Inputs:  RealityChecker, Reflection, Learning, GoalManager, SelfModel, Memory
Outputs: belief graph state, revision history, identity signals (not direct identity writes)
Dependencies: src.chetnaos.memory.json_loader (save_json, memory_path)
"""
from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from src.chetnaos.memory.json_loader import memory_path, save_json

if TYPE_CHECKING:
    from src.chetnaos.organism.beliefs import Beliefs

logger = logging.getLogger(__name__)

REVISION_FILE = "belief_revision_state.json"
_MAX_HISTORY = 100
_MAX_EVIDENCE = 30
_MAX_DELTA = 0.05
_MIN_DELTA = 0.01
_REPEAT_BOOST = 1.5


class BeliefRevisionEngine:
    """Signal provider — beliefs evolve gradually, identity receives signals only."""

    def __init__(self):
        self._belief_graph: Dict[str, Dict[str, Any]] = {}
        self._pending_evidence: List[Dict[str, Any]] = []
        self._revision_history: List[Dict[str, Any]] = []
        self._tracked_contradictions: List[Dict[str, Any]] = []
        self._last_evaluation: Dict[str, Any] = {}
        self._identity_signal: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        path = memory_path(REVISION_FILE)
        if not path.exists():
            return
        try:
            import json
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            self._belief_graph = {
                str(k): v for k, v in data.get("belief_graph", {}).items()
            }
            self._revision_history = list(data.get("revision_history", []))
            self._tracked_contradictions = list(data.get("contradictions", []))
            self._pending_evidence = list(data.get("pending_evidence", []))
        except Exception as exc:
            logger.error("BeliefRevisionEngine load failed: %s", exc)

    def _save(self) -> None:
        save_json(memory_path(REVISION_FILE), {
            "belief_graph": self._belief_graph,
            "revision_history": self._revision_history[-_MAX_HISTORY:],
            "contradictions": self._tracked_contradictions[-20:],
            "pending_evidence": self._pending_evidence[-_MAX_EVIDENCE:],
        })

    def _sync_graph(self, beliefs: List[Dict[str, Any]]) -> None:
        for b in beliefs:
            bid = str(b.get("id", b.get("text", "")[:20]))
            node = self._belief_graph.get(bid, {})
            node.update({
                "belief_id": b.get("id"),
                "text": b.get("text", ""),
                "confidence": float(b.get("confidence", 0.5)),
                "source": b.get("source", "unknown"),
                "stability": node.get("stability", self._initial_stability(b)),
                "supporting_evidence": node.get("supporting_evidence", [])[-10:],
                "contradictions": node.get("contradictions", [])[-5:],
            })
            self._belief_graph[bid] = node

    def _initial_stability(self, belief: Dict[str, Any]) -> float:
        if belief.get("source") == "constitution":
            return 0.95
        return round(min(0.9, float(belief.get("confidence", 0.5)) + 0.1), 3)

    def _tokenize(self, text: str) -> set[str]:
        return {w for w in re.findall(r"[a-z]{3,}", text.lower())}

    def _belief_match_score(self, belief_text: str, evidence_text: str) -> float:
        bt = self._tokenize(belief_text)
        et = self._tokenize(evidence_text)
        if not bt or not et:
            return 0.0
        overlap = len(bt & et)
        return overlap / max(len(bt), 1)

    def observe(
        self,
        *,
        beliefs: Optional[List[Dict[str, Any]]] = None,
        reality: Optional[Dict[str, Any]] = None,
        reflection: Optional[Dict[str, Any]] = None,
        learning: Optional[Dict[str, Any]] = None,
        goal_manager: Optional[Dict[str, Any]] = None,
        self_model: Optional[Dict[str, Any]] = None,
        memory_recalled: int = 0,
        external_contradictions: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Collect evidence from cognitive cycle outputs."""
        if beliefs:
            self._sync_graph(beliefs)

        items: List[Dict[str, Any]] = []
        reality = reality or {}
        reflection = reflection or {}
        learning = learning or {}

        quality = reflection.get("quality", "fair")
        reality_conf = float(reality.get("confidence", 0.5))
        support_strength = _MIN_DELTA
        if quality == "good" and reality_conf >= 0.6:
            support_strength = _MIN_DELTA * 2
        elif quality == "poor" or reality_conf < 0.4:
            support_strength = -_MIN_DELTA * 1.5

        items.append({
            "type": "reflection_reality",
            "text": f"quality={quality} confidence={reality_conf:.2f}",
            "strength": support_strength,
            "polarity": "support" if support_strength > 0 else "contradict",
        })

        for lesson in (learning.get("lessons") or [])[:3]:
            items.append({
                "type": "learning",
                "text": lesson.get("lesson", ""),
                "strength": _MIN_DELTA if lesson.get("quality") == "good" else -_MIN_DELTA,
                "polarity": "support" if lesson.get("quality") == "good" else "contradict",
            })

        active = (goal_manager or {}).get("active_goal")
        if active:
            items.append({
                "type": "goal",
                "text": active.get("text", ""),
                "strength": _MIN_DELTA,
                "polarity": "support",
            })

        if self_model:
            conf = float(self_model.get("self_confidence", 0.5))
            items.append({
                "type": "self_model",
                "text": f"self_confidence={conf:.2f}",
                "strength": _MIN_DELTA if conf >= 0.5 else -_MIN_DELTA,
                "polarity": "support" if conf >= 0.5 else "contradict",
            })

        if memory_recalled > 0:
            items.append({
                "type": "memory",
                "text": f"recalled_{memory_recalled}_memories",
                "strength": _MIN_DELTA * 0.5,
                "polarity": "support",
            })

        for contr in (external_contradictions or [])[:5]:
            items.append({
                "type": "contradiction",
                "text": f"{contr.get('belief_a', '')} vs {contr.get('belief_b', '')}",
                "strength": -_MIN_DELTA * 2,
                "polarity": "contradict",
                "conflict_score": contr.get("conflict_score", 50),
            })
            self._tracked_contradictions.append({
                **contr,
                "observed_at": datetime.utcnow().isoformat(),
            })

        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "items": items,
        }
        self._pending_evidence.append(entry)
        self._pending_evidence = self._pending_evidence[-_MAX_EVIDENCE:]
        self._save()

        return {
            "observed_items": len(items),
            "pending_batches": len(self._pending_evidence),
            "graph_size": len(self._belief_graph),
        }

    def evaluate(self) -> Dict[str, Any]:
        """Score pending evidence against the belief graph."""
        deltas: Dict[int, float] = {}
        support_map: Dict[str, List[float]] = {}

        for bid, node in self._belief_graph.items():
            belief_id = node.get("belief_id")
            if belief_id is None:
                continue
            text = node.get("text", "")
            net = 0.0
            supports: List[str] = []
            contradicts: List[str] = []

            for batch in self._pending_evidence[-5:]:
                for item in batch.get("items", []):
                    strength = float(item.get("strength", 0))
                    if item.get("type") == "contradiction":
                        score = self._belief_match_score(text, item.get("text", ""))
                        if score > 0.1 or node.get("source") != "constitution":
                            net += strength * max(score, 0.3)
                            contradicts.append(item.get("text", "")[:80])
                        continue

                    match = self._belief_match_score(text, item.get("text", ""))
                    if match < 0.05 and item.get("type") not in ("reflection_reality",):
                        continue
                    if item.get("type") == "reflection_reality":
                        if node.get("source") == "constitution" and strength > 0:
                            net += strength
                            supports.append(item.get("text", ""))
                        elif strength < 0 and node.get("source") != "constitution":
                            net += strength
                            contradicts.append(item.get("text", ""))
                    else:
                        net += strength * max(match, 0.2)
                        if strength > 0:
                            supports.append(item.get("text", "")[:80])
                        else:
                            contradicts.append(item.get("text", "")[:80])

            if abs(net) < 1e-6:
                continue

            repeat_key = f"{belief_id}:{1 if net > 0 else -1}"
            history_signs = [
                h.get("direction")
                for h in self._revision_history[-3:]
                if h.get("belief_id") == belief_id
            ]
            repeat_count = history_signs.count(1 if net > 0 else -1)
            magnitude = min(_MAX_DELTA, max(_MIN_DELTA, abs(net)))
            if repeat_count >= 2:
                magnitude = min(_MAX_DELTA, magnitude * _REPEAT_BOOST)

            delta = round(magnitude if net > 0 else -magnitude, 4)
            constitution_floor = node.get("source") == "constitution"
            if constitution_floor and delta < 0:
                delta = max(delta, -_MIN_DELTA)

            deltas[int(belief_id)] = delta
            support_map[bid] = [net]

            if supports:
                node["supporting_evidence"] = (node.get("supporting_evidence", []) + supports)[-10:]
            if contradicts:
                node["contradictions"] = (node.get("contradictions", []) + contradicts)[-5:]
            node["stability"] = round(
                max(0.1, min(0.99, node.get("stability", 0.7) - abs(delta) * 0.5)),
                3,
            )

        avg_stability = (
            sum(n.get("stability", 0.5) for n in self._belief_graph.values())
            / max(len(self._belief_graph), 1)
        )
        drift_risk = "low"
        if avg_stability < 0.5:
            drift_risk = "high"
        elif avg_stability < 0.7:
            drift_risk = "medium"

        self._identity_signal = {
            "belief_coherence": round(
                sum(n.get("confidence", 0.5) for n in self._belief_graph.values())
                / max(len(self._belief_graph), 1),
                3,
            ),
            "stability_score": round(avg_stability, 3),
            "drift_risk": drift_risk,
            "touch_identity": False,
            "summary": "Beliefs evolving gradually; identity signal only.",
        }

        self._last_evaluation = {
            "deltas": deltas,
            "beliefs_evaluated": len(deltas),
            "identity_signal": dict(self._identity_signal),
        }
        self._save()
        return dict(self._last_evaluation)

    def revise(self, beliefs_store: Optional["Beliefs"] = None) -> Dict[str, Any]:
        """Apply evaluated deltas — never instant flip."""
        deltas = self._last_evaluation.get("deltas", {})
        applied = 0
        if beliefs_store and deltas:
            applied = beliefs_store.apply_confidence_deltas(deltas)
            for bid, node in self._belief_graph.items():
                belief_id = node.get("belief_id")
                if belief_id in deltas:
                    node["confidence"] = round(
                        max(0.05, min(0.99, node.get("confidence", 0.5) + deltas[belief_id])),
                        3,
                    )

        for belief_id, delta in deltas.items():
            self._revision_history.append({
                "belief_id": belief_id,
                "delta": delta,
                "direction": 1 if delta > 0 else -1,
                "timestamp": datetime.utcnow().isoformat(),
            })
        self._revision_history = self._revision_history[-_MAX_HISTORY:]
        self._save()

        return {
            "revisions_applied": applied,
            "deltas": deltas,
            "identity_signal": dict(self._identity_signal),
        }

    def confidence(self, belief_id: Optional[int] = None) -> Any:
        if belief_id is not None:
            for node in self._belief_graph.values():
                if node.get("belief_id") == belief_id:
                    return node.get("confidence", 0.5)
            return None
        return {
            str(node.get("belief_id")): node.get("confidence", 0.5)
            for node in self._belief_graph.values()
        }

    def contradictions(self) -> List[Dict[str, Any]]:
        return list(self._tracked_contradictions[-20:])

    def history(self) -> List[Dict[str, Any]]:
        return list(self._revision_history)

    def statistics(self) -> Dict[str, Any]:
        stabilities = [n.get("stability", 0.5) for n in self._belief_graph.values()]
        return {
            "beliefs_tracked": len(self._belief_graph),
            "pending_evidence_batches": len(self._pending_evidence),
            "revisions_total": len(self._revision_history),
            "contradictions_tracked": len(self._tracked_contradictions),
            "avg_stability": round(
                sum(stabilities) / max(len(stabilities), 1), 3,
            ) if stabilities else 0.0,
            "avg_confidence": round(
                sum(n.get("confidence", 0.5) for n in self._belief_graph.values())
                / max(len(self._belief_graph), 1),
                3,
            ) if self._belief_graph else 0.0,
            "identity_signal": dict(self._identity_signal),
        }

    def snapshot(self) -> Dict[str, Any]:
        return {
            "statistics": self.statistics(),
            "confidence_map": self.confidence(),
            "recent_history": self.history()[-5:],
            "contradictions": self.contradictions()[-5:],
            "identity_signal": dict(self._identity_signal),
        }
