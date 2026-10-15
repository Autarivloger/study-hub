# Python Week 38 — Flask with databases & authentication

Six days, **36 parts**, **72 practice prompts**, **82 explained quiz questions**
and **108 executed examples/solutions**. Existing notes, completion,
navigation, search, learned-only review/practice and Day 7 use this material
through the current Study Hub architecture.

No old course material, application function, localStorage schema, backup,
import or sync mechanism is changed. The account system is a **separate local
Python project**, not a new login requirement for Study Hub.

## Learning sequence

1. **6 parts:** ORM objects/rows; URI/extension/engine; application context;
   constraints and rollback; create_all versus migration; modern result shapes.
2. **6 parts:** create/flush/commit; bound reads/literal search; tracked
   updates; deletion; authorised pagination; atomic recovery.
3. **6 parts:** one-to-many; many-to-many; joins/counts; loading strategies;
   foreign keys/delete behaviour; owner predicates/mass-assignment boundary.
4. **6 parts:** salted password verifiers; canonical usernames; registration;
   login/session rotation; per-request user loading; server session revocation.
5. **6 parts:** object-level access; CSRF; stored-text escaping; query/field
   control; local cookies/keys/data; negative-case access audit.
6. **6 parts:** config/factory isolation; auth/post blueprints; full request
   trace; durable local journal; acceptance suite; complete milestone.

Do not rush because a part is called a day. Explain a concept, predict and
run its example, solve both exercises without revealing solutions, then do
the quiz and record your own notes.

## Project files

Keep this complete structure:

    app.py
    lesson_support.py
    requirements.txt
    .gitignore
    study_app/
      __init__.py
      config.py
      extensions.py
      models.py
      security.py
      auth.py
      posts.py
      templates/
        base.html  home.html  auth.html  posts.html
        form.html  detail.html  error.html
      static/style.css

Most Day 1–2 snippets are complete in-memory scaffolds. When a snippet imports
lesson_support, keep that file and the whole study_app package beside it.
The helper builds isolated fictional accounts/data; it does not open a real
learner database, signing key or credential. No previous snippet state is
required.

## Install, initialise once, run locally

    python -m pip install -r requirements.txt
    python -m flask --app study_app init-db
    python app.py

Open **http://127.0.0.1:5000** on this computer; stop with Ctrl+C.
If port 5000 is busy:

    python -m flask --app study_app run --host 127.0.0.1 --port 5001

Open the matching port. Keep debug off for the supplied local app.
The development server is not a production internet deployment.
**GitHub Pages publishes the lessons/source, not a running Flask backend.**

Verified with Python 3.12.14, Flask 3.1.3, Flask-SQLAlchemy 3.1.1 and
SQLAlchemy 2.1.4. Initial package installation needs internet; installed
examples, local browser project and embedded lessons work offline.
There are no CDN, remote font, JavaScript or external account/API dependencies.

The init-db command creates schema and three known tags (flask, sql, practice).
It creates **no default account/password** and refuses a database that already
has tables. It is not a reset command or general migration engine.

### Browser exercise

1. Register a fictional username and a new **practice-only** passphrase.
   Never reuse an actual GitHub, email or personal account password.
2. Sign in, create a post with tags, read it, edit it and search its title.
3. Open another browser profile/private session, register another fictional
   account and create a separate post.
4. Try the first post's URL from the second account. Detail/edit/delete should
   return 404 and leave the first owner's record intact.
5. Sign out. The current server login record is revoked.
6. Stop/restart the app, sign in again and confirm posts persist.
7. Test labels, keyboard focus, empty state, narrow-screen wrapping and
   previous/next pages. Post lists use five records per page.

## Schema and state

- User: canonical unique username and a password_hash, not plaintext.
- Post: required author foreign key, title and body. Title 1–100 characters;
  body 1–2000 after declared outer-whitespace trimming; NUL rejected.
- Tag: shared known label.
- post_tags: composite post/tag key; explicit association rather than a CSV
  string. Removing a post removes its links, not the shared tag objects.
- LoginSession: random 64-character id, user foreign key and one-hour
  expiry. The cookie stores its id, not a password/hash or private post body.
- Factory attaches foreign-key enforcement to every owned SQLite connection.
- Models use modern select/scalars/session APIs, not a new dependency on the
  legacy Model.query interface.

Normal local mode creates an ignored **instance/journal.sqlite** database and
**instance/signing.key**. Flask's default instance path is used unless an
explicit owned test path is supplied. These artifacts persist across restart.
An existing valid 32-byte signing-key file is preserved; an invalid file stops
rather than being silently replaced.

Runtime keys/data are excluded from source commits. This is not encryption
or an operating-system access-control guarantee; protect local files and any
local backups. Do not put them in a public repository.
For a simple backup exercise, stop the app and preserve the owned instance
directory in a protected local backup location. Never publish that backup.

create_all creates missing tables, not changed columns on existing tables.
Use a reviewed migration and verified backup for schema evolution. Do not
delete a learner journal to make new model code fit it.

## Account and request policies

- Username: 3–32 ASCII letters/digits/underscores, lowercased with outer
  whitespace removed. This is a deliberate beginner identity policy, not a
  claim to solve all Unicode/collation identity issues.
- Password: 12–128 characters, never silently trimmed/lowercased. Werkzeug's
  purpose-built salted verifier is stored; check_password_hash verifies it.
- Registration uniqueness is enforced in storage. Integrity failures roll
  back and never overwrite an existing verifier.
- Login failures use a generic message. A dummy verifier reduces the obvious
  unknown-account fast path for normal-sized candidates; this does not
  promise perfect timing indistinguishability.
- Successful login creates a new database login record, clears old session
  fields and sets a new cookie identifier/form-token context.
- A request loader resolves the server login and expiry into request-local
  g.user. Cookie presence alone is not sufficient.
- Logout deletes only the current LoginSession record, so replaying its old
  signed cookie does not restore access. Another browser's independent
  login record is unaffected. Expired records are rejected; periodic
  database cleanup is not implemented.
- The default signed cookie is not encrypted. It contains only the small
  login id/form token/feedback state; never put credentials/private posts in it.
- HttpOnly and SameSite=Lax are set. Secure=False is deliberate for loopback
  HTTP; actual HTTPS deployment requires the appropriate cookie/deployment
  configuration.
- Every state-changing POST requires a matching session token, including
  register/login/logout. Missing, Unicode, oversized, cross-session or stale
  tokens fail before writes.
- Every private route checks authentication. Every object detail/edit/delete
  query also requires the current author's key; wrong-owner/missing ids both
  return 404.
- Only title/body/known tags are editable. A submitted author_id is ignored;
  ownership is derived from the verified account. Unknown/duplicate/excess
  tags are rejected.
- ORM expression values are bound. Literal title search escapes LIKE wildcard
  characters. An ORM does not make interpolated raw SQL safe.
- HTML templates autoescape stored names/posts/drafts; no user text is
  interpreted as template source or marked safe. Multiline bodies remain
  plain text with pre-wrap styling.
- Approved writes commit then redirect with short flash feedback. Invalid
  fields return 400 with bounded escaped drafts and no mutation.
- List/query input is bounded: at most 80 search characters, pages 1–1000,
  five owner-filtered records per page. Relationship collections use planned
  selectinload on the list. Apply owner filtering before both rows and totals.
- Request bodies are capped at 32 KiB. Helpful error pages keep their
  400/404/405/413 status; 405 responses retain the Allow header.

## Explicit local teaching scope

This implements real local credential verification and per-user database
access, unlike Week 37's display-name-only gate. It is still **not an internet
production account service**. It has no email verification, password reset,
MFA, sign-in throttling, account deletion, key rotation/backup automation,
session-renewal policy or complete operational deployment.

Use fictional accounts and loopback only. A broader deployment needs a
reviewed threat model and those additional controls.
It never reads, moves or clears Study Hub progress, localStorage, notes,
backups, Gist settings or real existing passwords/tokens.

## Source architecture

extensions.py owns the unbound ORM extension; models.py owns schema and
relationships. config.py defines local defaults. security.py contains small
token/input helpers. auth.py owns account/current-user flow; posts.py owns
owner-scoped CRUD. The factory configures the app and registers two blueprints.
Templates share one layout and use local CSS.

## Verification

All 108 snippets execute with fresh globals and owned temporary resources.
Public helper/package files are copied into each snippet's practice folder;
no existing real instance directory is read.
Static checks compare every previous lesson and all surrounding application/
storage code with the pre-Week-38 baseline.

Project tests cover actual token-protected registration/login/CRUD/logout,
hash-only storage, duplicate rollback, wrong-owner GET/POST operations,
unchanged data after rejection, malformed fields/tags, literal search,
signed-cookie separation/tampering, expiry/revoked-cookie replay, SQLite
constraints/link cleanup, non-destructive init and file-backed restart/key
persistence. Real loopback-browser checks cover the account/post flow,
local stylesheet, labels/keyboard target and mobile layout.
Study Hub tests cover all new parts/quizzes, navigation, notes/progress/search,
learned-only practice/review, mobile dark/light and console errors.
The existing learning smoke suite verifies actual backup/import merge/replace.

## Primary references

Original explanations, exercises, fictional fixtures and local project source
were checked against:

- [Flask-SQLAlchemy quickstart](https://flask-sqlalchemy.palletsprojects.com/en/stable/quickstart/)
- [SQLAlchemy relationships](https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html)
- [SQLAlchemy session basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- [SQLite foreign-key support](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#foreign-key-support)
- [Flask account-view tutorial](https://flask.palletsprojects.com/en/stable/tutorial/views/)
- [Flask blueprints](https://flask.palletsprojects.com/en/stable/blueprints/)
- [Flask web security](https://flask.palletsprojects.com/en/stable/web-security/)
- [Werkzeug security utilities](https://werkzeug.palletsprojects.com/en/stable/utils/#module-werkzeug.security)

References are optional further reading, not offline runtime dependencies.
