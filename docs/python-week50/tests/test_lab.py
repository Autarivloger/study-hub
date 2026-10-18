import asyncio
import csv
import json
import multiprocessing as mp
import socketserver
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

import pytest

import collector
from collector import bounded_map, collect_pipeline, collect_sync, fetch_many, make_jobs
from lab import cpu_benchmark, write_report
from sources import local_sources
from workers import fail_job, score_payload, square


def test_owned_http_is_real_and_all_strategies_compute_the_same_work():
    with local_sources(delay=0.003) as (base, state):
        jobs = make_jobs(base, 8)
        expected = collect_sync(jobs, rounds=100)
        assert collect_sync(jobs, threads=2, rounds=100) == expected
        fetched = asyncio.run(fetch_many(jobs, concurrency=2))
        assert not fetched["errors"]
        assert [score_payload(row, 100) for row in fetched["records"]] == expected
        result = asyncio.run(
            collect_pipeline(jobs, concurrency=2, cpu_workers=1, rounds=100, queue_capacity=1)
        )
        assert result["records"] == expected and not result["errors"]
        assert result["progress"] == {"completed": 8, "total": 8}
    assert state.snapshot()["requests"] == 32
    assert state.snapshot()["active"] == 0


def test_spawn_importable_workers_preserve_results_and_remote_errors():
    with ProcessPoolExecutor(max_workers=2, mp_context=mp.get_context("spawn")) as pool:
        assert list(pool.map(square, [1, 2, 3])) == [1, 4, 9]
        failed = pool.submit(fail_job, "expected worker failure")
        with pytest.raises(ValueError, match="expected worker failure"):
            failed.result()


def test_bounded_submission_does_not_pull_the_whole_source_and_keeps_none_data():
    seen = []

    def source():
        for value in range(20):
            seen.append(value)
            yield value

    with ThreadPoolExecutor(max_workers=2) as pool:
        rows = bounded_map(pool, square, source(), limit=3)
        assert next(rows) in {0, 1, 4}
        assert len(seen) == 3
        rows.close()
    with ThreadPoolExecutor(max_workers=1) as pool:
        assert list(bounded_map(pool, lambda x: x, [None, 2], limit=1)) == [None, 2]


def test_http_status_and_malformed_payloads_are_explicit_errors_not_fake_success():
    with local_sources(delay=0.003, fail_ids={1}, malformed_ids={2}) as (base, _):
        result = asyncio.run(fetch_many(make_jobs(base, 4), concurrency=2))
    assert [row["id"] for row in result["records"]] == [0, 3]
    assert [row["id"] for row in result["errors"]] == [1, 2]
    assert result["progress"] == {"completed": 4, "total": 4}


def test_deadline_records_a_failure_and_does_not_abandon_other_jobs():
    with local_sources(delay=0.002, slow_ids={0}) as (base, state):
        result = asyncio.run(fetch_many(make_jobs(base, 3), concurrency=2, timeout=0.05))
    assert [row["id"] for row in result["errors"]] == [0]
    assert [row["id"] for row in result["records"]] == [1, 2]
    assert state.snapshot()["active"] == 0


@pytest.mark.parametrize("phase", ["headers", "body"])
def test_windows_connection_abort_is_owned_cleanup_not_a_server_traceback(
    monkeypatch, capsys, phase
):
    original = socketserver._SocketWriter.write

    def abort_write(writer, data):
        is_headers = data.startswith(b"HTTP/")
        if (phase == "headers" and is_headers) or (phase == "body" and not is_headers):
            raise ConnectionAbortedError("simulated Windows client disconnect")
        return original(writer, data)

    monkeypatch.setattr(socketserver._SocketWriter, "write", abort_write)
    with local_sources(delay=0) as (base, state):
        result = asyncio.run(fetch_many(make_jobs(base, 1), concurrency=1))
    assert not result["records"] and [error["id"] for error in result["errors"]] == [0]
    assert state.snapshot()["active"] == 0
    assert "Traceback" not in capsys.readouterr().err


def test_actual_fetch_concurrency_is_bounded(monkeypatch):
    original = collector._fetch
    active = peak = 0

    async def observed(*args):
        nonlocal active, peak
        active += 1
        peak = max(peak, active)
        try:
            return await original(*args)
        finally:
            active -= 1

    monkeypatch.setattr(collector, "_fetch", observed)
    with local_sources(delay=0.01) as (base, _):
        result = asyncio.run(fetch_many(make_jobs(base, 12), concurrency=3))
    assert not result["errors"] and 1 < peak <= 3 and active == 0


def test_pipeline_counts_request_failures_and_progress_once_each():
    progress = []
    with local_sources(delay=0.002, fail_ids={1}, malformed_ids={3}) as (base, _):
        result = asyncio.run(
            collect_pipeline(
                make_jobs(base, 5),
                concurrency=2,
                cpu_workers=1,
                rounds=100,
                queue_capacity=1,
                progress=lambda done, total: progress.append((done, total)),
            )
        )
    assert [row["id"] for row in result["records"]] == [0, 2, 4]
    assert [row["id"] for row in result["errors"]] == [1, 3]
    assert progress == [(i, 5) for i in range(1, 6)]


def test_cancellation_propagates_and_no_owned_async_tasks_remain():
    async def check(base):
        task = asyncio.create_task(
            collect_pipeline(
                make_jobs(base, 20), concurrency=2, cpu_workers=1, rounds=100, queue_capacity=1
            )
        )
        await asyncio.sleep(0.02)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert not [task for task in asyncio.all_tasks() if task.get_name().startswith("week50-")]

    with local_sources(delay=0.04) as (base, state):
        asyncio.run(check(base))
    assert state.snapshot()["active"] == 0


def test_unexpected_callback_errors_fail_the_group_instead_of_becoming_success():
    def broken_progress(done, total):
        raise RuntimeError("unexpected callback bug")

    with local_sources(delay=0.003) as (base, _), pytest.raises(ExceptionGroup) as group:
        asyncio.run(fetch_many(make_jobs(base, 10), concurrency=2, progress=broken_progress))
    assert any(isinstance(error, RuntimeError) for error in group.value.exceptions)


def test_no_external_hosts_are_used_and_invalid_limits_are_rejected():
    with pytest.raises(ValueError, match="loopback"):
        make_jobs("https://example.com", 2)
    with local_sources(delay=0) as (base, _):
        with pytest.raises(ValueError):
            asyncio.run(fetch_many(make_jobs(base, 1), concurrency=0))
        with pytest.raises(ValueError):
            asyncio.run(collect_pipeline(make_jobs(base, 1), cpu_workers=0))
        assert asyncio.run(fetch_many(make_jobs(base, 0)))["progress"]["completed"] == 0


def test_cpu_benchmark_checks_equal_work_without_asserting_a_speedup():
    report = cpu_benchmark(rounds=100, repeats=1)
    assert report["jobs"] == 8
    assert set(report["median_seconds"]) == {"sequential", "threads", "processes"}
    assert all(value > 0 for value in report["median_seconds"].values())


def test_saved_report_and_results_reconstruct_counts_and_checksum(tmp_path):
    report = write_report(tmp_path, count=8, repeats=1, delay=0.002, rounds=100, cpu_rounds=100)
    with (tmp_path / "results.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    saved = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    assert len(rows) == saved["result_count"] == 8
    assert sum(int(row["score"]) for row in rows) == saved["result_checksum"]
    assert report["all_results_equal"]
    assert saved["final_pipeline_progress"] == {"completed": 8, "total": 8}
