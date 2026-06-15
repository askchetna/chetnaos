"""
Compatibility layer — existing import paths remain valid.

Purpose: Document and bridge legacy memory entry points to MemoryStore.
Inputs:  N/A (import-time wiring)
Outputs: re-exports for backward compatibility
Dependencies: memory.db, organism.memory, store
"""
from __future__ import annotations

# Legacy vector store — unchanged import path
from memory.db import MemoryDB, memory_db  # noqa: F401

# Unified facade — preferred for new code
from .store import MemoryStore, get_memory_store

__all__ = [
    "MemoryDB",
    "memory_db",
    "MemoryStore",
    "get_memory_store",
]
