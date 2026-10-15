"""Disposable public fixtures; never read a learner's local runtime folder."""
from contextlib import contextmanager
from tempfile import TemporaryDirectory
from fastapi.testclient import TestClient
from learning_api import create_app

PRACTICE_PASSWORD = "fictional-learning-passphrase"


def register(client, username="asha"):
    return client.post("/v1/users", json={"username": username, "password": PRACTICE_PASSWORD})


def login(client, username="asha"):
    response = client.post("/v1/token", data={"username": username, "password": PRACTICE_PASSWORD})
    assert response.status_code == 200
    return {"Authorization": "Bearer " + response.json()["access_token"]}


@contextmanager
def practice(seed=True):
    with TemporaryDirectory(prefix="studyhub-w39-practice-") as folder:
        app = create_app(folder)
        with TestClient(app) as client:
            headers = {}
            if seed:
                register(client, "asha")
                register(client, "ben")
                headers = login(client)
                for title in ("HTTP", "Validation", "100% practice"):
                    result = client.post("/v1/notes", headers=headers, json={"title": title, "body": "Fictional learning note"})
                    assert result.status_code == 201
            yield app, client, headers
