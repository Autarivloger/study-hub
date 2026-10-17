"""Explicit schema management. Startup never silently upgrades an older schema."""

import argparse
from pathlib import Path
from orm_api.database import make_engine, migrate, revision
from orm_api.settings import Settings

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["current", "upgrade", "downgrade"])
    parser.add_argument("--instance", type=Path, default=None)
    parser.add_argument("--allow-destructive", action="store_true")
    args = parser.parse_args()
    settings = Settings.from_env()
    path = (args.instance or settings.instance_dir).resolve() / "notes.sqlite"
    if settings.database_url is None and not path.is_file():
        parser.error(
            "Initialise a fresh instance by running app.py first; no implicit file is created here"
        )
    engine = (
        make_engine(url=settings.database_url)
        if settings.database_url is not None
        else make_engine(path)
    )
    try:
        if args.action == "upgrade":
            migrate(engine)
        elif args.action == "downgrade":
            migrate(engine, "-1", downgrade=True, allow_destructive=args.allow_destructive)
        print("Revision:", revision(engine))
    finally:
        engine.dispose()
