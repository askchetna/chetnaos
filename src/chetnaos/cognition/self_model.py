"""
Self Model — computational model of own capabilities and limits.

Purpose: Track what the organism can/cannot do based on skills and development.
Inputs:  skills dict, development stats, meta-cognition verdicts
Outputs: capability_map, known_limits, self_confidence
Dependencies: none (reads signals only)
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class SelfModel:
  """Explicit self-model distinct from Identity (name/values)."""

  _LIMIT_THRESHOLD = 0.45

  def __init__(self):
    self._capability_map: Dict[str, float] = {}
    self._known_limits: List[str] = []
    self._self_confidence: float = 0.6
    self._development_state: Dict[str, Any] = {}

  def update(
      self,
      *,
      skills: Optional[Dict[str, Any]] = None,
      development: Optional[Dict[str, Any]] = None,
      meta_cognition: Optional[Dict[str, Any]] = None,
      reality_confidence: Optional[float] = None,
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

    return self.snapshot()

  def capability_map(self) -> Dict[str, float]:
    return dict(self._capability_map)

  def known_limits(self) -> List[str]:
    return list(self._known_limits)

  def self_confidence(self) -> float:
    return self._self_confidence

  def snapshot(self) -> Dict[str, Any]:
    return {
        "capability_map": self.capability_map(),
        "known_limits": self.known_limits(),
        "self_confidence": self.self_confidence(),
        "development_state": dict(self._development_state),
    }
