"""Original testing, configuration and observability teaching material."""


def checks(source):
    return (
        'from lesson_support import run_checks\nsource = """\n'
        + clean(source)
        + '"""\nprint(run_checks(source))\n'
    )


def fixture(body, seed=True):
    return (
        "from lesson_support import practice,register,login,PRACTICE_PASSWORD\nwith practice(seed="
        + str(seed)
        + ") as (app,client,headers):\n"
        + textwrap.indent(clean(body), "    ")
    )


lesson(
    0,
    "1. Test a promise with arrange, act and assert",
    "Turn one observable API promise into a repeatable check.",
    [
        (
            "Automated test; arrange/act/assert",
            "Arrange controlled inputs/state, act once through the boundary you want to test, then assert a meaningful expected outcome. A test is evidence for its stated promise, not proof of all correctness.",
        ),
        (
            "pytest; test discovery; run_checks",
            "pytest collects test_*.py files and test_* functions. The supplied run_checks helper writes the authored source into a temporary folder, runs real pytest in a subprocess and returns stable outcome counts. It is an author-controlled teaching helper, not an untrusted-code sandbox.",
        ),
    ],
    "Week 40 gave the API a relational model, migrations and measured queries. Now make its promises repeatable so changes can be reviewed with evidence. "
    "Choose a concrete promise such as GET /health returns 200 and a public status object. Arrange a fresh app/client, send the request and inspect status plus JSON. "
    "Prefer externally meaningful outcomes over assertions that only repeat the implementation. A status-only assertion can miss a wrong body. "
    "The example uses the existing temporary practice helper, so it never opens a learner database or needs a real account. "
    "When reading a test, say which boundary it covers and what it would fail to detect.",
    'def test_health():\n    # arrange controlled app/client\n    response=client.get("/health")\n    assert response.status_code==200\n    assert response.json()=={"status":"ok"}',
    checks(
        'from lesson_support import practice\ndef test_health():\n    with practice(seed=False) as (app,client,headers):\n        response=client.get("/health")\n        assert response.status_code==200\n        assert response.json()=={"status":"ok"}'
    ),
    "Real pytest executes the function and reports one passing test. No Uvicorn server or network port is needed for this in-process contract check.",
    (
        "assert response.json()  # any truthy body passes",
        'assert response.status_code==200\nassert response.json()=={"status":"ok"}',
        "A truthy error or incorrect object is not the promised success representation.",
    ),
    "Test that an anonymous current-user request requires authentication.",
    checks(
        'from lesson_support import practice\ndef test_identity_requires_login():\n    with practice(seed=False) as (app,client,h):\n        r=client.get("/v1/me")\n        assert r.status_code==401\n        assert r.headers["WWW-Authenticate"]=="Bearer"'
    ),
    "Assert that generated OpenAPI is available and describes note creation.",
    checks(
        'from lesson_support import practice\ndef test_schema():\n    with practice(seed=False) as (app,client,h):\n        r=client.get("/openapi.json")\n        assert r.status_code==200\n        assert "post" in r.json()["paths"]["/v1/notes"]'
    ),
    "A useful test states a concrete promise, controls its inputs and checks the observable result.",
    [
        (
            "What does assert response.json() prove?",
            "Only that decoded data is truthy",
            "That the entire contract is correct",
            "That authorisation works",
            "Check the expected status and relevant body explicitly.",
        ),
        (
            "Does TestClient require a running Uvicorn port?",
            "No",
            "Always",
            "Only with pytest",
            "It invokes the ASGI application in-process.",
        ),
    ],
)

lesson(
    0,
    "2. Read a failure and make the test fail for the right reason",
    "Understand passing/failing counts and use a deliberately wrong expectation as a learning tool.",
    [
        (
            "Assertion failure; exit code",
            "A failed assertion reports a mismatch. pytest normally exits 0 when tests pass and 1 when tests fail; collection/configuration errors are different failures.",
        ),
        (
            "Red/green; regression test",
            "A focused failing example demonstrates the bug or missing behaviour, then a correction makes it pass. A regression test should fail when the relevant defect returns.",
        ),
    ],
    "A green test that never reaches its assertion is not helpful. First verify collection and the boundary being exercised. "
    "The deliberately failing example below is safe: it compares two small integers, and the helper reports the expected failure without changing the app. "
    "Do not weaken a valid expectation merely to make a failing implementation look green. Determine whether the expectation or the implementation is wrong. "
    "A collection error is not the same as a failed application assertion. Missing imports and invalid test names need a different repair. "
    "The helper reports intentional assertion failures but refuses to hide collection/environment errors as ordinary results.",
    "def test_expected_total():\n    assert actual_total==expected_total",
    checks(
        "def test_true_case():\n    assert 2+3==5\ndef test_deliberate_mismatch():\n    assert 2+3==6"
    ),
    "One test passes and one deliberately fails, producing exit code 1. The mismatch teaches feedback interpretation rather than demonstrating a real API bug.",
    (
        "# Delete the assertion whenever a test fails",
        "Check the promise, reproduce the defect and repair the correct side",
        "Removing the check hides evidence instead of fixing behaviour.",
    ),
    "Correct the deliberately wrong arithmetic expectation.",
    checks("def test_expected_total():\n    assert 2+3==5"),
    'Write a test that distinguishes False from the string "false".',
    checks(
        'def test_boolean_representation():\n    result={"completed":False}\n    assert result["completed"] is False\n    assert result["completed"]!="false"'
    ),
    "A failing test is useful when it reaches a meaningful assertion and identifies the intended behavioural mismatch.",
    [
        (
            "Should a valid assertion be deleted just to get green?",
            "No",
            "Always",
            "Only if it checks JSON",
            "Investigate the actual contract and defect.",
        ),
        (
            "Is a collection error an ordinary failed application assertion?",
            "No",
            "Always",
            "Only on Windows",
            "The tests may not have executed at all.",
        ),
    ],
)

lesson(
    0,
    "3. Isolate the real database with a fresh app fixture",
    "Give each test its own files and lifecycle instead of touching real progress.",
    [
        (
            "tmp_path; pytest fixture",
            "tmp_path is a pytest-provided temporary directory unique to a test. A fixture declared with @pytest.fixture supplies setup/resources to a test by parameter name.",
        ),
        (
            "Function scope; lifespan cleanup",
            "Function-scoped fixtures normally create fresh state per test. A yielded TestClient fixture enters lifespan and closes the app before pytest cleans its owned temporary files.",
        ),
    ],
    "Never point an acceptance test at the real instance directory just because the app already runs there. "
    "Construct an independent app with tmp_path and its own log stream. Enter TestClient as a context manager so migrations/startup actually run. "
    "A test that assumes previous tests registered its account depends on execution order. Function isolation makes that mistake visible. "
    "The supplied project uses fixtures for app, client, logs, headers and note; each resource has a clear owner. "
    "Temporary does not mean fake: these tests still execute real SQLite migrations, hashing and request logic on disposable state.",
    '@pytest.fixture\ndef client(tmp_path):\n    app=create_app(tmp_path/"instance")\n    with TestClient(app) as client:\n        yield client',
    checks(
        'from io import StringIO\nimport pytest\nfrom fastapi.testclient import TestClient\nfrom orm_api import create_app\n@pytest.fixture\ndef client(tmp_path):\n    with TestClient(create_app(tmp_path/"instance",log_stream=StringIO())) as c:\n        yield c\ndef test_fresh_app(client):\n    assert client.get("/health/ready").status_code==200'
    ),
    "pytest supplies an owned path, the fixture starts the real app and readiness succeeds against its temporary database.",
    (
        'app=create_app("my-real-instance")  # reusable test data',
        "Use tmp_path or the supplied practice helper",
        "A test must not reset, modify or inspect an existing learner instance.",
    ),
    "Show that two pytest tests receive separate empty directories.",
    checks(
        'import pytest\ndef test_first(tmp_path):\n    (tmp_path/"marker.txt").write_text("owned",encoding="utf-8")\ndef test_second(tmp_path):\n    assert not (tmp_path/"marker.txt").exists()'
    ),
    "Create and read a file only inside tmp_path.",
    checks(
        'def test_owned_file(tmp_path):\n    p=tmp_path/"sample.txt"\n    p.write_text("fictional",encoding="utf-8")\n    assert p.read_text(encoding="utf-8")=="fictional"'
    ),
    "Use real components with explicitly disposable state and verify their startup/cleanup lifetime.",
    [
        (
            "Does a temporary SQLite database mean SQL is mocked?",
            "No",
            "Always",
            "Only after login",
            "The database is real; its files are disposable.",
        ),
        (
            "What should test data depend on?",
            "Its own setup",
            "A previous test running first",
            "The learner’s current account",
            "Independent setup removes execution-order assumptions.",
        ),
    ],
)

lesson(
    0,
    "4. Parametrise input boundaries",
    "Cover accepted, boundary and rejected cases with one clear test shape.",
    [
        (
            "pytest.mark.parametrize",
            "Parametrisation runs one test body for several declared input/expected pairs. It should express meaningful categories, not generate many redundant checks.",
        ),
        (
            "Boundary matrix; error location",
            "An input matrix includes ordinary valid values, exact limits and first invalid values. A validation error location identifies the field/transport boundary involved.",
        ),
    ],
    "A page size rule of 1–50 needs more than a single test using 10. Check 1, 50, 0, 51 and a malformed value deliberately. "
    "Keep one primary failure per row when learning why a particular status occurs. An invalid token plus invalid body can obscure which boundary rejected the request. "
    "The fixture provides a valid fictional login while varying the query parameter only. "
    "Parametrisation improves readability and diagnosis; it is not a reason to duplicate dozens of equivalent cases. "
    "After a rejected write, still compare state when the no-side-effect promise matters.",
    '@pytest.mark.parametrize("value,expected",[(1,200),(50,200),(0,422),(51,422)])',
    checks(
        'import pytest\nfrom lesson_support import practice\n@pytest.mark.parametrize("value,expected",[(1,200),(50,200),(0,422),(51,422),("wrong",422)])\ndef test_limits(value,expected):\n    with practice() as (app,c,h):\n        assert c.get("/v1/notes",headers=h,params={"limit":value}).status_code==expected'
    ),
    "pytest counts each case independently. A failure can identify the specific value whose contract changed.",
    (
        "# Randomly repeat a typical valid limit 100 times",
        "Choose contract categories and boundary neighbours",
        "Representative boundaries supply more evidence than redundant ordinary successes.",
    ),
    "Parametrise the project’s configuration TTL limits without creating a server.",
    checks(
        'import pytest\nfrom orm_api.settings import Settings\n@pytest.mark.parametrize("value",[60,900,3600])\ndef test_allowed_ttl(value):\n    assert Settings(token_ttl=value).token_ttl==value'
    ),
    "Reject values just outside that configuration range.",
    checks(
        'import pytest\nfrom orm_api.settings import Settings\n@pytest.mark.parametrize("value",[59,3601])\ndef test_rejected_ttl(value):\n    with pytest.raises(ValueError):Settings(token_ttl=value)'
    ),
    "Use compact parameter tables to test distinct contract boundaries with useful failure names.",
    [
        (
            "Which set best tests 1–50 inclusive?",
            "1, 50, 0 and 51",
            "Only 10 repeated",
            "Only 9999",
            "It covers boundaries and their first invalid neighbours.",
        ),
        (
            "Why keep unrelated inputs valid in a boundary test?",
            "To isolate the failure being examined",
            "To remove authentication forever",
            "To avoid all assertions",
            "It makes the reason for rejection clearer.",
        ),
    ],
)

lesson(
    0,
    "5. Test both ownership refusal and unchanged data",
    "Verify private data stays private across every member operation.",
    [
        (
            "Negative test; state preservation",
            "A negative test deliberately requests a forbidden or invalid action. Comparing the original resource afterward establishes that refusal did not follow an unintended write.",
        ),
        (
            "Two-account fixture",
            "Two independent fictional users can prove owner isolation. A fake identity provider cannot by itself verify real password/token behaviour.",
        ),
    ],
    "A correct create/read happy path does not prove another account cannot edit the same id. "
    "Use a valid Asha token and a valid Ben token, then try cross-owner read, replace, patch, delete and tag access. "
    "The API intentionally returns 404 for both absent and other-owner notes. Check the owner’s original representation afterward. "
    "Also verify Ben’s collection total excludes Asha’s notes; list endpoints can leak counts even when individual reads are protected. "
    "All accounts here are fictional local fixtures, never real learner credentials.",
    "# authorised owner succeeds; other owner fails; original state stays unchanged",
    fixture(
        'ben=login(client,"ben")\nbefore=client.get("/v1/notes/1",headers=headers).json()\nr=client.patch("/v1/notes/1",headers=ben,json={"title":"Not mine"})\nassert r.status_code==404\nassert client.get("/v1/notes/1",headers=headers).json()==before\nprint("Refusal preserved owner data")'
    ),
    "A real Ben login is authenticated but not authorised for Asha’s note. The comparison proves the rejected patch did not change it.",
    (
        "assert denied.status_code==404  # assume no side effects",
        "Also compare the owner’s original resource afterward",
        "An incorrect implementation could mutate data and then return an error.",
    ),
    "Prove cross-owner delete leaves the owner’s row readable.",
    fixture(
        'ben=login(client,"ben")\nassert client.delete("/v1/notes/1",headers=ben).status_code==404\nassert client.get("/v1/notes/1",headers=headers).status_code==200\nprint("Other-owner delete blocked")'
    ),
    "Check collection totals for both valid identities.",
    fixture(
        'ben=login(client,"ben")\nprint(client.get("/v1/notes",headers=headers).json()["total"],client.get("/v1/notes",headers=ben).json()["total"])'
    ),
    "Test identity, per-resource authorisation and failure-side-effect preservation as separate promises.",
    [
        (
            "Does a valid token authorise every record?",
            "No",
            "Always",
            "Only for tags",
            "Each operation must enforce resource ownership.",
        ),
        (
            "What adds evidence beyond an error status?",
            "The original data remains unchanged",
            "The button is green",
            "The URL is short",
            "Stored-state comparison checks the side-effect boundary.",
        ),
    ],
)

lesson(
    0,
    "6. Maintain an endpoint contract inventory",
    "Check every API operation without mistaking an inventory for full coverage.",
    [
        (
            "Endpoint inventory; operation coverage",
            "An inventory lists method/path contracts. Testing every operation once is a useful baseline, but does not prove every input, failure, owner or concurrency case.",
        ),
        (
            "OpenAPI comparison",
            "Generated schema describes declared operations. Compare your test plan with it to notice missing routes, then execute meaningful requests separately.",
        ),
    ],
    "The Week 41 API has sixteen schema operations, including private CRUD/tags, account auth, liveness, readiness and protected metric counts. "
    "Keep a plan that names a successful and relevant failing case for each operation. Reuse fixtures rather than hiding all checks in one giant test. "
    "The supplied pytest suite exercises every operation and adds validation, ownership, secret-redaction and error cases. "
    "Static assets and the original explorer are checked too, even though they are not all part of the generated API schema. "
    "An endpoint count is a completeness aid, not a security certificate or a substitute for assertion quality.",
    'operations={(method.upper(),path) for path,methods in schema["paths"].items() for method in methods}',
    fixture(
        'schema=client.get("/openapi.json").json()\noperations={(m.upper(),p) for p,methods in schema["paths"].items() for m in methods}\nprint("Operations:",len(operations))\nprint(("GET","/health/ready") in operations,("GET","/internal/metrics") in operations)',
        False,
    ),
    "The inventory includes both new operational endpoints. Their actual success/failure behaviour requires request tests in later parts.",
    (
        "# Sixteen route names means every defect is covered",
        "Map routes to meaningful happy/failure/state assertions",
        "A list proves presence, not behaviour.",
    ),
    "Check public static documentation and protected metrics as different contracts.",
    fixture(
        'print(client.get("/docs").status_code,client.get("/internal/metrics").status_code,client.get("/internal/metrics",headers=headers).status_code)'
    ),
    "Verify the new source still advertises the original note-create success status.",
    fixture(
        'responses=client.get("/openapi.json").json()["paths"]["/v1/notes"]["post"]["responses"]\nprint("201" in responses)',
        False,
    ),
    "Use a complete operation inventory to find missing tests, then check the behaviours and boundaries behind each entry.",
    [
        (
            "Does testing each endpoint once cover every failure case?",
            "No",
            "Always",
            "Only with coverage installed",
            "Input, ownership and lifecycle cases still need deliberate checks.",
        ),
        (
            "What is OpenAPI useful for here?",
            "Finding operations missing from the test plan",
            "Proving every runtime permission",
            "Storing passwords",
            "It describes the declared interface, not all enforcement.",
        ),
    ],
)

lesson(
    1,
    "1. Compose fixtures with explicit scopes",
    "Reuse setup while retaining independent per-test state.",
    [
        (
            "Fixture dependency graph; scope",
            "Fixtures can request other fixtures. Function scope creates a fresh resource for each test; broader scopes share state and therefore require more care.",
        ),
        (
            "conftest.py",
            "pytest discovers shared fixtures in conftest.py for that directory tree. Tests request fixture names instead of manually calling decorated fixture functions.",
        ),
    ],
    "The project’s headers fixture depends on client, which depends on app and its temporary path/log stream. This makes setup dependencies visible. "
    "Keep mutable app/database fixtures function-scoped unless you have a concrete reason and safe reset policy for sharing. "
    "Do not make a session-scoped mutable list merely to make tests faster; one test’s append may become another test’s unexpected input. "
    "A fixture can return a value or yield a resource with cleanup. Its name is an explicit part of the test signature. "
    "Understand the dependency graph before adding autouse fixtures that silently affect every test.",
    "@pytest.fixture\ndef headers(client):\n    # register/login fictional account\n    return bearer_headers",
    checks(
        'import pytest\n@pytest.fixture\ndef original():return ["HTTP"]\n@pytest.fixture\ndef labelled(original):return original+["Test"]\ndef test_composed(labelled):assert labelled==["HTTP","Test"]\ndef test_independent(original):assert original==["HTTP"]'
    ),
    "Two tests share setup definitions without sharing a previously mutated list instance.",
    (
        "# Call a decorated fixture directly instead of requesting it",
        "def test_contract(client): ...",
        "pytest resolves named fixture dependencies and lifetime.",
    ),
    "Prove a function-scoped mutable fixture starts fresh for two tests.",
    checks(
        "import pytest\n@pytest.fixture\ndef items():return []\ndef test_first(items):items.append(1);assert items==[1]\ndef test_second(items):assert items==[]"
    ),
    "Request two independent fixtures in one test.",
    checks(
        'import pytest\n@pytest.fixture\ndef expected_status():return 200\n@pytest.fixture\ndef body():return {"ready":True}\ndef test_contract(expected_status,body):assert expected_status==200 and body["ready"] is True'
    ),
    "Reuse fixture definitions while deliberately controlling state sharing and setup dependencies.",
    [
        (
            "What does function scope normally provide?",
            "Fresh setup for each test",
            "One global mutable object forever",
            "Automatic real-account access",
            "It reduces cross-test state dependence.",
        ),
        (
            "How should tests obtain a fixture?",
            "Request its name as a parameter",
            "Read the learner’s browser",
            "Call its decorator directly",
            "pytest resolves the dependency/lifetime graph.",
        ),
    ],
)

lesson(
    1,
    "2. Yield fixtures guarantee cleanup boundaries",
    "Release owned resources even when an assertion fails.",
    [
        (
            "Yield fixture; teardown",
            "Code before yield sets up a resource; code after yield tears it down when the test finishes. Use try/finally for explicit cleanup that must occur despite failures.",
        ),
        (
            "Cleanup versus reset",
            "Cleanup releases resources owned by the test. It does not justify deleting an arbitrary real data folder or resetting another installation.",
        ),
    ],
    "A test failure should not leave a running server, held connection or global override that contaminates later work. "
    "The client fixture enters lifespan and closes the app before its temporary directory is removed. "
    "For custom resources, put cleanup in finally and test that boundary with a controlled failure. "
    "Keep cleanup paths tied to an explicitly created temporary resource; never build a broad recursive delete as a shortcut. "
    "The small example below records lifecycle order without opening any external service.",
    "@pytest.fixture\ndef resource():\n    owned=acquire()\n    try:yield owned\n    finally:release(owned)",
    checks(
        'import pytest\nfrom contextlib import contextmanager\ndef test_cleanup_after_error():\n    events=[]\n    @contextmanager\n    def resource():\n        events.append("open")\n        try:yield "owned"\n        finally:events.append("close")\n    with pytest.raises(ValueError):\n        with resource():raise ValueError("controlled")\n    assert events==["open","close"]'
    ),
    "A deliberate error still triggers finally cleanup. pytest.raises makes that failure part of the expected contract.",
    (
        "# Only clean up after a passing assertion",
        "Place owned cleanup in a guaranteed finally/yield boundary",
        "A test failure must not skip resource release.",
    ),
    "Write a yielded fixture and assert the resource is available during its test.",
    checks(
        'import pytest\n@pytest.fixture\ndef resource():\n    value={"open":True}\n    try:yield value\n    finally:value["open"]=False\ndef test_open(resource):assert resource["open"] is True'
    ),
    "Use monkeypatch.context to restore a local attribute after a scoped change.",
    checks(
        'from types import SimpleNamespace\ndef test_restore(monkeypatch):\n    obj=SimpleNamespace(label="original")\n    with monkeypatch.context() as patch:\n        patch.setattr(obj,"label","temporary")\n        assert obj.label=="temporary"\n    assert obj.label=="original"'
    ),
    "A repeatable test owns both setup and teardown, including the failure path.",
    [
        (
            "When must cleanup run?",
            "On both success and failure",
            "Only after a green test",
            "Only before deployment",
            "Resource ownership includes failed test paths.",
        ),
        (
            "Does a fixture justify deleting real learner data?",
            "No",
            "Always",
            "If called cleanup",
            "Only explicitly owned disposable resources may be removed.",
        ),
    ],
)

lesson(
    1,
    "3. Patch the name where the application looks it up",
    "Replace a narrow dependency without accidentally testing the wrong object.",
    [
        (
            "monkeypatch.setattr; lookup namespace",
            "Patch the name used by the code under test. If a module imported a function directly, replacing the original defining module’s name may not replace that already imported reference.",
        ),
        (
            "Test double; fake scope",
            "A fake provides controlled behaviour at one boundary. Name what it bypasses, and restore it after the test.",
        ),
    ],
    "The API imports database_ready into orm_api. Its readiness handler looks up orm_api.database_ready, so that is the name a focused readiness-failure test replaces. "
    "Patch only the boundary needed for the case. Replacing the whole app would prove little about the route’s response. "
    "pytest’s monkeypatch fixture restores changes after the test; explicit contexts can narrow that lifetime further. "
    "A mocked readiness helper does not prove the real database check works; another test must exercise the real temporary database. "
    "This separation keeps a failure test deterministic without claiming more than it covers.",
    'monkeypatch.setattr("orm_api.database_ready",lambda sessions:False)',
    checks(
        'from lesson_support import practice\ndef test_unavailable_readiness(monkeypatch):\n    with practice(seed=False) as (app,c,h):\n        monkeypatch.setattr("orm_api.database_ready",lambda sessions:False)\n        assert c.get("/health/ready").status_code==503\n        assert c.get("/health").status_code==200'
    ),
    "The readiness response becomes 503 while liveness stays 200. The test controls only the dependency result, not the route itself.",
    (
        "# Patch an unrelated original name and assume a direct import changed",
        "Patch the actual lookup name in the consuming module",
        "Imported references can keep pointing at the old object.",
    ),
    "Restore the real readiness provider after a narrow patch context.",
    checks(
        'from lesson_support import practice\ndef test_restore_readiness(monkeypatch):\n    with practice(seed=False) as (app,c,h):\n        with monkeypatch.context() as patch:\n            patch.setattr("orm_api.database_ready",lambda sessions:False)\n            assert c.get("/health/ready").status_code==503\n        assert c.get("/health/ready").status_code==200'
    ),
    "Verify a simple function dependency is called once with the expected input.",
    checks(
        'from unittest.mock import Mock\ndef test_collaborator():\n    check=Mock(return_value=True)\n    assert check("fictional") is True\n    check.assert_called_once_with("fictional")'
    ),
    "Patch a precise lookup boundary and state which real behaviour that fake does not verify.",
    [
        (
            "Where is readiness patched in this project?",
            "orm_api.database_ready",
            "An unrelated browser variable",
            "The password field",
            "The handler uses the imported name in the consuming module.",
        ),
        (
            "Can this mock prove the actual database is available?",
            "No",
            "Always",
            "Only if status is 503",
            "A separate real-database test supplies that evidence.",
        ),
    ],
)

lesson(
    1,
    "4. Mock HTTP at the transport boundary",
    "Exercise real request construction and response handling without contacting a service.",
    [
        (
            "httpx.MockTransport; request handler",
            "MockTransport calls a supplied Python handler instead of a network connection. It can inspect the real constructed request and return a controlled HTTPX response.",
        ),
        (
            "Reserved .test host; explicit client injection",
            "The optional read_notice helper requires a caller-supplied client and uses status.example.test, a fictional testing address. Lesson tests always supply MockTransport rather than trying live internet.",
        ),
    ],
    "Mocking read_notice itself would skip the code that builds its request, checks status and validates the response. "
    "A transport fake keeps that application code active while replacing only the network boundary. "
    "Inspect the method/host and return the documented message shape. Do not send a real account credential to a demo service. "
    "The project’s autouse fixture rejects unexpected use of real HTTPX sync/async transports; in-process TestClient and MockTransport remain usable. "
    "This blocker is specific to HTTPX paths used by these tests, not a universal operating-system network sandbox.",
    "with httpx.Client(transport=httpx.MockTransport(fake)) as client:\n    message=read_notice(client)",
    'import httpx\nfrom orm_api.upstream import read_notice\ncalls=[]\ndef fake(request):\n    calls.append((request.method,request.url.host))\n    return httpx.Response(200,json={"message":"Maintenance planned"})\nwith httpx.Client(transport=httpx.MockTransport(fake)) as client:\n    print(read_notice(client))\nprint(calls)',
    "The helper constructs a real HTTP request, but the fake handles it in memory. No DNS lookup, server account or internet response is involved.",
    (
        "# Mock the entire function and claim its request parsing passed",
        "Inject a mocked transport under the real function",
        "Test the application logic rather than bypassing it wholesale.",
    ),
    "Assert the request path and return a different valid message.",
    'import httpx\nfrom orm_api.upstream import read_notice\ndef fake(request):\n    assert request.url.path=="/notice"\n    return httpx.Response(200,json={"message":"All clear"})\nwith httpx.Client(transport=httpx.MockTransport(fake)) as client:print(read_notice(client))',
    "Use MockTransport in a real pytest test.",
    checks(
        'import httpx\nfrom orm_api.upstream import read_notice\ndef test_notice():\n    transport=httpx.MockTransport(lambda request:httpx.Response(200,json={"message":"Ready"}))\n    with httpx.Client(transport=transport) as client:assert read_notice(client)=="Ready"'
    ),
    "Replace the network boundary while keeping request construction, status checks and schema handling real.",
    [
        (
            "Does MockTransport need a real remote server?",
            "No",
            "Always",
            "Only for GET",
            "Its Python handler replaces network transport.",
        ),
        (
            "Is the supplied HTTPX blocker a universal network sandbox?",
            "No",
            "Always",
            "Only on Linux",
            "It blocks the specific HTTPX transport methods, not every possible networking library.",
        ),
    ],
)

lesson(
    1,
    "5. Cover timeout, bad status and invalid payloads",
    "Make upstream failures deterministic and keep private exception details out of the public error.",
    [
        (
            "side effect; ReadTimeout; HTTPStatusError",
            "A fake can raise an expected timeout or return an error status. raise_for_status rejects unsuccessful HTTP status; schema validation separately rejects an incorrect success payload.",
        ),
        (
            "UpstreamUnavailable",
            "The project helper translates expected HTTP/payload failures into a generic Notice unavailable exception. It does not expose an upstream response, secret URL or raw error message.",
        ),
    ],
    "A happy 200 mock cannot prove the timeout or malformed-response branch. Choose a distinct case for each contract. "
    "A 200 with the wrong JSON shape can be unusable even though transport succeeded. "
    "The helper sets a bounded request timeout but does not retry indefinitely. A timeout should lead to a documented failure or fallback decision. "
    "Do not use real outages or sleeps to make these tests fail predictably. "
    "The examples use only fictional messages and deliberately suppress private exception text in the translated result.",
    'raise httpx.ReadTimeout("fictional detail",request=request)\n# Assert the documented generic application failure.',
    checks(
        'import httpx,pytest\nfrom orm_api.upstream import read_notice,UpstreamUnavailable\n@pytest.mark.parametrize("mode",["timeout","status","shape"])\ndef test_failures(mode):\n    def fake(request):\n        if mode=="timeout":raise httpx.ReadTimeout("fictional detail",request=request)\n        return httpx.Response(503 if mode=="status" else 200,json={"wrong":True})\n    with httpx.Client(transport=httpx.MockTransport(fake)) as client:\n        with pytest.raises(UpstreamUnavailable,match="^Notice unavailable$"):read_notice(client)'
    ),
    "Three tests cover three different boundaries: transport time, status and data contract. Each produces the same documented generic application failure.",
    (
        "# Sleep until a real service happens to fail",
        "Raise/return a controlled failure at the transport boundary",
        "Deterministic tests should not depend on random internet outages.",
    ),
    "Reject a malformed JSON success body.",
    checks(
        'import httpx,pytest\nfrom orm_api.upstream import read_notice,UpstreamUnavailable\ndef test_invalid_json():\n    with httpx.Client(transport=httpx.MockTransport(lambda r:httpx.Response(200,text="not json"))) as client:\n        with pytest.raises(UpstreamUnavailable):read_notice(client)'
    ),
    "Confirm an empty message violates the helper’s response contract.",
    checks(
        'import httpx,pytest\nfrom orm_api.upstream import read_notice,UpstreamUnavailable\ndef test_empty_message():\n    with httpx.Client(transport=httpx.MockTransport(lambda r:httpx.Response(200,json={"message":""}))) as client:\n        with pytest.raises(UpstreamUnavailable):read_notice(client)'
    ),
    "Test transport, status and payload failures separately with deterministic fakes and a deliberate error contract.",
    [
        (
            "Can a 200 response still violate the application payload contract?",
            "Yes",
            "Never",
            "Only with a database",
            "The JSON shape/content still needs validation.",
        ),
        (
            "What should tests use for a predictable timeout?",
            "A controlled raised timeout",
            "A real outage",
            "An unbounded sleep",
            "A fake isolates the relevant failure branch.",
        ),
    ],
)

lesson(
    1,
    "6. Control time and environment without hidden state",
    "Make small policy tests independent of the current clock and real machine configuration.",
    [
        (
            "Dependency-injected clock; deterministic input",
            "Passing an explicit current-time value makes a policy calculation repeatable. It avoids patching a global time module that unrelated libraries may also use.",
        ),
        (
            "monkeypatch.setenv/delenv",
            "These helpers temporarily set/remove named environment values and restore them afterward. They do not justify dumping every real environment variable into a log.",
        ),
    ],
    "Tests that depend on today’s exact second or the developer’s actual APP_ENV can pass on one machine and fail elsewhere. "
    "For a pure expiry rule, supply now and expires_at explicitly. The API’s real JWT tests still use its verified token library and controlled issued/expired cases. "
    "For settings, pass a small explicit mapping to Settings.from_env when possible. Use monkeypatch only when you are specifically testing process-environment integration. "
    "Do not patch time.time globally to a historical date and assume JWT’s separate datetime clock will agree. "
    "State which clock or environment boundary is being controlled, and restore changes after the test.",
    'def active(expires_at,now):\n    return now<expires_at\nsettings=Settings.from_env({"API_TOKEN_TTL":"120"})',
    checks(
        'import pytest\n@pytest.mark.parametrize("now,expected",[(99,True),(100,False),(101,False)])\ndef test_expiry_boundary(now,expected):\n    def active(expires_at,now):return now<expires_at\n    assert active(100,now) is expected'
    ),
    "The exact expiry instant is rejected. Every run uses the same inputs rather than sleeping for a real token to expire.",
    (
        "time.sleep(900)  # wait for every expiry test",
        "Supply controlled policy inputs or deliberately signed fixture claims",
        "Long real-time waits make tests slow and flaky without adding necessary evidence.",
    ),
    "Parse a known environment mapping without reading the actual machine environment.",
    'from orm_api.settings import Settings\ns=Settings.from_env({"API_TOKEN_TTL":"120","API_PORT":"8002"})\nprint(s.token_ttl,s.port)',
    "Use a scoped environment patch for one harmless named variable.",
    checks(
        'import os\ndef test_environment_restore(monkeypatch):\n    with monkeypatch.context() as patch:\n        patch.setenv("STUDYHUB_LESSON_LABEL","fictional")\n        assert os.environ["STUDYHUB_LESSON_LABEL"]=="fictional"'
    ),
    "Make clocks and configuration explicit where possible; patch only a narrow owned boundary and never expose real environment contents.",
    [
        (
            "Why avoid a long sleep for a simple expiry rule?",
            "Controlled inputs are faster and repeatable",
            "Because expiry never matters",
            "Because tests should skip time",
            "The policy can be checked directly at its boundary.",
        ),
        (
            "Should a configuration test print the entire real environment?",
            "No",
            "Always",
            "Only in CI",
            "It can contain credentials and unrelated private settings.",
        ),
    ],
)

lesson(
    2,
    "1. Choose the smallest useful test boundary",
    "Distinguish pure unit, real integration and browser end-to-end evidence.",
    [
        (
            "Unit/integration/end-to-end",
            "A unit test isolates a small policy; an integration test connects real components such as routes/models/SQLite; a browser end-to-end check exercises the visible client and running server together.",
        ),
        (
            "Testing pyramid; cost versus confidence",
            "Keep many fast focused checks and a smaller set of meaningful integrated flows. This is a design guide, not a fixed numerical ratio or permission to skip important interfaces.",
        ),
    ],
    "A settings parser can be tested without starting the database. Ownership needs real request identity and persisted rows. A broken explorer button needs a browser check. "
    "Pick the boundary that can actually detect the defect. Running a browser for every integer constraint is expensive and obscures diagnosis. "
    "Likewise, mocking the database cannot prove that its actual foreign key or migration works. "
    "The project suite combines fast configuration/transport checks with real temporary API flows. The repository adds a real loopback browser acceptance check. "
    "Name the evidence accurately: TestClient is integration tooling, not a real browser.",
    "# Policy -> unit; route + real DB -> integration; visible client + server -> browser E2E.",
    checks(
        'from orm_api.settings import Settings\nfrom lesson_support import practice\ndef test_configuration_unit():assert Settings.from_env({"API_TOKEN_TTL":"120"}).token_ttl==120\ndef test_readiness_integration():\n    with practice(seed=False) as (app,c,h):assert c.get("/health/ready").status_code==200'
    ),
    "One test checks a pure parser policy; the other starts the real app and checks its temporary database. Neither claims to exercise browser rendering.",
    (
        "# A mocked repository proves the real SQLite constraints",
        "Use the real owned database for database-integrity claims",
        "A fake cannot establish behaviour in the component it replaced.",
    ),
    "Classify three promises by their smallest useful boundary.",
    'plan={"TTL range":"unit","private CRUD persistence":"integration","Send request button":"browser end-to-end"}\nfor promise,boundary in plan.items():print(promise+": "+boundary)',
    "Verify an expected strict-model failure without starting an app.",
    checks(
        'import pytest\nfrom pydantic import ValidationError\nfrom orm_api.schemas import NoteCreate\ndef test_strict_boolean_unit():\n    with pytest.raises(ValidationError):NoteCreate(title="A",body="B",completed="false")'
    ),
    "Use the least expensive boundary that supplies the needed evidence, then cover interactions with targeted broader flows.",
    [
        (
            "Is TestClient a real browser?",
            "No",
            "Always",
            "Only with JavaScript",
            "It tests requests in-process, not browser rendering/clicks.",
        ),
        (
            "What should prove real database constraints?",
            "Tests against a real temporary database",
            "Only a mocked repository",
            "A screenshot alone",
            "The actual database must enforce the tested rule.",
        ),
    ],
)

lesson(
    2,
    "2. Follow a complete user journey",
    "Verify registration, login, private CRUD, relationships and logout as one coherent flow.",
    [
        (
            "Acceptance flow; state transition",
            "An acceptance flow follows a user goal through several real transitions. Assert intermediate representations so a late success cannot hide an earlier mistake.",
        ),
        (
            "Flow size",
            "Keep one coherent journey instead of a giant order-dependent suite. Focused tests still handle independent edge cases.",
        ),
    ],
    "A learner registers, gets a token, writes a note, updates it, adds known tags, deletes it and logs out. "
    "Each transition has its own status and data meaning. Follow Location rather than inventing an id. "
    "After delete, verify absence. After logout, verify replay refusal rather than merely observing an empty browser field. "
    "Use the real hash/JWT/SQLite implementation so the integration flow proves those components cooperate. "
    "Separate smaller failure tests make a broken step easier to diagnose than one enormous flow with dozens of unrelated goals.",
    "# register -> token -> create -> read -> modify -> tag -> delete -> logout -> replay refused",
    fixture(
        'register(client,"asha");headers=login(client,"asha")\nr=client.post("/v1/notes",headers=headers,json={"title":"Journey","body":"Follow the contract"})\nurl=r.headers["Location"];assert r.status_code==201\nassert client.patch(url,headers=headers,json={"completed":True}).json()["completed"] is True\nassert client.put(url+"/tags",headers=headers,json={"names":["api"]}).json()==["api"]\nassert client.delete(url,headers=headers).status_code==204\nassert client.get(url,headers=headers).status_code==404\nassert client.post("/v1/logout",headers=headers).status_code==204\nassert client.get("/v1/me",headers=headers).status_code==401\nprint("Complete private journey passed")',
        False,
    ),
    "The flow asserts real intermediate changes and the final revoked-access boundary, not just a collection of successful requests.",
    (
        "# Guess every new resource is id 1",
        "Use the returned representation/Location",
        "A client should follow the server’s created-resource contract.",
    ),
    "Check a complete replacement preserves id and creation time.",
    fixture(
        'before=client.get("/v1/notes/1",headers=headers).json()\nafter=client.put("/v1/notes/1",headers=headers,json={"title":"Replacement","body":"Complete","completed":False}).json()\nprint(before["id"]==after["id"],before["created_at"]==after["created_at"])'
    ),
    "Check logout returns no content and blocks the old credential.",
    fixture(
        'r=client.post("/v1/logout",headers=headers)\nprint(r.status_code,len(r.content),client.get("/v1/me",headers=headers).status_code)'
    ),
    "A coherent acceptance flow checks the state and access consequences of each meaningful user transition.",
    [
        (
            "What should be verified after logout?",
            "Old credential replay fails",
            "Only a button label changed",
            "The database is empty",
            "Server-side revocation is the access guarantee.",
        ),
        (
            "Where should a client find the created member URL?",
            "The Location response header",
            "A guessed id",
            "The CSS class",
            "The server provides its resource location.",
        ),
    ],
)

lesson(
    2,
    "3. Prove persistence across independent app lifetimes",
    "Test a file-backed restart without reading any existing installation.",
    [
        (
            "Restart integration fixture",
            "Construct two independent apps sequentially against the same explicitly owned temporary instance. This tests persistent database/key reuse rather than a shared in-memory object.",
        ),
        (
            "Resource shutdown",
            "Close the first TestClient/app before reopening the same SQLite files. Do not keep a live engine or Session merely to make a persistence test pass.",
        ),
    ],
    "An in-memory test can validate CRUD but cannot establish what happens after a process/app restart. "
    "Use an owned temporary directory, commit a note through the API, close the first app and construct a second app against that directory. "
    "The signing key and issued-login row persist too, so a still-valid token from that same instance can remain usable. "
    "This does not make tokens portable across unrelated projects or signing-key changes. "
    "A test should never copy or inspect the learner’s actual instance to exercise this behaviour.",
    "with TestClient(create_app(owned_path)) as first: ...\nwith TestClient(create_app(owned_path)) as second: ...",
    """from io import StringIO
from tempfile import TemporaryDirectory
from fastapi.testclient import TestClient
from orm_api import create_app
from lesson_support import register,login
with TemporaryDirectory() as folder:
    with TestClient(create_app(folder,log_stream=StringIO())) as first:
        register(first);headers=login(first)
        first.post("/v1/notes",headers=headers,json={"title":"Retained","body":"Owned file"})
    with TestClient(create_app(folder,log_stream=StringIO())) as second:
        print(second.get("/v1/notes",headers=headers).json()["items"][0]["title"])""",
    "The second app has a fresh lifespan and reads the committed file-backed row using the preserved key/login state.",
    (
        "# Keep the first Session open and call that a restart test",
        "Close the first app and construct another against owned files",
        "A live shared object does not demonstrate persistence across lifetimes.",
    ),
    "Verify the regular fixture owns a file-backed database path.",
    fixture(
        'print(app.state.engine.url.get_backend_name(),app.state.engine.url.database.endswith("notes.sqlite"))',
        False,
    ),
    "Verify a new independent fixture starts with no accounts.",
    fixture(
        "from sqlalchemy import select,func\nfrom orm_api.models import User\nwith app.state.sessions() as s:print(s.scalar(select(func.count()).select_from(User)))",
        False,
    ),
    "Persistence evidence needs a real owned file and a fresh app lifetime, not an accidentally shared in-memory resource.",
    [
        (
            "Can an in-memory-only test prove restart persistence?",
            "No",
            "Always",
            "Only if committed",
            "The durable-file boundary must be exercised.",
        ),
        (
            "Should the test read the actual learner database?",
            "No",
            "Always",
            "Only once",
            "Owned temporary files supply the necessary evidence.",
        ),
    ],
)

lesson(
    2,
    "4. Test failures that matter to users",
    "Prioritise invalid input, inaccessible resources, outages and recovery behaviours.",
    [
        (
            "Failure matrix; risk-based selection",
            "Choose tests from actual promises and consequences: rejected writes preserve data, outages get useful generic results and private resources stay inaccessible.",
        ),
        (
            "Fault injection",
            "A test can deliberately replace one dependency with a controlled failure. That is evidence about error handling, not proof that every real outage behaves identically.",
        ),
    ],
    "Most meaningful software failures happen outside the happy path: malformed input, duplicate names, stale credentials or unavailable storage. "
    "Keep rejection tests specific and compare relevant state afterward. "
    "The project sanitises validation details and unexpected-error responses, with a generated request id to correlate safe logs. "
    "An injected database-provider failure tests the generic error boundary without causing an actual disk problem or collecting real credentials. "
    "Do not turn every exception into an identical successful result; clients need truthful status semantics.",
    "# Invalid write -> 422 + unchanged data; inaccessible id -> 404; unexpected internal failure -> safe 500.",
    fixture(
        'before=client.get("/v1/notes/1",headers=headers).json()\nr=client.patch("/v1/notes/1",headers=headers,json={"completed":None})\nprint(r.status_code,client.get("/v1/notes/1",headers=headers).json()==before)\nprint(client.get("/v1/notes/999",headers=headers).status_code)'
    ),
    "The invalid field causes no mutation. A valid-shaped missing id produces a different 404 boundary.",
    (
        'except Exception:return {"ok":True}',
        "Return the appropriate failure and record only safe diagnostic fields",
        "False success prevents clients from responding correctly.",
    ),
    "Assert duplicate registration returns a conflict rather than replacing the account.",
    fixture(
        'print(register(client,"asha").status_code,client.get("/v1/me",headers=login(client,"asha")).status_code)'
    ),
    "Reject a password canary without echoing the submitted value.",
    fixture(
        'marker="x7Q!z"\nr=client.post("/v1/users",json={"username":"new_user","password":marker})\nprint(r.status_code,marker not in r.text)',
        False,
    ),
    "Choose failure tests by concrete user consequences and verify honest status, safe diagnostics and preserved state.",
    [
        (
            "Should an unexpected internal failure be reported as successful JSON?",
            "No",
            "Always",
            "Only during CI",
            "Clients need truthful failure semantics.",
        ),
        (
            "What does fault injection establish?",
            "The tested error-handling path",
            "Every possible real outage",
            "That all infrastructure is healthy",
            "It controls one specific failure boundary.",
        ),
    ],
)

lesson(
    2,
    "5. Use browser E2E where the visible experience matters",
    "Separate request integration checks from real clicks, rendering and browser storage.",
    [
        (
            "Real-browser acceptance check",
            "A browser drives visible controls against a loopback server. It catches JavaScript, navigation, responsive layout, token display and storage behaviour that TestClient cannot see.",
        ),
        (
            "Disposable profile; fictional session",
            "Browser tests use a new temporary profile and owned server files. They must not read an existing Chrome profile, saved passwords or real Study Hub data.",
        ),
    ],
    "The repository’s browser acceptance script opens the original offline explorer on an actual local server. "
    "It registers fictional users, uses the Send request buttons, performs private CRUD/tags, checks token masking and logout replay, then tests phone-width light/dark layouts. "
    "This evidence complements the pytest suite; it does not replace focused state/security tests. "
    "Keep a small set of coherent browser journeys instead of repeating every integer constraint through a slow UI. "
    "The Python example below verifies the public assets/schema contract only. It is explicitly not a browser test; the separate repository browser script supplies that evidence.",
    "# Repository author check: node tests/python-week41-project-browser.cjs\n# Uses an owned loopback server and a disposable Chrome profile.",
    fixture(
        'text=client.get("/docs").text\nsource=client.get("/assets/explorer.js").text\nprint("Local Notes API" in text,"/assets/explorer.js" in text)\nprint("localStorage" in source,"[kept in this tab only]" in source)',
        False,
    ),
    "These request checks prove asset availability and source markers, not that a real browser executed those controls correctly.",
    (
        "# HTML contains a button, therefore clicking it works",
        "Drive the real control in an isolated browser and check its result",
        "Static markup alone does not execute JavaScript or reveal interaction failures.",
    ),
    "Check the explorer script is served locally rather than requiring a CDN.",
    fixture(
        'text=client.get("/docs").text\nprint(\'src="/assets/explorer.js"\' in text,\'href="/assets/style.css"\' in text)',
        False,
    ),
    "List three failures that require browser-level evidence.",
    'for risk in ["Send request button does nothing","Token response is visible instead of masked","375px layout overflows"]:print(risk)',
    "Use real browser checks for interaction/rendering claims and preserve isolated profiles and fictional credentials.",
    [
        (
            "Can TestClient prove a JavaScript click works?",
            "No",
            "Always",
            "Only with OpenAPI",
            "It does not execute the visible browser application.",
        ),
        (
            "Which browser profile should verification use?",
            "A new disposable one",
            "The learner’s normal saved-login profile",
            "Any available personal profile",
            "Testing must not inspect real saved sessions or credentials.",
        ),
    ],
)

lesson(
    2,
    "6. Coverage guides investigation, not correctness claims",
    "Interpret executed-line evidence alongside assertion quality and missing scenarios.",
    [
        (
            "pytest-cov; line coverage; branch coverage",
            "Coverage records which code ran. Line coverage and branch coverage measure different execution aspects; neither proves the expected result was asserted.",
        ),
        (
            "Coverage gate; missing-line report",
            "A chosen minimum can prevent obvious untested growth, but it is a project policy, not a guarantee of quality. Read missing lines and prioritise meaningful scenarios.",
        ),
    ],
    "The CI gate asks for at least 75 percent line coverage across orm_api, and the suite produces a missing-line report. "
    "A line can execute while the test makes no useful assertion about it. Conversely, some rare infrastructure branches may need careful fault injection rather than a repeated happy path. "
    "Do not write tests that merely import every file to inflate a number. "
    "Use the report to ask what user-visible behaviour remains unverified, and add a focused case only when it addresses a concrete gap. "
    "The published coverage result belongs to the verified code/test run; future edits can change it.",
    "python -m pytest -q -p pytest_cov --cov=orm_api --cov-report=term-missing --cov-fail-under=75",
    'executed,total=75,100\nprint("Illustrative line coverage:",round(executed/total*100),"percent")\nprint("A line ran; a meaningful assertion is still required.")',
    "The arithmetic is an illustration, not the project’s measured result. Run the supplied coverage command to obtain current evidence.",
    (
        "# 100 percent coverage means no bugs",
        "Inspect meaningful assertions, branches and real failure scenarios",
        "Execution is not the same as correctness.",
    ),
    "Write a test with a meaningful expected result rather than import-only execution.",
    checks(
        "from orm_api.settings import Settings\ndef test_expected_default():assert Settings.from_env({}).token_ttl==900"
    ),
    "Distinguish coverage and assertion evidence explicitly.",
    'evidence={"coverage":"This line/branch executed","assertion":"The stated observable result matched","limits":"Untested cases and incorrect expectations can remain"}\nfor key,value in evidence.items():print(key+": "+value)',
    "Use coverage to locate evidence gaps, then judge the actual contracts, assertions and remaining risks.",
    [
        (
            "Does 100 percent line coverage prove no bugs?",
            "No",
            "Always",
            "Only for Python",
            "Execution can occur without checking the right result.",
        ),
        (
            "What should a missing-line report guide?",
            "Meaningful scenario investigation",
            "Import-only number inflation",
            "Deleting all difficult branches",
            "Choose tests for concrete remaining behaviour gaps.",
        ),
    ],
)

lesson(
    3,
    "1. Read a GitHub Actions workflow as executable configuration",
    "Connect an event, job, runner and step to a real automated check.",
    [
        (
            "Workflow; event; job; runner; step",
            "A workflow file responds to events such as push. Jobs run on selected machines called runners; ordered steps inside a job execute commands or reusable actions.",
        ),
        (
            "YAML; indentation; working directory",
            "YAML indentation defines structure. A job’s command working directory matters because relative requirements/test paths are resolved there.",
        ),
    ],
    "A workflow is not a badge decoration. It must install the intended environment and execute commands that return a failure when the contract is broken. "
    "The actual repository file is .github/workflows/python-week41.yml. The project handout quality-workflow.yml is an identical readable copy. "
    "This workflow responds to relevant push/pull-request paths and can also be started manually. It runs from docs/python-week41. "
    "GitHub supplies the hosted runner; the Python backend is not deployed by this workflow. GitHub Pages continues publishing the static Study Hub separately. "
    "The example reads the actual workflow handout without needing a GitHub account or triggering a run.",
    "jobs:\n  tests:\n    runs-on: ubuntu-latest\n    steps:\n      - run: python -m pytest -q",
    'from pathlib import Path\nfrom orm_api.database import PROJECT\ns=(PROJECT/"quality-workflow.yml").read_text(encoding="utf-8")\nprint("name: Python Week 41 quality" in s,"working-directory: docs/python-week41" in s)\nprint("python -m pytest" in s)',
    "The distributed handout matches the checked-in workflow’s actual test command and project directory. Reading it does not run hosted jobs.",
    (
        "# Workflow exists, therefore tests must have run successfully",
        "Inspect a run for the exact commit and every required job",
        "Configuration presence and successful execution are different evidence.",
    ),
    "Find the actual lint and format-check steps.",
    'from orm_api.database import PROJECT\ns=(PROJECT/"quality-workflow.yml").read_text(encoding="utf-8")\nprint("python -m ruff check ." in s,"python -m ruff format --check ." in s)',
    "Verify the workflow is manually runnable as well as path-filtered.",
    'from orm_api.database import PROJECT\ns=(PROJECT/"quality-workflow.yml").read_text(encoding="utf-8")\nprint("workflow_dispatch:" in s,"paths:" in s)',
    "A useful workflow executes explicit checks in the correct directory and must be verified on the intended commit.",
    [
        (
            "Does a checked-in workflow prove a successful CI run?",
            "No",
            "Always",
            "If it has a name",
            "Inspect actual run/job results for the exact commit.",
        ),
        (
            "What determines relative command paths?",
            "The step/job working directory",
            "Only the repository display name",
            "The browser URL",
            "Commands resolve paths in their configured execution directory.",
        ),
    ],
)

lesson(
    3,
    "2. Reproduce the environment before comparing results",
    "Install pinned dependencies and choose Python versions explicitly.",
    [
        (
            "Pinned requirements; interpreter matrix",
            "Pins select known dependency versions. A matrix runs the same checks on declared Python versions; it detects interpreter differences but does not cover every operating system automatically.",
        ),
        (
            "setup-python; cache key",
            "The setup action selects an interpreter. A dependency-aware cache speeds downloads; it is an optimisation, not proof that packages were freshly validated or secure forever.",
        ),
    ],
    "A local test may pass because an unrecorded package was already installed. A clean runner exposes that missing dependency. "
    "The project separates runtime requirements from requirements-dev, which adds pytest, coverage and Ruff. "
    "CI explicitly tests Python 3.12 and 3.13 on Ubuntu. The local verification environment is Python 3.12 on Windows. "
    "The AnyIO pin keeps the selected Starlette/TestClient interface compatible with strict warning checks. Pins still need deliberate review over time. "
    "A cached download must not replace the install command or change the declared dependency set.",
    'strategy:\n  matrix:\n    python-version: ["3.12","3.13"]\n# python -m pip install -r requirements-dev.txt',
    'from pathlib import Path\nfrom orm_api.database import PROJECT\nrequirements=(PROJECT/"requirements-dev.txt").read_text(encoding="utf-8")\nprint("pytest==9.1.1" in requirements,"ruff==0.17.1" in requirements)',
    "The development tools are declared explicitly rather than relying on a developer’s global installation.",
    (
        "# CI can use whichever Python happens to be on PATH",
        "Select declared Python versions and install the known requirements",
        "Runner defaults and global environments can change.",
    ),
    "Inspect the two declared Python versions in the handout.",
    'from orm_api.database import PROJECT\ns=(PROJECT/"quality-workflow.yml").read_text(encoding="utf-8")\nprint("[\'3.12\', \'3.13\']" in s)',
    "Verify runtime requirements do not require pytest just to run the server.",
    'from orm_api.database import PROJECT\nruntime=(PROJECT/"requirements.txt").read_text(encoding="utf-8")\nprint("pytest==" in runtime,"fastapi==" in runtime)',
    "Compare checks in explicit reproducible environments and keep cache behaviour separate from dependency policy.",
    [
        (
            "Does a Python-version matrix automatically test Windows and Linux?",
            "No",
            "Always",
            "Only with two versions",
            "The selected runner OS is a separate dimension.",
        ),
        (
            "Does pinning mean dependencies stay secure forever?",
            "No",
            "Always",
            "Only in CI",
            "Pins reproduce versions and still require reviewed maintenance.",
        ),
    ],
)

lesson(
    3,
    "3. Test, lint and formatting checks catch different defects",
    "Use several complementary gates without confusing style with correctness.",
    [
        (
            "Ruff lint; formatter",
            "Lint checks selected static rules such as undefined names and unused imports. The formatter normalises source layout. Neither executes the API’s behaviour tests.",
        ),
        (
            "Non-mutating CI gate",
            "ruff format --check reports a mismatch without editing the runner’s source as a hidden repair. Local formatting can be applied deliberately before committing.",
        ),
    ],
    "A formatted function can return the wrong value, and a correct happy path can still contain an undefined name in an untested branch. "
    "The project uses selected Ruff E/F rules, a separate formatting check and pytest with a coverage gate. "
    "Keep the commands understandable so a failed step identifies the kind of problem to investigate. "
    "Do not add continue-on-error just to hide a broken required gate. Fix the relevant defect or explicitly redesign the justified gate. "
    "The examples inspect the actual configuration rather than modifying arbitrary source files.",
    "python -m ruff check .\npython -m ruff format --check .\npython -m pytest -q",
    'from orm_api.database import PROJECT\ns=(PROJECT/"pyproject.toml").read_text(encoding="utf-8")\nprint(\'select = ["E4", "E7", "E9", "F"]\' in s)\nprint("filterwarnings" in s)',
    "The lint rule set and strict pytest warning policy are explicit. They support behavioural tests rather than replacing them.",
    (
        "# Autoformat passed, therefore authentication is correct",
        "Run actual authentication/ownership acceptance tests too",
        "Layout normalisation cannot prove runtime access policy.",
    ),
    "Classify three gate failures by what they detect.",
    'for defect,gate in [("undefined variable","lint"),("inconsistent indentation/layout","format check"),("cross-owner write succeeds","behaviour test")]:print(defect+": "+gate)',
    "Check the workflow does not hide failed steps.",
    'from orm_api.database import PROJECT\ns=(PROJECT/"quality-workflow.yml").read_text(encoding="utf-8")\nprint("continue-on-error" not in s)',
    "Keep lint, formatting and behavioural evidence separate and let a required gate fail honestly.",
    [
        (
            "Does formatting prove correct access control?",
            "No",
            "Always",
            "Only if Ruff is used",
            "Access control needs behavioural tests.",
        ),
        (
            "Should a broken required check be hidden with continue-on-error?",
            "No",
            "Always",
            "Only on main",
            "Repair the defect or deliberately review the gate policy.",
        ),
    ],
)

lesson(
    3,
    "4. Keep CI permissions and credentials minimal",
    "Run public practice tests without giving jobs unnecessary write access or real secrets.",
    [
        (
            "contents: read; persist-credentials: false",
            "The workflow needs to read source, not push commits or access private learner accounts. Checkout is configured not to retain its credential for later commands.",
        ),
        (
            "pull_request versus pull_request_target",
            "Untrusted pull-request code should not casually run with elevated base-repository credentials. This workflow uses ordinary pull_request and contains no real application secret.",
        ),
    ],
    "The tests generate fictional accounts and temporary signing keys. No GitHub personal token or real API key is needed. "
    "Set the minimum token permissions and avoid printing environment variables, request headers or private runtime files into CI logs/artifacts. "
    "Do not copy a learner database to a runner to make tests realistic; controlled fixtures supply the relevant structure. "
    "The workflow uses ordinary push/pull-request events, a bounded job timeout and no deployment/publish permission. "
    "Reusable actions are dependencies too; the project uses official maintained actions at verified major versions, which can be hardened further with reviewed full commit pins.",
    "permissions:\n  contents: read\n# checkout: persist-credentials: false",
    'from orm_api.database import PROJECT\ns=(PROJECT/"quality-workflow.yml").read_text(encoding="utf-8")\nprint("contents: read" in s,"persist-credentials: false" in s)\nprint("pull_request_target" in s,"secrets." in s)',
    "The configuration requests read-only contents and no personal/application secret input. It does not elevate untrusted PR execution through pull_request_target.",
    (
        "# Put a real learner token into the workflow file",
        "Generate isolated fictional test state; keep source/jobs credential-minimal",
        "Public test infrastructure must not expose private account credentials.",
    ),
    "Verify the supplied example environment file contains no secret assignment.",
    'from orm_api.database import PROJECT\ns=(PROJECT/".env.example").read_text(encoding="utf-8")\nprint(any(line.startswith("API_JWT_SECRET=") for line in s.splitlines()))',
    "Check a settings object’s representation masks its explicitly fictional secret.",
    'from orm_api.settings import Settings\ns=Settings(jwt_secret=b"fictional-key-"*4)\nprint("fictional-key" not in repr(s))',
    "CI should validate public source with isolated fixtures and the smallest permissions its jobs actually need.",
    [
        (
            "Does this suite need the learner’s real GitHub token?",
            "No",
            "Always",
            "Only for unit tests",
            "Its accounts/keys are local fictional fixtures.",
        ),
        (
            "Why avoid casually using pull_request_target for untrusted code?",
            "It can expose elevated base-repository context",
            "It changes Python syntax",
            "It disables every test",
            "Event and credential scope are part of the trust boundary.",
        ),
    ],
)

lesson(
    3,
    "5. Read exact-commit CI results and keep checks bounded",
    "Distinguish queued, running, failed, cancelled and successful jobs.",
    [
        (
            "Job status; matrix result",
            "A successful check must correspond to the intended commit and all required matrix jobs. Queued/in-progress/cancelled is not a passing result.",
        ),
        (
            "Timeout; concurrency cancellation",
            "A timeout bounds hung work. Concurrency settings can cancel obsolete runs on the same workflow/ref so a newer commit does not waste duplicate runner work.",
        ),
    ],
    "After push, inspect the run’s commit SHA and each Python-version job. A green result from an earlier commit says nothing definitive about the new edit. "
    "Read the first failing required step: install, lint, format or tests. The repair depends on which boundary failed. "
    "A cancelled obsolete run is neither evidence the code passed nor necessarily a defect; check the latest intended run. "
    "Path filters intentionally limit when this project CI runs, while workflow_dispatch allows a manual relevant check. "
    "Hosted CI requires network for runners/packages; the installed local project tests can run without live external services.",
    "# commit -> workflow run -> every required matrix job -> conclusion",
    'runs=[{"sha":"old","state":"success"},{"sha":"wanted","state":"in_progress"}]\ncurrent=next(r for r in runs if r["sha"]=="wanted")\nprint("Wanted commit passed:",current["state"]=="success")',
    "This fictional status example prevents a common interpretation error: an older success does not make the wanted in-progress commit verified.",
    (
        "# An old green badge proves today’s new commit passed",
        "Check the exact commit and all required job conclusions",
        "Badges and previous results can lag behind the intended change.",
    ),
    "Inspect the workflow’s timeout and concurrency cancellation policy.",
    'from orm_api.database import PROJECT\ns=(PROJECT/"quality-workflow.yml").read_text(encoding="utf-8")\nprint("timeout-minutes: 10" in s,"cancel-in-progress: true" in s)',
    "Classify incomplete status values as not yet verified.",
    'for state in ["queued","in_progress","cancelled","failure","success"]:print(state,state=="success")',
    "Use exact-commit and per-job evidence, and bound runner work without treating incomplete states as success.",
    [
        (
            "Does cancelled mean passed?",
            "No",
            "Always",
            "Only after push",
            "Cancellation does not execute a successful verification conclusion.",
        ),
        (
            "Which commit should a reported CI result match?",
            "The exact intended edit commit",
            "Any old green run",
            "The first repository commit",
            "Verification must correspond to the code being delivered.",
        ),
    ],
)

lesson(
    3,
    "6. Keep a local gate equivalent to CI",
    "Run the same checks before pushing and record their scope honestly.",
    [
        (
            "Local/CI parity",
            "Use the same requirements and commands locally and in CI. Different OS/interpreter combinations can still reveal differences, which is why the matrix adds evidence.",
        ),
        (
            "Quality gate versus release approval",
            "Passing configured checks is one release input, not proof that all deployment, security, recovery and operational needs are satisfied.",
        ),
    ],
    "Install the development requirements, run tests/coverage, lint and format check from the project folder before pushing. "
    "Do not claim every runtime environment is validated because two matrix versions passed on one runner OS. "
    "Keep a concise verification record naming commands, results and relevant limits. Avoid copying secrets or the entire console environment into that record. "
    "The repository workflow applies these gates automatically on relevant changes. It does not deploy the Python server or configure branch protection. "
    "A branch-protection requirement is a separate repository policy decision; a workflow alone does not enforce it.",
    "python -m pip install -r requirements-dev.txt\npython -m pytest -q -p pytest_cov --cov=orm_api --cov-fail-under=75\npython -m ruff check .\npython -m ruff format --check .",
    'from orm_api.database import PROJECT\ns=(PROJECT/"quality-workflow.yml").read_text(encoding="utf-8")\ncommands=["python -m pip install -r requirements-dev.txt","python -m ruff check .","python -m ruff format --check .","python -m pytest -q"]\nprint(all(command in s for command in commands))',
    "The same declared commands exist in the workflow. Their successful execution must still be confirmed through actual local/hosted runs.",
    (
        "# A workflow automatically enables required branch protection",
        "Treat workflow execution and repository merge policy separately",
        "Checking and enforcing merge requirements are different configuration tasks.",
    ),
    "Make a small verification record with explicit scope instead of a blanket production claim.",
    'record={"local":"declared commands run in owned fixture environment","hosted":"check exact SHA/matrix conclusions","not_proven":"TLS, public deployment and recovery operations"}\nfor key,value in record.items():print(key+": "+value)',
    "Run a tiny real test through the same pytest toolchain.",
    checks(
        'def test_verification_record_scope():\n    record={"tests":"passed","deployment":"not performed"}\n    assert record["tests"]=="passed" and record["deployment"]!="passed"'
    ),
    "Keep local/CI commands aligned and report exactly which checks, environments and operational boundaries were verified.",
    [
        (
            "Does a workflow automatically configure branch protection?",
            "No",
            "Always",
            "Only on main",
            "Merge requirements are a separate repository policy.",
        ),
        (
            "Do passed tests alone prove public deployment readiness?",
            "No",
            "Always",
            "Only above 75 percent",
            "Operations, security and recovery need additional evidence.",
        ),
    ],
)

lesson(
    4,
    "1. Separate deployment configuration from code",
    "Read named settings through a validated boundary instead of editing Python per environment.",
    [
        (
            "Environment variable; Settings.from_env",
            "Process environment values arrive as text. The project parses only named configuration into an immutable Settings object; tests can pass an explicit mapping instead of reading the real machine.",
        ),
        (
            "Deployment configuration versus business rules",
            "Ports, instance location, log level and token lifetime can vary by environment. Not every constant or security invariant should become an arbitrary visitor-controlled setting.",
        ),
    ],
    "Changing an instance directory or port should not require editing a route. Put deployment-specific choices behind one explicit configuration interface. "
    "The project reads APP_ENV, STUDYHUB_INSTANCE_DIR, API_LOG_LEVEL, API_TOKEN_TTL, API_PORT and an optional private API_JWT_SECRET. "
    "Unknown unrelated environment values are not copied into the Settings object or logged. "
    "The same app factory receives the validated settings in development, tests and a stricter production-mode configuration. "
    "Mode names do not install HTTPS, account recovery, rate limiting or public hosting; those remain separate operational work.",
    'settings=Settings.from_env({"API_TOKEN_TTL":"120","API_PORT":"8002"})\napp=create_app(settings=settings)',
    'from orm_api.settings import Settings\ns=Settings.from_env({"APP_ENV":"testing","API_TOKEN_TTL":"120","API_PORT":"8002"})\nprint(s.environment,s.token_ttl,s.port)',
    "Text configuration becomes validated typed values. This example intentionally supplies a harmless mapping instead of printing the real process environment.",
    (
        "# Edit a hardcoded password/port in every route",
        "Load validated named settings once before app construction",
        "One configuration boundary is easier to review and test.",
    ),
    "Use defaults without relying on the current machine’s environment.",
    "from orm_api.settings import Settings\ns=Settings.from_env({})\nprint(s.environment,s.token_ttl,s.port)",
    "Verify an unrelated environment entry is not added as an arbitrary settings attribute.",
    'from orm_api.settings import Settings\ns=Settings.from_env({"UNRELATED_VALUE":"fictional"})\nprint(hasattr(s,"UNRELATED_VALUE"))',
    "Parse a small named configuration contract and keep environment variability separate from application rules.",
    [
        (
            "How do environment numbers initially arrive?",
            "As text",
            "As database rows",
            "As Boolean objects",
            "The parser must convert and validate textual values.",
        ),
        (
            "Does APP_ENV=production automatically provide HTTPS and recovery?",
            "No",
            "Always",
            "Only on GitHub Pages",
            "A mode label cannot implement missing operations or infrastructure.",
        ),
    ],
)

lesson(
    4,
    "2. Validate configuration before starting resources",
    "Reject invalid ranges and unsupported modes without exposing input values.",
    [
        (
            "Fail-fast configuration",
            "Validate required types/ranges before opening the application’s resources. A configuration error should be explicit rather than silently falling back to an insecure or surprising value.",
        ),
        (
            "Frozen dataclass; __post_init__",
            "A frozen dataclass prevents ordinary later field assignment. __post_init__ applies project-specific checks after construction, keeping direct construction and parsed settings consistent.",
        ),
    ],
    "A port outside 1–65535 cannot be used as declared. A token lifetime of zero or an arbitrary string is not a reasonable silent default. "
    "The project validates TTL 60–3600, allowed environment names and INFO/WARNING/ERROR log levels before constructing the app. "
    "Both direct Settings(...) and from_env(...) follow the same checks. "
    "Error messages name the invalid configuration field/rule without interpolating the submitted secret. "
    "A failing config must not reset an instance directory or replace its signing key as a recovery shortcut.",
    "try:settings=Settings.from_env(values)\nexcept ValueError:\n    # report the named rule; do not dump values",
    checks(
        'import pytest\nfrom orm_api.settings import Settings\n@pytest.mark.parametrize("values",[{"API_PORT":"70000"},{"API_TOKEN_TTL":"0"},{"API_TOKEN_TTL":"wrong"},{"APP_ENV":"unknown"}])\ndef test_bad_configuration(values):\n    with pytest.raises(ValueError):Settings.from_env(values)'
    ),
    "Each invalid configuration is rejected directly, before any server or learner data is involved.",
    (
        "ttl=int(value) if value else 900  # hide supplied bad configuration",
        "Validate supplied values and reject broken configuration explicitly",
        "An invalid supplied value is not the same as omission.",
    ),
    "Test both allowed endpoints of the token-lifetime range.",
    checks(
        "from orm_api.settings import Settings\ndef test_bounds():\n    assert Settings(token_ttl=60).token_ttl==60\n    assert Settings(token_ttl=3600).token_ttl==3600"
    ),
    "Show a short secret is rejected without printing its bytes.",
    'from orm_api.settings import Settings\ntry:Settings(jwt_secret=b"fictional-short")\nexcept ValueError:print("Secret configuration rejected without displaying it")',
    "Fail fast on bad configuration, and keep both the original runtime data and secret values out of the error path.",
    [
        (
            "Should an invalid supplied TTL silently become the default?",
            "No",
            "Always",
            "Only if zero",
            "A supplied bad value should be rejected by the declared contract.",
        ),
        (
            "When should settings validation happen?",
            "Before starting app resources",
            "After returning success",
            "Only during an outage",
            "Early validation avoids starting with invalid assumptions.",
        ),
    ],
)

lesson(
    4,
    "3. Keep secrets outside public source and representations",
    "Distinguish private runtime material, safe examples and masked object displays.",
    [
        (
            "Secret source; private runtime key",
            "Development uses an ignored local random signing.key. Production-mode configuration requires an externally supplied signing secret; it is never requested from a learner in chat or committed to source.",
        ),
        (
            "repr=False is masking, not encryption",
            "The secret field is excluded from a Settings repr. The value still exists in process memory and can be exposed by careless serialization or logging.",
        ),
    ],
    "A public JS file, HTML page, JSON handout or SQL table shipped with a static site cannot hide a real secret from its visitors. "
    "Keep credentials out of public source and retain private runtime files outside version control. "
    "The provided .env.example contains harmless values/comments only. The app does not auto-load that file; it reads process variables supplied deliberately. "
    "Changing a signing secret invalidates signatures from the old key unless a separate reviewed rotation strategy is implemented; this project has no multi-key rotation protocol. "
    "Do not print a configuration object via a generic asdict dump or print os.environ just because its normal repr masks one field.",
    "jwt_secret:bytes|None=field(default=None,repr=False)\n# Actual secret supplied privately, never committed.",
    'from orm_api.settings import Settings\ns=Settings(environment="production",jwt_secret=b"fictional-local-test-key-"*2)\nprint("Secret omitted from repr:","fictional-local-test-key" not in repr(s))\nprint("Secret still exists in memory:",s.jwt_secret is not None)',
    "The example uses a clearly fictional test value and prints only Boolean properties. Masking reduces accidental display; it is not encrypted storage.",
    (
        "# Hide a real password in another public JS file",
        "Keep real credentials outside distributed source/runtime exports",
        "Changing the filename does not make a publicly served value secret.",
    ),
    "Verify production-mode construction rejects a missing secret.",
    checks(
        'import pytest\nfrom orm_api.settings import Settings\ndef test_production_requires_secret():\n    with pytest.raises(ValueError):Settings(environment="production")'
    ),
    "Inspect the example file for safe defaults without copying real environment values.",
    'from orm_api.database import PROJECT\ns=(PROJECT/".env.example").read_text(encoding="utf-8")\nprint("APP_ENV=development" in s,not any(line.startswith("API_JWT_SECRET=") for line in s.splitlines()))',
    "Use private secret provisioning and ignored runtime artifacts; masking helps display safety but does not create confidentiality by itself.",
    [
        (
            "Can putting a secret in public JS hide it from visitors?",
            "No",
            "Always",
            "Only if minified",
            "Anything served publicly can be inspected.",
        ),
        (
            "Is repr=False encryption?",
            "No",
            "Always",
            "Only for bytes",
            "It suppresses one display representation; the value remains available in memory.",
        ),
    ],
)

lesson(
    4,
    "4. Select an owned instance explicitly",
    "Keep test, practice and existing project data paths separate.",
    [
        (
            "Instance-path configuration",
            "STUDYHUB_INSTANCE_DIR selects this project’s owned local database/key location. Tests pass their temporary path explicitly and therefore do not inherit a real instance from process configuration.",
        ),
        (
            "Path selection versus migration permission",
            "Selecting a file path does not authorise resetting, stamping or upgrading unknown existing data. The Week 40 known-schema/refusal policy remains in force.",
        ),
    ],
    "A correct test command pointed at the wrong persistent directory can still be destructive. Make ownership of its data path visible. "
    "The create_app(instance_path=...) fixture constructs testing settings directly, while the guarded server entry point explicitly reads environment settings. "
    "The factory rejects supplying both an instance_path and a settings object, avoiding ambiguous precedence. "
    "The database initialiser still refuses unfamiliar history and known older schemas rather than silently dropping or migrating them. "
    "No exercise needs the learner’s actual Week 40 database, Study Hub localStorage or Gist token.",
    'settings=Settings(instance_dir=owned_temp_path,environment="testing")\napp=create_app(settings=settings)',
    checks(
        'from io import StringIO\nfrom pathlib import Path\nfrom fastapi.testclient import TestClient\nfrom orm_api import create_app\nfrom orm_api.settings import Settings\ndef test_owned_instance(tmp_path):\n    settings=Settings(instance_dir=tmp_path/"isolated",environment="testing")\n    with TestClient(create_app(settings=settings,log_stream=StringIO())) as c:\n        assert c.get("/health/ready").status_code==200\n    assert (settings.instance_dir/"notes.sqlite").is_file()'
    ),
    "The test creates its own migrated file inside pytest’s temporary directory and releases the app before completion.",
    (
        "# Use whatever real instance path happens to be configured",
        "Pass a test-owned path/config explicitly",
        "A test must not accidentally inherit persistent learner data.",
    ),
    "Reject ambiguous factory configuration.",
    checks(
        "import pytest\nfrom orm_api import create_app\nfrom orm_api.settings import Settings\ndef test_no_ambiguous_precedence(tmp_path):\n    with pytest.raises(ValueError):create_app(tmp_path,settings=Settings(instance_dir=tmp_path))"
    ),
    "Show the regular practice fixture declares testing mode.",
    fixture(
        "print(app.state.settings.environment,app.state.settings.instance_dir.name)",
        False,
    ),
    "Make the instance owner and factory configuration source explicit before any file-backed resource is started.",
    [
        (
            "Does choosing a path permit resetting an unfamiliar database?",
            "No",
            "Always",
            "Only if it has the expected filename",
            "Ownership and safe schema operations remain separate requirements.",
        ),
        (
            "Why reject both instance_path and settings together?",
            "To avoid ambiguous configuration precedence",
            "To remove all tests",
            "To expose a secret",
            "The factory should have one clear configuration source.",
        ),
    ],
)

lesson(
    4,
    "5. Change an environment value while preserving behaviour",
    "Verify that a configuration change affects only the declared policy.",
    [
        (
            "Configuration contract test",
            "Construct the same app code with a different valid configuration, then assert the intended policy change and unchanged core behaviour.",
        ),
        (
            "Token lifetime configuration",
            "The selected TTL is used in both signed exp and server login expiry, and returned as expires_in. Changing a display label alone would not change access policy.",
        ),
    ],
    "A setting is useful only if the relevant code actually uses it. A token TTL must affect the signed claim and the server-side login record consistently. "
    "The example creates an owned app with a 120-second TTL and verifies the response plus authenticated identity. "
    "No real wait is needed: inspect the verified claim interval or declared expiry response in a controlled fixture. "
    "Environment mode does not fork the business implementation into separate untested versions. The same factory/routes are used. "
    "Still test each deployment environment’s infrastructure separately; matching app code cannot prove network/TLS behaviour.",
    'settings=Settings(instance_dir=owned_path,environment="testing",token_ttl=120)',
    """from io import StringIO
from tempfile import TemporaryDirectory
from fastapi.testclient import TestClient
from orm_api import create_app
from orm_api.settings import Settings
from lesson_support import register,PRACTICE_PASSWORD
with TemporaryDirectory() as folder:
    config=Settings(instance_dir=folder,environment="testing",token_ttl=120)
    with TestClient(create_app(settings=config,log_stream=StringIO())) as c:
        register(c)
        r=c.post("/v1/token",data={"username":"asha","password":PRACTICE_PASSWORD})
        h={"Authorization":"Bearer "+r.json()["access_token"]}
        print(r.json()["expires_in"],c.get("/v1/me",headers=h).status_code)""",
    "The intended shorter lifetime is reflected in the token response and the normal identity flow still succeeds. No token bytes are printed.",
    (
        "# Change expires_in text but leave signed/server expiry unchanged",
        "Apply the validated TTL consistently to all expiry boundaries",
        "A display-only change would misrepresent actual access lifetime.",
    ),
    "Verify the default fixture’s signed lifetime without displaying its credential.",
    fixture(
        'import jwt\nfrom orm_api import ISSUER,AUDIENCE\nencoded=headers["Authorization"].split(" ",1)[1]\nclaims=jwt.decode(encoded,app.state.key,algorithms=["HS256"],issuer=ISSUER,audience=AUDIENCE)\nprint(claims["exp"]-claims["iat"],app.state.settings.token_ttl)'
    ),
    "Create two validated configurations with distinct safe ports.",
    'from orm_api.settings import Settings\nprint(Settings.from_env({"API_PORT":"8002"}).port,Settings.from_env({"API_PORT":"8003"}).port)',
    "Prove a setting changes the real declared policy while the core application contract remains intact.",
    [
        (
            "Is changing an expiry label enough?",
            "No",
            "Always",
            "Only with JWT",
            "Signed and server-side expiry must match the declared policy.",
        ),
        (
            "Do identical routes prove public TLS is configured?",
            "No",
            "Always",
            "Only in production mode",
            "Infrastructure needs its own verified setup.",
        ),
    ],
)

lesson(
    4,
    "6. Make a release configuration checklist with honest limits",
    "Separate verified local readiness work from missing public deployment controls.",
    [
        (
            "Twelve-factor configuration idea",
            "Deployment-specific configuration should be separate from source. That principle alone does not supply security, backups, incident response or every environment dependency.",
        ),
        (
            "Release evidence and recovery plan",
            "A release needs the exact tested version, validated config, private secret provisioning, reviewed migration/backup strategy and operational monitoring appropriate to its environment.",
        ),
    ],
    "Review configuration defaults, ownership of persistent paths and which values must stay private before starting an installation. "
    "Record what was tested locally and in CI rather than using production-ready as a blanket label. "
    "This local project adds strong learning evidence, but it still lacks public HTTPS/reverse proxy, login throttling, account recovery/MFA, distributed operations and a tested production restore procedure. "
    "The next Docker/deployment week builds on these foundations; changing the bind address is not a complete deployment plan. "
    "A useful checklist points to concrete evidence or a clearly pending task, not a promise that a setting will solve everything.",
    "# tested version + validated config + private secrets + backup/migration + environment-specific operations",
    'checklist={"test_data":"fictional and isolated","secrets":"external or ignored local key","schema":"reviewed Alembic history","public_TLS":"not implemented here","restore_drill":"separate operational work"}\nfor item,state in checklist.items():print(item+": "+state)',
    "The checklist distinguishes implemented safeguards from required future operational work instead of claiming an untested public release.",
    (
        "APP_ENV=production  # assume every operational problem solved",
        "Validate configuration and separately verify deployment/recovery controls",
        "A mode flag cannot implement missing infrastructure.",
    ),
    "Verify the public server entry point remains loopback-bound.",
    'from orm_api.database import PROJECT\ns=(PROJECT/"app.py").read_text(encoding="utf-8")\nprint(\'host="127.0.0.1"\' in s)',
    "Record a pending control without falsely marking it tested.",
    'record={"control":"public restore drill","status":"not performed","next":"test a reviewed backup in the intended environment"}\nprint(record["control"],record["status"])',
    "Use configuration discipline as one release foundation and describe unimplemented or unverified operational controls explicitly.",
    [
        (
            "Does a production mode label prove production readiness?",
            "No",
            "Always",
            "Only after tests",
            "Configuration is only one part of a release.",
        ),
        (
            "How should an unperformed restore drill be recorded?",
            "As pending/not performed",
            "As passed because a backup exists",
            "As irrelevant forever",
            "Recovery needs actual environment-specific evidence.",
        ),
    ],
)

lesson(
    5,
    "1. Emit structured request logs with a correlation id",
    "Record useful operational facts without dumping the request.",
    [
        (
            "Structured JSON log; allowlist",
            "A structured log emits named machine-readable fields. The project allowlists timestamp, event, method, route template, status, duration_ms and generated request_id.",
        ),
        (
            "ASGI middleware; correlation id",
            "Middleware surrounds request execution. It adds a fresh X-Request-ID and records the same identifier so an operator can correlate a response with a safe log entry.",
        ),
    ],
    "A useful log answers which operation ran, how it ended and how long it took. It does not need a password, body or bearer header. "
    "The project generates its own request id instead of trusting arbitrary user-supplied identifiers as log text. "
    "Route labels use registered templates such as /v1/notes/{note_id}, never the raw query or a private note title. "
    "The fixture captures these logs in its own StringIO, available as app.state.lesson_logs for controlled teaching examples. The real local server writes JSON records to its configured stream. "
    "Timestamps and latency vary per run; the example checks the structure and correlation rather than publishing a credential or pretending timing is constant.",
    '{"event":"http_request","route":"/v1/notes/{note_id}","status":200,"request_id":"generated"}',
    fixture(
        'import json\nr=client.get("/v1/notes/1",headers=headers)\nentry=json.loads(app.state.lesson_logs.getvalue().splitlines()[-1])\nprint(sorted(entry))\nprint(entry["route"],entry["status"],entry["request_id"]==r.headers["X-Request-ID"])'
    ),
    "The log and response share a generated id while the route stays a template. No actual bearer credential or record body is printed.",
    (
        "logger.info(str(request.headers))",
        "Log only the declared operational fields",
        "Header dumps can contain credentials and session material.",
    ),
    "Check that a public health response includes a generated request id.",
    fixture(
        'r=client.get("/health")\nprint(r.status_code,len(r.headers["X-Request-ID"]))',
        False,
    ),
    "Read one log entry’s event and nonnegative measured duration.",
    fixture(
        'import json\nclient.get("/health")\nentry=json.loads(app.state.lesson_logs.getvalue().splitlines()[-1])\nprint(entry["event"],entry["duration_ms"]>=0)',
        False,
    ),
    "Log a bounded set of operational facts and correlate them with responses without collecting request secrets.",
    [
        (
            "What should replace raw request/header dumps?",
            "An explicit safe field allowlist",
            "A bigger secret log file",
            "The entire environment",
            "Collect only facts needed for the operational question.",
        ),
        (
            "Why use a generated correlation id?",
            "To match a response with its safe log record",
            "To authorise every note",
            "To encrypt the payload",
            "It supports diagnosis without being an access credential.",
        ),
    ],
)

lesson(
    5,
    "2. Test log redaction and bounded labels",
    "Assert that credentials and user-controlled details never enter application request records.",
    [
        (
            "Canary; negative log assertion",
            "A clearly fictional marker makes accidental disclosure detectable. Assert that it is absent from captured output while required safe fields remain present.",
        ),
        (
            "Cardinality; route template",
            "Unbounded raw paths/queries can create a different metric/log label for every user value. Registered route templates and an unmatched bucket keep labels tied to known operations.",
        ),
    ],
    "Do not assume logs are safe merely because nobody intentionally typed logger.info(password). Framework dumps, exception text and query strings can leak information indirectly. "
    "Send a fictional marker through a query and assert the captured application logs omit it. "
    "Likewise verify the actual fixture bearer value and known fictional password are absent. "
    "This field allowlist applies to the application’s own request telemetry; unrelated future plugins, proxy access logs or external monitoring systems need separate review. "
    "Unknown URLs get an unmatched route label instead of storing arbitrary path text.",
    "assert marker not in captured_logs\nassert bearer_value not in captured_logs",
    fixture(
        'marker="fictional-private-query-canary"\nclient.get("/v1/notes",headers=headers,params={"q":marker})\ntext=app.state.lesson_logs.getvalue()\nprint(marker not in text,PRACTICE_PASSWORD not in text,headers["Authorization"] not in text)'
    ),
    "The negative checks verify absence against actual captured telemetry rather than relying only on a code comment.",
    (
        "# Log every raw URL to make metrics detailed",
        "Use route templates and bounded fallback labels",
        "Private query text and arbitrary ids are unnecessary/high-cardinality labels.",
    ),
    "Request an unknown private-looking path and inspect only its safe fallback route label.",
    fixture(
        'import json\nclient.get("/not-real-fictional-private-marker")\nentry=json.loads(app.state.lesson_logs.getvalue().splitlines()[-1])\nprint(entry["route"],entry["status"])',
        False,
    ),
    "Check the exact field allowlist rather than only one missing password.",
    fixture(
        'import json\nclient.get("/health")\nentry=json.loads(app.state.lesson_logs.getvalue().splitlines()[-1])\nexpected={"timestamp","event","method","route","status","duration_ms","request_id"}\nprint(set(entry)==expected)',
        False,
    ),
    "Prove both what telemetry contains and what it deliberately excludes, using fictional canaries and bounded operation labels.",
    [
        (
            "Why avoid raw query strings in telemetry labels?",
            "They may contain private data and unbounded values",
            "They improve every metric automatically",
            "They are always encrypted at rest",
            "Templates provide useful bounded operation labels.",
        ),
        (
            "Does this app allowlist audit every future proxy/plugin log?",
            "No",
            "Always",
            "Only when INFO",
            "Other logging systems need their own review and tests.",
        ),
    ],
)

lesson(
    5,
    "3. Distinguish liveness from database readiness",
    "Expose a shallow process check and a bounded dependency check with truthful statuses.",
    [
        (
            "Liveness; readiness",
            "Liveness asks whether the app can answer a shallow request. Readiness asks whether a needed dependency is currently usable. A process can be alive while its database is unavailable.",
        ),
        (
            "503 Service Unavailable; bounded dependency probe",
            "The readiness helper executes a small SELECT 1 in its owned Session and returns a generic 503 on expected SQLAlchemy failure. It does not expose a connection string or perform an external internet request.",
        ),
    ],
    "Keep liveness cheap so it does not confuse every dependency outage with a dead process. "
    "Readiness may check a necessary dependency, but should not run a full migration or make expensive writes on every probe. "
    "The project keeps /health as the compatible {status:ok} route and adds /health/ready. "
    "Tests exercise both the real temporary database and a patched unavailable result. "
    "A 200 readiness result is a narrow observation at that instant, not proof every query, user permission or recovery path works.",
    "GET /health -> 200\nGET /health/ready -> 200 ready or 503 unavailable",
    fixture(
        'print(client.get("/health").status_code,client.get("/health/ready").status_code)\nprint(client.get("/health/ready").json())',
        False,
    ),
    "Both checks succeed against the owned working fixture, with a deliberately small generic readiness representation.",
    (
        "# Run schema upgrades or a huge report on every health request",
        "Use a shallow live check and a bounded necessary-dependency probe",
        "Probes should be predictable and should not mutate real installation state.",
    ),
    "Patch readiness unavailable while confirming the app remains live.",
    checks(
        'from lesson_support import practice\ndef test_alive_not_ready(monkeypatch):\n    with practice(seed=False) as (app,c,h):\n        monkeypatch.setattr("orm_api.database_ready",lambda sessions:False)\n        assert c.get("/health").status_code==200\n        assert c.get("/health/ready").status_code==503'
    ),
    "Verify readiness creates no accounts or notes.",
    fixture(
        'from sqlalchemy import select,func\nfrom orm_api.models import User,Note\nclient.get("/health/ready")\nwith app.state.sessions() as s:print(s.scalar(select(func.count()).select_from(User)),s.scalar(select(func.count()).select_from(Note)))',
        False,
    ),
    "Make health probes cheap, non-destructive and honest about the narrow condition each one observes.",
    [
        (
            "Can a process be live but not ready?",
            "Yes",
            "Never",
            "Only without a database",
            "Its request loop may work while a dependency fails.",
        ),
        (
            "Should health checks apply migrations on each request?",
            "No",
            "Always",
            "Only on GET",
            "Probes must not become hidden schema-management operations.",
        ),
    ],
)

lesson(
    5,
    "4. Return safe errors and preserve diagnostic correlation",
    "Handle an unexpected failure without returning its private exception message.",
    [
        (
            "Generic 500 boundary",
            "Before response headers are sent, the middleware converts an unexpected error into Internal server error plus request_id. It records safe status/timing rather than raw exception text.",
        ),
        (
            "Error tracking scope",
            "Correlation ids and counts are local diagnostic primitives, not a complete SaaS error tracker, alerting system or stored incident history. No external error report is sent by this project.",
        ),
    ],
    "A client should know its operation failed, but does not need internal SQL, filesystem paths, credentials or a traceback. "
    "Use a generated id to correlate the generic response with a safe application log record. "
    "The controlled test replaces the request Session provider with a failure carrying a fictional private marker, then asserts that marker is absent from both response and logs. "
    "Once headers have already been sent, an application cannot safely replace a streamed response with a new 500 body; that boundary is deliberately not claimed as universally recoverable. "
    "Operational error investigation still needs a reviewed local process; this project does not silently export user data to an external tracker.",
    '# Safe public error: {detail:"Internal server error",request_id:generated_id}',
    fixture(
        'from orm_api import get_session\ndef broken():raise RuntimeError("fictional-private-error-canary")\napp.dependency_overrides[get_session]=broken\ntry:\n    r=client.get("/v1/notes",headers=headers)\n    print(r.status_code,r.json()["detail"])\n    print(r.json()["request_id"]==r.headers["X-Request-ID"])\n    print("fictional-private-error-canary" not in r.text+app.state.lesson_logs.getvalue())\nfinally:app.dependency_overrides.clear()'
    ),
    "The injected failure reaches the actual safe-error middleware; the response/log correlation remains useful without publishing the canary.",
    (
        'return {"error":str(exception),"traceback":traceback_text}',
        "Return a generic failure and safe correlation id",
        "Raw exceptions can carry internal or sensitive data.",
    ),
    "Check that a restored dependency resumes normal access after the injected failure.",
    fixture(
        'from orm_api import get_session\ndef broken():raise RuntimeError("controlled")\napp.dependency_overrides[get_session]=broken\ntry:assert client.get("/v1/notes",headers=headers).status_code==500\nfinally:app.dependency_overrides.clear()\nprint(client.get("/v1/notes",headers=headers).status_code)'
    ),
    "Verify the protected metrics register one controlled server error.",
    fixture(
        'from orm_api import get_session\ndef broken():raise RuntimeError("controlled")\napp.dependency_overrides[get_session]=broken\ntry:client.get("/v1/notes",headers=headers)\nfinally:app.dependency_overrides.clear()\nprint(client.get("/internal/metrics",headers=headers).json()["server_errors"])'
    ),
    "Report failure truthfully, keep private exception content out of public output and retain a safe correlation path.",
    [
        (
            "Should clients receive raw internal exception text?",
            "No",
            "Always",
            "Only after login",
            "It can leak sensitive implementation/request details.",
        ),
        (
            "Does this local example send data to an external error tracker?",
            "No",
            "Always",
            "Only for 500",
            "It provides local safe records/counts, not an external reporting service.",
        ),
    ],
)

lesson(
    5,
    "5. Read bounded metrics and their operational limits",
    "Use local request/error counts without pretending they are durable monitoring.",
    [
        (
            "Counter; process-local metric",
            "The project keeps bounded operation/status counts in memory with a lock. A snapshot reports total requests and server errors; restart resets these counts.",
        ),
        (
            "Protected metrics; alerting distinction",
            "/internal/metrics requires a valid bearer. Counts do not automatically implement dashboards, alerts, retention or multi-process aggregation.",
        ),
    ],
    "A log gives individual request facts; a metric summarises a stream of events. They answer related but different operational questions. "
    "The example records one health call and verifies the request total increased by one. "
    "The current metrics request itself is recorded after its snapshot is constructed, so do not expect it to include its own completed record yet. "
    "The local counter is bounded by registered route templates/method/status combinations, not arbitrary query values. "
    "For multiple workers or durable monitoring, a separate reviewed collector/aggregation and retention strategy would be needed.",
    'before=telemetry.snapshot()["requests"]\nclient.get("/health")\nafter=telemetry.snapshot()["requests"]',
    fixture(
        'before=app.state.telemetry.snapshot()["requests"]\nclient.get("/health")\nafter=app.state.telemetry.snapshot()["requests"]\nprint("New completed requests:",after-before)\nprint(sorted(client.get("/internal/metrics",headers=headers).json()))'
    ),
    "The delta is one completed request. The snapshot exposes only aggregate counts, not user identities or credentials.",
    (
        "# One in-memory counter is a durable multi-worker monitoring platform",
        "Describe process-local reset and aggregation limits",
        "Monitoring claims must match the actual storage/lifetime design.",
    ),
    "Verify metrics require authentication.",
    fixture(
        'print(client.get("/internal/metrics").status_code,client.get("/internal/metrics",headers=headers).status_code)'
    ),
    "Check a fresh app has zero server errors after a successful health request.",
    fixture(
        'client.get("/health")\nprint(app.state.telemetry.snapshot()["server_errors"])',
        False,
    ),
    "Use bounded protected counts as local evidence, and keep restart, aggregation, alerting and retention limits explicit.",
    [
        (
            "Do these metrics survive a process restart?",
            "No",
            "Always",
            "Only after login",
            "They are process-local in-memory counters.",
        ),
        (
            "Do counts alone create an alerting/retention system?",
            "No",
            "Always",
            "Only on GitHub",
            "Collection, thresholds, notification and storage need separate design.",
        ),
    ],
)

lesson(
    5,
    "6. Milestone: a tested and observable Notes API",
    "Run the full quality workflow and explain the evidence behind this operational foundation.",
    [
        (
            "Complete Week 41 milestone",
            "The supplied API retains private CRUD/auth/tags and migrations, then adds an isolated pytest suite, mock-transport failures, lint/format gates, a Python-version CI matrix, validated settings and safe JSON request telemetry.",
        ),
        (
            "Readiness evidence, not a blanket deployment claim",
            "This is a loopback learning server. Tests/CI/config/logs are useful foundations, but public deployment, HTTPS, rate limiting, account recovery, secret rotation, durable monitoring and restore drills remain separate work.",
        ),
    ],
    "Keep the complete docs/python-week41 folder, install requirements-dev.txt and run the same test/lint/format commands as CI. "
    "Run python app.py and open http://127.0.0.1:8002/docs for the original local explorer. Use fictional accounts only. "
    "Inspect liveness/readiness, make an authorised request and observe its safe JSON log plus request id without printing a bearer credential. "
    "Read the exact-commit CI result for both Python versions; a workflow file or old green run alone is insufficient evidence. "
    "Use configuration mappings and temporary files in examples so neither the learner’s real environment nor existing runtime data is needed. "
    "Explain which boundary each test verifies and which operational capabilities remain unimplemented. That honest evidence is the milestone, and Week 42’s roadmap builds on it with containers/deployment.",
    "python -m pytest -q -p pytest_cov --cov=orm_api --cov-fail-under=75\npython -m ruff check .\npython -m ruff format --check .\npython app.py",
    fixture(
        'register(client,"asha");headers=login(client,"asha")\nr=client.post("/v1/notes",headers=headers,json={"title":"Week 41 evidence","body":"Tested boundaries and safe telemetry"})\nurl=r.headers["Location"]\nassert r.status_code==201\nassert client.put(url+"/tags",headers=headers,json={"names":["api"]}).json()==["api"]\nprint("Create/read:",r.status_code,client.get(url,headers=headers).status_code)\nprint("Live/ready:",client.get("/health").status_code,client.get("/health/ready").status_code)\nprint("Metrics protected:",client.get("/internal/metrics").status_code)\nprint("Delete/logout:",client.delete(url,headers=headers).status_code,client.post("/v1/logout",headers=headers).status_code)\nprint("Replay:",client.get("/v1/me",headers=headers).status_code)',
        False,
    ),
    "The milestone exercises real app components and operational endpoints against a temporary instance. It does not touch Study Hub learning storage or a public identity service.",
    (
        "# Commit private runtime files and call a green badge production proof",
        "Publish source/tests and report the exact evidence plus limits",
        "Runtime secrets/data and unverified operational claims do not belong in a public learning release.",
    ),
    "Verify the workflow handout and project expose the three required gate commands.",
    'from orm_api.database import PROJECT\ns=(PROJECT/"quality-workflow.yml").read_text(encoding="utf-8")\nprint(all(command in s for command in ["python -m pytest","python -m ruff check","python -m ruff format --check"]))',
    "Run one final real local pytest contract check without external networking.",
    checks(
        'from lesson_support import practice\ndef test_final_health_contract():\n    with practice(seed=False) as (app,c,h):\n        assert c.get("/health").json()=={"status":"ok"}\n        assert c.get("/health/ready").status_code==200\n        assert c.get("/internal/metrics").status_code==401'
    ),
    "A reliable operational foundation connects meaningful tests, reproducible CI, private configuration and safe observable behaviour with accurately stated limits.",
    [
        (
            "Does coverage prove every assertion is correct?",
            "No",
            "Always",
            "Only at 100 percent",
            "Execution evidence and expected-result quality differ.",
        ),
        (
            "Should integration tests use real learner databases?",
            "No",
            "Always",
            "Only in CI",
            "Owned temporary files provide real-component evidence safely.",
        ),
        (
            "Where should an imported dependency be patched?",
            "Where the code under test looks it up",
            "Any unrelated source module",
            "In a browser bookmark",
            "Patch the actual consuming namespace.",
        ),
        (
            "Does MockTransport require live internet?",
            "No",
            "Always",
            "Only for timeouts",
            "A supplied handler replaces the network boundary.",
        ),
        (
            "Is TestClient browser E2E evidence?",
            "No",
            "Always",
            "Only with HTML",
            "It does not execute browser interaction/rendering.",
        ),
        (
            "Which CI result verifies an edit?",
            "All required jobs for the exact commit",
            "Any previous green run",
            "Only a workflow filename",
            "The evidence must match the delivered code.",
        ),
        (
            "Does a public JS file hide a real secret?",
            "No",
            "Always",
            "If renamed",
            "Publicly served source can be inspected.",
        ),
        (
            "What happens to invalid configuration?",
            "It is rejected before resource startup",
            "It resets the database",
            "It is silently logged with secrets",
            "Fail-fast validation keeps the contract explicit.",
        ),
        (
            "Can an app be live but not ready?",
            "Yes",
            "Never",
            "Only without SQL",
            "A needed dependency can be unavailable while the process answers.",
        ),
        (
            "What belongs in request telemetry?",
            "Safe allowlisted operational fields",
            "Every header/body/query",
            "Passwords for troubleshooting",
            "Collect only the needed non-secret facts.",
        ),
        (
            "Are these counters durable across workers/restarts?",
            "No",
            "Always",
            "Only with INFO logs",
            "They are a deliberately limited process-local learning implementation.",
        ),
        (
            "Does this addition change Study Hub progress storage?",
            "No",
            "Always",
            "Only for CI",
            "It adds teaching data and a separate local Python project.",
        ),
    ],
)
