"""ChetnaOS v3 — memory kernel (lazy exports to avoid import cycles)."""
from .working_memory import WorkingMemory
from .episodic_memory import EpisodicMemory
from .semantic_memory import SemanticMemory
from .procedural_memory import ProceduralMemory
from .founder_context import FounderContext
from .source_ranks import COGNITIVE_SOURCE_RANKS
from .memory_item import normalize_memory_item, enrich_search_result

__all__ = [
    "WorkingMemory",
    "EpisodicMemory",
    "SemanticMemory",
    "ProceduralMemory",
    "FounderContext",
    "COGNITIVE_SOURCE_RANKS",
    "normalize_memory_item",
    "enrich_search_result",
    "MemoryStore",
]


def __getattr__(name: str):
    if name == "MemoryStore":
        from .memory_store import MemoryStore
        return MemoryStore
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
