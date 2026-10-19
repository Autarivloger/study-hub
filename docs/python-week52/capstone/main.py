"""Uvicorn import target. Run with --host 127.0.0.1 for the local rehearsal."""

import os
from pathlib import Path

from .api import create_app

token = os.environ.get("CAPSTONE_TOKEN")
if os.environ.get("CAPSTONE_PUBLIC") == "1" and not token:
    raise RuntimeError("Public-mode rehearsal requires an access token")
app = create_app(Path(os.environ.get("CAPSTONE_DB", "data/studylog.sqlite")), token)
