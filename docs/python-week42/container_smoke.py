"""Run only against this lab's owned Compose project and fictional accounts."""

import json
from pathlib import Path
import subprocess
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parent
BASE = "http://127.0.0.1:8042"


def command(*args):
    return subprocess.check_output(
        ["docker", "compose", *args], cwd=ROOT, text=True, stderr=subprocess.PIPE
    ).strip()


def request(path, method="GET", data=None, token=None, form=False):
    headers = {}
    if token:
        headers["Authorization"] = "Bearer " + token
    body = None
    if data is not None:
        body = (urlencode(data) if form else json.dumps(data)).encode()
        headers["Content-Type"] = (
            "application/x-www-form-urlencoded" if form else "application/json"
        )
    try:
        with urlopen(
            Request(BASE + path, data=body, headers=headers, method=method), timeout=5
        ) as response:
            return response.status, json.load(response)
    except HTTPError as error:
        return error.code, json.load(error)


def wait_ready(expected=200):
    for _ in range(40):
        try:
            if request("/health/ready")[0] == expected:
                return
        except OSError:
            pass
        time.sleep(0.5)
    raise AssertionError("Readiness did not reach expected status")


def main():
    wait_ready()
    assert request("/health")[0] == 200
    password = "fictional-container-practice-42"
    assert (
        request("/v1/users", "POST", {"username": "containerlearner", "password": password})[0]
        == 201
    )
    status, data = request(
        "/v1/token", "POST", {"username": "containerlearner", "password": password}, form=True
    )
    assert status == 200
    token = data["access_token"]
    assert (
        request(
            "/v1/notes",
            "POST",
            {"title": "Container persistence", "body": "Fictional CI fixture"},
            token,
        )[0]
        == 201
    )
    assert request("/v1/notes")[0] == 401
    assert request("/v1/notes", token=token)[1]["total"] == 1
    assert command("exec", "-T", "api", "id", "-u") == "10001"
    role = command(
        "exec",
        "-T",
        "db",
        "psql",
        "-U",
        "studyhub_owner",
        "-d",
        "studyhub",
        "-Atc",
        "SELECT rolsuper FROM pg_roles WHERE rolname='studyhub_runtime'",
    )
    assert role == "f"
    allowed = command(
        "exec",
        "-T",
        "db",
        "psql",
        "-U",
        "studyhub_owner",
        "-d",
        "studyhub",
        "-Atc",
        "SELECT has_schema_privilege('studyhub_runtime','public','CREATE')",
    )
    assert allowed == "f"
    contents = command(
        "exec",
        "-T",
        "api",
        "python",
        "-c",
        "from pathlib import Path;print(any(Path('/app').rglob('*.key')) or Path('/app/.secrets').exists())",
    )
    assert contents == "False"
    command("up", "-d", "--no-deps", "--force-recreate", "api")
    wait_ready()
    assert request("/v1/notes", token=token)[1]["total"] == 1
    command("stop", "db")
    wait_ready(503)
    assert request("/health")[0] == 200
    command("start", "db")
    wait_ready()
    assert request("/v1/notes", token=token)[1]["total"] == 1
    command(
        "exec",
        "-T",
        "db",
        "pg_dump",
        "-U",
        "studyhub_owner",
        "-d",
        "studyhub",
        "-Fc",
        "-f",
        "/tmp/week42.dump",
    )
    command(
        "exec",
        "-T",
        "db",
        "createdb",
        "-U",
        "studyhub_owner",
        "-O",
        "studyhub_migrator",
        "studyhub_restore",
    )
    command(
        "exec",
        "-T",
        "db",
        "pg_restore",
        "-U",
        "studyhub_owner",
        "--role",
        "studyhub_migrator",
        "--no-owner",
        "-d",
        "studyhub_restore",
        "/tmp/week42.dump",
    )
    assert (
        command(
            "exec",
            "-T",
            "db",
            "psql",
            "-U",
            "studyhub_owner",
            "-d",
            "studyhub_restore",
            "-Atc",
            "SELECT count(*) FROM notes",
        )
        == "1"
    )
    assert (
        command(
            "exec",
            "-T",
            "db",
            "psql",
            "-U",
            "studyhub_owner",
            "-d",
            "studyhub_restore",
            "-Atc",
            "SELECT version_num FROM alembic_version",
        )
        == "w42_003"
    )
    print(
        "PASS: actual image non-root; PostgreSQL migrations/roles/auth/CRUD; recreate persistence; outage/recovery; backup restored into a separate database."
    )


if __name__ == "__main__":
    main()
