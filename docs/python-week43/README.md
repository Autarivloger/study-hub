# Week 43 — Full-stack project sprint

**Study Notes** is an original, working browser interface and Python API for capturing and revisiting private learning notes. It extends the Week42 public teaching source in its own folder. Use fictional accounts and fresh Week43 storage. It has no connection to Study Hub browser progress, GitHub sync credentials or your other practice databases.

## Six-day route

| Day | Six parts cover | Deliverable |
|---|---|---|
| 1 | Problem, stories, acceptance, scope, entities, HTTP/screens, delivery plan | `spec.json` and a testable backlog |
| 2 | Project factory, migrations, owned creation, search/filter/pages, changes/deletion, tags | A backend with a known schema and explicit contracts |
| 3 | Registration/hash, token login, ownership, validation, errors, logout | Two-account isolation and useful failures |
| 4 | Same-origin frontend, forms/state, fetch, safe rendering, partial writes, races/pages | The working dashboard at `/` |
| 5 | Test strategy, boundaries, hostile inputs, real browser failures, accessibility, release gates | Reproducible evidence for important workflows |
| 6 | Fresh setup, containers, public release plan, documentation, recovery, portfolio milestone | A documented release candidate and honest deployment record |

Each day has six teaching parts in Study Hub, with examples, actual Python outputs, mistakes, practice, mini challenges and explained quizzes. JavaScript/HTML patterns are labelled in syntax boxes; Python TestClient outputs verify the server contract, while `browser_smoke.cjs` verifies actual browser behaviour.

## Run locally

From a terminal in this directory, use a virtual environment and run these lines separately:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
python app.py
```

On macOS/Linux activate with `source .venv/bin/activate` instead. If activation is unavailable, call the virtual environment's Python executable directly. The first local startup creates this folder's own SQLite `instance/` and reviewed `w43_001`–`w43_003` schema. A known older database requires an explicit reviewed upgrade; unfamiliar schemas are rejected and preserved.

Open **http://127.0.0.1:8002/** for the dashboard. `/docs` retains the local API explorer and `/openapi.json` supplies the generated contract. Ctrl+C stops the server. If port8002 is already in use, stop your other owned teaching server or set `API_PORT` to a free port before startup. Keep the dashboard and API on the same origin. Opening the HTML directly or through GitHub Pages does not run Python.

### Try it as a learner

1. Create a fictional account, for example `asha_demo`, with a 12–128 character practice passphrase. Choose a fresh name each independent demonstration.
2. Write a title and thought, select known tags and save. Notes are plain text. Mark a note complete, change it back, edit it, and cancel a deletion before confirming one.
3. Search a title, including a literal `%` or `_`. Filter All/To revisit/Completed. Five notes fit a page; create six to check Next/Previous.
4. Sign out, create another account and verify its empty collection. Server ownership checks apply to every note route, including tags; hiding another user's buttons is not the access control.
5. Refresh: the login is cleared because bearer tokens are kept in tab memory, while saved notes remain in the database. Sign in to retrieve them.

## Architecture

```text
browser / dashboard.html + dashboard.css + dashboard.js
        | same-origin fetch, JSON or login form
        v
FastAPI validation -> current_user -> owned scoped ORM query
        | transaction / flush / commit
        v
SQLAlchemy -> local SQLite OR independent PostgreSQL (Compose)
        ^
Alembic controlled migration job; runtime verifies w43_003
```

* `spec.json`: six user stories, acceptance criteria, out-of-scope features and completion evidence.
* `orm_api/__init__.py`: application factory, scoped sessions, account/owned-note API, search plus optional completion filter, static routes and validation errors.
* `models.py`, `schemas.py`, `database.py`, `migrations/`: relational integrity, JSON contracts and reviewed transaction/schema operations.
* `settings.py`, `telemetry.py`: explicit configuration, secret redaction, liveness/readiness and bounded request telemetry.
* `static/dashboard.js`: one closure holding the token, current editor, pagination and request version. A response from an older list request cannot repopulate a signed-out workspace. `textContent` treats authored notes as text.
* `tests/`: isolated Python contract, permissions, operations and sprint acceptance checks. `browser_smoke.cjs` uses a real loopback server and a fresh Chrome profile with fictional users.

The frontend uses ordinary DOM, forms, fetch and CSS; there is no npm dependency or build step. It contains loading/empty/error states, disabled mutation controls, inline feedback, labelled inputs, a native delete confirmation dialog, visible keyboard focus, 375px layout, reduced-motion support and light/dark colours. Theme selection is tab-local.

### Important behaviour and known limits

Notes and tag links are **two separate API transactions**. If saving tags fails after a note was created, the editor retains that note's id and the retry updates it rather than creating a duplicate. This is recoverable partial success, not an atomic combined save. A network timeout after an unconfirmed first POST can still leave an uncertain write; inspect/refetch before retrying if confirmation was lost. Duplicate-submit prevention does not implement server idempotency.

The API defaults to last successful write wins; simultaneous editing is not conflict-detected. Refresh discards unsaved editor state. Sign out/expiry clears the private workspace and editor; a failed ordinary write keeps the editor. Failed remote logout still forgets this tab's token, with a warning that revocation was not confirmed. Login sessions expire after fifteen minutes. This sample has no password recovery, refresh-token flow, offline write queue, rich HTML or shared notes.

Before inviting personal production data, add an appropriate edge/request-size and login-abuse policy, account recovery, provider-specific proxy hardening and a real operational review. HTTPS, safe rendering, ownership and memory-only tokens are useful controls; none alone establishes complete public-product security.

## Reproduce the browser checks

Install Node24 and Chrome if needed. There are no npm packages to install. From this folder:

```powershell
node browser_smoke.cjs
```

On Windows the script defaults to the authoring virtual environment path; set `PYTHON` to your environment's Python executable and `CHROME_PATH` to your installed Chrome if different. On Linux defaults are `python` and `/usr/bin/google-chrome`. The script creates its own temporary database/profile and never opens a learner's browser profile. It checks registration, CRUD/tags, literal search, filters, pagination, another owner's denial, text injection, failed-write drafts, partial-save retry, delayed response after logout, reload credentials, mobile themes and console errors. The mocked responses simulate only stated browser failures; ordinary API workflows use the real server.

## Actual Docker/PostgreSQL check

With Docker Engine/Desktop and the Compose plugin running:

```powershell
python ops.py init-secrets
docker compose config --quiet
docker compose up --build -d --wait api
docker compose ps
```

Open **http://127.0.0.1:8043/**. The API joins the normal frontend bridge and private backend; only the API loopback port is published. PostgreSQL has no host publication. A migration service uses its own restricted identity and must finish before the non-root API starts. The runtime gets only its database password and JWT signing secret. Fresh ignored secret files are preserved on rerun; changing a file is not a stored database credential rotation. `DB_SSLMODE=disable` is solely this private local lab setting, never the public managed-database recipe.

`container_smoke.py` is for a **fresh disposable stack only**, since it creates fixed fictional accounts and a separate restore database. It verifies the packaged dashboard/assets, PostgreSQL schema/auth/CRUD/literal search/completion filter, restricted role/user, API recreation persistence, database outage/readiness recovery and a backup restored separately. The GitHub workflow runs Python checks, real Chrome workflows and real containers. It removes only that runner's own throwaway volumes afterward. Ordinary `docker compose stop` keeps your local volume; do not remove a volume holding data you want.

## Public staging release checklist

1. Record source revision, tested artifact, schema head and actual check results. Build from repository root directory `docs/python-week43`. Keep a compatible previous artifact and a rollback/restore plan.
2. On an account/budget you choose, select a Docker web host and **fresh managed PostgreSQL**. Verify current migration-job, port, region, TLS, backup and billing capabilities. A repository/Page publication is not a running API deployment.
3. Privately configure `APP_ENV=production`, `DATABASE_URL` for the restricted runtime role and an externally generated `API_JWT_SECRET` or supported secret-file path. Follow provider verified-TLS/CA requirements. Never place secrets in Git, screenshot, build argument, browser storage or course backup.
4. Execute one reviewed `python manage.py upgrade` job with migration credentials, verify `w43_003`, then start `python server.py` with runtime credentials. The container binds0.0.0.0 internally and respects the provider's `PORT`. Review actual proxy addresses before expanding its default loopback forwarded-header trust.
5. Verify `/health/ready`, generated HTTPS hostname and the complete user flow from another device/network. Check another owner's denial as well as the happy path. Domain/DNS/certificate work follows the chosen provider's exact configuration; current plans/prices are not assumed here.
6. Configure and test external monitoring/alerts, incident ownership, resource/cost limits and backup retention. Rehearse recovery into a separate store. Record external-phone HTTPS evidence as **pending until performed**; this repository does not create paid resources automatically.

## Backup/restore rehearsal

Use only this lab's owned database. Preserve the source:

```powershell
docker compose exec -T db pg_dump -U studyhub_owner -d studyhub -Fc -f /tmp/week43.dump
python -c "from pathlib import Path; Path('backups').mkdir(exist_ok=True)"
docker compose cp db:/tmp/week43.dump ./backups/week43.dump
docker compose exec -T db createdb -U studyhub_owner -O studyhub_migrator studyhub_restore
docker compose exec -T db pg_restore -U studyhub_owner --role studyhub_migrator --no-owner -d studyhub_restore /tmp/week43.dump
docker compose exec -T db psql -U studyhub_owner -d studyhub_restore -c "SELECT count(*) FROM notes"
```

If the restore target already exists, pick another owned name instead of dropping unknown data. Protect private dumps and independently store a recovery copy with suitable encryption/access/retention. Include needed role/configuration/secret recovery separately. Local SQLite needs its own consistent backup approach; do not copy a live database casually and call it verified.

## Portfolio evidence

Write a concise problem/decision summary, actual screenshots, setup steps, API/ownership/transaction overview, test commands/results and known trade-offs. Browser checks save `studyhub-week43-project-desktop.png` and `studyhub-week43-project-mobile.png` in the operating system's temporary folder; capture your own fictional staging flow too. Redact all secrets. Mark local, container and public-host verification separately. A useful README lets another learner reproduce the result; a coverage percentage alone is not proof of all behaviour.

Primary references: [FastAPI static assets](https://fastapi.tiangolo.com/tutorial/static-files/), [MDN fetch](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch), [MDN textContent](https://developer.mozilla.org/en-US/docs/Web/API/Node/textContent), [W3C form feedback](https://www.w3.org/WAI/tutorials/forms/notifications/), [Docker Compose startup](https://docs.docker.com/compose/how-tos/startup-order/). All teaching prose, UI and exercises here are original.
