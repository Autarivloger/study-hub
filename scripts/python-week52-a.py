L(0, '1. Choose a problem you can finish and explain',
  'Choose one user, one useful outcome and a bounded first release.',
  [('Capstone', 'A project that combines earlier skills into working behavior you can demonstrate, explain and maintain independently.'),
   ('Version-one boundary', 'The deliberately limited set of user outcomes you commit to finish before adding optional features.'),
   ('StudyLog', 'Our original single-owner reference capstone: log study sessions, correct entries, see totals and preserve records in SQLite. It is separate from Study Hub.')],
  "The final course module is a sequence of milestones, not a deadline that requires you to rush a project into seven calendar days. Take additional sessions whenever a decision or implementation is not yet clear. Reading a reference solution is useful preparation; independently reproducing and changing it is the learning goal.\n\nChoose a problem with a real user outcome. 'Use FastAPI, SQLite and Docker' is a technology list. 'A learner can record a study session, correct a mistake and still see it tomorrow' describes useful behavior. Our reference project is StudyLog, a small independent app for one owner.\n\nLimit the first release to session records, editing/deleting with conflict checks, summaries and a backup/restore rehearsal. Multiple accounts, cloud synchronization and recommendation models would substantially expand the design. Put those in a later plan. A finished coherent slice gives you better evidence than many unrelated half-built features.",
  r'''candidates = [
    {"name": "StudyLog", "useful": 5, "familiar": 5, "scope_cost": 2},
    {"name": "Multi-user learning marketplace", "useful": 4, "familiar": 2, "scope_cost": 5},
]
for candidate in candidates:
    candidate["selection_score"] = candidate["useful"] + candidate["familiar"] - candidate["scope_cost"]
chosen = max(candidates, key=lambda item: item["selection_score"])
print("Illustrative selection:", chosen["name"])
print("Scoring supports a decision; it does not prove demand")''',
  'Write one user/outcome statement for your own version of the capstone.',
  r'''user, action, value = "one learner", "record and correct study sessions", "retain a useful history"
print(f"For {user}, let them {action} so they can {value}.")''',
  'Separate essential outcomes from optional expansion.',
  r'''features = {"record session": "v1", "restart persistence": "v1", "cloud social feed": "later"}
print("First release:", [name for name, scope in features.items() if scope == "v1"])
print("Later:", [name for name, scope in features.items() if scope == "later"])''',
  [('What defines a useful capstone?', 'A demonstrable user outcome and explainable implementation', 'The largest technology list', 'A fixed number of calendar days', 'The project should demonstrate working behavior and your judgment.'),
   ('Must you compress learning to finish in seven days?', 'No, use additional sessions as needed', 'Always', 'Only if you skip tests', 'The day labels organize milestones rather than impose an unsafe deadline.')],
  'Choose a huge feature list because every technology sounds useful.',
  'Choose one user outcome and finish a deliberately bounded release.',
  'A realistic scope lets you test the whole path and understand what you built.',
  syntax='user -> problem -> observable outcome -> first-release boundary')

L(0, '2. Turn a user story into acceptance examples',
  'Describe success and failure with concrete inputs and observable answers.',
  [('Acceptance example', 'A concrete scenario showing what a user must observe for a requirement to be met.'),
   ('SessionInput', 'The supplied Pydantic validation model in capstone/domain.py. It requires an ISO day, nonblank subject and strict integer minutes 1..1440.'),
   ('ValidationError', 'Pydantic rejects data that fails the declared contract; it does not silently turn a boolean or decimal into a minute count.')],
  "A user story such as 'I can record my study' is too broad to test alone. Add specific examples. Recording Python/25 and Japanese/15 should yield two records and forty minutes. Correcting Python to thirty should yield forty-five. Restarting the server should preserve that result.\n\nAlso define failures before writing the happy path. True is not a minute count even though Python bool subclasses int. An invalid calendar date is rejected. An edit using an old version should not overwrite a newer correction. A note containing angle brackets should display as text, not execute as browser markup.\n\nThe executable example inspects the shared validation model rather than a hypothetical checklist. You will build the storage and HTTP layers in later milestones; the supplied reference lets you run each contract now. Write your own acceptance examples in SPEC.md so a future test or reviewer can evaluate the same promise.",
  r'''from pydantic import ValidationError
from capstone.domain import SessionInput
entry = SessionInput(day="2026-10-19", subject="  Python  ", minutes=25)
print(entry.model_dump())
try:
    SessionInput(day="2026-10-19", subject="Python", minutes=True)
except ValidationError:
    print("Boolean minute count rejected")''',
  'Translate two valid sessions into a checkable total.',
  r'''from capstone.domain import SessionInput
entries = [SessionInput(day="2026-10-19", subject=subject, minutes=minutes)
           for subject, minutes in [("Python", 25), ("Japanese", 15)]]
print("Sessions:", len(entries), "minutes:", sum(entry.minutes for entry in entries))''',
  'Verify a real leap day while rejecting an invalid non-leap date.',
  r'''from pydantic import ValidationError
from capstone.domain import SessionInput
for day in ["2024-02-29", "2026-02-29"]:
    try:
        SessionInput(day=day, subject="Reading", minutes=10)
        print(day, "accepted")
    except ValidationError:
        print(day, "rejected")''',
  [('Which acceptance example is stronger?', 'Correcting 25 to 30 changes a 40-minute total to 45', 'The app is professional', 'The code is modern', 'Concrete input and output can be checked independently.'),
   ('Should True be accepted as a minute count in this contract?', 'No', 'Always', 'Only on weekdays', 'The domain deliberately requires a strict integer rather than a yes/no flag.')],
  'Write requirements that cannot distinguish success from failure.',
  'State concrete valid, invalid and restart/conflict scenarios.',
  'Acceptance examples become the shared language of your implementation and tests.',
  syntax='Given records -> When an operation occurs -> Then observe the specified result')

L(0, '3. Prioritize a complete release over feature accumulation',
  'Connect each essential feature to evidence and postpone unrelated expansion.',
  [('MVP', 'The smallest useful coherent product version, including the reliability needed for its promised use.'),
   ('Dependency order', 'Some tasks unblock others: a validated record and repository enable the API and browser workflow.'),
   ('Scope change', 'An explicit revision of release commitments, with time, design and test consequences.')],
  "Small does not mean fragile. If your product promises that records survive tomorrow, persistence and a restart test belong in the minimum useful release. If it promises corrections, editing errors and stale versions belong in the release too. A decorative chart cannot substitute for those obligations.\n\nOrganize tasks by the user path: validated input, stored record, readable list, correction, summary, backup and operational checks. Build an end-to-end slice early so integration failures appear while the design is still easy to change. Add refinements after the core path works.\n\nIf you later choose to add multiple users, acknowledge that identities, permissions, data ownership and testing change. That is not just a new dropdown. Keep a later list so useful ideas are preserved without quietly expanding the current commitment. Your chosen scope should remain visible in the specification and review notes.",
  r'''backlog = [
    ("validated add/list", "essential"), ("restart persistence", "essential"),
    ("safe correction", "essential"), ("animated achievements", "later"),
    ("multi-user accounts", "later"),
]
print("Committed:", [task for task, priority in backlog if priority == "essential"])
print("Deferred ideas:", [task for task, priority in backlog if priority == "later"])''',
  'Identify which proposed task supports a current acceptance promise.',
  r'''requirements = {"retain history": ["database", "restart test", "backup rehearsal"],
                "correct mistakes": ["edit", "version conflict test"]}
for outcome, work in requirements.items():
    print(outcome + " -> " + ", ".join(work))''',
  'Find an unfinished essential task before declaring the release done.',
  r'''tasks = {"add/list": True, "edit": True, "restart check": False}
print("Remaining essential work:", [task for task, done in tasks.items() if not done])''',
  [('Does MVP mean omitting promised persistence checks?', 'No', 'Always', 'Only for SQLite', 'Reliability supporting the chosen outcome is part of the useful minimum.'),
   ('What should happen when multi-user scope is added?', 'Revisit design, ownership and tests explicitly', 'Only add a label', 'Skip the specification', 'A scope change can alter the system boundary and required evidence.')],
  'Keep adding visible features while the promised save/restart path remains untested.',
  'Finish and verify a coherent essential user path first.',
  'Prioritization protects the learning and reliability of the release you actually intend to finish.',
  syntax='essential outcome -> implementation tasks -> observable evidence -> later ideas')

L(0, '4. Specify data, ordering and error contracts',
  'Write the domain rules callers and the interface can rely on.',
  [('Canonical representation', 'A deliberate consistent stored form; our day uses YYYY-MM-DD and subject boundaries are trimmed.'),
   ('Ordering contract', 'Sessions are listed by day descending then id descending, making ties deterministic.'),
   ('Version field', 'A positive revision number used to detect edits based on stale records.')],
  "A database schema is not the whole contract. Decide how dates are represented, what text normalization is intentional and whether minutes are a strict integer. Define maximum field lengths and what unknown request fields do. These choices affect both API consumers and browser validation.\n\nStudyLog stores real ISO calendar days, a trimmed nonblank subject, integer minutes from one through 1440 and an optional note. Notes retain their text. Listing uses date descending and id descending, while summaries group by subject. Editing increments a version so the server can reject a stale correction.\n\nWrite these rules before different layers invent conflicting interpretations. HTML field limits help the user, but the server must enforce its own contract. A required input can still be absent in a direct API call. The examples show actual model behavior, including rejection of an extra field.",
  r'''from capstone.domain import SessionInput
from pydantic import ValidationError
entry = SessionInput(day="2026-10-19", subject="  日本語  ", minutes=15, note="Keep my spacing  ")
print("Canonical subject:", repr(entry.subject))
print("Preserved note:", repr(entry.note))
try:
    SessionInput.model_validate({**entry.model_dump(), "unknown": 1})
except ValidationError:
    print("Unknown field rejected")''',
  'Check the accepted endpoints of the minute range.',
  r'''from capstone.domain import SessionInput
for minutes in [1, 1440]:
    print(SessionInput(day="2026-10-19", subject="Practice", minutes=minutes).minutes)''',
  'Create a valid edit model with its original revision.',
  r'''from capstone.domain import SessionEdit
edit = SessionEdit(day="2026-10-19", subject="Python", minutes=30, version=1)
print("Submitted revision:", edit.version)
print("Corrected minutes:", edit.minutes)''',
  [('Why define a tie-breaker for sessions on the same day?', 'To make the listing order deterministic', 'To hide duplicate data', 'To avoid all indexes', 'Date alone does not specify the order of equal-date records.'),
   ('Can HTML input limits replace server validation?', 'No', 'Always', 'Only for trusted browsers', 'Other clients and malformed requests can bypass the browser controls.')],
  'Let the browser, API and database silently accept different data meanings.',
  'Define one public contract and enforce it at the relevant boundaries.',
  'The specification makes both valid behavior and deliberate rejection predictable.',
  syntax='day: ISO date; subject: nonblank; minutes: strict int 1..1440; note: <=1000; edit: version')

L(0, '5. Identify failure cases before the happy path grows',
  'Turn likely data loss, validation and exposure failures into planned tests.',
  [('Risk-driven test', 'A check selected because a failure would matter to a promised user outcome.'),
   ('Lost update', 'One client silently overwrites a change made since it read the record.'),
   ('Uncertain write', 'A request can time out after the server committed; blindly retrying a creation can produce a duplicate.')],
  "Ask how a plausible user action could fail. Two tabs may edit the same session. A server may restart after saving. A malformed value may reach the API directly. A browser may display a note containing markup-like text. These are concrete tests, not abstract reasons to make the project enormous.\n\nStudyLog detects stale updates with a version comparison. It writes to SQLite before returning success. The browser displays strings using textContent. Its UI suppresses an accidental simultaneous save click, but the API does not promise exactly-once POST across arbitrary network retries. If a creation times out, check the current list before retrying.\n\nKeep limits honest. A shared access token is one-owner access, not a multi-user permission system. A bounded list response does not make every database query constant-cost. Choose protections and tests appropriate to the stated release, and write future risks into the next-version plan rather than claiming they are solved.",
  r'''from pydantic import ValidationError
from capstone.domain import SessionInput
invalid = [{"minutes": True}, {"minutes": -1}, {"subject": "  "}, {"day": "2026-02-29"}]
for changes in invalid:
    payload = {"day": "2026-10-19", "subject": "Python", "minutes": 25, **changes}
    try:
        SessionInput.model_validate(payload)
    except ValidationError:
        print("Rejected:", next(iter(changes)))''',
  'Map a likely failure to the evidence that would detect it.',
  r'''risks = {"lost edit": "stale-version update returns 409", "restart loss": "fresh process reads saved record",
         "broken backup": "open snapshot and read useful records"}
for risk, evidence in risks.items():
    print(risk + " -> " + evidence)''',
  'Explain why a timeout does not establish that no record was created.',
  r'''events = ["server commits record", "response is lost", "client sees timeout"]
print(" -> ".join(events))
print("Before retry: inspect current records or design an idempotent creation contract")''',
  [('Does a client timeout prove a server write failed?', 'No', 'Always', 'Only for JSON', 'The server may have committed before the response was lost.'),
   ('Does a shared token provide per-user record ownership?', 'No', 'Always', 'Only on localhost', 'Single-owner access and multi-user authorization are different contracts.')],
  'Assume retries, browser controls and a successful copy eliminate every failure.',
  'Name likely failures and verify the exact guarantees your release implements.',
  'A useful risk list leads to focused tests and honest boundaries.',
  syntax='failure -> user impact -> implemented protection -> regression/evidence -> remaining limit')

L(0, '6. Run one vertical slice before expanding the project',
  'Demonstrate validated input, database persistence and a readable API result together.',
  [('Vertical slice', 'One complete path through the relevant layers, rather than finishing all isolated layers before integration.'),
   ('create_app', 'The reference factory in capstone/api.py. It receives a database path, creates the HTTP application and keeps test instances isolated.'),
   ('TestClient', 'FastAPI test adapter for request/response checks inside the test process. It is not an external network or second-device deployment.')],
  "Build one useful path early: submit a session, store it and retrieve a summary. This reveals mismatched names, validation assumptions and transaction behavior before the feature list grows. The supplied reference lets you observe that path while learning how each layer is implemented.\n\nEach example uses a new synthetic database in its own lesson folder. Creating two TestClient contexts against that same file can demonstrate application-instance persistence, but it is not yet a real server-process restart. Later smoke.py checks actual localhost processes separately.\n\nYour first independent milestone is to reproduce the slice without copying unexplained code. Follow the request from SessionInput through Store.add to SQLite and back to a JSON response. Then make one small change, predict its effect and add a test. The diagram shows how acceptance examples connect to an integrated result.",
  r'''from pathlib import Path
from fastapi.testclient import TestClient
from capstone.api import create_app
with TestClient(create_app(Path("slice.sqlite"))) as client:
    response = client.post("/api/sessions", json={"day": "2026-10-19", "subject": "Python", "minutes": 25})
    print("Create status:", response.status_code)
    print("Read minutes:", client.get("/api/sessions/1").json()["minutes"])
    print("Total minutes:", client.get("/api/summary").json()["minutes"])''',
  'Verify the slice rejects an invalid record without adding a row.',
  r'''from pathlib import Path
from fastapi.testclient import TestClient
from capstone.api import create_app
with TestClient(create_app(Path("slice.sqlite"))) as client:
    print("Invalid:", client.post("/api/sessions", json={"day": "2026-10-19", "subject": "Python", "minutes": 0}).status_code)
    print("Retained count:", client.get("/api/summary").json()["sessions"])''',
  'Reopen the same file through a new app instance and retrieve the saved record.',
  r'''from pathlib import Path
from fastapi.testclient import TestClient
from capstone.api import create_app
database = Path("slice.sqlite")
with TestClient(create_app(database)) as client:
    client.post("/api/sessions", json={"day": "2026-10-19", "subject": "Reading", "minutes": 15})
with TestClient(create_app(database)) as client:
    print("New app instance sees:", client.get("/api/summary").json()["minutes"])
print("This check uses one test process; real process restart is checked later")''',
  [('What does a vertical slice demonstrate?', 'An integrated user path through the needed layers', 'Only a directory tree', 'Every future feature', 'It tests that the boundaries agree on one useful behavior.'),
   ('Is TestClient proof of a public deployment?', 'No', 'Always', 'Only if SQLite is used', 'Its request/response checks occur within a test process.')],
  'Call isolated function tests an already-deployed end-to-end service.',
  'Name the tested boundary and add real process/browser checks at later milestones.',
  'Early integration supports understanding without overstating what has been demonstrated.',
  syntax='POST validated session -> SQLite commit -> GET record/summary -> acceptance result',
  diagram=('From acceptance example to a working slice', ['Choose one learner outcome', 'Define valid input and observable errors', 'Connect validation, storage and HTTP', 'Create and retrieve a synthetic session', 'Add evidence before expanding scope'], 'The first slice uses the supplied reference; independent implementation and real process checks are later milestones.'))

L(1, '1. Keep domain, storage and HTTP responsibilities clear',
  'Trace a record through a small architecture with explicit ownership.',
  [('Domain layer', 'Validation and canonical data meaning: date, subject, minutes and edit version.'),
   ('Repository', 'The Store class owns parameterized SQL, transaction boundaries, ordering and persistence.'),
   ('HTTP adapter', 'The API maps requests to domain/repository operations and expected failures to HTTP statuses.')],
  "Architecture helps you reason about a change. If the minute range changes, begin with the domain rule and its database constraint. If the response format changes, inspect the HTTP adapter and browser consumer. If persistence fails, inspect the repository and filesystem path. Keeping these responsibilities visible reduces guesswork.\n\nThe reference uses domain.py, store.py, api.py and a static browser page. The layers are small modules rather than a large framework of interfaces. Store operations can be exercised directly without starting a server, and the API factory accepts a test database path.\n\nAvoid splitting every line into a new abstraction. A boundary earns its place when it separates responsibilities or makes a meaningful test possible. The example writes directly through the validated repository path; the previous slice showed the same operation through HTTP. Both should honor the same domain meaning.",
  r'''from pathlib import Path
from capstone.domain import SessionInput
from capstone.store import Store
entry = SessionInput(day="2026-10-19", subject="Python", minutes=25)
store = Store(Path("architecture.sqlite"))
record = store.add(entry)
print("Stored id:", record["id"])
print("Repository summary:", store.summary()["minutes"])''',
  'Identify the source file responsible for each boundary.',
  r'''from pathlib import Path
for responsibility, name in [("validation", "domain.py"), ("SQL", "store.py"), ("HTTP", "api.py")]:
    print(responsibility, (Path("capstone") / name).is_file())''',
  'Read the stored record through a newly constructed repository.',
  r'''from pathlib import Path
from capstone.domain import SessionInput
from capstone.store import Store
path = Path("architecture.sqlite")
record = Store(path).add(SessionInput(day="2026-10-19", subject="SQL", minutes=20))
print(Store(path).get(record["id"])["subject"])''',
  [('Which layer owns transaction and SQL behavior?', 'Repository', 'Browser heading text', 'Release notes alone', 'Store is the persistence boundary.'),
   ('Should every line become a separate abstraction?', 'No, split by useful responsibility and test boundary', 'Always', 'Only for SQLite', 'Architecture should make reasoning easier rather than add ceremony.')],
  'Put SQL, request parsing and HTML updates into one untestable operation.',
  'Keep a few clear boundaries and trace the same contract across them.',
  'A useful architecture gives each change a discoverable home.',
  syntax='browser -> HTTP adapter -> validated domain input -> repository -> SQLite',
  diagram=('StudyLog responsibility boundaries', ['Browser: inputs, feedback and safe text display', 'HTTP: request, access and status mapping', 'Domain: strict values and canonical meaning', 'Repository: SQL, transactions and versions', 'SQLite: persistent records and constraints'], 'Each operation opens its own connection; the browser and server do not read Study Hub localStorage.'))

L(1, '2. Design a schema and a deliberate migration boundary',
  'Inspect columns, constraints, indexes and the recorded schema version.',
  [('Schema', 'The database structure and constraints that define stored records.'),
   ('PRAGMA user_version', 'An application-controlled integer used here to mark schema version 1; SQLite does not invent your migration plan.'),
   ('Database constraint', 'A storage-level rule such as minute range or required text that protects against invalid direct writes too.')],
  "The sessions table stores identity, day, subject, minutes, note and version. The id is a stable record identity, not a display row position. Minutes have a database constraint in addition to request validation. A day/id index supports the declared list/filter pattern.\n\nInitialization accepts an empty database or the supported version-one schema. It rejects an unknown future version and a nonempty unversioned database rather than resetting it. This is an intentionally small migration policy: it does not pretend that creating a table automatically upgrades every old database safely.\n\nWhen a later release changes the schema, design and test a migration using a copy, take a snapshot and define rollback/compatibility behavior. Do not change user_version alone to force an old file through startup. The following code inspects the actual reference database instead of drawing a schema that might disagree with it.",
  r'''from pathlib import Path
from capstone.store import Store
store = Store(Path("schema.sqlite"))
with store.connection() as connection:
    print("Schema version:", connection.execute("PRAGMA user_version").fetchone()[0])
    print("Columns:", [row[1] for row in connection.execute("PRAGMA table_info(sessions)")])
    print("Indexes:", [row[1] for row in connection.execute("PRAGMA index_list(sessions)")])''',
  'Inspect the minute constraint in the table definition.',
  r'''from pathlib import Path
from capstone.store import Store
with Store(Path("schema.sqlite")).connection() as connection:
    definition = connection.execute("SELECT sql FROM sqlite_master WHERE name='sessions'").fetchone()[0]
print("Minute constraint present:", "BETWEEN 1 AND 1440" in definition)''',
  'Verify an unknown schema version is refused rather than erased.',
  r'''import sqlite3
from pathlib import Path
from capstone.store import Store
with sqlite3.connect("future.sqlite") as connection:
    connection.execute("PRAGMA user_version=99")
connection.close()
try:
    Store(Path("future.sqlite"))
except RuntimeError:
    print("Unsupported version rejected")''',
  [('Does setting user_version automatically migrate columns?', 'No', 'Always', 'Only on Windows', 'The application must implement and verify actual schema transformations.'),
   ('What should happen to an unrelated nonempty database file?', 'Refuse initialization and investigate', 'Drop its tables', 'Rename its columns blindly', 'The capstone must not silently adopt or erase unrelated data.')],
  'Reset an unrecognized database so startup appears to succeed.',
  'Reject unsupported schemas and plan migrations with backups and tests.',
  'A migration boundary is part of protecting persistent user work.',
  syntax='inspect version -> supported schema or explicit migration -> verify data -> serve')

L(1, '3. Enforce strict input at a shared validation boundary',
  'Reject ambiguous values and keep normalization intentional.',
  [('Strict field', 'A validation rule that rejects inappropriate coercion, such as strings, floats or booleans for minutes.'),
   ('field_validator', 'A Pydantic hook that applies the project-specific date, subject or note rule.'),
   ('extra=forbid', 'Unknown request fields are rejected instead of silently ignored.')],
  "Framework validation is useful when it matches your domain, not merely because a model exists. A decimal minute value and a yes/no flag should not become a whole-number count by accident. A date-looking string must refer to a real calendar day in the promised format.\n\nSubject whitespace is deliberately trimmed, blank/control-character subjects are rejected, and notes retain ordinary text up to their limit. Unknown fields fail so a misspelled client property does not appear to save successfully while losing information. Document these decisions alongside tests.\n\nThe browser repeats simple required/range hints for usability, but the shared model remains the server-side authority. Validate direct Python/repository examples with that model as well. The API maps request-model failures to 422; you will handle other domain/storage failures separately rather than catching everything as a success.",
  r'''from pydantic import ValidationError
from capstone.domain import SessionInput
for value in [25, "25", 25.0, True]:
    try:
        entry = SessionInput(day="2026-10-19", subject="Python", minutes=value)
        print(repr(value), "accepted:", entry.minutes)
    except ValidationError:
        print(repr(value), "rejected")''',
  'Verify text normalization and the required nonblank subject.',
  r'''from pydantic import ValidationError
from capstone.domain import SessionInput
print(SessionInput(day="2026-10-19", subject="  SQL  ", minutes=10).subject)
try:
    SessionInput(day="2026-10-19", subject="   ", minutes=10)
except ValidationError:
    print("Blank subject rejected")''',
  'Reject a date that uses the wrong representation even if its numbers form a real day.',
  r'''from pydantic import ValidationError
from capstone.domain import SessionInput
for day in ["2026-10-19", "20261019"]:
    try:
        SessionInput(day=day, subject="Dates", minutes=10)
        print(day, "accepted")
    except ValidationError:
        print(day, "rejected")''',
  [('Why forbid unknown fields?', 'To catch client mistakes instead of silently discarding them', 'To remove the need for documentation', 'To make every request valid', 'Unexpected properties often indicate a mismatched or misspelled contract.'),
   ('Where should direct Python callers validate input in these examples?', 'Through SessionInput/SessionEdit before repository writes', 'Only in browser JavaScript', 'Only after storing', 'The shared model keeps the intended domain meaning explicit.')],
  'Coerce every number-like value and ignore unknown input properties.',
  'Apply deliberate strict fields, canonical rules and explicit error behavior.',
  'Validation should prevent silent misunderstandings as well as obvious crashes.',
  syntax='SessionInput.model_validate(payload) -> valid record or ValidationError')

L(1, '4. Keep SQL values as parameters',
  'Treat user strings as data rather than SQL syntax.',
  [('Parameterized SQL', 'Use placeholders and a separate parameter sequence so input values are not parsed as query structure.'),
   ('SQL injection', 'Untrusted text changes query meaning when it is interpolated into SQL source.'),
   ('Static query structure', 'Only project-controlled clauses choose SQL structure; validated data still travels through parameters.')],
  "A subject can contain punctuation, apostrophes or text that resembles a command. Storing it should not change which tables exist. Build a fixed SQL statement with ? placeholders and pass values separately. Do not use f-strings to splice subject text into the query.\n\nThe repository parameterizes both writes and filters. Its optional WHERE clause is chosen from project-controlled constants; the day remains a parameter. This distinction matters: placeholders represent values, not arbitrary table or column names. If an API ever allows selectable ordering, map allowed choices to known query fragments rather than accepting SQL from the caller.\n\nThe example stores a synthetic hostile-looking subject through the normal validated path and verifies the table still works. It is a local correctness/security regression, not an attack against another system. Retain this case because later refactoring can accidentally reintroduce unsafe interpolation.",
  r'''from pathlib import Path
from capstone.domain import SessionInput
from capstone.store import Store
store = Store(Path("parameters.sqlite"))
subject = "x'); DROP TABLE sessions; --"
record = store.add(SessionInput(day="2026-10-19", subject=subject, minutes=5))
print("Stored exactly:", store.get(record["id"])["subject"] == subject)
print("Table still usable:", store.summary()["sessions"] == 1)''',
  'Use a parameter for a subject containing an apostrophe.',
  r'''from pathlib import Path
from capstone.domain import SessionInput
from capstone.store import Store
store = Store(Path("parameters.sqlite"))
store.add(SessionInput(day="2026-10-19", subject="Learner's SQL", minutes=10))
with store.connection() as connection:
    row = connection.execute("SELECT minutes FROM sessions WHERE subject=?", ("Learner's SQL",)).fetchone()
print(row[0])''',
  'Apply a known allowlist for a hypothetical sort choice without accepting SQL fragments.',
  r'''allowed = {"recent": "day DESC,id DESC", "oldest": "day ASC,id ASC"}
choice = "recent"
print("Project-controlled ordering:", allowed[choice])
print("Arbitrary expression accepted:", "DROP TABLE sessions" in allowed)''',
  [('What belongs in the parameter tuple?', 'Input values', 'A whole untrusted SQL statement', 'Only numeric values', 'Placeholders keep values separate from query syntax.'),
   ('Can a placeholder substitute for an arbitrary table name?', 'No, use a project-controlled identifier choice', 'Always', 'Only for dates', 'Identifiers and values occupy different SQL grammar positions.')],
  'Interpolate user subject text into SQL with an f-string.',
  'Keep query structure controlled and pass subject/date values through placeholders.',
  'The stored value remains data even when it resembles a command.',
  syntax='connection.execute("SELECT * FROM sessions WHERE subject=?", (subject,))')

L(1, '5. Give transactions and connections explicit lifetimes',
  'Verify rollback behavior and close a connection after each operation.',
  [('Transaction', 'A group of database changes that commit together or roll back when the operation fails.'),
   ('Connection lifetime', 'The period a database connection remains open. A SQLite transaction context does not itself guarantee that the connection is closed.'),
   ('One connection per operation', 'Each repository method opens, uses and closes its own connection instead of sharing one across request threads.')],
  "Persistent state needs a failure policy. If an operation writes then raises before success, its partial changes should not silently remain. The repository context manager wraps the transaction and closes the connection in a finally block.\n\nBe precise about SQLite's context manager: with connection handles commit/rollback, while explicitly closing the connection is a separate responsibility. The supplied wrapper combines those responsibilities so normal and error paths release the resource. The API uses synchronous handlers for blocking SQLite operations; it does not hide a blocking query inside an async handler.\n\nThe example deliberately raises after an insert. The count remains zero because the transaction rolls back. This establishes an operation boundary; it does not create a transaction across several HTTP requests or independent files. Keep these boundaries small enough to explain and avoid long unrelated work while a write transaction is open.",
  r'''from pathlib import Path
from capstone.store import Store
store = Store(Path("rollback.sqlite"))
try:
    with store.connection() as connection:
        connection.execute("INSERT INTO sessions(day,subject,minutes) VALUES(?,?,?)", ("2026-10-19", "Partial", 10))
        raise RuntimeError("Synthetic failure before operation success")
except RuntimeError:
    print("Operation failed as intended")
print("Retained rows:", store.summary()["sessions"])''',
  'Compare a committed repository add with the earlier rollback case.',
  r'''from pathlib import Path
from capstone.domain import SessionInput
from capstone.store import Store
store = Store(Path("committed.sqlite"))
store.add(SessionInput(day="2026-10-19", subject="Committed", minutes=10))
print("Retained rows:", Store(store.path).summary()["sessions"])''',
  'Verify a storage constraint rejects a negative minute count from direct SQL.',
  r'''import sqlite3
from pathlib import Path
from capstone.store import Store
store = Store(Path("constraints.sqlite"))
try:
    with store.connection() as connection:
        connection.execute("INSERT INTO sessions(day,subject,minutes) VALUES(?,?,?)", ("2026-10-19", "Invalid", -1))
except sqlite3.IntegrityError:
    print("Database constraint rejected invalid write")
print("Rows:", store.summary()["sessions"])''',
  [('Does with sqlite_connection automatically close that connection?', 'No, manage closure separately', 'Always', 'Only when a SELECT runs', 'The transaction context and connection lifetime are distinct responsibilities.'),
   ('Does one repository transaction span several independent HTTP requests?', 'No', 'Always', 'Only when JSON is used', 'A transaction protects its explicitly defined database operation boundary.')],
  'Leave shared connections open and assume a transaction context handles every resource lifetime.',
  'Commit or roll back the operation, then close its connection on every path.',
  'Explicit lifetimes make both failure behavior and request-thread use easier to reason about.',
  syntax='open connection -> transaction -> commit/rollback -> finally close')

L(1, '6. Prepare a repeatable project and CI from the start',
  'State setup, dependencies and required checks before the core build expands.',
  [('Prepared environment', 'A virtual environment with the declared runtime/development dependencies installed.'),
   ('CI matrix', 'The specific interpreter/runner combinations on which automated project checks run.'),
   ('Package data', 'Non-Python runtime files, here the HTML interface, that must be included in the built distribution.')],
  "A project that runs only in your current terminal is hard to maintain. Write the working directory, interpreter requirement and commands in README.md. Keep generated databases, environments, caches and reports out of source control. Store secrets in deliberate runtime configuration rather than lessons or Git.\n\nThe capstone has a pyproject.toml, a pinned direct requirements file, tests and a workflow. A direct requirements file is not a complete hashed transitive lockfile; describe that reproducibility boundary accurately. The package configuration includes the browser HTML, because a wheel missing that file would start an API but fail to display its interface.\n\nCI begins early with validation and repository checks and grows to real HTTP restart/restore and artifact checks. A workflow that merely exists is not evidence that it ran: inspect its actual result. The example reads the real project configuration so the stated package-data and interpreter promises can be checked.",
  r'''from pathlib import Path
import tomllib
config = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
print("Python:", config["project"]["requires-python"])
print("Package assets:", config["tool"]["setuptools"]["package-data"]["capstone"])
print("Tests present:", Path("tests/test_capstone.py").is_file())''',
  'Check the core reproducibility documents are supplied.',
  r'''from pathlib import Path
for name in ["README.md", "SPEC.md", "ARCHITECTURE.md", "requirements-dev.txt"]:
    print(name, Path(name).is_file())''',
  'Distinguish a declared test plan from recorded execution evidence.',
  r'''evidence = {"workflow written": True, "run completed": False}
print("Automation configured:", evidence["workflow written"])
print("Passing run proven:", evidence["run completed"])''',
  [('Why include the HTML in package data?', 'The installed app needs that runtime file', 'It makes tests unnecessary', 'It publishes to GitHub Pages automatically', 'The consumer artifact must contain the interface it serves.'),
   ('Does writing a workflow prove its checks passed?', 'No, inspect an actual run', 'Always', 'Only for Python', 'Configuration and executed evidence are distinct states.')],
  'Rely on an undocumented global environment and an unexecuted CI file.',
  'Provide setup instructions and inspect actual behavior, process and artifact check results.',
  'Repeatable setup is part of the project rather than a note added after someone cannot run it.',
  syntax='environment -> tests -> formatting -> HTTP/restart/restore -> installed artifact',
  shell='python -m pip install -r requirements-dev.txt\npython -m pytest -q\npython -m ruff check .\npython smoke.py --output artifacts/verification.json')
