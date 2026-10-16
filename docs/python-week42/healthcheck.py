"""Exit status only. Never print credentials or raw exception details."""

import json
import os
import sys
from urllib.request import urlopen


def healthy(opener=urlopen):
    try:
        port = int(os.environ.get("PORT", os.environ.get("API_PORT", "8002")))
        if not 1 <= port <= 65535:
            return False
        with opener(f"http://127.0.0.1:{port}/health/ready", timeout=2) as response:
            return response.status == 200 and json.load(response) == {"status": "ready"}
    except Exception:
        return False


if __name__ == "__main__":
    sys.exit(0 if healthy() else 1)
