import sqlite3
import json
import os
from typing import List, Dict, Optional, Tuple
import numpy as np
from pathlib import Path

# Global cache for embedding model
_embedding_model = None
_embedding_cache: Dict[str, np.ndarray] = {}


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


# LIGHT_MODE / embeddings toggle (kept local to avoid import cycles)
_LIGHT_MODE = _parse_bool(os.getenv("LIGHT_MODE"), default=True)
_EMBEDDINGS_ENABLED = (
    _parse_bool(os.getenv("EMBEDDINGS_ENABLED"), default=not _LIGHT_MODE)
)


def get_embedding_model():
    """Get or create embedding model singleton.

    In LIGHT_MODE or when embeddings are disabled, this becomes a no-op that
    returns None so the rest of the app can continue without vector memory.
    """
    global _embedding_model

    if not _EMBEDDINGS_ENABLED:
        # Hard-disable embeddings for lightweight / Railway-friendly deploys.
        if _embedding_model is None:
            print(
                "[ChetnaOS] Embeddings disabled "
                "(LIGHT_MODE/EMBEDDINGS_ENABLED). Memory will be sparse-only."
            )
            _embedding_model = None
        return _embedding_model

    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer

            _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        except ImportError:
            print(
                "[ChetnaOS] Warning: sentence-transformers not available, "
                "disabling embedding-backed memory."
            )
            _embedding_model = None
        except Exception as e:
            print(f"[ChetnaOS] Error initializing embedding model: {e}")
            _embedding_model = None
    return _embedding_model


def get_embedding(text: str) -> Optional[np.ndarray]:
    """Get embedding for text, with caching and LIGHT_MODE aware fallback."""
    if text in _embedding_cache:
        return _embedding_cache[text]

    model = get_embedding_model()
    if model is None:
        return None

    try:
        embedding = model.encode(text)
        _embedding_cache[text] = embedding
        return embedding
    except Exception as e:
        print(f"[ChetnaOS] Embedding error: {e}")
        return None

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors"""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def _query_terms(query: str) -> List[str]:
    """Tokenize query for sparse recall; drop high-frequency question words."""
    import re
    stop = frozenset({
        "what", "you", "know", "about", "your", "my", "the", "this", "that",
        "how", "when", "where", "who", "why", "can", "could", "would", "should",
        "tell", "give", "have", "has", "had", "are", "was", "were", "will",
        "like", "want", "need", "please", "any", "some", "all", "our", "not",
        "don", "does", "did", "just", "also", "very", "much", "more", "most",
    })
    terms = [t.lower() for t in re.findall(r"\w+", query) if len(t) > 2]
    terms = [t for t in terms if t not in stop]
    return terms or [query.lower().strip()[:80]]


def _sparse_score(text: str, terms: List[str]) -> float:
    """Keyword overlap score in [0, 1] with bonus for distinctive long tokens."""
    if not text or not terms:
        return 0.0
    lower = text.lower()
    hits = sum(1 for t in terms if t in lower)
    base = hits / len(terms)
    bonus = sum(0.12 for t in terms if len(t) >= 5 and t in lower)
    return min(1.0, base + bonus)

class MemoryDB:
    def __init__(self, db_path: str = 'mem.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize SQLite database with memory table"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    meta TEXT,
                    embedding BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    def upsert(self, text: str, meta: Optional[Dict] = None) -> int:
        """Add or update memory entry"""
        embedding = get_embedding(text)
        meta_json = json.dumps(meta) if meta else None
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                INSERT INTO memories (text, meta, embedding)
                VALUES (?, ?, ?)
            ''', (text, meta_json, embedding.tobytes() if embedding is not None else None))
            return cursor.lastrowid
    
    def _sparse_search(self, query: str, k: int = 5) -> List[Dict]:
        """Keyword overlap recall when embeddings are unavailable or empty."""
        terms = _query_terms(query)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id, text, meta FROM memories")
            memories = cursor.fetchall()

        scored: List[Dict] = []
        for mem_id, text, meta_json in memories:
            score = _sparse_score(text or "", terms)
            if score <= 0:
                continue
            scored.append({
                "id": mem_id,
                "text": text,
                "meta": json.loads(meta_json) if meta_json else None,
                "score": float(score),
                "method": "sparse_keyword",
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:k]

    def _vector_search(self, query: str, k: int = 5) -> List[Dict]:
        """Embedding cosine search over rows that have vectors."""
        query_embedding = get_embedding(query)
        if query_embedding is None:
            return []

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT id, text, meta, embedding FROM memories WHERE embedding IS NOT NULL"
            )
            memories = cursor.fetchall()

        similarities: List[Dict] = []
        for mem_id, text, meta_json, embedding_bytes in memories:
            if not embedding_bytes:
                continue
            try:
                embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
                similarity = cosine_similarity(query_embedding, embedding)
                similarities.append({
                    "id": mem_id,
                    "text": text,
                    "meta": json.loads(meta_json) if meta_json else None,
                    "score": float(similarity),
                    "method": "vector_cosine",
                })
            except Exception as e:
                print(f"Error processing memory {mem_id}: {e}")
                continue

        similarities.sort(key=lambda x: x["score"], reverse=True)
        return similarities[:k]

    def search_with_trace(self, query: str, k: int = 5) -> Tuple[List[Dict], Dict]:
        """Search with diagnostic trace for Phase 8F.1 recall investigation."""
        stats = self.statistics()
        trace: Dict = {
            "query": query,
            "embeddings_enabled": _EMBEDDINGS_ENABLED,
            "search_method": None,
            "memories_found": [],
            "memories_selected": [],
            "failure_point": None,
            "db_total": stats.get("total", 0),
            "db_with_embedding": stats.get("with_embedding", 0),
        }

        vector_results = self._vector_search(query, k=k)
        if vector_results:
            trace["search_method"] = "vector_cosine"
            trace["memories_found"] = vector_results
            trace["memories_selected"] = vector_results
            return vector_results, trace

        sparse_results = self._sparse_search(query, k=max(k, 10))
        trace["search_method"] = "sparse_keyword"
        trace["memories_found"] = sparse_results
        selected = sparse_results[:k]
        trace["memories_selected"] = selected

        if not selected:
            if not _EMBEDDINGS_ENABLED:
                trace["failure_point"] = "embeddings_disabled_and_no_keyword_overlap"
            elif stats.get("with_embedding", 0) == 0:
                trace["failure_point"] = "no_embeddings_in_db_and_no_keyword_overlap"
            else:
                trace["failure_point"] = "no_vector_or_keyword_matches"
        elif not _EMBEDDINGS_ENABLED or stats.get("with_embedding", 0) == 0:
            trace["failure_point"] = "recovered_via_sparse_fallback"
        return selected, trace

    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search memories by vector similarity, falling back to sparse keyword recall."""
        results, _ = self.search_with_trace(query, k=k)
        return results

    def recent(self, n: int = 10) -> List[Dict]:
        """Return the most recent memory entries by timestamp (newest first)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT id, text, meta, created_at
                FROM memories
                ORDER BY datetime(created_at) DESC, id DESC
                LIMIT ?
                """,
                (n,),
            )
            rows = cursor.fetchall()

        results = []
        for mem_id, text, meta_json, created_at in rows:
            results.append({
                "id": mem_id,
                "text": text,
                "meta": json.loads(meta_json) if meta_json else None,
                "created_at": created_at,
            })
        return results

    def delete(self, memory_id: int) -> bool:
        """Delete a memory row by id. Returns True if a row was removed."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM memories WHERE id = ?",
                (memory_id,),
            )
            conn.commit()
            return cursor.rowcount > 0

    def statistics(self) -> Dict:
        """Aggregate statistics for the memories table."""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            with_embedding = conn.execute(
                "SELECT COUNT(*) FROM memories WHERE embedding IS NOT NULL"
            ).fetchone()[0]
            oldest = conn.execute(
                "SELECT MIN(created_at) FROM memories"
            ).fetchone()[0]
            newest = conn.execute(
                "SELECT MAX(created_at) FROM memories"
            ).fetchone()[0]
        return {
            "total": total,
            "with_embedding": with_embedding,
            "without_embedding": total - with_embedding,
            "oldest_created_at": oldest,
            "newest_created_at": newest,
            "db_path": self.db_path,
        }


# Global memory instance
memory_db = MemoryDB()
