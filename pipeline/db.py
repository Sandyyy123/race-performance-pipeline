"""
PostgreSQL storage layer.

Schema is designed so the client can run their own SQL directly. Uses psycopg
when DATABASE_URL is set; otherwise falls back to local SQLite so the demo is
runnable with zero infra. Same schema either way.
"""
from __future__ import annotations

import os
import sqlite3
from typing import Sequence

from .logic_engine import RaceResult

SCHEMA = """
CREATE TABLE IF NOT EXISTS race_results (
    id            INTEGER PRIMARY KEY,
    athlete       TEXT    NOT NULL,
    event         TEXT    NOT NULL,
    race_date     TEXT    NOT NULL,
    time_seconds  REAL    NOT NULL,
    field_size    INTEGER NOT NULL,
    placing       INTEGER NOT NULL,
    UNIQUE(athlete, event, race_date)
);
"""


def connect():
    """Return a DB connection. Real deployments set DATABASE_URL to Supabase/RDS."""
    url = os.getenv("DATABASE_URL")
    if url:
        import psycopg  # type: ignore

        conn = psycopg.connect(url)
        return conn
    conn = sqlite3.connect(os.getenv("SQLITE_PATH", "race_results.db"))
    return conn


def init_db(conn) -> None:
    conn.executescript(SCHEMA) if hasattr(conn, "executescript") else conn.execute(SCHEMA)
    conn.commit()


def upsert_results(conn, results: Sequence[RaceResult]) -> int:
    cur = conn.cursor()
    n = 0
    for r in results:
        cur.execute(
            """INSERT OR IGNORE INTO race_results
               (athlete, event, race_date, time_seconds, field_size, placing)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (r.athlete, r.event, r.date, r.time_seconds, r.field_size, r.placing),
        )
        n += cur.rowcount
    conn.commit()
    return n
