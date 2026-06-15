"""
Procedural memory facade.

Purpose: Wrap organism.Skills and Habit for learned patterns and competencies.
Inputs:  domain, quality, intent strings
Outputs: skill rankings, habit check results
Dependencies: src.chetnaos.organism.skills.Skills, organism.habit.Habit
"""
from __future__ import annotations

from src.chetnaos.organism.habit import Habit
from src.chetnaos.organism.skills import Skills


class ProceduralMemory:
    """Facade over Skills + Habit — does not duplicate persistence logic."""

    def __init__(self, skills: Skills | None = None, habit: Habit | None = None):
        self._skills = skills or Skills()
        self._habit = habit or Habit()

    def get_skills(self) -> dict:
        return self._skills.get_all()

    def get_ranked_skills(self) -> list:
        return self._skills.get_ranked()

    def practice(self, domain: str, quality: str = "fair"):
        return self._skills.practice(domain, quality)

    def record_habit(self, intent: str, domain: str):
        return self._habit.record(intent, domain)

    def check_habit(self, intent: str, domain: str) -> dict:
        return self._habit.check(intent, domain)

    def get_frequent_habits(self) -> list:
        return self._habit.get_frequent()
