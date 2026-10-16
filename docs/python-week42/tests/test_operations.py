from io import StringIO
import json
from pathlib import Path
from unittest.mock import Mock
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError
from orm_api import create_app, get_session
from orm_api.settings import Settings
from orm_api.telemetry import database_ready

pytestmark = pytest.mark.integration


def test_readiness_failure_is_generic(client, monkeypatch):
    monkeypatch.setattr("orm_api.database_ready", lambda sessions: False)
    assert client.get("/health/ready").status_code == 503
    assert client.get("/health").status_code == 200
    factory = Mock(side_effect=SQLAlchemyError("fictional-private-database-detail"))
    assert database_ready(factory) is False


def test_error_response_and_logs_do_not_echo_exception(app, client, headers, logs):
    def broken():
        raise RuntimeError("fictional-private-error-canary")

    app.dependency_overrides[get_session] = broken
    try:
        response = client.get("/v1/notes", headers=headers)
        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error"
        assert response.headers["X-Request-ID"] == response.json()["request_id"]
    finally:
        app.dependency_overrides.clear()
    assert "fictional-private-error-canary" not in response.text + logs.getvalue()
    assert json.loads(logs.getvalue().splitlines()[-1])["status"] == 500


def test_persistence_and_configurable_token_lifetime(tmp_path):
    from tests.conftest import PASSWORD

    config = Settings(instance_dir=tmp_path / "persistent", environment="testing", token_ttl=120)
    with TestClient(create_app(settings=config, log_stream=StringIO())) as first:
        first.post("/v1/users", json={"username": "asha", "password": PASSWORD})
        token_response = first.post("/v1/token", data={"username": "asha", "password": PASSWORD})
        assert token_response.json()["expires_in"] == 120
        headers = {"Authorization": "Bearer " + token_response.json()["access_token"]}
        first.post("/v1/notes", headers=headers, json={"title": "Persist", "body": "Restart"})
    with TestClient(create_app(settings=config, log_stream=StringIO())) as second:
        assert second.get("/v1/notes", headers=headers).json()["items"][0]["title"] == "Persist"
    assert Path(config.instance_dir / "signing.key").is_file()
