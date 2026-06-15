"""
Episodic memory facade.

Purpose: Wrap organism.Experience for timestamped episode records.
Inputs:  cycle snapshot dicts
Outputs: experience record dicts, jsonl append results
Dependencies: src.chetnaos.organism.experience.Experience
"""
from __future__ import annotations

from src.chetnaos.organism.experience import Experience


class EpisodicMemory:
    """Facade over Experience — does not duplicate persistence logic."""

    def __init__(self, experience: Experience | None = None):
        self._experience = experience or Experience()

    def record(self, cycle_snapshot: dict) -> dict:
        return self._experience.record(cycle_snapshot)
