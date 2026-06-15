"""
JSON persistence schemas for memory state files.

Purpose: Pydantic models for validating identity, beliefs, purpose, skills, workspace.
Inputs:  raw dict/list JSON payloads
Outputs: validated model instances
Dependencies: pydantic
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class IdentitySchema(BaseModel):
    name: str
    version: str = "2.0"
    level: str = ""
    description: str = ""
    core_traits: List[str] = Field(default_factory=list)
    cycle_count: int = 0
    updates: int = 0
    last_growth: Optional[str] = None
    last_active: Optional[str] = None


class BeliefItem(BaseModel):
    id: int
    text: str
    confidence: float = Field(ge=0.0, le=1.0)
    source: str
    created: Optional[str] = None

    @field_validator("confidence", mode="before")
    @classmethod
    def clamp_confidence(cls, v: Any) -> float:
        val = float(v)
        return min(1.0, max(0.0, val))


class BeliefsSchema(BaseModel):
    beliefs: List[BeliefItem]

    @classmethod
    def from_list(cls, data: list) -> "BeliefsSchema":
        return cls(beliefs=[BeliefItem.model_validate(item) for item in data])


class PurposeSchema(BaseModel):
    statement: str
    refinements: int = 0
    version: int = 1
    last_refinement: Optional[str] = None


class SkillEntry(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    interactions: int = 0
    category: str
    last_practiced: Optional[str] = None

    @field_validator("score", mode="before")
    @classmethod
    def clamp_score(cls, v: Any) -> float:
        val = float(v)
        return min(1.0, max(0.0, val))


class SkillsSchema(BaseModel):
    skills: Dict[str, SkillEntry]

    @classmethod
    def from_dict(cls, data: dict) -> "SkillsSchema":
        return cls(skills={k: SkillEntry.model_validate(v) for k, v in data.items()})


class WorkspaceArtifact(BaseModel):
    name: str
    type: str
    created_at: str


class WorkspaceSchema(BaseModel):
    current_thought: str
    current_goal: str
    current_hypothesis: str
    current_plan: str
    active_priority: int = Field(ge=0, le=100)
    pending_contradictions: int = 0
    unsolved_questions: List[str] = Field(default_factory=list)
    artifacts: List[WorkspaceArtifact] = Field(default_factory=list)
    last_updated: Optional[str] = None


class HabitsSchema(BaseModel):
    patterns: Dict[str, int]

    @classmethod
    def from_dict(cls, data: dict) -> "HabitsSchema":
        return cls(patterns={k: int(v) for k, v in data.items()})


class DevelopmentSchema(BaseModel):
    total_cycles: int = 0
    good_cycles: int = 0
    poor_cycles: int = 0
    avg_confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    growth_events: List[Any] = Field(default_factory=list)


class RelationshipEntry(BaseModel):
    interactions: int = 0
    positive: int = 0


class RelationshipsSchema(BaseModel):
    entities: Dict[str, RelationshipEntry]

    @classmethod
    def from_dict(cls, data: dict) -> "RelationshipsSchema":
        return cls(entities={
            k: RelationshipEntry.model_validate(v) for k, v in data.items()
        })


class TrainingGoalItem(BaseModel):
    skill: str
    current_pct: float
    target_pct: float
    gap_pct: float
    priority: float
    suggested_training: str
    practice_topics: str
    expected_improvement: str
    category: str


class TrainingGoalsSchema(BaseModel):
    goals: List[TrainingGoalItem]

    @classmethod
    def from_list(cls, data: list) -> "TrainingGoalsSchema":
        return cls(goals=[TrainingGoalItem.model_validate(item) for item in data])


class ContradictionItem(BaseModel):
    type: str
    belief_a: str
    belief_b: str
    conflict_score: int = Field(ge=0, le=100)
    reason: str
    status: str
    detected_at: str


class ContradictionsSchema(BaseModel):
    items: List[ContradictionItem]

    @classmethod
    def from_list(cls, data: list) -> "ContradictionsSchema":
        return cls(items=[ContradictionItem.model_validate(item) for item in data])


class MemHierarchySchema(BaseModel):
    semantic_concepts: List[str] = Field(default_factory=list)
    forgotten_count: int = 0
    dream_queue: List[str] = Field(default_factory=list)
    long_term_count: int = 0
    episodic_count: int = 0
