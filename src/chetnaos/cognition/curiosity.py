"""
Curiosity Drive — intrinsic exploration from gaps and novelty.

Purpose: Generate exploration goals from unanswered questions and uncertainty.
Inputs:  workspace state, domain, reality confidence, poor-quality flags
Outputs: novelty_score, exploration_goals, next_question
Dependencies: none (reads signals only)
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class CuriosityDrive:
  """Computational curiosity — not human emotion simulation."""

  def __init__(self):
    self._seen_domains: set[str] = set()
    self._last_novelty: float = 0.5
    self._exploration_goals: List[Dict[str, Any]] = []
    self._next_question: Optional[str] = None

  def novelty_score(self, domain: str, workspace_questions: List[str]) -> float:
    domain_novelty = 0.8 if domain not in self._seen_domains else 0.3
    self._seen_domains.add(domain)
    gap_bonus = min(0.4, len(workspace_questions) * 0.1)
    score = min(1.0, domain_novelty + gap_bonus)
    self._last_novelty = round(score, 3)
    return self._last_novelty

  def exploration_goals(
      self,
      *,
      domain: str,
      workspace_questions: Optional[List[str]] = None,
      uncertainty: float = 0.5,
      poor_quality: bool = False,
  ) -> List[Dict[str, Any]]:
    questions = workspace_questions or []
    novelty = self.novelty_score(domain, questions)
    goals: List[Dict[str, Any]] = []

    if questions:
      goals.append({
          "type": "answer_question",
          "target": questions[0],
          "priority": round(0.5 + uncertainty * 0.3, 3),
      })
    if novelty >= 0.6:
      goals.append({
          "type": "explore_domain",
          "target": domain,
          "priority": round(novelty, 3),
      })
    if poor_quality:
      goals.append({
          "type": "improve_quality",
          "target": domain,
          "priority": 0.85,
      })
    if uncertainty >= 0.5:
      goals.append({
          "type": "reduce_uncertainty",
          "target": f"verify claims about {domain}",
          "priority": round(uncertainty, 3),
      })

    goals.sort(key=lambda g: g["priority"], reverse=True)
    self._exploration_goals = goals[:5]
    return list(self._exploration_goals)

  def next_question(self, workspace_questions: Optional[List[str]] = None) -> Optional[str]:
    questions = workspace_questions or []
    self._next_question = questions[0] if questions else None
    return self._next_question

  def snapshot(self) -> Dict[str, Any]:
    return {
        "novelty_score": self._last_novelty,
        "exploration_goals": list(self._exploration_goals),
        "next_question": self._next_question,
        "domains_seen": len(self._seen_domains),
    }
