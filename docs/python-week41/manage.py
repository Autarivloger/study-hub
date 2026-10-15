"""Explicit schema management. Startup never silently upgrades an older schema."""

import argparse
from pathlib import Path
from orm_api.database import make_engine, migrate, revision

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["current", "upgrade", "downgrade"])
    parser.add_argument(
        "--instance", type=Path, default=Path(__file__).resolve().parent / "instance"
    )
    parser.add_argument("--allow-destructive", action="store_true")
    args = parser.parse_args()
    path = args.instance.resolve() / "notes.sqlite"
    if not path.is_file():
        parser.error(
            "Initialise a fresh instance by running app.py first; no implicit file is created here"
        )
    engine = make_engine(path)
    try:
        if args.action == "upgrade":
            migrate(engine)
        elif args.action == "downgrade":
            migrate(engine, "-1", downgrade=True, allow_destructive=args.allow_destructive)
        print("Revision:", revision(engine))
    finally:
        engine.dispose()
