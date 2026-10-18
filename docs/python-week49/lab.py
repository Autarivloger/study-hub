"""Run a synthetic streaming CSV pipeline and a measured object-layout comparison."""

import argparse
import csv
import hashlib
import json
import platform
from pathlib import Path

from memory_lab import compare_layouts
from streamkit import FIELDS, atomic_text, write_selected


def make_demo(path, count=10_000):
    if type(count) is not int or count < 0:
        raise ValueError("count must be a nonnegative integer")
    with atomic_text(path) as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        categories = ("study", "review", "break")
        for index in range(count):
            writer.writerow(
                {
                    "event_id": f"demo-{index}",
                    "category": categories[index % 3],
                    "minutes": index % 60,
                }
            )


def file_digest(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def write_report(folder, *, source=None, count=10_000, memory_count=1_000_000):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    selected = folder / "selected.csv"
    if source is not None and Path(source).resolve() in {
        selected.resolve(),
        (folder / "report.json").resolve(),
    }:
        raise ValueError("source must not be an output artifact")
    if source is None:
        source = folder / "synthetic-events.csv"
        make_demo(source, count)
    result = write_selected(source, selected)
    result.update(
        {
            "dataset": "Synthetic local demo by default; never Study Hub progress",
            "policy": "strict parse -> study/review filter -> row projection -> streaming CSV write",
            "memory_scope": "Pipeline state bounded by one record/parser buffer and three allowed categories, not all input rows; record/field size and count integer sizes still matter",
            "selected_csv_sha256": file_digest(selected),
            "python": platform.python_version(),
            "layout_experiment": compare_layouts(memory_count),
            "limitations": [
                "CSV totals require complete consumption; creating a generator performs no parsing.",
                "The entire source is validated, including rows the category filter would discard.",
                "Outputs are replaced atomically per file, not as one multi-file transaction. Check the CSV hash against the report after interruptions.",
                "Call counters are local instrumentation and not thread-safe; generator creation is not generator consumption.",
                "Descriptors and slots express an API contract, not a security or deep-immutability boundary.",
            ],
        }
    )
    with atomic_text(folder / "report.json") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("artifacts"))
    parser.add_argument("--source", type=Path)
    parser.add_argument("--rows", type=int, default=10_000)
    parser.add_argument("--memory-records", type=int, default=1_000_000)
    args = parser.parse_args()
    report = write_report(
        args.output, source=args.source, count=args.rows, memory_count=args.memory_records
    )
    print("Parsed / written:", report["parsed"], report["written"])
    print("Selected totals:", report["minutes"])
    print("Measured objects per layout:", report["layout_experiment"]["objects_per_layout"])
    print("Saved selected.csv and a paired report in", args.output)


if __name__ == "__main__":
    main()
