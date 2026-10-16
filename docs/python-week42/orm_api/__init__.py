"""SQLAlchemy refactor of the local Notes API. Sync routes own scoped ORM sessions."""

from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated
import secrets
import time

import jwt
from fastapi import Depends, FastAPI, HTTPException, Path as PathParam, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from werkzeug.security import check_password_hash, generate_password_hash

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload
from .database import initialise, atomic
from .models import User as Account, Note, Tag, LoginSession
from .settings import Settings
from .telemetry import RequestTelemetry, Telemetry, database_ready
from .schemas import (
    TagSelection,
    NoteCreate,
    NotePage,
    NotePatch,
    NoteRead,
    NoteReplace,
    TokenRead,
    UserCreate,
    UserRead,
)

ISSUER = "studyhub-w42-local"
AUDIENCE = "studyhub-w42-clients"
TTL = 900
oauth = OAuth2PasswordBearer(tokenUrl="/v1/token", auto_error=False)


def unauthorised():
    return HTTPException(401, "Valid bearer token required", headers={"WWW-Authenticate": "Bearer"})


def get_session(request: Request):
    with request.app.state.sessions() as session:
        yield session


Database = Annotated[Session, Depends(get_session)]


@dataclass(frozen=True)
class Principal:
    id: int
    username: str
    jti: str


def current_user(request: Request, db: Database, token: Annotated[str | None, Depends(oauth)]):
    if token is None or len(token) > 4096:
        raise unauthorised()
    try:
        claims = jwt.decode(
            token,
            request.app.state.key,
            algorithms=["HS256"],
            issuer=ISSUER,
            audience=AUDIENCE,
            options={"require": ["sub", "exp", "iat", "nbf", "jti", "iss", "aud"]},
        )
        if (
            not isinstance(claims["sub"], str)
            or not claims["sub"].isascii()
            or not claims["sub"].isdigit()
            or not isinstance(claims["jti"], str)
            or not 1 <= len(claims["jti"]) <= 100
            or any(type(claims[k]) is not int for k in ("iat", "nbf", "exp"))
        ):
            raise ValueError("Unexpected claim types")
        user_id = int(claims["sub"])
        if not 0 < user_id <= 9223372036854775807 or claims.get("kind") != "access":
            raise ValueError("Unexpected access claims")
        row = db.scalar(
            select(Account)
            .join(LoginSession)
            .where(
                LoginSession.jti == claims["jti"],
                LoginSession.user_id == user_id,
                LoginSession.expires_at > int(time.time()),
            )
        )
        if row is None:
            raise ValueError("Revoked or unknown login")
    except (jwt.PyJWTError, ValueError, TypeError, KeyError):
        raise unauthorised() from None
    return Principal(row.id, row.username, claims["jti"])


User = Annotated[Principal, Depends(current_user)]
NoteId = Annotated[int, PathParam(gt=0)]


def owned(db, note_id, owner_id, *, tags=False):
    query = select(Note).where(Note.id == note_id, Note.owner_id == owner_id)
    if tags:
        query = query.options(selectinload(Note.tags))
    row = db.scalar(query)
    if row is None:
        raise HTTPException(404, "Note not found")
    return row


def note_view(row):
    return {name: getattr(row, name) for name in ("id", "title", "body", "completed", "created_at")}


def create_app(instance_path=None, *, settings=None, log_stream=None):
    if settings is not None and instance_path is not None:
        raise ValueError("Supply settings or instance_path, not both")
    config = settings or (
        Settings(instance_dir=instance_path, environment="testing")
        if instance_path is not None
        else Settings.from_env()
    )
    folder = config.instance_dir

    @asynccontextmanager
    async def lifespan(app):
        engine, sessions, key = initialise(
            folder, database_url=config.database_url, jwt_secret=config.jwt_secret
        )
        app.state.engine, app.state.sessions, app.state.key = (
            engine,
            sessions,
            config.jwt_secret or key,
        )
        try:
            app.state.dummy_hash = generate_password_hash(secrets.token_urlsafe(24))
            yield
        finally:
            engine.dispose()

    app = FastAPI(
        title="Week 42 SQLAlchemy Notes API",
        version="1.0.0",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url="/openapi.json",
    )
    app.state.settings = config
    app.state.telemetry = Telemetry(stream=log_stream, level=config.log_level)
    app.add_middleware(RequestTelemetry, telemetry=app.state.telemetry)
    assets = Path(__file__).parent / "static"
    app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        return JSONResponse(
            status_code=422,
            content={
                "detail": [
                    {"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]}
                    for e in exc.errors()
                ]
            },
        )

    @app.get("/", include_in_schema=False)
    @app.get("/docs", include_in_schema=False)
    def docs():
        return FileResponse(assets / "index.html")

    @app.get("/health", tags=["health"])
    def health():
        return {"status": "ok"}

    @app.get("/health/ready", tags=["health"])
    def ready(response: Response):
        available = database_ready(app.state.sessions)
        response.status_code = 200 if available else 503
        return {"status": "ready" if available else "unavailable"}

    @app.get("/internal/metrics", tags=["health"])
    def metrics(user: User):
        return app.state.telemetry.snapshot()

    @app.post("/v1/users", response_model=UserRead, status_code=201, tags=["accounts"])
    def register(data: UserCreate, db: Database, response: Response):
        row = Account(
            username=data.username,
            password_hash=generate_password_hash(data.password.get_secret_value()),
        )
        try:
            with atomic(db):
                db.add(row)
                db.flush()
                result = {"id": row.id, "username": row.username}
        except IntegrityError:
            raise HTTPException(409, "Username unavailable") from None
        response.headers["Location"] = "/v1/me"
        return result

    @app.post("/v1/token", response_model=TokenRead, tags=["accounts"])
    def login(
        request: Request, db: Database, form: Annotated[OAuth2PasswordRequestForm, Depends()]
    ):
        if not 3 <= len(form.username) <= 32 or not 12 <= len(form.password) <= 128:
            raise unauthorised()
        row = db.scalar(select(Account).where(Account.username == form.username.strip().lower()))
        matched = check_password_hash(
            row.password_hash if row else request.app.state.dummy_hash, form.password
        )
        if row is None or not matched:
            raise unauthorised()
        now = int(time.time())
        jti = secrets.token_urlsafe(24)
        ttl = app.state.settings.token_ttl
        claims = {
            "sub": str(row.id),
            "iat": now,
            "nbf": now,
            "exp": now + ttl,
            "jti": jti,
            "iss": ISSUER,
            "aud": AUDIENCE,
            "kind": "access",
        }
        encoded = jwt.encode(claims, request.app.state.key, algorithm="HS256")
        with atomic(db):
            db.execute(delete(LoginSession).where(LoginSession.expires_at <= now))
            db.add(LoginSession(jti=jti, user_id=row.id, expires_at=now + ttl))
        return {"access_token": encoded, "token_type": "bearer", "expires_in": ttl}

    @app.get("/v1/me", response_model=UserRead, tags=["accounts"])
    def me(user: User):
        return {"id": user.id, "username": user.username}

    @app.post("/v1/logout", status_code=204, tags=["accounts"])
    def logout(user: User, db: Database):
        with atomic(db):
            db.execute(
                delete(LoginSession).where(
                    LoginSession.jti == user.jti, LoginSession.user_id == user.id
                )
            )
        return Response(status_code=204)

    @app.get("/v1/notes", response_model=NotePage, tags=["notes"])
    def listing(
        user: User,
        db: Database,
        limit: Annotated[int, Query(ge=1, le=50)] = 10,
        offset: Annotated[int, Query(ge=0, le=10000)] = 0,
        q: Annotated[str, Query(max_length=80)] = "",
    ):
        predicate = (
            Note.owner_id == user.id,
            func.instr(func.lower(Note.title), func.lower(q)) > 0,
        )
        total = db.scalar(select(func.count()).select_from(Note).where(*predicate))
        rows = db.scalars(
            select(Note).where(*predicate).order_by(Note.id).limit(limit).offset(offset)
        ).all()
        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "items": [note_view(r) for r in rows],
        }

    @app.post("/v1/notes", response_model=NoteRead, status_code=201, tags=["notes"])
    def create(data: NoteCreate, user: User, db: Database, response: Response):
        with atomic(db):
            row = Note(
                **data.model_dump(),
                owner_id=user.id,
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            db.add(row)
            db.flush()
            result = note_view(row)
        response.headers["Location"] = f"/v1/notes/{result['id']}"
        return result

    @app.get("/v1/notes/{note_id}", response_model=NoteRead, tags=["notes"])
    def read(note_id: NoteId, user: User, db: Database):
        return note_view(owned(db, note_id, user.id))

    @app.put("/v1/notes/{note_id}", response_model=NoteRead, tags=["notes"])
    def replace(note_id: NoteId, data: NoteReplace, user: User, db: Database):
        with atomic(db):
            row = owned(db, note_id, user.id)
            for name, value in data.model_dump().items():
                setattr(row, name, value)
            db.flush()
            result = note_view(row)
        return result

    @app.patch("/v1/notes/{note_id}", response_model=NoteRead, tags=["notes"])
    def patch(note_id: NoteId, data: NotePatch, user: User, db: Database):
        with atomic(db):
            row = owned(db, note_id, user.id)
            for name, value in data.model_dump(exclude_unset=True).items():
                setattr(row, name, value)
            db.flush()
            result = note_view(row)
        return result

    @app.delete("/v1/notes/{note_id}", status_code=204, tags=["notes"])
    def remove(note_id: NoteId, user: User, db: Database):
        with atomic(db):
            db.delete(owned(db, note_id, user.id))
        return Response(status_code=204)

    @app.get("/v1/tags", response_model=list[str], tags=["relationships"])
    def tags(user: User, db: Database):
        return list(db.scalars(select(Tag.name).order_by(Tag.name)))

    @app.get("/v1/notes/{note_id}/tags", response_model=list[str], tags=["relationships"])
    def note_tag_list(note_id: NoteId, user: User, db: Database):
        return [t.name for t in owned(db, note_id, user.id, tags=True).tags]

    @app.put("/v1/notes/{note_id}/tags", response_model=list[str], tags=["relationships"])
    def set_tags(note_id: NoteId, data: TagSelection, user: User, db: Database):
        with atomic(db):
            row = owned(db, note_id, user.id, tags=True)
            selected = list(
                db.scalars(select(Tag).where(Tag.name.in_(data.names)).order_by(Tag.name))
            )
            if len(selected) != len(data.names):
                raise HTTPException(409, "Known tag catalog unavailable")
            row.tags = selected
            db.flush()
            result = [t.name for t in row.tags]
        return result

    return app
