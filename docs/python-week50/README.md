# Week 50 — Concurrency & parallelism

Open **Course → Week 50**. Six days with 36 parts cover concurrency, threads,
processes, futures and asyncio. There are 72 exercises, 72 explained quiz questions,
108 executed examples/solutions, five original diagrams and one measured timing
chart. New terms are explained when introduced; take as many sessions as needed.

## Install once and practise offline

Use Python 3.12 or 3.13 on Windows or Linux:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe lab.py --output artifacts
```

On Linux use `.venv/bin/python`. HTTPX and test tools need internet once to install.
All practice requests then go to the supplied **127.0.0.1 fixture** on your own
computer. It binds an ephemeral port, generates tiny fictional JSON responses and
stops/joins its owned server and handler threads on exit. No remote data, account,
API token, database or learner progress is used. The HTML text/outputs/figures
remain readable offline without running Python or the fixture.

The optional plotted timing example needs `requirements-authoring.txt`.
`collector`, `workers`, `sources` and `lab` refer to these supplied files. Keep them
together. Save process examples as scripts with a main guard:

```python
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp
from workers import square

if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=2, mp_context=mp.get_context("spawn")) as pool:
        print(list(pool.map(square, [1, 2, 3])))
```

Notebook/interactive definitions and lambdas are not portable spawn workers.
The authoring verifier also runs each example as its own guarded script, so spawn
does not accidentally rerun the lesson body or inherit a graphics-heavy main file.

## Study route

1. Concurrency versus simultaneous execution, I/O wait versus CPU computation,
   GIL scope, controlled benchmarking and choosing a tool from the workload.
2. Thread start/join, shared state, a deliberately coordinated lost update,
   locks, queues, error delivery, cooperative stopping and measured local HTTP.
3. Spawn processes, importable workers, process-local globals, transfer costs,
   exceptions, explicit shared-state designs and lifecycle ownership.
4. Futures, map/as_completed order, bounded submission, timeout/cancellation limits,
   deadlock risks and equal-result comparisons across executor types.
5. Coroutines, await, tasks, TaskGroup, event-loop blocking, queue limits, HTTPX
   AsyncClient, deadlines and 100 actual loopback requests with a sequential check.
6. Expected errors versus bugs, cancellation/cleanup, CPU offload, progress,
   backpressure and a measured offline collector milestone.

## The collector

`make_jobs(base, count)` builds a finite manifest of up to 1,000 unique fixture
jobs. The default experiment uses 100. Payloads contain matching id and bounded
integer value. All successful results undergo identical deterministic pure-Python
arithmetic; it is deliberately not a native hashing kernel that releases the GIL.

- `collect_sync(..., threads=0)` fetches and scores sequentially.
- `collect_sync(..., threads=4)` shares an HTTPX Client across four threads and uses
  bounded future submission. This overlaps I/O; it does not promise GIL-bound CPU
  speedup on an ordinary GIL-enabled CPython build.
- `fetch_many` uses one AsyncClient, fixed fetch workers and a bounded job queue;
  it returns raw validated payloads plus explicit errors/progress.
- `collect_pipeline` overlaps async HTTP with two spawn CPU workers. Its job and
  payload queues each have capacity 8 by default. Each CPU consumer awaits its
  submitted process call before submitting another, so CPU submissions are bounded.

Queue limits bound in-flight work, not all program memory: the finite manifest
and returned results are still stored and grow with job count. Slow CPU work can
back up the payload queue, then fetch workers and the producer. A streaming sink
would need its own ordering, storage and error contract.

The fixture uses HTTP/1.0 with connection close and known tiny response bodies.
This lab is not a general public scraper or complete policy for TLS, redirects,
authentication, rate limiting or arbitrary large/untrusted bodies. Browser Pages
hosts the lessons, not the Python processes or a public collection service.

## Error, deadline and cancellation contracts

Expected request failures, timeout and payload-validation errors become explicit
`{id, error}` records in the async collectors. Successful records are sorted by id
after completion. Completion order itself can differ, and progress counts both
successes and expected failures exactly once.

Unexpected bugs (including a broken progress callback) escape a TaskGroup,
cancel siblings and propagate as an exception group. `CancelledError` is not
swallowed. Client scopes close connections and the owned fixture closes after
outstanding finite handlers finish. A timed-out client does not forcibly stop an
already executing server handler.

The HTTPX timeout covers its individual transport phases; `asyncio.timeout`
additionally imposes a total request-scope deadline after a worker starts that
request. Queue waiting is outside that request scope. A future result timeout or
await cancellation does not kill a running thread/process function. Cleanup waits
for already running bounded CPU jobs; queued not-yet-running jobs can be cancelled.
Pool shutdown is awaited through `asyncio.to_thread` so the loop is not directly
blocked by its synchronous join. Do not promise instantaneous hard cancellation.

The synchronous benchmark helper is fail-fast on request failures. Benchmark
fixtures are all-success, and every method must produce identical complete output;
it cannot appear faster by silently dropping failed requests.

## Benchmark evidence

The default command measures three complete collectors for three trials each,
rotating their order. It includes HTTP work, CPU scoring, pool startup, transfers
and shutdown. It records all samples, medians, observed sequential-time ratios and
checks identical sorted outputs. Fixture delay and CPU rounds are declared.

A separate eight-job CPU experiment compares sequential, two-thread and two-process
execution of the same pure-Python arithmetic. Small jobs may lose to startup and
serialization overhead. No test asserts a speedup or an exact elapsed time. A ratio
below one honestly means that method was slower for that measured run.

Reports include Python implementation/version, platform, logical CPU count,
free-threaded-build flag and the runtime GIL probe when available. Standard CPython
3.12 has a GIL; optional free-threaded 3.13 builds differ. Native extensions can also
release the GIL. Logical CPU count does not establish actual core quota, and a few
trial medians are descriptive rather than confidence intervals or public-web SLAs.

For a shorter run:

```powershell
python lab.py --output artifacts-small --count 12 --repeats 1
```

`results.csv` preserves every successful id/score. `report.json` records timings,
workload, equality check, progress, limits, checksum and evidence boundaries.
Tests reconstruct its count/checksum and exercise real HTTP, spawn errors, bounded
submission/concurrency, malformed payloads, deadlines, cancellation and fail-fast
unexpected errors. These two practice artifacts are not a multi-file transaction.

## Optional primary references

- [Threading and GIL](https://docs.python.org/3.12/library/threading.html)
- [Multiprocessing and safe importing](https://docs.python.org/3.12/library/multiprocessing.html)
- [Futures](https://docs.python.org/3.12/library/concurrent.futures.html)
- [Async tasks and structured concurrency](https://docs.python.org/3.12/library/asyncio-task.html)
- [Async queues](https://docs.python.org/3.12/library/asyncio-queue.html)
- [Thread-safe queues](https://docs.python.org/3.12/library/queue.html)
- [Optional free-threaded Python](https://docs.python.org/3.13/howto/free-threading-python.html)
- [HTTPX async](https://www.python-httpx.org/async/)
- [HTTPX timeouts](https://www.python-httpx.org/advanced/timeouts/)

Explanations, exercises and diagrams are original. Checked outputs and visual
evidence are embedded for offline study; optional references supplement them.
