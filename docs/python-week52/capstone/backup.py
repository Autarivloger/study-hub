"""Make and verify a SQLite snapshot at an explicitly chosen separate path."""

import argparse
import os
import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path


def backup_database(source: Path, destination: Path) -> dict:
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if source == destination or not source.is_file():
        raise ValueError("Source must exist and differ from destination")
    if destination.exists():
        raise FileExistsError("Choose a new backup filename")
    destination.parent.mkdir(parents=True, exist_ok=True)
    handle, name = tempfile.mkstemp(
        prefix=".studylog-backup-", suffix=".sqlite", dir=destination.parent
    )
    os.close(handle)
    temporary = Path(name)
    try:
        with (
            closing(sqlite3.connect(source)) as original,
            closing(sqlite3.connect(temporary)) as snapshot,
        ):
            original.backup(snapshot)
            if snapshot.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                raise RuntimeError("Backup integrity check failed")
            rows = snapshot.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        # Connections are closed before replacement, including on Windows.
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)
    return {"sessions": rows, "integrity": "ok", "schema": 1}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    arguments = parser.parse_args()
    print(backup_database(arguments.source, arguments.destination))
