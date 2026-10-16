"""Deployment configuration contracts, isolated from any real environment/data."""

from pathlib import Path
import io
import json
import pytest
import yaml
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql
from orm_api.models import Note
from orm_api.settings import Settings, read_secret_file
from healthcheck import healthy
from ops import init_secrets

ROOT = Path(__file__).resolve().parents[1]


def test_secret_initialisation_preserves_existing_files(tmp_path):
    folder = tmp_path / "private"
    assert len(init_secrets(folder)) == 4
    before = {p.name: p.read_bytes() for p in folder.iterdir()}
    assert init_secrets(folder) == []
    assert before == {p.name: p.read_bytes() for p in folder.iterdir()}
    assert all(len(v) == 64 for v in before.values())


def test_file_secrets_are_redacted_and_newlines_consistent(tmp_path):
    path = tmp_path / "secret"
    path.write_bytes(b"x" * 64 + b"\r\n")
    config = Settings.from_env(
        {
            "APP_ENV": "production",
            "API_JWT_SECRET_FILE": str(path),
            "DB_HOST": "db",
            "DB_PASSWORD_FILE": str(path),
            "DB_SSLMODE": "disable",
        }
    )
    assert config.jwt_secret == b"x" * 64
    assert config.database_url.host == "db"
    assert config.database_url.password == "x" * 64
    assert "x" * 64 not in repr(config)


@pytest.mark.parametrize(
    "mapping",
    [
        {"PORT": "no"},
        {"PORT": "0"},
        {"API_JWT_SECRET": "short"},
        {"DATABASE_URL": "not a valid url"},
    ],
)
def test_invalid_configuration_fails_without_values(mapping):
    with pytest.raises(ValueError):
        Settings.from_env(mapping)


def test_provider_url_normalised():
    settings = Settings.from_env(
        {"DATABASE_URL": "postgresql://learner:fictional-only@db/notes?sslmode=require"}
    )
    assert settings.database_url.drivername == "postgresql+psycopg"
    assert settings.database_url.query["sslmode"] == "require"


def test_missing_secret_is_a_generic_error(tmp_path):
    with pytest.raises(ValueError, match="unavailable"):
        read_secret_file(tmp_path / "missing")


def test_conflicting_sources_are_rejected(tmp_path):
    with pytest.raises(ValueError, match="one JWT"):
        Settings.from_env({"API_JWT_SECRET": "x" * 64, "API_JWT_SECRET_FILE": str(tmp_path / "s")})


def test_port_precedence():
    assert Settings.from_env({"PORT": "9001", "API_PORT": "8002"}).port == 9001


def test_postgres_boolean_schema_compiles():
    sql = str(CreateTable(Note.__table__).compile(dialect=postgresql.dialect()))
    assert "BOOLEAN DEFAULT false" in sql
    assert "completed IN (false,true)" in sql


def test_compose_boundaries():
    config = yaml.safe_load((ROOT / "compose.yaml").read_text())
    db, api, migrate = (config["services"][name] for name in ["db", "api", "migrate"])
    assert "ports" not in db and api["ports"] == ["127.0.0.1:8042:8002"]
    assert api["depends_on"]["migrate"]["condition"] == "service_completed_successfully"
    assert api["environment"]["DB_USER"] == "studyhub_runtime"
    assert migrate["environment"]["DB_USER"] == "studyhub_migrator"
    assert "owner_db_password" not in api["secrets"]
    assert api["read_only"] and api["cap_drop"] == ["ALL"]
    assert api["networks"] == ["frontend", "backend"]
    assert db["networks"] == migrate["networks"] == ["backend"]
    assert config["networks"]["backend"]["internal"] is True
    assert not config["networks"]["frontend"].get("internal", False)


def test_image_has_explicit_runtime_surface():
    text = (ROOT / "Dockerfile").read_text()
    assert text.count("FROM ") == 2
    assert text.index("COPY requirements.txt") < text.index("COPY orm_api")
    assert "USER 10001:10001" in text and 'CMD ["python","server.py"]' in text
    assert "COPY . " not in text and "API_JWT_SECRET=" not in text
    ignore = (ROOT / ".dockerignore").read_text().splitlines()
    assert ignore[0] == "**" and "!instance/" not in ignore and "!.secrets/" not in ignore


def test_probe_is_bounded_and_checks_body(monkeypatch):
    monkeypatch.setenv("API_PORT", "8002")
    monkeypatch.delenv("PORT", raising=False)

    def opener(url, timeout):
        assert url == "http://127.0.0.1:8002/health/ready" and timeout == 2
        result = io.StringIO(json.dumps({"status": "ready"}))
        result.status = 200
        return result

    assert healthy(opener)

    def failed(*a, **kw):
        raise OSError("fictional connection failure")

    assert not healthy(failed)
