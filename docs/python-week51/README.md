# Week 51 — Performance, packaging and professional practice

An original, dependency-free runtime library for synthetic study records. The
lessons explain every step; the files here let you perform it. Python 3.12+.
This lab does not open Study Hub localStorage, backups, Gists or credentials.

## Setup (PowerShell; one line at a time)

Run these commands from this folder. Use the real path to your downloaded repo.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pip install --no-build-isolation --no-deps -e .
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m doctest src/studyhub_records/core.py
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mkdocs build --strict
.\.venv\Scripts\python.exe bench.py --output artifacts/benchmark.json
.\.venv\Scripts\python.exe verify_release.py --output artifacts/release.json
```

On Linux/macOS, use `.venv/bin/python` in place of `.\.venv\Scripts\python.exe`.
Initial installation needs internet or a prepared wheelhouse. Reading the lessons
and using the installed library work offline. Generated `site/index.html` uses
flat page links for local viewing; syntax rendering/search polish is secondary
to the readable page content. This is a local docs build, not public deployment.

## Package layout

`src/studyhub_records` contains the installable import package. `bench.py`, tests,
manual pages and release checks are development tools. `pyproject.toml` declares
the distribution name `studyhub51-records`, version, backend and CLI entry point.
Build requirements are not runtime dependencies. A version pin in the development
file is not a complete, hashed, transitive lockfile.

## What release verification really does

`verify_release.py` copies the source into a temporary working folder, builds an
sdist and a wheel (wheel from sdist), runs `twine check --strict`, builds MkDocs,
and installs that exact wheel into a fresh virtual environment. It runs import,
metadata and CLI checks with the current directory outside the checkout and
`PYTHONPATH` removed. It also runs the packaged doctests. Build tools must already
be installed; `--no-isolation` deliberately reuses this prepared development
environment. This mode is not a test of automatically resolved build dependencies.

The report stores artifact names, SHA-256, version, interpreter and successful
checks. Temporary environments are cleaned afterwards. It performs no publication,
GitHub message or TestPyPI upload. Publication instructions are in the release page.

## Learning evidence

Keep your before/after profile, equal-output tests, benchmark samples, memory scope,
wheel report, docs build and a small review response. Finish with a release note
and an honest portfolio entry distinguishing local verification from publication.
Take additional sessions for any part you cannot yet explain without copying.

## Primary references

- [Python profiling](https://docs.python.org/3.12/library/profile.html)
- [timeit](https://docs.python.org/3.12/library/timeit.html)
- [tracemalloc](https://docs.python.org/3.12/library/tracemalloc.html)
- [line_profiler](https://kernprof.readthedocs.io/en/latest/auto/line_profiler.html)
- [Packaging projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [TestPyPI](https://packaging.python.org/en/latest/guides/using-testpypi/)
- [MkDocs writing guide](https://www.mkdocs.org/user-guide/writing-your-docs/)
- [Semantic Versioning](https://semver.org/)
- [GitHub contribution guide](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project)
