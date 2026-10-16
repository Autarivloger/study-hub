"""Explicit, validated configuration. Never dump the environment or secret values."""

from dataclasses import dataclass, field
import os
from pathlib import Path
from sqlalchemy import URL, make_url


def read_secret_file(path):
    """Read only an explicitly configured file; never echo its contents."""
    try:
        value = Path(path).read_bytes().rstrip(b"\r\n")
    except OSError:
        raise ValueError("Configured secret file is unavailable") from None
    if not 32 <= len(value) <= 4096:
        raise ValueError("Secret file must contain 32 to 4096 bytes")
    return value


@dataclass(frozen=True)
class Settings:
    instance_dir: Path = field(
        default_factory=lambda: Path(__file__).resolve().parents[1] / "instance"
    )
    environment: str = "development"
    log_level: str = "INFO"
    token_ttl: int = 900
    port: int = 8002
    jwt_secret: bytes | None = field(default=None, repr=False)
    database_url: URL | None = field(default=None, repr=False)

    def __post_init__(self):
        if self.environment not in {"development", "testing", "production"}:
            raise ValueError("APP_ENV must be development, testing or production")
        if self.log_level not in {"INFO", "WARNING", "ERROR"}:
            raise ValueError("API_LOG_LEVEL must be INFO, WARNING or ERROR")
        if type(self.token_ttl) is not int or not 60 <= self.token_ttl <= 3600:
            raise ValueError("API_TOKEN_TTL must be an integer from 60 to 3600")
        if type(self.port) is not int or not 1 <= self.port <= 65535:
            raise ValueError("API_PORT must be a valid port")
        if self.jwt_secret is not None and (
            not isinstance(self.jwt_secret, bytes) or len(self.jwt_secret) < 32
        ):
            raise ValueError("API_JWT_SECRET must contain at least 32 UTF-8 bytes")
        if self.environment == "production" and self.jwt_secret is None:
            raise ValueError("Production mode requires an externally supplied signing secret")
        if self.database_url is not None and (
            not isinstance(self.database_url, URL)
            or self.database_url.drivername != "postgresql+psycopg"
        ):
            raise ValueError("Use a PostgreSQL psycopg URL for the server database")
        object.__setattr__(self, "instance_dir", Path(self.instance_dir).expanduser().resolve())

    @classmethod
    def from_env(cls, environment=None):
        values = os.environ if environment is None else environment
        try:
            ttl = int(values.get("API_TOKEN_TTL", "900"))
            port = int(values.get("PORT", values.get("API_PORT", "8002")))
        except (ValueError, TypeError):
            raise ValueError("API_TOKEN_TTL and API_PORT must be integers") from None
        secret = values.get("API_JWT_SECRET")
        secret_file = values.get("API_JWT_SECRET_FILE")
        if secret is not None and secret_file:
            raise ValueError("Supply one JWT secret source, not both")
        signing = (
            read_secret_file(secret_file)
            if secret_file
            else secret.encode("utf-8")
            if secret is not None
            else None
        )
        url = None
        if values.get("DATABASE_URL"):
            try:
                raw = values["DATABASE_URL"]
                if raw.startswith("postgres://"):
                    raw = "postgresql://" + raw[len("postgres://") :]
                url = make_url(raw)
                if url.drivername == "postgresql":
                    url = url.set(drivername="postgresql+psycopg")
            except Exception:
                raise ValueError("DATABASE_URL is invalid") from None
        elif values.get("DB_HOST"):
            try:
                password = read_secret_file(values["DB_PASSWORD_FILE"]).decode("utf-8")
                port_db = int(values.get("DB_PORT", "5432"))
                if not 1 <= port_db <= 65535:
                    raise ValueError()
                url = URL.create(
                    "postgresql+psycopg",
                    username=values.get("DB_USER", "studyhub"),
                    password=password,
                    host=values["DB_HOST"],
                    port=port_db,
                    database=values.get("DB_NAME", "studyhub"),
                    query={"sslmode": values.get("DB_SSLMODE", "require")},
                )
            except (KeyError, ValueError, UnicodeError):
                raise ValueError("Database host/file configuration is invalid") from None
        default = Path(__file__).resolve().parents[1] / "instance"
        return cls(
            instance_dir=Path(values.get("STUDYHUB_INSTANCE_DIR", str(default))),
            environment=values.get("APP_ENV", "development"),
            log_level=values.get("API_LOG_LEVEL", "INFO"),
            token_ttl=ttl,
            port=port,
            jwt_secret=signing,
            database_url=url,
        )
