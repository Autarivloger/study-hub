"""A small local Notes API. Routes use synchronous def for sqlite/hash work."""
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated
import secrets
import sqlite3
import time

import jwt
from fastapi import Depends, FastAPI, HTTPException, Path as PathParam, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from werkzeug.security import check_password_hash, generate_password_hash

from .database import connect, initialise, transaction
from .schemas import NoteCreate, NotePage, NotePatch, NoteRead, NoteReplace, TokenRead, UserCreate, UserRead

ISSUER = "studyhub-w39-local"
AUDIENCE = "studyhub-w39-clients"
TTL = 900
oauth = OAuth2PasswordBearer(tokenUrl="/v1/token", auto_error=False)


def unauthorised():
    return HTTPException(401, "Valid bearer token required", headers={"WWW-Authenticate": "Bearer"})


def get_db(request: Request):
    db = connect(request.app.state.database)
    try:
        yield db
    finally:
        db.close()


Database = Annotated[sqlite3.Connection, Depends(get_db)]


@dataclass(frozen=True)
class Principal:
    id: int
    username: str
    jti: str


def current_user(request: Request, db: Database, token: Annotated[str | None, Depends(oauth)]):
    if token is None or len(token) > 4096:
        raise unauthorised()
    try:
        claims = jwt.decode(token, request.app.state.key, algorithms=["HS256"],
                            issuer=ISSUER, audience=AUDIENCE,
                            options={"require": ["sub", "exp", "iat", "nbf", "jti", "iss", "aud"]})
        if (not isinstance(claims["sub"], str) or not claims["sub"].isascii()
                or not claims["sub"].isdigit() or not isinstance(claims["jti"], str)
                or not 1 <= len(claims["jti"]) <= 100
                or any(type(claims[k]) is not int for k in ("iat", "nbf", "exp"))):
            raise ValueError("Unexpected claim types")
        user_id = int(claims["sub"])
        if user_id <= 0 or claims.get("kind") != "access":
            raise ValueError("Unexpected access claims")
        row = db.execute("""SELECT users.id,users.username FROM token_sessions
            JOIN users ON users.id=token_sessions.user_id
            WHERE jti=? AND user_id=? AND expires_at>?""",
                         (claims["jti"], user_id, int(time.time()))).fetchone()
        if row is None:
            raise ValueError("Revoked or unknown login")
    except (jwt.PyJWTError, ValueError, TypeError, KeyError):
        raise unauthorised() from None
    return Principal(row["id"], row["username"], claims["jti"])


User = Annotated[Principal, Depends(current_user)]
NoteId = Annotated[int, PathParam(gt=0)]


def owned(db, note_id, owner_id):
    row = db.execute("SELECT * FROM notes WHERE id=? AND owner_id=?", (note_id, owner_id)).fetchone()
    if row is None:
        raise HTTPException(404, "Note not found")
    return dict(row)


def create_app(instance_path=None):
    folder = Path(instance_path) if instance_path is not None else Path(__file__).resolve().parents[1] / "instance"

    @asynccontextmanager
    async def lifespan(app):
        app.state.database, app.state.key = initialise(folder)
        app.state.dummy_hash = generate_password_hash(secrets.token_urlsafe(24))
        yield
        # All request connections have already been closed by yield dependencies.

    app = FastAPI(title="Week 39 Local Notes API", version="1.0.0", lifespan=lifespan,
                  docs_url=None, redoc_url=None, openapi_url="/openapi.json")
    assets = Path(__file__).parent / "static"
    app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        # Pydantic's raw error input could contain a password. Return structure only.
        errors = [{"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]} for e in exc.errors()]
        return JSONResponse(status_code=422, content={"detail": errors})

    @app.get("/", include_in_schema=False)
    @app.get("/docs", include_in_schema=False)
    def docs():
        return FileResponse(assets / "index.html")

    @app.get("/health", tags=["health"])
    def health():
        return {"status": "ok"}

    @app.post("/v1/users", response_model=UserRead, status_code=201, tags=["accounts"])
    def register(data: UserCreate, db: Database, response: Response):
        hashed = generate_password_hash(data.password.get_secret_value())
        try:
            with transaction(db):
                cursor = db.execute("INSERT INTO users(username,password_hash) VALUES(?,?)", (data.username, hashed))
                user_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            raise HTTPException(409, "Username unavailable") from None
        response.headers["Location"] = "/v1/me"
        return {"id": user_id, "username": data.username}

    @app.post("/v1/token", response_model=TokenRead, tags=["accounts"])
    def login(request: Request, db: Database, form: Annotated[OAuth2PasswordRequestForm, Depends()]):
        # Bound credential sizes also apply to this form endpoint.
        if not 3 <= len(form.username) <= 32 or not 12 <= len(form.password) <= 128:
            raise unauthorised()
        row = db.execute("SELECT * FROM users WHERE username=?", (form.username.strip().lower(),)).fetchone()
        matched = check_password_hash(row["password_hash"] if row else request.app.state.dummy_hash, form.password)
        if row is None or not matched:
            raise unauthorised()
        now = int(time.time())
        jti = secrets.token_urlsafe(24)
        claims = {"sub": str(row["id"]), "iat": now, "nbf": now, "exp": now + TTL,
                  "jti": jti, "iss": ISSUER, "aud": AUDIENCE, "kind": "access"}
        encoded = jwt.encode(claims, request.app.state.key, algorithm="HS256")
        with transaction(db):
            db.execute("DELETE FROM token_sessions WHERE expires_at<=?", (now,))
            db.execute("INSERT INTO token_sessions(jti,user_id,expires_at) VALUES(?,?,?)", (jti, row["id"], now + TTL))
        return {"access_token": encoded, "token_type": "bearer", "expires_in": TTL}

    @app.get("/v1/me", response_model=UserRead, tags=["accounts"])
    def me(user: User):
        return {"id": user.id, "username": user.username}

    @app.post("/v1/logout", status_code=204, tags=["accounts"])
    def logout(user: User, db: Database):
        with transaction(db):
            db.execute("DELETE FROM token_sessions WHERE jti=? AND user_id=?", (user.jti, user.id))
        return Response(status_code=204)

    @app.get("/v1/notes", response_model=NotePage, tags=["notes"])
    def listing(user: User, db: Database,
                limit: Annotated[int, Query(ge=1, le=50)] = 10,
                offset: Annotated[int, Query(ge=0, le=10000)] = 0,
                q: Annotated[str, Query(max_length=80)] = ""):
        # A read transaction gives count/items one consistent SQLite snapshot.
        with transaction(db):
            args = (user.id, q)
            where = "owner_id=? AND instr(lower(title),lower(?))>0"
            total = db.execute("SELECT count(*) FROM notes WHERE " + where, args).fetchone()[0]
            rows = db.execute("SELECT * FROM notes WHERE " + where + " ORDER BY id LIMIT ? OFFSET ?", (*args, limit, offset)).fetchall()
        return {"total": total, "offset": offset, "limit": limit, "items": [dict(r) for r in rows]}

    @app.post("/v1/notes", response_model=NoteRead, status_code=201, tags=["notes"])
    def create(data: NoteCreate, user: User, db: Database, response: Response):
        with transaction(db):
            cursor = db.execute("INSERT INTO notes(owner_id,title,body,completed,created_at) VALUES(?,?,?,?,?)",
                                (user.id, data.title, data.body, int(data.completed), datetime.now(timezone.utc).isoformat()))
            result = owned(db, cursor.lastrowid, user.id)
        response.headers["Location"] = f"/v1/notes/{result['id']}"
        return result

    @app.get("/v1/notes/{note_id}", response_model=NoteRead, tags=["notes"])
    def read(note_id: NoteId, user: User, db: Database):
        return owned(db, note_id, user.id)

    @app.put("/v1/notes/{note_id}", response_model=NoteRead, tags=["notes"])
    def replace(note_id: NoteId, data: NoteReplace, user: User, db: Database):
        with transaction(db):
            owned(db, note_id, user.id)
            db.execute("UPDATE notes SET title=?,body=?,completed=? WHERE id=? AND owner_id=?",
                       (data.title, data.body, int(data.completed), note_id, user.id))
            result = owned(db, note_id, user.id)
        return result

    @app.patch("/v1/notes/{note_id}", response_model=NoteRead, tags=["notes"])
    def patch(note_id: NoteId, data: NotePatch, user: User, db: Database):
        with transaction(db):
            previous = owned(db, note_id, user.id)
            previous.update(data.model_dump(exclude_unset=True))
            db.execute("UPDATE notes SET title=?,body=?,completed=? WHERE id=? AND owner_id=?",
                       (previous["title"], previous["body"], int(previous["completed"]), note_id, user.id))
            result = owned(db, note_id, user.id)
        return result

    @app.delete("/v1/notes/{note_id}", status_code=204, tags=["notes"])
    def delete(note_id: NoteId, user: User, db: Database):
        with transaction(db):
            owned(db, note_id, user.id)
            db.execute("DELETE FROM notes WHERE id=? AND owner_id=?", (note_id, user.id))
        return Response(status_code=204)

    return app
