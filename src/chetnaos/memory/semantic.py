"""
Semantic memory facade.

Purpose: Wrap organism.Beliefs and Learning for conceptual knowledge.
Inputs:  reflection/learning dicts, belief text
Outputs: belief lists, lesson extraction results
Dependencies: src.chetnaos.organism.beliefs.Beliefs, organism.learning.Learning
"""
from __future__ import annotations

from src.chetnaos.organism.beliefs import Beliefs
from src.chetnaos.organism.learning import Learning


class SemanticMemory:
    """Facade over Beliefs + Learning — does not duplicate persistence logic."""

    def __init__(self, beliefs: Beliefs | None = None, learning: Learning | None = None):
        self._beliefs = beliefs or Beliefs()
        self._learning = learning or Learning()

    def get_all_beliefs(self) -> list:
        return self._beliefs.get_all()

    def add_belief(self, text: str, confidence: float = 0.6, source: str = "experience"):
        return self._beliefs.add(text, confidence=confidence, source=source)

    def update_beliefs(self, reflection: dict, learning: dict) -> dict:
        return self._beliefs.update(reflection, learning)

    def learn(self, reflection: dict, experience: dict) -> dict:
        return self._learning.learn(reflection, experience)
