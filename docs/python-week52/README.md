# Week 52 capstone — StudyLog

An original single-owner study-session app: SQLite persistence, validated JSON API,
responsive light/dark browser interface, editing conflicts, summaries and verified
backups. It is independent of Study Hub's browser data. Python 3.12+.

## Start in this project folder

PowerShell, one line at a time:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe smoke.py --output artifacts/verification.json
.\.venv\Scripts\python.exe -m uvicorn capstone.main:app --host 127.0.0.1 --port 8000
```

Then open http://127.0.0.1:8000/ in your browser. Ctrl+C stops the server.
On Linux/macOS use `.venv/bin/python`. Initial dependencies need internet or a
prepared wheelhouse; the installed app, its static interface and SQLite work
without external services. No CDN/fonts or external data is loaded by the UI.

Read SPEC.md before editing. ARCHITECTURE.md explains boundaries and tradeoffs;
DEPLOYMENT.md explains the local/remote distinction and manual production steps;
RETROSPECTIVE.md gives an honest final review and next-six-month plan.

## Verification

The tests cover data contracts, persistence, transaction rollback, constraints,
parameterized values, stale edits/deletes, filters, limits, authorization, origin
checks, generic database errors and snapshots. smoke.py launches actual owned
Uvicorn processes on 127.0.0.1, sends HTTP requests, stops/restarts the process,
then opens a backed-up database in another fresh server. It uses synthetic data,
temporary paths and a generated test-only token that is never printed.

The root repository browser check exercises the actual interface in an isolated
Chrome profile. API TestClient checks, real HTTP checks and browser UI checks
establish different boundaries; none is represented as a public deployment.

## Package and CI

pyproject.toml includes the HTML as package data. `python -m build --no-isolation`
uses the already-prepared backend; a fresh artifact rehearsal in release_check.py
verifies wheel contents and runs the app from its installed package outside the
checkout. The CI workflow repeats the project checks on Python 3.12 and 3.13.
The artifact rehearsal prepares dependency wheels online unless you provide
`--wheelhouse YOUR-WHEELHOUSE`; its fresh consumer then installs without an index.
This is separate from ordinary offline use after the initial app setup.

## Primary references

- https://docs.python.org/3.12/library/sqlite3.html
- https://fastapi.tiangolo.com/tutorial/testing/
- https://fastapi.tiangolo.com/tutorial/dependencies/
- https://fastapi.tiangolo.com/deployment/concepts/
- https://www.uvicorn.org/settings/
- https://docs.docker.com/engine/containers/run/
- https://packaging.python.org/en/latest/tutorials/packaging-projects/
