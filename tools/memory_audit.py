#!/usr/bin/env python3
"""
Utility script to audit the mem.db store for duplicate or overly similar
embeddings and report the largest stored memories.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

try:
    import numpy as np
except ImportError as exc:  # pragma: no cover - numpy is required here
    raise SystemExit("memory_audit requires numpy to run") from exc


@dataclass
class MemoryRow:
    mem_id: int
    text: str
    meta: Optional[str]
    embedding: Optional[bytes]
    created_at: str

    @property
    def text_length(self) -> int:
        return len(self.text or "")

    @property
    def meta_length(self) -> int:
        return len(self.meta or "")

    @property
    def storage_size(self) -> int:
        """Approximate storage footprint for ranking purposes."""
        embed_size = len(self.embedding) if self.embedding else 0
        return self.text_length + self.meta_length + embed_size


def load_memories(db_path: Path) -> List[MemoryRow]:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            "SELECT id, text, meta, embedding, created_at FROM memories ORDER BY id ASC"
        )
        rows = [
            MemoryRow(
                mem_id=row[0],
                text=row[1] or "",
                meta=row[2],
                embedding=row[3],
                created_at=row[4],
            )
            for row in cursor.fetchall()
        ]
    return rows


def find_duplicate_embeddings(rows: List[MemoryRow]) -> List[List[int]]:
    digest_map = {}
    duplicates = []
    for row in rows:
        if not row.embedding:
            continue
        digest = hashlib.sha1(row.embedding).hexdigest()
        seen = digest_map.setdefault(digest, [])
        seen.append(row.mem_id)
    for mem_ids in digest_map.values():
        if len(mem_ids) > 1:
            duplicates.append(mem_ids)
    return duplicates


def detect_similar_pairs(
    rows: List[MemoryRow],
    threshold: float,
    limit: int,
) -> List[dict]:
    vectors = []
    info = []
    for row in rows:
        if not row.embedding:
            continue
        vec = np.frombuffer(row.embedding, dtype=np.float32)
        norm = np.linalg.norm(vec)
        if norm == 0:
            continue
        vectors.append(vec / norm)
        info.append(row)

    flagged = []
    count = len(info)
    for i in range(count):
        vi = vectors[i]
        for j in range(i + 1, count):
            score = float(np.dot(vi, vectors[j]))
            if score >= threshold:
                flagged.append(
                    {
                        "a_id": info[i].mem_id,
                        "b_id": info[j].mem_id,
                        "similarity": round(score, 4),
                    }
                )
            if len(flagged) >= limit:
                return flagged
    return flagged


def top_largest(rows: List[MemoryRow], top_n: int) -> List[dict]:
    ranking = sorted(rows, key=lambda r: r.storage_size, reverse=True)[:top_n]
    return [
        {
            "id": row.mem_id,
            "chars": row.text_length,
            "meta_bytes": row.meta_length,
            "embedding_bytes": len(row.embedding) if row.embedding else 0,
            "created_at": row.created_at,
            "preview": (row.text or "")[:120].replace("\n", " ") + (
                "..." if len(row.text) > 120 else ""
            ),
        }
        for row in ranking
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit the ChetnaOS memory store")
    parser.add_argument(
        "--db",
        default="mem.db",
        type=Path,
        help="Path to mem.db (defaults to project root mem.db)",
    )
    parser.add_argument("--top", type=int, default=50, help="Top-N largest memories")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.90,
        help="Cosine similarity threshold for duplicate detection",
    )
    parser.add_argument(
        "--max-pairs",
        type=int,
        default=50,
        help="Maximum number of high-similarity pairs to report",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db_path = args.db
    if not db_path.exists():
        raise SystemExit(f"Database not found: {db_path}")

    rows = load_memories(db_path)
    duplicate_sets = find_duplicate_embeddings(rows)
    similar_pairs = detect_similar_pairs(rows, args.threshold, args.max_pairs)
    largest = top_largest(rows, args.top)

    report = {
        "db_path": str(db_path.resolve()),
        "total_memories": len(rows),
        "duplicate_embedding_sets": duplicate_sets,
        "high_similarity_pairs": similar_pairs,
        "largest_entries": largest,
    }
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()

