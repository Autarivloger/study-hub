"""Each API test owns its files, logs, app and fictional account."""

from io import StringIO
import httpx
import pytest
from fastapi.testclient import TestClient
from orm_api import create_app

PASSWORD = "fictional-learning-passphrase"


@pytest.fixture(autouse=True)
def deny_live_http(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError("Unexpected real HTTP transport; supply a fake")

    async def deny_async(*args, **kwargs):
        raise AssertionError("Unexpected real async HTTP transport; supply a fake")

    monkeypatch.setattr(httpx.HTTPTransport, "handle_request", deny)
    monkeypatch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", deny_async)


@pytest.fixture
def logs():
    return StringIO()


@pytest.fixture
def app(tmp_path, logs):
    return create_app(tmp_path / "instance", log_stream=logs)


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client


@pytest.fixture
def headers(client):
    assert (
        client.post("/v1/users", json={"username": "asha", "password": PASSWORD}).status_code == 201
    )
    result = client.post("/v1/token", data={"username": "asha", "password": PASSWORD})
    assert result.status_code == 200
    return {"Authorization": "Bearer " + result.json()["access_token"]}


@pytest.fixture
def note(client, headers):
    result = client.post(
        "/v1/notes", headers=headers, json={"title": "Private", "body": "Fictional body"}
    )
    assert result.status_code == 201
    return result.headers["Location"]
