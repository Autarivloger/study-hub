"""Append only Week36 teaching data after executing every authored snippet."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap

ROOT = Path(__file__).resolve().parents[1]
DAYS = {f"36.{d}": {"parts": []} for d in range(6)}
JOBS = []


def clean(code):
    return textwrap.dedent(code).strip() + "\n"


def sec(t, v=None, **extra):
    return {"t": t, **({"v": v} if v is not None else {}), **extra}


def lesson(day, title, goal, terms, explanation, syntax, example, walkthrough,
           mistake, task, solution, challenge, challenge_code, takeaway, quizzes):
    parts = DAYS[f"36.{day}"]["parts"]
    index = len(parts)
    questions = []
    for i, (q, answer, wrong1, wrong2, why) in enumerate(quizzes):
        correct = (index + i) % 3
        options = [answer, wrong1, wrong2]
        for _ in range(correct):
            options.insert(0, options.pop())
        questions.append({"q": q, "options": options, "correct": correct, "why": why})
    output = sec("out", "")
    build = sec("sol", code=clean(solution), out="", why="Build check: " + takeaway)
    stretch = sec("sol", code=clean(challenge_code), out="", why="Challenge check: " + takeaway)
    parts.append({"title": title, "sections": [
        sec("h", title), sec("key", "Learning objective: " + goal),
        *[sec("new", name, note=note) for name, note in terms],
        sec("p", explanation), sec("syn", syntax, note="Python/HTTP pattern; run in the practice folder containing the supplied mock_api.py fixture."),
        sec("code", clean(example)), output, sec("p", walkthrough),
        sec("mis", wrong=mistake[0], right=mistake[1], why=mistake[2]),
        sec("ex", task, practiceId=f"36.{day}.{index}.build"), build,
        sec("ex", "Mini challenge: " + challenge, practiceId=f"36.{day}.{index}.challenge"), stretch,
        sec("try", q=quizzes[0][0], code="# Predict, then explain before revealing.", a=quizzes[0][1], why=quizzes[0][4]),
        sec("checkpoint", lesson={"id": f"course:36.{day}.{index}", "quiz": questions}), sec("key", takeaway)
    ]})
    JOBS.extend([(clean(example), output), (clean(solution), build), (clean(challenge_code), stretch)])


def demo(body, *, auth=False):
    head = "import requests\nfrom mock_api import DemoAPI, PRACTICE_TOKEN\n"
    head += "with DemoAPI() as base, requests.Session() as session:\n    session.trust_env=False\n"
    if auth:
        head += '    session.headers["Authorization"]="Bearer "+PRACTICE_TOKEN\n'
    return head + textwrap.indent(clean(body),"    ")


lesson(0,"1. Client, server and the request-response cycle",
    "Explain which program asks, which replies and how Python reads a response.",
    [("HTTP; API; client/server", "HTTP is an application protocol for requests and responses. An API defines operations and data contracts. Python is the client; a separate server receives its request and replies."),
     ("requests; Response", "Requests is a Python HTTP client package. session.get sends a GET and returns a Response with status_code, headers and body. response.json parses a JSON body; it does not prove HTTP success."),
     ("DemoAPI; loopback fixture", "Download mock_api.py from docs/python-week36 into your practice folder first. Its DemoAPI context manager starts a fresh fictional API at 127.0.0.1 on a free port and closes it afterward. It requires no internet or real token. Server internals are support code; this week teaches clients.")],
    "Weeks 35 and 36 connect naturally: a database stores facts, while an API offers a documented way for programs to exchange selected facts. "
    "The client sends a method, target, headers and sometimes a body. The server returns a status, headers and sometimes a body. "
    "The first route, /health, returns a small JSON object identifying the practice service. A 200 response means this request succeeded under that route's contract. "
    "Every network example below uses the supplied local fixture. Keep mock_api.py next to your snippet; each example starts fresh state and cleans it up. "
    "trust_env=False keeps this practice session from picking up ambient proxy or .netrc credentials. Corporate proxy environments need deliberate configuration; do not disable certificate verification. "
    "The website itself remains an offline reader. Real internet APIs need network access; loopback practice and saved lesson outputs do not.",
    'response=session.get(base+"/health",timeout=(3.05,10))\nprint(response.status_code,response.json())',
    demo('response=session.get(base+"/health",timeout=(3.05,10))\nprint("Status:",response.status_code)\nprint("Body:",response.json())\nresponse.close()'),
    "DemoAPI supplies the base address. /health is a path on that server. status_code is an integer; json returns a Python dictionary. The code closes the response and session.",
    ('# Treat a browser screenshot as an API contract', '# Read the documented route, method, status and JSON schema', "An API is a program interface with a contract."),
    "GET /health and print only the service name after checking for status 200.",
    demo('with session.get(base+"/health",timeout=(3.05,10)) as response:\n    if response.status_code!=200:\n        raise RuntimeError("Health request failed")\n    print(response.json()["service"])'),
    "Request an unknown route and compare its status with /health without treating the error body as a successful service result.",
    demo('with session.get(base+"/missing",timeout=(3.05,10)) as response:\n    print("Unknown route status:",response.status_code)\nwith session.get(base+"/health",timeout=(3.05,10)) as response:\n    print("Health status:",response.status_code)'),
    "HTTP success, parseable JSON and correct application data are three separate checks.",
    [("Which program initiates the request here?","The Python client","The SQLite table","The quiz button","Requests sends a request to the local server."),
     ("Does response.json prove status 200?","No","Always","Only for dictionaries","An error response can also contain valid JSON.")])

lesson(0,"2. URLs, DNS, ports and HTTPS",
    "Separate the target's scheme, host, port, path and query.",
    [("URL components; DNS; port", "A URL identifies a scheme, host, optional port, path and query. DNS resolves hostnames; a numeric loopback address needs no public hostname lookup. A port selects a listening service."),
     ("HTTPS; TLS; verify", "HTTPS uses TLS to protect the connection to a verified server. Requests verifies certificates by default. HTTP is used only for this local fictional loopback fixture."),
     ("urlsplit; urlencode", "urllib.parse.urlsplit separates URL fields. urlencode encodes query values so spaces, ampersands and other characters remain data rather than changing parameter structure.")],
    "In https://example.org:443/api/books?q=SQL, https is the scheme, example.org the host, 443 the port, /api/books the path and q=SQL the query. "
    "A path is meaningful to a particular service, not a filename you can assume exists on your computer. "
    "A URL fragment after # is client-side information and is not sent as the HTTP request target. Never put tokens in fragments or query strings as a secrecy trick. "
    "DNS, connection establishment, TLS and HTTP occur at different layers; a DNS failure is not a 404 HTTP response. "
    "The example only parses a reserved example URL and prepares encoded text. It makes no external connection.",
    'parts=urlsplit(url)\nquery=urlencode({"q":"Python & SQL"})',
    '''from urllib.parse import urlsplit,urlencode
url="https://example.org:443/api/books?q=SQL#chapter"
parts=urlsplit(url)
print(parts.scheme,parts.hostname,parts.port,parts.path,parts.query,parts.fragment)
print(urlencode({"q":"Python & SQL","language":"日本語"}))''',
    "The ampersand in the search value becomes%26; it is not a second parameter separator. Fragment chapter is separate from path/query.",
    ('url=base+"/echo?q="+term', 'session.get(base+"/echo",params={"q":term},timeout=(3.05,10))', "Pass values through an encoder instead of assembling URL syntax."),
    "Parse https://example.org/items?page=2and show host, path and query without making a request.",
    '''from urllib.parse import urlsplit
p=urlsplit("https://example.org/items?page=2")
print(p.hostname,p.path,p.query)''',
    "Encode the two values A&B and a/b as query data and then decode them again.",
    '''from urllib.parse import urlencode,parse_qs
encoded=urlencode({"q":"A&B","path":"a/b"})
print(encoded)
print(parse_qs(encoded))''',
    "Know the destination and encoded values. A correct URL is still not proof of a correct response.",
    [("Which layer commonly resolves a hostname?","DNS","GROUP BY","JSON decoding","DNS maps names to network addresses."),
     ("Should verify=False be the normal certificate fix?","No","Always","Only for passwords","Fix trust/configuration rather than bypassing verification.")])

lesson(0,"3. HTTP methods express intended operations",
    "Distinguish reading, creating, replacing and deleting a resource.",
    [("GET; POST; PUT; DELETE; PATCH", "GET retrieves a representation; POST submits an operation, often creation; PUT replaces the target representation under its contract; DELETE removes it; PATCH applies a documented partial change."),
     ("Safe versus idempotent", "A safe method is intended to be read-only in effect. Idempotency concerns the same intended server effect after repeated identical requests, not identical response codes. POST is not generally idempotent."),
     ("Request.prepare", "requests.Request(...).prepare() builds the outgoing method, headers, URL and body without sending anything. It lets us inspect fictional requests safely.")],
    "Read an endpoint's documentation rather than guessing operations from its path. The same /tasks collection may support GET and POST with different meanings. "
    "PUT and PATCH are not synonyms: the server contract specifies replacement versus partial update. "
    "DELETE may first return204then404on repetition while still leaving the same final absence; idempotent does not mean identical status. "
    "A timed-out POST might already have created something. Automatically resending it can create a duplicate unless the provider documents an idempotency mechanism. "
    "We prepare requests below without sending them. Actual write-method drills later target only the disposable local API.",
    'request=requests.Request("POST",url,json={"title":"Read docs"}).prepare()',
    '''import requests
for method in ["GET","POST","PUT","DELETE"]:
    options={"json":{"title":"Read docs"}} if method in {"POST","PUT"} else {}
    req=requests.Request(method,"https://example.org/tasks",**options).prepare()
    print(req.method,"has body:",req.body is not None)
''',
    "The prepared JSON writes have bodies; GET and DELETE here do not. No live service is contacted or changed.",
    ('# Retry every timed-out POST automatically', '# Check the endpoint idempotency contract before repeating a write', "A lost response does not prove a lost operation."),
    "Prepare a POST with JSON and inspect its Content-Type and decoded body without sending it.",
    '''import requests,json
req=requests.Request("POST","https://example.org/tasks",json={"title":"Practice"}).prepare()
print(req.headers["Content-Type"],json.loads(req.body))''',
    "Prepare a GET with a search parameter and confirm its body is absent.",
    '''import requests
from urllib.parse import urlsplit
req=requests.Request("GET","https://example.org/tasks",params={"q":"SQL basics"}).prepare()
print(req.method,urlsplit(req.url).query,req.body is None)''',
    "Methods have semantics; retry safety follows the operation's contract, not just the fact that a client saw an error.",
    [("Does idempotent mean identical response status?","No","Always","Only for DELETE","Repeated calls can have different responses but the same intended final effect."),
     ("May a timed-out POST already have succeeded?","Yes","Never","Only when using pandas","The server can finish even if the client loses the response.")])

lesson(0,"4. Status, headers and body are different evidence",
    "Check success, representation type and payload separately.",
    [("Status families; Content-Type; Accept", "2xx indicates success,3xx redirection,4xx request/access problems,5xx server problems. Content-Type describes the body; Accept requests a preferred representation."),
     ("raise_for_status; response truthiness", "raise_for_status raises HTTPError for4xx/5xx, not all3xx. A Response's truth value is false for error statuses, so use response is not None to test existence.")],
    "A response can contain valid JSON explaining a failure. Parsing that dictionary does not make it a successful data result. "
    "Check the status expected by the endpoint, the content type when relevant, and the application's payload shape. "
    "Accept asks for JSON; it cannot force a server to comply. Header names are case-insensitive in Requests. "
    "A 302 is a redirect, not a JSON success. Our later client disables automatic redirects for authenticated collection and stops for review. "
    "Do not print response bodies or Authorization while debugging real credentials. A status and a sanitised operation name usually provide a useful first diagnostic.",
    'if response.status_code==200:\n    payload=response.json()\nelse:\n    # Handle the documented failure.',
    demo('for path in ["/health","/missing"]:\n    with session.get(base+path,timeout=(3.05,10)) as response:\n        print(path,response.status_code,response.headers["Content-Type"].split(";")[0])\n        try:\n            response.raise_for_status()\n            print("HTTP success checked")\n        except requests.HTTPError:\n            print("HTTP failure; do not treat as data")'),
    "The missing endpoint returns a JSON error with 404. Its body format and failure status describe separate facts.",
    ('if response:  # assume this means a response exists', 'if response is not None:  # existence, not success', "Error Response objects can be false in boolean context."),
    "Send Accept:application/json and print what the local echo endpoint received.",
    demo('with session.get(base+"/echo",headers={"Accept":"application/json"},timeout=(3.05,10)) as response:\n    print(response.json()["accept"])'),
    "Request a redirect with allow_redirects=False and print status and Location only.",
    demo('with session.get(base+"/redirect",allow_redirects=False,timeout=(3.05,10)) as response:\n    print(response.status_code,response.headers["Location"])'),
    "Success status, media type and schema validation answer different questions. Check each deliberately.",
    [("Does raise_for_status reject every redirect?","No","Always","Only302","It raises for4xx/5xx; handle3xx separately when required."),
     ("Can a 404 response have valid JSON?","Yes","Never","Only offline","Error details are often JSON too.")])

lesson(0,"5. Inspect a request without exposing a credential",
    "Connect browser Network observations with a Python prepared request.",
    [("Developer Tools Network panel; request target", "The Network panel shows method, path, status, timing and headers. Inspect only your own authorised traffic; do not copy credential-bearing requests into public notes."),
     ("PreparedRequest versus Response", "response.request contains the PreparedRequest actually sent. A prepared request alone has no server result; a Response records what returned.")],
    "For browser practice, run python mock_api.py in the supplied folder. It prints a loopback URL. Open that URL plus /health, open Developer Tools, choose Network and reload. "
    "Select /health and locate method GET, status 200and JSON response. The random port changes between runs; that is expected. "
    "You can also inspect the Python response.request method and parsed path. Do not dump all headers once authentication is involved. "
    "Browser JavaScript obeys browser restrictions such as CORS, while a Python HTTP client is a different environment. A browser failure does not automatically establish the API is down. "
    "The local fixture is an explicit helper; we do not alter the Study Hub browser page or launch any real authenticated request to perform this exercise.",
    'sent=response.request\nprint(sent.method,urlsplit(sent.url).path)',
    demo('from urllib.parse import urlsplit\nwith session.get(base+"/echo",params={"q":"notes & code"},timeout=(3.05,10)) as response:\n    sent=response.request\n    parsed=urlsplit(sent.url)\n    print("Sent:",sent.method,parsed.path,parsed.query)\n    print("Received:",response.status_code)'),
    "The query is encoded in the sent URL. The response status belongs to the returned response, not to the prepared request object.",
    ('print(dict(response.request.headers))  # may include Authorization', 'print(response.request.method,urlsplit(response.request.url).path)', "Inspect useful request structure without dumping credentials."),
    "Inspect a local /health request's method/path and returned JSON keys.",
    demo('from urllib.parse import urlsplit\nwith session.get(base+"/health",timeout=(3.05,10)) as response:\n    print(response.request.method,urlsplit(response.request.url).path)\n    print(sorted(response.json()))'),
    "Prepare an unsent request and prove it has a method but no status_code field.",
    '''import requests
req=requests.Request("GET","https://example.org/health").prepare()
print(req.method,hasattr(req,"status_code"))''',
    "Inspect the right object and the right layer. A useful diagnostic need not reveal headers or personal data.",
    [("Where is the server status stored?","Response","PreparedRequest alone","The DNS hostname","A prepared request has not received a server reply."),
     ("Should you publish a copied authenticated curl request unchanged?","No","Always","If the URL is short","It may contain a bearer token or cookies.")])

lesson(1,"1. GET with encoded params and repeated values",
    "Send search values without accidentally creating new query parameters.",
    [("params; repeated query keys", "Requests params encodes a mapping. A list value sends the same key multiple times; a None value is omitted. The server's contract defines how repeated values are interpreted.")],
    "Let Requests encode the query instead of joining strings. A search value containing & must remain one value, not introduce another parameter. "
    "The local /echo route returns parsed query values as lists, letting you compare what you intended with what arrived. "
    "A query string is visible in request logs and URLs; do not put a bearer credential in it. "
    "List parameters can represent repeated filters, but another API may expect commas or a different structure. Read its contract. "
    "Always supply a timeout. A GET is generally safe to repeat, but retries still need limits and provider-specific rules.",
    'session.get(base+"/echo",params={"q":"Python & SQL","tag":["http","json"]},timeout=(3.05,10))',
    demo('params={"q":"Python & SQL","tag":["http","json"],"skip":None}\nwith session.get(base+"/echo",params=params,timeout=(3.05,10)) as response:\n    response.raise_for_status()\n    print(response.json()["query"])'),
    "q stays one value, tag appears twice and skip is absent. Encoding preserves data structure; it does not decide business meaning.",
    ('url=base+"/echo?q="+term', 'session.get(base+"/echo",params={"q":term},timeout=(3.05,10))', "The encoder preserves separators inside values."),
    "Send Japanese text and a space in q; prove the server receives the original string.",
    demo('term="日本語 basics"\nwith session.get(base+"/echo",params={"q":term},timeout=(3.05,10)) as response:\n    print(response.json()["query"]["q"][0]==term)'),
    "Send min=10and active=True; inspect their string representations on the server rather than assuming JSON types in a URL.",
    demo('with session.get(base+"/echo",params={"min":10,"active":True},timeout=(3.05,10)) as response:\n    print(response.json()["query"])'),
    "Query parameters are encoded strings interpreted by an endpoint contract, not automatically typed JSON.",
    [("What does params do with a None value?","Omits that parameter","Sends JSON null","Creates a header","This is Requests' query encoding behaviour."),
     ("Who defines the meaning of repeated keys?","The API contract","Python's list type alone","SQLite","Encoding does not define the provider's filter semantics.")])

lesson(1,"2. POST JSON and inspect a created resource",
    "Create one fictional task and verify the expected201response.",
    [("json= versus data=", "json=dict serialises JSON and sets the JSON Content-Type. data=dict normally encodes a form. Choose the endpoint's required representation, not whichever happens to run."),
     ("201 Created; Location", "201reports creation. Location can identify the created resource; its meaning is part of the endpoint contract. It is not automatic permission to send credentials to any URL.")],
    "Our /tasks route accepts a JSON object with a nonempty title. It returns 201, a generated id and a relative Location. "
    "The json argument handles serialisation; do not double-encode a dictionary into a JSON string unless the contract actually expects a string. "
    "The example verifies201before using the id. A200or204response would be a different contract. "
    "Writing here changes only fresh loopback fixture state. It never creates an issue in the user's GitHub repository. "
    "Do not automatically retry this POST after a timeout. A response can be lost after creation, leaving you uncertain whether the write happened.",
    'response=session.post(base+"/tasks",json={"title":"Read API docs"},timeout=(3.05,10))',
    demo('with session.post(base+"/tasks",json={"title":"Read API docs"},timeout=(3.05,10)) as response:\n    if response.status_code!=201:\n        raise RuntimeError("Creation failed")\n    print(response.status_code,response.json(),response.headers["Location"])'),
    "id 1 belongs to this newly created fictional task; every independent snippet starts fresh task state.",
    ('session.post(url,data={"title":"Read docs"})  # JSON endpoint', 'session.post(url,json={"title":"Read docs"},timeout=(3.05,10))', "Form encoding and JSON are different representations."),
    "Create a task with an apostrophe in its title and verify the returned text is unchanged.",
    demo('title="A reader\'s notes"\nwith session.post(base+"/tasks",json={"title":title},timeout=(3.05,10)) as response:\n    print(response.status_code,response.json()["title"]==title)'),
    "Send an empty title and check the400failure without treating its error JSON as a task.",
    demo('with session.post(base+"/tasks",json={"title":""},timeout=(3.05,10)) as response:\n    print("Rejected:",response.status_code==400)\nwith session.get(base+"/tasks",timeout=(3.05,10)) as response:\n    print("Tasks retained:",len(response.json()))'),
    "Use the documented representation and expected creation status; verify before using the new resource.",
    [("Which argument sends a JSON object?","json=","data=dict always","params=","json performs JSON serialisation."),
     ("Does POST 201mean this example changed GitHub?","No","Always","Only with an id","Only the disposable loopback service is written.")])

lesson(1,"3. PUT replacement and DELETE with no response body",
    "Update and remove a fictional resource while respecting response contracts.",
    [("PUT replacement;204 No Content", "PUT sends the intended replacement representation under this route's contract.204means no response body; calling json on it is an error, not an empty dictionary.")],
    "Create a task first, replace its title with PUT and then delete it. The path includes the generated numeric id. "
    "The fixture's entire task representation is id and title; replacing title supplies all editable fields. A richer provider may require more fields. "
    "DELETE returns 204 without JSON. Check the status and absence of body rather than calling json unconditionally. "
    "A repeat DELETE returns 404 because the task is already absent. The final resource effect still demonstrates idempotency. "
    "PATCH has separate partial-update semantics and is not implemented by this fixture; do not invent support just because Requests has a patch function.",
    'session.put(base+"/tasks/1",json={"title":"Revised"},timeout=(3.05,10))\n# For DELETE 204, do not call response.json().',
    demo('with session.post(base+"/tasks",json={"title":"Draft"},timeout=(3.05,10)) as response:\n    task_id=response.json()["id"]\nwith session.put(base+"/tasks/"+str(task_id),json={"title":"Revised"},timeout=(3.05,10)) as response:\n    print("PUT:",response.status_code,response.json())\nwith session.delete(base+"/tasks/"+str(task_id),timeout=(3.05,10)) as response:\n    print("DELETE:",response.status_code,"Empty:",not response.content)\nwith session.get(base+"/tasks",timeout=(3.05,10)) as response:\n    print("Remaining:",response.json())'),
    "PUT changes the existing task, DELETE removes it and GET verifies an empty collection. The 204 body is deliberately empty.",
    ('payload=delete_response.json()  # assume every response is JSON', 'if delete_response.status_code==204:\n    pass  # expected no body', "No-content success and empty JSON are not the same."),
    "Create then delete one task; attempt the same delete again and compare statuses.",
    demo('with session.post(base+"/tasks",json={"title":"Temporary"},timeout=(3.05,10)) as response:\n    task_id=response.json()["id"]\nfor _ in range(2):\n    with session.delete(base+"/tasks/"+str(task_id),timeout=(3.05,10)) as response:\n        print(response.status_code)'),
    "PUT to nonexistent task99and verify404rather than assuming this API creates it.",
    demo('with session.put(base+"/tasks/99",json={"title":"Unknown"},timeout=(3.05,10)) as response:\n    print(response.status_code)'),
    "Do not infer write semantics from a method name alone. Verify the provider's status/body contract.",
    [("Should a204DELETE body be parsed as JSON?","No","Always","Only when empty","204has no response content."),
     ("Must repeated idempotent DELETE return the same status?","No","Always","Only locally","Final intended state can agree while status changes.")])

lesson(1,"4. Sessions reuse configuration and connections",
    "Scope shared headers and close the session after its work.",
    [("requests.Session; connection pooling", "A Session keeps configuration and can reuse underlying connections to the same service. Use a context manager or close it when finished; fully consume/close responses so connections can be released."),
     ("Per-request overrides; trust_env", "Session headers supply defaults; an individual call can override them. trust_env=False prevents ambient environment proxy/.netrc discovery in this controlled drill; configure production proxies deliberately.")],
    "An API client usually makes several calls to one service. A Session avoids repeating common headers and can reuse network connections when server/protocol conditions permit. "
    "Set Accept and a descriptive User-Agent once. The example overrides Accept on a second call without changing the session's default. "
    "This fixture uses a simple HTTP server, so do not interpret the example as a measured connection-pooling benchmark. The configuration behaviour is what it demonstrates. "
    "Avoid sharing one authenticated session across unrelated origins. Our final collector fixes its allowed origin and refuses automatic redirects. "
    "Session closure and HTTP result validation are different responsibilities; a with block does not mean an error status became successful.",
    'with requests.Session() as session:\n    session.headers.update({"Accept":"application/json","User-Agent":"StudyHub-Practice/1.0"})',
    demo('session.headers.update({"Accept":"application/json","User-Agent":"StudyHub-Practice/1.0"})\nwith session.get(base+"/echo",timeout=(3.05,10)) as response:\n    body=response.json();print(body["accept"],body["user_agent"])\nwith session.get(base+"/echo",headers={"Accept":"text/plain"},timeout=(3.05,10)) as response:\n    print("Override received:",response.json()["accept"])\nprint("Default retained:",session.headers["Accept"])'),
    "The second request overrides one header only for that request. The session default remains application/json.",
    ('# Reuse one bearer-bearing session for arbitrary websites', '# Keep authenticated sessions scoped to the approved API origin', "Common configuration should not spread credentials across unrelated services."),
    "Set User-Agent once and verify both requests receive the same value.",
    demo('session.headers["User-Agent"]="My-Learning-Client/1.0"\nfor _ in range(2):\n    with session.get(base+"/echo",timeout=(3.05,10)) as response:\n        print(response.json()["user_agent"])'),
    "Prepare a request through the session and inspect only its nonsecret Accept default.",
    demo('session.headers["Accept"]="application/json"\nprepared=session.prepare_request(requests.Request("GET",base+"/health"))\nprint(prepared.headers["Accept"])'),
    "Reuse intentional configuration, scope sessions carefully and close resources explicitly.",
    [("Does a Session guarantee every server keeps a connection alive?","No","Always","Only for GET","Pooling depends on server/protocol and response lifecycle."),
     ("Does a one-request header override change the session default?","No","Always","Only for Accept","The per-call value applies to that request.")])

lesson(1,"5. Timeouts bound waiting stages, not the whole workflow",
    "Set connect/read timeouts and handle a request that never returns promptly.",
    [("Connect/read timeout tuple; Timeout", "timeout=(connect_seconds,read_seconds) controls connection establishment and socket read waiting. It is not a strict total download or workflow deadline."),
     ("ConnectionError; unknown write outcome", "ConnectionError covers connection-level failures. Timeout/connection errors do not universally establish whether a write was processed; retries must consider operation semantics.")],
    "Requests does not choose a safe timeout for you by default. Every lesson call supplies one. "
    "A connect timeout and read timeout govern different stages. A response that continues sending bytes can take longer overall than the read timeout value. "
    "The fixture's /slow endpoint waits briefly before responding; a 0.01-second read timeout demonstrates the exception without a long wait. "
    "Catch the expected Timeout and report it clearly. Later GET retry policy uses bounded attempts and waiting; it is not an infinite loop. "
    "For a strict end-to-end deadline you need more control than a Requests timeout tuple, including limits across retries, body processing and upstream stages.",
    'try:\n    response=session.get(url,timeout=(1,0.01))\nexcept requests.Timeout:\n    # Report or apply a bounded safe-read retry policy.',
    demo('try:\n    with session.get(base+"/slow",timeout=(1,0.01)) as response:\n        response.raise_for_status()\nexcept requests.Timeout:\n    print("Read timeout handled")'),
    "This is a deliberately slow local read. The exception is caught as expected, rather than leaving the learner waiting indefinitely.",
    ('session.get(url)  # no timeout', 'session.get(url,timeout=(3.05,10))', "Make waiting behaviour explicit on every path."),
    "Use a normal timeout for /health and print success only after validation.",
    demo('try:\n    with session.get(base+"/health",timeout=(1,1)) as response:\n        response.raise_for_status();print("Health checked")\nexcept requests.Timeout:\n    print("Health check timed out")'),
    "Classify a synthetic Timeout versus ConnectionError without making an external request.",
    '''import requests
for error in [requests.Timeout(),requests.ConnectionError()]:
    if isinstance(error,requests.Timeout):
        print("Timed out: stage wait exceeded")
    else:
        print("Connection failed: inspect network/configuration")''',
    "Always set timeouts, and do not confuse stage limits with a whole-operation deadline.",
    [("Is timeout=(3,10)a strict13-second workflow deadline?","No","Always","Only for JSON","DNS/address attempts, repeated reads, retries and processing complicate total duration."),
     ("Does a POST timeout prove no creation happened?","No","Always","Only with JSON","The server may have processed it before the client timed out.")])

lesson(1,"6. Bound a downloaded body and close the response",
    "Use streaming for a declared small response instead of trusting Content-Length alone.",
    [("stream=True; iter_content; byte budget", "Streaming exposes chunks as they arrive. Count actual received/decompressed bytes and stop when a chosen limit is exceeded; Content-Length alone is not a complete bound."),
     ("Encoding versus JSON shape", "Bytes need decoding under a representation contract. Successful decoding still does not prove that required fields and types are valid.")],
    "The health response is tiny, but the same pattern can protect a file-transfer task from an unexpectedly large body. "
    "Open the response in a with block, validate status and accumulate chunks only while a declared budget remains. "
    "This demonstrator uses a 1 KiB body limit. Choose realistic limits for the documented endpoint rather than applying the same number blindly. "
    "Streaming read timeouts still are not a complete total-duration guarantee. Requests can also expose connection exceptions during streamed consumption. "
    "The final collector is bounded by attempts, wait budget, pages and items; its JSON parsing does not claim a hard byte-size or overall deadline guarantee. Production large-response clients should extend this bounded-body pattern.",
    'with session.get(url,stream=True,timeout=(3.05,10)) as response:\n    for chunk in response.iter_content(256):\n        # Count bytes before retaining more.',
    demo('import json\nbody=bytearray()\nwith session.get(base+"/health",stream=True,timeout=(3.05,10)) as response:\n    response.raise_for_status()\n    for chunk in response.iter_content(16):\n        if len(body)+len(chunk)>1024:\n            raise ValueError("Body budget exceeded")\n        body.extend(chunk)\nprint(json.loads(body.decode("utf-8"))["ok"])'),
    "The code validates actual retained byte count, decodes UTF-8 and then parses JSON. It does not assume an advertised body length is authoritative.",
    ('# Trust a missing or incorrect Content-Length as the only bound', '# Count actual body bytes while reading and stop at the chosen limit', "A response's framing metadata is not the entire resource policy."),
    "Repeat the bounded-body drill with a deliberately tiny 1-byte budget and handle rejection.",
    demo('try:\n    used=0\n    with session.get(base+"/health",stream=True,timeout=(3.05,10)) as response:\n        response.raise_for_status()\n        for chunk in response.iter_content(16):\n            used+=len(chunk)\n            if used>1:raise ValueError("Too large for chosen budget")\nexcept ValueError:\n    print("Body budget refusal handled")'),
    "Parse known UTF-8 JSON bytes and validate that ok is a real boolean rather than the string true.",
    '''import json
payload=json.loads(b'{"ok":true}')
print(type(payload["ok"]) is bool,payload["ok"])''',
    "Bound work where needed, close responses on success and failure, and state what a resource policy does not guarantee.",
    [("Is Content-Length alone an adequate retained-byte limit?","No","Always","Only when absent","Count actual received/decompressed body bytes."),
     ("Does the project claim a strict total network deadline?","No","Always","Only for GitHub","Its documented limits concern stages, attempts, waits, pages and items.")])

lesson(2,"1. Authentication, authorisation and credential scope",
    "Explain who a credential represents and which actions it permits.",
    [("Authentication; authorisation", "Authentication establishes an identity or credential context; authorisation decides allowed resources/actions.401and 403 often signal different failures, but read the provider's documented meanings."),
     ("API key; bearer token; OAuth", "An API key is a provider-defined credential. A bearer token grants its holder the permitted access. OAuth is an authorisation framework for obtaining scoped access; pasting a token alone is not an OAuth implementation.")],
    "A credential is not a public identifier such as a repository name. Anyone holding a bearer token can use its allowed capabilities while it remains valid. "
    "Our fixture accepts the public value practice-only-token. It is intentionally not a real secret and grants access only to fictional loopback data. "
    "The final optional GitHub run uses a token supplied locally by the learner. We never need to see, print or store it in lesson data. "
    "Use the least privilege needed for the endpoint and do not request write access for a read-only collector. Public GitHub reads can also work unauthenticated within different limits; the authenticated exercise is an explicit learner option. "
    "OAuth involves provider-controlled authorisation and token issuance; this week explains roles without building a pretend login protocol.",
    'headers={"Authorization":"Bearer "+token}\n# Credential issuance and permissions come from the provider.',
    demo('with session.get(base+"/items",timeout=(3.05,10)) as response:\n    print("Without practice credential:",response.status_code)\nsession.headers["Authorization"]="Bearer "+PRACTICE_TOKEN\nwith session.get(base+"/items",timeout=(3.05,10)) as response:\n    print("With practice credential:",response.status_code,len(response.json()["items"]))'),
    "The first call is 401; the fictional credential grants this fixture's read access. Only a first page is returned; authentication is not pagination.",
    ('# Request broad write permissions for a read-only report', '# Match credential scope to the documented read operation', "Access should match the required capability."),
    "Send an intentionally wrong fictional bearer value and verify401without printing it.",
    demo('with session.get(base+"/items",headers={"Authorization":"Bearer wrong-practice-value"},timeout=(3.05,10)) as response:\n    print("Credential rejected:",response.status_code==401)'),
    "Authenticate to the fixture and print only item ids, not the request headers.",
    demo('with session.get(base+"/items",timeout=(3.05,10)) as response:\n    response.raise_for_status();print([row["id"] for row in response.json()["items"]])',auth=True),
    "A token's identity, permissions and destination must be deliberate. Never treat a public repository id as a secret token.",
    [("Is pasting a token a complete OAuth implementation?","No","Always","If it starts with Bearer","OAuth includes provider authorisation and issuance flows."),
     ("Should the read-only collector request unnecessary write access?","No","Always","Only for public repositories","Match permissions to the endpoint's read requirements.")])

lesson(2,"2. Send a bearer header only to the intended service",
    "Keep credentials out of URLs and reject surprising redirects.",
    [("Authorization header; origin", "A bearer credential belongs in the provider's documented header, not the query. An origin combines scheme, host and port; an authenticated client should stay scoped to its approved destination."),
     ("allow_redirects=False", "Disabling automatic redirects lets the client inspect3xxrather than silently moving an authenticated operation. Requests has redirect protections, but an explicit fixed-origin collector has a narrower contract.")],
    "Bearer values belong to the intended API over HTTPS for real internet traffic. The fixture uses HTTP only on numeric loopback with a fake token. "
    "Do not print complete prepared request headers or share copied authenticated commands. URLs are commonly recorded and should not contain credentials. "
    "Our collector permits the exact GitHub HTTPS origin or the numeric loopback practice origin, fixes relative endpoint paths and stops on redirects. "
    "This narrow contract avoids turning a pagination link into permission to contact an arbitrary host. "
    "TLS verification remains enabled; a token does not replace server identity verification.",
    'session.headers["Authorization"]="Bearer "+token\nresponse=session.get(url,allow_redirects=False,timeout=(3.05,10))',
    demo('from urllib.parse import urlsplit,parse_qs\nsession.headers["Authorization"]="Bearer "+PRACTICE_TOKEN\nwith session.get(base+"/items",allow_redirects=False,timeout=(3.05,10)) as response:\n    print("Status:",response.status_code)\n    print("Token in query:", "token" in parse_qs(urlsplit(response.request.url).query))\nwith session.get(base+"/redirect",allow_redirects=False,timeout=(3.05,10)) as response:\n    print("Redirect stopped:",300<=response.status_code<400)'),
    "The request URL has no token parameter. The302is observed rather than followed. A local fake credential is never a template for sending real tokens over public HTTP.",
    ('params={"token":token}', 'headers={"Authorization":"Bearer "+token}', "Follow the provider's header contract and avoid credential-bearing URLs."),
    "Prepare a fictional authenticated request and print only whether the header exists, never its value.",
    '''import requests
req=requests.Request("GET","https://example.org/items",headers={"Authorization":"Bearer practice-only-token"}).prepare()
print("Has credential header:","Authorization" in req.headers)
print("URL has no token:","token" not in req.url)''',
    "Parse two URLs and show that changing a port changes the origin even when the host is the same.",
    '''from urllib.parse import urlsplit
def origin(url):
    p=urlsplit(url);return p.scheme,p.hostname,p.port or (443 if p.scheme=="https" else 80)
print(origin("https://example.org:443/items")==origin("https://example.org:8443/items"))''',
    "Bind credential use to a verified intended origin and inspect redirects before trusting a new destination.",
    [("Where should a documented bearer credential be sent?","Authorization header","A public URL query","A repository title","Use the provider's credential header contract."),
     ("Does the same hostname but a new port always mean the same origin?","No","Always","Only for HTTPS","Scheme, host and port define an origin.")])

lesson(2,"3. Environment variables without printing a token",
    "Obtain configuration at runtime and fail clearly when it is absent.",
    [("Environment variable; os.environ.get", "An environment variable is process configuration, not encrypted storage. Read it only in the operation needing it; never print the value or bake it into public HTML."),
     ("Missing-credential boundary", "Check presence/format before sending a live authenticated request. Give a setup message that names the variable, not its content.")],
    "A program can read STUDYHUB_API_TOKEN when the learner explicitly selects live mode. The offline mock mode never needs that variable. "
    "The following executable example uses an isolated dictionary representing configuration, not the real machine's environment. No real credential is inspected while generating these lessons. "
    "In the actual CLI, os.environ.get supplies the value and the fixed-origin client receives it. Logs, reports and database files never receive it. "
    "Environment variables can still be exposed by process tooling or careless logging; they are a separation-of-configuration technique, not a promise of perfect secrecy. "
    "Do not paste an actual token into chat, screenshots or code. If a credential was published, hiding the current line does not revoke the leaked value; revoke/rotate it through its provider.",
    'token=os.environ.get("STUDYHUB_API_TOKEN","")\nif not token:\n    raise ValueError("Set STUDYHUB_API_TOKEN locally")',
    '''def require_token(configuration):
    token=configuration.get("STUDYHUB_API_TOKEN","")
    if not token:
        raise ValueError("Set STUDYHUB_API_TOKEN locally")
    return token
fictional={"STUDYHUB_API_TOKEN":"practice-only-token"}
token=require_token(fictional)
print("Credential present:",bool(token))
try:
    require_token({})
except ValueError as error:
    print(str(error))''',
    "Only presence and the variable's name are printed. The sample token is fictional and comes from the example dictionary.",
    ('print("Using token:",token)', 'print("Credential configured:",bool(token))', "Debug output must not disclose the credential value."),
    "Write a configuration check that refuses empty credentials without returning a successful client result.",
    '''def configured(value):
    if not value:raise ValueError("Local credential required")
    return True
for value in ["", "practice-only-token"]:
    try:print(configured(value))
    except ValueError:print("Setup required")''',
    "Verify that a deliberately sanitised error contains no fictional bearer value.",
    '''token="practice-only-token"
message="Authentication failed; check local configuration"
print(token not in message)''',
    "Load secrets only when needed; report presence or a setup action, never the value.",
    [("Are environment variables encrypted by definition?","No","Always","Only on Windows","They are configuration and can still be disclosed."),
     ("Does deleting a leaked token line revoke the credential?","No","Always","If the repository is public","Revocation/rotation must occur with the provider.")])

lesson(2,"4. A local .env file is configuration, not public lesson data",
    "Load an ignored local file without overriding deliberate process configuration.",
    [("python-dotenv; dotenv_values; load_dotenv", "python-dotenv reads .env syntax. dotenv_values can parse a supplied stream into a dict without modifying process environment. load_dotenv loads a chosen local file; override=False preserves existing environment values."),
     (".gitignore; .env.example", "Ignore .env before adding credentials. A public .env.example contains variable names/empty placeholders only. Ignoring a file does not remove a secret already committed to history.")],
    "The project's folder includes a scoped .gitignore and an empty .env.example. A learner can create .env locally in that folder for the optional live run. "
    "The CLI chooses .env beside collector.py instead of searching arbitrary directories, and loads it only for --github. Existing environment configuration takes precedence. "
    "The executable example parses a fictional string with dotenv_values and never opens the user's .env or prints its contents. "
    "Keep backups and screenshots from disclosing local configuration too. No token belongs in a report or exported SQLite table. "
    "If a secret has already been committed, an ignore rule is insufficient: revoke it and assess repository history separately. This week adds only a blank template and fictional fixture values.",
    'load_dotenv(Path(__file__).with_name(".env"),override=False)\n# .env is ignored; .env.example has no real value.',
    '''import io
from dotenv import dotenv_values
settings=dotenv_values(stream=io.StringIO("STUDYHUB_API_TOKEN=practice-only-token\\n"))
print("Variable found:","STUDYHUB_API_TOKEN" in settings)
print("Nonempty value:",bool(settings["STUDYHUB_API_TOKEN"]))''',
    "The parser handles the supplied fake stream. It neither reads nor changes actual environment credentials.",
    ('# Commit .env and assume hiding the filename makes it private', '# Ignore .env first; publish only an empty .env.example', "Public source files are readable; configuration must stay local."),
    "Parse an empty placeholder template and verify it is not a usable credential.",
    '''import io
from dotenv import dotenv_values
settings=dotenv_values(stream=io.StringIO("STUDYHUB_API_TOKEN=\\n"))
print("Needs local setup:",not settings["STUDYHUB_API_TOKEN"])''',
    "Simulate environment precedence without touching os.environ: existing configuration should win over a file value.",
    '''file_config={"STUDYHUB_API_TOKEN":"practice-file-value"}
process_config={"STUDYHUB_API_TOKEN":"practice-process-value"}
effective={**file_config,**process_config}
print("Process setting retained:",effective["STUDYHUB_API_TOKEN"]==process_config["STUDYHUB_API_TOKEN"])''',
    "Keep real configuration local and untracked; a blank example documents names, not secret values.",
    [("Does .gitignore erase a previously committed secret?","No","Always","Only for .env","History and credential validity require separate action."),
     ("With override=False, which existing setting wins?","Process environment","Always the .env file","The report title","Explicit process configuration is preserved.")])

lesson(2,"5. Read provider documentation before the live call",
    "Map a real endpoint's auth, data shape, pagination and limits into a client contract.",
    [("GitHub repository issues endpoint", "GET /repos/{owner}/{repo}/issues returns both issue and pull-request records. The pull_request field identifies PR entries; the mixed count must not be labelled issue-only."),
     ("Provider version/permissions/rate headers", "Review the provider's current endpoint, authentication, accepted headers, pagination and rate-limit documentation. Quotas and permissions are external contracts, not timeless constants to hard-code.")],
    "Our optional real endpoint lists public repository issue-like records. The collector deliberately preserves kind=issue or kind=pull_request. "
    "It requests state=all, creation-time ascending order and pages of100, then follows a validated next-page hint. The response's id is the stable provider id, not the same concept as a repository-local number. "
    "Before a real run, read GitHub's endpoint and rate-limit documentation and choose an appropriate local read credential. We do not request your token or invoke live authentication while authoring. "
    "The local fixture mirrors the relevant fields and includes one fictional pull_request record so the analysis can prove it does not silently mix labels. "
    "Public APIs can change; the live option validates required fields and stops if its contract is not met. The saved lesson and mock drill remain usable offline.",
    'kind="pull_request" if "pull_request" in source else "issue"\n# GET https://api.github.com/repos/OWNER/REPO/issues',
    '''sample=[
    {"id":101,"number":7,"title":"Fictional bug","state":"open","comments":2},
    {"id":102,"number":8,"title":"Fictional change","state":"closed","comments":1,"pull_request":{}}
]
print([(row["id"],"pull_request" if "pull_request" in row else "issue") for row in sample])''',
    "The second entry is preserved as a pull request instead of being falsely described as an issue. This is a fictional provider-shaped example, not downloaded live data.",
    ('# Label all repository /issues results as issues', '# Classify pull_request entries and report kind-specific counts', "The endpoint can include both kinds."),
    "Count issue-only and pull-request records in a fictional mixed list.",
    '''rows=[{"kind":"issue"},{"kind":"pull_request"},{"kind":"issue"}]
print({kind:sum(r["kind"]==kind for r in rows) for kind in ["issue","pull_request"]})''',
    "Create a documentation checklist covering method, endpoint, auth, pagination, status and schema.",
    '''contract={"method":"GET","path":"/repos/OWNER/REPO/issues","auth":"local scoped bearer for optional drill","pagination":"Link next","success":200,"required":["id","title","state","comments"]}
print(sorted(contract))''',
    "External documentation defines the contract. Preserve returned record kinds and do not promise a frozen remote census.",
    [("Can GitHub's repository issues endpoint include PRs?","Yes","Never","Only private repositories","The provider documents issue and pull-request entries."),
     ("Should quotas be assumed permanent constants?","No","Always","If copied once","Check current provider contracts and response hints.")])

lesson(3,"1. Handle statuses by meaning, not one generic retry",
    "Distinguish invalid input, missing credentials, denied access and temporary failures.",
    [("400/401/403/404/429/5xx", "400usually needs input correction;401credential review;403permission or provider-specific rate handling;404route/resource review;429rate-limit handling. Some5xxmay be transient. Provider semantics take precedence."),
     ("Retry policy versus raise_for_status", "raise_for_status reports HTTP failure. A retry policy separately decides which safe operation can be repeated, how often and after how much waiting.")],
    "Repeating a 400 request with the same invalid payload usually wastes work. Repeating a 401 does not invent a valid credential. "
    "A 403 can mean denied access or, for GitHub, a rate restriction with documented headers. Do not retry every 403 blindly. "
    "The read-only final collector retries selected GET failures:429and selected500/502/503/504, plus scoped network errors. It handles known GitHub rate hints separately. "
    "A 404 is not automatically an empty page; treating it as the end could silently truncate a collection. "
    "The expected status is part of each operation: a POST 201and a DELETE 204have different bodies and success contracts.",
    'if status==401: # check local auth, do not loop\n    ...\nelif status in {429,500,502,503,504}: # bounded GET policy only\n    ...',
    demo('for path in ["/missing","/unavailable"]:\n    with session.get(base+path,timeout=(3.05,10)) as response:\n        status=response.status_code\n        action="Review path/access" if status==404 else "Candidate for bounded GET retry"\n        print(status,action)'),
    "The two errors call for different decisions. The example classifies them without performing an unbounded retry loop.",
    ('while response.status_code!=200:\n    response=session.get(url)', '# Classify the failure; limit attempts; retry only permitted safe operations', "A generic loop can hammer a permanently failing endpoint."),
    "Classify401,403,429and503with explicit messages; keep403as provider-specific review.",
    '''actions={401:"Review credentials",403:"Review permissions/rate hints",429:"Respect rate wait",503:"Possible transient GET failure"}
for status in [401,403,429,503]:
    print(status,actions[status])''',
    "Prove the missing route raises HTTPError while its Response object still exists.",
    demo('with session.get(base+"/missing",timeout=(3.05,10)) as response:\n    print("Exists:",response is not None,"Boolean:",bool(response))\n    try:response.raise_for_status()\n    except requests.HTTPError:print("404handled distinctly")'),
    "Classify failures before choosing an action. A failed page is not an empty successful page.",
    [("Should401be retried forever with the same credential?","No","Always","Only for GET","Credential problems require correction."),
     ("Is every403a temporary server failure?","No","Always","Only on GitHub","Inspect documented permission and rate-limit signals.")])

lesson(3,"2. Parse JSON, then validate fields and types",
    "Reject malformed content and unexpected schemas before storing it.",
    [("JSONDecodeError; schema validation", "json can fail on invalid JSON. Valid JSON may still be the wrong type or lack required fields. Validate the application contract after parsing."),
     ("type(value) is int versus isinstance", "Python bool is a subclass of int. For an id/count contract requiring real integers, type(value) is int rejects True/False rather than accepting them as numbers.")],
    "There are three distinct success layers: HTTP, representation parsing and application validation. "
    "Our /bad-json route returns 200 with non-JSON text; /wrong-shape returns a JSON list where a health-like object would be expected. "
    "For collected items, validate a positive integer id, bounded title, allowed state/kind and nonnegative integer comment count. "
    "Reject invalid records before publishing a database or report. Do not coerce a string 'many' to0just to make totals run. "
    "Unknown provider fields can be ignored deliberately while selecting approved output fields; required fields cannot be silently invented.",
    'payload=response.json()\nif not isinstance(payload,dict):raise ValueError("Expected an object")\nif type(payload.get("id")) is not int:raise ValueError("Invalid id")',
    demo('for path in ["/bad-json","/wrong-shape"]:\n    with session.get(base+path,timeout=(3.05,10)) as response:\n        response.raise_for_status()\n        try:\n            body=response.json()\n            if not isinstance(body,dict):raise ValueError("Expected object")\n        except requests.exceptions.JSONDecodeError:\n            print("Malformed JSON rejected")\n        except ValueError:\n            print("Unexpected JSON shape rejected")'),
    "The first response fails representation parsing; the second passes parsing but fails the object schema. Both have HTTP 200.",
    ('comments=int(row.get("comments",0))  # hide invalid/missing data', 'if type(row.get("comments")) is not int or row["comments"]<0:\n    raise ValueError("Invalid count")', "Silently invented zeros distort the report."),
    "Validate that ids 1 and True are not both accepted as genuine integer ids.",
    '''for value in [1,True,"1",0]:
    valid=type(value) is int and value>0
    print(repr(value),valid)''',
    "Reject an item whose state is pending when the declared contract permits only open or closed.",
    '''row={"id":1,"state":"pending"}
if row.get("state") not in {"open","closed"}:
    print("Unknown state rejected")''',
    "A successful parse is the start of validation, not the end.",
    [("Can valid JSON still violate the API data contract?","Yes","Never","Only arrays","Its shape, fields or value types can be wrong."),
     ("Why reject True as an integer id?","It is a boolean, not the required id type","It is always negative","JSON cannot contain booleans","bool is an int subclass, so validate the intended type.")])

lesson(3,"3. Bounded retries for safe GET operations",
    "Limit retries and preserve the difference between temporary and permanent failure.",
    [("Attempt count; retryable set", "Count the initial request as attempt 1. Retry only selected safe failures and stop after a declared total. No final sleep is needed when no further attempt will occur."),
     ("Failure context", "A retry loop should produce a clear sanitised final error, not an empty successful collection. Never retry TLS verification failures as ordinary transient errors.")],
    "The fixture's /flaky route fails once with 503 and Retry-After:0, then returns200. That makes a controlled retry drill reproducible. "
    "A three-attempt loop has at most three requests, not three retries after the first. "
    "The example handles only this documented local case. It is a stepping stone; the final client adds wait parsing, scoped network errors, budgets and schema checks. "
    "Do not generalise this GET policy to POST. A repeated creation could duplicate a side effect. "
    "A repeatedly unavailable endpoint must end with a failure that prevents publication, not a zero-item success report.",
    'for attempt in range(max_attempts):\n    # request; validate; return on success\n    # retry only allowed transient reads; otherwise stop',
    demo('for attempt in range(1,4):\n    with session.get(base+"/flaky",timeout=(3.05,10)) as response:\n        status=response.status_code\n        print("Attempt",attempt,"status",status)\n        if status==200:\n            print("Recovered:",response.json()["ok"]);break\n        if status!=503 or response.headers.get("Retry-After")!="0":\n            raise RuntimeError("Outside this fixture retry contract")\nelse:\n    raise RuntimeError("GET attempts exhausted")'),
    "Attempt 1 gets 503with an explicit zero wait; attempt 2 succeeds. There is no endless loop or hidden extra attempt.",
    ('# Count only retries and forget the initial request', '# Define max_attempts as total request attempts', "Clear counting keeps load and waiting bounded."),
    "Try /unavailable at most2times; report exhaustion without publishing data.",
    demo('for attempt in range(1,3):\n    with session.get(base+"/unavailable",timeout=(3.05,10)) as response:\n        print("Attempt",attempt,response.status_code)\n        if response.status_code==200:break\nelse:\n    print("Attempts exhausted; no complete dataset")'),
    "Classify SSL errors as immediate stop and Timeout as a possible bounded GET retry without sending a request.",
    '''import requests
for error in [requests.exceptions.SSLError(),requests.Timeout()]:
    if isinstance(error,requests.exceptions.SSLError):
        print("Stop: verify TLS trust")
    else:
        print("Possible bounded GET retry")''',
    "A resilient client has a stopping condition and never disguises exhausted collection as success.",
    [("Does max_attempts 3 mean four calls?","No","Always","Only for503","It includes the initial call."),
     ("Should an exhausted GET silently return an empty list?","No","Always","If all statuses are503","The collection failed; an empty list would misrepresent evidence.")])

lesson(3,"4. Backoff, jitter and Retry-After",
    "Respect server waits and stop when the required delay exceeds the budget.",
    [("Exponential backoff; jitter", "Backoff increases waits between safe retries. A small random jitter spreads clients apart. Cap the policy and total wait budget; do not sleep after the last attempt."),
     ("Retry-After seconds or HTTP date", "Retry-After can be nonnegative integer seconds or an HTTP date. A server-mandated wait is not a suggestion to shorten; if it exceeds your budget, stop and resume later."),
     ("UTC; parsedate_to_datetime", "Use timezone-aware UTC when comparing HTTP dates. email.utils.parsedate_to_datetime parses the header date; a malformed header should be handled deliberately.")],
    "Without a server hint, a simple policy might wait 0.5 then 1 second plus bounded jitter. That reduces immediate repeated traffic. "
    "When the server says wait 120 seconds and your operation allows 10 seconds of waiting, do not cap the server hint to 10 and retry too early. Stop. "
    "The example uses the already supplied api_client.retry_delay helper, whose full implementation appears in Day6. It parses hints without making any HTTP call. "
    "An HTTP-date comparison depends on the chosen current UTC time. The example supplies a fixed clock for reproducible output. "
    "The final client's budget limits accumulated waiting, not all network and parsing time. Keep that distinction explicit.",
    'delay=server_hint if server_hint is not None else backoff+jitter\nif delay>remaining_wait_budget:raise RuntimeError("Stop; required wait is too long")',
    '''from datetime import datetime,timezone
from api_client import retry_delay
now=datetime(2026,1,1,tzinfo=timezone.utc)
print("Seconds:",retry_delay("3",now=now))
print("Date:",retry_delay("Thu, 01 Jan 2026 00:00:05 GMT",now=now))
for attempt in range(2):
    print("No-hint wait:",0.5*2**attempt)
print("Long hint allowed:",retry_delay("120")<=10)''',
    "Both hint forms become seconds. The date is 5 seconds after the supplied clock; the120-second hint is refused under a 10-second budget.",
    ('delay=min(server_retry_after,10)  # retry too early', 'if server_retry_after>10:\n    raise RuntimeError("Stop and resume later")', "A local convenience limit must not shorten the provider's minimum wait."),
    "Parse a past HTTP date with a fixed clock and show that the remaining delay is0.",
    '''from datetime import datetime,timezone
from api_client import retry_delay
now=datetime(2026,1,1,0,0,10,tzinfo=timezone.utc)
print(retry_delay("Thu, 01 Jan 2026 00:00:05 GMT",now=now))''',
    "Reject a malformed Retry-After value instead of guessing a short delay.",
    '''from api_client import retry_delay,APIError
try:retry_delay("soon")
except APIError:print("Malformed wait hint: stop for review")''',
    "Wait politely within a declared budget or stop; never shorten a mandated delay to force progress.",
    [("What if Retry-After 120 exceeds a 10-second budget?","Stop rather than retry early","Wait10then retry","Ignore it","The provider's minimum delay must not be shortened."),
     ("Does a wait budget include all network execution time here?","No","Always","Only for dates","It limits accumulated sleeps, separately from request-stage timeouts.")])

lesson(3,"5. Rate limits and uncertain write outcomes",
    "Handle provider limits without retry storms or duplicated writes.",
    [("429; provider rate headers", "429means too many requests. GitHub can also use403with rate hints; inspect Retry-After and its documented rate headers. A plain forbidden response is not automatically retryable."),
     ("Idempotency key; reconciliation", "Some write APIs document idempotency keys or lookup-based reconciliation. Without that contract, a timed-out POST has an uncertain outcome and should not be blindly resent.")],
    "The /rate fixture returns 429 with Retry-After: 1 once. The example actually waits one second before the second GET. "
    "A production collector should not assume a specific quota remains forever. Provider limits vary by auth context and resource and can change. "
    "For GitHub's exhausted-primary-limit hint, the final client respects the reset time within its wait budget or stops. Unknown403failures stop immediately. "
    "After a timed-out POST, check the provider's operation-status or idempotency contract before trying again. Never invent an idempotency header and assume the server honours it. "
    "All write examples here are disposable local tasks; the optional GitHub collector performs GET only.",
    'if status==429:\n    # Respect Retry-After, bounded attempts and wait budget.\n# Do not apply this generic GET retry loop to POST.',
    demo('import time\nfor attempt in range(1,3):\n    with session.get(base+"/rate",timeout=(3.05,10)) as response:\n        print("Attempt",attempt,response.status_code)\n        if response.status_code==200:break\n        if response.status_code!=429 or response.headers.get("Retry-After")!="1":\n            raise RuntimeError("Unexpected rate contract")\n    if attempt<2:time.sleep(1)\nelse:\n    raise RuntimeError("Rate wait did not recover")'),
    "This controlled endpoint allows recovery after its documented one-second wait. It does not justify hard-coding one second for unrelated real limits.",
    ('# Retry a timed-out payment/create operation with no documented protection', '# Reconcile outcome or use the provider-documented idempotency mechanism', "Network uncertainty and write duplication are different from safe-read retry."),
    "Use a synthetic provider hint to distinguish exhausted rate allowance from ordinary forbidden access.",
    '''responses=[(403,{"X-RateLimit-Remaining":"0"}),(403,{}),(429,{"Retry-After":"2"})]
for status,headers in responses:
    limited=status==429 or (status==403 and headers.get("X-RateLimit-Remaining")=="0")
    print(status,"Rate review" if limited else "Access denied: stop")''',
    "Explain uncertain write state using three explicit client outcomes instead of claiming every timeout means failure.",
    '''outcomes=["Confirmed success","Confirmed rejection","Unknown outcome after lost response"]
for outcome in outcomes:print(outcome)''',
    "Respect the provider's rate contract and treat uncertain writes as a reconciliation problem.",
    [("Is every GitHub403safe to retry automatically?","No","Always","If authenticated","Only documented rate hints justify that rate-handling path."),
     ("Can an invented idempotency header guarantee no duplicates?","No","Always","Only for JSON","The provider must implement and document the mechanism.")])

lesson(3,"6. Failure drills and sanitised diagnostics",
    "Test bad status, wrong schema and retry exhaustion before trusting the client.",
    [("Fault injection; sanitised APIError", "A fixture can deliberately return malformed JSON, redirects and transient failures. Test that the client stops correctly and reports a useful error without including credentials or raw bodies.")],
    "Happy-path GET 200 is not enough. A collector also needs predictable behaviour when a page fails halfway. "
    "Use controlled failures to verify that malformed JSON and redirects stop, rather than becoming an empty dataset. "
    "The final APIClient is provided as support code and examined in Day6. Its APIError carries a sanitised operation-level message. "
    "The example uses only fake local authentication. It demonstrates the public client interface while testing actual network responses from the fixture. "
    "No test needs a real token, a production API write or a copy of the user's browser storage.",
    'try:\n    api.get_json("/bad-json")\nexcept APIError as error:\n    print(str(error))  # sanitised message, not raw response/request dump',
    '''from mock_api import DemoAPI,PRACTICE_TOKEN
from api_client import APIClient,APIError
with DemoAPI() as base, APIClient(base,PRACTICE_TOKEN,attempts=2) as api:
    for path in ["/bad-json","/redirect","/unavailable"]:
        try:api.get_json(path)
        except APIError as error:print(path,str(error))
''',
    "Malformed representation, unexpected redirect and exhausted retries are reported distinctly. No partial list or token is printed.",
    ('except Exception:\n    return []', 'except APIError:\n    raise  # prevent a failed collection from publishing success', "An empty success would hide the failure."),
    "Call /missing through the client and show that the sanitised error contains no fictional token.",
    '''from mock_api import DemoAPI,PRACTICE_TOKEN
from api_client import APIClient,APIError
with DemoAPI() as base,APIClient(base,PRACTICE_TOKEN) as api:
    try:api.get_json("/missing")
    except APIError as error:print(str(error),PRACTICE_TOKEN not in str(error))''',
    "Recover from the once-failing local /flaky route through the bounded client.",
    '''from mock_api import DemoAPI
from api_client import APIClient
with DemoAPI() as base,APIClient(base) as api:
    payload,_=api.get_json("/flaky")
    print(payload["ok"])''',
    "Test failure behaviour as deliberately as success. No complete validated collection means no published report.",
    [("Should a malformed page become an empty successful result?","No","Always","Only on the last page","It failed the contract and must stop collection."),
     ("Do these failure drills require a real credential?","No","Always","Only for redirects","The loopback fixture uses a public fake token.")])

lesson(4,"1. One response is often only one page",
    "Recognise page-number and cursor pagination before counting records.",
    [("Page number; page size; cursor", "Page-number pagination requests numbered slices. Cursor pagination sends an opaque continuation token returned by the server. Do not infer the total from the first response."),
     ("Terminal signal", "Use the documented next-link/cursor/terminal marker. A short page is not universally an end signal, and a failed request is never a successful empty page.")],
    "The authenticated /items route returns two rows at a time, even though the fictional collection has six. "
    "The /paged route demonstrates page-number requests; /items demonstrates opaque cursors. Both have an explicit next_cursor field whose null value means complete for this fixture. "
    "Do not assume page 2 means cursor 2. The server's c2 token is opaque even if its sample spelling looks numerical. "
    "A real API may place its next hint in an HTTP Link header instead of the JSON body. GitHub does that; the final client validates it. "
    "Collection totals are meaningful only after the documented terminal signal has been reached within your chosen bounds.",
    'payload=GET_page()\n# Process items; follow the documented next hint until terminal.',
    demo('with session.get(base+"/items",timeout=(3.05,10)) as response:\n    body=response.json();print("First page ids:",[r["id"] for r in body["items"]],"Next:",body["next_cursor"])\nwith session.get(base+"/paged",params={"page":2},timeout=(3.05,10)) as response:\n    print("Page2ids:",[r["id"] for r in response.json()["items"]])',auth=True),
    "First-page ids 1 and 2 are not the collection total. Numbered page 2 contains 3 and 4under this fixture's page contract.",
    ('all_items=first_response.json()["items"]  # claim complete', '# Follow the endpoint continuation contract before claiming completion', "A first page is only a first page."),
    "Request page 3 and inspect its item ids and terminal marker.",
    demo('with session.get(base+"/paged",params={"page":3},timeout=(3.05,10)) as response:\n    body=response.json();print([r["id"] for r in body["items"]],body["next_cursor"])',auth=True),
    "Request cursor c2 and verify it is sent as a parameter rather than incremented by the client.",
    demo('with session.get(base+"/items",params={"cursor":"c2"},timeout=(3.05,10)) as response:\n    body=response.json();print([r["id"] for r in body["items"]],body["next_cursor"])',auth=True),
    "Read the continuation contract before choosing a loop or interpreting a count.",
    [("Does receiving2rows prove the total is2?","No","Always","Only with authentication","The response may be a page."),
     ("Should clients calculate an opaque cursor's next value?","No","Always","If it contains a digit","Send the exact server-supplied continuation token.")])

lesson(4,"2. Follow cursors exactly and stop on the terminal marker",
    "Collect all six fictional records with an explicit continuation loop.",
    [("Cursor loop; params per page", "Start without a cursor, then send exactly the returned token on the next GET. A null continuation ends this fixture's sequence."),
     ("Bounded for loop; loop else", "A bounded for loop can fail in its else block if no normal terminal break occurred. The cap is a failure guard, not permission to publish an incomplete list.")],
    "Write the loop in visible stages: request, check HTTP, parse, inspect items, process continuation, stop or repeat. "
    "The compact example has a ten-page ceiling and uses the fixture's known schema. Later parts add full validation and duplicate detection. "
    "Never retain an old cursor parameter accidentally on the first request of a new collection. Fresh local state begins each example. "
    "If the terminal signal does not arrive before the ceiling, raise an error. A list of some collected rows is not a complete successful result. "
    "This practice material uses six fixed fictional rows; real APIs can change while you paginate.",
    'cursor=None\nfor _ in range(max_pages):\n    params={} if cursor is None else {"cursor":cursor}\n    # request/process\n    if next_cursor is None:break',
    demo('cursor=None;rows=[];pages=0\nfor _ in range(10):\n    params={} if cursor is None else {"cursor":cursor}\n    with session.get(base+"/items",params=params,timeout=(3.05,10)) as response:\n        response.raise_for_status();body=response.json()\n    pages+=1;rows.extend(body["items"]);cursor=body["next_cursor"]\n    if cursor is None:break\nelse:\n    raise RuntimeError("Page ceiling reached")\nprint("Pages:",pages,"IDs:",[r["id"] for r in rows])',auth=True),
    "Three successful pages reach the null marker. All ids 1 through 6 are present in the returned order.",
    ('cursor=str(int(cursor)+1)', 'cursor=payload["next_cursor"]', "Opaque tokens belong to the server contract, not client arithmetic."),
    "Using the supplied bounded client, collect all items and print their count.",
    '''from mock_api import DemoAPI,PRACTICE_TOKEN
from api_client import APIClient
with DemoAPI() as base,APIClient(base,PRACTICE_TOKEN) as api:
    rows=api.collect_mock()
    print(len(rows))''',
    "Choose max_pages 2 for a three-page fixture and verify it fails instead of reporting four items as complete.",
    '''from mock_api import DemoAPI,PRACTICE_TOKEN
from api_client import APIClient,APIError
with DemoAPI() as base,APIClient(base,PRACTICE_TOKEN) as api:
    try:api.collect_mock(max_pages=2)
    except APIError:print("Incomplete collection refused")''',
    "Pagination completion is an explicit contract event, not merely the moment a loop stops.",
    [("What does exhausting the page cap mean here?","Collection failure","Complete data automatically","No rows exist","A cap does not replace the terminal marker."),
     ("How many successful pages contain this fixture's six rows?","3","1","6","Each page contains two records.")])

lesson(4,"3. Validate every page, cursor and record",
    "Reject missing metadata, invalid fields and repeated continuations.",
    [("Envelope validation; cursor cycle", "Validate that the response object contains an items list and a next_cursor key. Track seen nonterminal cursors; repeating one indicates a loop or inconsistent provider behaviour."),
     ("Item budget; schema boundary", "Bound total retained items independently of page count. Every row must satisfy its field/type contract before the full result can be returned.")],
    "A dictionary with no next_cursor key must not be interpreted as completion just because .get returns None. Required metadata must actually be present. "
    "Track cursors so a server repeatedly returning c2 cannot trap the client. A page cap remains a second defence. "
    "Validate each item before appending approved fields. Boolean ids, negative comments and unknown categories are rejected. "
    "The final client caps pages and items and throws a sanitised error if either budget is exhausted before completion. "
    "Limits depend on the use case. They protect a bounded teaching operation, not a claim that every large real repository fits the default settings.",
    'if not isinstance(payload,dict) or "next_cursor" not in payload:\n    raise ValueError("Invalid page metadata")\nif cursor in seen_cursors:raise ValueError("Repeated cursor")',
    '''from api_client import validate_item,APIError
valid={"id":1,"title":"Read docs","state":"open","comments":0,"kind":"issue"}
print(validate_item(valid))
for change in [{"id":True},{"comments":-1},{"state":"pending"}]:
    try:validate_item({**valid,**change})
    except APIError:print("Invalid record rejected")''',
    "The valid object is reduced to approved fields; each changed required value fails explicitly.",
    ('cursor=payload.get("next_cursor")  # missing looks terminal', 'if "next_cursor" not in payload:raise ValueError("Missing continuation metadata")', "Absent metadata and explicit JSON null differ."),
    "Set max_items 5 for the six-row fixture and handle item-budget failure.",
    '''from mock_api import DemoAPI,PRACTICE_TOKEN
from api_client import APIClient,APIError
with DemoAPI() as base,APIClient(base,PRACTICE_TOKEN) as api:
    try:api.collect_mock(max_items=5)
    except APIError:print("Item ceiling refused incomplete success")''',
    "Simulate continuation values c2,c4,c2and stop at the repeated token.",
    '''seen=set()
for cursor in ["c2","c4","c2"]:
    if cursor in seen:
        print("Repeated cursor rejected");break
    seen.add(cursor)
    print("Accepted continuation",cursor)''',
    "Validate metadata as carefully as item values; missing or cycling continuation cannot establish completeness.",
    [("Is a missing next_cursor key the same as explicit null?","No","Always","Only for empty pages","The envelope contract requires the key."),
     ("Why bound items separately from pages?","Page sizes and retained data can vary","To change every id","Because JSON is SQL","A page ceiling alone does not define a memory/item budget.")])

lesson(4,"4. Stable IDs, duplicates and changing remote data",
    "Detect repeated records without silently claiming a frozen snapshot.",
    [("Stable provider id; duplicate policy", "Track the provider's stable record id across pages. This collector rejects repeats instead of silently choosing one conflicting version."),
     ("Snapshot consistency; page drift", "Real pages can shift while records change. Completing continuation does not prove an atomic historical snapshot. Ordering and duplicate checks improve observability but cannot guarantee that no item was missed.")],
    "Numbered pagination over changing data can repeat or skip records. Cursor pagination has provider-specific consistency guarantees; do not invent them. "
    "The collector requests a stable-looking creation order for GitHub, but labels the result as a completed request sequence at a recorded time, not a frozen census. "
    "A repeated id triggers review rather than automatic deduplication. Silently keeping the first or last could hide a changed comment count or state. "
    "Provider id and repository number are different keys. The returned id is used for this collection's SQLite primary key. "
    "If a provider offers snapshot tokens or export endpoints, use its documented stronger contract when needed; our teaching client makes no such claim.",
    'if row["id"] in seen_ids:raise ValueError("Repeated provider id")\nseen_ids.add(row["id"])',
    '''records=[{"id":1,"comments":2},{"id":2,"comments":0},{"id":1,"comments":3}]
seen=set()
for row in records:
    if row["id"] in seen:
        print("Repeated id: collection requires review");break
    seen.add(row["id"])
print("Approved unique records before stop:",len(seen))''',
    "The last id 1 has changed comments. Rejecting the sequence exposes uncertainty instead of silently picking a version.",
    ('rows=list({r["id"]:r for r in rows}.values())  # hide repeated-page evidence', '# Stop on duplicate ids unless a reviewed merge/snapshot policy exists', "A deduplication expression can hide page drift."),
    "Collect the fixture and verify all returned ids are unique.",
    '''from mock_api import DemoAPI,PRACTICE_TOKEN
from api_client import APIClient
with DemoAPI() as base,APIClient(base,PRACTICE_TOKEN) as api:
    rows=api.collect_mock()
    print(len(rows)==len({r["id"] for r in rows}))''',
    "Split the known mixed collection into issue and pull-request counts without deleting either kind.",
    '''from mock_api import ITEMS
print({kind:sum(r["kind"]==kind for r in ITEMS) for kind in ["issue","pull_request"]})''',
    "Detect duplicates, retain provenance and state the remote consistency limitation honestly.",
    [("Do unique returned ids prove no remote record was missed?","No","Always","Only for pages of100","A changing remote source can still drift or omit records."),
     ("Should conflicting duplicate ids be silently overwritten here?","No","Always","If the latest is larger","The declared policy stops for review.")])

lesson(4,"5. Turn a complete collection into database evidence",
    "Store approved rows atomically and reconcile grouped totals.",
    [("API -> validation -> SQLite -> report", "Finish the bounded validated collection before publishing outputs. SQL constraints and bound inserts protect the database layer; grouped reports preserve item kind and state."),
     ("Reconciliation", "Group counts should sum to the approved item count; comment totals should equal the sum of recorded comment fields. These are collection facts, not causal or historical-completeness claims.")],
    "Reuse Week 35's transaction principles. A collection that failed halfway should never publish a new successful report bundle. "
    "After completion and validation, insert approved columns with parameters, then query grouped counts and comment sums. "
    "Keep issue and pull_request separate. The fixture has six records but only five issue records. "
    "Comments describe the endpoint's field, not every review thread or every historical discussion. Do not exaggerate what a count measures. "
    "The final bundle records provider, collection time and a hash of the saved JSON, and refuses an existing destination. It does not store request headers or credentials.",
    "BEGIN IMMEDIATE;\n-- Bound inserts of approved rows\nCOMMIT;\nSELECT kind,state,COUNT(*),SUM(comments) FROM items GROUP BY kind,state;",
    '''from mock_api import ITEMS
import sqlite3
from contextlib import closing
with closing(sqlite3.connect(":memory:",isolation_level=None)) as con:
    con.execute("CREATE TABLE items(id INTEGER PRIMARY KEY,kind TEXT,state TEXT,comments INTEGER)")
    con.execute("BEGIN IMMEDIATE")
    try:
        con.executemany("INSERT INTO items VALUES(?,?,?,?)",[(r["id"],r["kind"],r["state"],r["comments"]) for r in ITEMS])
        con.execute("COMMIT")
    except BaseException:
        if con.in_transaction:con.execute("ROLLBACK")
        raise
    print(con.execute("SELECT kind,state,COUNT(*),SUM(comments) FROM items GROUP BY kind,state ORDER BY kind,state").fetchall())
    print("Totals:",con.execute("SELECT COUNT(*),SUM(comments) FROM items").fetchone())''',
    "Totals reconcile to 6 items and 18 recorded comments. The open pull-request row is reported as its own kind rather than counted as an issue.",
    ('# Save first-page rows and label the report complete', '# Complete/validate collection before publishing a new bundle', "Partial collection must not become a successful artifact."),
    "Calculate the same approved-record totals in Python for an independent comparison.",
    '''from mock_api import ITEMS
print("Items:",len(ITEMS),"Comments:",sum(r["comments"] for r in ITEMS))
print("Open:",sum(r["state"]=="open" for r in ITEMS))''',
    "Group by kind in Python and verify the grouped item counts sum back to6.",
    '''from mock_api import ITEMS
counts={kind:sum(r["kind"]==kind for r in ITEMS) for kind in ["issue","pull_request"]}
print(counts,sum(counts.values())==len(ITEMS))''',
    "Publish only complete approved collections and reconcile every report total to that declared population.",
    [("How many issue-only records are in the six-row fixture?","5","6","1","One of the six is explicitly a pull_request."),
     ("What does the 18 total measure?","Recorded comments on the returned items","All discussion everywhere","The number of pages","It sums the selected endpoint field.")])

lesson(5,"1. A class gives repeated API work one clear interface",
    "Encapsulate session lifetime and expose a typed operation instead of arbitrary requests.",
    [("Client class; typed method", "A client object keeps the service's base address and session configuration together. A typed method such as health()->dict documents intended input/output; type hints do not validate data at runtime."),
     ("__enter__/__exit__; composition", "Context methods let with close an owned client reliably. Composition means this client uses a Requests Session instead of rebuilding HTTP networking itself.")],
    "Weeks 18 and 19 introduced objects; now use that model for one service. A caller should ask client.health rather than repeatedly assembling URLs and status checks. "
    "Keep the public operation small and meaningful. The class below owns a session, closes it and validates a minimal health payload. "
    "The final APIClient supports bounded GET collection only, not arbitrary authenticated writes. The local write-method lessons are deliberately separate. "
    "Type hints communicate intent but do not turn a list into a dictionary or validate required keys. Runtime schema checks still matter. "
    "When a supplied session belongs to another caller, ownership rules should be explicit; this beginner implementation owns the session it creates.",
    'class HealthClient:\n    def health(self)->dict:\n        # Request, validate and return the approved result.',
    '''import requests
from mock_api import DemoAPI
class HealthClient:
    def __init__(self,base:str):
        self.base=base
        self.session=requests.Session();self.session.trust_env=False
    def health(self)->dict:
        with self.session.get(self.base+"/health",timeout=(3.05,10)) as response:
            response.raise_for_status();body=response.json()
            if not isinstance(body,dict) or body.get("ok") is not True:
                raise ValueError("Invalid health result")
            return body
    def close(self)->None:
        self.session.close()
with DemoAPI() as base:
    client=HealthClient(base)
    try:print(client.health())
    finally:client.close()
''',
    "The caller gets an approved dictionary without managing request details. finally closes the owned session even if validation fails.",
    ('# Assume ->dict guarantees every response is a valid dict', '# Keep type hints and runtime payload validation', "Annotations describe intent, not runtime enforcement."),
    "Use the supplied final APIClient as a context manager and request the health operation.",
    '''from mock_api import DemoAPI
from api_client import APIClient
with DemoAPI() as base,APIClient(base) as client:
    body,_=client.get_json("/health")
    print(body["ok"])''',
    "Explain optional parameter typing with a small pure helper accepting a dict or None.",
    '''def page_params(cursor:str|None)->dict:
    return {} if cursor is None else {"cursor":cursor}
print(page_params(None),page_params("c2"))''',
    "Wrap a service contract in a small client; reuse Requests and preserve explicit validation/resource ownership.",
    [("Do type hints validate HTTP data automatically?","No","Always","Only dictionaries","They document intent; runtime checks enforce the response contract."),
     ("Should this client reimplement sockets and TLS?","No","Always","For pagination","Compose the tested HTTP library instead.")])

lesson(5,"2. Separate transport, validation, pagination and storage",
    "Give each layer one responsibility so failures can be tested independently.",
    [("Transport boundary; dependency injection", "Transport obtains a response; validation approves data; pagination assembles a complete sequence; storage publishes approved facts. Inject sleep/clock/transport in tests to observe decisions without real credentials or long waits."),
     ("Pure validator; approved fields", "A pure validator can check a supplied object without making requests or writing files. Return selected approved fields and preserve meaningful record kinds.")],
    "One giant function that downloads, guesses types, writes rows and catches all errors is hard to trust. "
    "The final project splits responsibilities into mock_api.py, api_client.py and collector.py. Each part has a small observable contract. "
    "validate_item checks one row and returns only id,title,state,comments,kind. It does not silently fill missing counts or print unknown response fields. "
    "get_json handles fixed-origin GET and representation checks; collect_mock/collect_github handle continuation and duplicate policy; publish writes a new bundle. "
    "Tests can inject a fake sleep recorder to verify waiting decisions on a fixture. That is a test tool, not permission to skip a provider-mandated wait in live use.",
    'rows=client.collect_mock()\nfacts=publish(rows,new_destination,provider="mock")\n# A failure in collection prevents publish from being called.',
    '''from api_client import validate_item,APIError
raw={"id":1,"title":"Fictional result","state":"open","comments":2,"kind":"issue","extra":"not stored"}
approved=validate_item(raw)
print(sorted(approved))
print("Raw preserved:","extra" in raw)
try:validate_item({**raw,"comments":"two"})
except APIError:print("Invalid count rejected before storage")''',
    "The source object remains unchanged. Only approved fields pass the boundary, and invalid counts do not become stored zeros.",
    ('# Catch every error inside the database writer and report success', '# Let invalid collection/validation stop publication before storage', "Responsibility boundaries should preserve failure meaning."),
    "Inject a sleep recorder into a retrying client on the local flaky fixture and inspect the mandated zero wait.",
    '''from mock_api import DemoAPI
from api_client import APIClient
waits=[]
with DemoAPI() as base,APIClient(base,sleep=waits.append) as api:
    payload,_=api.get_json("/flaky")
    print(payload["ok"],waits)
''',
    "Demonstrate validation as a deterministic function with no network: the same approved input yields the same fields.",
    '''from api_client import validate_item
row={"id":9,"title":"Deterministic","state":"closed","comments":0,"kind":"issue"}
print(validate_item(row)==validate_item(dict(row)))''',
    "Test each boundary independently and let errors prevent the next dependent action.",
    [("Should a pure validator need a real API token?","No","Always","Only for ids","It inspects a supplied data object."),
     ("May fake sleep be used to bypass real provider waits?","No","Always","If you are impatient","It is for controlled tests, not live rate-limit evasion.")])

FOLDER=ROOT/"docs"/"python-week36"
CLIENT=(FOLDER/"api_client.py").read_text(encoding="utf-8")
COLLECTOR=(FOLDER/"collector.py").read_text(encoding="utf-8")

lesson(5,"3. Assemble the bounded read-only API client",
    "Trace the full implementation from approved origin through complete validated records.",
    [("APIError; retry_delay; APIClient", "APIError exposes a sanitised message. retry_delay parses provider waits. APIClient owns the session, fixed-origin transport, GET retry policy and complete bounded collection."),
     ("tuple[object,dict]; list[dict]", "These annotations describe a payload plus link metadata, or a list of approved row dictionaries. They are documentation for the interface, not substitutes for schema checks.")],
    "The full client follows the pieces already studied. Read __init__first, then get_json, validate_item and the two collectors. "
    "It accepts only the exact GitHub HTTPS origin or numeric loopback fixture origin. Relative paths are fixed, redirects stop and normal TLS verification stays enabled. "
    "Selected transient GET failures retry within total-attempt and accumulated-wait budgets. Credential errors, bad JSON, schema failures and unknown403access failures stop. "
    "GitHub next links are inspected for approved origin, exact endpoint and unchanged filter parameters; the client reconstructs the next request instead of following an arbitrary URL. "
    "All pages must reach their terminal marker within limits. The collector rejects duplicate ids and unexpected cursor/link sequences. "
    "This client does not claim a strict whole-workflow deadline, hard JSON byte bound, frozen remote snapshot or write-idempotency implementation. Those are separate requirements.",
    'with APIClient(base,token,attempts=3,max_wait=10) as client:\n    rows=client.collect_mock(max_pages=10,max_items=1000)',
    CLIENT+'''
from mock_api import DemoAPI,PRACTICE_TOKEN
with DemoAPI() as base,APIClient(base,PRACTICE_TOKEN) as api:
    rows=api.collect_mock()
    print("Collected:",len(rows),"IDs:",[row["id"] for row in rows])
''',
    "The long example is the actual project client plus a short offline run. Inspect one method at a time; the printed result verifies the terminal collection, not just a first page.",
    ('# Follow a next URL from any host with the bearer session', '# Validate the origin/path/continuation contract and reconstruct the request', "A next-link hint is not unlimited authority to forward credentials."),
    "Verify that the client refuses an unapproved external origin before any request.",
    '''from api_client import APIClient
try:APIClient("https://example.org","practice-only-token")
except ValueError:print("Unapproved origin refused")''',
    "Collect the fixture with a low page cap and verify no successful result is returned.",
    '''from mock_api import DemoAPI,PRACTICE_TOKEN
from api_client import APIClient,APIError
with DemoAPI() as base,APIClient(base,PRACTICE_TOKEN) as api:
    try:api.collect_mock(max_pages=1)
    except APIError:print("No complete result within page budget")''',
    "The client contract narrows where requests go, what may retry, which data is valid and when collection is complete.",
    [("Does an arbitrary next-page URL get followed with credentials?","No","Always","Only if it contains page2","The client validates origin/path/query and reconstructs an approved request."),
     ("What happens when no terminal marker arrives within the cap?","Failure; no complete result","Successful partial report","Automatic overwrite","Incomplete pagination cannot satisfy the collection contract.")])

COLLECTOR_CORE=COLLECTOR.rsplit('\nif __name__=="__main__":',1)[0]
lesson(5,"4. Publish SQLite, JSON, CSV and an evidence report together",
    "Create a new complete output bundle and preserve prior runs.",
    [("Staging directory; atomic rename; manifest", "Prepare outputs in an owned temporary folder beside a new destination, then rename it into place only after successful writes. A manifest records provenance, scope, retrieval time and a saved-JSON hash."),
     ("Raw source versus selected payload", "The saved JSON contains approved selected fields, not the full HTTP response or headers. A hash verifies those saved bytes; it does not prove provider accuracy or historical completeness.")],
    "The publisher validates selected rows again, creates a constrained SQLite table and inserts rows in one transaction. It then derives grouped evidence with SQL. "
    "Six outputs are created: items.json, items.csv, collection.sqlite, summary.json, manifest.json and report.md. Existing destinations are refused. "
    "A failure before final rename leaves no published partial bundle and removes only the temporary folder this operation owns. Prior reports remain. "
    "The report distinguishes issue and pull-request kinds and states that remote pages are not a frozen historical census. "
    "CSV is an interchange format: external titles can contain spreadsheet formula-like text, so import titles as text rather than blindly executing them in a spreadsheet. The file preserves approved source text. "
    "Credentials never enter selected rows, metadata, SQLite or diagnostics. The optional live branch reads local configuration only when explicitly chosen.",
    'facts=publish(rows,Path("api-run-01"),provider="mock")\n# Use api-run-02 next time; do not overwrite a prior run.',
    COLLECTOR_CORE+'''
with TemporaryDirectory() as folder:
    with DemoAPI() as base,APIClient(base,PRACTICE_TOKEN) as api:
        rows=api.collect_mock()
    target=Path(folder)/"api-run-01"
    facts=publish(rows,target,provider="mock")
    print("Files:",sorted(p.name for p in target.iterdir()))
    print("Items/comments:",facts["items"],facts["comments"])
    print("Groups:",facts["groups"])
''',
    "The temporary demonstration publishes all six artifacts and reconciles 6 items / 18 comments. The source fixture remains separate from the report's approved-field snapshot.",
    ('# Write over api-run-01 halfway through a new collection', '# Stage a complete new bundle and refuse an existing destination', "Previous evidence should survive a failed new run."),
    "Publish the fixture, reopen SQLite and verify the total count independently.",
    '''from tempfile import TemporaryDirectory
from pathlib import Path
from contextlib import closing
import sqlite3
from mock_api import ITEMS
from collector import publish
with TemporaryDirectory() as folder:
    target=Path(folder)/"run"
    publish(ITEMS,target,provider="mock")
    with closing(sqlite3.connect(target/"collection.sqlite")) as con:
        print(con.execute("SELECT COUNT(*),SUM(comments) FROM items").fetchone())''',
    "Publish a run, try the same destination again, and show that its prior summary bytes remain unchanged.",
    '''from tempfile import TemporaryDirectory
from pathlib import Path
from mock_api import ITEMS
from collector import publish
with TemporaryDirectory() as folder:
    target=Path(folder)/"run";publish(ITEMS,target,provider="mock")
    before=(target/"summary.json").read_bytes()
    try:publish(ITEMS,target,provider="mock")
    except ValueError:print("Existing run refused")
    print((target/"summary.json").read_bytes()==before)''',
    "Publish one complete new evidence bundle or publish nothing; preserve previous reports and record exact scope.",
    [("Does a hash prove provider accuracy?","No","Always","Only for JSON","It checks saved byte equality, not truth or sampling."),
     ("Should a new run replace an existing bundle silently?","No","Always","Only if smaller","New destinations preserve prior evidence.")])

lesson(5,"5. Milestone: a resilient API-to-SQLite collection pipeline",
    "Run the offline drill end to end and understand the explicit optional live mode.",
    [("Offline mock versus optional live", "The default CLI starts only the local fixture with fake authentication. --github OWNER/REPO explicitly chooses the real GitHub HTTPS API, local credential loading and network access."),
     ("End-to-end acceptance", "Check complete pagination, approved rows, SQLite totals, report limits, missing-credential failure, refusal to overwrite and failure cleanup. A clean happy path alone is insufficient.")],
    "Download the files in docs/python-week36 and keep them together. Install requirements once, then run python collector.py api-run-01 from that folder. "
    "The default drill obtains three authenticated local pages, validates six records and publishes six files. It needs no real token and no internet after package installation. "
    "Read report.md, inspect summary.json and query collection.sqlite. Counts reconcile to 6 records, 5 issues, 1 pull request, 4 open records and 18 recorded comments. "
    "For a later live exercise, read GitHub's current docs, configure a scoped credential locally and run the explicit --github option with your chosen public repository. Do not send the token here. "
    "Large repositories can exceed the page budget; that is a deliberate stop with no report, not permission to label the partial result complete. "
    "The live option is supported by provider-contract fixtures and endpoint documentation; the automated teaching checks use fictional local authentication, not your real GitHub account. "
    "This is a separate Python practice project. Study Hub's lessons, notes, progress, dark/light mode, backup/import and existing sync remain in their current system.",
    'python -m pip install -r requirements.txt\npython collector.py api-run-01\npython collector.py api-run-02 --max-pages 2\n# Optional learner-run live command, after local credential setup:\npython collector.py api-live-01 --github OWNER/REPO --max-pages 10',
    '''from pathlib import Path
from tempfile import TemporaryDirectory
import json
from mock_api import DemoAPI,PRACTICE_TOKEN
from api_client import APIClient
from collector import publish
with TemporaryDirectory() as folder:
    with DemoAPI() as base,APIClient(base,PRACTICE_TOKEN) as api:
        rows=api.collect_mock()
    target=Path(folder)/"api-run-01"
    facts=publish(rows,target,provider="mock")
    manifest=json.loads((target/"manifest.json").read_text())
    print("Provider:",manifest["provider"])
    print("Artifacts:",len(list(target.iterdir())))
    print("Items/comments:",facts["items"],facts["comments"])
    print("Open items:",sum(r["state"]=="open" for r in rows))
    print("Issue-only:",sum(r["kind"]=="issue" for r in rows))
''',
    "The complete sequence goes from real local HTTP requests to validated records, a database and a report. The printed results are from the fictional fixture; they are not current GitHub statistics.",
    ('# Paste a real token into lesson HTML to make live mode easy', '# Keep real credentials locally; default to the offline fixture', "Public website source must not contain a usable credential."),
    "Run the default CLI in a fresh temporary folder and verify its six-file summary using the supplied main function.",
    '''from pathlib import Path
from tempfile import TemporaryDirectory
import json
from collector import main
with TemporaryDirectory() as folder:
    target=Path(folder)/"run"
    main([str(target)])
    print(json.loads((target/"summary.json").read_text())["items"])''',
    "Perform a recovery check: a deliberately too-small page cap should leave no published destination.",
    '''from tempfile import TemporaryDirectory
from pathlib import Path
from mock_api import DemoAPI,PRACTICE_TOKEN
from api_client import APIClient,APIError
from collector import publish
with TemporaryDirectory() as folder:
    target=Path(folder)/"incomplete"
    try:
        with DemoAPI() as base,APIClient(base,PRACTICE_TOKEN) as api:
            rows=api.collect_mock(max_pages=2)
        publish(rows,target,provider="mock")
    except APIError:print("Collection stopped before publication")
    print("Published:",target.exists())''',
    "A reliable API pipeline validates every boundary, respects waits, detects incomplete pages and publishes only a complete new result.",
    [("Does default collector mode need a real token?","No","Always","Only on Windows","It uses a public fake credential on numeric loopback."),
     ("How many fixture records are issue-only?","5","6","1","One record is explicitly a pull request."),
     ("How many complete fixture pages are needed?","3","1","6","Six rows arrive in pages of two."),
     ("Does a Requests read timeout guarantee a total workflow deadline?","No","Always","If less than10","It governs a stage of waiting, not the whole pipeline."),
     ("May a long Retry-After be shortened to force a retry?","No","Always","If the API is public","Stop if the required wait exceeds the allowed budget."),
     ("Should a timed-out POST be blindly retried?","No","Always","Only for creation","The operation may already have completed."),
     ("Is .env.example a place for a real token?","No","Always","Only offline","The public template contains names/empty placeholders only."),
     ("Does a parseable JSON body prove success?","No","Always","Only for arrays","HTTP status and application schema must also be checked."),
     ("What happens to a repeated cursor or conflicting id?","Collection stops for review","It is silently skipped","The token is printed","The declared policy avoids concealing page drift."),
     ("Does completed pagination prove a frozen historical census?","No","Always","Only for GitHub","Remote data can change between requests."),
     ("Does a failed two-page collection publish four records as complete?","No","Always","If sorted","Only the terminal complete collection may be published."),
     ("Where does this project store Study Hub progress?","Nowhere; it is a separate practice project","Inside the token","In a public SQL table","The website's existing learning storage is unchanged.")])


def write():
    target=ROOT/"study-hub.html";original=target.read_bytes().decode("utf-8")
    start=original.index("const DAY_TEACH = {");end=original.index("\n};\n\nconst REST_DAY",start)
    if any(('"'+key+'":') in original[start:end] for key in DAYS):
        if "--refresh" not in sys.argv:raise RuntimeError("Week36 exists; refusing overwrite")
        first=original.index('\n"36.0": {',start)
        if not all(('"'+key+'":') in original[first:end] for key in DAYS):raise RuntimeError("Unexpected Week36 block")
        original=original[:first]+original[end:];end=original.index("\n};\n\nconst REST_DAY",start)
    assert [len(day["parts"]) for day in DAYS.values()]==[5,6,5,6,5,5]
    files={name:(FOLDER/name).read_text(encoding="utf-8") for name in ["mock_api.py","api_client.py","collector.py"]}
    bootstrap='import sys,json\nfrom pathlib import Path\nfor name,source in '+repr(files)+'.items():\n    Path(name).write_text(source,encoding="utf-8")\n    sys.modules.pop(name[:-3],None)\nsys.path.insert(0,str(Path.cwd()))\n'
    with tempfile.TemporaryDirectory(prefix="studyhub-w36-verify-") as temp:
        manifest=Path(temp)/"examples.json";result=Path(temp)/"results.json"
        manifest.write_text(json.dumps([bootstrap+code for code,_ in JOBS]),encoding="utf-8")
        subprocess.run([sys.executable,str(ROOT/"scripts"/"python-example-worker.py"),str(manifest),str(result)],check=True,timeout=300,
            env={**os.environ,"MPLBACKEND":"Agg","OPENBLAS_NUM_THREADS":"1","PYTHONDONTWRITEBYTECODE":"1"})
        results=json.loads(result.read_text(encoding="utf-8"))
    for (_,destination),result in zip(JOBS,results,strict=True):
        destination["v" if destination["t"]=="out" else "out"]=result["out"]
    DAYS["36.0"]["parts"][0]["sections"].insert(3,sec("sh","python -m pip install -r requirements.txt\npython mock_api.py"))
    DAYS["36.0"]["parts"][0]["sections"].insert(4,sec("tip","First download mock_api.py, api_client.py, collector.py, requirements.txt and README.md from docs/python-week36 and keep them together in a new practice folder. Install requirements once. The standalone mock_api.py command is for browser inspection; Python snippets automatically start/close their own server. Requests and python-dotenv must already be installed for offline use. Verified with Python3.12.14, Requests2.34.2 and python-dotenv1.2.4. Every example was executed against supplied fictional fixtures; no real token was read."))
    final=DAYS["36.5"]["parts"][4]["sections"]
    final.extend([sec("sh","python collector.py api-run-01\npython collector.py api-run-02 --max-pages 2\npython collector.py --help"),
        sec("p","Project folder: docs/python-week36 in the repository. Default mode is the offline loopback drill. The intentionally too-small max-pages 2 command fails without publishing a result. Optional --github OWNER/REPO needs internet and your locally configured STUDYHUB_API_TOKEN; no token belongs in this HTML, a report or a public commit."),
        sec("p","Primary references: https://requests.readthedocs.io/en/latest/user/quickstart/ · https://requests.readthedocs.io/en/latest/user/advanced/ · https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods · https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Retry-After · https://docs.github.com/en/rest/issues/issues · https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api · https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api . Explanations, exercises, fictional fixtures and recorded outputs are original and embedded for offline reading.")])
    addition="\n".join(json.dumps(k)+": "+json.dumps(v,ensure_ascii=False,indent=2)+"," for k,v in DAYS.items()).replace("</","<\\/")
    prefix=original[:end].rstrip()
    if not prefix.endswith(","):prefix+=","
    temporary=target.with_suffix(".html.tmp")
    temporary.write_bytes((prefix+"\n"+addition+original[end:]).encode("utf-8"));temporary.replace(target)
    print("Added Week36:6days,32parts,64practice prompts,74explained quiz questions,96executed examples/solutions; all earlier lessons/application/storage unchanged.")


if __name__=="__main__":
    write()

