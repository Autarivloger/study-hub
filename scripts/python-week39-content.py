"""Original Week39 teaching material; loaded by the small authoring generator."""

def basic(routes, calls):
    # Introduce imports only when the current example actually uses the name.
    import re
    names=set(re.findall(r'\b[A-Za-z_]\w*\b',routes+'\n'+calls))
    imports='from typing import Annotated\n' if 'Annotated' in names else ''
    imports+='from fastapi import '+', '.join(['FastAPI']+[n for n in ['Path','Query','HTTPException','Response','Depends'] if n in names])+'\n'
    imports+='from fastapi.testclient import TestClient\n'
    models=[n for n in ['BaseModel','Field','ConfigDict','field_validator','model_validator','ValidationError'] if n in names]
    if models:imports+='from pydantic import '+', '.join(models)+'\n'
    return imports+'app = FastAPI()\n'+clean(routes)+'\nwith TestClient(app) as client:\n'+textwrap.indent(clean(calls),'    ')


def fixture(body, seed=True):
    return ('from lesson_support import practice, register, login, PRACTICE_PASSWORD\n'
            'with practice(seed=' + str(seed) + ') as (app, client, headers):\n' + textwrap.indent(clean(body), '    '))


lesson(0, '1. Trace your first FastAPI request',
 'Connect a URL, an HTTP method, a Python function and its JSON response.',
 [('FastAPI; ASGI; Uvicorn', 'FastAPI is a Python API framework. ASGI is the interface between an async-capable server and an application. Uvicorn is a server that runs that interface.'),
  ('@app.get; path operation', 'This decorator registers a function for a method/path pair. The path operation is the handler, not a function that your browser directly imports.'),
  ('TestClient; context manager', 'TestClient sends simulated HTTP requests to the app in-process. Entering it with with also runs application startup/shutdown. It does not need an open network port.')],
 'Week 36 introduced HTTP requests and Week 37 used Flask. The same request/response reasoning applies here. '
 'A client sends GET /hello; FastAPI matches the route, calls hello, and serialises the returned dictionary as JSON. '
 'You still write ordinary Python functions. FastAPI adds routing, input processing, schema generation and response handling around them. '
 'The introductory examples repeat complete imports so you can run them independently after installing the supplied requirements. '
 'Read the method, URL, status and body separately; a working Python function alone does not prove the HTTP contract.',
 '@app.get("/hello")\ndef hello():\n    return {"message": "Hello"}',
 basic('@app.get("/hello")\ndef hello():\n    return {"message": "Namaste"}',
       'r = client.get("/hello")\nprint(r.status_code, r.json())\nprint(r.headers["content-type"])'),
 'The request reaches the registered handler, returns 200 and supplies application/json. .json() decodes the response body into Python values; it is not the function return object itself.',
 ('hello()  # assume this checks routing and HTTP', 'client.get("/hello")', 'A direct call skips HTTP method matching, validation, response status and serialisation.'),
 'Add GET /ready returning a ready Boolean and inspect its status and JSON.',
 basic('@app.get("/ready")\ndef ready():\n    return {"ready": True}', 'r=client.get("/ready")\nprint(r.status_code, r.json())'),
 'Request an unregistered URL and show the framework response.',
 basic('@app.get("/ready")\ndef ready():\n    return {"ready": True}', 'r=client.get("/missing")\nprint(r.status_code, r.json())'),
 'A route is a method/path contract that turns a request into an HTTP response.',
 [('What matches a path operation?', 'An HTTP method and path', 'A Python filename alone', 'A CSS selector', 'The router uses the HTTP method and URL path.'),
  ('Does TestClient require starting Uvicorn?', 'No', 'Always', 'Only for GET', 'It invokes the ASGI app in-process.')])

lesson(0, '2. JSON values and response boundaries',
 'Distinguish Python values from JSON text and an HTTP response.',
 [('JSON serialisation; Response.json()', 'Serialisation converts Python data into wire-format JSON; a client decodes that JSON. JSON true/null correspond to Python True/None, but JSON text is not Python source.'),
  ('Response status and headers', 'The status describes the HTTP result; headers describe metadata. The JSON body carries application data. Check all three at the appropriate boundary.')],
 'Return a dictionary or list rather than manually building JSON with string interpolation. The framework handles quoting and content type. '
 'Python None becomes JSON null and a Python Boolean becomes JSON true/false. Keep this conversion separate from your data model. '
 'Do not return a password hash, key or internal owner record just because it is easy to serialise. Later response models explicitly filter public fields. '
 'An HTTP error can still contain valid JSON. Parsing its body is not evidence that the operation succeeded. '
 'The sample prints decoded values and status rather than relying on whitespace in a raw JSON string.',
 'response = client.get("/summary")\nprint(response.status_code, response.json())',
 basic('@app.get("/summary")\ndef summary():\n    return {"done": False, "next": None, "topics": ["HTTP", "JSON"]}',
       'r=client.get("/summary")\nprint(r.status_code)\nprint(r.json())\nprint(type(r.json()["done"]).__name__)'),
 'Decoded done is a Python bool again. Its wire representation was JSON false. The body is structured data, not executable browser markup.',
 ('return "{title: " + title + "}"', 'return {"title": title}', 'Manual concatenation breaks JSON quoting and mixes data with format syntax.'),
 'Return a title containing a quotation mark and verify that decoding preserves it.',
 basic('@app.get("/title")\ndef title():\n    return {"title": \'Read "HTTP"\'}', 'print(client.get("/title").json()["title"])'),
 'Return an empty list and an empty result marker without turning them into strings.',
 basic('@app.get("/empty")\ndef empty():\n    return {"items": [], "next": None}', 'r=client.get("/empty");print(r.json()["items"], r.json()["next"] is None)'),
 'Treat status, headers and typed JSON as separate parts of the response contract.',
 [('Does response.json() prove success?', 'No; inspect status too', 'Always', 'Only if it is a dictionary', 'Error responses can contain valid JSON.'),
  ('What should a handler return for structured JSON?', 'A Python dictionary or list', 'Concatenated user text', 'eval of the request', 'The framework serialises structured data safely.')])

lesson(0, '3. def, async def and cooperative waiting',
 'Choose the correct handler style without assuming async makes blocking work faster.',
 [('async def; await; coroutine', 'async def defines a coroutine function. await suspends its coroutine while an awaitable operation completes, allowing other work on that event loop.'),
  ('Event loop; blocking I/O; thread pool', 'Blocking code occupies its thread until done. FastAPI runs normal def handlers/dependencies in a thread pool; async def handlers execute on the event loop and must avoid blocking it.'),
  ('asyncio.sleep', 'An awaitable delay used here to demonstrate yielding without networking. It is not a database driver or a speed optimisation.')],
 'The final SQLite driver and password hashing are synchronous operations, so their routes use def. '
 'Use async def when the actual library operation offers an awaitable interface; writing async before blocking sqlite3 or time.sleep does not change those libraries. '
 'A coroutine must be awaited to obtain its result. Do not return an unawaited coroutine as if it were a JSON value. '
 'CPU-heavy work remains CPU-heavy; async waiting does not provide unlimited parallel CPU execution. '
 'This tiny delay demonstrates scheduling semantics only. It makes no performance benchmark claim.',
 'async def handler():\n    await an_async_operation()\n    return {"ready": True}',
 basic('import asyncio\n@app.get("/async-ready")\nasync def ready():\n    await asyncio.sleep(0)\n    return {"ready": True}',
       'print(client.get("/async-ready").json())'),
 'The awaited delay yields control, then the handler returns ordinary JSON data. TestClient still presents a synchronous testing interface.',
 ('async def route():\n    time.sleep(2)', 'def route():\n    time.sleep(2)  # blocking example belongs off the event loop', 'Changing the function declaration cannot make a blocking operation awaitable.'),
 'Create a normal def handler performing a small synchronous calculation.',
 basic('@app.get("/total")\ndef total():\n    return {"total": sum([10, 20, 30])}', 'print(client.get("/total").json())'),
 'Await a small helper coroutine and return its result.',
 basic('async def label():\n    return "ready"\n@app.get("/label")\nasync def read_label():\n    return {"label": await label()}', 'print(client.get("/label").json())'),
 'Match handler style to the real I/O library; do not block the event loop or confuse concurrency with CPU speed.',
 [('Does async def make sqlite3 calls nonblocking?', 'No', 'Always', 'If the function has one parameter', 'The underlying driver remains synchronous.'),
  ('What does await do while an awaitable waits?', 'Allows cooperative progress on the event loop', 'Creates a new database table', 'Encrypts the response', 'Await suspends the current coroutine at an awaitable boundary.')])

lesson(0, '4. Lifespan owns startup and shutdown',
 'Initialise shared configuration deliberately and clean up at a known boundary.',
 [('lifespan; asynccontextmanager', 'FastAPI accepts an async context manager for startup/shutdown. Code before yield starts resources; code after yield releases them.'),
  ('app.state; Request', 'app.state holds app-owned runtime state. A Request parameter provides the current request and its app. State is not browser localStorage and not a current-user identity.')],
 'Importing a module should not launch a server or open a learner database. A factory constructs the app; lifespan starts its owned resources. '
 'Store shared immutable configuration on app.state and give request-specific resources their own dependency lifetime. '
 'TestClient must be used as a context manager when your assertions depend on startup. Constructing it alone does not enter lifespan. '
 'The counter below demonstrates order without files or clocks. The actual project initialises its ignored database/key at the same boundary. '
 'Always name who owns a resource and when it is released instead of hiding setup in an unrelated route.',
 '@asynccontextmanager\nasync def lifespan(app):\n    # startup\n    yield\n    # shutdown',
 '''from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.testclient import TestClient
events=[]
@asynccontextmanager
async def lifespan(app):
    events.append("start")
    yield
    events.append("stop")
app=FastAPI(lifespan=lifespan)
with TestClient(app) as client:
    print(events)
print(events)''',
 'The first print occurs inside the started app; the second occurs after shutdown. No resource is created by merely declaring the context-manager function.',
 ('client=TestClient(app)  # assume startup ran', 'with TestClient(app) as client:\n    # startup is active here', 'Entering the context drives lifespan.'),
 'Store an app-owned label during startup and read it through Request.',
 '''from contextlib import asynccontextmanager
from fastapi import FastAPI,Request
from fastapi.testclient import TestClient
@asynccontextmanager
async def lifespan(app):
    app.state.label="local"
    yield
app=FastAPI(lifespan=lifespan)
@app.get("/label")
def label(request:Request):
    return {"label":request.app.state.label}
with TestClient(app) as client:
    print(client.get("/label").json())''',
 'Show that creating an app does not enter its lifespan.',
 '''from contextlib import asynccontextmanager
from fastapi import FastAPI
events=[]
@asynccontextmanager
async def lifespan(app):
    events.append("started")
    yield
app=FastAPI(lifespan=lifespan)
print("Startup ran:",bool(events))''',
 'Construct the application separately from starting its resources, and test both lifetime boundaries.',
 [('When does code after lifespan yield run?', 'During shutdown', 'At import time', 'Before startup', 'The context exits after application use.'),
  ('Is app.state a verified current user?', 'No', 'Always', 'Only for GET', 'Application runtime state does not authenticate a request.')])

lesson(0, '5. Automatic OpenAPI and genuinely local documentation',
 'Read the generated API contract and understand the offline explorer.',
 [('OpenAPI; operationId; schema', 'OpenAPI is a machine-readable description of paths, parameters, bodies and responses. FastAPI generates it from declared route/model metadata.'),
  ('Swagger UI; CDN; local explorer', 'Default interactive Swagger UI normally loads assets from a CDN. The supplied project disables that page and serves an original local explorer built from /openapi.json, with local CSS/JS.')],
 'Documentation should describe the implemented contract, not a disconnected handwritten list. Type hints and models contribute to FastAPI’s generated schema. '
 'A schema documents expected shapes and constraints; request tests still need to prove actual behaviour and ownership. '
 'Fetching /openapi.json through TestClient does not require the internet. Default /docs HTML may reference external assets, so that default page alone is not an offline guarantee. '
 'Our final /docs reads the local generated schema and renders request controls. It is an original learning tool, not a copy of Swagger UI. '
 'Optional external reference links are further reading; explanations, source and project documentation are included locally.',
 'schema = client.get("/openapi.json").json()\noperation = schema["paths"]["/hello"]["get"]',
 basic('@app.get("/hello", tags=["basics"])\ndef hello():\n    return {"message":"Hello"}',
       'schema=client.get("/openapi.json").json()\noperation=schema["paths"]["/hello"]["get"]\nprint("Version:",schema["openapi"])\nprint("Tags:",operation["tags"])\nprint("Success documented:","200" in operation["responses"])'),
 'The handler declaration contributes a GET operation and a successful response entry. The OpenAPI version is a contract format version, not your Python version.',
 ('# Default docs HTML loaded, therefore every asset is offline', '# Verify /docs, /openapi.json and every referenced asset are local', 'A remotely loaded JavaScript bundle would still require network access.'),
 'Inspect the final project’s generated note-create success response.',
 fixture('schema=client.get("/openapi.json").json()\nprint("201" in schema["paths"]["/v1/notes"]["post"]["responses"])',False),
 'Verify the original explorer and its local assets are available.',
 fixture('print([client.get(path).status_code for path in ["/docs","/assets/style.css","/assets/explorer.js"]])',False),
 'Generated contracts and locally served assets make API exploration consistent and usable offline after installation.',
 [('Does an OpenAPI schema prove owner isolation?', 'No; test requests and stored state', 'Always', 'If tagged notes', 'Metadata describes a contract; enforcement must be verified.'),
  ('Why replace the default documentation page here?', 'To serve all interactive documentation assets locally', 'To remove validation', 'To hide every endpoint', 'Default UI assets commonly come from an external CDN.')])

lesson(0, '6. Separate a test client from a running server',
 'Run the local project and distinguish source hosting from Python execution.',
 [('Loopback; port; Uvicorn run', '127.0.0.1 addresses this computer. A port selects a listening service. uvicorn.run starts an ASGI server; the supplied app.py uses port 8000 and disables access logs.'),
  ('Application factory; import guard', 'create_app constructs an independent app. if __name__ == "__main__" prevents importing app.py from automatically starting its server.')],
 'Save the complete docs/python-week39 folder, install requirements in your practice environment and run python app.py from that folder. '
 'Open http://127.0.0.1:8000/docs on the same computer. Keep the terminal running; Ctrl+C stops the server. '
 'GitHub Pages can publish these lessons and Python source files but cannot execute the Python backend. No Study Hub password or learning database is used. '
 'The following example uses the same app factory through a disposable TestClient rather than starting a long-running server inside a lesson. '
 'Use fictional accounts while learning. Public deployment would require operational controls beyond this local project.',
 'python -m pip install -r requirements.txt\npython app.py\n# Open http://127.0.0.1:8000/docs',
 fixture('print(client.get("/health").status_code,client.get("/health").json())\nprint(client.get("/v1/me").status_code)',False),
 'Health is public; identity is protected. Seeing 401 on /v1/me before login is expected behaviour rather than a server failure.',
 ('# Upload app.py to GitHub Pages and expect it to execute', '# Read the hosted lesson; run the Python API locally', 'Static file hosting and a running application server are different services.'),
 'Inspect the original documentation title from a fresh project app.',
 fixture('text=client.get("/docs").text\nprint("Local Notes API" in text, "/assets/explorer.js" in text)',False),
 'Verify a fresh private database has no accounts before registration.',
 fixture('from learning_api.database import connect\ndb=connect(app.state.database)\ntry:print("Accounts:",db.execute("SELECT count(*) FROM users").fetchone()[0])\nfinally:db.close()',False),
 'Run a local Python server deliberately; publishing its source does not turn static hosting into a backend.',
 [('What does 127.0.0.1 refer to here?', 'The computer running the server', 'Any phone on the internet', 'GitHub Pages', 'Loopback is local to the machine using it.'),
  ('Why use an app factory in examples?', 'To construct independent disposable apps', 'To store tokens in HTML', 'To bypass validation', 'Each test can own a separate database/key lifetime.')])

lesson(1, '1. A path parameter identifies the resource',
 'Parse an integer path value and distinguish a bad identifier from an absent record.',
 [('Path parameter; int conversion', 'A placeholder such as {note_id} captures a URL segment. The int annotation asks FastAPI to parse and validate it before calling the handler.'),
  ('HTTPException; raise', 'raise HTTPException(status_code, detail) stops normal handler processing and asks FastAPI to return that deliberate HTTP failure. It is different from an accidental server traceback.'),
  ('422 versus 404', '422 means this request fails the declared input contract. 404 means an acceptable identifier does not reveal an accessible matching resource.')],
 'URL path segments arrive as text. FastAPI processes a typed parameter into a Python int before your handler uses it. '
 'The int annotation alone accepts zero and negative integers; add a constraint when your identifiers must be positive. '
 'A syntactically valid number is not proof a row exists. The route must still query its data and return 404 when appropriate. '
 'Do not use int conversion exceptions as a reason to return 500. Framework input processing should produce a structured client error. '
 'This first example uses a tiny in-memory lookup; persistent, owner-filtered lookup arrives on Day 5.',
 '@app.get("/items/{item_id}")\ndef read(item_id:int):\n    ...',
 basic('items={1:"HTTP"}\n@app.get("/items/{item_id}")\ndef read(item_id:int):\n    if item_id not in items:raise HTTPException(404,"Item not found")\n    return {"id":item_id,"title":items[item_id]}',
       'for value in ["1","abc","99"]:\n    r=client.get("/items/"+value)\n    print(value,r.status_code)'),
 '1 is parsed and found; abc cannot be an integer; 99 parses but has no record. These are three distinct outcomes.',
 ('if item_id: return all_items  # no lookup', 'row = lookup(item_id)\nif row is None: raise HTTPException(404,"Not found")', 'A valid type does not establish existence or access.'),
 'Return a typed path id and prove it arrives as int.',
 basic('@app.get("/items/{item_id}")\ndef read(item_id:int):\n    return {"type":type(item_id).__name__,"id":item_id}', 'print(client.get("/items/7").json())'),
 'Show that int alone permits a negative number.',
 basic('@app.get("/items/{item_id}")\ndef read(item_id:int):\n    return {"id":item_id}', 'print(client.get("/items/-1").status_code)'),
 'Parse the path first, then apply domain constraints, existence and ownership checks.',
 [('What happens to /items/abc with item_id:int?', 'Input validation fails', 'It becomes zero', 'The route receives any text', 'abc cannot be parsed as an integer.'),
  ('Does int alone require a positive identifier?', 'No', 'Always', 'Only on Windows', 'Positivity needs an explicit constraint.')])

lesson(1, '2. Annotated and positive identifier constraints',
 'Keep the Python type and HTTP validation metadata together.',
 [('typing.Annotated; Path(gt=0)', 'Annotated[int, Path(gt=0)] attaches FastAPI metadata to an int type. gt means strictly greater than; the handler receives an int only after the constraint passes.'),
  ('Constraint boundary', 'A boundary test checks values just below, on and above a rule, such as -1, 0 and 1. This is more useful than testing only a large valid id.')],
 'Type information answers what kind of value a handler receives; constraints describe which values are allowed for this interface. '
 'Annotated lets you express both without treating metadata as the actual integer value. '
 'Path parameters cannot be omitted because their segment is part of matching the URL. A missing route segment may produce a routing 404 rather than a parameter 422. '
 'Do not describe every rejected URL as the same kind of validation problem. Identify which layer rejected it. '
 'The final project reuses a NoteId alias to avoid duplicating the positive-id rule across read, update and delete.',
 'NoteId = Annotated[int, Path(gt=0)]',
 basic('@app.get("/items/{item_id}")\ndef read(item_id:Annotated[int,Path(gt=0)]):\n    return {"id":item_id}',
       'for value in [-1,0,1]:\n    print(value,client.get(f"/items/{value}").status_code)'),
 'Zero is rejected as well as negative numbers. The constraint applies before entering the handler.',
 ('item_id:int  # assume positive', 'item_id:Annotated[int,Path(gt=0)]', 'The annotation int includes zero and negative integers.'),
 'Use ge=1 as an equivalent constraint for integer ids.',
 basic('@app.get("/items/{item_id}")\ndef read(item_id:Annotated[int,Path(ge=1)]):\n    return {"id":item_id}', 'print(client.get("/items/0").status_code,client.get("/items/1").status_code)'),
 'Compare a missing URL segment with an invalid existing segment.',
 basic('@app.get("/items/{item_id}")\ndef read(item_id:Annotated[int,Path(gt=0)]):\n    return {"id":item_id}', 'print(client.get("/items").status_code,client.get("/items/nope").status_code)'),
 'Use explicit boundary rules and test the layer where a request fails.',
 [('What does gt=0 mean?', 'Strictly greater than zero', 'Greater than or equal to zero', 'Convert to text', 'Zero does not satisfy a strict greater-than rule.'),
  ('Does Annotated replace int with a database row?', 'No', 'Always', 'Only on GET', 'It carries metadata alongside the underlying type.')])

lesson(1, '3. Query parameters, defaults and bounded pagination',
 'Give optional query controls safe limits without confusing them with the resource id.',
 [('Query; ge; le; default', 'Query metadata controls URL query input. ge/le are inclusive lower/upper bounds. A default is used only when a value is omitted, not when an invalid value is sent.'),
  ('limit; offset', 'limit caps returned items and offset skips a count of ordered items. They need a deterministic ordering and explicit upper limits.')],
 'A path typically selects the resource or collection; query parameters filter or page that selection. '
 'URLs carry query values as text, so FastAPI parses limit=2 into an int. Body strictness later does not mean every URL value must arrive as a JSON integer. '
 'A default of 10 does not repair limit=0 or limit=abc. Invalid supplied values should be rejected. '
 'Bound both limit and offset so the API contract does not invite unbounded response sizes or arbitrary deep offset work. '
 'The final database route applies owner filtering before counting and paging, so totals do not reveal other users’ rows.',
 'limit:Annotated[int,Query(ge=1,le=50)]=10',
 basic('@app.get("/items")\ndef listing(limit:Annotated[int,Query(ge=1,le=50)]=10,offset:Annotated[int,Query(ge=0,le=10000)]=0):\n    return {"limit":limit,"offset":offset}',
       'print(client.get("/items").json())\nprint(client.get("/items?limit=2&offset=3").json())\nprint(client.get("/items?limit=0").status_code)'),
 'Omission receives defaults, valid supplied controls are parsed, and zero violates the contract instead of falling back silently.',
 ('limit = supplied or 10', 'limit:Annotated[int,Query(ge=1,le=50)]=10', 'A truthiness fallback hides invalid zero and omits clear schema metadata.'),
 'Reject a too-large page size and a negative offset.',
 fixture('print(client.get("/v1/notes?limit=51",headers=headers).status_code)\nprint(client.get("/v1/notes?offset=-1",headers=headers).status_code)'),
 'Fetch the second one-item page and show the owner-filtered total.',
 fixture('page=client.get("/v1/notes?limit=1&offset=1",headers=headers).json()\nprint(page["total"],page["items"][0]["title"])'),
 'Defaults support omission; validation handles supplied bad values, and pagination needs deterministic ordering.',
 [('Does a default replace an explicitly invalid value?', 'No', 'Always', 'Only if zero', 'A supplied value must satisfy its declared contract.'),
  ('What must pagination use for repeatable ordering?', 'An explicit stable order', 'Natural file order', 'Random ids each request', 'Without ORDER BY the database does not promise a stable page sequence.')])

lesson(1, '4. Optional text, repeated query values and fixed routes',
 'Distinguish missing values, empty strings, lists and route precedence.',
 [('str | None; empty versus omitted', 'The union permits either text or None. A missing optional query value can become None; ?q= is supplied empty text, which is a distinct value.'),
  ('list[str] with Query; route order', 'Query can collect repeated query keys into a list. Register a fixed route such as /items/latest before a dynamic /items/{item_id} route that could also match it.')],
 'Choose deliberately whether empty text means no filter or an invalid value. Do not accidentally conflate None with an empty string using truthiness. '
 'Repeated tag=python&tag=http parameters can represent a list when declared as query metadata. '
 'A dynamic route can capture words intended for a later fixed route. FastAPI checks routes in declaration order, so put the specific fixed path first. '
 'Type conversion happens after route selection; a fixed word captured by an int route can produce 422 rather than finding the later fixed handler. '
 'Our final notes search treats omitted/empty q as no text filter and bounds q at 80 characters.',
 'q:Annotated[str|None,Query(max_length=80)]=None\ntags:Annotated[list[str]|None,Query()]=None',
 basic('@app.get("/filters")\ndef filters(q:Annotated[str|None,Query(max_length=80)]=None,tags:Annotated[list[str]|None,Query()]=None):\n    return {"q":q,"tags":tags or []}',
       'print(client.get("/filters").json())\nprint(client.get("/filters?q=&tags=python&tags=http").json())'),
 'The first q is None; the second is an explicitly supplied empty string. Repeated tags are collected in their request order.',
 ('@app.get("/items/{item_id}")  # declared before /items/latest', '@app.get("/items/latest")  # declare specific route first', 'Route selection order can matter before parameter validation.'),
 'Declare a fixed latest route before an integer-id route and verify both.',
 basic('@app.get("/items/latest")\ndef latest():\n    return {"id":9}\n@app.get("/items/{item_id}")\ndef read(item_id:int):\n    return {"id":item_id}', 'print(client.get("/items/latest").json(),client.get("/items/2").json())'),
 'Show that an 81-character search is rejected by the final API.',
 fixture('r=client.get("/v1/notes",params={"q":"x"*81},headers=headers)\nprint(r.status_code)'),
 'Model missing, empty and repeated values intentionally, and put specific routes before overlapping dynamic ones.',
 [('Are omitted q and ?q= necessarily the same?', 'No', 'Always', 'Only on POST', 'One can be None while the other is empty text.'),
  ('Which overlapping route belongs first?', 'The specific fixed route', 'Always the dynamic route', 'Whichever has a shorter function name', 'The router considers route declaration order.')])

lesson(1, '5. Read validation errors without leaking submitted secrets',
 'Locate an invalid field and return useful error structure safely.',
 [('RequestValidationError; loc; type', 'FastAPI raises RequestValidationError for invalid HTTP input. loc describes the location such as query/limit; type identifies the validation category.'),
  ('Exception handler; sanitised error', 'A registered exception handler converts a particular exception into a response. The project returns loc/msg/type and removes raw input/context that could echo a password.')],
 'Input errors should help a client repair the request without dumping its entire body into a response or log. '
 'Default validation details can include the rejected input. That is useful during development but can expose a submitted secret if copied into screenshots or logs. '
 'Our project’s handler retains field location, a generic message and error type. Custom validator messages never interpolate the submitted value. '
 'A 422 contract rejection should have no write side effect. Verify that separately rather than assuming an error response implies nothing was stored. '
 'This is field-level validation; it is not a complete reverse-proxy request-byte limit, rate limiter or account-security system.',
 '@app.exception_handler(RequestValidationError)\nasync def handler(request, exc):\n    # return selected safe fields only',
 fixture('r=client.post("/v1/users",json={"username":"ab","password":"short"})\nerror=r.json()["detail"][0]\nprint(r.status_code,error["loc"])\nprint("Raw input returned:",any("input" in e for e in r.json()["detail"]))',False),
 'The response identifies a body field while omitting raw rejected input. It remains a client-validation response rather than a server traceback.',
 ('return JSONResponse({"detail":exc.errors()})  # might echo secrets', 'return selected loc/msg/type fields without input/context', 'Raw validation inputs can contain password fields.'),
 'Attempt a whitespace-only title and confirm the note count stays unchanged.',
 fixture('before=client.get("/v1/notes",headers=headers).json()["total"]\nr=client.post("/v1/notes",headers=headers,json={"title":"   ","body":"Body"})\nafter=client.get("/v1/notes",headers=headers).json()["total"]\nprint(r.status_code,before==after)'),
 'Identify the query location of an invalid limit in the sanitised response.',
 fixture('r=client.get("/v1/notes?limit=0",headers=headers)\nprint(r.json()["detail"][0]["loc"])'),
 'Return actionable validation structure while keeping submitted secrets and internal tracebacks out of it.',
 [('Which field can echo submitted input in raw validation details?', 'input', 'loc only', 'The status number', 'Raw input can contain a password or other private text.'),
  ('Does a field-length rule implement whole-request byte limiting?', 'No', 'Always', 'Only for JSON', 'It constrains parsed fields, not all transport resource usage.')])

lesson(1, '6. A typed endpoint acceptance matrix',
 'Test valid, boundary, malformed and inaccessible requests as different cases.',
 [('Acceptance matrix; status assertion', 'A small table pairs a request category with its expected status. Assertions make the expected interface executable rather than relying on visual inspection.')],
 'Choose cases from the contract, not random URLs. Include an ordinary success, the exact boundary, one value past it, wrong type and missing resource. '
 'An authenticated valid request may succeed while an unauthenticated request fails before meaningful resource access. Do not rely on a universal ordering between independent input/auth failures. '
 'Test one primary failure at a time when learning why a particular status occurs. '
 'A list endpoint with no matches returns an empty successful collection, while a single missing record returns 404. '
 'The fixture owns its own records and token, so these checks neither read nor alter existing Study Hub activity.',
 'for url, expected in cases:\n    response=client.get(url,headers=headers)\n    assert response.status_code==expected',
 fixture('cases=[("/v1/notes?limit=1",200),("/v1/notes?limit=50",200),("/v1/notes?limit=51",422),("/v1/notes/abc",422),("/v1/notes/999",404)]\nfor url,expected in cases:\n    actual=client.get(url,headers=headers).status_code\n    assert actual==expected\n    print(url,actual)'),
 'Each case isolates a specific contract property. The table tests both accepted boundaries and rejected requests.',
 ('assert response.json()  # any truthy body means correct', 'assert response.status_code == expected', 'A JSON error body can be truthy; assert the stated outcome.'),
 'Check a positive id, zero and a negative id against the actual API.',
 fixture('print([client.get("/v1/notes/"+str(i),headers=headers).status_code for i in [1,0,-1]])'),
 'Contrast an empty filtered collection with a missing single record.',
 fixture('r=client.get("/v1/notes?q=no-match",headers=headers)\nprint(r.status_code,r.json()["items"])\nprint(client.get("/v1/notes/999",headers=headers).status_code)'),
 'Test requests by contract category and verify status plus relevant data, not a merely truthy response.',
 [('What does an empty successful collection usually return here?', '200 with an empty items list', 'Always 404', 'An internal traceback', 'The collection exists even when its filter matches no rows.'),
  ('Which is the best boundary set for limit<=50?', '1, 50 and 51', 'Only 10', 'Only random strings', 'Test an ordinary valid value, the boundary and the first rejected value.')])

lesson(2, '1. A Pydantic model describes the request body',
 'Validate structured JSON before using its fields in application logic.',
 [('BaseModel; model_validate; model_dump', 'Subclass BaseModel to declare typed fields. model_validate validates incoming Python data; model_dump converts a validated model to a dictionary. A model is not a database table.'),
  ('Request body; required field; Field', 'A model-typed handler parameter is read from the JSON body. Fields without defaults are required. Field adds constraints and schema metadata.')],
 'A dictionary can contain arbitrary keys and values. A Pydantic model states which values your operation expects. '
 'FastAPI parses the body, validates it, then passes a model instance to the handler. Read its values with ordinary attributes such as data.title. '
 'Model construction is not persistence, and a valid request does not establish identity or ownership. Those are later layers. '
 'Field limits should match the database’s permitted values; otherwise validation can succeed but storage can fail. '
 'Start with the smallest useful contract, then add constraints when you can explain their purpose.',
 'class NoteInput(BaseModel):\n    title:str\n    completed:bool=False',
 basic('class NoteInput(BaseModel):\n    title:str\n    completed:bool=False\n@app.post("/notes")\ndef create(data:NoteInput):\n    return data.model_dump()',
       'print(client.post("/notes",json={"title":"Read the contract"}).json())\nprint(client.post("/notes",json={}).status_code)'),
 'The omitted completed field receives False. The missing required title fails validation before the handler can create anything.',
 ('data["title"]  # treat a model exactly like a dict', 'data.title  # or data.model_dump()["title"]', 'A Pydantic model exposes attributes and explicit conversion methods.'),
 'Construct NoteCreate directly and dump its validated fields.',
 'from learning_api.schemas import NoteCreate\nmodel=NoteCreate.model_validate({"title":"Models","body":"Contracts first"})\nprint(model.model_dump())',
 'Show that a model instance alone does not create a persistent database.',
 'from learning_api.schemas import NoteCreate\nfrom pathlib import Path\nrow=NoteCreate(title="Draft",body="Still a Python object")\nprint(row.title,Path("instance/notes.sqlite").exists())',
 'A model validates a data shape; a separate application/storage layer decides what to do with that valid data.',
 [('Does a Pydantic model automatically save a database row?', 'No', 'Always', 'If named Note', 'Validation and persistence are separate responsibilities.'),
  ('Which field is required when it has no default?', 'The declared field', 'No fields', 'Only Boolean fields', 'Missing required input produces a validation error.')])

lesson(2, '2. Strict JSON and forbidden extra fields',
 'Reject surprising coercion and prevent clients assigning internal fields.',
 [('ConfigDict; strict=True; extra="forbid"', 'Model configuration can require actual JSON/Python types rather than common coercions and reject undeclared fields. These policies apply to that model, not automatically to all URL transport values.'),
  ('Coercion; writable-field allowlist', 'Coercion changes a supplied representation into another type. An explicit model field list defines what a client may write; server-owned owner_id must stay outside it.')],
 'Default Pydantic behaviour often accepts useful conversions. For this project’s JSON bodies, completed must be a Boolean rather than the string "false". '
 'Explicit strictness makes the contract predictable, but it is a design choice rather than a universal rule for every API. '
 'Rejecting extra keys catches misspellings and visitor-supplied owner_id. The authenticated principal supplies ownership on the server. '
 'Path/query values are text on the wire and intentionally parsed into their declared types. That is separate from strict JSON body values. '
 'A schema that rejects unknown keys reduces accidental mass assignment, but routes must still enforce owner checks.',
 'model_config=ConfigDict(strict=True,extra="forbid")',
 fixture('for change in [{"completed":False},{"completed":"false"},{"owner_id":2}]:\n    payload={"title":"Strict body","body":"Actual Boolean"};payload.update(change)\n    print(client.post("/v1/notes",headers=headers,json=payload).status_code)'),
 'Actual False is accepted. A string Boolean and a client-selected owner field are rejected without writing a note.',
 ('db.insert(**request.json())  # accept all submitted keys', 'data=NoteCreate.model_validate(payload)\n# derive owner from verified user', 'Do not let incoming JSON select internal ownership or database columns.'),
 'Reject a misspelled title field while keeping the correct title present.',
 fixture('r=client.post("/v1/notes",headers=headers,json={"title":"Correct","body":"Body","titel":"Typo"})\nprint(r.status_code,r.json()["detail"][0]["type"])'),
 'Compare an accepted integer query string with a rejected string Boolean body.',
 fixture('print(client.get("/v1/notes?limit=2",headers=headers).status_code)\nprint(client.patch("/v1/notes/1",headers=headers,json={"completed":"false"}).status_code)'),
 'Declare writable fields explicitly and distinguish intentional transport parsing from unwanted JSON coercion.',
 [('Can a client choose owner_id in NoteCreate?', 'No', 'Always', 'If it is an integer', 'The body forbids that field; ownership comes from the verified account.'),
  ('Does strict JSON prevent parsing ?limit=2 as int?', 'No', 'Always', 'Only with SQLite', 'URL parsing and body-model strictness are separate contracts.')])

lesson(2, '3. Field validators and normalisation order',
 'Reject meaningless text after trimming without changing passwords.',
 [('field_validator; classmethod; normalisation', 'A field validator runs custom logic for declared fields. Here it trims note text and validates the resulting value. A classmethod receives the class rather than an instance.'),
  ('ValidationError; errors()', 'Direct model construction raises Pydantic ValidationError on invalid data. errors() gives structured details. At an HTTP boundary FastAPI wraps invalid request input as RequestValidationError; do not print raw secret-bearing inputs.'),
  ('SecretStr; get_secret_value', 'SecretStr masks ordinary representations, but authorised code can retrieve its value to hash it. Masking is not encryption, safe storage or permission to log raw validation inputs.')],
 'A min_length=1 check sees spaces as characters. If your application strips them later, a seemingly valid input can become empty. '
 'The project therefore trims note title/body and rejects an empty result inside the validator before the value reaches storage. '
 'Username canonicalisation uses a documented ASCII lowercase policy. It is not an international username transliteration algorithm. '
 'Do not apply note-text trimming to a password; spaces may be intentional parts of that credential. '
 'Keep validator error messages generic so they do not echo private input into HTTP error responses.',
 '@field_validator("title")\n@classmethod\ndef meaningful(cls,value):\n    value=value.strip()\n    if not value:raise ValueError("Text is required")\n    return value',
 'from learning_api.schemas import NoteCreate,UserCreate\nfrom pydantic import ValidationError\nprint(NoteCreate(title="  HTTP  ",body=" Explain ").title)\ntry:NoteCreate(title="   ",body="Body")\nexcept ValidationError:print("Whitespace rejected")\nuser=UserCreate(username=" ASHA ",password=" fictional-long-password ")\nprint(user.username,user.password.get_secret_value().startswith(" "))',
 'Notes are normalised and validated; the username becomes asha; the password’s leading space is preserved. Different data deserves different policies.',
 ('if len(title)>0: save(title.strip())', 'title=title.strip()\nif not title: reject()', 'Validate the value that will actually be stored.'),
 'Check that both note fields are trimmed.',
 'from learning_api.schemas import NoteCreate\nnote=NoteCreate(title=" A ",body=" B ")\nprint(repr(note.title),repr(note.body))',
 'Show that a SecretStr representation does not reveal the fictional password.',
 'from learning_api.schemas import UserCreate\nuser=UserCreate(username="asha",password="fictional-learning-passphrase")\nprint(str(user.password))\nprint("fictional-learning" in repr(user))',
 'Normalise where appropriate, validate after transformation, and keep password handling deliberately separate.',
 [('When should whitespace-only note text be rejected?', 'After trimming inside validation', 'After committing it', 'Only when displayed', 'Storage should receive the validated meaningful value.'),
  ('Is SecretStr encryption?', 'No', 'Always', 'Only on Windows', 'It masks common representations; raw retrieval is still possible.')])

lesson(2, '4. Nested models and cross-field rules',
 'Validate related fields and report the location of nested problems.',
 [('Nested model; list[Model]', 'A model can contain another model or a list of models. Validation walks the nested structure and reports a location path to the failing field.'),
  ('model_validator(mode="after")', 'An after-model validator inspects the validated model as a whole, allowing rules such as end>=start. Return self when the rule is satisfied.')],
 'A resource may contain structured subobjects, not just flat strings. Use nested models when those parts have their own contract. '
 'Single-field rules cannot express every relationship. A range with positive start/end can still have its end before its start. '
 'Validate that relationship after both individual fields have been parsed successfully. '
 'Nested input does not automatically imply nested database tables or permission to create arbitrary related rows. Decide persistence separately. '
 'This independent study-session model introduces the pattern without complicating the final notes database.',
 'class Session(BaseModel):\n    topics:list[Topic]\n    @model_validator(mode="after")\n    def order(self):\n        ...\n        return self',
 '''from pydantic import BaseModel,Field,ValidationError,model_validator
class Topic(BaseModel):
    title:str=Field(min_length=1)
class Session(BaseModel):
    start:int=Field(ge=0)
    end:int=Field(ge=0)
    topics:list[Topic]
    @model_validator(mode="after")
    def ordered(self):
        if self.end<self.start:raise ValueError("End must not precede start")
        return self
session=Session(start=5,end=15,topics=[{"title":"HTTP"}])
print(session.topics[0].title,session.end-session.start)
try:Session(start=20,end=10,topics=[])
except ValidationError:print("Reversed range rejected")''',
 'The dictionary inside topics becomes a Topic model. A reversed interval fails the relationship rule even though both endpoints are nonnegative integers.',
 ('start>=0 and end>=0  # assume correct order', 'if end<start: raise ValueError("Invalid order")', 'Independent field validity does not establish a valid relationship.'),
 'Find the failing location of a blank nested topic title.',
 '''from pydantic import BaseModel,Field,ValidationError
class Topic(BaseModel):
    title:str=Field(min_length=1)
class Batch(BaseModel):
    topics:list[Topic]
try:Batch(topics=[{"title":""}])
except ValidationError as error:print(error.errors()[0]["loc"])''',
 'Dump a nested batch and confirm it becomes ordinary dictionaries/lists.',
 '''from pydantic import BaseModel
class Topic(BaseModel):
    title:str
class Batch(BaseModel):
    topics:list[Topic]
print(Batch(topics=[Topic(title="Models")]).model_dump())''',
 'Use field rules for individual values and model rules for relationships; nested schemas do not decide database design for you.',
 [('Where does an ordering rule between two fields belong?', 'A model-level validator', 'Only CSS', 'A URL filename', 'It needs the relationship between already validated fields.'),
  ('Does a nested model automatically create a related database row?', 'No', 'Always', 'Only with a list', 'A data contract and persistence mapping are distinct.')])

lesson(2, '5. Separate writable models from public responses',
 'Use response models to expose only the intended public representation.',
 [('response_model; output validation/filtering', 'A route response model validates/serialises the returned data and filters undeclared fields. Keep private fields outside the response schema.'),
  ('Input model versus output model', 'Creation may accept a password; a public user response must never include it or its hash. Server-generated ids/timestamps can appear only in output models.')],
 'Input and output are different promises. A create body has no server-generated id, while a created note response does. '
 'An internal row may contain owner_id or password_hash for application work. That is not a reason to publish every column. '
 'The final UserRead exposes only id and username; NoteRead omits internal ownership even though the query uses it. '
 'Do not rely on output filtering as your only permission check. A filtered private note is still a private note. '
 'Invalid server output is an application bug, not a client’s invalid-input problem; test response schemas as well as requests.',
 '@app.get("/user",response_model=UserRead)\ndef user():\n    return internal_user',
 basic('class PublicUser(BaseModel):\n    id:int\n    username:str\n@app.get("/user",response_model=PublicUser)\ndef user():\n    return {"id":1,"username":"asha","password_hash":"fictional-internal-placeholder"}',
       'print(client.get("/user").json())'),
 'The response contains only the declared public fields. The fictional internal placeholder is not a credential and is filtered out.',
 ('return dict(database_row)  # expose every field without a response contract', '@app.get("/user",response_model=UserRead)', 'Explicit public schemas prevent accidental disclosure of internal fields.'),
 'Inspect the exact keys returned by the project’s current-user route.',
 fixture('print(sorted(client.get("/v1/me",headers=headers).json()))'),
 'Verify a public note response excludes its stored owner_id.',
 fixture('data=client.get("/v1/notes/1",headers=headers).json()\nprint("owner_id" in data,sorted(data))'),
 'Accept only intended writable fields and return only intended public fields, while enforcing access separately.',
 [('Should UserRead contain password_hash?', 'No', 'Always', 'Only for the current user', 'Password verifiers remain internal even for the account owner.'),
  ('Does response_model replace ownership checks?', 'No', 'Always', 'If it hides owner_id', 'Filtering fields does not authorise access to the record.')])

lesson(2, '6. PUT, PATCH, omission and False',
 'Represent partial updates without losing a legitimate False value.',
 [('PUT versus PATCH', 'This API defines PUT as replacement of all writable fields and PATCH as modification of supplied fields. These are documented interface semantics, not automatically implemented by a decorator.'),
  ('model_fields_set; exclude_unset=True', 'Pydantic records which fields were explicitly supplied. model_dump(exclude_unset=True) includes supplied False while leaving omitted fields out.'),
  ('Explicit null policy', 'This project rejects null for note updates and rejects an empty PATCH. Optional defaults support omission in the model; a before-model validator disallows explicit null in the submitted object.')],
 'An update needs three distinct cases: omitted, supplied False, and supplied null. A truthiness check destroys that distinction. '
 'For PATCH, preserve fields the client did not send. For this API, null is not a command to erase required text or reset a Boolean. '
 'For PUT, require title, body and completed together so replacement cannot silently retain unspecified writable fields. '
 'Use the validated model’s exclude_unset dump, then update only the fixed supported columns. '
 'The server still chooses the owner and retains the original creation timestamp for both operations.',
 'changes=data.model_dump(exclude_unset=True)\n# False stays present; omitted fields stay absent.',
 fixture('client.patch("/v1/notes/1",headers=headers,json={"completed":True})\nr=client.patch("/v1/notes/1",headers=headers,json={"completed":False})\nprint(r.status_code,r.json()["completed"],r.json()["title"])\nprint(client.patch("/v1/notes/1",headers=headers,json={"completed":None}).status_code)'),
 'False is stored rather than skipped, the old title survives omission, and explicit null is rejected.',
 ('if data.completed: update_completed(data.completed)', 'changes=data.model_dump(exclude_unset=True)', 'False is a valid supplied value, not evidence of omission.'),
 'Show the fields explicitly supplied to NotePatch.',
 'from learning_api.schemas import NotePatch\npatch=NotePatch(completed=False)\nprint(sorted(patch.model_fields_set),patch.model_dump(exclude_unset=True))',
 'Contrast an incomplete PUT, empty PATCH and complete PUT.',
 fixture('print(client.put("/v1/notes/1",headers=headers,json={"title":"Only title"}).status_code)\nprint(client.patch("/v1/notes/1",headers=headers,json={}).status_code)\nprint(client.put("/v1/notes/1",headers=headers,json={"title":"Replacement","body":"All fields","completed":False}).status_code)'),
 'Update semantics must preserve the difference between omission, False and explicit null.',
 [('Which setting preserves an explicitly supplied False?', 'exclude_unset=True', 'if value', 'Drop all falsey values', 'It tracks supplied fields rather than truthiness.'),
  ('What does this API require for PUT?', 'All writable note fields', 'Only any one field', 'A visitor-chosen owner_id', 'Its contract defines PUT as full writable-field replacement.')])

lesson(3, '1. Design resources and methods before routes',
 'Write a coherent resource contract before implementing handlers.',
 [('REST; resource; representation', 'REST-oriented APIs identify resources with URLs and transfer representations such as JSON. HTTP methods communicate operation intent; using JSON alone does not establish a coherent design.'),
  ('Collection and member URL', '/v1/notes identifies a collection; /v1/notes/{note_id} identifies a member. Use method semantics rather than action words in every URL.')],
 'Begin with the user’s task: an authenticated person owns notes and can list, create, read, replace, modify and delete them. '
 'Write the method/path/input/success/error contract before writing SQL. This reveals missing operations and inconsistent response shapes early. '
 'Use plural collection nouns consistently. An action such as logout is reasonably an account operation; do not force every domain concept into a fake CRUD resource. '
 'Every member operation must scope the selected id to its verified owner. Resource naming does not provide that enforcement. '
 'The final project generates its machine-readable contract from the implemented route declarations; request tests check the promised behaviour.',
 'GET /v1/notes\nPOST /v1/notes\nGET|PUT|PATCH|DELETE /v1/notes/{note_id}',
 fixture('paths=client.get("/openapi.json").json()["paths"]\nfor path in ["/v1/notes","/v1/notes/{note_id}"]:\n    print(path,sorted(paths[path]))',False),
 'The collection supports GET/POST, and the member supports GET/PUT/PATCH/DELETE. The URL stays stable while the HTTP method expresses intent.',
 ('GET /deleteNote?id=1  # mutation by GET', 'DELETE /v1/notes/1', 'GET should not intentionally mutate resource state.'),
 'Write and print a compact method/status contract for create, read and delete.',
 'contract={"POST /v1/notes":201,"GET /v1/notes/1":200,"DELETE /v1/notes/1":204}\nfor operation,status in contract.items():print(operation,status)',
 'Verify an unsupported write method is rejected instead of accidentally invoking a read.',
 fixture('print(client.post("/v1/notes/1",headers=headers,json={}).status_code)'),
 'Design the resource, method, input, response and access rule together before implementing storage.',
 [('Which operation should intentionally delete a note?', 'DELETE on its member URL', 'GET on a delete link', 'A CSS class change', 'GET is a safe read method; deletion is a state-changing operation.'),
  ('Does a well-named URL enforce ownership?', 'No', 'Always', 'Only with v1', 'The handler/query must apply the verified owner predicate.')])

lesson(3, '2. Success statuses, Location and empty 204 bodies',
 'Return a response whose status and body match the operation.',
 [('201 Created; Location', '201 reports successful creation. Location can identify the created resource so a client can fetch it without reconstructing a URL.'),
  ('204 No Content; Response', '204 deliberately has no response body. Return Response(status_code=204), not a JSON message or null body advertised as content.')],
 'A successful read returns 200 with a representation. A create returns 201 with the new note and Location. '
 'Our replacement and partial update return 200 with the current representation, and successful deletion returns 204 with no body. '
 'Do not call .json() on a successful empty 204 response. Check status and content length instead. '
 'An HTTP response contract should be predictable enough for a program, not just readable to a person watching a terminal. '
 'Registration returns a public account and points to /v1/me; it still requires a separate login before accessing that protected route.',
 'response.headers["Location"]=f"/v1/notes/{note_id}"\nreturn Response(status_code=204)  # delete only',
 fixture('r=client.post("/v1/notes",headers=headers,json={"title":"Status practice","body":"Created"})\nprint(r.status_code,r.headers["Location"])\nurl=r.headers["Location"]\nprint(client.get(url,headers=headers).status_code)\ndeleted=client.delete(url,headers=headers)\nprint(deleted.status_code,len(deleted.content))'),
 'The client follows the server-provided Location, reads the new record and then receives a truly empty deletion response.',
 ('return {"deleted":True}  # while declaring 204', 'return Response(status_code=204)', 'A no-content status must not carry a JSON representation.'),
 'Assert a create response Location agrees with its returned id.',
 fixture('r=client.post("/v1/notes",headers=headers,json={"title":"Location","body":"Follow it"})\nprint(r.headers["Location"]==f"/v1/notes/{r.json()[\'id\']}")'),
 'Delete twice and interpret the different responses.',
 fixture('first=client.delete("/v1/notes/1",headers=headers)\nsecond=client.delete("/v1/notes/1",headers=headers)\nprint(first.status_code,second.status_code)'),
 'Use status, Location and body consistently; a 204 result is intentionally not JSON.',
 [('What body belongs with a 204 response?', 'No body', 'A JSON success object', 'A JSON null message', '204 means no response content.'),
  ('What can Location identify after note creation?', 'The newly created member URL', 'The password hash', 'The local database file', 'The client can follow the resource URL.')])

lesson(3, '3. Error contracts, authentication and existence',
 'Choose meaningful failure responses without revealing another owner’s record.',
 [('401; WWW-Authenticate; 403; 404; 409', '401 requests valid authentication and includes a Bearer challenge here. 403 means authenticated but forbidden in some APIs. This project uses 404 for absent or other-owner notes, 409 for an unavailable username.'),
  ('Uniform inaccessible-resource response', 'Applying id and owner together gives the same public response for missing and other-owner records. It avoids directly confirming another user’s resource existence.')],
 'A missing credential, malformed input and duplicate account name are different failures; do not collapse all of them into 200 with an error string. '
 'The API returns a short detail message for deliberate HTTP failures and safe structured field errors for validation. '
 'A nonexistent note and another owner’s note both produce Note not found. The caller cannot use that message to distinguish them. '
 'Do not expose SQL errors, stack traces, raw password input or signing keys as repair advice. '
 'A database uniqueness conflict must roll back cleanly so the original account and subsequent requests remain usable.',
 'raise HTTPException(401,"Valid bearer token required",headers={"WWW-Authenticate":"Bearer"})',
 fixture('anonymous=client.get("/v1/me")\nprint(anonymous.status_code,anonymous.headers["www-authenticate"])\nben=login(client,"ben")\na=client.get("/v1/notes/1",headers=ben)\nb=client.get("/v1/notes/999",headers=ben)\nprint(a.status_code,b.status_code,a.json()==b.json())'),
 'The anonymous call receives a Bearer challenge. Ben receives the same 404 representation for Asha’s note and a missing note.',
 ('return {"error":"not logged in"}  # 200', 'raise HTTPException(401,"Valid bearer token required",headers={"WWW-Authenticate":"Bearer"})', 'Clients need the correct failure status, not only a message.'),
 'Try a duplicate username and confirm the original account can still log in.',
 fixture('print(register(client,"asha").status_code)\nprint(client.get("/v1/me",headers=login(client,"asha")).status_code)'),
 'Compare two error categories: a malformed identifier and a valid but missing identifier.',
 fixture('print(client.get("/v1/notes/nope",headers=headers).status_code)\nprint(client.get("/v1/notes/999",headers=headers).status_code)'),
 'Use errors to explain the contract while keeping credentials and inaccessible resource existence private.',
 [('What does this API return for another owner’s note?', 'The same 404 as a missing note', 'Its private body with a warning', 'Always a successful empty object', 'The query requires both id and verified owner.'),
  ('Which status represents an unavailable unique username?', '409', '201', '204', 'It conflicts with an existing resource constraint.')])

lesson(3, '4. Safe reads and idempotent final state',
 'Understand repeated request effects instead of memorising verbs without meaning.',
 [('Safe method; idempotence', 'A safe method is intended for reading, not requested state changes. Idempotence means repeating the same request has the same intended final effect as making it once, not necessarily the same status or log entry.'),
  ('POST duplicates; replacement semantics', 'A normal create POST can make a new row every time. Repeating the same PUT replacement should produce the same resource state. This project does not implement idempotency keys.')],
 'A link preview or browser prefetch can issue GET without the learner intending a mutation, so GET /delete is a poor design. '
 'Two identical create POST requests may create two notes; a network retry therefore needs client awareness or an explicitly designed deduplication mechanism. '
 'Repeating the same PUT leaves title, body and completed with the same values. Our PATCH sets supplied values, so repeating these assignments also leaves the same state; not every possible PATCH operation is idempotent. '
 'A second DELETE can return 404 after the first returned 204 while the intended final state remains absent. '
 'Do not describe idempotence as identical response bytes or as protection from every concurrency problem.',
 '# Compare final resource state after repeated calls, not just equal statuses.',
 fixture('payload={"title":"Stable","body":"Same replacement","completed":False}\na=client.put("/v1/notes/1",headers=headers,json=payload).json()\nb=client.put("/v1/notes/1",headers=headers,json=payload).json()\nprint("Repeated PUT same state:",a==b)\nprint(client.delete("/v1/notes/1",headers=headers).status_code,client.delete("/v1/notes/1",headers=headers).status_code)'),
 'The replacement representation is stable. Both deletes leave the record absent even though the second reports that it no longer exists.',
 ('# Idempotent means every response status must be identical', '# Idempotent refers to the intended repeated effect', 'A repeated delete may report a missing record without restoring it.'),
 'Create the same payload twice and show that this API does not deduplicate POST.',
 fixture('body={"title":"Retry example","body":"Same payload"}\na=client.post("/v1/notes",headers=headers,json=body).json()\nb=client.post("/v1/notes",headers=headers,json=body).json()\nprint(a["id"]!=b["id"])'),
 'Make two reads and verify neither changes the count.',
 fixture('a=client.get("/v1/notes",headers=headers).json()\nb=client.get("/v1/notes",headers=headers).json()\nprint(a["total"],b["total"],a==b)'),
 'Reason about intended final effects under repetition; do not mistake that property for identical responses or automatic retry safety.',
 [('Can a repeated DELETE return 404 and remain idempotent?', 'Yes', 'Never', 'Only without a database', 'The intended final state is still absence.'),
  ('Does this create POST deduplicate identical payloads?', 'No', 'Always', 'If the title matches', 'No idempotency-key or uniqueness contract for note titles is implemented.')])

lesson(3, '5. Versioning, literal search and pagination contracts',
 'Keep the interface explicit and prevent search from changing SQL meaning.',
 [('API version prefix; backward compatibility', '/v1 is an interface namespace. A version label alone does not preserve compatibility; changes to required fields, status semantics or output shape can still break clients.'),
  ('Bound SQL parameters; instr; ASCII lowercase', 'SQLite instr checks literal substring occurrence. Bound values remain data. SQLite lower has limited built-in Unicode case handling; this project does not claim full multilingual case folding.')],
 'A client should know the maximum page size, ordering, count meaning and search policy. Document those choices rather than leaving them accidental. '
 'The final list route orders by id, returns an owner-filtered total and applies a literal title substring search. '
 'Percent and underscore are literal characters here, not LIKE wildcards. An apostrophe remains text because the value is bound. '
 'Offset pagination can shift when rows are inserted/deleted between requests; a consistent count/items snapshot inside one request does not freeze all future pages. '
 'A future cursor API can address different pagination needs, but adding complexity before understanding the current contract would obscure the lesson.',
 'WHERE owner_id=? AND instr(lower(title),lower(?))>0\nORDER BY id LIMIT ? OFFSET ?',
 fixture('for query in ["http","%","_","\' OR 1=1 --"]:\n    r=client.get("/v1/notes",headers=headers,params={"q":query})\n    print(repr(query),r.json()["total"])'),
 'The literal percent finds the fixture’s 100% title. The SQL-looking string matches no title and cannot broaden the owner predicate.',
 ('sql=f"SELECT * FROM notes WHERE title LIKE \'%{q}%\'"', 'db.execute("SELECT * FROM notes WHERE instr(title,?)>0",(q,))', 'Bind data values; do not insert visitor text into SQL source.'),
 'Fetch a page beyond the available rows while preserving the total.',
 fixture('page=client.get("/v1/notes?offset=100",headers=headers).json()\nprint(page["total"],page["items"])'),
 'Verify another owner’s total is independent of Asha’s notes.',
 fixture('ben=login(client,"ben")\nprint(client.get("/v1/notes",headers=headers).json()["total"],client.get("/v1/notes",headers=ben).json()["total"])'),
 'Document version, ordering, limits and literal search precisely; binding protects query meaning, not every application policy.',
 [('Does % behave as a wildcard with this instr search?', 'No', 'Always', 'Only when authenticated', 'instr uses a literal substring rather than LIKE wildcard syntax.'),
  ('Does a v1 prefix automatically make breaking changes safe?', 'No', 'Always', 'Only with JSON', 'Compatibility depends on preserving the actual contract.')])

lesson(3, '6. Turn the REST contract into executable checks',
 'Verify complete request flows with statuses and data assertions.',
 [('Contract test; OpenAPI response metadata', 'A contract test verifies a client-visible promise. OpenAPI describes the implemented interface but does not by itself verify status/body/ownership behaviour.')],
 'Build a short flow that creates a note, follows Location, updates it, deletes it and verifies absence. '
 'Assert the representation after update rather than merely asserting that the route returned 200. '
 'Check the generated schema advertises the create status and authentication scheme, then separately test those requirements. '
 'Use a fresh fixture for each coherent experiment so earlier examples do not silently influence results. '
 'The final acceptance suite later expands this flow to multiple accounts, token failures, restart persistence and non-destructive initialisation.',
 '# create -> read -> update -> delete -> missing',
 fixture('r=client.post("/v1/notes",headers=headers,json={"title":"Contract","body":"First version"})\nassert r.status_code==201\nurl=r.headers["Location"]\nr=client.patch(url,headers=headers,json={"body":"Second version"})\nassert r.json()["body"]=="Second version"\nassert client.delete(url,headers=headers).status_code==204\nassert client.get(url,headers=headers).status_code==404\nprint("Create/update/delete contract passed")'),
 'These assertions check state and the final missing response. A returned success alone would not prove the update changed the intended field.',
 ('assert result.status_code==200  # enough for every operation', 'assert result.status_code==expected\nassert relevant_fields==expected_fields', 'Different operations have different success statuses and state promises.'),
 'Confirm create and delete success statuses are present in the generated schema.',
 fixture('paths=client.get("/openapi.json").json()["paths"]\nprint("201" in paths["/v1/notes"]["post"]["responses"],"204" in paths["/v1/notes/{note_id}"]["delete"]["responses"])',False),
 'Verify an update preserves both the resource id and its creation timestamp.',
 fixture('before=client.get("/v1/notes/1",headers=headers).json()\nafter=client.patch("/v1/notes/1",headers=headers,json={"title":"Revised"}).json()\nprint(before["id"]==after["id"],before["created_at"]==after["created_at"])'),
 'A useful API contract is documented, executable and verified against relevant stored state.',
 [('What should an update test check beyond status?', 'The changed and preserved fields', 'Only CSS colour', 'The terminal font', 'The data representation proves the intended state transition.'),
  ('Can metadata replace request-level contract tests?', 'No', 'Always', 'If generated automatically', 'Generation does not prove the implementation enforces every promise.')])

lesson(4, '1. Dependency injection makes required resources explicit',
 'Declare a handler dependency instead of constructing hidden global resources.',
 [('Depends; dependency injection; dependency graph', 'Depends tells FastAPI to call a provider and supply its result. Providers can depend on other providers, forming a graph of required values for a request.'),
  ('Annotated dependency alias', 'Annotated[SomeType, Depends(provider)] combines an expected result type with its provider. It does not call the provider at import time or make that result a query parameter.')],
 'A route needs things such as configuration, a database connection and a verified principal. Put these requirements in its signature. '
 'FastAPI resolves the dependency graph before invoking the handler and can reuse a provider’s result within that request by default. '
 'Injection is not an authentication system by itself. A provider must actually verify the credential if its job is to return a trusted user. '
 'Keep each provider narrow and explain what it returns, what failure it raises and who owns cleanup. '
 'This first provider returns a simple label; later providers yield connections and validate bearer tokens.',
 'def provider():\n    return value\nValue=Annotated[str,Depends(provider)]',
 basic('def source():\n    return "local"\nLabel=Annotated[str,Depends(source)]\n@app.get("/source")\ndef read(label:Label):\n    return {"source":label}',
       'print(client.get("/source").json())'),
 'The label comes from the provider, not from a visitor-controlled source query argument. Its type and source are visible in the signature.',
 ('value: str = provider()  # runs while defining the function', 'value:Annotated[str,Depends(provider)]', 'Pass the provider function to Depends rather than calling it at definition time.'),
 'Inject a small settings dictionary and use one of its values.',
 basic('def settings():\n    return {"mode":"practice"}\n@app.get("/mode")\ndef read(config:Annotated[dict,Depends(settings)]):\n    return config', 'print(client.get("/mode").json())'),
 'Build a second provider that depends on the first.',
 basic('def base():\n    return "local"\ndef label(value:Annotated[str,Depends(base)]):\n    return value+" API"\n@app.get("/label")\ndef read(value:Annotated[str,Depends(label)]):\n    return {"label":value}', 'print(client.get("/label").json())'),
 'Dependencies describe required values explicitly; the provider’s implementation determines whether those values are trustworthy.',
 [('Should Depends receive provider or provider()?', 'provider', 'provider()', 'Its printed result', 'The framework calls the provider at the appropriate request boundary.'),
  ('Does dependency injection automatically authenticate a user?', 'No', 'Always', 'Only with Annotated', 'Authentication requires an implemented verification provider.')])

lesson(4, '2. Yield dependencies own request cleanup',
 'Acquire and close a request resource even when the handler fails.',
 [('yield dependency; finally', 'A dependency that yields supplies a value and later resumes for cleanup. Put release logic in finally so both successful and failed request paths clean up.'),
  ('Per-request connection; check_same_thread=False', 'The project creates one SQLite connection per request. Disabling the thread check accommodates sync-worker execution; it does not make one global connection safe for concurrent requests.')],
 'A shared database filename is not a reason to share one connection across every request. Give each request an explicit connection lifetime. '
 'The get_db provider opens an existing database in read/write mode, yields it and closes it in finally. '
 'The normal response path and an HTTPException both finish the dependency boundary. Test both, not just a successful query. '
 'FastAPI may resolve the same provider through several branches of the dependency graph; its default per-request caching avoids opening duplicates unnecessarily. '
 'Do not return a generator itself from a handler or forget to close resources on exceptions.',
 'def get_db(request:Request):\n    db=connect(request.app.state.database)\n    try:yield db\n    finally:db.close()',
 basic('events=[]\ndef resource():\n    events.append("open")\n    try:yield "connection placeholder"\n    finally:events.append("close")\n@app.get("/read")\ndef read(value:Annotated[str,Depends(resource)]):\n    return {"ready":bool(value)}\n@app.get("/fail")\ndef fail(value:Annotated[str,Depends(resource)]):\n    raise HTTPException(404,"Missing")',
       'print(client.get("/read").status_code,events)\nevents.clear()\nprint(client.get("/fail").status_code,events)'),
 'Both request paths show an open/close pair. The placeholder makes lifetime visible without mistaking an event list for a real database connection.',
 ('db=connect(path)\nreturn db  # nobody closes it', 'try:yield db\nfinally:db.close()', 'Resource ownership must include cleanup, including failure paths.'),
 'Use the project’s connection helper with an explicit try/finally for a standalone count.',
 fixture('from learning_api.database import connect\ndb=connect(app.state.database)\ntry:print("Notes:",db.execute("SELECT count(*) FROM notes").fetchone()[0])\nfinally:db.close()'),
 'Prove an unhandled error in a handler still runs dependency cleanup without leaking a traceback into the lesson output.',
 basic('events=[]\ndef resource():\n    try:yield "owned"\n    finally:events.append("closed")\n@app.get("/fail")\ndef fail(value:Annotated[str,Depends(resource)]):\n    raise RuntimeError("Fictional failure")',
       'try:client.get("/fail")\nexcept RuntimeError:print("Raised during test")\nprint(events)'),
 'Pair acquisition with finally cleanup; a thread-check option is not permission to share a mutable connection globally.',
 [('What belongs in a yielded connection dependency’s finally block?', 'Connection cleanup', 'Publishing the password', 'Starting a new global server', 'Cleanup must happen on success and failure.'),
  ('Does check_same_thread=False guarantee concurrency safety?', 'No', 'Always', 'Only for writes', 'It removes a driver check, not the need for scoped ownership.')])

lesson(4, '3. Transactions protect complete changes',
 'Commit an approved unit of work and roll it back after an integrity failure.',
 [('BEGIN IMMEDIATE; commit; rollback', 'The explicit transaction helper starts a SQLite write reservation, commits on success and rolls back on failure. Related writes then succeed or fail as one unit.'),
  ('Foreign key pragma; database constraints', 'Each connection enables foreign_keys. Uniqueness, required fields, CHECK constraints and foreign keys protect stored data even when code bypasses an HTTP model.')],
 'A valid JSON body cannot guarantee a write will succeed: another request may already have taken the username, or a stored relationship may be invalid. '
 'Use both application validation and database constraints. Catch expected integrity conflicts, roll back and report the intended client outcome. '
 'The project uses an explicit transaction helper with SQLite autocommit outside the helper. Do not assume the connection context manager closes a connection or starts every needed transaction. '
 'The simple list route also uses a transaction for a consistent total/items snapshot; BEGIN IMMEDIATE serialises more work than an optimised read-only design would. '
 'This local teaching API favours clear boundaries and small workloads, not high write throughput or distributed consistency claims.',
 'with transaction(db):\n    db.execute(sql,parameters)\n# commit on success; rollback on failure',
 fixture('import sqlite3\nfrom learning_api.database import connect,transaction\ndb=connect(app.state.database)\ntry:\n    before=db.execute("SELECT count(*) FROM notes").fetchone()[0]\n    try:\n        with transaction(db):\n            db.execute("INSERT INTO notes(owner_id,title,body,completed,created_at) VALUES(?,?,?,?,?)",(1,"Will roll back","Body",0,"fictional"))\n            db.execute("INSERT INTO users(username,password_hash) VALUES(?,?)",("asha","fictional-placeholder"))\n    except sqlite3.IntegrityError:print("Conflict rolled back")\n    print(before==db.execute("SELECT count(*) FROM notes").fetchone()[0],db.in_transaction)\nfinally:db.close()'),
 'The duplicate username fails after the note insert. Rollback removes that earlier insert too and leaves the connection outside a transaction.',
 ('try:write_one();write_two()\nexcept Exception:print("Saved")', 'with transaction(db):\n    write_one()\n    write_two()', 'A partially completed change must not be falsely reported as saved.'),
 'Check that the project connection actually enables foreign keys.',
 fixture('from learning_api.database import connect\ndb=connect(app.state.database)\ntry:print(db.execute("PRAGMA foreign_keys").fetchone()[0])\nfinally:db.close()'),
 'Attempt a blank title directly in SQLite and show the database rejects it.',
 fixture('import sqlite3\nfrom learning_api.database import connect,transaction\ndb=connect(app.state.database)\ntry:\n    try:\n        with transaction(db):db.execute("UPDATE notes SET title=? WHERE id=?",("",1))\n    except sqlite3.IntegrityError:print("Database CHECK rejected empty title")\n    print(db.execute("SELECT title FROM notes WHERE id=1").fetchone()[0])\nfinally:db.close()'),
 'Transactions define atomic work; database constraints remain necessary even with validated HTTP input.',
 [('What happens to earlier writes in a failed transaction?', 'They are rolled back together', 'They always remain saved', 'They become response headers', 'The unit of work is atomic when the failure rolls back.'),
  ('Should only the form UI enforce stored relationships?', 'No', 'Always', 'Only for local apps', 'Database constraints protect paths that bypass a particular UI.')])

lesson(4, '4. Route, model and storage layers cooperate',
 'Follow one private CRUD operation across validation, identity and SQL.',
 [('Layer boundary; owned lookup', 'Models validate shapes, dependencies supply verified identity/resources, routes coordinate outcomes and SQL persists constrained state. owned requires both id and server-derived owner_id.'),
  ('Full CRUD; server-owned fields', 'CRUD means create/read/update/delete. Id, owner and creation time are generated or derived by the server, not accepted as writable client fields.')],
 'Keep the project small enough to trace. schemas.py holds contracts, database.py owns storage lifetime and transaction helpers, and the app module coordinates routes and authentication. '
 'For create, validate the body, verify the caller, insert with user.id, read the new row and return its public model plus Location. '
 'For a member update/delete, first require the owner-filtered lookup inside the transaction, then write using the same id/owner predicate. '
 'A hidden input or a JSON owner_id supplied by a client is not a trusted identity source. '
 'These boundaries allow Week 40’s planned SQLAlchemy refactor to change the storage implementation without casually changing the HTTP contract.',
 'SELECT * FROM notes WHERE id=? AND owner_id=?\n# Both values bound; owner comes from the verified principal.',
 fixture('created=client.post("/v1/notes",headers=headers,json={"title":"Layer trace","body":"Validate -> authorise -> store"})\nurl=created.headers["Location"]\nprint("Create:",created.status_code)\nprint("Read:",client.get(url,headers=headers).json()["title"])\nprint("Patch:",client.patch(url,headers=headers,json={"completed":True}).json()["completed"])\nprint("Delete:",client.delete(url,headers=headers).status_code)'),
 'The same URL identifies the member through read, partial update and delete. The body never provides an owner id.',
 ('owner_id=payload["owner_id"]', 'owner_id=current_user.id', 'Ownership must be derived from the verified request identity.'),
 'Try a valid cross-owner PATCH and prove the original title is unchanged.',
 fixture('ben=login(client,"ben")\nr=client.patch("/v1/notes/1",headers=ben,json={"title":"Wrong owner"})\nprint(r.status_code,client.get("/v1/notes/1",headers=headers).json()["title"])'),
 'Try a cross-owner delete and prove the original record remains readable by its owner.',
 fixture('ben=login(client,"ben")\nprint(client.delete("/v1/notes/1",headers=ben).status_code,client.get("/v1/notes/1",headers=headers).status_code)'),
 'Trace every write through validated input, verified identity, owner-scoped lookup, transaction and public output.',
 [('Where does a newly created note’s owner come from?', 'The verified current user', 'A visitor-controlled JSON field', 'The title prefix', 'The server associates the record with authenticated identity.'),
  ('Can storage later change while preserving the HTTP contract?', 'Yes, with explicit compatibility tests', 'Never', 'Only by deleting old lessons', 'Layer boundaries and contract tests support a controlled refactor.')])

lesson(4, '5. Override dependencies without replacing the real rules',
 'Use a controlled fake resource for a focused test and keep integration tests real.',
 [('app.dependency_overrides', 'This mapping replaces a specific dependency function during a test. Clear it in finally so later tests cannot inherit the fake.'),
  ('Fake versus integration fixture', 'A fake makes one narrow behaviour easy to test. It cannot prove real hashing, SQL ownership or resource cleanup when those components have been bypassed.')],
 'Dependency injection makes focused tests possible without editing production route code. Replace the exact provider function used in Depends. '
 'Use a fake configuration value for a formatting test or a controlled repository for an error path. '
 'Do not override authentication and then claim the real token verifier passed. Name the boundary you bypassed. '
 'The final project’s main acceptance checks use real temporary SQLite databases and real fictional-account tokens. '
 'Always restore overrides so one test’s convenience cannot silently weaken another test.',
 'app.dependency_overrides[provider]=fake_provider\ntry:...\nfinally:app.dependency_overrides.clear()',
 basic('def source():\n    return "real"\n@app.get("/source")\ndef read(value:Annotated[str,Depends(source)]):\n    return {"source":value}\ndef fake():\n    return "controlled test"',
       'app.dependency_overrides[source]=fake\ntry:print(client.get("/source").json())\nfinally:app.dependency_overrides.clear()\nprint(client.get("/source").json())'),
 'The first request receives the controlled value. Clearing the mapping restores the real provider for the second request.',
 ('app.dependency_overrides[provider]=fake  # never restore', 'try:run_test()\nfinally:app.dependency_overrides.clear()', 'Persistent overrides can contaminate later verification.'),
 'Override a numeric provider, assert the response, then verify the real value returns.',
 basic('def number():\n    return 3\n@app.get("/number")\ndef read(value:Annotated[int,Depends(number)]):\n    return {"number":value}',
       'app.dependency_overrides[number]=lambda:7\ntry:assert client.get("/number").json()["number"]==7\nfinally:app.dependency_overrides.clear()\nprint(client.get("/number").json())'),
 'Verify the actual project fixture has no dependency overrides masking its authentication/database.',
 fixture('print("Real providers active:",not app.dependency_overrides)\nprint(client.get("/v1/me",headers=headers).status_code)'),
 'Use fakes for narrow contracts and real temporary components for the integration guarantees you actually claim.',
 [('Can a fake login provider prove real JWT verification works?', 'No', 'Always', 'If the status is 200', 'The verifier was bypassed by that test.'),
  ('Where should overrides be cleared?', 'In a finally cleanup boundary', 'Never', 'Only at public deployment', 'Cleanup prevents cross-test contamination.')])

lesson(4, '6. Persistence, schema ownership and restart safety',
 'Preserve records and signing configuration across app reconstruction without resetting unknown files.',
 [('Instance directory; schema version', 'instance/ contains this project’s private runtime database/key and is ignored by Git. user_version marks its known schema; initialisation checks expected tables/columns before reuse.'),
  ('secrets.token_bytes; signing key', 'The secrets module creates cryptographically strong random bytes rather than predictable teaching random numbers. The project generates 32 bytes once for its local JWT signing key, stores them privately and never prints them.'),
  ('Exclusive creation; non-destructive initialisation', 'Opening a new file in xb mode fails if it exists. The project creates new owned files only once and refuses unfamiliar databases instead of dropping tables.')],
 'In-memory examples are useful but cannot prove restart persistence. Use a temporary file-backed instance and reconstruct the app against that same owned folder. '
 'The data and signing key must both persist; changing the key would invalidate existing signed access tokens. '
 'Startup creates a new database only if its filename did not exist. An unknown existing schema or invalid key stops startup without resetting it. '
 'This shape/version check is a deliberate learning safeguard, not a general migration framework or tamper-proof database audit. '
 'Never include a real notes.sqlite or signing.key in source control. These local project files are separate from Study Hub’s browser progress and Gist sync.',
 'first=create_app(owned_folder)\nsecond=create_app(owned_folder)\n# Reuse only an explicitly owned instance directory.',
 '''from tempfile import TemporaryDirectory
from fastapi.testclient import TestClient
from learning_api import create_app
from lesson_support import register,login
with TemporaryDirectory() as folder:
    with TestClient(create_app(folder)) as first:
        register(first)
        headers=login(first)
        first.post("/v1/notes",headers=headers,json={"title":"Survives restart","body":"Local file"})
    with TestClient(create_app(folder)) as second:
        print(second.get("/v1/notes",headers=headers).json()["items"][0]["title"])''',
 'The second app reads the first app’s persisted row and verifies the still-valid token using the same private runtime key and login record.',
 ('DROP TABLE notes;  # reset whatever exists at startup', 'verify_known_schema_or_stop()  # preserve unfamiliar files', 'Initialisation must not silently erase existing user data.'),
 'Show that repeated initialisation preserves the owned signing key.',
 '''from tempfile import TemporaryDirectory
from learning_api.database import initialise
with TemporaryDirectory() as folder:
    path,key1=initialise(folder)
    path,key2=initialise(folder)
    print("Same key:",key1==key2,"Bytes:",len(key1))''',
 'Create an unfamiliar database in an owned temporary folder and verify it is refused without losing its row.',
 '''from tempfile import TemporaryDirectory
from pathlib import Path
import sqlite3
from learning_api.database import initialise
with TemporaryDirectory() as folder:
    path=Path(folder)/"notes.sqlite"
    db=sqlite3.connect(path);db.execute("CREATE TABLE unrelated(value TEXT)");db.execute("INSERT INTO unrelated VALUES('preserve')");db.commit();db.close()
    try:initialise(folder)
    except RuntimeError:print("Unknown schema refused")
    db=sqlite3.connect(path)
    try:print(db.execute("SELECT value FROM unrelated").fetchone()[0])
    finally:db.close()''',
 'Persist owned data/key files, verify known schema on restart and refuse destructive automatic resets.',
 [('Should startup erase an unfamiliar existing database?', 'No', 'Always', 'If its filename matches', 'Stop and review a migration while preserving the file.'),
  ('Where does this Python project store its durable notes?', 'Its ignored local SQLite instance', 'Study Hub localStorage', 'A public GitHub token', 'The teaching project owns separate runtime data.')])

lesson(5, '1. Bearer tokens and the local password-form lesson',
 'Distinguish browser sessions, bearer credentials and the scope of this learning flow.',
 [('Bearer token; Authorization header', 'Anyone holding a valid bearer credential can present it. This API expects Authorization: Bearer <token>; the explorer keeps it in a password field in the current tab, not localStorage.'),
  ('OAuth2PasswordRequestForm; tokenUrl', 'FastAPI supplies a form dependency for username/password token requests and OpenAPI metadata for a token endpoint. This local teaching password flow is not a recommendation for modern third-party browser login; authorization-code with PKCE is a different flow.'),
  ('Authentication versus authorisation', 'Authentication verifies the caller’s identity. Authorisation checks whether that verified caller may perform this operation on this resource.')],
 'Week 38 used a cookie-based browser login. Here a client explicitly sends a bearer header with API requests. '
 'Registration creates the account, while POST /v1/token verifies its fictional password and issues a 15-minute access token. '
 'The token endpoint reads application/x-www-form-urlencoded fields, not the JSON registration body. Sending the wrong format is a contract error. '
 'The local explorer is deliberately limited: it holds a token only in the current tab, clears it on successful logout and masks token responses. '
 'Do not paste a GitHub token or real account password into this exercise. Use only the supplied fictional practice credentials.',
 'client.post("/v1/token",data={"username":name,"password":password})\nheaders={"Authorization":"Bearer "+access_token}',
 fixture('register(client,"asha")\nr=client.post("/v1/token",data={"username":"asha","password":PRACTICE_PASSWORD})\ndata=r.json()\nprint(r.status_code,data["token_type"],data["expires_in"])\nh={"Authorization":"Bearer "+data["access_token"]}\nprint(client.get("/v1/me",headers=h).json())',False),
 'The example prints only token type/expiry, never the actual bearer value. The verified header allows /v1/me to return a public identity.',
 ('# Paste a real GitHub credential into the lesson', '# Use the fictional local practice account only', 'This project has its own local account system and no need for an external credential.'),
 'Show that login expects a form rather than the registration JSON shape.',
 fixture('print(client.post("/v1/token",json={"username":"asha","password":PRACTICE_PASSWORD}).status_code)'),
 'Inspect the generated OAuth2 security metadata without printing a credential.',
 fixture('scheme=client.get("/openapi.json").json()["components"]["securitySchemes"]["OAuth2PasswordBearer"]\nprint(scheme["type"],scheme["flows"]["password"]["tokenUrl"])',False),
 'Use fictional local credentials, explicit bearer headers and per-resource authorisation; do not confuse this teaching flow with a complete public identity platform.',
 [('Does possession of a token automatically authorise every note?', 'No', 'Always', 'Only for DELETE', 'The verified user still needs an ownership check.'),
  ('What format does /v1/token consume here?', 'Form-encoded username/password', 'Registration JSON only', 'An HTML cookie file', 'OAuth2PasswordRequestForm reads form fields.')])

lesson(5, '2. Password hashing and generic login failures',
 'Store password verifiers instead of plaintext and avoid revealing which part of login failed.',
 [('scrypt; salted password hash; check_password_hash', 'Werkzeug’s default password hashing uses scrypt with a random salt. Verify with check_password_hash, not by generating a new salted hash and comparing strings.'),
  ('Dummy verification; generic credential failure', 'The project checks a dummy hash for an unknown username to avoid a simple missing-hash shortcut. It returns the same generic 401 outcome, without claiming perfect timing equality.')],
 'Registration validates the fictional password, hashes it and stores only the verifier. Password hashing is intentionally more expensive than ordinary string comparison. '
 'A random salt means the same password can produce different stored strings. That is expected and does not mean verification is broken. '
 'Do not log plaintext, return the hash from /v1/me or store a bearer credential in source code. '
 'Unknown users and incorrect passwords receive the same public failure. The local project does not implement login throttling, MFA, recovery or account lockout. '
 'Those missing operational controls are why this remains a local learning API rather than a ready public account service.',
 'stored=generate_password_hash(password)\nvalid=check_password_hash(stored,password)',
 '''from werkzeug.security import generate_password_hash,check_password_hash
password="fictional-learning-passphrase"
first=generate_password_hash(password)
second=generate_password_hash(password)
print("Different salts:",first!=second)
print("Correct:",check_password_hash(first,password))
print("Wrong:",check_password_hash(first,"fictional-wrong-password"))''',
 'Both verifiers correspond to the same fictional password despite different strings. Verification succeeds only with the correct value.',
 ('generate_password_hash(attempt)==stored_hash', 'check_password_hash(stored_hash,attempt)', 'A fresh random salt prevents meaningful direct string equality.'),
 'Inspect a fictional stored verifier without printing its contents.',
 fixture('from learning_api.database import connect\ndb=connect(app.state.database)\ntry:\n    value=db.execute("SELECT password_hash FROM users WHERE username=?",("asha",)).fetchone()[0]\n    print(value!=PRACTICE_PASSWORD,value.startswith("scrypt:"))\nfinally:db.close()'),
 'Compare public results for an unknown username and a known username with the wrong password.',
 fixture('a=client.post("/v1/token",data={"username":"missing","password":PRACTICE_PASSWORD})\nb=client.post("/v1/token",data={"username":"asha","password":"fictional-wrong-password"})\nprint(a.status_code,b.status_code,a.json()==b.json())'),
 'Store a salted verifier, verify with the matching password API and keep public failures generic without overstating account-security completeness.',
 [('Why can two hashes of one password differ?', 'They use different random salts', 'One must be corrupt', 'The password is stored as JSON', 'Salts deliberately make independently generated verifier strings different.'),
  ('Does this local lesson implement login throttling?', 'No', 'Always', 'Only on phones', 'It explicitly limits its public-deployment claims.')])

lesson(5, '3. JWT claims, signatures and fixed verification policy',
 'Explain what a signed access token proves and what it does not hide.',
 [('JWT; PyJWT; HS256', 'A JWT carries encoded claims plus a signature. PyJWT creates/verifies it. HS256 signs with a shared secret; the verifier fixes the allowed algorithm instead of trusting a token-selected choice.'),
  ('sub; exp; iat; nbf; iss; aud; jti', 'sub identifies the subject; exp expires access; iat records issue time; nbf limits earliest use; iss/aud bind issuer/audience; jti identifies this login for server-side revocation.'),
  ('Signature versus encryption', 'A signed JWT payload is readable to its holder. Signing detects unauthorised changes; it does not make password/private-body claims confidential.')],
 'The server signs public identity metadata using its ignored 32-byte local key. It never puts a password or note body into claims. '
 'Decode only with a fixed algorithm allowlist, the expected issuer/audience and required claims. Reading an unverified payload is not authentication. '
 'The project additionally requires kind=access, valid claim shapes and a live token-session row tied to that user. '
 'The sample inspects verified claim names and policy outcomes without printing a bearer credential or signing key. '
 'A changed signature, expired timestamp or wrong audience must fail closed rather than quietly becoming an anonymous successful request.',
 'jwt.decode(token,key,algorithms=["HS256"],issuer=ISSUER,audience=AUDIENCE,options={"require":["sub","exp","iat","nbf","jti","iss","aud"]})',
 fixture('import jwt\nfrom learning_api import ISSUER,AUDIENCE\nencoded=headers["Authorization"].split(" ",1)[1]\nclaims=jwt.decode(encoded,app.state.key,algorithms=["HS256"],issuer=ISSUER,audience=AUDIENCE)\nprint(sorted(claims))\nprint("Lifetime seconds:",claims["exp"]-claims["iat"])\nprint("Private claims absent:","password" not in claims and "body" not in claims)'),
 'Only policy-approved verification produces these claims. The print shows names and lifetime, not the signed credential itself.',
 ('jwt.decode(token,options={"verify_signature":False})  # trust the result', 'jwt.decode(token,key,algorithms=["HS256"],issuer=ISSUER,audience=AUDIENCE)', 'Unverified decoding does not establish authenticity or intended audience.'),
 'Alter a payload segment without a new signature and show the request is rejected.',
 fixture('token=headers["Authorization"].split(" ",1)[1]\nsegments=token.split(".");segments[1]="eyJzdWIiOiI5OTkifQ"\nr=client.get("/v1/me",headers={"Authorization":"Bearer "+".".join(segments)})\nprint(r.status_code)'),
 'Create an expired token using only this owned fictional fixture key and confirm rejection.',
 fixture('import jwt,time\nfrom learning_api import ISSUER,AUDIENCE\nnow=int(time.time())\nclaims={"sub":"1","iat":now-120,"nbf":now-120,"exp":now-60,"jti":"fictional-expired","iss":ISSUER,"aud":AUDIENCE,"kind":"access"}\nexpired=jwt.encode(claims,app.state.key,algorithm="HS256")\nprint(client.get("/v1/me",headers={"Authorization":"Bearer "+expired}).status_code)'),
 'Verify signature, algorithm, required claims and intended issuer/audience; signed claims are not encrypted private storage.',
 [('Is a signed JWT payload encrypted by default?', 'No', 'Always', 'Only if it has exp', 'Its encoded claims remain readable; the signature protects integrity.'),
  ('Who chooses the accepted JWT algorithm?', 'The verifier’s fixed policy', 'Any untrusted token header', 'The note title', 'An allowlist prevents accepting an unapproved algorithm.')])

lesson(5, '4. Ownership, revocation and browser security boundaries',
 'Revoke one login and explain why CORS is not an access-control system.',
 [('Token-session allowlist; revocation', 'The server stores jti/user/expiry for issued logins and requires that row on every protected request. Logout deletes the current row; a still-signed old token then fails.'),
  ('CORS; CSRF; explicit credentials', 'CORS controls which browser origins can read certain cross-origin responses; it is not authentication. Browser cookies are often sent automatically; this API instead requires an explicitly added bearer header and has no cookie login.')],
 'A signature alone cannot tell whether someone logged out after issuance. This project deliberately keeps a small server-side login record for revocation. '
 'Independent logins have different jti values, so revoking one does not sign out every other valid login. '
 'Ownership is checked after identity and on every member operation, not only when listing notes. '
 'The explorer is served by the same local origin; no permissive CORS middleware is needed. Non-browser clients are not constrained by browser CORS policy anyway. '
 'Bearer handling does not remove XSS risk: injected script could steal a live token. The explorer renders server/schema text with textContent and loads no third-party scripts.',
 'DELETE FROM token_sessions WHERE jti=? AND user_id=?\n# Every protected request also checks this row exists.',
 fixture('other=login(client,"asha")\nprint("Before:",client.get("/v1/me",headers=headers).status_code)\nprint("Logout:",client.post("/v1/logout",headers=headers).status_code)\nprint("Replayed:",client.get("/v1/me",headers=headers).status_code)\nprint("Other login:",client.get("/v1/me",headers=other).status_code)'),
 'Logout revokes the current server record, so replay fails while a separate valid login remains usable.',
 ('# CORS is off, therefore nobody can call the API', '# Require authentication and owner checks regardless of browser policy', 'CORS is not a general server-side permission boundary.'),
 'Verify a revoked token cannot write a note.',
 fixture('client.post("/v1/logout",headers=headers)\nprint(client.post("/v1/notes",headers=headers,json={"title":"Replay","body":"Must fail"}).status_code)'),
 'Confirm the API does not issue a login cookie or allow a credential-free current-user request.',
 fixture('r=client.get("/v1/me",headers=headers)\nprint("set-cookie" in r.headers,client.get("/v1/me").status_code)'),
 'Revocation, ownership, browser-origin policy and script safety solve different problems; implement and test the actual required boundary.',
 [('Does deleting a token’s server record affect its signed bytes?', 'No, but the server rejects its missing login record', 'It decrypts the token', 'It edits the browser history', 'The verifier requires both a valid JWT and a live matching server row.'),
  ('Is CORS a replacement for authentication?', 'No', 'Always', 'Only for REST', 'It is a browser response-access policy, not a general identity control.')])

lesson(5, '5. Test API failures, isolation and local documentation',
 'Prove the project’s guarantees using fictional accounts and disposable state.',
 [('Acceptance suite; failure-path state assertion', 'An acceptance suite follows real operations across layers. After a rejected write, inspect the original resource to prove it remained unchanged.'),
  ('Offline explorer token handling', 'The original explorer fetches /openapi.json and local assets, renders text safely and masks token output. It keeps the bearer field only in memory for this tab; tests use disposable browser profiles.')],
 'A green 200 screenshot cannot prove private account isolation, token expiry, rollback or restart persistence. '
 'Use two fictional accounts, try cross-owner read/update/delete, and inspect the owner’s original note afterward. '
 'Also test malformed input, duplicate usernames, missing/expired/revoked/tampered tokens and sanitised validation errors. '
 'For the explorer, inspect actual local requests, interactive operations, mobile layout and browser console errors. '
 'Do not read a real learner’s token, runtime database or Chrome profile to run these checks; controlled fixtures exercise the same logic.',
 '# request rejected -> original owner reads unchanged record -> assertions pass',
 fixture('ben=login(client,"ben")\nurl="/v1/notes/1"\nbefore=client.get(url,headers=headers).json()\nprint(client.get(url,headers=ben).status_code,client.patch(url,headers=ben,json={"title":"Wrong owner"}).status_code,client.delete(url,headers=ben).status_code)\nafter=client.get(url,headers=headers).json()\nassert before==after\nprint("Owner data unchanged")'),
 'The valid other account receives 404 for all member operations, and an explicit representation comparison proves no accidental change occurred.',
 ('# Test only a happy-path status', '# Test refusal plus the original stored state', 'A failure status alone may miss a side effect performed before returning it.'),
 'Inspect explorer source for local-only schema loading and safe text rendering.',
 fixture('source=client.get("/assets/explorer.js").text\nprint("fetch(\'/openapi.json\')" in source,"textContent" in source,"localStorage" in source)',False),
 'Send a unique short fictional password marker and verify it is absent from the validation response.',
 fixture('marker="x7Q!z"\nr=client.post("/v1/users",json={"username":"new_user","password":marker})\nprint(r.status_code,marker not in r.text)',False),
 'Test the claimed guarantee at the boundary that enforces it, then confirm failures preserve data and avoid secret leakage.',
 [('What confirms a rejected cross-owner write had no effect?', 'The original owner’s data is unchanged', 'Only a screenshot', 'A success-coloured button', 'Stored-state or response-representation assertions prove the write did not occur.'),
  ('Should verification inspect real learner credentials?', 'No', 'Always', 'Only once', 'Disposable fictional accounts provide the required evidence.')])

lesson(5, '6. Milestone: a validated private FastAPI Notes API',
 'Run a complete local API and explain the whole request-to-storage flow.',
 [('Complete local API milestone', 'The supplied project combines typed routes, Pydantic contracts, OpenAPI, full private CRUD, SQLite persistence, yielded dependencies, password hashing, verified JWTs and individual logout revocation.'),
  ('Operational scope; next refactor', 'This is a loopback teaching project, not a public production identity service. Week 40’s roadmap refactors the database layer to SQLAlchemy while preserving the client contract.')],
 'Keep the entire docs/python-week39 folder, including learning_api/static and lesson_support.py. Install requirements once, run python app.py and open the local /docs explorer. '
 'Register a fictional account, request its token, create/read/replace/patch/delete a note and observe each status. The explorer masks token responses and holds the bearer only in this tab. '
 'Create a second account and verify its collection begins empty. Test a note id from the first account and explain why the response is 404. '
 'Stop/restart to see owned runtime persistence, then logout and confirm replay is rejected. Never publish instance/ files or use external service credentials in the exercise. '
 'The project has no refresh tokens, MFA, account recovery, public HTTPS deployment, rate limiting or whole-request byte limit. Do not expose it publicly by merely changing the listen host. '
 'Your milestone is understanding the complete boundary chain: HTTP parsing, model validation, verified identity, owner authorisation, transaction, filtered output and executable tests.',
 'python -m pip install -r requirements.txt\npython app.py\n# http://127.0.0.1:8000/docs',
 fixture('register(client,"asha");headers=login(client,"asha")\nr=client.post("/v1/notes",headers=headers,json={"title":"My FastAPI milestone","body":"Explain every boundary."})\nurl=r.headers["Location"];print("Create/read:",r.status_code,client.get(url,headers=headers).status_code)\nr=client.put(url,headers=headers,json={"title":"Milestone understood","body":"All writable fields","completed":True});print("Replace:",r.status_code,r.json()["completed"])\nr=client.patch(url,headers=headers,json={"completed":False});print("Patch:",r.status_code,r.json()["completed"])\nprint("Delete/read:",client.delete(url,headers=headers).status_code,client.get(url,headers=headers).status_code)\nprint("Logout/replay:",client.post("/v1/logout",headers=headers).status_code,client.get("/v1/me",headers=headers).status_code)',False),
 'This complete fictional flow exercises the actual model, authentication, ownership and database code. No real account or Study Hub progress is touched.',
 ('# Commit instance/signing.key and notes.sqlite with source', '# Publish source only; keep ignored runtime data private', 'A database and signing key are runtime artifacts, not course distribution files.'),
 'Register two accounts and verify both collections start empty.',
 fixture('register(client,"asha");register(client,"ben")\nfor name in ["asha","ben"]:\n    h=login(client,name)\n    print(name,client.get("/v1/notes",headers=h).json()["total"])',False),
 'Verify the project exposes health, generated schema and original local documentation without authentication.',
 fixture('print([client.get(path).status_code for path in ["/health","/openapi.json","/docs"]])',False),
 'A dependable learning API connects clear contracts, verified identity, ownership, durable storage, honest limits and repeatable tests.',
 [('Does async def make blocking SQLite nonblocking?', 'No', 'Always', 'Only with JWT', 'The driver remains synchronous; these routes use def.'),
  ('Does a valid int id prove an owned note exists?', 'No', 'Always', 'If positive', 'Type, existence and authorisation are separate checks.'),
  ('Can the create body supply owner_id?', 'No', 'Always', 'Only for updates', 'Strict writable models forbid it; the server derives ownership.'),
  ('What preserves an explicitly supplied False update?', 'exclude_unset=True', 'if value', 'An empty PATCH', 'It selects supplied fields rather than truthy fields.'),
  ('What body should successful DELETE return here?', 'No body with 204', 'A password hash', 'A JSON success body with 204', '204 has no response content.'),
  ('Does a response model replace owner checks?', 'No', 'Always', 'If owner_id is hidden', 'Field filtering cannot authorise a private resource.'),
  ('Are signed JWT claims encrypted?', 'No', 'Always', 'If they expire', 'Signing protects integrity, not payload confidentiality.'),
  ('Why check a token-session row?', 'To enforce revocation and a live login', 'To store the plaintext password', 'To change CORS', 'A signature alone cannot report a later logout.'),
  ('Should unfamiliar database schemas be reset at startup?', 'No', 'Always', 'Only when empty-looking', 'Preserve existing files and review migrations.'),
  ('What drives the original offline explorer?', 'The local generated OpenAPI schema', 'A required external CDN', 'A copied public credential', 'The app serves the schema and all UI assets locally.'),
  ('Can GitHub Pages execute this Python API?', 'No', 'Always', 'If named app.py', 'It publishes static course/source files; the server runs locally.'),
  ('Does this addition change Study Hub progress storage?', 'No', 'Always', 'Only for JWT', 'It adds lesson data and a separate local learning project.')])
