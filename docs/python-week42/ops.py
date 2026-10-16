"""Local author-owned operations; outputs never include secret contents."""

import argparse
import os
from pathlib import Path
import secrets


def init_secrets(folder=Path(".secrets")):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    if os.name == "posix":
        folder.chmod(0o700)
    created = []
    for name in ("owner_db_password", "runtime_db_password", "migration_db_password", "jwt_secret"):
        path = folder / name
        try:
            with path.open("xb") as stream:
                stream.write(secrets.token_hex(32).encode("ascii"))
            # Non-root containers read bind secrets; the host directory is owner-only.
            if os.name == "posix":
                path.chmod(0o444)
            created.append(name)
        except FileExistsError:
            pass
    return created


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["init-secrets"])
    args = parser.parse_args()
    print("Created secret files:", len(init_secrets()))
