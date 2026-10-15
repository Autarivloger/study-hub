# Python Week 40 — Databases at depth with SQLAlchemy

**6 days · 36 teaching parts · 72 practice prompts · 82 explained quiz questions · 108 executed examples/solutions.**

This is an original, separate learning project that refactors Week 39’s local Notes API onto SQLAlchemy, then adds shared tags, reviewed Alembic history and measured query experiments. The Week 39 project and all existing Study Hub application/storage code remain intact.

## Run locally on Windows

Download this complete folder. Keep `app.py`, `manage.py`, `alembic.ini`, `lesson_support.py`, `orm_api/` and `migrations/` together. In PowerShell in this folder, run each command separately:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Open **http://127.0.0.1:8001/docs** on the same computer. **Ctrl+C** stops the server. A brand-new owned instance receives the three reviewed migrations automatically. A known older instance is refused at startup until explicitly upgraded; an unfamiliar instance is preserved and refused.

Initial package installation needs internet. Afterwards the lessons, local server, migrations, original OpenAPI explorer and supplied fixtures run offline. The explorer uses local HTML/CSS/JS, no CDN scripts/fonts. GitHub Pages publishes course/source files; it cannot execute this Python server.

Verified environment: Python 3.12.14, SQLAlchemy 2.1.4, Alembic 1.20.0, FastAPI 0.143.1, Starlette 0.52.1, Pydantic 2.13.5, HTTPX 0.28.1, Uvicorn 0.54.0, PyJWT 2.15.1 and Werkzeug 3.1.9. Use the included pinned requirements to reproduce the examples.

## Study sequence

| Day | Six parts |
| --- | --- |
| 1 | Core/ORM; engine/pool; Session/flush/commit; identity/expiration; expressions/results; FastAPI Session scope |
| 2 | Ownership; many-to-many links; constraints; cascades; owned tag endpoints; graph reconciliation |
| 3 | SQL filtering/paging; aggregate/outer joins; join multiplicity; measured N+1; eager loading; response boundaries |
| 4 | Schema history; three revisions; autogenerate review; downgrade; expand/backfill/constrain; explicit restart policy |
| 5 | Atomic business changes; failure rollback; database integrity; savepoints; optional optimistic-version example; acceptance checks |
| 6 | Index plans; measured timings; projection/aggregation; bulk operations; refactor verification; complete project |

Do one part at a time: predict, execute, explain, complete both exercises and then answer the quiz. Early examples repeat a complete one-table in-memory scaffold. `create_all` there is only for a fresh disposable demonstration; the actual project uses Alembic.

Examples importing `sandbox`, `practice` or `orm_api` need this complete folder beside the snippet. The supplied helper imports the project’s known mapped classes for direct experiments; their relationships are unpacked on Day 2. No learner database/key is included.

## Practice in the original explorer

1. Register **asha** with the fictional password **fictional-learning-passphrase** using **POST /v1/users**.
2. Use **POST /v1/token** with the same fictional form credentials. The bearer is placed in the masked field for this tab only and redacted in response output. Password fields are cleared after requests.
3. Create/read/replace/patch/delete your own notes. PUT requires all writable fields; PATCH retains omitted fields and preserves supplied False.
4. Use **GET /v1/tags**, then **PUT /v1/notes/{note_id}/tags** with `{"names":["python","api"]}`. Expect sorted names.
5. Read the member’s tags. Send `{"names":[]}` to remove links. The shared catalog remains.
6. Register/log in as **ben**. Ben’s notes begin empty. Asha’s member and tag URLs return the same 404 policy as a missing resource.
7. Logout and verify the old bearer cannot be replayed. A separate independent login retains its own lifetime.
8. Stop/restart: the local database/key persist. Reloading the explorer forgets its current-tab bearer field.

Use only fictional practice accounts. This project never needs a GitHub credential, real service password or existing Study Hub sync token. The explorer stores no token in browser localStorage/sessionStorage/cookies or a source file. The API necessarily returns bearer credentials to API clients; handle them as credentials. The explorer masks them only in its displayed response.

## Preserved core contract and added relationships

The original operations remain: public health, JSON registration, form login, protected current user/logout, private bounded collection listing and full member CRUD under `/v1/notes`. Original note input/output fields remain unchanged; tags are managed separately rather than silently expanding writable note data.

| Added method | URL | Purpose |
| --- | --- | --- |
| GET | `/v1/tags` | Authenticated known catalog: api, database, python |
| GET | `/v1/notes/{note_id}/tags` | Names assigned to an owned note |
| PUT | `/v1/notes/{note_id}/tags` | Replace that owned note’s links from unique known names |

All tag operations require a verified bearer. An empty names list clears links; unknown/duplicate names, null and extra fields produce 422. The server resolves known names to Tag objects, not arbitrary visitor-selected related objects. There is no endpoint deleting a shared catalog tag or a user account.

Core semantics retained:

- Positive member ids; default limit 10, allowed 1–50; offset 0–10000; title search at most 80 characters.
- Owner filter before count/page; ascending id order; beyond-end page succeeds with empty items.
- Literal substring search through bound expressions and SQLite `instr(lower(title),lower(q))`; `%`/`_` are literal, and built-in lowercase is not full Unicode case folding.
- Strict JSON note fields; title 1–100 and body 1–2000 characters, trimmed and rejected if empty afterward; actual Boolean completed.
- Server-derived id, owner and creation time. PUT replaces all writable fields; PATCH preserves omissions/False, rejects null and `{}`.
- Public response fields exclude password verifiers and internal owner ids. Sanitised 422 details omit raw rejected input/context.
- 201/Location on creation, 200 representations on reads/updates, truly empty 204 on delete/logout, 401/Bearer challenge for invalid authentication, 404 for absent/inaccessible members, 409 username conflict, 422 invalid inputs, 405 unsupported methods.

The new project has its own instance and JWT issuer/audience (`studyhub-w40-local`, `studyhub-w40-clients`); tokens from another project instance are not portable merely because paths are compatible. This source refactor does not claim automatic conversion of real Week 39 data or credentials.

## Code and relational model

- `orm_api/models.py`: typed SQLAlchemy mappings for User, Note, Tag and LoginSession plus the `note_tags` table. User→Note is one-to-many; Note↔Tag is many-to-many. The link pair is a composite primary key. Password hashes remain internal.
- `orm_api/database.py`: engine configuration, per-connection foreign keys, explicit SQLite BEGIN, Session factory, commit/rollback helper and reviewed migration operations.
- `orm_api/__init__.py`: app factory/lifespan, scoped Session dependency, verified principal, public API coordination and local explorer delivery.
- `orm_api/schemas.py`: Pydantic request/response contracts and tag selection rules.
- `migrations/`: independently declared baseline, tags and indexes plus env/template supporting reviewable autogeneration.
- `manage.py`: explicit current/upgrade/downgrade operations on an existing selected instance file.
- `lesson_support.py`: direct ORM sandbox, real API fixtures, count-only SELECT instrumentation and isolated index/timing experiment.
- `instance/`: ignored `notes.sqlite` and `signing.key`, created locally. Never publish these runtime artifacts.

User notes/login records are exclusively owned, with matching ORM and FK cascade rules. Deleting a note removes its association links while preserving shared Tag rows. The API has no user-deletion route; direct sandbox examples demonstrate that owned lifecycle independently.

## Session and transaction policy

The app owns one engine and configured `sessionmaker`; each request receives one fresh Session and closes it in the yielded dependency. A Session is neither a browser login session nor a safe global object shared between concurrent requests. Sync ORM/hash handlers use `def`. No AsyncSession/async-driver implementation is claimed.

Authentication reads can start the request’s transaction through autobegin. The `atomic` helper commits that existing coherent unit **inside the handler before returning success**, rolling back on any exception. It does not blindly open another root `Session.begin` after authentication. Read-only Session cleanup rolls back unfinished reads. `expire_on_commit=False` supports a short request boundary, not perpetual freshness.

For Python 3.12 SQLite legacy-mode behaviour, the engine sets the DBAPI connection isolation level to None and SQLAlchemy’s begin event explicitly issues BEGIN. That makes SELECT/DDL/savepoint transaction ownership deliberate. Each connection enables foreign keys. File-backed pooling is bounded to five connections, no overflow, with pre-ping. Pool size is resource reuse/capping, not a promise of unlimited concurrent SQLite writes. Loaded objects and their Session must not be used concurrently across workers.

The main API retains last-writer update behaviour; it does not introduce an ETag/version conflict contract. A separate executable versioned-item example demonstrates SQLAlchemy’s mapped-instance optimistic version checking and StaleDataError. That mechanism does not automatically cover arbitrary bulk SQL.

## Three migrations and safe operations

| Revision | Change | Downgrade consequence |
| --- | --- | --- |
| `w40_001` | Users, private notes, token sessions, constraints and owner/id index | Drops those baseline tables/data |
| `w40_002` | Shared known tags and constrained links | Drops tag/link tables and assignments |
| `w40_003` | Owner/completed/id and reverse tag-link indexes | Drops those two indexes; keeps rows/tables |

Stop the server. Select an explicitly owned instance/backup and review the files before operations. Default commands target this project’s local instance:

```powershell
.\.venv\Scripts\python.exe manage.py current
.\.venv\Scripts\python.exe manage.py upgrade
```

Only on an owned disposable test/backup copy, after reviewing the previous revision:

```powershell
.\.venv\Scripts\python.exe manage.py downgrade --instance "D:\YOUR-OWNED-TEST-COPY" --allow-destructive
```

The placeholder must be replaced with an actual owned test copy. The explicit flag permits a one-revision downgrade; it does not guarantee data recovery. An index-only rollback preserves rows, while rolling back tags or baseline history destroys their data. Recreating a table does not restore deleted values. Independently test backup restoration.

`alembic.ini` stores no database credential. `env.py` requires an explicit supplied connection; management/helpers choose the owned SQLite engine. `Base.metadata` supports comparison, while immutable historical revisions declare their own operations. `script.py.mako` supports generating candidate revisions; the course demonstrates `compare_metadata` safely and explains reviewing a proposed file before applying it. Autogenerate cannot infer every rename/backfill or audit all CHECK/data/permission rules.

Existing unknown histories/table sets are preserved/refused. Known older schemas need explicit upgrade. The guard checks known history and table sets, not every externally edited column/constraint. A real drift audit also needs inspected schema, comparison, data checks and tested recovery. Do not use `stamp` to pretend an unconverted Week 39 schema is migrated. A real legacy conversion requires a reviewed, copy-first mapping/backfill/constraint plan; this project does not touch an old instance.

## Measured query experiments

- A fresh three-user sandbox deliberately issues **4 SELECTs** for lazy user/notes traversal: one parent plus three child queries.
- `selectinload(User.notes)` obtains the same `[2,2,0]` counts in **2 SELECTs** for this small fixture. Larger parent sets may batch more.
- `joinedload(User.notes)` plus `Result.unique()` obtains that fixture in **1 SELECT** but can multiply transferred rows; fewer queries alone is not proof of lower total cost.
- An independent **20,000-row** measurement table runs a bound owner/completed ordered query before and after a composite index. Plans change from table scan to the named index, and the returned 20 ids remain identical.
- Seven execute/fetch timing samples per case produce medians. Course output shows one real verified run, not a guaranteed speed ratio. These local largely warm-cache samples exclude network/concurrent workloads.

The normal Notes list already uses its owner/id index. The additional owner/completed/id index serves the demonstrated more selective direct workload; it is not falsely presented as speeding every API query. Literal substring search is not automatically accelerated by a normal title B-tree. Indexes cost storage and write maintenance. Projection, SQL aggregation, bounded results and explicit eager loading often matter as much as one new index.

## Authentication scope

The local API preserves salted Werkzeug scrypt hashing, generic credential failure/dummy verification, strict public responses, fixed HS256 JWT verification, required typed claims, 15-minute lifetime and a live token-session allowlist. Current logout revokes one jti; unrelated logins retain their own expiry. Claims contain no password or note body. A signature is not encryption. Every member/relation query requires the verified owner.

The password-form flow is a local learning mechanism, not a recommendation for third-party browser identity deployment. CORS is not authentication. The explorer uses same-origin explicit bearer headers, safe text rendering and local assets. The project has no public HTTPS deployment, MFA, refresh tokens, recovery, throttling, full request-byte cap, general legacy conversion or distributed database support. Keep it on loopback for learning.

## Verification

From the repository root using the environment with these requirements:

```powershell
python -B tests/python-week40-project.py
node tests/python-week40.cjs
node tests/python-week40-browser.cjs
node tests/python-week40-project-browser.cjs
node tests/python-learning-smoke.cjs
```

The generator executes all 108 authored example/solution blocks in owned temporary folders before inserting only Week 40 lesson data. Static tests compare every old lesson and all application/storage code with the previous commit. Browser checks use disposable profiles and fictional progress. They cover all parts/quizzes, navigation, notes/progress refresh, studied-only practice/review, exact search, 375px themes and actual backup/import regression. Project checks exercise real private API CRUD/auth, tags/cascades, constraints/rollback, persistence/refusal, three migrations/downgrade, metadata comparison, SELECT counts, query plans/timings and the actual local explorer.

## Primary references

- [SQLAlchemy Session basics](https://docs.sqlalchemy.org/en/21/orm/session_basics.html)
- [Relationship patterns](https://docs.sqlalchemy.org/en/21/orm/basic_relationships.html)
- [Relationship loading](https://docs.sqlalchemy.org/en/21/orm/queryguide/relationships.html)
- [Connection pooling](https://docs.sqlalchemy.org/en/21/core/pooling.html)
- [SQLite transaction/foreign-key behaviour](https://docs.sqlalchemy.org/en/21/dialects/sqlite.html)
- [Alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Autogenerate review](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)

Explanations, examples, fixtures, exercises and explorer UI are original. References are optional further reading; the course does not depend on external pages to explain its lessons.
