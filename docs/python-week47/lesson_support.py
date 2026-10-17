"""Owned loopback server lifetime for executable teaching examples."""

import os
import socket
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path

import httpx

from bundle import save_bundle


@contextmanager
def running_api(bundle):
    root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(prefix="week47-local-api-") as folder:
        folder = Path(folder)
        model_path = folder / "model.json"
        save_bundle(bundle, model_path)
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        log_path = folder / "server.log"
        with log_path.open("w", encoding="utf-8") as log:
            process = subprocess.Popen(
                [
                    sys.executable,
                    str(root / "api.py"),
                    "--bundle",
                    str(model_path),
                    "--port",
                    str(port),
                ],
                cwd=root,
                stdout=log,
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            try:
                with httpx.Client(
                    base_url=f"http://127.0.0.1:{port}", timeout=2, trust_env=False
                ) as client:
                    deadline = time.monotonic() + 30
                    while time.monotonic() < deadline:
                        try:
                            if client.get("/health").status_code == 200:
                                break
                        except httpx.TransportError:
                            pass
                        if process.poll() is not None:
                            raise RuntimeError(log_path.read_text(encoding="utf-8"))
                        time.sleep(0.1)
                    else:
                        raise RuntimeError("Local inference API did not become ready")
                    yield client
            finally:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
