"""Fictional HTTP practice API, bound only to loopback. No internet or real token."""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import Thread
import time
from urllib.parse import parse_qs, urlsplit

PRACTICE_TOKEN = "practice-only-token"  # Public fixture, NOT a real credential.
ITEMS = [
    {"id":1,"title":"Learn HTTP","state":"open","comments":2,"kind":"issue"},
    {"id":2,"title":"Encode params","state":"open","comments":0,"kind":"issue"},
    {"id":3,"title":"Validate JSON","state":"closed","comments":5,"kind":"issue"},
    {"id":4,"title":"Bound retries","state":"open","comments":1,"kind":"pull_request"},
    {"id":5,"title":"Page contracts","state":"closed","comments":3,"kind":"issue"},
    {"id":6,"title":"Publish atomically","state":"open","comments":7,"kind":"issue"},
]


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # Never log request headers, tokens or response bodies.

    def reply(self, status, value=None, headers=None, raw=None):
        body = raw if raw is not None else (b"" if status == 204 else json.dumps(value).encode())
        self.send_response(status)
        self.send_header("Content-Type", "application/json" if raw is None else "text/plain")
        self.send_header("Content-Length", str(len(body)))
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass

    def do_GET(self):
        url = urlsplit(self.path)
        q = parse_qs(url.query)
        self.server.calls[url.path] = self.server.calls.get(url.path, 0) + 1
        if url.path == "/health":
            return self.reply(200, {"service":"practice","ok":True})
        if url.path == "/echo":
            return self.reply(200, {"query":q,"accept":self.headers.get("Accept"),
                                    "user_agent":self.headers.get("User-Agent")})
        if url.path == "/empty":
            return self.reply(204)
        if url.path == "/bad-json":
            return self.reply(200, raw=b"this is not JSON")
        if url.path == "/wrong-shape":
            return self.reply(200, ["not","an","object"])
        if url.path == "/redirect":
            return self.reply(302, {}, {"Location":"/health"})
        if url.path == "/unavailable":
            return self.reply(503, {"error":"temporary"}, {"Retry-After":"0"})
        if url.path == "/flaky" and self.server.calls[url.path] == 1:
            return self.reply(503, {"error":"try again"}, {"Retry-After":"0"})
        if url.path == "/flaky":
            return self.reply(200, {"ok":True})
        if url.path == "/rate" and self.server.calls[url.path] == 1:
            return self.reply(429, {"error":"wait"}, {"Retry-After":"1"})
        if url.path == "/rate":
            return self.reply(200, {"ok":True})
        if url.path == "/slow":
            time.sleep(0.08)
            return self.reply(200, {"ok":True})
        if url.path in ("/items", "/paged"):
            if self.headers.get("Authorization") != "Bearer " + PRACTICE_TOKEN:
                return self.reply(401, {"error":"practice token required"})
            try:
                if url.path == "/paged":
                    page = int(q.get("page", ["1"])[0])
                    if page < 1:
                        raise ValueError
                    offset = (page-1)*2
                else:
                    cursor = q.get("cursor", ["start"])[0]
                    if cursor not in ("start","c2","c4"):
                        raise ValueError
                    offset = {"start":0,"c2":2,"c4":4}[cursor]
            except ValueError:
                return self.reply(400, {"error":"invalid page/cursor"})
            next_cursor = {0:"c2",2:"c4"}.get(offset)
            return self.reply(200, {"items":ITEMS[offset:offset+2],"next_cursor":next_cursor})
        if url.path == "/tasks":
            return self.reply(200, [self.server.tasks[k] for k in sorted(self.server.tasks)])
        return self.reply(404, {"error":"not found"})

    def body(self):
        size = int(self.headers.get("Content-Length", "0"))
        if not 0 <= size <= 4096:
            raise ValueError
        value = json.loads(self.rfile.read(size))
        if not isinstance(value, dict) or not isinstance(value.get("title"), str) or not value["title"].strip():
            raise ValueError
        return value

    def do_POST(self):
        if self.path != "/tasks":
            return self.reply(404, {"error":"not found"})
        try:
            value = self.body()
        except (ValueError, json.JSONDecodeError):
            return self.reply(400, {"error":"nonempty title JSON required"})
        task_id = max(self.server.tasks, default=0)+1
        task = {"id":task_id,"title":value["title"]}
        self.server.tasks[task_id] = task
        return self.reply(201, task, {"Location":"/tasks/"+str(task_id)})

    def do_PUT(self):
        try:
            task_id = int(self.path.removeprefix("/tasks/"))
            value = self.body()
        except (ValueError, json.JSONDecodeError):
            return self.reply(400, {"error":"invalid task"})
        if task_id not in self.server.tasks:
            return self.reply(404, {"error":"not found"})
        self.server.tasks[task_id] = {"id":task_id,"title":value["title"]}
        return self.reply(200, self.server.tasks[task_id])

    def do_DELETE(self):
        try:
            task_id = int(self.path.removeprefix("/tasks/"))
        except ValueError:
            return self.reply(400, {"error":"invalid task"})
        if task_id not in self.server.tasks:
            return self.reply(404, {"error":"not found"})
        del self.server.tasks[task_id]
        return self.reply(204)


@contextmanager
def DemoAPI():
    """Create fresh fictional state and a new loopback port for every drill."""
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    server.tasks = {}
    server.calls = {}
    worker = Thread(target=server.serve_forever, kwargs={"poll_interval":0.01}, daemon=True)
    worker.start()
    try:
        yield "http://127.0.0.1:" + str(server.server_address[1])
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=2)


if __name__ == "__main__":
    with DemoAPI() as base:
        print("Practice API:", base)
        print("Loopback only. Stop with Ctrl+C.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
