# Architecture and decisions

`domain.py` owns validation and canonical date/subject rules. `store.py` owns SQL,
transaction boundaries, row ordering and optimistic versions. `api.py` maps HTTP
requests to those operations and translates expected failures into status codes.
`static/index.html` uses the API and displays user strings through textContent.
`main.py` is the environment-configured Uvicorn entry point. `backup.py` and
`smoke.py` are explicit operational and verification tools.

## Why this stack

SQLite fits one owner and modest local write volume, with no separate database
server to maintain. FastAPI reuses the validation model for request handling and
gives a clear JSON boundary. One connection per operation avoids sharing a SQLite
connection across request threads. Sync handlers let the framework run blocking
SQLite operations in its threadpool; no async handler performs a blocking query.

## Persistence and consistency

Schema user_version is 1. Empty databases initialize; unknown future versions and
nonempty unversioned files are rejected. No destructive migration/reset is hidden.
Parameterized SQL treats values as data. Updating/deleting compares id and version
in one write statement; a successful update increments version. Two stale clients
cannot silently overwrite each other through the provided API.

The date/id index supports the ordered date-filtered list. Summary scans depend
on dataset size; a bounded response is not a bounded amount of database work.
Offset pagination is simple but not a stable snapshot across concurrent changes.

## Boundaries and failures

An HTTP timeout does not prove a write failed. The service is not idempotent for
POST; check current records before retrying an uncertain creation. UI button state
helps with double-clicks but cannot solve arbitrary network retries. SQLite busy
errors return a generic retryable service failure. Request origin checks reject
cross-origin writes; no broad CORS policy is enabled. A shared token gives one
owner's access, not separate identities, per-record permissions or a revocation UI.

## Operational limits

Use a persistent, writable database directory, one application worker initially
and a tested snapshot/restore procedure. More workers do not remove SQLite's
write-serialization constraints. Public hosting is a separate operational decision
with HTTPS, access controls and appropriate monitoring. GitHub Pages cannot execute
this Python server; it hosts the learning website and source documentation only.
