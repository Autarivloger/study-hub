import sqlite3
from contextlib import closing

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from capstone.api import create_app
from capstone.backup import backup_database
from capstone.domain import SessionEdit, SessionInput
from capstone.store import Conflict, NotFound, Store


def entry(**changes):
    return SessionInput(day="2026-10-19", subject="Python", minutes=25, **changes)


@pytest.mark.parametrize("minutes", [True, 0, -1, 1441, 2.5, "25"])
def test_strict_minutes(minutes):
    with pytest.raises(ValidationError):
        SessionInput(day="2026-10-19", subject="Python", minutes=minutes)


@pytest.mark.parametrize("day", ["2026-02-29", "2026-13-01", "20261019", "yesterday"])
def test_real_canonical_dates(day):
    with pytest.raises(ValidationError):
        SessionInput(day=day, subject="Python", minutes=25)


def test_subject_note_and_unknown_fields():
    assert SessionInput(day="2024-02-29", subject="  日本語  ", minutes=10).subject == "日本語"
    for field in [{"subject": "  "}, {"subject": "a\nb"}, {"note": "\0"}, {"unexpected": 1}]:
        with pytest.raises(ValidationError):
            SessionInput.model_validate(
                {"day": "2026-10-19", "subject": "Python", "minutes": 25, **field}
            )


def test_crud_restart_and_conflict(tmp_path):
    store = Store(tmp_path / "sessions.sqlite")
    record = store.add(entry())
    changed = store.update(
        record["id"], SessionEdit(day="2026-10-19", subject="Python", minutes=30, version=1)
    )
    assert changed["version"] == 2
    with pytest.raises(Conflict):
        store.update(
            record["id"], SessionEdit(day="2026-10-19", subject="Python", minutes=99, version=1)
        )
    with pytest.raises(Conflict):
        store.delete(record["id"], 1)
    assert Store(store.path).get(record["id"])["minutes"] == 30
    store.delete(record["id"], 2)
    with pytest.raises(NotFound):
        store.get(record["id"])


def test_list_filter_order_and_summary(tmp_path):
    store = Store(tmp_path / "sessions.sqlite")
    for day, subject, minutes in [
        ("2026-10-18", "Python", 20),
        ("2026-10-19", "SQL", 10),
        ("2026-10-19", "Python", 15),
    ]:
        store.add(SessionInput(day=day, subject=subject, minutes=minutes))
    assert [row["id"] for row in store.list_sessions(limit=2)] == [3, 2]
    assert [row["id"] for row in store.list_sessions(limit=2, offset=2)] == [1]
    assert len(store.list_sessions(day="2026-10-18")) == 1
    assert store.summary()["minutes"] == 45
    assert store.summary(day="2026-10-18")["minutes"] == 20
    assert store.summary(day="2026-10-17") == {"sessions": 0, "minutes": 0, "subjects": []}


def test_parameters_and_transaction_rollback(tmp_path):
    store = Store(tmp_path / "sessions.sqlite")
    hostile = "x'); DROP TABLE sessions; --"
    store.add(SessionInput(day="2026-10-19", subject=hostile, minutes=5))
    assert store.summary()["sessions"] == 1
    with pytest.raises(RuntimeError), store.connection() as connection:
        connection.execute(
            "INSERT INTO sessions(day,subject,minutes) VALUES(?,?,?)",
            ("2026-10-19", "rollback", 10),
        )
        raise RuntimeError("simulated operation failure")
    assert store.summary()["sessions"] == 1
    with pytest.raises(sqlite3.IntegrityError), store.connection() as connection:
        connection.execute(
            "INSERT INTO sessions(day,subject,minutes) VALUES(?,?,?)",
            ("2026-10-19", "invalid", -1),
        )


def test_schema_refuses_future_and_unversioned_data(tmp_path):
    path = tmp_path / "future.sqlite"
    with closing(sqlite3.connect(path)) as connection:
        connection.execute("PRAGMA user_version=99")
    with pytest.raises(RuntimeError):
        Store(path)
    other = tmp_path / "unrelated.sqlite"
    with closing(sqlite3.connect(other)) as connection:
        connection.execute("CREATE TABLE precious(value TEXT)")
    with pytest.raises(RuntimeError):
        Store(other)
    with closing(sqlite3.connect(other)) as connection:
        assert connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall() == [("precious",)]


@pytest.mark.parametrize("limit,offset", [(0, 0), (101, 0), (True, 0), (2, -1)])
def test_page_bounds(tmp_path, limit, offset):
    with pytest.raises(ValueError):
        Store(tmp_path / "sessions.sqlite").list_sessions(limit, offset)


def test_api_status_auth_origin_and_ui(tmp_path):
    app = create_app(tmp_path / "sessions.sqlite", token="test-only-access-token")
    with TestClient(app) as client:
        assert client.get("/health").json()["status"] == "ok"
        assert "StudyLog" in client.get("/").text
        assert client.get("/api/sessions").status_code == 401
        client.headers["Authorization"] = "Bearer test-only-access-token"
        payload = {"day": "2026-10-19", "subject": "Python", "minutes": 25}
        record = client.post("/api/sessions", json=payload)
        assert record.status_code == 201
        session_id = record.json()["id"]
        assert (
            client.put(f"/api/sessions/{session_id}", json={**payload, "version": 1}).json()[
                "version"
            ]
            == 2
        )
        assert client.delete(f"/api/sessions/{session_id}?version=1").status_code == 409
        assert client.post("/api/sessions", json={**payload, "minutes": False}).status_code == 422
        assert (
            client.post(
                "/api/sessions", json=payload, headers={"Origin": "https://other.invalid"}
            ).status_code
            == 403
        )
        assert client.get("/api/sessions?limit=101").status_code == 422
        assert client.get("/api/summary?day=not-a-date").status_code == 422
        assert client.get("/api/sessions/999").status_code == 404
        assert client.get("/api/summary").headers["cache-control"] == "no-store"


def test_busy_error_is_generic(tmp_path, monkeypatch):
    app = create_app(tmp_path / "sessions.sqlite")

    def fail(*args):
        raise sqlite3.OperationalError("private database path or SQL detail")

    monkeypatch.setattr(app.state.store, "summary", fail)
    with TestClient(app) as client:
        response = client.get("/api/summary")
        assert response.status_code == 503
        assert "private" not in response.text


def test_backup_restores_old_snapshot(tmp_path):
    store = Store(tmp_path / "live.sqlite")
    record = store.add(entry())
    backup = tmp_path / "backup.sqlite"
    assert backup_database(store.path, backup)["sessions"] == 1
    store.delete(record["id"], 1)
    assert store.summary()["sessions"] == 0
    assert Store(backup).summary()["minutes"] == 25
    with pytest.raises(FileExistsError):
        backup_database(store.path, backup)
    with pytest.raises(ValueError):
        backup_database(store.path, store.path)


def test_backup_failed_replace_cleans_temporary(tmp_path, monkeypatch):
    import capstone.backup as backup_module

    store = Store(tmp_path / "live.sqlite")
    store.add(entry())

    def fail(*args):
        raise PermissionError("simulated replacement failure")

    monkeypatch.setattr(backup_module.os, "replace", fail)
    with pytest.raises(PermissionError):
        backup_database(store.path, tmp_path / "target.sqlite")
    assert not list(tmp_path.glob(".studylog-backup-*.sqlite"))
    assert store.summary()["sessions"] == 1
