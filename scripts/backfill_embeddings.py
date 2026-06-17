#!/usr/bin/env python3
"""
Backfill NULL embedding vectors in mem.db.

Safe to restart: only updates rows WHERE embedding IS NULL.
Progress logged every 100 rows.

Usage:
  EMBEDDINGS_ENABLED=true python scripts/backfill_embeddings.py
  python scripts/backfill_embeddings.py --db mem.db
"""
from __future__ import annotations

import argparse
import os
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Force embeddings on for this script unless explicitly disabled.
os.environ.setdefault("EMBEDDINGS_ENABLED", "true")


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill mem.db embedding vectors")
    parser.add_argument("--db", default="mem.db", help="Path to SQLite memory DB")
    parser.add_argument("--batch-size", type=int, default=50, help="Commit every N rows")
    parser.add_argument("--log-every", type=int, default=100, help="Progress log interval")
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.is_file():
        print(f"[backfill] ERROR: database not found: {db_path}")
        return 1

    from memory.embedding_config import refresh_embedding_config, get_embeddings_enabled
    from memory.db import get_embedding, reset_embedding_model

    refresh_embedding_config()
    reset_embedding_model()

    if not get_embeddings_enabled():
        print(
            "[backfill] ERROR: EMBEDDINGS_ENABLED is false. "
            "Set EMBEDDINGS_ENABLED=true to run backfill."
        )
        return 1

    conn = sqlite3.connect(db_path)
    pending = conn.execute(
        "SELECT COUNT(*) FROM memories WHERE embedding IS NULL"
    ).fetchone()[0]
    total = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
    already = total - pending

    print(f"[backfill] db={db_path.resolve()}")
    print(f"[backfill] total={total} already_embedded={already} to_backfill={pending}")

    if pending == 0:
        print("[backfill] Nothing to do.")
        return 0

    cursor = conn.execute(
        "SELECT id, text FROM memories WHERE embedding IS NULL ORDER BY id"
    )

    updated = 0
    failed = 0
    started = time.time()

    for row_id, text in cursor:
        if not text:
            failed += 1
            continue
        try:
            vec = get_embedding(text)
            if vec is None:
                print(f"[backfill] WARN: no vector for id={row_id} — is sentence-transformers installed?")
                failed += 1
                continue
            conn.execute(
                "UPDATE memories SET embedding = ? WHERE id = ? AND embedding IS NULL",
                (vec.tobytes(), row_id),
            )
            updated += 1
            if updated % args.batch_size == 0:
                conn.commit()
            if updated % args.log_every == 0:
                elapsed = time.time() - started
                rate = updated / elapsed if elapsed > 0 else 0
                print(
                    f"[backfill] progress updated={updated}/{pending} "
                    f"failed={failed} rate={rate:.1f}/s"
                )
        except Exception as exc:
            print(f"[backfill] ERROR id={row_id}: {exc}")
            failed += 1

    conn.commit()
    conn.close()

    with_emb = sqlite3.connect(db_path).execute(
        "SELECT COUNT(*) FROM memories WHERE embedding IS NOT NULL"
    ).fetchone()[0]
    elapsed = time.time() - started
    print(
        f"[backfill] done updated={updated} failed={failed} "
        f"with_embedding={with_emb}/{total} elapsed={elapsed:.1f}s"
    )
    return 0 if failed == 0 or updated > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
