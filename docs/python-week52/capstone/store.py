"""Parameterized SQLite persistence; one connection per operation, explicit versions."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .domain import SessionEdit, SessionInput, canonical_day


class NotFound(LookupError):
    """The requested session does not exist."""


class Conflict(ValueError):
    """The caller edited/deleted an older version of a session."""


class Store:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as connection:
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 1):
                raise RuntimeError("Unsupported schema version; back up before a planned migration")
            tables = connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            ).fetchall()
            if version == 0 and tables:
                raise RuntimeError("Refusing to initialize a nonempty unversioned database")
            if version == 0:
                connection.execute(
                    "CREATE TABLE sessions ("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, day TEXT NOT NULL, "
                    "subject TEXT NOT NULL CHECK(length(subject) BETWEEN 1 AND 80), "
                    "minutes INTEGER NOT NULL CHECK(typeof(minutes)='integer' AND minutes BETWEEN 1 AND 1440), "
                    "note TEXT NOT NULL DEFAULT '' CHECK(length(note)<=1000), "
                    "version INTEGER NOT NULL DEFAULT 1 CHECK(version>=1))"
                )
                connection.execute("CREATE INDEX sessions_day_id ON sessions(day DESC,id DESC)")
                connection.execute("PRAGMA user_version=1")
            # Check the existing schema before serving requests; do not silently reset it.
            connection.execute("SELECT id,day,subject,minutes,note,version FROM sessions LIMIT 0")

    @contextmanager
    def connection(self):
        connection = sqlite3.connect(self.path, timeout=3)
        connection.row_factory = sqlite3.Row
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def add(self, entry: SessionInput) -> dict:
        with self.connection() as connection:
            cursor = connection.execute(
                "INSERT INTO sessions(day,subject,minutes,note) VALUES(?,?,?,?)",
                (entry.day, entry.subject, entry.minutes, entry.note),
            )
            return dict(
                connection.execute(
                    "SELECT * FROM sessions WHERE id=?", (cursor.lastrowid,)
                ).fetchone()
            )

    def get(self, session_id: int) -> dict:
        with self.connection() as connection:
            row = connection.execute("SELECT * FROM sessions WHERE id=?", (session_id,)).fetchone()
            if row is None:
                raise NotFound("Session not found")
            return dict(row)

    def list_sessions(self, limit: int = 50, offset: int = 0, day: str | None = None) -> list[dict]:
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
            raise ValueError("limit must be an integer from 1 to 100")
        if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
            raise ValueError("offset must be a nonnegative integer")
        with self.connection() as connection:
            if day is None:
                rows = connection.execute(
                    "SELECT * FROM sessions ORDER BY day DESC,id DESC LIMIT ? OFFSET ?",
                    (limit, offset),
                )
            else:
                rows = connection.execute(
                    "SELECT * FROM sessions WHERE day=? ORDER BY id DESC LIMIT ? OFFSET ?",
                    (canonical_day(day), limit, offset),
                )
            return [dict(row) for row in rows]

    def update(self, session_id: int, entry: SessionEdit) -> dict:
        with self.connection() as connection:
            cursor = connection.execute(
                "UPDATE sessions SET day=?,subject=?,minutes=?,note=?,version=version+1 WHERE id=? AND version=?",
                (entry.day, entry.subject, entry.minutes, entry.note, session_id, entry.version),
            )
            if cursor.rowcount != 1:
                exists = connection.execute(
                    "SELECT 1 FROM sessions WHERE id=?", (session_id,)
                ).fetchone()
                if exists is None:
                    raise NotFound("Session not found")
                raise Conflict("Session changed; reload before editing again")
            return dict(
                connection.execute("SELECT * FROM sessions WHERE id=?", (session_id,)).fetchone()
            )

    def delete(self, session_id: int, version: int) -> None:
        if isinstance(version, bool) or not isinstance(version, int) or version < 1:
            raise ValueError("version must be a positive integer")
        with self.connection() as connection:
            cursor = connection.execute(
                "DELETE FROM sessions WHERE id=? AND version=?", (session_id, version)
            )
            if cursor.rowcount != 1:
                exists = connection.execute(
                    "SELECT 1 FROM sessions WHERE id=?", (session_id,)
                ).fetchone()
                if exists is None:
                    raise NotFound("Session not found")
                raise Conflict("Session changed; reload before deleting")

    def summary(self, day: str | None = None) -> dict:
        clause, parameters = ("", ()) if day is None else (" WHERE day=?", (canonical_day(day),))
        with self.connection() as connection:
            totals = connection.execute(
                "SELECT COUNT(*) AS sessions,COALESCE(SUM(minutes),0) AS minutes FROM sessions"
                + clause,
                parameters,
            ).fetchone()
            groups = connection.execute(
                "SELECT subject,SUM(minutes) AS minutes FROM sessions"
                + clause
                + " GROUP BY subject ORDER BY subject",
                parameters,
            ).fetchall()
            return {**dict(totals), "subjects": [dict(row) for row in groups]}
