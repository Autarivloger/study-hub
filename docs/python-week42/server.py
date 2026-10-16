"""Container entry point, configurable port, one worker, explicit proxy trust."""

import os
import uvicorn
from orm_api import create_app
from orm_api.settings import Settings


def create_server():
    return create_app(settings=Settings.from_env())


if __name__ == "__main__":
    settings = Settings.from_env()
    host = os.environ.get("API_BIND", "127.0.0.1")
    if host not in {"127.0.0.1", "0.0.0.0"}:
        raise ValueError("API_BIND must be loopback or all container interfaces")
    uvicorn.run(
        "server:create_server",
        factory=True,
        host=host,
        port=settings.port,
        access_log=False,
        proxy_headers=True,
        forwarded_allow_ips="127.0.0.1",
        timeout_graceful_shutdown=15,
    )
