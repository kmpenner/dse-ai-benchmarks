"""SQLite-backed response cache.

Keys are SHA-256 over a canonical JSON of (kind, model, messages, params).
This makes reruns free, lets interrupted runs resume, and guarantees the
pairwise stage reuses exactly the translations the rubric stage scored.
"""
from __future__ import annotations

import hashlib
import time
import json
import sqlite3
import threading
from pathlib import Path
from typing import Optional


class Cache:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(path), check_same_thread=False)
        self._lock = threading.Lock()
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS cache ("
            "  key TEXT PRIMARY KEY,"
            "  value TEXT NOT NULL,"
            "  created REAL"
            ")"
        )
        self._conn.commit()

    @staticmethod
    def key(**parts) -> str:
        blob = json.dumps(parts, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def get(self, key: str) -> Optional[dict]:
        with self._lock:
            row = self._conn.execute(
                "SELECT value FROM cache WHERE key = ?", (key,)
            ).fetchone()
        return json.loads(row[0]) if row else None

    def put(self, key: str, value: dict) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT OR REPLACE INTO cache (key, value, created) VALUES (?, ?, ?)",
                (key, json.dumps(value, ensure_ascii=False), time.time()),
            )
            self._conn.commit()

    def close(self) -> None:
        self._conn.close()
