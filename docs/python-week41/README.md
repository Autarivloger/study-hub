# Python Week 41 — Testing, quality & production readiness

**6 days · 36 parts · 72 practice prompts · 82 explained quiz questions · 108 executed example/solution blocks.**

Build evidence around the Week 40 API: isolated pytest fixtures, private CRUD/auth acceptance checks, mocked external HTTP, reproducible CI, validated environment configuration and safe JSON request telemetry. The original Week 40 project and Study Hub progress/storage remain unchanged.

## Install and run on Windows

Keep this entire folder, including `orm_api/`, `migrations/`, `tests/`, requirements, `alembic.ini`, `pyproject.toml` and the workflow handout. In PowerShell in this folder, run each command separately:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q -p pytest_cov --cov=orm_api --cov-report=term-missing --cov-fail-under=75
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe app.py
```

Open **http://127.0.0.1:8002/docs** on this computer. Ctrl+C stops the loopback server. Use fictional accounts such as `asha` with `fictional-learning-passphrase`; never use an external-service credential for a lesson.

Initial dependency installation needs internet. Installed local tests, fixtures and the original OpenAPI explorer work offline. Hosted GitHub Actions needs network for its runner/actions/package installation. GitHub Pages publishes these lessons/source but cannot run this Python server.

Verified local environment: Python 3.12.14, pytest 9.1.1, pytest-cov 7.1.0, coverage 7.16.2, Ruff 0.17.1, FastAPI 0.143.1, Starlette 0.52.1, AnyIO 4.12.1, Pydantic 2.13.5 and SQLAlchemy 2.1.4. Requirements pin the exercise environment; pins need deliberate maintenance and are not permanent security guarantees. The AnyIO pin avoids a newer alias-deprecation path under strict pytest warnings with this Starlette version.

## Study one part at a time

| Day | Six parts |
| --- | --- |
| 1 | Arrange/act/assert; meaningful failures; owned app/database fixtures; parameter boundaries; ownership refusal; endpoint inventory |
| 2 | Fixture composition/scopes; cleanup; patching lookup names; MockTransport; upstream failure cases; explicit time/environment inputs |
| 3 | Unit/integration/E2E boundaries; complete user journey; restart persistence; meaningful failures; real-browser evidence; coverage interpretation |
| 4 | Workflow structure; interpreter/dependency parity; tests/lint/format; minimal CI permission; exact-commit status; local gates |
| 5 | Named environment settings; fail-fast validation; secret boundaries; owned instance paths; configuration behaviour; release limits |
| 6 | Safe JSON request logs; canary/redaction tests; liveness/readiness; correlated generic errors; bounded metrics; complete milestone |

Read each new-concept box, predict the output, execute the example, complete both practice tasks and explain the quiz answers. Depth matters more than finishing six parts in one sitting.

### Executable pytest examples

Some lesson blocks define `source` as a complete test module and call `lesson_support.run_checks(source)`. The helper writes that authored module to a temporary directory, launches **real pytest in a subprocess**, parses its outcome report and returns stable passed/failed/error/skipped counts. Intentionally failing arithmetic tests teach red/green feedback; they are not bugs in the app. Collection/environment failures are rejected rather than hidden.

This helper executes author-controlled Python. It is **not an untrusted-code sandbox**, not a browser Python interpreter and not a feature that executes arbitrary website visitor code. Keep it with this public project package. All files/accounts used by examples are explicitly owned temporary resources.

`practice()` provides the real local API with fictional accounts and a private captured StringIO log stream. `sandbox()` retains the prior direct ORM demonstrations. `app.state.lesson_logs` exists only in the teaching practice fixture, not as a public API endpoint.

## The real pytest suite

- `tests/conftest.py`: function-scoped app/client/logs/header/note fixtures; each app uses `tmp_path`. No real learner database is read.
- `tests/test_api.py`: every declared API operation, private CRUD, strict PATCH False/null/extra rules, boundary pagination, literal search, other-owner refusal and unchanged state, shared tags, hashing/conflict/errors, JWT expiry/claims/logout and safe logs.
- `tests/test_units.py`: valid/invalid settings, secret repr masking, actual helper request handling through MockTransport, controlled timeout/status/schema failures, response parsing.
- `tests/test_operations.py`: real-app readiness failure, generic correlated 500 handling and file-backed persistence with configured TTL.

The suite contains **43 parametrised test cases**. A verified local run reached about **97% line coverage** of `orm_api`; use the command above for the current result. CI gates at 75%, a deliberate teaching policy rather than a guarantee of correctness. Code can execute without a useful assertion; examine missing scenarios and expected outcomes as well as coverage.

An autouse fixture rejects unexpected real HTTPX synchronous/asynchronous transports. The in-process TestClient and supplied MockTransport remain usable. This is a targeted test guard, **not an OS-wide network sandbox**. The optional `read_notice(client)` helper uses the reserved fictional `status.example.test` host and receives an explicitly injected mocked client in tests; the API never calls that host as a background task.

For focused subsets:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -m unit
.\.venv\Scripts\python.exe -m pytest -q -m integration
```

The real-browser author check is `tests/python-week41-project-browser.cjs` at the repository root. It uses a configured Windows Python/Chrome runtime, a disposable profile and an owned loopback server. It exercises actual controls, schema/assets, two-account isolation, tags, token masking/logout, 375px light/dark layouts and JavaScript errors. It is distinct from TestClient evidence. The separate Study Hub browser test verifies the lesson platform, notes/progress and studied-only practice/review.

## Actual GitHub Actions workflow

The repository uses **`.github/workflows/python-week41.yml`**. `quality-workflow.yml` in this folder is an identical readable handout, not another active workflow. If adapting the project to another repository, review paths/permissions and place the intended workflow in that repository’s `.github/workflows/` directory.

The actual workflow:

- Runs on relevant push/pull-request paths and manual dispatch.
- Uses the official checkout/setup-python actions, explicit Python **3.12 and 3.13**, Ubuntu, pinned development requirements and dependency-aware pip caching.
- Uses `contents: read`, `persist-credentials: false`, no personal/application secrets and no elevated `pull_request_target` event.
- Runs Ruff lint, non-mutating formatting check and pytest/coverage. A failed required step is not hidden.
- Limits jobs to ten minutes and cancels obsolete concurrent runs for the same workflow/ref.
- Does not deploy the Python API, change branch-protection rules, upload learner data or configure public infrastructure.

Inspect the workflow run’s **exact commit** and both matrix job conclusions. Queued, running, failed or cancelled is not passed. The local Windows run supplies one interpreter/OS combination; the hosted Ubuntu matrix supplies additional interpreter evidence when its actual jobs complete. A version matrix is not a full cross-platform guarantee. Major-version action tags can later be hardened with reviewed full commit pins.

## Configuration contract

| Variable | Default | Validation/meaning |
| --- | --- | --- |
| `APP_ENV` | development | development, testing or production |
| `STUDYHUB_INSTANCE_DIR` | this project’s `instance/` | Explicitly owned local database/key path |
| `API_LOG_LEVEL` | INFO | INFO, WARNING or ERROR |
| `API_TOKEN_TTL` | 900 | Integer 60–3600 seconds |
| `API_PORT` | 8002 | Integer 1–65535; server still binds loopback |
| `API_JWT_SECRET` | absent | Optional private bytes ≥32; mandatory for production mode |

`Settings.from_env()` parses only named values and validates them before resource startup. Unit tests pass a small explicit mapping. `create_app(instance_path=...)` builds testing settings directly, avoiding accidental inheritance of a real process instance path. Passing both `settings` and `instance_path` is rejected.

The actual guarded `app.py` reads environment settings. For harmless local configuration in PowerShell:

```powershell
$env:APP_ENV='development'
$env:API_TOKEN_TTL='120'
$env:API_PORT='8002'
.\.venv\Scripts\python.exe app.py
```

`.env.example` contains safe examples/comments only. The app does **not** automatically load a `.env` file. Supply actual secrets privately outside source; never paste them into chat, public JS/HTML, workflow YAML, notes or logs. Secret repr masking is not encryption; generic serialization/environment dumps can still expose a value. Changing the signing secret invalidates old signatures; no multi-key rotation protocol is implemented.

Development/testing can use the ignored locally generated 32-byte signing key. Production-mode parsing requires an externally supplied secret, but this mode **does not establish public production readiness**. Both modes use the same app code. The new project owns a separate instance/JWT issuer and retains the known-history migration refusal policy from Week 40; it never converts or resets a real old instance silently.

## Operational endpoints and safe telemetry

The original private API and shared-tag operations remain compatible; the app now declares **16 schema operations**.

| Endpoint | Access | Meaning |
| --- | --- | --- |
| `GET /health` | Public | Shallow compatible `{"status":"ok"}` liveness |
| `GET /health/ready` | Public | Bounded owned-database SELECT 1; 200 ready or generic 503 |
| `GET /internal/metrics` | Verified bearer | Process-local completed request/server-error totals |

No health route runs migrations or writes accounts/notes on every probe. A ready result is a narrow observation at that instant, not a guarantee that every operation or recovery path works.

Request middleware emits JSON records with an allowlist: timestamp, event, bounded method, registered route template (or unmatched), status, measured duration_ms and generated request_id. Responses include X-Request-ID. It does not record raw URL/query/body/header/password/bearer/exception text. Tests use fictional canaries and exact field checks. This applies to the app’s own telemetry; proxy/plugins/external error systems need separate review.

Before headers have been sent, an unexpected failure becomes a generic 500 body with a generated correlation id, and a safe error-status record. An already-started streamed response cannot universally be replaced; that branch is not advertised as a complete error-recovery system. No outside error-tracking service receives data here.

Counters use a lock and bounded route/method/status keys, live in one process and reset on restart. The metrics request’s own record is added after its snapshot. No durable metrics, multi-worker aggregation, alert rules, tracing backend or retention system is implemented. INFO request records can be filtered at WARNING/ERROR; counters still track the completed requests.

## What this project does not claim

This remains a local learning server. It does not add public HTTPS/reverse-proxy deployment, login throttling, MFA/recovery, refresh tokens, distributed storage, secret rotation, a complete request-byte cap, general legacy data conversion or a production restore drill. Do not expose it publicly by changing its listen address. Week 42’s roadmap addresses containers/deployment on top of these foundations.

Private `instance/`, `.env`, virtual environments, pytest/Ruff caches, `.coverage` and generated reports are ignored. Publish source/lessons, not runtime databases/keys or real environment material. Study Hub’s existing backup/import/sync and all old course data retain their structures.

## Primary references

- [pytest fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [Monkeypatching](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)
- [Logging capture](https://docs.pytest.org/en/stable/how-to/logging.html)
- [Where to patch](https://docs.python.org/3/library/unittest.mock.html#where-to-patch)
- [HTTPX transports](https://www.python-httpx.org/advanced/transports/)
- [GitHub Python CI](https://docs.github.com/en/actions/tutorials/build-and-test-code/python)
- [Ruff lint](https://docs.astral.sh/ruff/linter/)

Teaching text, fixtures, exercises and explorer UI are original. Links are optional further reading; the embedded explanations/examples remain readable offline.
