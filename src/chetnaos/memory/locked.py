"""
Locked memory architecture — Phase 2.5.

DO NOT:
- Create a second MemoryStore or parallel vector kernel
- Move memory/ JSON folder or rename import paths
- Bypass validation on JSON load paths wired in organism modules

SINGLE KERNEL:
- Vector: MemoryStore -> memory.db.MemoryDB -> mem.db
- JSON:   validated load via json_loader -> organism modules
- Facades: episodic, semantic, procedural, working_memory (wrap organism, no duplicate logic)

HEALTH: memory.health.report()
GATE:   python scripts/phase25_gate.py
"""

MEMORY_ARCHITECTURE_VERSION = "2.5"
LOCKED = True
