"""Measure a declared, synthetic workload; preserve equality before speed claims."""

import argparse
import cProfile
import json
import platform
import pstats
import timeit
import tracemalloc
from pathlib import Path
from statistics import median

from studyhub_records import unique_in_order


def slow_unique(values):
    """Reference implementation for valid strings, using linear membership scans."""
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def fixture(size):
    """Use distinct labels followed by the same labels again; no real learner data."""
    return [f"topic-{i}" for i in range(size)] * 2


def benchmark(size=2000, repeats=5):
    """Alternate measurement order and include each complete function call."""
    if not 1 <= size <= 10000 or repeats < 3:
        raise ValueError("size must be 1..10000 and repeats at least 3")
    values = fixture(size)  # Input creation excluded; validation and set creation included.
    expected = slow_unique(values)
    assert unique_in_order(values) == expected
    samples = {"list_scan": [], "set_index": []}
    functions = {"list_scan": slow_unique, "set_index": unique_in_order}
    for repeat in range(repeats):
        order = list(functions) if repeat % 2 == 0 else list(reversed(functions))
        for name in order:
            function = functions[name]
            samples[name].append(
                timeit.Timer(lambda function=function: function(values)).timeit(number=1)
            )
    medians = {name: median(times) for name, times in samples.items()}
    return {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "input_items": len(values),
        "distinct_labels": size,
        "repeats": repeats,
        "equal_results": True,
        "seconds": samples,
        "median_seconds": medians,
        "observed_ratio": medians["list_scan"] / medians["set_index"],
        "scope": "Synthetic in-memory labels; setup excluded; validation included; timeit GC default",
    }


def memory_peak(function, values):
    """Trace allocations during one call; excludes already-existing input and RSS."""
    tracemalloc.start()
    try:
        result = function(values)
        current, peak = tracemalloc.get_traced_memory()
        return {"current_bytes": current, "peak_bytes": peak, "result_items": len(result)}
    finally:
        tracemalloc.stop()


def profile_summary(values):
    """Return function call counts and timings, without parsing a pretty table."""
    profile = cProfile.Profile()
    profile.runcall(slow_unique, values)
    stats = pstats.Stats(profile)
    return [
        {
            "name": key[2],
            "calls": record[1],
            "own_seconds": record[2],
            "cumulative_seconds": record[3],
        }
        for key, record in stats.stats.items()
        if key[2] == "slow_unique"
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=2000)
    parser.add_argument("--output", type=Path, default=Path("artifacts/benchmark.json"))
    args = parser.parse_args()
    report = benchmark(args.size)
    report["memory"] = {
        name: memory_peak(function, fixture(args.size))
        for name, function in [("list_scan", slow_unique), ("set_index", unique_in_order)]
    }
    report["profile"] = profile_summary(fixture(args.size))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Equal outputs:", report["equal_results"])
    print("Observed ratio:", round(report["observed_ratio"], 2))
    print("Scope:", report["scope"])


if __name__ == "__main__":
    main()
