"""Cognition layer — executive orchestration and cognitive organs."""

from .executive import ExecutiveController
from .self_model import SelfModel
from .curiosity import CuriosityDrive
from .emotion import EmotionalState
from .goal_manager import GoalManager, GoalType

__all__ = [
    "ExecutiveController",
    "SelfModel",
    "CuriosityDrive",
    "EmotionalState",
    "GoalManager",
    "GoalType",
]
