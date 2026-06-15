"""
ChetnaOS unified memory subsystem.

Purpose: Single MemoryStore facade above all persistence layers.
Dependencies: memory.db (SQLite vector store), organism modules (JSON facades)
"""

from .store import MemoryStore, get_memory_store
from .health import report as memory_health_report
from .locked import LOCKED, MEMORY_ARCHITECTURE_VERSION

__all__ = [
    "MemoryStore",
    "get_memory_store",
    "memory_health_report",
    "LOCKED",
    "MEMORY_ARCHITECTURE_VERSION",
]
