"""Explicit connection/transaction lifetime, parameter binding and schema ownership."""
from contextlib import contextmanager
from pathlib import Path
import secrets
import sqlite3

SCHEMA = """
BEGIN IMMEDIATE;
CREATE TABLE users (
 id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE,
 password_hash TEXT NOT NULL
);
CREATE TABLE notes (
 id INTEGER PRIMARY KEY, owner_id INTEGER NOT NULL REFERENCES users(id),
 title TEXT NOT NULL CHECK(length(trim(title)) BETWEEN 1 AND 100),
 body TEXT NOT NULL CHECK(length(trim(body)) BETWEEN 1 AND 2000),
 completed INTEGER NOT NULL DEFAULT 0 CHECK(completed IN (0,1)),
 created_at TEXT NOT NULL
);
CREATE INDEX notes_owner_id ON notes(owner_id,id);
CREATE TABLE token_sessions (
 jti TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id),
 expires_at INTEGER NOT NULL
);
PRAGMA user_version=1;
COMMIT;
"""
EXPECTED = {
    "users": {"id", "username", "password_hash"},
    "notes": {"id", "owner_id", "title", "body", "completed", "created_at"},
    "token_sessions": {"jti", "user_id", "expires_at"},
}


def connect(path):
    # Each yielded connection belongs to one request, never a shared global.
    db = sqlite3.connect(Path(path).resolve().as_uri() + "?mode=rw", uri=True,
                         isolation_level=None, check_same_thread=False, timeout=3)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    return db


def initialise(folder):
    folder = Path(folder).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "notes.sqlite"
    created = False
    try:
        with path.open("xb"):
            created = True
    except FileExistsError:
        pass
    db = connect(path)
    try:
        if created:
            db.executescript(SCHEMA)
        names = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        version = db.execute("PRAGMA user_version").fetchone()[0]
        if names != set(EXPECTED) or version != 1:
            raise RuntimeError("Unknown database schema; no reset or automatic migration attempted")
        for table, columns in EXPECTED.items():
            # table identifiers come only from our fixed source mapping.
            if {r[1] for r in db.execute(f"PRAGMA table_info({table})")} != columns:
                raise RuntimeError("Unexpected database columns; preserve the file and review a migration")
    except Exception:
        db.close()
        if created:
            path.unlink(missing_ok=True)
        raise
    else:
        db.close()
    key_path = folder / "signing.key"
    try:
        with key_path.open("xb") as file:
            file.write(secrets.token_bytes(32))
    except FileExistsError:
        pass
    key = key_path.read_bytes()
    if len(key) != 32:
        raise RuntimeError("Invalid signing key; preserve runtime files and investigate")
    return path, key


@contextmanager
def transaction(db):
    db.execute("BEGIN IMMEDIATE")
    try:
        yield db
        db.commit()
    except BaseException:
        if db.in_transaction:
            db.rollback()
        raise
