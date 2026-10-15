# Python Week 39 — FastAPI & modern API development

An original local learning project accompanying **6 days, 36 teaching parts, 72 practice prompts, 82 explained quiz questions and 108 executed example/solution blocks** in Study Hub.

Build and understand a private Notes API: typed routes, Pydantic validation, public response models, REST contracts, SQLite transactions, scoped dependencies, password hashing, JWT verification, ownership and individual logout revocation.

## Setup on Windows

Download this entire folder. Keep `learning_api/`, including its `static/` files, alongside `app.py` and `lesson_support.py`. Open PowerShell in this folder. Run each command separately:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Open **http://127.0.0.1:8000/docs** on the same computer. Stop with **Ctrl+C**.

Internet is required for the initial package installation. Once installed, this local server, generated OpenAPI explorer and the executable lesson fixtures work offline. The explorer uses original HTML/CSS/JS served from this project, without CDN scripts, external fonts or third-party UI bundles. The pinned Starlette release keeps the HTTPX TestClient examples compatible without its newer HTTPX deprecation path.

Tested with Python 3.12.14, FastAPI 0.143.1, Starlette 0.52.1, Pydantic 2.13.5, Uvicorn 0.54.0, HTTPX 0.28.1, PyJWT 2.15.1, python-multipart 0.0.32 and Werkzeug 3.1.9. These pins reproduce the exercises; review dependencies before using a different deployment context.

## How to study

| Day | Six parts |
| --- | --- |
| 1 | Request flow; JSON; sync/async; lifespan; OpenAPI/offline docs; local server |
| 2 | Path types; positive ids; query pagination; optional/repeated values; safe validation errors; request matrix |
| 3 | Models; strict/extra fields; validators; nested/cross-field rules; public responses; PUT/PATCH |
| 4 | Resource design; statuses/Location; error policy; idempotence; version/search/pagination; contracts |
| 5 | Injection; yield cleanup; transactions; layers/private CRUD; dependency overrides; persistence/schema ownership |
| 6 | Bearer form flow; password hashing; JWT policy; ownership/revocation; acceptance tests; complete milestone |

Do not rush all parts into one sitting. Predict an output, run it, explain the boundary, complete both exercises and then answer the quiz. Every supplied example/solution runs in a fresh temporary working directory during authoring. Statements such as `from lesson_support import practice` need this folder’s public helper and full `learning_api` package. No private learner instance data is distributed.

## Practice in the original local explorer

1. Expand **POST /v1/users**. Register username `asha` and the **fictional** practice password `fictional-learning-passphrase`. Send the request. Expect **201** with public id/username only. The explorer clears the password from its registration editor afterward.
2. Expand **POST /v1/token**. Enter the same fictional username/password in the form fields. Send. Expect **200**. The token is placed in the masked bearer field and redacted in the displayed response. The form password is cleared.
3. Expand **POST /v1/notes**. Create a note. Expect **201**, an id and a representation.
4. Use **GET /v1/notes**, then **GET /v1/notes/{note_id}** with that id.
5. **PUT** supplies all three writable fields; **PATCH** supplies only desired changes. Try `{"completed": false}` and verify False survives.
6. **DELETE** the note. Expect **204** with no body. Reading its old id now returns **404**.
7. Register `ben`, log in as Ben and observe an independent empty collection. An Asha-owned id returns **404** for Ben.
8. **POST /v1/logout** revokes the current login and clears the explorer field. Previously issued access from that login is no longer accepted. An independent login remains valid until its own expiry/logout.

The explorer holds the token only in the current tab’s memory/password field, never browser localStorage, cookies or a source file. Reload/Forget token clears the field. The JSON registration editor is not a password manager: use only fictional learning accounts. The API still returns a real bearer token to API clients by design; they must handle it as a credential. The explorer deliberately masks it in response output.

## Interface contract

| Method | Path | Success | Input/access |
| --- | --- | --- | --- |
| GET | `/health` | 200 | Public status |
| POST | `/v1/users` | 201 | Strict JSON username/password |
| POST | `/v1/token` | 200 | Form username/password; token response |
| GET | `/v1/me` | 200 | Verified bearer |
| POST | `/v1/logout` | 204 | Revoke current bearer login |
| GET | `/v1/notes` | 200 | Own collection, bounded query controls |
| POST | `/v1/notes` | 201 | Own new resource, Location header |
| GET | `/v1/notes/{note_id}` | 200 | Own member |
| PUT | `/v1/notes/{note_id}` | 200 | Full writable-field replacement |
| PATCH | `/v1/notes/{note_id}` | 200 | Nonempty supplied-field update |
| DELETE | `/v1/notes/{note_id}` | 204 | Own member, empty body |
| GET | `/openapi.json` | 200 | Generated public contract |
| GET | `/docs` | 200 | Original local explorer |

Note ids must be positive integers. `limit` defaults to 10, ranges 1–50; `offset` defaults to 0, ranges 0–10000; `q` is at most 80 characters. Owner filtering precedes count/page. Ordering is ascending id. A beyond-end page returns 200 with empty items and the owner-filtered total. Count and items share a request transaction, but later pages may shift if records change between requests.

Search is a **literal title substring** using bound parameters and `instr(lower(title),lower(?))`. `%` and `_` are not wildcards. SQLite’s built-in `lower` does not promise complete Unicode case folding. An empty query matches all owned titles.

JSON note inputs are strict and forbid extras. Title is 1–100 characters; body 1–2000; both are trimmed and rejected if empty afterward. Completed is a JSON Boolean, not a string. Server-generated id/owner/timestamp cannot be written by the client. PUT requires all writable fields. PATCH preserves omissions, retains explicitly supplied False and rejects explicit null and `{}`.

Username policy: 3–32 ASCII letters/digits/underscores, canonical lowercase with outer whitespace removed. Password: 12–128 characters, **not trimmed**, stored only as a salted Werkzeug scrypt verifier. `SecretStr` masks common representations; it is not encryption. Public models omit passwords/hashes. Sanitised 422 responses omit raw rejected input and exception context.

Failure statuses: **401** with `WWW-Authenticate: Bearer` for missing/invalid authentication; **404** for absent or inaccessible notes; **409** for unavailable usernames; **422** for invalid declared input; **405** for unsupported methods. Independent validation/auth failures do not have a universally promised ordering. No internal SQL traceback is an intentional client response.

## Code map and lifetimes

- `app.py`: guarded loopback Uvicorn entry point.
- `learning_api/__init__.py`: factory, lifespan, sanitised errors, request dependencies, JWT/current-user verification and API routes.
- `learning_api/schemas.py`: strict writable models, validators, replacement/patch rules and public responses.
- `learning_api/database.py`: schema ownership, existing-file connection, bound SQL support and explicit transaction helper.
- `learning_api/static/`: original responsive OpenAPI explorer with safe text rendering and local assets.
- `lesson_support.py`: disposable fictional accounts, token helpers and temporary app/client fixture.
- `instance/`: ignored, automatically created runtime **notes.sqlite** and **signing.key**. Never commit/share these files. This is not Study Hub localStorage or its sync data.

Lifespan initialises owned runtime files. Each request gets a separate SQLite connection via a `yield` dependency and closes it in `finally`. Sync database/hash routes use `def`, avoiding synchronous SQLite/hash calls directly in an async handler’s event loop. `check_same_thread=False` accommodates sync-worker execution, not arbitrary concurrent sharing. A helper starts `BEGIN IMMEDIATE`, commits on success and rolls back on failure. The read-list snapshot uses this simple transaction too; it serialises more work than an optimised read-only strategy. This is a small local teaching workload.

Initialisation creates new files exclusively, checks known schema version/table/column shape on reuse and refuses unfamiliar schemas without dropping/resetting them. This is not a general migration framework or proof of every constraint on an externally altered database. A wrong-length signing key stops startup without replacing it. Keep data and key together on restart. No reset button is provided.

## Authentication policy and limits

JWTs use a fixed **HS256** verification allowlist and a random **32-byte** local signing key. Required claims: `sub`, `exp`, `iat`, `nbf`, `jti`, `iss`, `aud`; `kind` must be access and shapes must match. Issuer: `studyhub-w39-local`; audience: `studyhub-w39-clients`; lifetime: **900 seconds**. Tokens contain no password or note body. Signed claims are readable, not encrypted.

Every protected request verifies signature/claims **and** a live matching token-session row/user/expiry. Logout removes that specific jti. Expired login rows are cleaned on later successful login. Per-resource SQL requires both the id and verified owner; identity alone is insufficient. Unknown username and incorrect password use the same generic failure; a dummy hash avoids an obvious skipped-verification path but does not claim perfect timing equality.

The password-form endpoint demonstrates FastAPI’s local OAuth2 password-flow tools. It is **not a modern third-party browser login deployment recipe**; authorization-code with PKCE is a different flow. CORS is not authentication or a non-browser access boundary. This API has no cookie login, and the same-origin explorer explicitly adds bearer headers. Safe rendering helps reduce injection risks but does not make all future frontend changes automatically safe.

This project has **no** public HTTPS deployment, refresh tokens, MFA, password recovery, account lockout/login throttling, whole-request byte cap, distributed database, general migrations or production monitoring. Do not expose it publicly by changing the bind address. GitHub Pages hosts the lessons/source but cannot run FastAPI. Week 40’s roadmap replaces the SQLite access implementation with SQLAlchemy; Week 39 retains direct `sqlite3` to make that transition teachable.

## Verification from the repository root

Using the environment where requirements were installed:

```powershell
python -B tests/python-week39-project.py
node tests/python-week39.cjs
node tests/python-week39-browser.cjs
node tests/python-week39-project-browser.cjs
node tests/python-learning-smoke.cjs
```

The authoring generator `scripts/python-week39.py` executes all 108 example/solution blocks in disposable folders before inserting only new Week 39 lesson data. Static verification compares all earlier lessons and all application/storage code against the previous commit. Browser checks use isolated profiles and fictional progress, not the learner’s actual browser state. They cover lesson rendering, quiz saving, navigation, notes/progress refresh, studied-only practice/review, mobile themes and backup/import regression. API verification covers real local CRUD, ownership, validation, token failures/revocation, hashing, persistence/schema refusal and the offline explorer.

## Primary references

- [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Sync/async reasoning](https://fastapi.tiangolo.com/async/)
- [Lifespan](https://fastapi.tiangolo.com/advanced/events/)
- [Response models](https://fastapi.tiangolo.com/tutorial/response-model/)
- [Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [OAuth2/JWT learning tools](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [Pydantic models](https://docs.pydantic.dev/latest/concepts/models/)
- [PyJWT verification](https://pyjwt.readthedocs.io/en/stable/usage.html)

All explanations, fixtures, exercises and explorer UI here are original. External references are optional further reading; no internet is needed to read the embedded lessons after the page has been saved/cached.
