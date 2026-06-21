"""Trust scores for cognitive prompt sources."""

COGNITIVE_SOURCE_RANKS = {
    "founder_context": 0.95,
    "working_memory": 0.80,
    "long_term_memory": 0.65,
    "general_knowledge": 0.25,
}

__all__ = ["COGNITIVE_SOURCE_RANKS"]
