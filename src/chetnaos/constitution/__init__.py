"""
ChetnaOS Constitution — Core principles that govern the organism.
These are immutable at runtime; only founder governance can amend them.
"""
from .mission import MISSION
from .values import VALUES
from .ethics import ETHICS
from .compassion import COMPASSION
from .sovereignty import SOVEREIGNTY
from .founder_governance import FOUNDER_GOVERNANCE

CONSTITUTION = {
    "mission": MISSION,
    "values": VALUES,
    "ethics": ETHICS,
    "compassion": COMPASSION,
    "sovereignty": SOVEREIGNTY,
    "founder_governance": FOUNDER_GOVERNANCE,
}

__all__ = ["CONSTITUTION", "MISSION", "VALUES", "ETHICS",
           "COMPASSION", "SOVEREIGNTY", "FOUNDER_GOVERNANCE"]
