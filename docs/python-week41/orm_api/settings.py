"""Explicit, validated configuration. Never dump the environment or secret values."""

from dataclasses import dataclass, field
import os
from pathlib import Path


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
        object.__setattr__(self, "instance_dir", Path(self.instance_dir).expanduser().resolve())

    @classmethod
    def from_env(cls, environment=None):
        values = os.environ if environment is None else environment
        try:
            ttl = int(values.get("API_TOKEN_TTL", "900"))
            port = int(values.get("API_PORT", "8002"))
        except (ValueError, TypeError):
            raise ValueError("API_TOKEN_TTL and API_PORT must be integers") from None
        secret = values.get("API_JWT_SECRET")
        default = Path(__file__).resolve().parents[1] / "instance"
        return cls(
            instance_dir=Path(values.get("STUDYHUB_INSTANCE_DIR", str(default))),
            environment=values.get("APP_ENV", "development"),
            log_level=values.get("API_LOG_LEVEL", "INFO"),
            token_ttl=ttl,
            port=port,
            jwt_secret=secret.encode("utf-8") if secret is not None else None,
        )
