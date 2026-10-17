"""Explicit HTTP-client dependency: teaching tests provide MockTransport, never live internet."""

import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError


class Notice(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    message: str = Field(min_length=1, max_length=200)


class UpstreamUnavailable(Exception):
    pass


def read_notice(client: httpx.Client) -> str:
    try:
        response = client.get("https://status.example.test/notice", timeout=2)
        response.raise_for_status()
        return Notice.model_validate(response.json()).message
    except (httpx.HTTPError, ValueError, ValidationError):
        raise UpstreamUnavailable("Notice unavailable") from None
