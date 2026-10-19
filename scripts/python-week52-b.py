L(2, '1. Save a validated session and return its identity',
  'Implement the first create/read path with a committed record and a stable id.',
  [('201 Created', 'The HTTP success status used when this API creates a new session resource.'),
   ('Generated identity', 'SQLite assigns the primary-key id; callers use that identity rather than guessing a list position.'),
   ('Commit before success', 'The repository operation completes its transaction before the API response is returned.')],
  "The first core feature accepts a valid record, inserts it through parameters and returns the saved row. The database assigns identity and starts the version at one. The HTTP adapter should report a creation result only after the persistence operation succeeds.\n\nDo not infer identity from the number of visible rows. Deletion, filtering and pagination mean display positions change. A client edits or reads the id returned by the server. A later GET should return the same stored contract, including any intentional subject trimming.\n\nThe example uses TestClient against a new file. It checks the status, identity and read-back result. That proves this request/repository path inside the test process; later process and browser checks exercise different boundaries. A timed-out POST remains uncertain to a remote client, so this endpoint does not promise exactly-once creation across retries.",
  r'''from pathlib import Path
from fastapi.testclient import TestClient
from capstone.api import create_app
with TestClient(create_app(Path("create.sqlite"))) as client:
    response = client.post("/api/sessions", json={"day": "2026-10-19", "subject": "  Python  ", "minutes": 25})
    saved = response.json()
    print("Status:", response.status_code, "id:", saved["id"], "version:", saved["version"])
    print("Read-back subject:", client.get(f"/api/sessions/{saved['id']}").json()["subject"])''',
  'Create two sessions and use their returned identities.',
  r'''from pathlib import Path
from fastapi.testclient import TestClient
from capstone.api import create_app
with TestClient(create_app(Path("create.sqlite"))) as client:
    ids = []
    for subject in ["Python", "Japanese"]:
        ids.append(client.post("/api/sessions", json={"day": "2026-10-19", "subject": subject, "minutes": 15}).json()["id"])
    print("Returned identities:", ids)''',
  'Show that a rejected create does not add a partial row.',
  r'''from pathlib import Path
from fastapi.testclient import TestClient
from capstone.api import create_app
with TestClient(create_app(Path("create.sqlite"))) as client:
    response = client.post("/api/sessions", json={"day": "2026-10-19", "subject": "Python", "minutes": 2.5})
    print("Rejected status:", response.status_code)
    print("Count:", client.get("/api/summary").json()["sessions"])''',
  [('Which identity should the client use after creation?', 'The id returned by the server', 'The current display row number', 'The last guessed integer', 'The server assigns a stable resource identity.'),
   ('Does a timed-out POST automatically mean no insert occurred?', 'No', 'Always', 'Only if it used SQLite', 'A response can be lost after the transaction commits.')],
  'Return success before the database operation is known to have completed.',
  'Validate, commit the insert and return the saved identity/version.',
  'A useful create endpoint gives the client a concrete resource it can retrieve and correct.',
  syntax='POST /api/sessions -> 201 + saved {id, day, subject, minutes, note, version}')

L(2, '2. Make listing order, filters and page size explicit',
  'Return bounded pages with deterministic ordering and a declared pagination limit.',
  [('Pagination', 'Return a bounded portion of the result rather than every record in one response.'),
   ('limit / offset', 'limit controls page length and offset skips earlier rows in the selected ordering.'),
   ('Moving-page limitation', 'Offset pages can shift if another client inserts/deletes rows between requests; this is not a frozen snapshot.')],
  "A list endpoint needs more than SELECT *. Define which records appear first, how a caller requests another page and what maximum size the server accepts. StudyLog orders by day descending then id descending and allows a limit from one to one hundred.\n\nThe browser asks for ten rows per page. An optional exact-date filter applies to both the list and its displayed totals. Keeping those meanings aligned prevents a page showing one date while its headline silently reports a different scope.\n\nOffset pagination is intentionally simple for this single-owner app. It does not guarantee a stable snapshot while concurrent changes occur. Also distinguish bounded response size from query cost: a summary can still scan many rows, and large offsets can cost additional work. If real usage grows, measure and consider cursor pagination with a suitable contract rather than changing behavior silently.",
  r'''from pathlib import Path
from capstone.domain import SessionInput
from capstone.store import Store
store = Store(Path("pages.sqlite"))
for day, subject in [("2026-10-18", "Older"), ("2026-10-19", "First today"), ("2026-10-19", "Latest today")]:
    store.add(SessionInput(day=day, subject=subject, minutes=10))
print("Page one:", [row["subject"] for row in store.list_sessions(limit=2)])
print("Page two:", [row["subject"] for row in store.list_sessions(limit=2, offset=2)])''',
  'Read only one exact date through the API.',
  r'''from pathlib import Path
from fastapi.testclient import TestClient
from capstone.api import create_app
with TestClient(create_app(Path("pages.sqlite"))) as client:
    for day in ["2026-10-18", "2026-10-19"]:
        client.post("/api/sessions", json={"day": day, "subject": "Python", "minutes": 10})
    print([row["day"] for row in client.get("/api/sessions?day=2026-10-18").json()["items"]])''',
  'Check that the maximum page limit is enforced by the server.',
  r'''from pathlib import Path
from fastapi.testclient import TestClient
from capstone.api import create_app
with TestClient(create_app(Path("pages.sqlite"))) as client:
    print("Limit 100:", client.get("/api/sessions?limit=100").status_code)
    print("Limit 101:", client.get("/api/sessions?limit=101").status_code)''',
  [('Does a page-size limit make all queries constant-cost?', 'No', 'Always', 'Only with an index', 'The response bound and database work are different quantities.'),
   ('Can offset pages shift during concurrent changes?', 'Yes', 'Never', 'Only if dates are invalid', 'Rows can move relative to offsets as the ordered result changes.')],
  'Return an unlimited unordered list and let the browser guess page boundaries.',
  'Define ordering, limits, filters and the concurrency limits of pagination.',
  'A predictable list contract supports both the interface and realistic scaling decisions.',
  syntax='GET /api/sessions?limit=10&offset=0&day=2026-10-19')

L(2, '3. Read records and summaries with meaningful empty states',
  'Distinguish a missing resource from an empty collection and a zero summary.',
  [('404 Not Found', 'A specific requested session id does not exist.'),
   ('Empty collection', 'A valid list request can return zero items with a successful response.'),
   ('COALESCE', 'SQLite expression used here to turn a NULL aggregate sum on no rows into the required zero.')],
  "A missing session and an empty session list are different situations. GET /api/sessions/999 asks for a specific resource and returns 404 if it does not exist. A valid list filter with no matches returns 200 and an empty items list. The summary returns zero sessions and zero minutes.\n\nMake these distinctions usable in the browser. A new learner should see an invitation to add a session rather than a crash caused by assuming the first row exists. A stale edit of a deleted record should explain that it is missing rather than pretending a successful update occurred.\n\nThe summary uses SQL COUNT and SUM with an explicit zero for no rows. It also returns per-subject totals in a predictable order. These values are derived from records, not separately editable counters that could drift from the source data.",
  r'''from pathlib import Path
from fastapi.testclient import TestClient
from capstone.api import create_app
with TestClient(create_app(Path("read.sqlite"))) as client:
    print("Missing record:", client.get("/api/sessions/999").status_code)
    print("Empty items:", client.get("/api/sessions").json()["items"])
    print("Empty summary:", client.get("/api/summary").json())''',
  'Calculate a report from two subjects and repeated sessions.',
  r'''from pathlib import Path
from capstone.domain import SessionInput
from capstone.store import Store
store = Store(Path("read.sqlite"))
for subject, minutes in [("Python", 25), ("Japanese", 15), ("Python", 10)]:
    store.add(SessionInput(day="2026-10-19", subject=subject, minutes=minutes))
print(store.summary())''',
  'Verify a no-match date filter has a valid zero summary.',
  r'''from pathlib import Path
from capstone.store import Store
print(Store(Path("read.sqlite")).summary(day="2026-10-20"))''',
  [('Should an empty valid list request be treated as a missing-resource error?', 'No', 'Always', 'Only for the first user', 'A collection can validly have zero matching records.'),
   ('Why derive the headline total from source records?', 'To avoid an independently edited counter drifting from the data', 'To avoid all queries', 'To hide missing records', 'The records remain the authoritative data for the summary.')],
  'Assume the first row exists and fail on a new empty database.',
  'Return and display explicit empty-list and zero-summary states.',
  'Empty data is a normal part of the product, not merely a test inconvenience.',
  syntax='missing id -> 404; valid empty list -> 200 + []; no-match summary -> count 0 / minutes 0')

L(2, '4. Edit with an atomic version comparison',
  'Prevent a stale client from silently overwriting a newer correction.',
  [('Optimistic concurrency', 'Allow reading normally, then accept a write only if its expected version still matches.'),
   ('409 Conflict', 'This session exists but changed since the client read it; reload and reconcile before retrying.'),
   ('Atomic predicate', 'The UPDATE checks id and version in the same SQL statement that applies the change.')],
  "Imagine two tabs load version one. The first changes minutes from twenty-five to thirty and saves version two. The second still submits version one. Without a version predicate, that old tab could overwrite the correction without knowing it.\n\nThe repository uses UPDATE ... WHERE id=? AND version=? and increments version on success. A zero affected-row count means the requested version no longer matches or the resource is missing. The API distinguishes 409 from 404. Checking the version in a separate earlier SELECT would leave a gap in which another write could occur.\n\nA conflict message should preserve the user's intended edit in the form while asking them to reload/reconcile. Automatically resubmitting the stale edit with the newest version would defeat the protection. This is single-record concurrency control, not a transaction spanning several browser tabs or separate resources.",
  r'''from pathlib import Path
from fastapi.testclient import TestClient
from capstone.api import create_app
with TestClient(create_app(Path("edit.sqlite"))) as client:
    payload = {"day": "2026-10-19", "subject": "Python", "minutes": 25}
    record = client.post("/api/sessions", json=payload).json()
    changed = client.put(f"/api/sessions/{record['id']}", json={**payload, "minutes": 30, "version": 1})
    stale = client.put(f"/api/sessions/{record['id']}", json={**payload, "minutes": 99, "version": 1})
    print("New version:", changed.json()["version"])
    print("Stale status:", stale.status_code)
    print("Retained minutes:", client.get(f"/api/sessions/{record['id']}").json()["minutes"])''',
  'Perform a second intentional edit using the returned current version.',
  r'''from pathlib import Path
from capstone.domain import SessionInput, SessionEdit
from capstone.store import Store
store = Store(Path("edit.sqlite"))
record = store.add(SessionInput(day="2026-10-19", subject="Python", minutes=25))
for minutes in [30, 35]:
    record = store.update(record["id"], SessionEdit(day=record["day"], subject=record["subject"], minutes=minutes, version=record["version"]))
print("Final version:", record["version"], "minutes:", record["minutes"])''',
  'Distinguish editing a missing id from a stale existing record.',
  r'''from pathlib import Path
from fastapi.testclient import TestClient
from capstone.api import create_app
with TestClient(create_app(Path("edit.sqlite"))) as client:
    response = client.put("/api/sessions/999", json={"day": "2026-10-19", "subject": "Missing", "minutes": 10, "version": 1})
    print("Missing edit:", response.status_code)''',
  [('Why compare version inside the UPDATE statement?', 'To avoid a check-then-write race', 'To make every edit win', 'To replace the primary key', 'The predicate and write need the same atomic operation boundary.'),
   ('Should the UI silently retry a stale edit with the latest version?', 'No, reconcile the conflicting intent', 'Always', 'Only for minute counts', 'Blind retry would overwrite another correction and bypass the protection.')],
  'Read version, wait, then issue an unconditional update.',
  'Apply a conditional update and explain stale conflicts to the user.',
  'Concurrency behavior belongs in the product contract and its regression tests.',
  syntax='UPDATE sessions SET ...,version=version+1 WHERE id=? AND version=?')

L(2, '5. Delete deliberately and preserve newer edits',
  'Require identity and current version for a destructive record operation.',
  [('Delete confirmation', 'The reference interface asks before deleting the chosen record; cancellation does not issue the request.'),
   ('Versioned delete', 'A delete also compares the expected revision so an old page cannot silently remove a newer correction.'),
   ('Recovery policy', 'State whether deletion is reversible. This version has explicit permanent deletion and separately verified snapshots, not an undo feature.')],
  "Deleting a record has a different consequence from changing a display filter. Give the user a clear action and confirmation, and keep that operation tied to the selected resource id. The server must still enforce its own version check because browser confirmation is only an interface behavior.\n\nA stale page must not delete a record after another tab changed it. The same id/version predicate used for editing prevents that silent loss. The API reports a conflict for an existing newer record and not-found for an absent one.\n\nBe honest about recovery. The reference does not implement soft deletion or undo. A previous snapshot can be opened in a separate restore rehearsal, but it is not an automatic per-record undo button. If your user needs undo, design its retention, UI and tests as a separate feature rather than implying the current backup routine provides it.",
  r'''from pathlib import Path
from fastapi.testclient import TestClient
from capstone.api import create_app
with TestClient(create_app(Path("delete.sqlite"))) as client:
    payload = {"day": "2026-10-19", "subject": "Python", "minutes": 25}
    record = client.post("/api/sessions", json=payload).json()
    client.put(f"/api/sessions/{record['id']}", json={**payload, "minutes": 30, "version": 1})
    print("Stale delete:", client.delete(f"/api/sessions/{record['id']}?version=1").status_code)
    print("Current delete:", client.delete(f"/api/sessions/{record['id']}?version=2").status_code)
    print("Count:", client.get("/api/summary").json()["sessions"])''',
  'Verify a missing deletion does not pretend another record was removed.',
  r'''from pathlib import Path
from fastapi.testclient import TestClient
from capstone.api import create_app
with TestClient(create_app(Path("delete.sqlite"))) as client:
    print("Missing delete:", client.delete("/api/sessions/999?version=1").status_code)''',
  'Verify the server requires a version rather than trusting a browser label.',
  r'''from pathlib import Path
from fastapi.testclient import TestClient
from capstone.api import create_app
with TestClient(create_app(Path("delete.sqlite"))) as client:
    print("Missing version:", client.delete("/api/sessions/1").status_code)''',
  [('Why version a delete?', 'A stale page should not remove a newer correction silently', 'To make every delete idempotent', 'To replace backups', 'The destructive operation also needs the stated concurrency protection.'),
   ('Does this reference implement per-record undo?', 'No, its deletion and snapshot policies are explicit', 'Always', 'Only in dark mode', 'Backup/restore and a product undo feature are different behaviors.')],
  'Delete by visible row position with no version or clear recovery policy.',
  'Confirm the selected identity, compare its current version and document recovery limits.',
  'A deliberate delete path protects users from hidden assumptions about what can be undone.',
  syntax='DELETE /api/sessions/{id}?version={expected_version}')

L(2, '6. Demonstrate the complete core user path',
  'Create, read, correct and summarize records through the same interface contract.',
  [('Core acceptance path', 'A coherent end-to-end sequence that demonstrates the essential user outcome.'),
   ('Derived state', 'A report calculated from authoritative records instead of maintained as an unrelated manual counter.'),
   ('Integration evidence', 'Proof that components agree at their boundaries; it complements individual unit tests.')],
  "Now join the core operations into one observable story. Add Python/25 and Japanese/15, verify forty total, correct the Python entry to thirty, and verify forty-five total. Read the corrected row and check its revision. This sequence catches mismatched fields and stale report logic that isolated tests can miss.\n\nKeep the scenario small and deterministic. It is easier to diagnose one failing acceptance path than a large seed dataset with many unrelated operations. Add invalid/conflict cases as focused tests rather than hiding every possibility inside one enormous test.\n\nThis example uses the request adapter in-process. Real HTTP, restart persistence and browser feedback still need their own evidence. A healthy project describes what each check establishes rather than labeling every test 'end-to-end' without naming the boundary.",
  r'''from pathlib import Path
from fastapi.testclient import TestClient
from capstone.api import create_app
with TestClient(create_app(Path("core.sqlite"))) as client:
    first = client.post("/api/sessions", json={"day": "2026-10-19", "subject": "Python", "minutes": 25}).json()
    client.post("/api/sessions", json={"day": "2026-10-19", "subject": "Japanese", "minutes": 15})
    print("Before correction:", client.get("/api/summary").json()["minutes"])
    client.put(f"/api/sessions/{first['id']}", json={"day": first["day"], "subject": first["subject"], "minutes": 30, "version": first["version"]})
    print("After correction:", client.get("/api/summary").json()["minutes"])
    print("Corrected revision:", client.get(f"/api/sessions/{first['id']}").json()["version"])''',
  'Verify a selected date uses only its own records in the summary.',
  r'''from pathlib import Path
from capstone.domain import SessionInput
from capstone.store import Store
store = Store(Path("core.sqlite"))
for day, minutes in [("2026-10-18", 20), ("2026-10-19", 30)]:
    store.add(SessionInput(day=day, subject="Python", minutes=minutes))
print("All:", store.summary()["minutes"])
print("Selected date:", store.summary(day="2026-10-19")["minutes"])''',
  'Check that an empty new app has no inherited synthetic records from another database.',
  r'''from pathlib import Path
from capstone.domain import SessionInput
from capstone.store import Store
Store(Path("one.sqlite")).add(SessionInput(day="2026-10-19", subject="One", minutes=10))
print("First file:", Store(Path("one.sqlite")).summary()["sessions"])
print("Second file:", Store(Path("two.sqlite")).summary()["sessions"])''',
  [('What does this acceptance sequence add beyond isolated functions?', 'Evidence that the components agree on a complete user path', 'Automatic public deployment', 'A guarantee of every possible input', 'Integration can reveal boundary mismatches and stale derived state.'),
   ('Should an in-process request test be labeled a second-device check?', 'No', 'Always', 'Only when it uses JSON', 'Name the actual boundary of the evidence.')],
  'Declare the product complete because its isolated functions each returned something.',
  'Demonstrate the coherent user path, then check remaining process and browser boundaries.',
  'The core build is ready to extend when its essential story can be reproduced and explained.',
  syntax='create two -> total 40 -> correct one -> total 45 -> retrieve revision 2',
  diagram=('Core behavior with revision-aware corrections', ['Validate and create two sessions', 'Read ids and the forty-minute summary', 'Correct one record using its version', 'Commit the update and increment revision', 'Read the forty-five-minute result'], 'A stale parallel edit is rejected; the example checks the in-process request boundary.'))

L(3, '1. Finish predictable error responses',
  'Give callers distinct validation, missing-resource, conflict and service-failure outcomes.',
  [('422 / 404 / 409 / 503', 'Invalid request/domain value, missing record, stale existing record, and temporary database unavailability are different failure meanings.'),
   ('Error adapter', 'Translate expected domain/storage failures into an API response without exposing private SQL/path details.'),
   ('Actionable feedback', 'Tell a user what to correct, reload or retry; do not show a success message for a failed operation.')],
  "Feature completion includes failures. A caller should not need to parse an arbitrary traceback to distinguish an invalid minute count from a stale edit or an unavailable database. Use stable status meanings and readable messages.\n\nThe reference maps model/query errors to 422, missing ids to 404 and version conflicts to 409. SQLite operational failures return a generic 503 message instead of embedding the database path or SQL. Detailed operational diagnosis belongs in appropriately protected server logs; the reference deliberately keeps its public error small.\n\nThe browser keeps entered form values when saving fails and shows an aria-live status message. After a conflict, review current data before resubmitting. Do not catch every exception and return an empty successful list: that would make a broken storage service indistinguishable from a user with no sessions.",
  r'''from pathlib import Path
from fastapi.testclient import TestClient
from capstone.api import create_app
with TestClient(create_app(Path("errors.sqlite"))) as client:
    print("Invalid body:", client.post("/api/sessions", json={"day": "bad", "subject": "Python", "minutes": 10}).status_code)
    print("Missing id:", client.get("/api/sessions/999").status_code)
    print("Invalid page:", client.get("/api/sessions?limit=101").status_code)
    print("Invalid filter:", client.get("/api/summary?day=bad").status_code)''',
  'Simulate a database failure and verify the client does not receive the private detail.',
  r'''import sqlite3
from pathlib import Path
from fastapi.testclient import TestClient
from capstone.api import create_app
app = create_app(Path("errors.sqlite"))
def unavailable(*args):
    raise sqlite3.OperationalError("private database path detail")
app.state.store.summary = unavailable
with TestClient(app) as client:
    response = client.get("/api/summary")
    print("Status:", response.status_code)
    print("Private detail exposed:", "private" in response.text)''',
  'Connect the error status with a sensible user action.',
  r'''actions = {422: "Correct invalid input", 404: "Check whether the record still exists",
           409: "Reload and reconcile the newer version", 503: "Retry later or inspect service health"}
for status, action in actions.items():
    print(status, action)''',
  [('Should a database exception be converted into a fake successful empty list?', 'No', 'Always', 'Only for the first page', 'That hides a service failure as ordinary empty data.'),
   ('Where should private path/SQL details appear?', 'In appropriately protected operational diagnostics, not the public response', 'In every browser message', 'Inside the saved note', 'Public error feedback and operator diagnostics have different audiences.')],
  'Return success for failed writes and expose raw internal errors to every caller.',
  'Return meaningful failures and preserve user input for correction.',
  'Reliable failure behavior is part of completing the feature, not optional polish.',
  syntax='invalid -> 422; missing -> 404; stale -> 409; storage unavailable -> 503')

L(3, '2. Keep reports consistent with the selected scope',
  'Verify count, minutes and per-subject totals for all data and an exact date.',
  [('Aggregation scope', 'The records included in a total; the UI should label whether it means all dates or one selected day.'),
   ('GROUP BY', 'Combine rows by subject and calculate their total minutes in the database.'),
   ('Report invariant', 'A property that should hold across a report, such as per-subject minutes summing to the headline total.')],
  "A polished dashboard is misleading if its numbers disagree about scope. The session list and headline totals use the same exact-date filter. The interface labels that date or says all dates so the reader knows what is being counted.\n\nThe database returns count, total minutes and subject groups from the matching records. A useful invariant is that group minutes sum to the headline minutes. Another is that an empty scope yields zero rather than an exception or a null value the browser cannot format.\n\nThese checks are more valuable than comparing a chart screenshot alone. A graph can be attractive while plotting the wrong filtered dataset. Keep reporting logic small, derive values from source records and test invariants alongside a few concrete examples.",
  r'''from pathlib import Path
from capstone.domain import SessionInput
from capstone.store import Store
store = Store(Path("reports.sqlite"))
for day, subject, minutes in [("2026-10-18", "Python", 20), ("2026-10-19", "Python", 30), ("2026-10-19", "Japanese", 15)]:
    store.add(SessionInput(day=day, subject=subject, minutes=minutes))
for day in [None, "2026-10-19"]:
    report = store.summary(day)
    print(day or "all dates", report["sessions"], report["minutes"])
    print("Group total matches:", sum(row["minutes"] for row in report["subjects"]) == report["minutes"])''',
  'Check a subject total is derived across repeated records.',
  r'''from pathlib import Path
from capstone.domain import SessionInput
from capstone.store import Store
store = Store(Path("reports.sqlite"))
for minutes in [10, 20, 5]:
    store.add(SessionInput(day="2026-10-19", subject="Python", minutes=minutes))
print(store.summary()["subjects"])''',
  'Validate the zero-report invariant for a date with no records.',
  r'''from pathlib import Path
from capstone.store import Store
report = Store(Path("reports.sqlite")).summary(day="2026-10-20")
print("Count:", report["sessions"], "minutes:", report["minutes"])
print("Group total:", sum(row["minutes"] for row in report["subjects"]))''',
  [('What should the interface state about a headline total?', 'Which date/data scope it summarizes', 'Only its font size', 'Only the number of source files', 'Users need to know what records contribute to the number.'),
   ('Which invariant helps catch reporting mistakes?', 'Subject totals sum to the headline minutes for the same scope', 'Every chart must be green', 'Every subject has one record', 'Cross-checks connect the derived report to its intended dataset.')],
  'Filter the displayed rows but leave an unlabeled all-time headline above them.',
  'Apply and label a consistent scope, then verify report invariants.',
  'Meaningful reports combine correct calculations with clear interpretation.',
  syntax='same WHERE scope -> COUNT + SUM + GROUP BY -> labeled report')

L(3, '3. Render user text safely and preserve a usable form',
  'Treat saved notes as text and give the user visible success/error feedback.',
  [('textContent', 'Browser DOM property that inserts a value as text rather than parsing it as HTML.'),
   ('XSS boundary', 'Untrusted saved strings must not become executable markup when displayed.'),
   ('Accessible status', 'A live status region communicates save/error outcomes without requiring a color-only signal.')],
  "Your app stores note text chosen by its owner, but that text still crosses a browser rendering boundary. A note such as <img src=x onerror=...> should remain a note. The reference creates DOM elements and assigns textContent instead of interpolating saved strings into innerHTML.\n\nUsability also matters for correctness. Labels connect to fields, buttons remain keyboard reachable, the save action has a pending state, and errors retain the entered values. The interface provides an explicit cancel-edit action so the user can return to creating a new record.\n\nThe Python example checks the API retains a synthetic markup-looking note and the supplied interface source uses the intended rendering mechanism. That source inspection is not a substitute for an actual browser test. The project browser check later verifies the string is displayed without executing it and exercises add/edit/filter/delete across screen sizes.",
  r'''from pathlib import Path
from fastapi.testclient import TestClient
from capstone.api import create_app
note = '<img src=x onerror="window.unwanted=true">'
with TestClient(create_app(Path("text.sqlite"))) as client:
    record = client.post("/api/sessions", json={"day": "2026-10-19", "subject": "Python", "minutes": 10, "note": note}).json()
    print("Note retained as data:", record["note"] == note)
source = Path("capstone/static/index.html").read_text(encoding="utf-8")
print("Uses textContent:", "element.textContent=value" in source)
print("No innerHTML assignment:", ".innerHTML=" not in source)''',
  'Identify the form/status hooks provided for keyboard users and feedback.',
  r'''from pathlib import Path
source = Path("capstone/static/index.html").read_text(encoding="utf-8")
for marker in ['for="subject"', 'aria-live="polite"', 'id="cancelEdit"', ':focus-visible']:
    print(marker, marker in source)''',
  'Distinguish source inspection from an executed browser result.',
  r'''evidence = {"rendering source inspected": True, "browser executed by this snippet": False}
for name, value in evidence.items():
    print(name + ":", value)''',
  [('Which property treats a note as text?', 'textContent', 'innerHTML', 'An unescaped HTML template', 'The DOM should not parse saved user strings as markup.'),
   ('Does inspecting source alone prove browser interaction works?', 'No', 'Always', 'Only if there is a form', 'Actual browser execution checks a different boundary.')],
  'Build note HTML by concatenating saved strings into innerHTML.',
  'Create elements and assign user strings as text, then test the real browser workflow.',
  'The UI boundary deserves both safe rendering and feedback a learner can understand.',
  syntax='element.textContent = saved_note  // user data remains text')

L(3, '4. Make single-owner access and origin rules explicit',
  'Test access denial while understanding what a shared token does and does not establish.',
  [('Bearer access token', 'A private value sent in an Authorization header; possession grants this one owner access to data routes.'),
   ('Same-origin write check', 'Reject a browser write whose supplied Origin differs from this server origin. This complements access configuration; it is not a multi-user identity system.'),
   ('Runtime secret', 'A value configured outside source code. The interface keeps it only in page memory, not a URL, SQLite record or localStorage.')],
  "Default practice operation binds the server to localhost. If an access token is configured, every data route requires the matching Authorization header. Health and the empty UI shell remain readable without data access. A shared token represents one owner's access; it does not provide separate accounts or per-record permissions.\n\nThe example uses a deliberately synthetic lesson-only token. Your real runtime token belongs in your host's secret configuration and the UI's password field, entered by you. It must not be placed in the lesson, Git, a note, a screenshot or a URL. A remote connection also requires HTTPS so the header is protected in transit.\n\nBrowser origin checks reject cross-origin writes and no broad CORS policy is enabled. A non-browser client can omit Origin, so do not treat that header as authentication. If you expand to multiple people, design identities, authorization and revocation separately. Test unauthorized and cross-origin paths, not just a successful authenticated call.",
  r'''from pathlib import Path
from fastapi.testclient import TestClient
from capstone.api import create_app
with TestClient(create_app(Path("access.sqlite"), token="lesson-only-access-token")) as client:
    print("Unauthenticated data:", client.get("/api/sessions").status_code)
    client.headers["Authorization"] = "Bearer lesson-only-access-token"
    print("Authenticated data:", client.get("/api/sessions").status_code)
    response = client.post("/api/sessions", json={"day": "2026-10-19", "subject": "Python", "minutes": 10}, headers={"Origin": "https://other.invalid"})
    print("Cross-origin write:", response.status_code)''',
  'Verify health can be checked without revealing stored records.',
  r'''from pathlib import Path
from fastapi.testclient import TestClient
from capstone.api import create_app
with TestClient(create_app(Path("access.sqlite"), token="lesson-only-access-token")) as client:
    print(client.get("/health").json())
    print("Private report denied:", client.get("/api/summary").status_code)''',
  'Check that a short configured token fails startup validation.',
  r'''from pathlib import Path
from capstone.api import create_app
try:
    create_app(Path("access.sqlite"), token="short")
except ValueError:
    print("Invalid configuration rejected before serving")''',
  [('Is an Origin header an authentication credential?', 'No', 'Always', 'Only for JSON', 'Non-browser clients can supply or omit it; authentication needs its own mechanism.'),
   ('Does this shared token provide separate user identities?', 'No', 'Always', 'Only if it is long', 'The project deliberately has a single-owner access boundary.')],
  'Store the server token in public HTML or assume Origin proves identity.',
  'Configure secrets outside source and test the actual access boundary.',
  'Security behavior should match the stated owner model and deployment conditions.',
  syntax='Authorization: Bearer <your private runtime token>; never place a real value in source or a URL')

L(3, '5. Back up data and prove restoration',
  'Create a SQLite snapshot and verify useful records in a separate reopened database.',
  [('SQLite backup API', 'Copy a consistent database snapshot through SQLite rather than assuming a live database is safely captured by a plain file copy.'),
   ('Restore rehearsal', 'Open the saved snapshot separately and verify real expected records before relying on it.'),
   ('Failure domain', 'A failure source shared by copies; two files on one lost disk are not an independent recovery plan.')],
  "A backup is useful only if it contains the records you need and can be restored. The helper uses Connection.backup, checks the snapshot and writes to a chosen separate destination. It rejects a same-path operation and an already-existing backup filename in the intended single-operator workflow.\n\nThe example saves one record, takes a snapshot, then deletes the live record. Opening the snapshot through a separate Store still retrieves its original twenty-five minutes. This is a restore rehearsal using synthetic data. It does not replace your live database or inspect any Study Hub backup.\n\nFor real operation, keep protected copies on an appropriate separate failure domain and periodically rehearse recovery. Name the snapshot time and expected data loss since then. A successful copy message alone is not proof that a future operator can recover the service, and a local snapshot helper is not a remote backup system.",
  r'''from pathlib import Path
from capstone.backup import backup_database
from capstone.domain import SessionInput
from capstone.store import Store
live = Store(Path("live.sqlite"))
record = live.add(SessionInput(day="2026-10-19", subject="Python", minutes=25))
print("Snapshot:", backup_database(live.path, Path("snapshot.sqlite")))
live.delete(record["id"], record["version"])
print("Live count:", live.summary()["sessions"])
print("Restored minutes:", Store(Path("snapshot.sqlite")).summary()["minutes"])''',
  'Refuse a backup source/destination collision.',
  r'''from pathlib import Path
from capstone.backup import backup_database
from capstone.store import Store
store = Store(Path("live.sqlite"))
try:
    backup_database(store.path, store.path)
except ValueError:
    print("Same-path backup rejected")''',
  'Protect an existing snapshot from an accidental reuse of its filename.',
  r'''from pathlib import Path
from capstone.backup import backup_database
from capstone.store import Store
store = Store(Path("live.sqlite"))
backup_database(store.path, Path("snapshot.sqlite"))
try:
    backup_database(store.path, Path("snapshot.sqlite"))
except FileExistsError:
    print("Choose a new backup filename")''',
  [('What demonstrates a useful restore?', 'Opening the snapshot and reading expected records', 'Only printing copied', 'Only checking a filename exists', 'Recovery needs verified usable data, not merely an apparent copy.'),
   ('Are two files on one disk independent protection against losing that disk?', 'No', 'Always', 'Only for SQLite', 'Copies can share the same failure domain.')],
  'Call an untested live file copy a complete recovery strategy.',
  'Create a valid snapshot, reopen it separately and rehearse useful record recovery.',
  'Recovery is a behavior you verify, not just a file you hope is usable.',
  syntax='live SQLite -> backup API -> integrity check -> separate snapshot -> reopen and verify',
  diagram=('A backup earns trust through restoration', ['Record known synthetic sessions', 'Create a separate SQLite snapshot', 'Check the snapshot and retain its identity', 'Open it in a separate repository/server', 'Verify the expected records and recovery scope'], 'The rehearsal does not overwrite the live file; real copies also need an appropriate protected failure domain.'))

L(3, '6. Finish with layered behavior tests',
  'Run targeted domain, repository and API tests before adding release confidence.',
  [('Test pyramid in practice', 'Use focused low-level checks plus a smaller number of integrated process/browser checks, each with a clear purpose.'),
   ('Failure injection', 'Deliberately simulate a storage or replacement failure to verify cleanup and preservation behavior.'),
   ('Test isolation', 'Use synthetic data and temporary database paths so runs do not depend on or alter actual user records.')],
  "A completed feature needs more evidence than a successful personal click. The project suite checks strict data, ordering, page bounds, transaction rollback, SQL-like values, stale edits/deletes, access denial, generic errors and snapshots. Each test uses its own temporary path.\n\nFailure injection is particularly useful for paths that are hard to reproduce reliably by chance. The backup test simulates os.replace failure and checks temporary cleanup and preserved source records. The API test simulates a private operational error and checks the public response remains generic.\n\nThe example below runs the actual supplied pytest suite in a child process and fails if the tests fail. A test count is not a quality score by itself: the important question is which promised failures and boundaries it covers. Add real network/browser checks for what in-process tests cannot establish, and stop repeating broad tests once the relevant checks pass unless a new change or failure justifies another run.",
  r'''import os
import subprocess
import sys
result = subprocess.run([sys.executable, "-m", "pytest", "-q"], check=True,
                        env={**os.environ, "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"},
                        capture_output=True, text=True)
print("Actual behavior suite passed:", result.returncode == 0)
print("Test report records passes:", "passed" in result.stdout)''',
  'Select a test boundary for three specific concerns.',
  r'''checks = {"bool minute rejection": "domain test", "rollback": "repository test",
          "stale HTTP edit": "API test", "restart persistence": "fresh process check"}
for concern, boundary in checks.items():
    print(concern + " -> " + boundary)''',
  'Verify the packaged source includes the concrete behavior suite.',
  r'''from pathlib import Path
source = Path("tests/test_capstone.py").read_text(encoding="utf-8")
for name in ["test_crud_restart_and_conflict", "test_parameters_and_transaction_rollback", "test_backup_failed_replace_cleans_temporary"]:
    print(name, name in source)''',
  [('Why use temporary databases?', 'To isolate synthetic checks from real user data and other tests', 'To avoid testing persistence', 'To hide failures', 'Each run should have a deliberate independent state boundary.'),
   ('Does a larger test count automatically prove better coverage?', 'No, inspect the behaviors and boundaries checked', 'Always', 'Only for APIs', 'The evidence must connect to requirements and meaningful failure cases.')],
  'Rely on one happy-path click and a large-looking test count.',
  'Test the promised behaviors and failures at the boundaries where they occur.',
  'A feature is easier to trust when its success and failure contracts are reproducible.',
  syntax='domain + repository + API -> real HTTP/restart -> actual browser workflow')
