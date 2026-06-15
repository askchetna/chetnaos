# ------------------------------
# Smriti Engine v1.0
# ------------------------------

import sqlite3
from datetime import datetime

class Smriti:
    def __init__(self):
        self.db = "mem.db"
        self._setup()

    def _setup(self):
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS smriti (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                content TEXT,
                timestamp TEXT
            );
        """)
        con.commit()
        con.close()

    def store_event(self, type_, content, ts):
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        cur.execute("INSERT INTO smriti (type, content, timestamp) VALUES (?, ?, ?)",
                    (type_, str(content), str(ts)))
        con.commit()
        con.close()