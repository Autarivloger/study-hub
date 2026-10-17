"""Acceptance checks for the new sprint behaviour, using owned temporary data."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_completion_filter_combines_with_search_and_pagination(client, headers):
    for title, completed in [("API one", False), ("API two", True), ("HTTP", True)]:
        assert (
            client.post(
                "/v1/notes",
                headers=headers,
                json={"title": title, "body": "Practice", "completed": completed},
            ).status_code
            == 201
        )
    page = client.get(
        "/v1/notes", headers=headers, params={"q": "api", "completed": "false", "limit": 1}
    ).json()
    assert page["total"] == 1 and page["items"][0]["title"] == "API one"
    page = client.get("/v1/notes?completed=true&limit=1&offset=1", headers=headers).json()
    assert page["total"] == 2 and page["items"][0]["title"] == "HTTP"
    assert client.get("/v1/notes?completed=banana", headers=headers).status_code == 422


def test_sprint_assets_and_spec_are_local(client):
    page = client.get("/")
    assert page.status_code == 200 and "Study Notes" in page.text
    assert 'id="noteForm"' in page.text and 'id="deleteDialog"' in page.text
    for route in ["/assets/dashboard.css", "/assets/dashboard.js", "/docs"]:
        assert client.get(route).status_code == 200
    assert "Local Notes API" in client.get("/docs").text
    spec = json.loads((ROOT / "spec.json").read_text())
    assert len(spec["stories"]) == 6 and "password recovery" in spec["out_of_scope"]
