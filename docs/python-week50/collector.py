"""Finite-manifest collection with bounded queues and explicit failure semantics."""

import asyncio
import multiprocessing as mp
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, ThreadPoolExecutor, wait
from dataclasses import dataclass
from itertools import islice
from urllib.parse import urlsplit

import httpx

from workers import score_payload


@dataclass(frozen=True, slots=True)
class Job:
    identifier: int
    url: str


def make_jobs(base, count=100):
    parts = urlsplit(base)
    if parts.scheme != "http" or parts.hostname != "127.0.0.1" or not parts.port or parts.username:
        raise ValueError("Use only the owned loopback fixture base URL")
    if (
        parts.path
        or parts.query
        or parts.fragment
        or type(count) is not int
        or not 0 <= count <= 1000
    ):
        raise ValueError("Use a fixture base and 0 through 1000 jobs")
    return [Job(index, f"{base}/item/{index}") for index in range(count)]


def _check(jobs, concurrency, timeout):
    if type(concurrency) is not int or not 1 <= concurrency <= 16 or not 0 < timeout <= 10:
        raise ValueError("Use 1–16 workers and a positive deadline up to 10 seconds")
    if len(jobs) > 1000 or len({job.identifier for job in jobs}) != len(jobs):
        raise ValueError("Use a finite manifest of at most1000 unique job ids")
    for job in jobs:
        parts = urlsplit(job.url)
        if (
            parts.scheme != "http"
            or parts.hostname != "127.0.0.1"
            or not parts.port
            or parts.username
        ):
            raise ValueError("This lab accepts owned loopback HTTP jobs only")


def _decode(response, job):
    response.raise_for_status()
    body = response.json()
    if not isinstance(body, dict) or set(body) != {"id", "value"}:
        raise ValueError("Unexpected fixture payload shape")
    if type(body["id"]) is not int or body["id"] != job.identifier:
        raise ValueError("Payload id differs from the requested job")
    if type(body["value"]) is not int or not 0 <= body["value"] <= 1_000_000:
        raise ValueError("Payload value must be a bounded nonnegative integer")
    return body


def bounded_map(executor, function, iterable, limit=8):
    """Completion-order results with at most limit submitted, unconsumed futures."""
    if type(limit) is not int or limit < 1:
        raise ValueError("limit must be positive")
    source = iter(iterable)
    exhausted = object()
    pending = {executor.submit(function, value) for value in islice(source, limit)}
    try:
        while pending:
            done, pending = wait(pending, return_when=FIRST_COMPLETED)
            for future in done:
                yield future.result()
                value = next(source, exhausted)
                if value is not exhausted:
                    pending.add(executor.submit(function, value))
    finally:
        for future in pending:
            future.cancel()


def collect_sync(jobs, *, threads=0, rounds=20_000, timeout=1):
    _check(jobs, max(1, threads), timeout)
    limits = httpx.Limits(max_connections=max(1, threads), max_keepalive_connections=0)
    with httpx.Client(timeout=timeout, trust_env=False, limits=limits) as client:

        def work(job):
            return score_payload(_decode(client.get(job.url), job), rounds)

        if threads:
            with ThreadPoolExecutor(max_workers=threads) as executor:
                rows = list(bounded_map(executor, work, jobs, threads * 2))
        else:
            rows = [work(job) for job in jobs]
    return sorted(rows, key=lambda row: row["id"])


async def _fetch(client, job, timeout):
    async with asyncio.timeout(timeout):
        return _decode(await client.get(job.url), job)


def _notify(progress, completed, total):
    if progress is not None:
        progress(completed, total)


async def fetch_many(jobs, *, concurrency=4, timeout=1, progress=None):
    _check(jobs, concurrency, timeout)
    queue = asyncio.Queue(maxsize=concurrency * 2)
    records, errors = [], []
    completed = 0

    async def producer():
        for job in jobs:
            await queue.put(job)
        for _ in range(concurrency):
            await queue.put(None)

    limits = httpx.Limits(max_connections=concurrency, max_keepalive_connections=0)
    async with httpx.AsyncClient(limits=limits, timeout=timeout, trust_env=False) as client:

        async def consumer():
            nonlocal completed
            while True:
                job = await queue.get()
                try:
                    if job is None:
                        return
                    try:
                        payload = await _fetch(client, job, timeout)
                    except (TimeoutError, httpx.HTTPError, ValueError) as exc:
                        errors.append({"id": job.identifier, "error": type(exc).__name__})
                    else:
                        records.append(payload)
                    completed += 1
                    _notify(progress, completed, len(jobs))
                finally:
                    queue.task_done()

        async with asyncio.TaskGroup() as group:
            group.create_task(producer(), name="week50-producer")
            for index in range(concurrency):
                group.create_task(consumer(), name=f"week50-fetch-{index}")
    return {
        "records": sorted(records, key=lambda row: row["id"]),
        "errors": sorted(errors, key=lambda row: row["id"]),
        "progress": {"completed": completed, "total": len(jobs)},
        "limits": {"fetch_workers": concurrency, "queue_capacity": concurrency * 2},
    }


async def collect_pipeline(
    jobs, *, concurrency=4, cpu_workers=2, rounds=20_000, timeout=1, queue_capacity=8, progress=None
):
    _check(jobs, concurrency, timeout)
    if (
        type(cpu_workers) is not int
        or not 1 <= cpu_workers <= 4
        or type(queue_capacity) is not int
        or queue_capacity < 1
    ):
        raise ValueError("Use 1–4 CPU workers and a positive queue capacity")
    if type(rounds) is not int or not 0 <= rounds <= 2_000_000:
        raise ValueError("rounds out of range")
    jobs_queue, payload_queue = asyncio.Queue(queue_capacity), asyncio.Queue(queue_capacity)
    records, errors = [], []
    completed = 0
    loop = asyncio.get_running_loop()
    pool = ProcessPoolExecutor(max_workers=cpu_workers, mp_context=mp.get_context("spawn"))
    limits = httpx.Limits(max_connections=concurrency, max_keepalive_connections=0)
    try:
        async with httpx.AsyncClient(limits=limits, timeout=timeout, trust_env=False) as client:

            async def producer():
                for job in jobs:
                    await jobs_queue.put(job)
                for _ in range(concurrency):
                    await jobs_queue.put(None)

            async def fetch_worker():
                nonlocal completed
                while True:
                    job = await jobs_queue.get()
                    try:
                        if job is None:
                            return
                        try:
                            payload = await _fetch(client, job, timeout)
                        except (TimeoutError, httpx.HTTPError, ValueError) as exc:
                            errors.append({"id": job.identifier, "error": type(exc).__name__})
                            completed += 1
                            _notify(progress, completed, len(jobs))
                        else:
                            await payload_queue.put(payload)
                    finally:
                        jobs_queue.task_done()

            async def cpu_worker():
                nonlocal completed
                while True:
                    payload = await payload_queue.get()
                    try:
                        if payload is None:
                            return
                        result = await loop.run_in_executor(pool, score_payload, payload, rounds)
                        records.append(result)
                        completed += 1
                        _notify(progress, completed, len(jobs))
                    finally:
                        payload_queue.task_done()

            async def finish_cpu(fetchers):
                for task in fetchers:
                    await task
                for _ in range(cpu_workers):
                    await payload_queue.put(None)

            async with asyncio.TaskGroup() as group:
                group.create_task(producer(), name="week50-producer")
                fetchers = [
                    group.create_task(fetch_worker(), name=f"week50-fetch-{index}")
                    for index in range(concurrency)
                ]
                for index in range(cpu_workers):
                    group.create_task(cpu_worker(), name=f"week50-cpu-{index}")
                group.create_task(finish_cpu(fetchers), name="week50-close-stage")
    finally:
        # Cancellation can cancel queued work, not forcibly interrupt running CPU calls.
        await asyncio.to_thread(pool.shutdown, wait=True, cancel_futures=True)
    return {
        "records": sorted(records, key=lambda row: row["id"]),
        "errors": sorted(errors, key=lambda row: row["id"]),
        "progress": {"completed": completed, "total": len(jobs)},
        "limits": {
            "fetch_workers": concurrency,
            "cpu_workers": cpu_workers,
            "queue_capacity": queue_capacity,
        },
    }
