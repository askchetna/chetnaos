"""
State Machine — Manages transitions between cognitive cycle stages.
"""
from enum import Enum
from typing import Optional


class CycleStage(str, Enum):
    EXIST           = "EXIST"
    PURPOSE         = "PURPOSE"
    OBSERVE         = "OBSERVE"
    ATTEND          = "ATTEND"
    RECALL          = "RECALL"
    PREDICT         = "PREDICT"
    IMAGINE         = "IMAGINE"
    PLAY            = "PLAY"
    PLAN            = "PLAN"
    DECIDE          = "DECIDE"
    ACT             = "ACT"
    HABIT           = "HABIT"
    WORLD_UPDATE    = "WORLD_UPDATE"
    EXPERIENCE      = "EXPERIENCE"
    REALITY_CHECK   = "REALITY_CHECK"
    EVALUATE        = "EVALUATE"
    FAILURE_RECOVERY = "FAILURE_RECOVERY"
    REFLECT         = "REFLECT"
    SELF_QUESTION   = "SELF_QUESTION"
    UPDATE_BELIEFS  = "UPDATE_BELIEFS"
    UPDATE_IDENTITY = "UPDATE_IDENTITY"
    REFINE_PURPOSE  = "REFINE_PURPOSE"
    SLEEP           = "SLEEP"
    FORGET          = "FORGET"
    CONSOLIDATE     = "CONSOLIDATE"
    WAKE            = "WAKE"


STAGE_ORDER = list(CycleStage)


class StateMachine:
    def __init__(self):
        self._current: CycleStage = CycleStage.EXIST
        self._history: list[str]  = []
        self._cycle_count: int    = 0

    @property
    def current(self) -> CycleStage:
        return self._current

    @property
    def cycle_count(self) -> int:
        return self._cycle_count

    def advance(self, to: CycleStage):
        self._history.append(self._current.value)
        self._current = to
        if to == CycleStage.WAKE:
            self._cycle_count += 1

    def complete_cycle(self):
        self._cycle_count += 1
        self._history.append(self._current.value)
        self._current = CycleStage.EXIST

    def trace(self) -> list[str]:
        return list(self._history[-30:])

    def summary(self) -> dict:
        return {
            "current":     self._current.value,
            "cycle_count": self._cycle_count,
            "last_stages": self._history[-5:],
        }
