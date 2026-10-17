"""Small bounded observability; no raw URL, query, body, credential or exception text."""

from collections import Counter
from datetime import datetime, timezone
import json
import logging
import sys
from threading import Lock
from time import perf_counter
from uuid import uuid4
from starlette.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


class Telemetry:
    def __init__(self, stream=None, level="INFO"):
        self.logger = logging.Logger("studyhub.local." + uuid4().hex, level=getattr(logging, level))
        self.logger.propagate = False
        self.logger.addHandler(logging.StreamHandler(sys.stdout if stream is None else stream))
        self.counts = Counter()
        self.lock = Lock()

    def record(self, *, method, route, status, duration_ms, request_id):
        method = (
            method
            if method in {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}
            else "OTHER"
        )
        with self.lock:
            self.counts[(method, route, status)] += 1
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "http_request",
            "method": method,
            "route": route,
            "status": status,
            "duration_ms": round(max(0, duration_ms), 3),
            "request_id": request_id,
        }
        level = logging.ERROR if status >= 500 else logging.INFO
        self.logger.log(level, json.dumps(entry, separators=(",", ":")))

    def snapshot(self):
        with self.lock:
            return {
                "requests": sum(self.counts.values()),
                "server_errors": sum(
                    count for (_, _, status), count in self.counts.items() if status >= 500
                ),
            }


class RequestTelemetry:
    def __init__(self, app, telemetry, clock=perf_counter):
        self.app, self.telemetry, self.clock = app, telemetry, clock

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        started, status, request_id = False, 500, uuid4().hex
        began = self.clock()

        async def wrapped(message):
            nonlocal started, status
            if message["type"] == "http.response.start":
                started, status = True, message["status"]
                message = {
                    **message,
                    "headers": list(message.get("headers", []))
                    + [(b"x-request-id", request_id.encode("ascii"))],
                }
            await send(message)

        try:
            await self.app(scope, receive, wrapped)
        except Exception:
            # A safe public error + correlation id; no raw exception or request content is logged.
            status = 500
            if started:
                raise
            await JSONResponse(
                {"detail": "Internal server error", "request_id": request_id}, status_code=500
            )(scope, receive, wrapped)
        finally:
            route = getattr(scope.get("route"), "path", "unmatched")
            self.telemetry.record(
                method=scope["method"],
                route=route,
                status=status,
                duration_ms=(self.clock() - began) * 1000,
                request_id=request_id,
            )


def database_ready(sessions):
    try:
        with sessions() as session:
            return session.scalar(text("SELECT 1")) == 1
    except SQLAlchemyError:
        return False
