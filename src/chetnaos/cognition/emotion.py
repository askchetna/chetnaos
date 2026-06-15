"""
Emotional State — computational affect for tone and risk tolerance.

Purpose: Model valence/arousal from cycle outcomes (not human emotions).
Inputs:  reflection quality, homeostasis stress, attention priority
Outputs: valence, arousal, risk_tolerance, interaction_tone
Dependencies: none (reads signals only)
"""
from __future__ import annotations

from typing import Any, Dict, Optional


class EmotionalState:
  """Computational affect signals — influences tone, not pipeline."""

  def update(
      self,
      *,
      reflection_quality: str = "fair",
      homeostasis_health: str = "healthy",
      attention_priority: str = "NORMAL",
      emotional_cue: bool = False,
      reality_confidence: float = 0.5,
  ) -> Dict[str, Any]:
    quality_valence = {"good": 0.7, "fair": 0.1, "poor": -0.6}.get(reflection_quality, 0.0)
    stress_valence = {"healthy": 0.1, "stressed": -0.3, "critical": -0.7}.get(
        homeostasis_health, 0.0
    )
    self._valence = round(max(-1.0, min(1.0, quality_valence + stress_valence)), 3)

    priority_arousal = {"HIGH": 0.8, "MEDIUM": 0.5, "NORMAL": 0.3}.get(attention_priority, 0.3)
    emotional_arousal = 0.2 if emotional_cue else 0.0
    quality_arousal = 0.4 if reflection_quality == "poor" else 0.1
    self._arousal = round(min(1.0, priority_arousal + emotional_arousal + quality_arousal), 3)

    base_risk = 0.5 + self._valence * 0.2
    confidence_adj = (reality_confidence - 0.5) * 0.3
    self._risk_tolerance = round(max(0.1, min(0.9, base_risk + confidence_adj)), 3)

    self._interaction_tone = self._derive_tone()
    return self.snapshot()

  def _derive_tone(self) -> str:
    if self._valence >= 0.5 and self._arousal < 0.6:
      return "warm_confident"
    if self._valence < -0.3:
      return "cautious_empathetic"
    if self._arousal >= 0.7:
      return "focused_direct"
    return "neutral_clear"

  @property
  def valence(self) -> float:
    return getattr(self, "_valence", 0.0)

  @property
  def arousal(self) -> float:
    return getattr(self, "_arousal", 0.3)

  @property
  def risk_tolerance(self) -> float:
    return getattr(self, "_risk_tolerance", 0.5)

  @property
  def interaction_tone(self) -> str:
    return getattr(self, "_interaction_tone", "neutral_clear")

  def snapshot(self) -> Dict[str, Any]:
    return {
        "valence": self.valence,
        "arousal": self.arousal,
        "risk_tolerance": self.risk_tolerance,
        "interaction_tone": self.interaction_tone,
    }
