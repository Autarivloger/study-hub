"""HTTP adapter for the single-owner local capstone; no Study Hub storage access."""

import hmac
import sqlite3
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse

from .domain import SessionEdit, SessionInput
from .store import Conflict, NotFound, Store


def create_app(database: Path, token: str | None = None) -> FastAPI:
    if token is not None and (len(token) < 16 or not token.isascii()):
        raise ValueError("Configured access token must have at least 16 ASCII characters")
    store = Store(database)
    app = FastAPI(title="StudyLog capstone", version="1.0.0", docs_url=None, redoc_url=None)
    app.state.store = store

    @app.middleware("http")
    async def browser_boundary(request: Request, call_next):
        origin = request.headers.get("origin")
        if (
            request.method in {"POST", "PUT", "DELETE", "PATCH"}
            and origin
            and origin.rstrip("/") != str(request.base_url).rstrip("/")
        ):
            return JSONResponse({"detail": "Cross-origin write rejected"}, status_code=403)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        return response

    def authorize(request: Request):
        if token is not None:
            supplied = request.headers.get("authorization", "")
            if not hmac.compare_digest(supplied.encode(), ("Bearer " + token).encode()):
                raise HTTPException(status_code=401, detail="Access token required")

    access = [Depends(authorize)]

    @app.exception_handler(NotFound)
    async def not_found(request, error):
        return JSONResponse({"detail": str(error)}, status_code=404)

    @app.exception_handler(Conflict)
    async def stale_version(request, error):
        return JSONResponse({"detail": str(error)}, status_code=409)

    @app.exception_handler(ValueError)
    async def invalid_value(request, error):
        return JSONResponse({"detail": str(error)}, status_code=422)

    @app.exception_handler(sqlite3.OperationalError)
    async def database_unavailable(request, error):
        return JSONResponse(
            {"detail": "Database unavailable; retry or check server logs"}, status_code=503
        )

    @app.get("/", response_class=HTMLResponse)
    def home():
        return (Path(__file__).parent / "static/index.html").read_text(encoding="utf-8")

    @app.get("/health")
    def health():
        store.summary()
        return {"status": "ok", "service": "studylog-capstone", "schema": 1}

    @app.get("/api/sessions", dependencies=access)
    def list_sessions(
        limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0), day: str | None = None
    ):
        return {"items": store.list_sessions(limit, offset, day), "limit": limit, "offset": offset}

    @app.get("/api/sessions/{session_id}", dependencies=access)
    def get_session(session_id: int):
        return store.get(session_id)

    @app.post("/api/sessions", status_code=201, dependencies=access)
    def add_session(entry: SessionInput):
        return store.add(entry)

    @app.put("/api/sessions/{session_id}", dependencies=access)
    def update_session(session_id: int, entry: SessionEdit):
        return store.update(session_id, entry)

    @app.delete("/api/sessions/{session_id}", dependencies=access)
    def delete_session(session_id: int, version: int = Query(..., ge=1)):
        store.delete(session_id, version)
        return {"deleted": session_id}

    @app.get("/api/summary", dependencies=access)
    def summary(day: str | None = None):
        return store.summary(day)

    return app
