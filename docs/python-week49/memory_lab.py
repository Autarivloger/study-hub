"""Measure equal-size object batches in separate CPython processes."""

import argparse
import gc
import json
import os
import platform
import subprocess
import sys
import tracemalloc
from pathlib import Path


class PlainPoint:
    def __init__(self, x, y):
        self.x, self.y = x, y


class SlottedPoint:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x, self.y = x, y


def measure_one(kind, count):
    if kind not in {"plain", "slots"} or type(count) is not int or not 1 <= count <= 1_000_000:
        raise ValueError("choose plain/slots and 1 through 1000000 objects")
    if tracemalloc.is_tracing():
        raise RuntimeError("measurement needs its own tracing session")
    cls = PlainPoint if kind == "plain" else SlottedPoint
    gc.collect()
    tracemalloc.start()
    try:
        points = [cls(0, 0) for _ in range(count)]
        current, peak = tracemalloc.get_traced_memory()
        assert len(points) == count  # Keep every object alive until after the snapshot.
    finally:
        tracemalloc.stop()
    return {"kind": kind, "count": count, "current_bytes": current, "peak_bytes": peak}


def compare_layouts(count=1_000_000):
    if type(count) is not int or not 1 <= count <= 1_000_000:
        raise ValueError("count must be 1 through 1000000")
    results = []
    for kind in ["plain", "slots"]:
        process = subprocess.run(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "--worker",
                kind,
                "--count",
                str(count),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
            timeout=90,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        if process.stderr.strip():
            raise RuntimeError(process.stderr)
        results.append(json.loads(process.stdout))
    return {
        "implementation": platform.python_implementation(),
        "python": platform.python_version(),
        "objects_per_layout": count,
        "measurements": results,
        "limits": "Live/peak tracemalloc bytes in separate processes; includes reference list and traced instance storage, shared zero values. Not whole-process RSS, recursive object sizing or a speed benchmark.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", choices=["plain", "slots"])
    parser.add_argument("--count", type=int, default=1_000_000)
    args = parser.parse_args()
    result = measure_one(args.worker, args.count) if args.worker else compare_layouts(args.count)
    print(json.dumps(result, indent=None if args.worker else 2))


if __name__ == "__main__":
    main()
