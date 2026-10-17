"""Loopback teaching server. Never enable reload/debug on a public interface."""

import uvicorn
from orm_api import create_app
from orm_api.settings import Settings

if __name__ == "__main__":
    settings = Settings.from_env()
    uvicorn.run(
        create_app(settings=settings), host="127.0.0.1", port=settings.port, access_log=False
    )
