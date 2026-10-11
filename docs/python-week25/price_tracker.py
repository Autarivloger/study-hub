"""Week 25 owned local HTML tracker. Python 3.11+; install beautifulsoup4. No network."""
import argparse
from datetime import datetime
from decimal import Decimal
import json
from pathlib import Path
import re
import sys
from bs4 import BeautifulSoup

SOURCE = "own-practice-catalogue"

def validate_records(rows):
    if not isinstance(rows, list):
        raise ValueError("Records must be a list")
    by_id = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"id", "title", "currency", "cents"}:
            raise ValueError("Record schema mismatch")
        identity = row["id"]
        if not isinstance(identity, str) or re.fullmatch(r"[A-Z0-9-]{1,40}", identity) is None:
            raise ValueError("Invalid id")
        if not isinstance(row["title"], str) or not row["title"].strip() or len(row["title"]) > 180:
            raise ValueError("Invalid title")
        if row["currency"] != "USD" or type(row["cents"]) is not int or not 0 <= row["cents"] <= 100_000_000:
            raise ValueError("Invalid currency/amount")
        if identity in by_id and by_id[identity] != row:
            raise ValueError("Conflicting duplicate: " + identity)
        by_id[identity] = row
    return [by_id[key] for key in sorted(by_id)]

def parse_page(text, index, total):
    soup = BeautifulSoup(text, "html.parser")
    root = soup.select_one("#catalog")
    if root is None or root.get("data-page") != str(index) or root.get("data-pages") != str(total):
        raise ValueError("Missing or inconsistent page marker")
    cards = root.select("article.item")
    empty = root.get("data-empty") == "true"
    if empty == bool(cards):
        raise ValueError("Ambiguous empty-page state")
    records = []
    for card in cards:
        title, price = card.select_one("h2"), card.select_one(".price")
        if title is None or price is None:
            raise ValueError("Required card field missing")
        value = " ".join(price.get_text(" ", strip=True).split())
        if re.fullmatch(r"USD (?:[0-9]+|[0-9]{1,3}(?:,[0-9]{3})+)\.[0-9]{2}", value) is None or len(value) > 24:
            raise ValueError("Unsupported price text")
        cents = int(Decimal(value[4:].replace(",", "")) * 100)
        records.append({"id": card.get("data-id"), "title": title.get_text(" ", strip=True),
                        "currency": "USD", "cents": cents})
    return validate_records(records)

def collect(folder):
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or type(manifest.get("schema")) is not int or manifest["schema"] != 1:
        raise ValueError("Manifest schema mismatch")
    if manifest.get("source") != SOURCE or manifest.get("complete") is not True:
        raise ValueError("Unverified or incomplete fixture set")
    captured = manifest.get("captured_at")
    if not isinstance(captured, str) or datetime.fromisoformat(captured.replace("Z", "+00:00")).tzinfo is None:
        raise ValueError("Need a timezone-aware acquisition time")
    pages = manifest.get("pages")
    if not isinstance(pages, list) or not 1 <= len(pages) <= 10:
        raise ValueError("Need 1 to 10 pages")
    if any(not isinstance(name, str) or re.fullmatch(r"page[1-9][0-9]?\.html", name) is None for name in pages):
        raise ValueError("Invalid fixture filename")
    if len(set(pages)) != len(pages):
        raise ValueError("Duplicate page filename")
    rows = []
    for index, name in enumerate(pages, 1):
        path = folder / name
        if path.is_symlink():
            raise ValueError("Fixture must be a regular local copy")
        rows.extend(parse_page(path.read_text(encoding="utf-8"), index, len(pages)))
    return validate_records(rows), captured, pages

def read_state(path):
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or type(data.get("schema")) is not int or data["schema"] != 1 or data.get("source") != SOURCE:
        raise ValueError("Previous snapshot schema/source mismatch")
    return validate_records(data.get("records"))

def changes(previous, current):
    old, new = ({row["id"]: row for row in rows} for rows in (previous, current))
    report = []
    for identity in sorted(old.keys() | new.keys()):
        if identity not in old:
            report.append(("added", identity))
        elif identity not in new:
            report.append(("missing", identity))
        elif old[identity] != new[identity]:
            report.append(("changed", identity))
    return report

def main(argv=None):
    parser = argparse.ArgumentParser(description="Track complete owned local HTML fixture sets; no network.")
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("state", type=Path)
    args = parser.parse_args(argv)
    temporary = None
    try:
        if args.state.resolve() == (args.input_dir / "manifest.json").resolve() or args.state.suffix.lower() != ".json":
            raise ValueError("Use a separate .json snapshot filename")
        current, captured, pages = collect(args.input_dir)
        previous = read_state(args.state)
        report = changes(previous, current)
        state = {"schema": 1, "source": SOURCE, "captured_at": captured,
                 "parser_version": 1, "pages": pages, "records": current, "changes": report}
        args.state.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.state.with_name(args.state.name + ".tmp")
        # Exclusive creation avoids silently overwriting an unrelated temporary file.
        with temporary.open("x", encoding="utf-8") as stream:
            json.dump(state, stream, ensure_ascii=False, indent=2, allow_nan=False)
        temporary.replace(args.state)
    except (OSError, ValueError, TypeError, ArithmeticError) as error:
        print("FAILED:", error, file=sys.stderr)
        return 1
    print("Validated records:", len(current))
    print("Changes:", len(report))
    for kind, identity in report:
        print(kind + ":", identity)
    return 0

if __name__ == "__main__":
    sys.exit(main())
