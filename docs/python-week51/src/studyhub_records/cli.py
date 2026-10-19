"""A small CSV-to-JSON command with explicit failure and replacement behavior."""

import argparse
import csv
import json
import os
import sys
import tempfile
from pathlib import Path

from .core import totals_by_category


def read_rows(path: Path) -> list[tuple[str, int]]:
    """Read exact category/minutes columns; reject malformed and negative values."""
    rows = []
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != ["category", "minutes"]:
            raise ValueError("CSV header must be category,minutes in that order")
        for number, row in enumerate(reader, 2):
            category, minutes = row.get("category"), row.get("minutes")
            if None in row or category is None or minutes is None:
                raise ValueError(f"line {number}: expected exactly two fields")
            # Restrict the external representation; int() alone accepts more forms.
            if not minutes or not minutes.isascii() or not minutes.isdecimal():
                raise ValueError(f"line {number}: minutes must contain ASCII digits")
            rows.append((category, int(minutes)))
    totals_by_category(rows)  # Validate every category before any output replacement.
    return rows


def write_report(path: Path, report: dict) -> None:
    """Replace one JSON file after success; this is not a multi-file transaction."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix=".studyhub51-",
            suffix=".tmp",
            delete=False,
        ) as destination:
            temporary = Path(destination.name)
            json.dump(report, destination, ensure_ascii=False, indent=2)
            destination.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    """Return 0 on success or 2 for an input/output error, with no traceback."""
    parser = argparse.ArgumentParser(description="Summarize synthetic study minutes")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.input.resolve() == args.output.resolve():
            raise ValueError("input and output paths must differ")
        rows = read_rows(args.input)
        report = {"rows": len(rows), "totals": totals_by_category(rows)}
        write_report(args.output, report)
    except (OSError, ValueError, TypeError, csv.Error) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    print(f"Processed {len(rows)} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
