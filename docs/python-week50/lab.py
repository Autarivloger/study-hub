"""Measured offline collector: equal results, bounded work and owned resource cleanup."""

import argparse
import asyncio
import csv
import json
import multiprocessing as mp
import os
import platform
import statistics
import sys
import sysconfig
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path

from collector import collect_pipeline, collect_sync, make_jobs
from sources import local_sources
from workers import score_payload


def cpu_benchmark(*, rounds=200_000, repeats=3):
    payloads = [{"id": index, "value": index * 17 + 5} for index in range(8)]
    expected = [score_payload(payload, rounds) for payload in payloads]
    samples = {name: [] for name in ["sequential", "threads", "processes"]}
    names = list(samples)
    for trial in range(repeats):
        for name in names[trial % 3 :] + names[: trial % 3]:
            start = time.perf_counter()
            if name == "sequential":
                rows = [score_payload(payload, rounds) for payload in payloads]
            else:
                options = {"max_workers": 2}
                executor_type = ThreadPoolExecutor
                if name == "processes":
                    executor_type = ProcessPoolExecutor
                    options["mp_context"] = mp.get_context("spawn")
                with executor_type(**options) as executor:
                    rows = list(executor.map(score_payload, payloads, [rounds] * len(payloads)))
            elapsed = time.perf_counter() - start
            if rows != expected:
                raise AssertionError("CPU strategies did not compute equal work")
            samples[name].append(elapsed)
    return {
        "jobs": len(payloads),
        "rounds_per_job": rounds,
        "samples_seconds": samples,
        "median_seconds": {name: statistics.median(values) for name, values in samples.items()},
        "scope": "Pure-Python arithmetic; full pool startup/transfer/shutdown included. Small jobs can be slower with processes. No speedup assertion.",
    }


def run_experiment(*, count=100, repeats=3, delay=0.025, rounds=20_000, cpu_rounds=200_000):
    if type(repeats) is not int or not 1 <= repeats <= 5:
        raise ValueError("use 1–5 benchmark repetitions")
    samples = {name: [] for name in ["sequential", "threads", "async_processes"]}
    expected, last = None, None
    with local_sources(delay=delay) as (base, state):
        jobs = make_jobs(base, count)
        names = list(samples)
        for trial in range(repeats):
            for name in names[trial % 3 :] + names[: trial % 3]:
                start = time.perf_counter()
                if name == "sequential":
                    rows = collect_sync(jobs, rounds=rounds)
                elif name == "threads":
                    rows = collect_sync(jobs, threads=4, rounds=rounds)
                else:
                    last = asyncio.run(
                        collect_pipeline(jobs, concurrency=4, cpu_workers=2, rounds=rounds)
                    )
                    if last["errors"]:
                        raise AssertionError(
                            "A benchmark cannot claim speed by silently losing jobs"
                        )
                    rows = last["records"]
                elapsed = time.perf_counter() - start
                if expected is None:
                    expected = rows
                if rows != expected:
                    raise AssertionError("Collector strategies produced different records")
                samples[name].append(elapsed)
        observed = state.snapshot()
    gil_probe = getattr(sys, "_is_gil_enabled", None)
    medians = {name: statistics.median(values) for name, values in samples.items()}
    report = {
        "environment": {
            "implementation": platform.python_implementation(),
            "python": platform.python_version(),
            "platform": platform.system(),
            "logical_cpu_count": os.cpu_count(),
            "free_threaded_build": bool(sysconfig.get_config_var("Py_GIL_DISABLED")),
            "runtime_gil_enabled": gil_probe() if callable(gil_probe) else None,
        },
        "workload": {
            "jobs": count,
            "fixture_delay_seconds": delay,
            "rounds_per_payload": rounds,
            "repeats": repeats,
        },
        "collection_samples_seconds": samples,
        "collection_median_seconds": medians,
        "observed_ratio_to_sequential": {
            name: medians["sequential"] / value for name, value in medians.items()
        },
        "all_results_equal": True,
        "result_count": len(expected),
        "result_checksum": sum(row["score"] for row in expected),
        "final_pipeline_progress": last["progress"],
        "pipeline_limits": last["limits"],
        "fixture_observations": observed,
        "cpu_experiment": cpu_benchmark(rounds=cpu_rounds, repeats=repeats),
        "limitations": [
            "Owned loopback fixture with synthetic delay/payloads, not public-web or production throughput.",
            "Complete collectors include HTTP work, CPU scoring, pool startup and shutdown; median of a few trials is descriptive, not a confidence interval.",
            "GIL behavior depends on interpreter/build and native extensions. Logical CPU count does not establish available CPU quota.",
            "Queues and submitted CPU calls are bounded; finite manifest and returned results still grow with total job count.",
            "Expected request/data errors are explicit records. Unexpected failures cancel sibling tasks; running threads/process calls are not forcibly interrupted by task cancellation.",
            "This fixture is plain local HTTP with tiny known bodies; it is not a general public scraper, TLS/redirect policy or untrusted large-body service.",
        ],
    }
    return expected, report


def write_report(folder, **options):
    rows, report = run_experiment(**options)
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / "results.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "score"])
        writer.writeheader()
        writer.writerows(rows)
    (folder / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("artifacts"))
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    report = write_report(args.output, count=args.count, repeats=args.repeats)
    print("Equal successful results:", report["all_results_equal"], report["result_count"])
    print(
        "Collection median seconds:",
        {name: round(value, 3) for name, value in report["collection_median_seconds"].items()},
    )
    print(
        "CPU median seconds:",
        {
            name: round(value, 3)
            for name, value in report["cpu_experiment"]["median_seconds"].items()
        },
    )
    print(
        "Observed ratios:",
        {name: round(value, 2) for name, value in report["observed_ratio_to_sequential"].items()},
    )
    print("Saved paired results and measured limits in", args.output)


if __name__ == "__main__":
    main()
