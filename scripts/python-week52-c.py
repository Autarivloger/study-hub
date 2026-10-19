L(4, '1. Polish the workflow a user actually performs',
  'Improve clarity, keyboard access, feedback and small-screen reading around the core behavior.',
  [('Interaction state', 'The visible state of the form or action: creating, editing, saving, failed or complete.'),
   ('Progressive feedback', 'Communicate the result of an action without discarding useful input or relying only on color.'),
   ('Responsive layout', 'The same meaningful workflow fits smaller screens rather than merely shrinking every control.')],
  "Polish begins with a real user path. Add a record, correct it, cancel an edit, filter a date, clear the filter and delete a chosen session. Check which state the form is in and whether success/error messages match the actual operation.\n\nThe reference uses labels, visible focus, an aria-live status region, a disabled save state during its request and an explicit cancel-edit action. The layout becomes one column on narrow screens. Both light and dark themes use local styles; the interface loads no external font or UI service.\n\nA pending save guard reduces accidental double-clicks, but it does not establish exactly-once network behavior. A success on the server followed by a failed refresh is also a state that deserves clear feedback. Test what the user observes, not just whether the page has the right CSS class. The Python source checks below identify the intended hooks; the actual browser test exercises them.",
  r'''from pathlib import Path
source = Path("capstone/static/index.html").read_text(encoding="utf-8")
for marker in ['id="cancelEdit"', 'aria-live="polite"', 'if(busy)return', '@media(max-width:760px)', 'prefers-color-scheme:dark']:
    print(marker, marker in source)
print("External script source:", '<script src="https://' in source)''',
  'Verify the server serves the interface as an HTML page.',
  r'''from pathlib import Path
from fastapi.testclient import TestClient
from capstone.api import create_app
with TestClient(create_app(Path("ui.sqlite"))) as client:
    response = client.get("/")
    print("Status:", response.status_code)
    print("HTML response:", response.headers["content-type"].startswith("text/html"))
    print("Title present:", "StudyLog" in response.text)''',
  'Specify a useful browser acceptance scenario instead of asserting only a class name.',
  r'''steps = ["Enter a valid session", "Save once", "Observe the new row and total",
         "Edit minutes", "Observe corrected value", "Cancel a different edit"]
for number, step in enumerate(steps, 1):
    print(number, step)''',
  [('What should UI testing focus on?', 'The observable user workflow and feedback', 'Only the presence of a color class', 'Only a desktop screenshot', 'A real interaction checks state transitions and results.'),
   ('Does disabling the save button guarantee exactly-once POST across network retries?', 'No', 'Always', 'Only in dark mode', 'The UI guard and an API idempotency contract solve different problems.')],
  'Polish a screenshot while ignoring edit state, failed requests and keyboard use.',
  'Exercise the complete workflow at usable sizes and inspect the actual feedback.',
  'Good polish makes the correct behavior easier to perform and understand.',
  syntax='form state -> action -> pending feedback -> actual result -> accessible message')

L(4, '2. Measure the database workload before optimizing',
  'Separate bounded response size from query cost and record a realistic local measurement.',
  [('Query plan', 'SQLite explanation of the access strategy chosen for a query; it can help locate scans or useful indexes.'),
   ('Response bound', 'A page can contain at most ten or one hundred rows while the database still performs more work to produce it.'),
   ('Benchmark scope', 'Here the measurement includes a complete repository call and connection lifetime, while synthetic dataset creation is excluded.')],
  "A fast empty database says little about growth. Create a declared synthetic fixture, run the same useful query repeatedly and retain the observation. Week 51's measurement habits still apply: equal required work, explicit setup and no invented speed claim.\n\nThe example compares an ordered ten-row list with a full summary at two dataset sizes. Each complete method call opens and closes a connection. Data preparation is outside timing. The summary must return the correct total for every row; the list must remain bounded. The chart reports measured median milliseconds on the authoring machine, not a promise for all hardware or users.\n\nThe date/id index supports the ordered/date-filtered list. It does not make every summary constant-time or eliminate SQLite write serialization. If the actual use case becomes large or highly concurrent, profile the relevant operation and consider a new database or pagination strategy based on evidence, not just a desire to add infrastructure.",
  r'''from pathlib import Path
from statistics import median
from timeit import Timer
import matplotlib.pyplot as plt
from capstone.store import Store
sizes, list_times, summary_times = [100, 1000], [], []
for size in sizes:
    store = Store(Path(f"measure-{size}.sqlite"))
    with store.connection() as connection:
        connection.executemany("INSERT INTO sessions(day,subject,minutes,note) VALUES(?,?,?,?)",
                               [("2026-10-19", f"Topic {i%5}", 10, "Synthetic") for i in range(size)])
    assert store.summary()["minutes"] == size * 10
    assert len(store.list_sessions(limit=10)) == 10
    list_times.append(median(Timer(lambda: store.list_sessions(limit=10)).repeat(repeat=5, number=3))/3*1000)
    summary_times.append(median(Timer(store.summary).repeat(repeat=5, number=3))/3*1000)
fig, ax = plt.subplots(figsize=(4.8, 4.6))
ax.plot(sizes, list_times, marker="o", label="List ten rows")
ax.plot(sizes, summary_times, marker="s", label="Summarize all rows")
ax.set(xlabel="Rows in synthetic database", ylabel="Median milliseconds per call")
ax.set_title("Local repository calls\nConnection lifetime included")
ax.legend(fontsize=9)
fig.tight_layout()
fig.savefig("chart.png", dpi=120)
print("Correct totals and page bounds checked for:", sizes)
print("List medians ms:", [round(value, 3) for value in list_times])
print("Summary medians ms:", [round(value, 3) for value in summary_times])''',
  'Inspect the plan for the date-filtered ordered list.',
  r'''from pathlib import Path
from capstone.store import Store
with Store(Path("plan.sqlite")).connection() as connection:
    plan = connection.execute("EXPLAIN QUERY PLAN SELECT * FROM sessions WHERE day=? ORDER BY id DESC LIMIT ?", ("2026-10-19", 10)).fetchall()
print("Date index selected:", any("sessions_day_id" in row[3] for row in plan))''',
  'Demonstrate that a bounded page and full summary describe different amounts of data.',
  r'''from pathlib import Path
from capstone.domain import SessionInput
from capstone.store import Store
store = Store(Path("scope.sqlite"))
for i in range(12):
    store.add(SessionInput(day="2026-10-19", subject="Python", minutes=5))
print("Page rows:", len(store.list_sessions(limit=3)))
print("Summary rows:", store.summary()["sessions"])''',
  [('Does LIMIT 10 prove the database performs only ten operations?', 'No', 'Always', 'Only with a summary', 'The response bound does not specify the full query cost.'),
   ('Should this local chart be promised as universal latency?', 'No, retain workload and environment scope', 'Always', 'Only when the total is correct', 'Timing evidence is specific to its declared experiment.')],
  'Declare the database scalable because a small page returned quickly once.',
  'Measure complete relevant calls, inspect their plan and preserve correctness checks.',
  'Performance decisions should follow observed workload behavior and real constraints.',
  syntax='fixture outside timing -> correct result -> repeated full call -> scoped observation',
  figure=('Measured local list and summary timings', 'Five repeated samples of three complete repository calls per size; medians shown. Dataset creation excluded, connection lifetime included. These are observations, not latency guarantees.'))

L(4, '3. Configure data paths and deployment boundaries deliberately',
  'Keep persistent data, runtime secrets and network exposure separate from application source.',
  [('Environment configuration', 'Runtime values such as CAPSTONE_DB and CAPSTONE_TOKEN are supplied by the operator rather than embedded in source.'),
   ('Persistent data directory', 'A writable location whose lifetime survives replacing application code or a container image.'),
   ('Bind address', '127.0.0.1 confines a service to the local machine; a broader bind/exposure decision requires deliberate access and transport configuration.')],
  "A database path relative to the working directory can surprise an operator who starts the same code from a different folder. The default is convenient for practice, while an operational installation should use an explicit persistent path and a service identity allowed to write there.\n\nKeep secrets out of the repository and browser URLs. CAPSTONE_TOKEN is read from runtime environment configuration. CAPSTONE_PUBLIC=1 refuses to start without a token, but it does not itself provide HTTPS, bind a network interface or implement multi-user authorization. Those remain deliberate deployment responsibilities.\n\nUse localhost for the supplied rehearsal. A second phone cannot reach 127.0.0.1 on your computer by entering that address on the phone; it refers to the phone itself. The manual second-device exercise needs an intentionally configured private or remote route, HTTPS where appropriate and a real access check. GitHub Pages serves the learning website, not this Python process.",
  r'''from pathlib import Path
import os
default = Path("data/studylog.sqlite")
selected = Path(os.environ.get("CAPSTONE_DB", str(default)))
print("Default practice filename:", default.name)
print("Selected path type:", "absolute" if selected.is_absolute() else "relative to working directory")
print("Local rehearsal bind:", "127.0.0.1")''',
  'Separate a source artifact from persistent data in a simple deployment inventory.',
  r'''inventory = {"application code": "replaceable release", "SQLite directory": "persistent state",
             "access token": "private runtime configuration"}
for item, lifetime in inventory.items():
    print(item + " -> " + lifetime)''',
  'Explain which machine a loopback address refers to.',
  r'''for device in ["computer", "phone"]:
    print(f"127.0.0.1 entered on the {device} refers to that {device}")''',
  [('Does CAPSTONE_PUBLIC=1 automatically supply HTTPS?', 'No', 'Always', 'Only for SQLite', 'The flag is a configuration guard, not a complete network/transport deployment.'),
   ('Should application replacement erase the database directory?', 'No', 'Always', 'Only on a phone', 'Code release lifetime and persistent state lifetime must be separated.')],
  'Put a token in source and store live data inside a replaceable image layer.',
  'Use explicit runtime secrets and a persistent writable data path with deliberate exposure.',
  'Deployment configuration is part of preserving the user outcome after your terminal closes.',
  syntax='CAPSTONE_DB: persistent path; CAPSTONE_TOKEN: private runtime value; local bind: 127.0.0.1',
  shell='python -m uvicorn capstone.main:app --host 127.0.0.1 --port 8000')

L(4, '4. Verify a real server restart and restored service',
  'Cross the actual HTTP/process boundary instead of labeling an in-process test a deployment.',
  [('Uvicorn', 'The ASGI server that runs the FastAPI application as a listening HTTP process.'),
   ('smoke.verify', 'The supplied controlled rehearsal starts owned localhost servers with temporary databases, sends real requests, restarts and opens a snapshot in a fresh process.'),
   ('Health versus readiness evidence', 'A health response shows a narrow service check; user acceptance still requires operations such as create, read and restore.')],
  "TestClient is fast and useful, but it does not prove the server process starts, binds a socket or reads the intended database after restart. The supplied smoke verifier creates real Uvicorn processes on owned 127.0.0.1 ports and performs actual HTTP requests.\n\nIt creates and corrects a synthetic session, checks conflict/validation/access behavior, stops the server, starts a new process and retrieves the corrected value. It takes a SQLite snapshot, changes the live database and starts another server on the snapshot to verify recovery. Child processes are stopped before temporary files are cleaned.\n\nThis is executed local deployment evidence. It is not a public URL or a separate-device result. A public/second-device milestone remains a manual exercise after you configure a host, storage, access and transport deliberately. Name these boundaries clearly in your release record so someone can understand exactly what was demonstrated.",
  r'''from pathlib import Path
from smoke import verify
report = verify(Path("http-evidence.json"))
print("Network boundary:", report["network"])
print("Completed checks:", len(report["checks"]))
print("Public deployment proven:", report["public_deployment_verified"])''',
  'Use an actual owned server context for one request path.',
  r'''from pathlib import Path
from smoke import running_server
with running_server(Path("server.sqlite"), "lesson-only-access-token") as client:
    print("Health:", client.get("/health").json()["status"])
    print("Private empty summary:", client.get("/api/summary").json()["sessions"])''',
  'Distinguish three kinds of evidence instead of merging them into a single deployed label.',
  r'''checks = ["In-process request test", "Owned localhost HTTP process", "Manually verified second-device/private deployment"]
for number, boundary in enumerate(checks, 1):
    print(number, boundary)''',
  [('Does a health response alone prove the whole user workflow?', 'No', 'Always', 'Only after a restart', 'Health is a narrow check; acceptance needs meaningful operations too.'),
   ('Does localhost verification prove another phone can reach the service?', 'No', 'Always', 'Only with JSON', 'A second-device path has separate network, access and transport configuration.')],
  'Call a TestClient result a live public deployment.',
  'Run real owned HTTP processes and record the additional external steps separately.',
  'Deployment evidence is useful when its process and network boundary are explicit.',
  syntax='real server -> HTTP operation -> stop -> new process -> persisted result -> restored snapshot')

L(4, '5. Build a consumer artifact with its interface included',
  'Test the installed wheel outside the source checkout, including packaged HTML and HTTP behavior.',
  [('release_check.verify', 'Build the capstone wheel from its source archive, prepare runtime dependency wheels, install into a fresh environment and run the installed service outside the checkout.'),
   ('Wheelhouse', 'A folder of prepared dependency wheels used for a later --no-index installation. Preparing it may require internet.'),
   ('Artifact identity', 'The exact wheel name and SHA-256 identify the bytes tested; a hash alone does not prove trustworthy authorship.')],
  "A source checkout can hide a missing runtime HTML file. The installed server may import successfully but fail when the user opens its home page. The capstone package declares static/index.html as package data and the release check inspects the wheel before starting a consumer server.\n\nThe executable example performs a real artifact rehearsal. It builds an sdist and wheel with prepared backend tools, downloads runtime wheels unless a wheelhouse is supplied, creates a fresh environment and installs using only that wheelhouse. The consumer runs outside the checkout and its import origin must belong to the fresh environment. Actual HTTP checks retrieve the packaged UI, create a session and read a summary.\n\nThe dependency-preparation step can need internet once; the subsequent wheelhouse installation is offline. The installed app itself uses no external service for its core workflow. This is a local artifact/deployment check, not evidence that a container image or public host was run. The Dockerfile is a separate optional recipe and its status must be recorded honestly.",
  r'''from pathlib import Path
from release_check import verify
report = verify(Path("wheel-evidence.json"))
print("Wheel:", report["wheel"])
print("Installed origin:", report["origin"])
print("Consumer checks:", len(report["checks"]))
print("Digest characters:", len(report["sha256"]))
print("Public deployment proven:", report["public_deployment_verified"])''',
  'Read the packaging declaration that includes the browser interface.',
  r'''from pathlib import Path
import tomllib
config = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
print(config["tool"]["setuptools"]["package-data"]["capstone"])
print("Actual asset exists:", Path("capstone/static/index.html").is_file())''',
  'Record an optional container recipe as a recipe, not as an executed deployment.',
  r'''from pathlib import Path
print("Docker recipe supplied:", Path("Dockerfile").is_file())
print("Recipe existence proves container execution:", False)
print("Record actual build/run evidence if you perform that optional exercise")''',
  [('What can a source-tree test miss?', 'A runtime HTML file omitted from the wheel', 'Only spelling mistakes', 'Every function call', 'The consumer runs packaged files, not uninstalled checkout assets.'),
   ('Does --no-index mean dependency preparation never needed a network?', 'No, the wheelhouse may have been prepared online earlier', 'Always', 'Only for Linux', 'State both preparation and installation boundaries.')],
  'Test editable source only and assume the deployed artifact includes every needed file.',
  'Install the exact wheel outside the checkout and exercise its actual UI/API files.',
  'The artifact is ready for a consumer when its installed behavior has been demonstrated.',
  syntax='sdist -> wheel + HTML -> prepared wheelhouse -> fresh install -> outside-checkout HTTP',
  shell='python release_check.py --output artifacts/release.json\n# For prepared offline dependency wheels:\npython release_check.py --wheelhouse YOUR-WHEELHOUSE --output artifacts/release.json')

L(4, '6. Prepare an operational handoff and rollback plan',
  'State how the app starts, survives restart, preserves data and recovers from a bad release.',
  [('Operational handoff', 'Instructions and evidence another operator needs to start, check, back up and maintain the service.'),
   ('Code rollback', 'Return to a previously verified application artifact; it does not automatically undo a database migration.'),
   ('Production gate', 'The access, transport, persistence and operating checks required before making a real service available to intended users.')],
  "A local app that works while your editor is open still needs operating instructions. Record the environment, start command, persistent database path, health check, log destination, backup schedule and recovery rehearsal. Keep credentials private and explain how an operator rotates them.\n\nA rollback plan must consider data. Replacing application code does not reverse a schema change, and deleting the live database is not a rollback strategy. The reference currently rejects unsupported schemas; a future migration needs its own backup, compatibility and restore test.\n\nFor real remote operation, follow DEPLOYMENT.md: a deliberately chosen host/private route, HTTPS, appropriate proxy trust, access checks, persistent storage and front-door limits. Do not imply that a CAPSTONE_PUBLIC flag or a Dockerfile provides those automatically. The second-device exercise is complete only after you perform its user operations from another device and record real results.",
  r'''from pathlib import Path
from capstone.store import Store
store = Store(Path("handoff.sqlite"))
with store.connection() as connection:
    print("Expected schema:", connection.execute("PRAGMA user_version").fetchone()[0])
print("Deployment guide:", Path("DEPLOYMENT.md").is_file())
print("Code rollback alone reverses a data migration:", False)''',
  'Write the minimum operational inventory for this release.',
  r'''handoff = {"start": "Uvicorn on the deliberately configured interface", "state": "persistent CAPSTONE_DB path",
           "health": "GET /health plus a user acceptance operation", "recovery": "verified snapshot and restore rehearsal"}
for item, meaning in handoff.items():
    print(item + ":", meaning)''',
  'Separate completed local evidence from unperformed second-device verification.',
  r'''evidence = {"local HTTP": True, "restart": True, "snapshot restore": True, "second device": False}
print("Still to perform for that milestone:", [name for name, done in evidence.items() if not done])''',
  [('Does rolling back code automatically reverse schema changes?', 'No', 'Always', 'Only with a wheel', 'Persistent state has its own migration and recovery lifecycle.'),
   ('When is the second-device milestone verified?', 'After actual operations from the other device succeed', 'When a README lists an address', 'When TestClient passes', 'A written recipe is not executed external evidence.')],
  'Treat deleting the database or changing an exposure flag as a complete deployment plan.',
  'Preserve state and verify the intended operating, access and recovery boundaries.',
  'A handoff makes continued operation part of the finished product.',
  syntax='release artifact + persistent state + start/health + access/TLS + backup/restore + rollback policy')

L(5, '1. Review the capstone against its acceptance promises',
  'Judge completed behavior using reproducible evidence rather than a feature count.',
  [('Acceptance review', 'Compare the finished product against the concrete user scenarios you wrote before the build.'),
   ('Evidence ledger', 'Record which boundary was checked, the result and any remaining manual or external action.'),
   ('Completion claim', 'State precisely whether you read, reproduced, independently built or operated the project.')],
  "Return to the original story. Can one learner record a session, correct it and retrieve the intended result later? Can they understand a validation failure, recover an older snapshot and use the interface on their screen? These questions matter more than how many source files the project contains.\n\nKeep an evidence ledger. Unit/domain tests cover data rules, repository tests cover database behavior, request tests cover API mapping, real HTTP checks cover the process/network boundary and browser checks cover the interface workflow. The installed-wheel check verifies a separate consumer artifact.\n\nDo not mark a manual remote or second-device exercise done because the local reference passed. Equally, do not dismiss local verified work: it is concrete evidence with a stated scope. Your own completion record should distinguish understanding a lesson, reproducing the reference and implementing a meaningful part independently.",
  r'''from pathlib import Path
from fastapi.testclient import TestClient
from capstone.api import create_app
with TestClient(create_app(Path("acceptance.sqlite"))) as client:
    for subject, minutes in [("Python", 25), ("Japanese", 15)]:
        assert client.post("/api/sessions", json={"day": "2026-10-19", "subject": subject, "minutes": minutes}).status_code == 201
    summary = client.get("/api/summary").json()
    print("Accepted count:", summary["sessions"] == 2)
    print("Accepted minutes:", summary["minutes"] == 40)
print("Boundary: in-process API acceptance")''',
  'Connect a completed check to what it actually establishes.',
  r'''evidence = {"strict invalid-minute test": "domain contract", "new server process reads prior record": "restart persistence",
            "installed home page retrieved": "wheel contains working interface"}
for check, claim in evidence.items():
    print(check + " -> " + claim)''',
  'Keep a manual external milestone pending when it has not been performed.',
  r'''ledger = {"reference reproduced": True, "independent extension": False, "second-device operations": False}
print("Next evidence:", [name for name, done in ledger.items() if not done])''',
  [('What should determine capstone acceptance?', 'Observed behavior against the promised scenarios', 'Only file count', 'Only a final screenshot', 'The original user outcome defines the relevant evidence.'),
   ('Are reading and independent implementation the same learning milestone?', 'No', 'Always', 'Only with tests', 'They demonstrate different levels of understanding and independence.')],
  'Declare universal completion because the final lesson page was opened.',
  'Review the promised behavior and record the scope of actual evidence.',
  'The final review should make your achievements and remaining work easy to assess.',
  syntax='requirement -> relevant check -> observed result -> supported claim -> remaining action')

L(5, '2. Rebuild one slice independently to expose learning gaps',
  'Use a small deliberate change to demonstrate understanding beyond copying.',
  [('Independent reconstruction', 'Implement a bounded piece from its contract without looking at the reference, then compare behavior.'),
   ('Transfer', 'Apply a learned design or testing idea to a new input or change rather than only repeat the original example.'),
   ('Learning gap', 'A specific skill that still needs practice, identified by what you cannot yet explain or reproduce.')],
  "After a complete walkthrough, close the reference and rebuild one small boundary: strict session validation, a parameterized insert, a stale-version update or a filtered summary. Choose one you can finish and test. The purpose is to discover what you understand, not to create a second enormous app.\n\nWrite the expected behavior first. Try valid values and a meaningful failure. If you need the reference, identify the missing concept and revisit that part, then attempt again later with a changed case. An honest small gap gives you a useful practice target.\n\nThe example below transfers the strict-minute idea into an independent plain-Python validator, then checks representative boundaries. It is a learning exercise, not a replacement for the supplied Pydantic model. In your own attempt, explain why bool needs special treatment and what the upper limit means for your chosen product.",
  r'''def validate_minutes(value):
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("whole-number minutes required")
    if not 1 <= value <= 1440:
        raise ValueError("minutes outside 1..1440")
    return value
for value in [1, 1440, 0, True]:
    try:
        print(repr(value), validate_minutes(value))
    except (TypeError, ValueError) as error:
        print(repr(value), type(error).__name__)''',
  'Predict and verify a new invalid input rather than copying only the original happy path.',
  r'''from pydantic import ValidationError
from capstone.domain import SessionInput
try:
    SessionInput(day="2026-10-19", subject="Python", minutes=1441)
except ValidationError:
    print("Upper-bound extension case rejected")''',
  'Turn a learning gap into a concrete next exercise.',
  r'''gap = "I cannot yet explain check-then-write races"
exercise = "Reproduce two stale edits and implement one conditional UPDATE test"
print(gap)
print(exercise)''',
  [('What makes reconstruction useful?', 'A contract-first independent attempt with checked new cases', 'Copying the same code faster', 'Avoiding every failure case', 'It reveals understanding that can transfer beyond the walkthrough.'),
   ('What should happen when you find a gap?', 'Choose a focused exercise and revisit the concept', 'Hide it in the portfolio', 'Add unrelated tools', 'A precise gap is a useful learning target.')],
  'Treat recognition of copied code as proof you can rebuild it independently.',
  'Attempt a bounded slice from the contract and check changed cases.',
  'Independent attempts turn the capstone into evidence of learning rather than only a finished folder.',
  syntax='contract -> independent attempt -> new test case -> explain -> targeted feedback')

L(5, '3. Explain your design tradeoffs with concrete evidence',
  'Defend a design choice while naming the conditions under which you would change it.',
  [('Tradeoff', 'A choice that gains something while accepting a cost or limitation.'),
   ('Decision record', 'The context, alternatives, chosen option, evidence and consequences of a design choice.'),
   ('Change trigger', 'A measured requirement or workload condition that would justify revisiting the decision.')],
  "SQLite removes the need for a separate database server and fits this one-owner app. It also serializes writes and needs deliberate filesystem persistence and backups. A shared token keeps the owner model small but does not support independent user permissions. Offset pagination is easy to learn but can shift under concurrent changes.\n\nThese are not hidden embarrassments; they are engineering choices with boundaries. State what would make you revisit them: sustained write contention, multiple users needing record-level permissions, a measured large-offset problem or a required recovery objective. Avoid choosing a more complex system solely to make the architecture diagram look advanced.\n\nSupport explanations with inspectable evidence. The date/id index is present and can be selected for the list query. The stale edit test demonstrates a protected contract. The backup rehearsal proves a specific recovered dataset. A design explanation is stronger when the reader can reproduce its claims.",
  r'''from pathlib import Path
from capstone.store import Store
store = Store(Path("decision.sqlite"))
with store.connection() as connection:
    names = [row[1] for row in connection.execute("PRAGMA index_list(sessions)")]
    version = connection.execute("PRAGMA user_version").fetchone()[0]
print("Declared index present:", "sessions_day_id" in names)
print("Supported schema:", version)
print("Decision: one-owner SQLite; revisit for measured write contention or multi-user needs")''',
  'Write a decision record with its change trigger.',
  r'''decision = {"choice": "offset pagination", "benefit": "simple small-app interface",
            "limit": "pages can shift during concurrent changes",
            "revisit when": "measured large offsets or stable-cursor requirements"}
for key, value in decision.items():
    print(key + ":", value)''',
  'Connect an access-model limitation to a future design requirement.',
  r'''print("Current: one shared owner token")
print("New requirement: separate users may see only their own records")
print("Needed design: identities, record ownership, authorization and regression tests")''',
  [('What justifies revisiting a design?', 'A changed requirement or measured relevant limit', 'Only a fashionable library name', 'Only a larger diagram', 'Complexity should respond to a concrete need.'),
   ('Should a decision record hide its limitations?', 'No', 'Always', 'Only in a portfolio', 'Tradeoffs are useful when the conditions and costs are explicit.')],
  'Claim the chosen architecture is best for every workload and user model.',
  'Explain its fit, evidence, cost and change triggers.',
  'Good judgment includes knowing when your current decision stops fitting the problem.',
  syntax='context -> alternatives -> choice -> evidence -> consequences -> revisit trigger')

L(5, '4. Write an honest portfolio and release narrative',
  'Describe your demonstrated work without inventing deployment or independence claims.',
  [('Portfolio case study', 'A clear account of the user problem, decisions, behavior, evidence and limitations you can discuss.'),
   ('Release narrative', 'What the current version does, how it was checked and what remains manual or outside scope.'),
   ('Traceable evidence', 'Real code, test results, artifacts and links a reader can inspect rather than unsupported labels.')],
  "Write for someone who has not seen this course. Explain who StudyLog helps, what its first release does and which difficult decision you can defend. Include a concrete failure you reproduced and repaired, such as stale edits or an invalid record that must not be stored.\n\nState your role accurately. If you reproduced the reference, say so; describe an independent extension only after implementing and testing it yourself. A locally verified artifact is useful evidence, while a public service or second-device result requires its own observed record.\n\nDo not claim a universal speedup, production scale or a security model the project does not implement. Keep the case study focused on demonstrated skills: writing contracts, tracing data boundaries, testing failures, packaging assets and planning operations. A thoughtful discussion of a rejected alternative can show more judgment than a long technology list.",
  r'''case_study = {"user": "one learner recording study sessions",
              "behavior": "validated records, corrections, totals and persistence",
              "decision": "SQLite with atomic revision checks",
              "evidence": "behavior tests, real HTTP restart/restore and wheel consumer",
              "limit": "single-owner local reference; external deployment needs separate evidence"}
for key, value in case_study.items():
    print(key + ":", value)''',
  'Describe one actual regression and the evidence that supports its correction.',
  r'''print("Problem: an old edit could overwrite a newer correction")
print("Correction: conditional id/version update")
print("Evidence: version-one retry returns 409 while version-two data remains")''',
  'Label learning and operating milestones separately.',
  r'''milestones = ["Reference understood", "Reference reproduced", "Independent change tested", "Actual deployment operated"]
for stage in milestones:
    print(stage, "requires its own evidence")''',
  [('What should the case study emphasize?', 'Decisions and demonstrated behavior with limits', 'Only a tool list', 'Unperformed public deployment', 'A reader should be able to inspect and discuss the actual work.'),
   ('Is reproducing a reference identical to an independently built feature?', 'No', 'Always', 'Only with a screenshot', 'Accurate role and evidence descriptions make the work credible.')],
  'Describe every tutorial result as independent production experience.',
  'Name your actual contribution, checked behavior and remaining boundaries.',
  'A credible portfolio helps someone understand what you can really explain and do.',
  syntax='problem -> role -> design decision -> observed result -> evidence -> limitation')

L(5, '5. Plan the next six months around specific gaps',
  'Choose deliberate practice targets from the capstone rather than restarting random tutorials.',
  [('Retrospective', 'A review of what happened, what evidence exists, what was difficult and what you would change next.'),
   ('Deliberate practice plan', 'A focused attempt, feedback and a harder follow-up case for a named weak skill.'),
   ('Maintenance learning', 'Continue learning through migrations, failures, restore drills and user-driven changes, not only new feature syntax.')],
  "Finishing the curriculum gives you a foundation, not a guarantee that every future project is easy. Review which parts you can explain without looking and which still depend on copying. Use those observations to choose your next work.\n\nThe supplied retrospective suggests six adaptable areas: independent vertical slices, migrations with compatibility tests, multi-user access design, deliberate private operation/recovery, a real focused contribution and a measured refactor with a case study. These are learning themes, not a promise that each takes exactly one month.\n\nChoose one concrete next exercise and define evidence of improvement. For example, reproduce a stale-update bug, explain its race and implement a conditional-write test independently. After feedback, change the scenario and repeat. This keeps years of study productive because each cycle targets a specific skill rather than accumulating unchecked lesson completions.",
  r'''skills = {"explain revision conflict": 4, "design a migration": 2, "write API tests independently": 3}
target = min(skills, key=skills.get)
print("Illustrative next focus:", target)
print("Evidence: migrate a copied fixture, preserve its records and verify rollback/compatibility")''',
  'Turn an uncertain skill into an observable practice task.',
  r'''gap = "I have never restored a service from a snapshot"
task = "Create synthetic records, snapshot them, start a separate restored instance and verify values"
print(gap)
print(task)''',
  'Check the provided six-month planning document without treating it as completed history.',
  r'''from pathlib import Path
text = Path("RETROSPECTIVE.md").read_text(encoding="utf-8")
print("Next-plan section supplied:", "Next six months" in text)
print("A plan proves those tasks are complete:", False)''',
  [('What should choose the next learning target?', 'A specific observed gap and useful requirement', 'Only a random tool list', 'Only the current calendar month', 'Practice is stronger when it responds to evidence.'),
   ('Does finishing the lesson calendar prove all skills are mastered?', 'No', 'Always', 'Only after Week 52', 'Demonstrated understanding and transfer matter more than calendar position.')],
  'Restart unrelated tutorials whenever a difficult maintenance problem appears.',
  'Name the gap, attempt a focused task, get feedback and repeat a changed case.',
  'The next learning cycle should grow from the evidence you now have.',
  syntax='observed gap -> independent exercise -> feedback -> changed case -> recorded progress')

L(5, '6. Final capstone handoff: demonstrate, explain and maintain',
  'Bring together validated behavior, persistence, interface, artifact checks and a truthful operating record.',
  [('Capstone handoff', 'The usable project plus its specification, tests, operating instructions, evidence and next-step plan.'),
   ('Independent demonstration', 'You can run a scenario, explain its boundaries and make a checked change without relying on an unexplained pasted solution.'),
   ('Continuing maintenance', 'The work after a successful demo: preserve data, handle changes, verify recovery and revisit decisions as requirements grow.')],
  "The year ends with a coherent reference app and a process you can reuse. StudyLog combines a clear user problem, domain validation, a SQLite repository, a JSON API, a responsive browser interface, conflict handling, tests, snapshots and an installable artifact. Its documentation tells another person how to run and evaluate it.\n\nYour final demonstration should include a valid create/read/correct path, an intentional invalid request, a stale-edit conflict, a real restart and a verified snapshot. Explain where data lives, why user text is not executable HTML, which access model exists and what the local deployment evidence does not establish. Use the supplied guides to perform any desired remote/second-device exercise deliberately.\n\nThen make one small independent change and test it. That step turns the reference from something you watched into a tool for demonstrating your own understanding. There is no need to rush the final checkbox. Finish when you can reproduce the behavior, explain the tradeoffs and maintain the data safely. The existing seventh day remains a review/rest opportunity for revisiting the whole course.",
  r'''from pathlib import Path
from capstone.backup import backup_database
from capstone.domain import SessionInput, SessionEdit
from capstone.store import Store, Conflict
store = Store(Path("final.sqlite"))
record = store.add(SessionInput(day="2026-10-19", subject="Capstone practice", minutes=25))
changed = store.update(record["id"], SessionEdit(day=record["day"], subject=record["subject"], minutes=30, version=1))
try:
    store.update(record["id"], SessionEdit(day=record["day"], subject=record["subject"], minutes=99, version=1))
except Conflict:
    print("Stale correction protected")
print("Snapshot:", backup_database(store.path, Path("final-backup.sqlite")))
print("Reopened minutes:", Store(Path("final-backup.sqlite")).summary()["minutes"])
print("Current revision:", changed["version"])''',
  'Check the documents needed for another learner/operator to reproduce the capstone.',
  r'''from pathlib import Path
for name in ["README.md", "SPEC.md", "ARCHITECTURE.md", "DEPLOYMENT.md", "RETROSPECTIVE.md"]:
    print(name, Path(name).is_file())''',
  'Write a final evidence statement that preserves the difference between local and external results.',
  r'''print("Demonstrate: validated session, correction, conflict, persistence and restored data")
print("Explain: boundaries, access model, query cost and recovery policy")
print("Record: actual local, independent and external milestones separately")
print("Continue: one deliberate maintenance or extension task")''',
  [('What is the strongest final evidence?', 'Behavior you can reproduce, explain, change and maintain', 'Only reaching the final page', 'Only a green heading', 'The capstone demonstrates understanding and a usable maintained result.'),
   ('Should the final checkbox replace independent practice?', 'No', 'Always', 'Only after testing', 'Completion controls record study activity; they do not establish every skill automatically.')],
  'Call the course mastered because every lesson page was opened.',
  'Demonstrate the project and its limits, then perform an independently tested change.',
  'The reference is complete when its behavior is checked; your learning continues through the work you can now own.',
  syntax='demonstrate -> explain -> change with tests -> preserve data -> maintain -> learn deliberately',
  diagram=('Your capstone evidence and continuing path', ['A specified user problem and bounded release', 'Validated API, SQLite and usable interface', 'Behavior, HTTP, browser and artifact checks', 'Verified persistence, snapshot and handoff', 'Independent change and next learning plan'], 'Keep actual local and external milestones distinct. Use additional sessions whenever understanding needs more time.'))
