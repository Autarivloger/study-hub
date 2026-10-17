import json
import time
import jwt
import pytest
from sqlalchemy import select
from werkzeug.security import check_password_hash
from orm_api import AUDIENCE, ISSUER
from orm_api.models import User

pytestmark = pytest.mark.integration
PASSWORD = "fictional-learning-passphrase"


def test_public_contract(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/health/ready").json() == {"status": "ready"}
    for path in ["/docs", "/openapi.json", "/assets/style.css", "/assets/explorer.js"]:
        assert client.get(path).status_code == 200
    schema = client.get("/openapi.json").json()
    operations = {(m.upper(), p) for p, methods in schema["paths"].items() for m in methods}
    assert len(operations) == 16
    assert (
        schema["components"]["securitySchemes"]["OAuth2PasswordBearer"]["flows"]["password"][
            "tokenUrl"
        ]
        == "/v1/token"
    )


def test_private_crud(client, headers):
    assert client.get("/v1/me", headers=headers).json() == {"id": 1, "username": "asha"}
    created = client.post("/v1/notes", headers=headers, json={"title": " First ", "body": " Body "})
    assert created.status_code == 201
    data, url = created.json(), created.headers["Location"]
    assert data["title"] == "First" and data["body"] == "Body"
    assert "owner_id" not in data
    assert client.get(url, headers=headers).json() == data
    assert client.patch(url, headers=headers, json={"completed": True}).json()["completed"] is True
    assert (
        client.patch(url, headers=headers, json={"completed": False}).json()["completed"] is False
    )
    replacement = {"title": "Replaced", "body": "All writable fields", "completed": False}
    changed = client.put(url, headers=headers, json=replacement)
    assert changed.status_code == 200 and changed.json()["created_at"] == data["created_at"]
    assert client.put(url, headers=headers, json={"title": "Incomplete"}).status_code == 422
    assert client.get("/v1/notes", headers=headers).json()["total"] == 1
    deleted = client.delete(url, headers=headers)
    assert deleted.status_code == 204 and deleted.content == b""
    assert client.get(url, headers=headers).status_code == 404


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"title": ""},
        {"completed": None},
        {"completed": "false"},
        {"completed": 0},
        {"owner_id": 2},
        {"body": " "},
    ],
)
def test_bad_patch_preserves_data(client, headers, note, payload):
    before = client.get(note, headers=headers).json()
    assert client.patch(note, headers=headers, json=payload).status_code == 422
    assert client.get(note, headers=headers).json() == before


@pytest.mark.parametrize(
    "query", ["limit=0", "limit=51", "limit=wrong", "offset=-1", "offset=10001", "q=" + "x" * 81]
)
def test_query_boundaries(client, headers, query):
    assert client.get("/v1/notes?" + query, headers=headers).status_code == 422


def test_pagination_and_literal_search(client, headers):
    for title in ["HTTP", "100% practice", "under_score"]:
        client.post("/v1/notes", headers=headers, json={"title": title, "body": "Body"})
    page = client.get("/v1/notes?limit=1&offset=1", headers=headers).json()
    assert page["total"] == 3 and page["items"][0]["title"] == "100% practice"
    for q, total in [("%", 1), ("_", 1), ("' OR 1=1 --", 0)]:
        assert client.get("/v1/notes", headers=headers, params={"q": q}).json()["total"] == total
    assert client.get("/v1/notes?offset=100", headers=headers).json()["items"] == []


@pytest.mark.parametrize(
    "method,payload",
    [
        ("GET", None),
        ("DELETE", None),
        ("PATCH", {"title": "Other"}),
        ("PUT", {"title": "Other", "body": "Body", "completed": False}),
    ],
)
def test_other_owner_denied(client, headers, note, method, payload):
    before = client.get(note, headers=headers).json()
    client.post("/v1/users", json={"username": "ben", "password": PASSWORD})
    token = client.post("/v1/token", data={"username": "ben", "password": PASSWORD}).json()[
        "access_token"
    ]
    other = {"Authorization": "Bearer " + token}
    kwargs = {"headers": other}
    if payload is not None:
        kwargs["json"] = payload
    assert client.request(method, note, **kwargs).status_code == 404
    assert client.get("/v1/notes", headers=other).json()["total"] == 0
    assert client.put(note + "/tags", headers=other, json={"names": ["api"]}).status_code == 404
    assert client.get(note + "/tags", headers=other).status_code == 404
    assert client.get(note, headers=headers).json() == before


def test_tags_survive_note_deletion(client, headers, note):
    assert client.put(
        note + "/tags", headers=headers, json={"names": ["python", "api"]}
    ).json() == ["api", "python"]
    assert client.get(note + "/tags", headers=headers).json() == ["api", "python"]
    for names in [["api", "api"], ["missing"]]:
        assert client.put(note + "/tags", headers=headers, json={"names": names}).status_code == 422
    assert client.put(note + "/tags", headers=headers, json={"names": []}).json() == []
    client.delete(note, headers=headers)
    assert client.get("/v1/tags", headers=headers).json() == ["api", "database", "python"]


def test_credentials_hash_conflict_and_errors(app, client, headers):
    with app.state.sessions() as session:
        value = session.scalar(select(User.password_hash).where(User.username == "asha"))
        assert value != PASSWORD and check_password_hash(value, PASSWORD)
    assert (
        client.post("/v1/users", json={"username": "asha", "password": PASSWORD}).status_code == 409
    )
    a = client.post("/v1/token", data={"username": "missing", "password": PASSWORD})
    b = client.post("/v1/token", data={"username": "asha", "password": "fictional-wrong-password"})
    assert a.status_code == b.status_code == 401 and a.json() == b.json()
    marker = "x7Q!z"
    error = client.post("/v1/users", json={"username": "canary", "password": marker})
    assert error.status_code == 422 and marker not in error.text
    assert all(set(e) == {"loc", "msg", "type"} for e in error.json()["detail"])


def test_jwt_policy_expiry_and_logout(app, client, headers):
    encoded = headers["Authorization"].split(" ", 1)[1]
    claims = jwt.decode(
        encoded, app.state.key, algorithms=["HS256"], issuer=ISSUER, audience=AUDIENCE
    )
    for changed in [
        {**claims, "exp": int(time.time()) - 10},
        {**claims, "aud": "wrong"},
        {**claims, "iss": "wrong"},
        {**claims, "jti": "not-issued"},
        {**claims, "sub": "9" * 100},
    ]:
        candidate = jwt.encode(changed, app.state.key, algorithm="HS256")
        assert (
            client.get("/v1/me", headers={"Authorization": "Bearer " + candidate}).status_code
            == 401
        )
    assert client.get("/v1/me", headers={"Authorization": "Bearer malformed"}).status_code == 401
    other_token = client.post("/v1/token", data={"username": "asha", "password": PASSWORD}).json()[
        "access_token"
    ]
    assert client.post("/v1/logout", headers=headers).status_code == 204
    assert client.get("/v1/me", headers=headers).status_code == 401
    assert (
        client.get("/v1/me", headers={"Authorization": "Bearer " + other_token}).status_code == 200
    )


@pytest.mark.parametrize("path", ["/v1/me", "/v1/notes", "/v1/tags", "/internal/metrics"])
def test_protected_paths(client, path):
    response = client.get(path)
    assert response.status_code == 401 and response.headers["WWW-Authenticate"] == "Bearer"


def test_logs_are_structured_and_exclude_sensitive_data(client, headers, logs, note):
    client.get(note, headers=headers, params={"q": "private-query-canary"})
    entries = [json.loads(line) for line in logs.getvalue().splitlines()]
    assert entries and all(e["event"] == "http_request" for e in entries)
    assert all(
        set(e) == {"timestamp", "event", "method", "route", "status", "duration_ms", "request_id"}
        for e in entries
    )
    assert any(e["route"] == "/v1/notes/{note_id}" for e in entries)
    assert PASSWORD not in logs.getvalue() and "private-query-canary" not in logs.getvalue()
    assert (
        headers["Authorization"] not in logs.getvalue() and "Fictional body" not in logs.getvalue()
    )
    assert client.get("/internal/metrics", headers=headers).json()["requests"] >= 1
