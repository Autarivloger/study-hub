"""Disposable public fixtures; never read a learner's local runtime folder."""

from contextlib import contextmanager
from tempfile import TemporaryDirectory
from io import StringIO
from fastapi.testclient import TestClient
from orm_api import create_app
from orm_api.database import initialise
from orm_api.models import User, Note, Tag
from sqlalchemy import event, select

PRACTICE_PASSWORD = "fictional-learning-passphrase"


def run_checks(source):
    """Run authored lesson tests in a subprocess; this is not an untrusted-code sandbox."""
    import os
    from pathlib import Path
    import subprocess
    import sys
    from xml.etree import ElementTree

    with TemporaryDirectory(prefix="studyhub-w43-pytest-") as folder:
        path = Path(folder)
        (path / "test_lesson.py").write_text(source, encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-m",
                "pytest",
                "-q",
                "-p",
                "no:cacheprovider",
                "--junitxml=result.xml",
            ],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=30,
            env={
                **os.environ,
                "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONPATH": str(Path(__file__).resolve().parent),
            },
        )
        if result.returncode not in {0, 1}:
            raise RuntimeError(
                "Lesson pytest collection/environment failed: " + result.stdout[-1500:]
            )
        root = ElementTree.parse(path / "result.xml").getroot()
        suites = list(root.iter("testsuite"))

        def count(key):
            return sum(int(s.get(key, 0)) for s in suites)

        total, failures, errors, skipped = (
            count(k) for k in ["tests", "failures", "errors", "skipped"]
        )
        return {
            "passed": total - failures - errors - skipped,
            "failed": failures,
            "errors": errors,
            "skipped": skipped,
            "exit_code": result.returncode,
        }


def register(client, username="asha"):
    return client.post("/v1/users", json={"username": username, "password": PRACTICE_PASSWORD})


def login(client, username="asha"):
    response = client.post("/v1/token", data={"username": username, "password": PRACTICE_PASSWORD})
    assert response.status_code == 200
    return {"Authorization": "Bearer " + response.json()["access_token"]}


@contextmanager
def practice(seed=True):
    with TemporaryDirectory(prefix="studyhub-w43-practice-") as folder:
        stream = StringIO()
        app = create_app(folder, log_stream=stream)
        app.state.lesson_logs = stream
        with TestClient(app) as client:
            headers = {}
            if seed:
                register(client, "asha")
                register(client, "ben")
                headers = login(client)
                for title in ("HTTP", "Validation", "100% practice"):
                    result = client.post(
                        "/v1/notes",
                        headers=headers,
                        json={"title": title, "body": "Fictional learning note"},
                    )
                    assert result.status_code == 201
            yield app, client, headers


@contextmanager
def sandbox(seed=True):
    """Direct ORM experiments without HTTP/password work; every file is temporary."""
    with TemporaryDirectory(prefix="studyhub-w43-orm-") as folder:
        engine, sessions, _ = initialise(folder)
        try:
            if seed:
                with sessions.begin() as session:
                    a = User(username="asha", password_hash="fictional-not-a-login-verifier")
                    b = User(username="ben", password_hash="fictional-not-a-login-verifier")
                    c = User(username="chen", password_hash="fictional-not-a-login-verifier")
                    session.add_all([a, b, c])
                    session.flush()
                    python = session.scalar(select(Tag).where(Tag.name == "python"))
                    api = session.scalar(select(Tag).where(Tag.name == "api"))
                    session.add_all(
                        [
                            Note(
                                owner=a,
                                title="HTTP",
                                body="Request boundaries",
                                completed=False,
                                created_at="2026-01-01",
                                tags=[api, python],
                            ),
                            Note(
                                owner=a,
                                title="Models",
                                body="Explicit contracts",
                                completed=True,
                                created_at="2026-01-02",
                                tags=[python],
                            ),
                            Note(
                                owner=b,
                                title="Transactions",
                                body="Atomic writes",
                                completed=False,
                                created_at="2026-01-03",
                            ),
                            Note(
                                owner=b,
                                title="Indexes",
                                body="Measured plans",
                                completed=False,
                                created_at="2026-01-04",
                            ),
                        ]
                    )
            yield engine, sessions
        finally:
            engine.dispose()


@contextmanager
def query_counter(engine):
    """Count SELECTs only; never record SQL parameters or account credentials."""
    counts = {"selects": 0}

    def count(connection, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith("SELECT"):
            counts["selects"] += 1

    event.listen(engine, "before_cursor_execute", count)
    try:
        yield counts
    finally:
        event.remove(engine, "before_cursor_execute", count)


def index_experiment():
    """Measure one real query before/after an index on an isolated 20,000-row table."""
    from statistics import median
    from time import perf_counter
    from sqlalchemy import text
    from orm_api.database import make_engine
    from pathlib import Path

    with TemporaryDirectory(prefix="studyhub-w43-index-") as folder:
        engine = make_engine(Path(folder) / "benchmark.sqlite")
        try:
            with engine.begin() as c:
                c.exec_driver_sql(
                    "CREATE TABLE measurements(id INTEGER PRIMARY KEY,owner INTEGER NOT NULL,done INTEGER NOT NULL)"
                )
                c.execute(
                    text("INSERT INTO measurements(id,owner,done) VALUES(:id,:owner,:done)"),
                    [{"id": i, "owner": i % 100, "done": (i // 100) % 2} for i in range(1, 20001)],
                )
            sql = (
                "SELECT id FROM measurements WHERE owner=:owner AND done=:done ORDER BY id LIMIT 20"
            )
            params = {"owner": 7, "done": 0}

            def sample(c):
                timings = []
                for _ in range(7):
                    start = perf_counter()
                    rows = c.execute(text(sql), params).scalars().all()
                    timings.append((perf_counter() - start) * 1000)
                return median(timings), rows

            with engine.begin() as c:
                before_plan = c.execute(text("EXPLAIN QUERY PLAN " + sql), params).all()
                before_ms, before = sample(c)
                c.exec_driver_sql(
                    "CREATE INDEX ix_measurements_owner_done_id ON measurements(owner,done,id)"
                )
                after_plan = c.execute(text("EXPLAIN QUERY PLAN " + sql), params).all()
                after_ms, after = sample(c)
            assert before == after
            return {
                "before_ms": before_ms,
                "after_ms": after_ms,
                "rows": len(after),
                "same_rows": before == after,
                "before_scan": any("SCAN measurements" in row[-1] for row in before_plan),
                "after_index": any(
                    "ix_measurements_owner_done_id" in row[-1] for row in after_plan
                ),
            }
        finally:
            engine.dispose()
