"""
Memory Hierarchy — Models distinct memory types like a cognitive organism.

Working Memory:   Last 5 active interactions (volatile)
Long-Term Memory: Persistent experiences (jsonl store)
Semantic Memory:  Concepts and domains learned
Episodic Memory:  Specific timestamped events
Forgotten Memory: Items dropped during sleep consolidation
Dream Queue:      Unresolved items awaiting consolidation
"""
import json, os
from datetime import datetime

from src.chetnaos.memory.json_loader import load_mem_hierarchy, save_json, memory_path

MEM_STATE_FILE = os.path.join(os.path.dirname(__file__), "../../..", "memory", "mem_hierarchy.json")
EXP_FILE       = os.path.join(os.path.dirname(__file__), "../../..", "memory", "experiences.jsonl")

_MEM_H_DEFAULT = {
    "semantic_concepts": [],
    "forgotten_count":   0,
    "dream_queue":       [],
    "long_term_count":   0,
    "episodic_count":    0,
}


class MemoryHierarchy:
    def __init__(self):
        self._state   = self._load()
        self._working = []  # in-process, not persisted

    def _load(self) -> dict:
        return load_mem_hierarchy(dict(_MEM_H_DEFAULT))

    def _save(self):
        save_json(memory_path("mem_hierarchy.json"), self._state)

    def push_working(self, item: dict):
        """Add to working memory (volatile, max 5)."""
        self._working.insert(0, item)
        self._working = self._working[:5]

    def add_semantic(self, concept: str):
        concepts = self._state.get("semantic_concepts", [])
        if concept not in concepts:
            concepts.insert(0, concept)
        self._state["semantic_concepts"] = concepts[:30]
        self._save()

    def add_dream(self, item: str):
        dq = self._state.get("dream_queue", [])
        if item not in dq:
            dq.append(item)
        self._state["dream_queue"] = dq[:8]
        self._save()

    def record_forgetting(self, count: int):
        self._state["forgotten_count"] = self._state.get("forgotten_count", 0) + count
        self._save()

    def sync_counts(self):
        """Count actual experiences from jsonl file."""
        try:
            p = os.path.abspath(EXP_FILE)
            if os.path.exists(p):
                with open(p) as f:
                    lines = [l for l in f if l.strip()]
                self._state["long_term_count"] = len(lines)
                self._state["episodic_count"]  = min(len(lines), max(0, len(lines) - 3))
        except Exception:
            pass
        self._save()

    def snapshot(self) -> dict:
        self.sync_counts()
        return {
            "working_memory":   self._working[:5],
            "working_count":    len(self._working),
            "long_term_count":  self._state.get("long_term_count", 0),
            "semantic_count":   len(self._state.get("semantic_concepts", [])),
            "semantic_concepts": self._state.get("semantic_concepts", [])[:8],
            "episodic_count":   self._state.get("episodic_count", 0),
            "forgotten_count":  self._state.get("forgotten_count", 0),
            "dream_queue":      self._state.get("dream_queue", []),
            "dream_count":      len(self._state.get("dream_queue", [])),
        }
