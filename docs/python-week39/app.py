"""Loopback teaching server. Never enable reload/debug on a public interface."""
import uvicorn
from learning_api import create_app

if __name__ == "__main__":
    uvicorn.run(create_app(), host="127.0.0.1", port=8000, access_log=False)
