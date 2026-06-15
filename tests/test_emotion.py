"""Tests for EmotionalState — Phase 3c."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class TestEmotionalState(unittest.TestCase):
    def test_good_quality_positive_valence(self):
        from src.chetnaos.cognition.emotion import EmotionalState

        em = EmotionalState()
        snap = em.update(
            reflection_quality="good",
            homeostasis_health="healthy",
            attention_priority="NORMAL",
            reality_confidence=0.8,
        )
        self.assertGreater(snap["valence"], 0)
        self.assertIn(snap["interaction_tone"], (
            "warm_confident", "neutral_clear", "focused_direct",
        ))

    def test_poor_quality_cautious_tone(self):
        from src.chetnaos.cognition.emotion import EmotionalState

        em = EmotionalState()
        snap = em.update(
            reflection_quality="poor",
            homeostasis_health="critical",
            attention_priority="HIGH",
            reality_confidence=0.2,
        )
        self.assertLess(snap["valence"], 0)
        self.assertLess(snap["risk_tolerance"], 0.5)

    def test_computational_properties(self):
        from src.chetnaos.cognition.emotion import EmotionalState

        em = EmotionalState()
        snap = em.update(reflection_quality="fair")
        for key in ("valence", "arousal", "risk_tolerance", "interaction_tone"):
            self.assertIn(key, snap)


if __name__ == "__main__":
    unittest.main()
