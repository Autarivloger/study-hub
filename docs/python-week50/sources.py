"""Owned loopback HTTP fixture: no external services, credentials or user data."""

import json
import threading
import time
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


class SourceState:
    def __init__(self):
        self.lock = threading.Lock()
        self.active = self.peak = self.requests = 0

    def snapshot(self):
        with self.lock:
            return {"active": self.active, "peak": self.peak, "requests": self.requests}


@contextmanager
def local_sources(*, delay=0.025, fail_ids=(), malformed_ids=(), slow_ids=()):
    if not 0 <= delay <= 0.1:
        raise ValueError("fixture delay must be between 0 and 0.1 seconds")
    failures, malformed, slow = map(frozenset, [fail_ids, malformed_ids, slow_ids])
    state = SourceState()

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.0"

        def log_message(self, *args):
            pass

        def do_GET(self):
            path = urlsplit(self.path).path
            try:
                if not path.startswith("/item/"):
                    raise ValueError
                identifier = int(path.removeprefix("/item/"))
                if not 0 <= identifier < 1000:
                    raise ValueError
            except ValueError:
                self.send_error(404)
                return
            with state.lock:
                state.active += 1
                state.requests += 1
                state.peak = max(state.peak, state.active)
            try:
                time.sleep(0.2 if identifier in slow else delay)
                status = 503 if identifier in failures else 200
                body = {"id": identifier, "value": identifier * 17 + 5}
                raw = b"not-json" if identifier in malformed else json.dumps(body).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.send_header("Connection", "close")
                self.end_headers()
                self.wfile.write(raw)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass  # Expected when an owned client times out or is cancelled.
            finally:
                with state.lock:
                    state.active -= 1

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = False
    server.block_on_close = True
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.02})
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", state
    finally:
        server.shutdown()
        thread.join(timeout=3)
        server.server_close()
        if thread.is_alive():
            raise RuntimeError("Owned fixture server did not stop")
