import sqlite3
import json
import os
from typing import List, Dict, Optional, Tuple
import numpy as np
from pathlib import Path

# Global cache for embedding model
_embedding_model = None
_embedding_cache = {}

def get_embedding_model():
    """Get or create embedding model singleton"""
    global _embedding_model
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError:
            print("Warning: sentence-transformers not available, memory disabled")
            _embedding_model = None
    return _embedding_model

def get_embedding(text: str) -> Optional[np.ndarray]:
    """Get embedding for text, with caching"""
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
        print(f"Embedding error: {e}")
        return None

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors"""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

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
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search memories by similarity"""
        query_embedding = get_embedding(query)
        if query_embedding is None:
            return []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT id, text, meta, embedding FROM memories')
            memories = cursor.fetchall()
        
        similarities = []
        for mem_id, text, meta_json, embedding_bytes in memories:
            if embedding_bytes is None:
                continue
            
            try:
                embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
                similarity = cosine_similarity(query_embedding, embedding)
                similarities.append({
                    'id': mem_id,
                    'text': text,
                    'meta': json.loads(meta_json) if meta_json else None,
                    'score': float(similarity)
                })
            except Exception as e:
                print(f"Error processing memory {mem_id}: {e}")
                continue
        
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x['score'], reverse=True)
        return similarities[:k]

# Global memory instance
memory_db = MemoryDB()
