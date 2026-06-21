"""
Self Model — computational model of own capabilities, limits, and becoming.

Purpose: Track what the organism can/cannot do; persist across restarts.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from src.chetnaos.memory.json_loader import load_self_model, memory_path, save_json

_PERSIST_DEFAULT = {
    "who_am_i": "I am Chetna, a cognitive AI system with memory, goals, and reasoning.",
    "becoming": "A reflective partner serving with truth and compassion.",
    "matters_most": ["truth", "growth", "founder alignment"],
    "current_focus": "",
    "recent_changes": [],
    "capability_map": {},
    "known_limits": [],
    "self_confidence": 0.6,
    "updated_at": None,
}


class SelfModel:
  """Explicit self-model distinct from Identity (name/values)."""

  _LIMIT_THRESHOLD = 0.45

  def __init__(self):
    self._capability_map: Dict[str, float] = {}
    self._known_limits: List[str] = []
    self._self_confidence: float = 0.6
    self._development_state: Dict[str, Any] = {}
    self._persisted = self._load_persisted()

  def _load_persisted(self) -> dict:
    from src.chetnaos.memory.identity_guard import scrub_self_model_record

    return scrub_self_model_record(load_self_model(dict(_PERSIST_DEFAULT)))

  def _save_persisted(self) -> None:
    data = {
        "who_am_i": self._persisted.get("who_am_i", _PERSIST_DEFAULT["who_am_i"]),
        "becoming": self._persisted.get("becoming", _PERSIST_DEFAULT["becoming"]),
        "matters_most": self._persisted.get("matters_most", _PERSIST_DEFAULT["matters_most"]),
        "current_focus": self._persisted.get("current_focus", ""),
        "recent_changes": self._persisted.get("recent_changes", [])[-10:],
        "capability_map": self.capability_map(),
        "known_limits": self.known_limits(),
        "self_confidence": self.self_confidence(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    self._persisted = data
    save_json(memory_path("self_model.json"), data)

  def update(
      self,
      *,
      skills: Optional[Dict[str, Any]] = None,
      development: Optional[Dict[str, Any]] = None,
      meta_cognition: Optional[Dict[str, Any]] = None,
      reality_confidence: Optional[float] = None,
      current_focus: str = "",
  ) -> Dict[str, Any]:
    if skills:
      self._capability_map = {
          name: float(data.get("score", 0.5))
          for name, data in skills.items()
      }
      self._known_limits = [
          name for name, score in self._capability_map.items()
          if score < self._LIMIT_THRESHOLD
      ]

    if development:
      self._development_state = dict(development)

    confidence_signals: List[float] = []
    if meta_cognition:
      correctness = meta_cognition.get("correctness")
      if isinstance(correctness, (int, float)):
        confidence_signals.append(float(correctness) / 100.0 if correctness > 1 else correctness)
    if reality_confidence is not None:
      confidence_signals.append(float(reality_confidence))
    if development:
      total = max(development.get("total_cycles", 0), 1)
      good_ratio = development.get("good_cycles", 0) / total
      confidence_signals.append(min(0.95, 0.4 + good_ratio * 0.5))
    if self._capability_map:
      confidence_signals.append(sum(self._capability_map.values()) / len(self._capability_map))

    if confidence_signals:
      self._self_confidence = round(sum(confidence_signals) / len(confidence_signals), 3)

    if current_focus:
      self._persisted["current_focus"] = current_focus[:200]

    self._save_persisted()
    return self.snapshot()

  def record_change(self, change: str) -> None:
    if not change:
      return
    changes = self._persisted.get("recent_changes", [])
    changes.append(change[:200])
    self._persisted["recent_changes"] = changes[-10:]
    self._save_persisted()

  def capability_map(self) -> Dict[str, float]:
    return dict(self._capability_map)

  def known_limits(self) -> List[str]:
    return list(self._known_limits)

  def self_confidence(self) -> float:
    return self._self_confidence

  def snapshot(self) -> Dict[str, Any]:
    return {
        "who_am_i": self._persisted.get("who_am_i", _PERSIST_DEFAULT["who_am_i"]),
        "becoming": self._persisted.get("becoming", _PERSIST_DEFAULT["becoming"]),
        "matters_most": list(self._persisted.get("matters_most", [])),
        "current_focus": self._persisted.get("current_focus", ""),
        "recent_changes": list(self._persisted.get("recent_changes", [])),
        "capability_map": self.capability_map(),
        "known_limits": self.known_limits(),
        "self_confidence": self.self_confidence(),
        "development_state": dict(self._development_state),
    }
