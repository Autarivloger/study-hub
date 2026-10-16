import httpx
import pytest
from orm_api.settings import Settings
from orm_api.upstream import UpstreamUnavailable, read_notice

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "values",
    [
        {"API_TOKEN_TTL": "wrong"},
        {"API_TOKEN_TTL": "0"},
        {"API_PORT": "70000"},
        {"API_LOG_LEVEL": "DEBUG"},
        {"APP_ENV": "unknown"},
        {"APP_ENV": "production"},
        {"API_JWT_SECRET": "short"},
    ],
)
def test_invalid_configuration(values):
    with pytest.raises(ValueError):
        Settings.from_env(values)


def test_configured_environment_without_secret_repr(tmp_path):
    settings = Settings.from_env(
        {
            "APP_ENV": "production",
            "API_JWT_SECRET": "fictional-test-key-" * 3,
            "API_TOKEN_TTL": "120",
            "STUDYHUB_INSTANCE_DIR": str(tmp_path),
        }
    )
    assert settings.token_ttl == 120 and settings.instance_dir == tmp_path.resolve()
    assert "fictional-test-key" not in repr(settings)
    assert Settings.from_env({}).port == 8002


def test_mocked_upstream_never_uses_real_network():
    calls = []

    def fake(request):
        calls.append((request.method, request.url.host))
        return httpx.Response(200, json={"message": "Maintenance planned"})

    with httpx.Client(transport=httpx.MockTransport(fake)) as client:
        assert read_notice(client) == "Maintenance planned"
    assert calls == [("GET", "status.example.test")]


@pytest.mark.parametrize("mode", ["timeout", "status", "shape"])
def test_upstream_failure_contract(mode):
    def fake(request):
        if mode == "timeout":
            raise httpx.ReadTimeout("fictional-private-upstream-detail", request=request)
        return httpx.Response(503 if mode == "status" else 200, json={"unexpected": True})

    with httpx.Client(transport=httpx.MockTransport(fake)) as client:
        with pytest.raises(UpstreamUnavailable, match="^Notice unavailable$"):
            read_notice(client)
