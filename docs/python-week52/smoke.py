"""Exercise real owned HTTP processes, restart persistence and a restored snapshot."""

import argparse
import json
import os
import secrets
import socket
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path

import httpx

from capstone.backup import backup_database


@contextmanager
def running_server(database, token, python=None, cwd=None, extra_env=None):
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    env = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    env.update(CAPSTONE_DB=str(Path(database).resolve()), CAPSTONE_TOKEN=token, PYTHONUTF8="1")
    env.update(extra_env or {})
    with tempfile.TemporaryFile(mode="w+b") as log:
        process = subprocess.Popen(
            [
                str(python or sys.executable),
                "-m",
                "uvicorn",
                "capstone.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--log-level",
                "error",
            ],
            cwd=cwd or Path(__file__).resolve().parent,
            env=env,
            stdout=log,
            stderr=log,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        try:
            with httpx.Client(
                base_url=f"http://127.0.0.1:{port}",
                timeout=4,
                headers={"Authorization": "Bearer " + token},
                trust_env=False,
            ) as client:
                for _ in range(100):
                    if process.poll() is not None:
                        log.seek(0)
                        raise RuntimeError(
                            "Owned server failed to start: "
                            + log.read().decode("utf-8", errors="replace")
                        )
                    try:
                        health = client.get("/health")
                        if (
                            health.status_code == 200
                            and health.json().get("service") == "studylog-capstone"
                        ):
                            break
                    except httpx.TransportError:
                        pass
                    time.sleep(0.08)
                else:
                    raise RuntimeError("Owned localhost server did not become healthy")
                yield client
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def verify(output):
    token = secrets.token_urlsafe(24)  # Generated test-only access; never printed or saved.
    with tempfile.TemporaryDirectory(prefix="studylog52-http-") as temporary:
        database, snapshot = Path(temporary) / "live.sqlite", Path(temporary) / "snapshot.sqlite"
        with running_server(database, token) as client:
            entry = {
                "day": "2026-10-19",
                "subject": "Python",
                "minutes": 30,
                "note": "Synthetic smoke fixture",
            }
            response = client.post("/api/sessions", json=entry)
            assert response.status_code == 201
            record = response.json()
            response = client.put(
                f"/api/sessions/{record['id']}", json={**entry, "minutes": 45, "version": 1}
            )
            assert response.status_code == 200 and response.json()["version"] == 2
            assert (
                client.put(
                    f"/api/sessions/{record['id']}", json={**entry, "version": 1}
                ).status_code
                == 409
            )
            assert client.post("/api/sessions", json={**entry, "minutes": True}).status_code == 422
            assert (
                client.get("/api/sessions", headers={"Authorization": "Bearer wrong"}).status_code
                == 401
            )
            assert (
                client.post(
                    "/api/sessions", json=entry, headers={"Origin": "https://other.invalid"}
                ).status_code
                == 403
            )
            assert client.get("/api/summary").json()["minutes"] == 45
        with running_server(database, token) as client:
            assert client.get(f"/api/sessions/{record['id']}").json()["minutes"] == 45
            assert len(client.get("/api/sessions?day=2026-10-19").json()["items"]) == 1
            assert backup_database(database, snapshot)["sessions"] == 1
            assert client.delete(f"/api/sessions/{record['id']}?version=2").status_code == 200
            assert client.get("/api/summary").json()["sessions"] == 0
        with running_server(snapshot, token) as client:
            assert client.get("/api/summary").json()["minutes"] == 45
            assert client.get(f"/api/sessions/{record['id']}").json()["version"] == 2
    report = {
        "network": "owned 127.0.0.1 HTTP",
        "checks": [
            "health",
            "create",
            "update",
            "stale conflict",
            "validation",
            "access denial",
            "cross-origin denial",
            "process restart persistence",
            "date filter",
            "online snapshot",
            "delete",
            "restored snapshot in a fresh process",
        ],
        "public_deployment_verified": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("artifacts/verification.json"))
    arguments = parser.parse_args()
    result = verify(arguments.output)
    print("Verified HTTP, restart and restore checks:", len(result["checks"]))
