"""Append only Week37 teaching data after executing every authored snippet."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap

ROOT = Path(__file__).resolve().parents[1]
DAYS = {f"37.{d}": {"parts": []} for d in range(6)}
JOBS = []


def clean(code):
    return textwrap.dedent(code).strip() + "\n"


def sec(t, v=None, **extra):
    return {"t": t, **({"v": v} if v is not None else {}), **extra}


def lesson(day, title, goal, terms, explanation, syntax, example, walkthrough,
           mistake, task, solution, challenge, challenge_code, takeaway, quizzes):
    parts = DAYS[f"37.{day}"]["parts"]
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
        sec("p", explanation), sec("syn", syntax, note="Python/HTML pattern. The complete example uses Flask's local test client or in-memory templates; no external server is needed."),
        sec("code", clean(example)), output, sec("p", walkthrough),
        sec("mis", wrong=mistake[0], right=mistake[1], why=mistake[2]),
        sec("ex", task, practiceId=f"37.{day}.{index}.build"), build,
        sec("ex", "Mini challenge: " + challenge, practiceId=f"37.{day}.{index}.challenge"), stretch,
        sec("try", q=quizzes[0][0], code="# Predict, then explain before revealing.", a=quizzes[0][1], why=quizzes[0][4]),
        sec("checkpoint", lesson={"id": f"course:37.{day}.{index}", "quiz": questions}), sec("key", takeaway)
    ]})
    JOBS.extend([(clean(example), output), (clean(solution), build), (clean(challenge_code), stretch)])


BASIC='from flask import Flask\napp=Flask(__name__)\napp.config["TESTING"]=True\n'


def demo(body):
    return BASIC+clean(body)


def project(body):
    return 'from app import create_app\napp=create_app({"TESTING":True})\n'+clean(body)


lesson(0,"1. From an HTTP client to a web application",
    "Explain what Flask does between a request and a browser response.",
    [("Flask; web framework; WSGI", "Flask helps Python map requests to functions and create responses. A WSGI server calls the application; Flask is not itself a browser or a production hosting service."),
     ("Flask(__name__); app object", "The app object holds routes/configuration. __name__ identifies this Python module so Flask can locate resources such as templates and static files."),
     ("Route decorator; view function", "@app.get('/') registers the function below as the handler for GET /. The decorator connects a URL rule to a Python function; it does not call the function immediately."),
     ("test_client", "app.test_client sends simulated HTTP requests through Flask in process, without opening a network port. It lets us execute lesson examples offline; a real browser server is introduced separately.")],
    "Last week Python requested another service. Now Python becomes the application receiving the request. "
    "A browser asks for a URL, a server passes the request to Flask, Flask selects a view, and the returned value becomes an HTTP response. "
    "The first view returns a small HTML paragraph. The test client requests the route and prints the returned status and body. "
    "TESTING=True makes unexpected application failures visible during tests; it is not a production configuration. "
    "Run each example in a fresh practice folder after installing Flask. These introductory snippets are complete and need no browser, public host, token or prior snippet state.",
    'app=Flask(__name__)\n@app.get("/")\ndef home():\n    return "<p>Hello from Python</p>"',
    demo('@app.get("/")\ndef home():\n    return "<p>Hello from Python</p>"\nwith app.test_client() as client:\n    response=client.get("/")\n    print(response.status_code,response.get_data(as_text=True))'),
    "The view returns HTML; Flask produces a200response. get_data(as_text=True) decodes the response body so we can inspect what a browser would receive.",
    ('home()  # assume this alone registers a URL', '@app.get("/")\ndef home():\n    return "<p>Hello</p>"', "Registration connects the function to the request router."),
    "Create GET /welcome returning a short paragraph and verify its status/body.",
    demo('@app.get("/welcome")\ndef welcome():\n    return "<p>Welcome, learner</p>"\nwith app.test_client() as client:\n    r=client.get("/welcome");print(r.status_code,r.get_data(as_text=True))'),
    "Request a URL that has no registered view and inspect the status without treating it as a crash.",
    demo('@app.get("/")\ndef home():return "Home"\nwith app.test_client() as client:\n    print(client.get("/missing").status_code)'),
    "A route maps a request to a view; a view returns a response. Test-client execution is not a public deployment.",
    [("Who selects the view for a matching request?","Flask's router","The SQLite primary key","The CSS file","Registered route rules connect paths/methods to views."),
     ("Does test_client open an internet server?","No","Always","Only for HTML","It exercises the application in process.")])

lesson(0,"2. Response bodies, status codes and headers",
    "Return an intentional response instead of assuming every value means the same thing.",
    [("Return tuple; make_response; dictionary JSON", "A view may return body, status and headers. make_response creates a Response you can configure. Returning a dict is converted to JSON by Flask."),
     ("HTML versus JSON Content-Type", "A string normally becomes an HTML response; a dict becomes JSON. The browser/client uses the media type to interpret the body.")],
    "A page and an API endpoint can live in the same application, but they have different representation contracts. "
    "Return HTML for a page and JSON for a small machine-readable health endpoint. Do not tell a client to parse every HTML page as JSON. "
    "Status200means a successful request; a missing application record can deliberately return404. That is separate from an unexpected Python exception. "
    "Headers supply metadata such as a teaching marker. They are not another place to embed a password. "
    "The example returns202for an accepted demonstration response; it does not claim to have scheduled a real background job.",
    'return {"ok":True}\nreturn "<p>Accepted</p>",202,{"X-Practice":"Week37"}',
    demo('@app.get("/health")\ndef health():return {"ok":True}\n@app.get("/accepted")\ndef accepted():return "<p>Accepted demo</p>",202,{"X-Practice":"Week37"}\nwith app.test_client() as client:\n    a=client.get("/health");b=client.get("/accepted")\n    print(a.status_code,a.mimetype,a.get_json())\n    print(b.status_code,b.mimetype,b.headers["X-Practice"])'),
    "get_json reads the JSON response. mimetype identifies each representation. The explicit202belongs only to the demonstration route.",
    ('return {"ok":True}  # assume this renders a full HTML page', 'return render_template("home.html",...)  # HTML page; taught on Day3', "Choose a representation for the consumer rather than relying on appearance."),
    "Return a deliberate404JSON result for one fixed missing-resource example.",
    demo('@app.get("/example")\ndef example():return {"error":"Fictional item missing"},404\nwith app.test_client() as client:\n    r=client.get("/example");print(r.status_code,r.get_json())'),
    "Use make_response to add a harmless custom header to an HTML page.",
    demo('from flask import make_response\n@app.get("/")\ndef home():\n    r=make_response("<p>Learning desk</p>");r.headers["X-Lesson"]="response";return r\nwith app.test_client() as client:\n    r=client.get("/");print(r.status_code,r.headers["X-Lesson"])'),
    "A response has body, status and headers. Make all three agree with the route's purpose.",
    [("What happens when a view returns a dict?","Flask produces JSON","It becomes a SQL table","It cannot be returned","Flask serialises a dictionary response."),
     ("Is a deliberate404necessarily a Python crash?","No","Always","Only for JSON","A missing record can be a handled application result.")])

lesson(0,"3. Test requests before opening a browser",
    "Verify route behaviour with statuses, bodies and request methods.",
    [("Test response; get_data; get_json", "Flask's test response exposes status_code, headers, decoded body and JSON. Tests can inspect the application contract without external network variability."),
     ("HEAD and OPTIONS", "Flask normally adds HEAD and OPTIONS for GET routes. HEAD returns headers without a response body; OPTIONS describes permitted methods. They are not extra page views to count as lessons.")],
    "A quick test should ask whether the route exists, whether the intended method is allowed and whether the returned content is correct. "
    "The same client can send GET, POST and HEAD. POST to a GET-only route normally returns405 Method Not Allowed. "
    "HEAD should not return the page body, even though it can report the same successful resource metadata. "
    "Use assertions for meaningful contracts, not a test that merely repeats the implementation's exact source text. "
    "The test client does not verify CSS layout or real browser navigation; later browser checks cover the final project separately.",
    'with app.test_client() as client:\n    response=client.get("/")\n    assert response.status_code==200',
    demo('@app.get("/")\ndef home():return "<h1>Local desk</h1>"\nwith app.test_client() as client:\n    print("GET:",client.get("/").status_code)\n    print("POST:",client.post("/").status_code)\n    print("HEAD bytes:",len(client.head("/").data))'),
    "The GET succeeds, the unsupported write method fails 405, and HEAD has no response bytes. These results teach different request contracts.",
    ('assert client.get("/")  # unclear intent', 'assert client.get("/").status_code==200', "State the expected response property explicitly."),
    "Add /health returning JSON and assert its ok value is a real boolean.",
    demo('@app.get("/health")\ndef health():return {"ok":True}\nwith app.test_client() as client:\n    r=client.get("/health");assert r.status_code==200\n    print(type(r.get_json()["ok"]) is bool)'),
    "Inspect the Allow header after a POST to a read-only page.",
    demo('@app.get("/read")\ndef read():return "Read only"\nwith app.test_client() as client:\n    r=client.post("/read");print(r.status_code,"GET" in r.headers["Allow"])'),
    "Use in-process tests for request/response contracts and a real browser for visual interaction.",
    [("What normally happens to POST on a GET-only route?","405","200with a hidden write","A database reset","The registered methods do not permit POST."),
     ("Does a successful test-client GET prove mobile CSS is correct?","No","Always","If body contains HTML","Layout needs browser verification.")])

lesson(0,"4. Request context is not a global browser",
    "Access request data only during an active request or deliberate test context.",
    [("request proxy; request context", "flask.request refers to the currently handled request. It is not a permanent global request object usable before a request exists."),
     ("test_request_context", "This context supplies request data for small isolated demonstrations such as URL building. It does not run the full before-request/view/response pipeline like test_client does.")],
    "Multiple requests can carry different arguments. Do not store one request's values in a shared module global and assume they belong to the next visitor. "
    "Inside a view, request.method and request.args refer to that call. Outside a request, using the proxy raises a context error. "
    "A deliberate test_request_context lets us demonstrate request fields, but it is not a substitute for full route integration tests. "
    "Later session values are browser-specific signed-cookie state; app configuration and in-memory lists belong to the server process. Those lifetimes differ. "
    "Keeping lifetimes clear prevents accidental sharing or loss of data.",
    'with app.test_request_context("/search?q=Flask"):\n    print(request.method,request.args["q"])',
    demo('from flask import request\nwith app.test_request_context("/search?q=Flask"):\n    print(request.method,request.path,request.args["q"])\ntry:\n    print(request.method)\nexcept RuntimeError:\n    print("No active request context outside the block")'),
    "The proxy works inside the temporary context and fails clearly afterward. Nothing was sent to a real server.",
    ('current_name=request.args["name"]  # module import time', '# Read request.args inside the view handling that request', "A module import is not an active browser request."),
    "Use two separate contexts and show their query values do not leak into each other.",
    demo('from flask import request\nfor term in ["SQL","Flask"]:\n    with app.test_request_context("/search",query_string={"q":term}):\n        print(request.args["q"])'),
    "Use test_client to execute a real view that reads request.path.",
    demo('from flask import request\n@app.get("/where")\ndef where():return {"path":request.path}\nwith app.test_client() as client:print(client.get("/where").get_json())'),
    "Request data has request lifetime. Use the right test tool and avoid shared request-state globals.",
    [("Can flask.request be used freely at module import time?","No","Always","If Flask is installed","There is no active request then."),
     ("Does test_request_context automatically execute the view?","No","Always","Only for GET","It supplies context, not the full dispatch pipeline.")])

lesson(0,"5. Run the development server locally and keep roles clear",
    "Know the file, command, host and port needed to open a Flask app.",
    [("python -m flask --app; development server", "The Flask CLI imports your application and starts a local development server. Use a normal module name such as hello.py, not flask.py which would shadow the package."),
     ("Loopback; debug mode; GitHub Pages boundary", "127.0.0.1 serves your own computer. Debugging and the built-in server are development tools, not internet production hosting. GitHub Pages serves this course/static files; it does not execute Flask Python.")],
    "Save a small example as hello.py, then run the Flask CLI command shown in the terminal block below. "
    "Open http://127.0.0.1:5000 in the same computer's browser and stop the server with Ctrl+C. If port 5000 is occupied, choose 5001 and use the matching URL. "
    "The excerpt below still uses test_client so every lesson output can be checked without leaving a background server running. "
    "The final app.py has a local debug-off entry point. No Flask service is added to Study Hub's public GitHub Pages hosting. "
    "Keep the complete project folder structure when downloading; templates/static are resources, not optional decoration.",
    'python -m flask --app hello run --host 127.0.0.1 --port 5000\n# Open http://127.0.0.1:5000 ; stop with Ctrl+C.',
    demo('@app.get("/")\ndef home():return "<p>Ready for a local browser</p>"\nwith app.test_client() as client:\n    print(client.get("/").get_data(as_text=True))\nprint("Browser mode: save as hello.py and use the Flask CLI command")'),
    "The command is a separate terminal action, not a line of Python to paste inside a function. A running local server is required for browser mode.",
    ('# Rename the application flask.py', '# Use hello.py or app.py so the installed flask package remains importable', "A conflicting filename can shadow the dependency."),
    "Inspect the application name and count only its custom rule, excluding the automatic static endpoint.",
    demo('@app.get("/")\ndef home():return "Hello"\nprint(sorted(rule.rule for rule in app.url_map.iter_rules() if rule.endpoint!="static"))'),
    "Create two independent app objects and prove registering one does not register the other.",
    '''from flask import Flask
a=Flask("first");b=Flask("second")
@a.get("/only-a")
def only_a():return "A"
print(a.test_client().get("/only-a").status_code,b.test_client().get("/only-a").status_code)''',
    "Static hosting publishes lessons; a local Python server executes Flask. Know which program you are opening.",
    [("Will GitHub Pages execute app.py as a Flask server?","No","Always","If the file is public","It is static hosting for this repository."),
     ("What address keeps the practice server on this computer?","127.0.0.1","0.0.0.0for public access","A session cookie","Loopback is the intended local teaching scope.")])

lesson(1,"1. Five routes, five deliberate page purposes",
    "Register meaningful URLs with distinct endpoint names.",
    [("Endpoint; URL rule", "An endpoint normally uses the view function's name; the URL rule is its path. They are related but different. Endpoint names must not collide accidentally.")],
    "A small app can have home, lessons, planner, settings and about pages. Each URL should answer a clear visitor task. "
    "Use separate view names so URL building can refer to endpoints unambiguously. A function named about need not have the path /about if the rule changes. "
    "A route with a trailing slash and one without it have different canonical behaviour. Do not add arbitrary slashes to every URL. "
    "The example uses add_url_rule, an explicit registration method equivalent in purpose to a route decorator. Its fixed handlers return small text pages. "
    "Later templates provide a consistent layout rather than copying full HTML into five Python strings.",
    'app.add_url_rule("/about",endpoint="about",view_func=about_view)\n# Decorators normally supply endpoint from the function name.',
    demo('def page(title):\n    def view():return "<h1>"+title+"</h1>"\n    return view\nfor path,endpoint,title in [("/","home","Home"),("/lessons","lessons","Lessons"),("/planner","planner","Planner"),("/settings","settings","Settings"),("/about","about","About")]:\n    app.add_url_rule(path,endpoint=endpoint,view_func=page(title))\nwith app.test_client() as client:\n    print([(path,client.get(path).status_code) for path in ["/","/lessons","/planner","/settings","/about"]])'),
    "Five different endpoints all respond to their intended GET path. The title strings are fixed developer text, not unescaped visitor input.",
    ('# Give unrelated views the same endpoint name accidentally', '# Use meaningful unique view/endpoint names', "URL building and registration need unambiguous identifiers."),
    "Register /about with a normal decorator and inspect its endpoint name.",
    demo('@app.get("/about")\ndef about():return "About this desk"\nprint([(r.rule,r.endpoint) for r in app.url_map.iter_rules() if r.endpoint=="about"])'),
    "Register a canonical /projects/route and inspect the redirect when the final slash is omitted.",
    demo('@app.get("/projects/")\ndef projects():return "Projects"\nwith app.test_client() as client:\n    r=client.get("/projects");print(r.status_code,r.headers["Location"].endswith("/projects/"))'),
    "Choose page purposes, endpoint names and canonical paths before adding navigation.",
    [("Is an endpoint name always identical to its URL text?","No","Always","Only when using HTML","The endpoint identifies a view; the rule defines its path."),
     ("Should unrelated views accidentally share an endpoint?","No","Always","If both return200","Registration and URL building need distinct identities.")])

lesson(1,"2. Dynamic paths and converters",
    "Receive typed path values and handle unknown application records.",
    [("Path variable; int converter", "<int:lesson_id> matches a compatible integer path segment and passes it to the view as an int. It does not prove a record with that id exists."),
     ("abort(404)", "abort raises a handled HTTP error for an absent record. An invalid path shape and a valid-shaped unknown id can both return404for different reasons.")],
    "A lesson detail page needs an id. The converter checks URL shape before the view runs. "
    "Then the view looks up that id in the application's current data. /lessons/99can match the route while still having no matching record. "
    "Do not assume an id being numeric grants access to an object or proves its existence; authorisation is a separate later topic. "
    "For text variables, escape output or render through Jinja instead of returning raw untrusted HTML. "
    "The fixed two-record dictionary here is a small teaching data source, not the user's curriculum database.",
    '@app.get("/lessons/<int:lesson_id>")\ndef detail(lesson_id):\n    # Validate existence, then render.',
    demo('from flask import abort\nrecords={1:"HTTP",2:"Flask"}\n@app.get("/lessons/<int:lesson_id>")\ndef detail(lesson_id):\n    if lesson_id not in records:abort(404)\n    return {"id":lesson_id,"title":records[lesson_id]}\nwith app.test_client() as client:\n    print(client.get("/lessons/2").get_json())\n    print("Unknown:",client.get("/lessons/99").status_code,"Wrong shape:",client.get("/lessons/abc").status_code)'),
    "The known record returns an integer id in JSON. Unknown99and text abc both produce404, but only99entered the view.",
    ('return records[lesson_id]  # assume every numeric id exists', 'if lesson_id not in records:abort(404)', "A converter validates shape, not application existence."),
    "Create /square/<int:value>returning a JSON result for7.",
    demo('@app.get("/square/<int:value>")\ndef square(value):return {"result":value*value}\nwith app.test_client() as client:print(client.get("/square/7").get_json())'),
    "Use a string path parameter and render it safely with escape from MarkupSafe.",
    demo('from markupsafe import escape\n@app.get("/hello/<name>")\ndef hello(name):return "<p>Hello "+str(escape(name))+"</p>"\nwith app.test_client() as client:\n    print(client.get("/hello/%3Cb%3EAsha").status_code)\n    print(client.get("/hello/%3Cb%3E").get_data(as_text=True))'),
    "Converters help route matching; record lookup and safe rendering remain your responsibility.",
    [("Does <int:id>prove a database record exists?","No","Always","If positive","Existence needs an application lookup."),
     ("Should unknown ids cause an unhandled KeyError?","No","Always","Only in tests","Return a deliberate missing-resource response.")])

lesson(1,"3. Build paths with url_for",
    "Generate links from endpoints and parameters instead of duplicating path strings.",
    [("url_for; query arguments; BuildError", "url_for('detail',lesson_id=2) builds the registered path. Extra arguments become query parameters. A missing endpoint or required value causes a URL-building error.")],
    "If you rename a route path, links written as fixed strings can become stale. Refer to the endpoint with url_for instead. "
    "Pass dynamic values as keyword arguments so Flask handles path encoding. Unknown-to-the-rule values become query parameters. "
    "URL building normally needs application/request context; a small test_request_context is appropriate for this isolated example. "
    "url_for chooses a route; it does not authorise a user or verify the target record exists. "
    "In templates Flask exposes url_for automatically, so navigation and form action URLs can use the same endpoint definitions.",
    'url_for("detail",lesson_id=2)\nurl_for("search",q="Python & SQL")',
    demo('from flask import url_for\n@app.get("/lesson/<int:lesson_id>")\ndef detail(lesson_id):return str(lesson_id)\n@app.get("/search")\ndef search():return "Search"\nwith app.test_request_context():\n    print(url_for("detail",lesson_id=2))\n    print(url_for("search",q="Python & SQL"))'),
    "The first URL includes the path id. The second encodes the ampersand as data in q, matching last week's URL-encoding lesson.",
    ('href="/old-detail-path/2"', 'href="{{ url_for(\'detail\',lesson_id=2) }}"', "Endpoint-based links stay aligned with route definitions."),
    "Build an about URL after registering it at /info instead of /about.",
    demo('from flask import url_for\n@app.get("/info")\ndef about():return "About"\nwith app.test_request_context():print(url_for("about"))'),
    "Attempt to build a dynamic URL without its required id and handle BuildError.",
    demo('from flask import url_for\nfrom werkzeug.routing import BuildError\n@app.get("/items/<int:item_id>")\ndef detail(item_id):return str(item_id)\nwith app.test_request_context():\n    try:url_for("detail")\n    except BuildError:print("Required path value missing")'),
    "Build links from endpoint contracts, then still validate the destination record when requested.",
    [("What happens to extra url_forarguments not in the path rule?","They become query parameters","They grant access","They overwrite a session","Flask encodes them into the query."),
     ("Does url_forprove a requested record exists?","No","Always","If it builds successfully","It builds a route-shaped URL only.")])

lesson(1,"4. Query strings and allowed methods",
    "Read filters without changing data and reject unsupported methods.",
    [("request.args; getlist; type conversion", "request.args holds query values. get reads one value; getlist reads repeated values. Conversion with a default can hide invalid input, so explicitly validate when malformed values must be rejected."),
     ("request.method; @app.post", "A route can allow selected methods. Use GET for retrieving a filtered view and POST for an intended state change; method separation is not a substitute for validation or CSRF handling.")],
    "A search query belongs in the URL so it can be bookmarked and revisited. It should not add a note merely because a browser loads it. "
    "Repeated tag parameters need getlist when the contract permits multiple tags. Calling get alone returns only one value. "
    "Decide whether bad numeric input means an error or a default. Do not silently turn page=bananainto page1and then claim input was valid. "
    "Flask routes normally permit only GET unless methods are added. A dedicated @app.post makes a write route's intent visible. "
    "These simple request-shape examples do not implement real account writes; the final local form project includes a matching per-session token.",
    'term=request.args.get("q","").strip()\ntags=request.args.getlist("tag")\n@app.post("/submit")',
    demo('from flask import request\n@app.get("/search")\ndef search():return {"q":request.args.get("q",""),"tags":request.args.getlist("tag")}\nwith app.test_client() as client:\n    print(client.get("/search",query_string=[("q","Flask"),("tag","web"),("tag","python")]).get_json())\n    print(client.post("/search").status_code)'),
    "The repeated tags remain a list. POST is not allowed on the read-only search route.",
    ('tag=request.args.get("tag")  # assume all repeated tags returned', 'tags=request.args.getlist("tag")', "The access method should match the parameter contract."),
    "Explicitly reject a nonnumeric positive page parameter.",
    demo('from flask import request,abort\n@app.get("/page")\ndef page():\n    raw=request.args.get("page","1")\n    if not raw.isascii() or not raw.isdecimal() or not 1<=int(raw)<=100:abort(400)\n    return {"page":int(raw)}\nwith app.test_client() as client:\n    print(client.get("/page?page=2").get_json(),client.get("/page?page=banana").status_code)'),
    "Add a POST-only acknowledgement endpoint and show GET gets405without mutating anything.",
    demo('@app.post("/ack")\ndef acknowledge():return {"accepted":True}\nwith app.test_client() as client:print(client.get("/ack").status_code,client.post("/ack").get_json())'),
    "Use query strings for read filters, preserve repeated values deliberately and validate malformed input explicitly.",
    [("Which access method reads repeated tag values?","getlist","get alone always","url_for","The query can contain multiple values for one key."),
     ("Should a normal search GET create a note?","No","Always","If bookmarked","A read filter should not perform that write.")])

lesson(1,"5. Redirects and useful missing-page responses",
    "Return deliberate redirects and preserve meaningful error statuses.",
    [("redirect;303; follow_redirects", "redirect creates a3xxresponse with Location.303instructs the next request to use GET after a successful POST. The test client can follow the chain for verification."),
     ("errorhandler; response status", "An error handler can render a useful page, but must still return the correct status. A pretty missing page with200misleads clients and tests.")],
    "A renamed page can redirect to its new endpoint; a successful form can redirect to a results page to avoid resubmitting on refresh. "
    "Use a fixed url_for destination instead of reflecting an arbitrary next URL supplied by a visitor. An unchecked external redirect can send someone to an unintended site. "
    "A missing lesson should render a helpful page but keep404. Rendering a template alone defaults to200unless you return the status too. "
    "follow_redirects=True lets a test inspect the final body and redirect history. It should not conceal an unexpected infinite loop. "
    "Later Post/Redirect/Get applies this response pattern to a validated form submission.",
    'return redirect(url_for("home"),code=303)\n@app.errorhandler(404)\ndef missing(error):return "<h1>Not found</h1>",404',
    demo('from flask import redirect,url_for\n@app.get("/")\ndef home():return "Home"\n@app.get("/start")\ndef start():return redirect(url_for("home"),code=303)\n@app.errorhandler(404)\ndef missing(error):return "<h1>Page not found</h1>",404\nwith app.test_client() as client:\n    r=client.get("/start",follow_redirects=True)\n    print(r.status_code,len(r.history),r.get_data(as_text=True))\n    print(client.get("/missing").status_code)'),
    "The final home response is200after one redirect. A missing path still returns404with a readable page.",
    ('@app.errorhandler(404)\ndef missing(error):return "<h1>Not found</h1>"', '@app.errorhandler(404)\ndef missing(error):return "<h1>Not found</h1>",404', "The error page's appearance must not erase its status."),
    "Return a303redirect and inspect Location before following it.",
    demo('from flask import redirect,url_for\n@app.get("/target")\ndef target():return "Target"\n@app.get("/old")\ndef old():return redirect(url_for("target"),code=303)\nwith app.test_client() as client:\n    r=client.get("/old");print(r.status_code,r.headers["Location"])'),
    "Add a handled405response with a useful message and retain405.",
    demo('@app.get("/read")\ndef read():return "Read"\n@app.errorhandler(405)\ndef method_error(error):return "Use the documented method",405\nwith app.test_client() as client:\n    r=client.post("/read");print(r.status_code,r.get_data(as_text=True))'),
    "Redirect to an intended local endpoint and keep error statuses accurate even when rendering a friendly page.",
    [("Should a friendly missing-page response retain404?","Yes","Never","Only if JSON","Clients need the correct error status."),
     ("What does303normally cause after POST?","A follow-up GET","An automatic duplicate POST","A session deletion","It implements the redirect-to-read part of PRG.")])

lesson(2,"1. Jinja renders data into HTML",
    "Separate trusted template structure from passed data.",
    [("Jinja; render_template_string; {{ expression }}", "Jinja is Flask's template engine. {{ name }} inserts a passed value. render_template_string uses a developer-written template string; never treat visitor text as template source."),
     ("Template context; autoescaping", "Keyword arguments provide template data. Flask autoescapes render_template_string content and normal HTML template files so data such as <b> is displayed as text rather than becoming markup.")],
    "Building a page by concatenating Python strings becomes hard to maintain and easy to render unsafely. Pass data to a trusted template instead. "
    "The template contains HTML structure and an expression placeholder. A visitor's value belongs in that placeholder, not in the template source string. "
    "The first example passes a title containing angle brackets. Jinja escapes them automatically. "
    "This protects an HTML text context; other contexts such as script code or untrusted URL schemes require their own deliberate handling. Do not assume autoescaping solves every possible context. "
    "render_template_string is a compact teaching tool; the project uses normal files in templates/.",
    'render_template_string("<h1>{{ title }}</h1>",title="Flask basics")',
    demo('from flask import render_template_string\n@app.get("/")\ndef home():return render_template_string("<h1>{{ title }}</h1>",title="<b>Flask basics</b>")\nwith app.test_client() as client:\n    print(client.get("/").get_data(as_text=True))'),
    "The h1is trusted structure, while the passed b-like text is escaped. The browser should show literal angle-bracket text inside the heading.",
    ('render_template_string(visitor_input)  # untrusted template source', 'render_template_string("<p>{{ value }}</p>",value=visitor_input)', "Template source is code-like structure; visitor content must stay data."),
    "Render a name and a fixed learning objective using two passed variables.",
    demo('from flask import render_template_string\n@app.get("/")\ndef home():return render_template_string("<h1>{{ name }}</h1><p>{{ goal }}</p>",name="Asha",goal="Explain a route")\nwith app.test_client() as client:print(client.get("/").get_data(as_text=True))'),
    "Pass a value that looks like a Jinja expression and verify it remains literal data.",
    demo('from flask import render_template_string\n@app.get("/")\ndef home():return render_template_string("<p>{{ value }}</p>",value="{{ 7*7 }}")\nwith app.test_client() as client:print(client.get("/").get_data(as_text=True))'),
    "Trusted template structure and untrusted data must stay separate; rendering data is not executing it as a template.",
    [("Should visitor text be passed as template source?","No","Always","If it is short","Keep it in variables in a trusted template."),
     ("What does {{ title }}do?","Inserts a context expression","Runs an SQL migration","Registers a route","Jinja evaluates the expression within the template context.")])

lesson(2,"2. Move templates into named files",
    "Use render_template with a predictable resource location.",
    [("templates folder; render_template", "Flask normally finds templates in a templates folder relative to the app module/package. render_template('home.html',...) loads that named resource."),
     ("DictLoader; TemplateNotFound", "Jinja DictLoader provides named in-memory templates for self-contained examples. It models filenames without writing them. A missing named template raises TemplateNotFound, not a route404.")],
    "A real project should have Python routes and separate HTML files. Keep the folder structure when copying or downloading it. "
    "The example uses a named in-memory template so it is immediately runnable; the final app uses actual templates/home.html and other files. "
    "The route chooses data and render_template chooses presentation. A template does not automatically fetch a database record. "
    "Flask locating the wrong resource folder can look like an HTML error even when the route is correct. Inspect module location, spelling and filename case. "
    "A missing template is a development problem to fix, not an ordinary missing lesson to disguise as success.",
    'return render_template("home.html",title="My desk")\n# Real file: templates/home.html',
    demo('from flask import render_template\nfrom jinja2 import DictLoader\napp.jinja_loader=DictLoader({"home.html":"<h1>{{ title }}</h1>"})\n@app.get("/")\ndef home():return render_template("home.html",title="My desk")\nwith app.test_client() as client:print(client.get("/").get_data(as_text=True))'),
    "The named loader supplies home.html. Switching from DictLoader to real files leaves the route's render_template call unchanged.",
    ('render_template("templates/home.html")  # normal root loader', 'render_template("home.html")', "Template names are relative to the template search directory."),
    "Create two named in-memory templates and render the about page.",
    demo('from flask import render_template\nfrom jinja2 import DictLoader\napp.jinja_loader=DictLoader({"home.html":"Home","about.html":"<p>{{ purpose }}</p>"})\n@app.get("/about")\ndef about():return render_template("about.html",purpose="Local Flask practice")\nwith app.test_client() as client:print(client.get("/about").get_data(as_text=True))'),
    "Attempt to render a missing named template and identify TemplateNotFound under testing mode.",
    demo('from flask import render_template\nfrom jinja2 import DictLoader,TemplateNotFound\napp.jinja_loader=DictLoader({})\n@app.get("/")\ndef home():return render_template("absent.html")\ntry:app.test_client().get("/")\nexcept TemplateNotFound:print("Template resource missing: fix the project files")'),
    "Routes identify operations; named templates identify presentation resources. Preserve their directory structure.",
    [("Does render_template('home.html') normally need a templates/ prefix?","No","Always","Only for HTML","The loader already searches the template directory."),
     ("Is TemplateNotFound the same as an unknown record404?","No","Always","Only in testing","It signals an absent presentation resource.")])

lesson(2,"3. Loops, empty states and data-driven cards",
    "Render a list without duplicating page markup.",
    [("{% for %}; loop.index; for-else", "Jinja control statements use {% ... %}. A for loop repeats markup; loop.index counts from1. The loop's else block renders when there are no items."),
     ("Dictionary attributes in templates", "Jinja can access simple dictionary fields with lesson.title for these examples; use consistent known keys. A missing field should not silently conceal a broken data contract.")],
    "Pass a list of approved lesson dictionaries to the template. One card pattern can render every record. "
    "The view prepares the data; the template presents it. Do not embed database writes or complex data cleaning in a display loop. "
    "A filtered empty result is not a broken page. Give it a readable empty state such as No matching lessons. "
    "The loop index is display numbering, not a durable record key. Links should use lesson.id, even when records are reordered. "
    "The example renders a nonempty list and a separate empty state using the same template.",
    '{% for lesson in lessons %}<li>{{ loop.index }}. {{ lesson.title }}</li>{% else %}<li>No lessons</li>{% endfor %}',
    demo('from flask import render_template_string\nTEMPLATE="<ul>{% for lesson in lessons %}<li>{{ loop.index }}. {{ lesson.title }}</li>{% else %}<li>No lessons</li>{% endfor %}</ul>"\n@app.get("/")\ndef home():return render_template_string(TEMPLATE,lessons=[{"id":8,"title":"Routes"},{"id":3,"title":"Templates"}])\n@app.get("/empty")\ndef empty():return render_template_string(TEMPLATE,lessons=[])\nwith app.test_client() as client:\n    print(client.get("/").get_data(as_text=True))\n    print(client.get("/empty").get_data(as_text=True))'),
    "Display numbers1and2do not replace record ids8and3. The empty route shows a deliberate message rather than a blank list.",
    ('href="/lessons/{{ loop.index }}"', 'href="{{ url_for(\'detail\',lesson_id=lesson.id) }}"', "Display position changes when the list is filtered or reordered."),
    "Render three fictional topic labels from one loop.",
    demo('from flask import render_template_string\n@app.get("/")\ndef home():return render_template_string("{% for topic in topics %}<p>{{ topic }}</p>{% endfor %}",topics=["HTTP","SQL","Flask"])\nwith app.test_client() as client:print(client.get("/").get_data(as_text=True))'),
    "Render the same card template with an empty list and assert its empty-state text is present.",
    demo('from flask import render_template_string\n@app.get("/")\ndef home():return render_template_string("{% for row in rows %}{{ row.title }}{% else %}Nothing matched{% endfor %}",rows=[])\nwith app.test_client() as client:print("Nothing matched" in client.get("/").get_data(as_text=True))'),
    "Repeat structure with loops, preserve true record keys and design the empty state as carefully as the populated one.",
    [("Is loop.index a stable record identity?","No","Always","If the list is short","It is the current display position."),
     ("When does a Jinja for-else block run?","When the sequence is empty","After every item","Only on HTTP errors","It supplies an empty-state presentation.")])

lesson(2,"4. Conditions, filters and responsible template logic",
    "Use simple presentation choices while keeping calculations explicit.",
    [("{% if %}; filters; length; default", "Conditions choose markup. Filters transform display values: title adjusts case, length counts, default supplies a fallback for undefined values under its options. They do not validate upstream data."),
     ("Undefined versus false/empty", "A missing template value and a valid empty value differ. Do not replace missing required data with a cheerful default that hides a programming error.")],
    "A template may choose whether to show a duration badge or an empty-state prompt. That is presentation logic. "
    "Calculate complex results in Python where they can be tested and explained, then pass them in a clear context. "
    "The example uses title and length to display known strings/list sizes. It does not infer whether a lesson is complete or change progress. "
    "A default is useful for a genuinely optional description; it must not turn a missing required title into an apparently valid record. "
    "Never use a truthy text string such as 'false' when a real boolean is intended. Prepare proper data types in Python.",
    '{{ title|title }}\n{% if lessons %}{{ lessons|length }} lessons{% else %}No lessons{% endif %}',
    demo('from flask import render_template_string\n@app.get("/")\ndef home():return render_template_string("<h1>{{ title|title }}</h1>{% if lessons %}<p>{{ lessons|length }} lessons</p>{% else %}<p>No lessons</p>{% endif %}",title="my learning desk",lessons=[1,2,3])\nwith app.test_client() as client:print(client.get("/").get_data(as_text=True))'),
    "The heading is formatted for display and the supplied sequence count is3. No stored source values were modified.",
    ('{% if "false" %}Complete{% endif %}', '{% if is_complete %}Complete{% else %}Keep practising{% endif %}', "Use a real boolean rather than a nonempty string."),
    "Render an optional description with a default while still passing a required title.",
    demo('from flask import render_template_string\n@app.get("/")\ndef home():return render_template_string("<h1>{{ title }}</h1><p>{{ description|default(\'No description yet\') }}</p>",title="Routes")\nwith app.test_client() as client:print(client.get("/").get_data(as_text=True))'),
    "Pass Falseand render the correct incomplete label.",
    demo('from flask import render_template_string\n@app.get("/")\ndef home():return render_template_string("{% if complete %}Complete{% else %}Keep practising{% endif %}",complete=False)\nwith app.test_client() as client:print(client.get("/").get_data(as_text=True))'),
    "Keep templates focused on presentation and make required data/type contracts explicit before rendering.",
    [("Is a template default a substitute for required-field validation?","No","Always","If it looks nice","It can conceal a broken upstream contract."),
     ("Is the string 'false' false in a normal truth test?","No","Always","Only in templates","It is nonempty text, not a boolean False.")])

lesson(2,"5. Escaping, safe markup and trusted template boundaries",
    "Keep user text as text and understand why disabling escaping is risky.",
    [("Autoescape; |safe; Markup", "Autoescape protects HTML text/attribute rendering for normal HTML templates. |safe or Markup marks content as trusted HTML; never apply it to arbitrary user input."),
     ("HTML context versus URL policy", "Escaping quotes does not decide whether a URL scheme is acceptable. Build local links with url_for and validate any externally supplied link under a separate policy.")],
    "A note may contain <script>as literal text. The page must display it without executing it. "
    "Jinja autoescaping turns angle brackets into entities. Do not add |safejust to make an entered string look like formatted HTML. "
    "Trusted static template markup can contain real tags; the boundary is between template structure and passed user data. "
    "Attribute values must be quoted too. Avoid putting arbitrary strings directly into inline JavaScript or style contexts, where HTML escaping alone is not the full answer. "
    "The final app has no user HTML rendering feature. Its names, queries and notes remain escaped text.",
    '<p>{{ note }}</p>\n<!-- Do not use {{ note|safe }} for visitor-entered text. -->',
    demo('from flask import render_template_string\n@app.get("/")\ndef home():return render_template_string("<p>{{ note }}</p>",note="<script>alert(1)</script>")\nwith app.test_client() as client:\n    text=client.get("/").get_data(as_text=True)\n    print(text)\n    print("Raw script absent:","<script>" not in text)'),
    "The returned HTML contains escaped text, not an executable script element. The browser's visible note can still show the original characters.",
    ('{{ visitor_note|safe }}', '{{ visitor_note }}', "Do not turn untrusted data into trusted HTML."),
    "Render a quoted attribute value safely and prove no raw onfocusattribute is injected.",
    demo('from flask import render_template_string\n@app.get("/")\ndef home():return render_template_string(\'<input value="{{ value }}">\',value=\'" onfocus="bad()\')\nwith app.test_client() as client:\n    text=client.get("/").get_data(as_text=True);print(text)\n    print(\'value="" onfocus=\' not in text)'),
    "Pass a Jinja-like expression as note text and show it is not evaluated a second time.",
    demo('from flask import render_template_string\n@app.get("/")\ndef home():return render_template_string("<p>{{ note }}</p>",note="{{ 2+2 }}")\nwith app.test_client() as client:print(client.get("/").get_data(as_text=True))'),
    "Trusted markup belongs in the template; arbitrary names, notes and queries stay escaped data.",
    [("Should |safe be applied to arbitrary notes?","No","Always","If the note is short","It disables the relevant escaping boundary."),
     ("Does escaping alone make javascript:URLs acceptable?","No","Always","If quoted","URL schemes need a separate policy; local url_forlinks avoid this input path.")])

lesson(3,"1. Template inheritance gives pages one shared layout",
    "Extend a base template instead of copying navigation and page shells.",
    [("{% extends %}; {% block %}", "A base template defines named replaceable blocks such as title/content. A child extends the base and supplies only those sections."),
     ("Shared layout; single source of presentation", "Navigation, document metadata and common footer can live once in the base. Page-specific data and content belong in the child.")],
    "Five pages with duplicated navigation drift when a label or link changes. Put that structure in base.html and extend it. "
    "The child is not a complete independent HTML document pasted inside another document. It fills named blocks in the shared shell. "
    "Keep block names consistent. A misspelled child block can leave the intended area unchanged. "
    "This example uses a DictLoader for self-contained execution; the project writes the same design as real files. "
    "A shared layout reduces repetition without merging unrelated views or changing their route contracts.",
    '{% extends "base.html" %}\n{% block title %}Home{% endblock %}\n{% block content %}<h1>{{ heading }}</h1>{% endblock %}',
    demo('from flask import render_template\nfrom jinja2 import DictLoader\napp.jinja_loader=DictLoader({"base.html":"<title>{% block title %}Desk{% endblock %}</title><nav>Shared nav</nav><main>{% block content %}{% endblock %}</main>","home.html":\'{% extends "base.html" %}{% block title %}Home{% endblock %}{% block content %}<h1>{{ heading }}</h1>{% endblock %}\'})\n@app.get("/")\ndef home():return render_template("home.html",heading="One shared layout")\nwith app.test_client() as client:print(client.get("/").get_data(as_text=True))'),
    "The output has the base navigation and the child's title/heading. There is only one outer layout.",
    ('# Copy the full <html> shell into every child', '{% extends "base.html" %}\n{% block content %}...{% endblock %}', "Children provide changing sections, not duplicated document shells."),
    "Create two children sharing the same footer and verify it appears in each.",
    demo('from flask import render_template\nfrom jinja2 import DictLoader\napp.jinja_loader=DictLoader({"base.html":"<main>{% block content %}{% endblock %}</main><footer>Local desk</footer>","a.html":\'{% extends "base.html" %}{% block content %}A{% endblock %}\',"b.html":\'{% extends "base.html" %}{% block content %}B{% endblock %}\'})\n@app.get("/<page>")\ndef page(page):\n    if page not in {"a","b"}:return "Not found",404\n    return render_template(page+".html")\nwith app.test_client() as client:print(["Local desk" in client.get("/"+p).get_data(as_text=True) for p in ["a","b"]])'),
    "Override a title block and inspect the resulting document title.",
    demo('from flask import render_template\nfrom jinja2 import DictLoader\napp.jinja_loader=DictLoader({"base.html":"<title>{% block title %}Desk{% endblock %}</title>","settings.html":\'{% extends "base.html" %}{% block title %}Settings{% endblock %}\'})\n@app.get("/")\ndef home():return render_template("settings.html")\nwith app.test_client() as client:print(client.get("/").get_data(as_text=True))'),
    "Keep one document shell and replace named sections through inheritance.",
    [("Where should shared navigation normally live?","The base layout","A separate copied version in every child","A session secret","One layout keeps common presentation consistent."),
     ("Does a child need another complete <html>shell inside its content block?","No","Always","Only on mobile","It fills the base document's blocks.")])

lesson(3,"2. Shared navigation, active links and includes",
    "Build links from endpoints and reuse a small presentation fragment.",
    [("{% include %}; request.endpoint", "include renders a named template fragment. request.endpoint identifies the selected view so navigation can indicate the current page."),
     ("aria-current", "aria-current='page' communicates the active navigation link to assistive technology. Visual highlight alone is not the entire interaction.")],
    "The base can include nav.html and use url_for for every internal link. A route path can change without hand-editing all those links. "
    "Mark the selected endpoint as the current page and keep link text readable. The same fragment belongs to all pages using the base. "
    "An include is for presentation reuse, not for hiding complicated application mutations inside a template. "
    "The final app uses ordinary named links and a skip-to-content link. The minimal snippet focuses on active navigation state. "
    "Do not accept an arbitrary filename from a visitor for include/render_template. Choose known presentation resources.",
    '{% include "nav.html" %}\n<a href="{{ url_for(\'about\') }}" {% if request.endpoint==\'about\' %}aria-current="page"{% endif %}>About</a>',
    demo('from flask import render_template\nfrom jinja2 import DictLoader\napp.jinja_loader=DictLoader({"nav.html":\'<a href="{{ url_for("about") }}" {% if request.endpoint=="about" %}aria-current="page"{% endif %}>About</a>\',"about.html":\'{% include "nav.html" %}<h1>About</h1>\'})\n@app.get("/info")\ndef about():return render_template("about.html")\nwith app.test_client() as client:print(client.get("/info").get_data(as_text=True))'),
    "The endpoint is about even though its path is /info. The generated href and current-page metadata reflect the selected view.",
    ('render_template(request.args["template"])', '# Select from fixed known page templates', "Presentation filenames are developer-controlled resources."),
    "Render a reusable small notice fragment inside a page.",
    demo('from flask import render_template\nfrom jinja2 import DictLoader\napp.jinja_loader=DictLoader({"notice.html":"<aside>{{ message }}</aside>","page.html":\'{% include "notice.html" %}<h1>Desk</h1>\'})\n@app.get("/")\ndef home():return render_template("page.html",message="Practice locally")\nwith app.test_client() as client:print(client.get("/").get_data(as_text=True))'),
    "Use request.endpoint in a view's returned JSON to distinguish it from the URL path.",
    demo('from flask import request\n@app.get("/info")\ndef about():return {"endpoint":request.endpoint,"path":request.path}\nwith app.test_client() as client:print(client.get("/info").get_json())'),
    "Reuse small fragments and endpoint-based links; keep template selection controlled.",
    [("Does request.endpoint always equal request.path?","No","Always","Only for includes","Endpoint names and URL rules have different roles."),
     ("What does aria-current='page' communicate?","The active page link","A secret credential","A POST method","It adds accessible current-page information.")])

lesson(3,"3. Serve local CSS with the static endpoint",
    "Keep stylesheet resources in static and build their URLs correctly.",
    [("static directory; static endpoint; send file", "Flask's static endpoint serves developer-owned static resources. url_for('static',filename='style.css') builds their URL. Keep CSS separate from request-handling Python."),
     ("TemporaryDirectory; owned test resources", "This example creates its own temporary static folder and passes that explicit path to Flask. It removes only the resources it created when the context ends.")],
    "HTML describes content; CSS describes presentation. Put the project stylesheet in static/style.css. "
    "A browser loading an HTML page makes another request for the stylesheet linked in its head. A successful page response does not prove that stylesheet URL works. "
    "Use url_forstatic generation instead of a relative path that breaks on nested detail routes. "
    "This snippet writes a tiny developer-owned CSS file in a temporary folder so both the resource request and URL construction can be checked. "
    "The final project has no remote CDN, web fonts or JavaScript dependency, so the local app can render offline.",
    '<link rel="stylesheet" href="{{ url_for(\'static\',filename=\'style.css\') }}">',
    '''from flask import Flask,url_for
from pathlib import Path
from tempfile import TemporaryDirectory
with TemporaryDirectory() as folder:
    Path(folder,"style.css").write_text("body{font-family:system-ui}",encoding="utf-8")
    app=Flask(__name__,static_folder=folder,static_url_path="/static")
    with app.test_request_context():print(url_for("static",filename="style.css"))
    with app.test_client() as client:
        r=client.get("/static/style.css")
        print(r.status_code,r.mimetype)
        r.close()
''',
    "The static response is200and text/css. Explicit static_url_path makes the output stable even though the temporary folder name changes.",
    ('href="static/style.css"  # can resolve relative to a nested URL', 'href="{{ url_for(\'static\',filename=\'style.css\') }}"', "Build the correct application-relative resource path."),
    "Create a tiny owned CSS file and verify the actual body contains the declared colour.",
    '''from flask import Flask
from pathlib import Path
from tempfile import TemporaryDirectory
with TemporaryDirectory() as folder:
    Path(folder,"style.css").write_text("h1{color:teal}",encoding="utf-8")
    app=Flask(__name__,static_folder=folder,static_url_path="/static")
    with app.test_client() as client:
        r=client.get("/static/style.css");print("teal" in r.get_data(as_text=True));r.close()
''',
    "Request a missing static resource and confirm404rather than assuming the page's200covers it.",
    demo('with app.test_client() as client:print(client.get("/static/does-not-exist.css").status_code)'),
    "Check HTML and its assets separately. Local static files preserve offline rendering.",
    [("Does page200prove the CSS loaded?","No","Always","If it has a title","The browser makes a separate stylesheet request."),
     ("Which endpoint builds a static resource URL?","static","SECRET_KEY","request.form","Use url_for('static',filename=...).")])

lesson(3,"4. Responsive, readable HTML is part of the application",
    "Connect semantic markup, viewport settings and flexible CSS.",
    [("Viewport meta; responsive grid; minmax(0,1fr)", "The viewport tag lets mobile browsers use the device width. Flexible grids and a narrow-screen media query adapt layout. minmax(0,1fr) prevents a grid column's intrinsic width from forcing overflow."),
     ("Labels; focus; empty state", "A label associates a form prompt with its control; visible keyboard focus and meaningful empty states support use beyond a mouse. Server correctness does not replace interface usability.")],
    "A functional route can still be uncomfortable to read. Give pages a logical heading, bounded reading width, readable contrast and controls that fit narrow screens. "
    "The project uses local CSS, a two-column area that stacks on mobile, labelled controls and a keyboard skip link. "
    "Its light/dark preference is a small signed-cookie session value, separate from Study Hub's own theme setting. "
    "The example inspects structure, not a full visual result. Real desktop/mobile browser checks are still needed for the finished app. "
    "Avoid fixed widths that require sideways page scrolling for ordinary text; long user notes must wrap instead of expanding a card.",
    '<meta name="viewport" content="width=device-width,initial-scale=1">\n<!-- Flexible columns, then one column on narrow screens. -->',
    demo('from flask import render_template_string\n@app.get("/")\ndef home():return render_template_string(\'<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1"><main><h1>Learning desk</h1><label for="q">Search</label><input id="q" name="q"></main></html>\')\nwith app.test_client() as client:\n    text=client.get("/").get_data(as_text=True)\n    print("Viewport:",\'name="viewport"\' in text,"Label:",\'for="q"\' in text)'),
    "These checks confirm important HTML structure. They do not claim to measure contrast or actual narrow-screen layout.",
    ('<input placeholder="Name">  <!-- no persistent label -->', '<label for="name">Name</label><input id="name" name="name">', "Placeholders disappear and are not a full label replacement."),
    "Render an explicit empty-state heading for a page with no results.",
    demo('from flask import render_template_string\n@app.get("/")\ndef home():return render_template_string("<main><h1>Lessons</h1>{% if rows %}Results{% else %}<h2>No matching lessons</h2><p>Try a broader word.</p>{% endif %}</main>",rows=[])\nwith app.test_client() as client:print("No matching lessons" in client.get("/").get_data(as_text=True))'),
    "Render a labelled multiline note control with a visible maximum length.",
    demo('from flask import render_template_string\n@app.get("/")\ndef home():return render_template_string(\'<label for="body">Practice note</label><textarea id="body" name="body" rows="5" maxlength="200"></textarea>\')\nwith app.test_client() as client:\n    text=client.get("/").get_data(as_text=True);print(\'rows="5"\' in text,\'maxlength="200"\' in text)'),
    "Verify both server behaviour and the browser's reading/input experience.",
    [("Does a placeholder fully replace a label?","No","Always","Only on mobile","A persistent associated label serves a different purpose."),
     ("Can in-process HTML checks prove the visual layout is comfortable?","No","Always","If viewport is present","Use a real browser at desktop/mobile widths too.")])

lesson(3,"5. Shared messages and error pages belong in the layout",
    "Keep navigation and feedback consistent without changing error meaning.",
    [("Shared error child; status preservation", "An error page can extend the same base while its view returns the original400/404/405status. Layout reuse and response semantics are independent."),
     ("Context processor", "A context processor contributes small shared template helpers or values. Keep it lightweight; do not use it for unrelated writes or large hidden queries.")],
    "Missing-page feedback should feel like part of the app, including a way back home. Use the base layout rather than an unrelated plain error screen. "
    "A small shared helper can supply a form token function later, so each template does not need a repeated argument. "
    "Do not silently calculate or mutate important state inside a context processor on every render. Template rendering should remain understandable. "
    "The example contributes a fixed practice label and renders a404child. Its status remains404. "
    "Day 5 adds flash messages to the shared layout and Day 6 uses shared session preferences.",
    '@app.context_processor\ndef common():return {"practice_label":"Local lab"}\n# Error child extends the base and is returned with its correct status.',
    demo('from flask import render_template\nfrom jinja2 import DictLoader\napp.jinja_loader=DictLoader({"base.html":"<header>{{ practice_label }}</header>{% block content %}{% endblock %}","error.html":\'{% extends "base.html" %}{% block content %}<h1>Missing page</h1>{% endblock %}\'})\n@app.context_processor\ndef common():return {"practice_label":"Local lab"}\n@app.errorhandler(404)\ndef missing(error):return render_template("error.html"),404\nwith app.test_client() as client:\n    r=client.get("/missing");print(r.status_code,r.get_data(as_text=True))'),
    "The shared label appears without being passed by that view. The route still reports missing status correctly.",
    ('# Hide a note insertion inside a context processor', '# Supply a small display helper; perform writes in explicit validated routes', "Shared template context should not create surprising side effects."),
    "Add a shared site label and use it in two known templates.",
    demo('from flask import render_template\nfrom jinja2 import DictLoader\napp.jinja_loader=DictLoader({"a.html":"{{ site }} / A","b.html":"{{ site }} / B"})\n@app.context_processor\ndef common():return {"site":"Desk"}\n@app.get("/<page>")\ndef page(page):\n    if page not in {"a","b"}:return "Missing",404\n    return render_template(page+".html")\nwith app.test_client() as client:print([client.get("/"+p).get_data(as_text=True) for p in ["a","b"]])'),
    "Render a helpful custom400page while retaining400.",
    demo('from flask import abort,render_template_string\n@app.get("/bad")\ndef bad():abort(400)\n@app.errorhandler(400)\ndef invalid(error):return render_template_string("<h1>Check the request</h1>"),400\nwith app.test_client() as client:print(client.get("/bad").status_code)'),
    "Reuse presentation and feedback, but keep significant state changes explicit in their routes.",
    [("Should a shared context helper perform hidden note writes?","No","Always","Only for dark mode","Writes need explicit validated request handling."),
     ("Can an error child extend the normal base while keeping404?","Yes","Never","Only with JSON","Presentation inheritance does not require changing status.")])

lesson(4,"1. A GET search form reads without saving",
    "Connect labelled form fields to request.args and a filtered result.",
    [("Form method/action; input name", "method selects the request method; action selects its endpoint. A control's name determines the submitted field key. id connects a label but is not the submission key."),
     ("Read-only search contract", "A GET query is suitable for a bookmarkable filter. Validate query length and render the entered value safely; searching must not create or delete records.")],
    "The search page has an input named q. The browser encodes it into the query string when the user submits GET. "
    "The view reads request.args, trims the term and filters a fixed data list. It passes both results and q back to the template. "
    "A label for=qconnects to id=q; the name=qis what sends the value. Those attributes solve different problems. "
    "Preserve the searched term in a quoted autoescaped input value so the user can refine it. "
    "The example uses fixed fictional topic data and no storage. The final project also bounds query length and shows an empty state.",
    '<form method="get" action="{{ url_for(\'search\') }}"><label for="q">Topic</label><input id="q" name="q" value="{{ q }}"><button>Search</button></form>',
    demo('from flask import request,render_template_string\nTOPICS=["HTTP cycle","SQL joins","Flask routes"]\n@app.get("/search")\ndef search():\n    q=request.args.get("q","").strip()\n    if len(q)>80:return "Search too long",400\n    rows=[t for t in TOPICS if q.casefold() in t.casefold()]\n    return render_template_string(\'<form method="get"><label for="q">Topic</label><input id="q" name="q" value="{{ q }}"><button>Search</button></form><p>{{ rows|join(", ") }}</p>\',q=q,rows=rows)\nwith app.test_client() as client:\n    text=client.get("/search",query_string={"q":"sql"}).get_data(as_text=True)\n    print("Found SQL:","SQL joins" in text,"No unrelated HTTP:","HTTP cycle" not in text)'),
    "The filtered page contains SQL joins and preserves the query. It does not mutate the source list.",
    ('<input id="q">  <!-- assume q is submitted -->', '<label for="q">Search</label><input id="q" name="q">', "name supplies the submitted key; id alone does not."),
    "Read a missing q as an empty string and return all three fixed topics.",
    demo('from flask import request\n@app.get("/search")\ndef search():\n    q=request.args.get("q","").strip()\n    return {"results":[t for t in ["HTTP","SQL","Flask"] if q.casefold() in t.casefold()]}\nwith app.test_client() as client:print(client.get("/search").get_json())'),
    "Reject an 81-character query before attempting display or filtering.",
    demo('from flask import request\n@app.get("/search")\ndef search():\n    q=request.args.get("q","")\n    return ("Too long",400) if len(q)>80 else ("Search ready",200)\nwith app.test_client() as client:print(client.get("/search",query_string={"q":"x"*81}).status_code)'),
    "A search form is a validated read operation with a clear submitted field name.",
    [("Which input attribute defines the submitted key?","name","id alone","class","Labels use id; submitted values use name."),
     ("Should the search GET save a new note?","No","Always","If a result is found","Searching is a read-only operation.")])

lesson(4,"2. POST fields and server-side validation",
    "Read form data separately from query parameters and reject invalid input.",
    [("request.form; browser validation versus server validation", "request.form contains submitted form fields. required/maxlength improve browser interaction but can be bypassed; enforce rules again on the server."),
     ("Validation error response", "On invalid input, return a useful message, preserve bounded entered text and avoid changing state. A400response is a deliberate rejected request, not a successful save.")],
    "A note-writing form uses POST and a body field. Read request.form, not request.args, for this URL-encoded form submission. "
    "A browser's required attribute does not stop a script from submitting blank data. Treat all received input as untrusted. "
    "Trim the boundary whitespace, check length and return clear feedback before any mutation. "
    "These tiny in-process examples demonstrate parsing/validation only; they do not expose a real persistent write service. The final local dashboard adds a per-session CSRF token for every state-changing POST. "
    "Accepting a field is not permission to interpret it as HTML or template source.",
    'body=request.form.get("body","").strip()\nif not 1<=len(body)<=200:return "Write 1–200 characters",400',
    demo('from flask import request\n@app.post("/validate-note")\ndef validate_note():\n    body=request.form.get("body","").strip()\n    if not 1<=len(body)<=200:return {"error":"Write 1–200 characters"},400\n    return {"approved_length":len(body)}\nwith app.test_client() as client:\n    print(client.post("/validate-note",data={"body":"  A clear idea  "}).get_json())\n    print(client.post("/validate-note",data={"body":"   "}).status_code)'),
    "The accepted body length excludes trimmed outer spaces. Blank input returns400instead of being saved.",
    ('body=request.args.get("body")  # URL-encoded POST form', 'body=request.form.get("body","")', "Query parameters and posted form fields are separate request locations."),
    "Reject an oversized note and demonstrate the failure status.",
    demo('from flask import request\n@app.post("/validate")\ndef validate():\n    value=request.form.get("body","").strip()\n    return ("Invalid",400) if not 1<=len(value)<=200 else ("Approved",200)\nwith app.test_client() as client:print(client.post("/validate",data={"body":"x"*201}).status_code)'),
    "Send the same key in query and form and show the two locations remain distinct.",
    demo('from flask import request\n@app.post("/locations")\ndef locations():return {"query":request.args.get("value"),"form":request.form.get("value")}\nwith app.test_client() as client:print(client.post("/locations?value=query",data={"value":"form"}).get_json())'),
    "Validate on the server before state changes; browser hints and request method alone are not validation.",
    [("Can HTML maxlength be bypassed by a scripted request?","Yes","Never","Only for GET","Server validation remains required."),
     ("Where is URL-encoded POST form data read?","request.form","request.args only","url_for","Each request location has a separate accessor.")])

lesson(4,"3. Invalid forms keep the draft and explain the correction",
    "Render validation feedback without saving bad data or discarding useful input.",
    [("Bounded redisplay; role=alert", "Keep a bounded escaped draft after failure and display an associated error. role=alert can announce new error feedback to assistive technology."),
     ("Validation pipeline", "Receive, normalise only the declared boundary, validate, then mutate. If validation fails, render the form with its error and leave stored state unchanged.")],
    "A form that wipes the entire draft after one mistake makes the learner redo work. Retain a bounded safe draft for correction. "
    "Display the reason beside the field and keep a visible label. A red border alone does not explain what failed. "
    "Autoescaping is especially important when inserting a user's draft back into an input or textarea. "
    "Do not save first and validate later. A failed validation response must leave the old approved records unchanged. "
    "The example uses a small in-memory list purely to prove that rejected data is not appended.",
    'if error:\n    return render_template("form.html",draft=raw[:200],error=error),400\n# Append only after validation succeeds.',
    demo('from flask import request,render_template_string\nnotes=[]\n@app.post("/note")\ndef note():\n    raw=request.form.get("body","")\n    body=raw.strip()\n    if not 1<=len(body)<=20:\n        return render_template_string(\'<label for="body">Note</label><textarea id="body" name="body">{{ draft }}</textarea><p role="alert">{{ error }}</p>\',draft=raw[:20],error="Use 1–20 characters"),400\n    notes.append(body);return "Approved"\nwith app.test_client() as client:\n    r=client.post("/note",data={"body":"<b>"+"x"*25})\n    text=r.get_data(as_text=True)\n    print(r.status_code,"&lt;b&gt;" in text,\'role="alert"\' in text,len(notes))'),
    "The invalid long draft is bounded and escaped in the returned form. The approved note list stays empty.",
    ('notes.append(raw)\n# Now check whether raw is valid', '# Check first; append only the approved value', "A validation failure must not leave an invalid saved row."),
    "Handle a whitespace-only draft without saving and show a clear correction.",
    demo('from flask import request\nnotes=[]\n@app.post("/note")\ndef note():\n    body=request.form.get("body","").strip()\n    if not body:return "Write a visible note",400\n    notes.append(body);return "Approved"\nwith app.test_client() as client:\n    r=client.post("/note",data={"body":" "});print(r.status_code,r.get_data(as_text=True),len(notes))'),
    "Preserve a quoted draft as escaped template data rather than inserting it into HTML source.",
    demo('from flask import render_template_string\n@app.get("/")\ndef form():return render_template_string(\'<input name="draft" value="{{ draft }}">\',draft=\'" <b>draft</b>\')\nwith app.test_client() as client:print(client.get("/").get_data(as_text=True))'),
    "A useful form protects both data integrity and the user's correction workflow.",
    [("Should invalid submitted data be appended before checking?","No","Always","If the response later says400","The mutation must follow validation."),
     ("How should a rejected draft be redisplayed?","Bounded and escaped with a clear error","As trusted raw HTML","By deleting every field","Preserve useful text without rendering it as markup.")])

lesson(4,"4. Post/Redirect/Get avoids normal refresh resubmission",
    "Redirect successful form submissions to a read page.",
    [("PRG;303redirect", "Post/Redirect/Get handles a valid POST then returns a redirect to GET. Refreshing the resulting page repeats a read, not the original form submission."),
     ("PRG versus idempotency", "PRG improves browser navigation but does not guarantee exactly-once processing if the original POST itself is repeated or its response is lost. Database/business rules solve that separate problem.")],
    "After a successful note submission, redirect to the planner. The browser then displays a normal GET result page. "
    "An invalid form should stay on the form response with its error instead of pretending success through a redirect. "
    "The small example counts submissions and uses a fixed read endpoint. It demonstrates PRG in an in-process client, not a production write service. "
    "Following the redirect and refreshing GET leaves the count unchanged. Repeating the original POST could still add another event; PRG is not a duplicate-write guarantee. "
    "The final dashboard combines PRG with validation and CSRF checking, while persistent transaction/idempotency work belongs to later database-backed projects.",
    'if valid:\n    # perform the intended change\n    return redirect(url_for("result"),code=303)',
    demo('from flask import redirect,url_for\nsaved=[]\n@app.post("/submit")\ndef submit():saved.append("approved");return redirect(url_for("result"),code=303)\n@app.get("/result")\ndef result():return {"saved":len(saved)}\nwith app.test_client() as client:\n    first=client.post("/submit");print(first.status_code,first.headers["Location"])\n    print(client.get("/result").get_json(),client.get("/result").get_json())'),
    "The POST adds one record and returns303. Both later GETs report one saved record without adding another.",
    ('return "Saved"  # remain at the POST response in normal form navigation', 'return redirect(url_for("planner"),code=303)', "A successful read destination makes ordinary refresh repeat GET."),
    "Follow a successful redirect in the test client and inspect the method of its final request.",
    demo('from flask import redirect,url_for\n@app.post("/submit")\ndef submit():return redirect(url_for("result"),code=303)\n@app.get("/result")\ndef result():return "Read result"\nwith app.test_client() as client:\n    r=client.post("/submit",follow_redirects=True);print(len(r.history),r.request.method,r.status_code)'),
    "Show that sending the original POST twice still represents two submissions despite PRG.",
    demo('from flask import redirect,url_for\nsaved=[]\n@app.post("/submit")\ndef submit():saved.append(1);return redirect(url_for("result"),code=303)\n@app.get("/result")\ndef result():return {"count":len(saved)}\nwith app.test_client() as client:\n    client.post("/submit");client.post("/submit");print(client.get("/result").get_json())'),
    "PRG controls browser follow-up behaviour; it is not a substitute for write idempotency.",
    [("What does refreshing the final PRG page normally repeat?","GET","The original POST","A database migration","The browser is at the redirect's read destination."),
     ("Does PRG guarantee a repeated original POST cannot duplicate work?","No","Always","Only with303","It does not implement exactly-once processing.")])

lesson(4,"5. Flash messages are one-time feedback, not durable records",
    "Show confirmation after a redirect through the shared layout.",
    [("flash; get_flashed_messages; categories", "flash queues a short session-backed message. The next template can retrieve it, with optional category, and show it after a redirect. It is feedback, not persistent history."),
     ("SECRET_KEY; fictional test key", "Session-backed feedback needs a signing key. Examples use a public fake key only for isolated tests; the local project generates a fresh random process key and never stores a real secret in source.")],
    "A successful form redirects, so it cannot simply return its confirmation text as the final page. A flash message carries short feedback to the next rendered GET. "
    "Put the message loop in the shared base, not in every child. Categories such as success/errorcan choose a presentation class from a known set. "
    "The first retrieval consumes the queued message. A later refresh normally shows no old confirmation. "
    "Keep messages short because Flask's default session is cookie-backed. Do not flash a whole document, private data or an actual credential. "
    "Signed means tamper-detectable, not encrypted. Day 6 explains cookie/session scope in more detail.",
    'flash("Practice note added","success")\nreturn redirect(url_for("result"),code=303)',
    demo('from flask import flash,get_flashed_messages,redirect,url_for\napp.config["SECRET_KEY"]="public-test-key-not-for-deployment"\n@app.post("/submit")\ndef submit():flash("Practice note added","success");return redirect(url_for("result"),code=303)\n@app.get("/result")\ndef result():return {"messages":get_flashed_messages(with_categories=True)}\nwith app.test_client() as client:\n    r=client.post("/submit",follow_redirects=True);print(r.get_json())\n    print(client.get("/result").get_json())'),
    "The first GET receives a success message; the next GET receives no queued message. This is not a durable log of saved notes.",
    ('flash(entire_document)  # use cookie-backed feedback as storage', 'flash("Short confirmation","success")', "Flash queues small transient feedback, not a dataset."),
    "Queue an info message and retrieve its category and text once.",
    demo('from flask import flash,get_flashed_messages\napp.config["SECRET_KEY"]="public-test-key-not-for-deployment"\n@app.get("/message")\ndef message():flash("Local practice","info");return {"messages":get_flashed_messages(with_categories=True)}\nwith app.test_client() as client:print(client.get("/message").get_json())'),
    "Use a trusted template to escape a message containing angle brackets.",
    demo('from flask import flash,get_flashed_messages,render_template_string\napp.config["SECRET_KEY"]="public-test-key-not-for-deployment"\n@app.get("/")\ndef home():\n    flash("<b>Fictional note</b>")\n    return render_template_string("{% for message in messages %}<p>{{ message }}</p>{% endfor %}",messages=get_flashed_messages())\nwith app.test_client() as client:print(client.get("/").get_data(as_text=True))'),
    "Use short escaped flash feedback across redirects; keep durable state in an appropriate storage layer.",
    [("Are flash messages durable note storage?","No","Always","If categorised","They are transient session-backed feedback."),
     ("Is a signed session encrypted by default?","No","Always","Only if it has a key","Signing protects integrity, not confidentiality.")])

lesson(4,"6. Match form intent with a per-session token",
    "Reject a missing/stale form token before state changes.",
    [("CSRF; session-bound token", "A browser may send cookies automatically. A matching unpredictable form token helps distinguish a form rendered for that session from an unrelated cross-site submission. POST alone is not that check."),
     ("secrets; compare_digest; body limit", "secrets creates unpredictable tokens. compare_digest compares expected/supplied values carefully. Bound request sizes and reject malformed tokens before mutation; do not disable checks just to make a test pass.")],
    "The supplied dashboard includes a small explicit token helper for its local forms. A GET form render provides a token; POST checks it against the current signed session. "
    "The token belongs to a session, so a token from another test client must not work. Entering/leaving the demo clears old state and a fresh form obtains a new token. "
    "Missing, stale or malformed input returns400with no note/state change. The implementation rejects non-ASCII supplied tokens rather than allowing a type-comparison error. "
    "This is a focused local teaching mechanism, not a claim to replace every mature form/security integration. Week 38handles fuller account and access-control work. "
    "For the example, keep the complete app.py/templates/static project folder beside your script. Its source is included later; tests use the real local project, not a disabled token check.",
    '<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">\n# Check expected session token before processing POST.',
    project('import re\nwith app.test_client() as client:\n    page=client.get("/enter").get_data(as_text=True)\n    token=re.search(r\'name="csrf_token" value="([^"]+)"\',page).group(1)\n    missing=client.post("/enter",data={"display_name":"Asha"})\n    good=client.post("/enter",data={"display_name":"Asha","csrf_token":token})\n    print("Missing token:",missing.status_code,"Matching token:",good.status_code)'),
    "The first rejected request leaves the gate unopened. A token from the rendered form allows the validated display-name submission and returns303.",
    ('# Disable token validation to make a POST test succeed', '# Render a form, capture its session-bound token, then submit it', "A meaningful form test exercises the actual validation boundary."),
    "Send a malformed Unicode token to the real project and confirm400rather than an application error.",
    project('with app.test_client() as client:\n    client.get("/enter")\n    print(client.post("/enter",data={"display_name":"Asha","csrf_token":"日本語"}).status_code)'),
    "Take a token from client A and attempt to use it in a separate client B.",
    project('import re\na=app.test_client();b=app.test_client()\ntoken=re.search(r\'name="csrf_token" value="([^"]+)"\',a.get("/enter").get_data(as_text=True)).group(1)\nb.get("/enter")\nprint(b.post("/enter",data={"display_name":"Ben","csrf_token":token}).status_code)'),
    "A POST must pass both form/session-intent checks and field validation before any change is accepted.",
    [("Does method=post alone implement a CSRF check?","No","Always","If the form is local","Automatic browser cookies still need a deliberate request-intent boundary."),
     ("Should a token from another session be accepted?","No","Always","If the names match","The token must match the submitting session.")])

lesson(5,"1. Cookies and Flask sessions have different responsibilities",
    "Read and update small browser-specific state without treating it as secret storage.",
    [("Cookie; Flask signed-cookie session", "The browser stores a cookie and sends it back under its rules. Flask's default session serialises data into a signed cookie: readable by its holder, tamper-detectable with the key, not encrypted."),
     ("Session lifetime; key stability", "A matching signing key validates the session across requests. The local project generates one key per app process; restarting changes it and invalidates earlier demo cookies.")],
    "A server can ask a browser to keep a small cookie. The next request brings it back, allowing a session counter or display preference. "
    "Flask's default session is not a server-side database containing a secret opaque id. Its contents must not include passwords, bearer tokens or large notes. "
    "The example uses a public test-only key and a visit count. Two requests from one test client bring the same session back. "
    "The project chooses a random runtime key, so copying public source does not reveal a usable shared signing key. It is intentionally a local restartable demo, not durable account hosting. "
    "Cookie flags such as HttpOnly/SameSitehave useful roles; they do not make session contents confidential.",
    'app.config["SECRET_KEY"]=runtime_signing_key\nsession["visits"]=session.get("visits",0)+1',
    demo('from flask import session\napp.config["SECRET_KEY"]="public-test-key-not-for-deployment"\n@app.get("/")\ndef home():\n    session["visits"]=session.get("visits",0)+1\n    return {"visits":session["visits"]}\nwith app.test_client() as client:\n    print(client.get("/").get_json(),client.get("/").get_json())'),
    "The second request returns visits 2 because the client returned its signed cookie. This incidental visit drill is not a rigorous analytics counter.",
    ('session["api_token"]=real_token', 'session["theme"]="dark"  # small nonsecret preference', "Default cookie sessions are not encrypted secret storage."),
    "Use two independent clients and show each begins at visit1.",
    demo('from flask import session\napp.config["SECRET_KEY"]="public-test-key-not-for-deployment"\n@app.get("/")\ndef home():\n    session["visits"]=session.get("visits",0)+1;return {"visits":session["visits"]}\na=app.test_client();b=app.test_client()\nprint(a.get("/").get_json(),a.get("/").get_json(),b.get("/").get_json())'),
    "Inspect only whether a session cookie is set, not the full cookie value.",
    demo('from flask import session\napp.config["SECRET_KEY"]="public-test-key-not-for-deployment"\n@app.get("/")\ndef home():session["theme"]="light";return "Preference set"\nwith app.test_client() as client:\n    r=client.get("/");print("Set-Cookie" in r.headers)'),
    "Session state is small browser-returned signed data; keep secrets and durable records elsewhere.",
    [("Does Flask's default signed cookie hide its contents from the holder?","No","Always","Only if HttpOnly","Integrity and confidentiality are different."),
     ("Do two fresh clients automatically share one session counter?","No","Always","If routes are identical","Each client has its own cookie state.")])

lesson(5,"2. Persist a small preference and understand storage scope",
    "Keep theme state per browser while distinguishing memory-only notes.",
    [("Allowlisted session preference", "A small theme value can be limited to light/dark, stored in session and used to choose CSS variables. A submitted preference is still input needing validation."),
     ("Browser cookie versus process memory", "Session preferences belong to that browser cookie. The project notes list belongs to one running app process, is shared by its demo visitors and disappears on restart. Neither replaces persistent Study Hub data.")],
    "The project applies a session theme through data-theme on the document root. Its stylesheet changes CSS variables for dark mode. "
    "An unknown theme token must not be inserted as arbitrary CSS or trusted markup. Choose from light/dark only. "
    "The example validates two choices and returns the current preference. The invalid choice changes nothing. "
    "Do not confuse the final demo's temporary notes with browser-only state. They are intentionally a server-memory list, not personal private accounts. "
    "Keep fictional notes only. Week 38will add a real persistent storage model and account isolation; Study Hub's existing progress remains separate.",
    'if theme not in {"light","dark"}:return "Invalid theme",400\nsession["theme"]=theme',
    demo('from flask import request,session\napp.config["SECRET_KEY"]="public-test-key-not-for-deployment"\n@app.post("/theme")\ndef theme():\n    value=request.form.get("theme","")\n    if value not in {"light","dark"}:return "Invalid",400\n    session["theme"]=value;return {"theme":value}\n@app.get("/theme")\ndef read_theme():return {"theme":session.get("theme","light")}\nwith app.test_client() as client:\n    print(client.post("/theme",data={"theme":"dark"}).get_json())\n    print(client.post("/theme",data={"theme":"arbitrary"}).status_code,client.get("/theme").get_json())'),
    "The approved preference remains dark after the invalid request. This compact in-process contract is separate from the final project's token-protected settings form.",
    ('# Assume a server-global theme variable is private to one visitor', '# Keep a small per-browser preference in its session', "Shared server state and browser state have different owners/lifetimes."),
    "Set one client's theme and verify another client's default stays light.",
    demo('from flask import session\napp.config["SECRET_KEY"]="public-test-key-not-for-deployment"\n@app.get("/")\ndef home():return {"theme":session.get("theme","light")}\na=app.test_client();b=app.test_client()\nwith a.session_transaction() as values:values["theme"]="dark"\nprint(a.get("/").get_json(),b.get("/").get_json())'),
    "Create two project app instances and prove a temporary note in one does not survive into the new process-like instance.",
    '''from app import create_app
a=create_app({"TESTING":True});b=create_app({"TESTING":True})
a.config["DEMO_NOTES"].append({"author":"Practice","body":"Memory-only"})
print(len(a.config["DEMO_NOTES"]),len(b.config["DEMO_NOTES"]))''',
    "Name each state store and its lifetime before promising persistence or privacy.",
    [("Where are the final project's practice notes stored?","Server-process memory","Study Hub localStorage","An encrypted private cloud","The project explicitly labels its temporary shared list."),
     ("Should an invalid theme change the last approved preference?","No","Always","Only if empty","Validate first, mutate only after approval.")])

lesson(5,"3. A demo session gate is not verified account login",
    "Protect a practice route with a flag while explaining the missing account guarantees.",
    [("Demo gate; server-side route check", "A session flag can choose whether the app shows a practice area. Check it inside the route, not only by hiding a navigation link."),
     ("Identity verification versus display name", "Typing a name proves no identity. This week deliberately uses fictional names and no password. Password hashing, accounts, durable user data and real authorisation are Week 38topics.")],
    "The roadmap asks for a simple session gate so you can understand the navigation mechanism. Do not label a self-entered name as a secure account. "
    "The project redirects a visitor without demo_namefrom /planner to /enter. A validated token-protected POST stores the fictional name and redirects back. "
    "The gate is checked in the route even if someone types /plannerdirectly. Hiding a link alone is not access control. "
    "There is no password, registration or identity verification in this demo. Its process-memory notes are shared practice data. "
    "Entering clears the old session first, preventing stale unrelated values from being carried into the new demo state.",
    'if not session.get("demo_name"):\n    return redirect(url_for("enter"),code=303)',
    project('import re\nwith app.test_client() as client:\n    first=client.get("/planner");print(first.status_code,first.headers["Location"])\n    page=client.get("/enter").get_data(as_text=True)\n    token=re.search(r\'name="csrf_token" value="([^"]+)"\',page).group(1)\n    entered=client.post("/enter",data={"display_name":"Asha","csrf_token":token},follow_redirects=True)\n    print(entered.status_code,"practice planner" in entered.get_data(as_text=True))'),
    "The route itself redirects before entry and renders the planner after the fictional session gate. No verified account was created.",
    ('# Hide the Planner link and assume direct URL access is blocked', '# Check the session gate inside the planner view', "A visitor can request URLs without clicking your navigation."),
    "Request the planner in a fresh independent client and verify it still redirects.",
    project('a=app.test_client();b=app.test_client()\nwith a.session_transaction() as values:values["demo_name"]="Practice"\nprint(a.get("/planner").status_code,b.get("/planner").status_code)'),
    "Submit an invalid short display name with the real form token and verify the gate remains closed.",
    project('import re\nwith app.test_client() as client:\n    token=re.search(r\'name="csrf_token" value="([^"]+)"\',client.get("/enter").get_data(as_text=True)).group(1)\n    print(client.post("/enter",data={"display_name":"A","csrf_token":token}).status_code)\n    print(client.get("/planner").status_code)'),
    "A gate teaches session flow; secure accounts require identity, password, storage and authorisation work beyond a name flag.",
    [("Does a display name prove identity?","No","Always","If signed into a cookie","The user supplied it without verification."),
     ("Where must the gate be checked?","In the route handling the request","Only in link styling","Only in CSS","Direct URL requests bypass hidden links.")])

lesson(5,"4. Leave the demo, clear state and test cookie isolation",
    "Use a POST logout-like action and verify old browser state is gone.",
    [("session.clear; POST leave", "Clearing the current session removes its demo fields; the response updates the browser cookie. A logout-like mutation uses POST plus the form token rather than a side-effect GET."),
     ("session_transaction; test fixture state", "The test client provides session_transaction to prepare or inspect isolated test state. It is a testing helper, not a real login flow to expose to visitors.")],
    "The base layout supplies a Leave demo form. Its POST includes the session token and clears the current session. "
    "After leaving, a direct planner request redirects again. Other browsers keep their own cookie state; clearing one client's session is not a global reset. "
    "Clearing a cookie session is also not a general token-revocation system. An older signed cookie can have separate replay/lifetime considerations; real authentication needs a fuller design. "
    "Leaving does not delete server-process notes. The UI labels their shared temporary scope and provides a separate clear-notes action. "
    "Use the real enter/form-token path for acceptance tests; session_transaction is helpful for narrowly scoped state assertions.",
    'session.clear()\nflash("You left the demo space.","info")\nreturn redirect(url_for("home"),code=303)',
    project('import re\nwith app.test_client() as client:\n    token=re.search(r\'name="csrf_token" value="([^"]+)"\',client.get("/enter").get_data(as_text=True)).group(1)\n    client.post("/enter",data={"display_name":"Asha","csrf_token":token})\n    token=re.search(r\'name="csrf_token" value="([^"]+)"\',client.get("/planner").get_data(as_text=True)).group(1)\n    left=client.post("/leave",data={"csrf_token":token})\n    print("Leave:",left.status_code,"Planner after:",client.get("/planner").status_code)\n    with client.session_transaction() as values:print("Name retained:","demo_name" in values)'),
    "The current cookie no longer carries demo_name. The planner refuses entry until a new valid demo entry is made.",
    ('@app.get("/leave")\ndef leave():session.clear()', '# Use a token-protected POST form for the state-changing leave action', "Normal page visits should not unexpectedly trigger logout-like changes."),
    "Verify GET /leavedoes not perform the POST-only leave action.",
    project('with app.test_client() as client:print(client.get("/leave").status_code)'),
    "Prepare two isolated clients, clear one session, and prove the other demo_nameis unchanged.",
    demo('from flask import session\napp.config["SECRET_KEY"]="public-test-key-not-for-deployment"\n@app.get("/")\ndef home():return {"name":session.get("demo_name")}\na=app.test_client();b=app.test_client()\nwith a.session_transaction() as values:values["demo_name"]="Asha"\nwith b.session_transaction() as values:values["demo_name"]="Ben"\nwith a.session_transaction() as values:values.clear()\nprint(a.get("/").get_json(),b.get("/").get_json())'),
    "Name the scope of a clear operation: one browser session, shared process memory or durable account state.",
    [("Does clearing one session clear every browser's cookie?","No","Always","If they use the same route","Each client returns its own state."),
     ("Does leaving automatically erase shared process-memory notes?","No","Always","Only in dark mode","That is a separate server-state action in this demo.")])

FOLDER=ROOT/"docs"/"python-week37"
APP_SOURCE=(FOLDER/"app.py").read_text(encoding="utf-8")
APP_CORE=APP_SOURCE.rsplit('\nif __name__=="__main__":',1)[0]

lesson(5,"5. Assemble routes, templates, forms and sessions into one app",
    "Trace the complete dashboard implementation with explicit data lifetimes.",
    [("Application factory; project layout", "create_app constructs an app with its own config, routes and process-memory list. templates/ contains shared/child HTML; static/style.css is the offline stylesheet."),
     ("Random process signing key; request size limit", "The project generates a random key at startup and caps request bodies at 16 KiB. It never reads an existing user token/password. A restart deliberately resets the demo signing context and memory-only notes.")],
    "Read create_app in stages: configuration, token helper/check, public reads, demo entry/gated routes, validated note writes, settings, leave and error handlers. "
    "The factory locates templates/static beside app.py using an absolute resource root. Starting from another working directory does not change those resource locations. "
    "Every state-changing project POST passes the form token check, then the route's own validation. Successful submissions use 303 and flash feedback. "
    "The base owns navigation/messages; all user names, notes and queries are autoescaped. Light/dark CSS uses a small allowlisted session preference. "
    "The memory-only note list is bounded to 20 short entries and labelled shared; no persistent storage or verified identity is claimed. "
    "This separate local app does not read or migrate Study Hub's existing saved progress, notes, backup or sync credentials.",
    'python -m pip install -r requirements.txt\npython app.py\n# Open http://127.0.0.1:5000 ; Ctrl+C stops the local server.',
    APP_CORE+'''
practice=create_app({"TESTING":True})
with practice.test_client() as client:
    for path in ["/","/lessons","/lessons/1","/about","/enter"]:
        response=client.get(path)
        print(path,response.status_code)
    print("CSS:",client.get("/static/style.css").status_code)
''',
    "The full app code is followed by a compact request drill. Real templates/static are supplied alongside it; keep the complete project folder. The test checks public pages and the asset endpoint, not a live public deployment.",
    ('# Copy only app.py and discard templates/static', '# Keep app.py, templates/, static/ and requirements.txt together', "The application needs its local presentation resources."),
    "Verify all expected project endpoints are registered without opening a port.",
    project('names={r.endpoint for r in app.url_map.iter_rules()}\nprint(all(name in names for name in ["home","lessons","lesson_detail","planner","enter","settings","add_note","leave"]))'),
    "Request an unknown detail id and inspect the useful inherited404page.",
    project('with app.test_client() as client:\n    r=client.get("/lessons/999");text=r.get_data(as_text=True)\n    print(r.status_code,"Request 404" in text,"My learning desk" in text)'),
    "A clear factory and folder layout connect the pieces without confusing temporary demonstration state with durable learning data.",
    [("Does this project replace Study Hub's browser storage?","No","Always","Only after note entry","It is a separate local Flask exercise."),
     ("What happens to its memory-only notes on restart?","They disappear","They become a database automatically","They sync to GitHub","No persistent note store is implemented this week.")])

lesson(5,"6. Milestone: a complete local Flask learning dashboard",
    "Run the dashboard in a browser and verify the complete form/session workflow.",
    [("End-to-end acceptance; browser versus test-client checks", "Test-client checks verify route/form/state contracts. A real local browser check verifies navigation, asset loading, mobile layout, keyboard/labels and theme rendering."),
     ("Week 37 scope; next step", "This milestone is a local single-user teaching dashboard with fictional data and shared memory-only notes. Week 38addresses real persistence/accounts; GitHub Pages continues hosting the course and downloadable source, not a Python backend.")],
    "Download docs/python-week37 as a complete folder. Install requirements once, run python app.py and open the loopback URL printed in the terminal. "
    "Start at Home, search lessons, open a detail page, then enter a fictional demo name. Add a short practice note and see the redirect/confirmation. "
    "Try a blank or oversized note and verify no invalid entry is saved. Change the demo theme, refresh, leave and try the gated planner again. "
    "The example below performs that same approved flow without a network port. It obtains real form tokens instead of disabling them. "
    "A useful test checks state after failure as well as after success. The project acceptance suite also covers cross-session/stale tokens, tampered cookies, two-client separation, invalid methods, escaped text and reset behaviour. "
    "The full Study Hub course remains offline and unchanged around the new teaching data. This project is a practice deliverable rather than a change to public website hosting.",
    'python app.py\n# Browser: Home -> Lessons -> Enter demo -> Planner -> Settings -> Leave demo',
    project('import re\ndef token(client,path):\n    page=client.get(path).get_data(as_text=True)\n    return re.search(r\'name="csrf_token" value="([^"]+)"\',page).group(1)\nwith app.test_client() as client:\n    print("Search:",client.get("/lessons?q=HTTP").status_code)\n    entered=client.post("/enter",data={"display_name":"Asha","csrf_token":token(client,"/enter")})\n    added=client.post("/notes",data={"body":"Routes connect a request to a view.","csrf_token":token(client,"/planner")},follow_redirects=True)\n    themed=client.post("/settings",data={"theme":"dark","csrf_token":token(client,"/settings")},follow_redirects=True)\n    print("Entry redirect:",entered.status_code,"Note page:",added.status_code)\n    print("Notes:",len(app.config["DEMO_NOTES"]),"Dark:",\'data-theme="dark"\' in themed.get_data(as_text=True))\n    client.post("/leave",data={"csrf_token":token(client,"/planner")})\n    print("Planner after leave:",client.get("/planner").status_code)'),
    "The note exists only in this app's temporary process list. Dark preference belongs to that client's signed cookie; leaving clears its demo session. The next planner request redirects.",
    ('# Describe the display-name gate as secure verified user accounts', '# Label the demo honestly and add real account/persistence work in Week 38', "A learning scaffold must not imply guarantees it has not implemented."),
    "Enter the real demo, reject a blank note with a valid token, and prove the note count remains zero.",
    project('import re\ndef token(client,path):return re.search(r\'name="csrf_token" value="([^"]+)"\',client.get(path).get_data(as_text=True)).group(1)\nwith app.test_client() as client:\n    client.post("/enter",data={"display_name":"Asha","csrf_token":token(client,"/enter")})\n    r=client.post("/notes",data={"body":" ","csrf_token":token(client,"/planner")})\n    print(r.status_code,len(app.config["DEMO_NOTES"]))'),
    "Add a script-like note as literal text and verify it is escaped in the planner.",
    project('import re\ndef token(client,path):return re.search(r\'name="csrf_token" value="([^"]+)"\',client.get(path).get_data(as_text=True)).group(1)\nwith app.test_client() as client:\n    client.post("/enter",data={"display_name":"Asha","csrf_token":token(client,"/enter")})\n    r=client.post("/notes",data={"body":"<script>alert(1)</script>","csrf_token":token(client,"/planner")},follow_redirects=True)\n    text=r.get_data(as_text=True)\n    print(r.status_code,"&lt;script&gt;" in text,"<script>" not in text)'),
    "A complete local web app connects routes, trusted templates, validated forms, deliberate session state and tested browser behaviour.",
    [("What handles the incoming URL in Flask?","A registered route/view","The CSS grid","The session signing key","Routes choose the view for path/method."),
     ("Where do child templates get shared navigation?","The base layout","A duplicated Python string in every view","The database password","Inheritance keeps the shell in one resource."),
     ("Does a path int converter prove a record exists?","No","Always","If greater than0","The view must still look it up."),
     ("Should visitor-entered notes use |safe?","No","Always","If they include brackets","They remain escaped data."),
     ("Is client-side required enough to validate a POST?","No","Always","Only offline","Server validation is still necessary."),
     ("What does a valid successful form normally return in this project?","303redirect to GET","An unhandled exception","A silent overwrite of all notes","PRG supports ordinary browser navigation."),
     ("Does PRG alone make repeated writes exactly-once?","No","Always","If using POST","That needs a separate operation/storage contract."),
     ("Is Flask's default cookie session encrypted?","No","Always","With HttpOnly","Signing does not hide contents."),
     ("Does the fictional display name verify identity?","No","Always","If the cookie is signed","No account verification is implemented."),
     ("Where do this project's practice notes live?","Shared process memory","Study Hub localStorage","A private cloud account","They are explicitly temporary local demo records."),
     ("Can GitHub Pages run this Flask backend?","No","Always","If app.py is uploaded","It publishes the static course/source only."),
     ("What happens to a POST missing its required form token?","Rejected before state change","Saved anyway","It becomes a GET search","The project checks request intent and field data separately.")])


def write():
    target=ROOT/"study-hub.html";original=target.read_bytes().decode("utf-8")
    start=original.index("const DAY_TEACH = {");end=original.index("\n};\n\nconst REST_DAY",start)
    if any(('"'+key+'":') in original[start:end] for key in DAYS):
        if "--refresh" not in sys.argv:raise RuntimeError("Week37 exists; refusing overwrite")
        first=original.index('\n"37.0": {',start)
        if not all(('"'+key+'":') in original[first:end] for key in DAYS):raise RuntimeError("Unexpected Week37 block")
        original=original[:first]+original[end:];end=original.index("\n};\n\nconst REST_DAY",start)
    assert [len(day["parts"]) for day in DAYS.values()]==[5,5,5,5,6,6]
    files={str(path.relative_to(FOLDER)).replace("\\","/"):path.read_text(encoding="utf-8")
           for path in [FOLDER/"app.py",*sorted((FOLDER/"templates").glob("*.html")),FOLDER/"static"/"style.css"]}
    bootstrap='import sys\nfrom pathlib import Path\nfor name,source in '+repr(files)+'.items():\n    p=Path(name);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(source,encoding="utf-8")\nsys.modules.pop("app",None)\nsys.path.insert(0,str(Path.cwd()))\n'
    with tempfile.TemporaryDirectory(prefix="studyhub-w37-verify-") as temp:
        manifest=Path(temp)/"examples.json";result=Path(temp)/"results.json"
        manifest.write_text(json.dumps([bootstrap+code for code,_ in JOBS]),encoding="utf-8")
        subprocess.run([sys.executable,str(ROOT/"scripts"/"python-example-worker.py"),str(manifest),str(result)],check=True,timeout=300,
            env={**os.environ,"MPLBACKEND":"Agg","OPENBLAS_NUM_THREADS":"1","PYTHONDONTWRITEBYTECODE":"1"})
        results=json.loads(result.read_text(encoding="utf-8"))
    for (_,destination),result in zip(JOBS,results,strict=True):
        destination["v" if destination["t"]=="out" else "out"]=result["out"]
    DAYS["37.0"]["parts"][0]["sections"].insert(3,sec("sh",'python -m pip install "Flask>=3.1,<4"'))
    DAYS["37.0"]["parts"][0]["sections"].insert(4,sec("tip","Verified with Python3.12.14 and Flask3.1.3. Initial package installation needs internet; lesson reading, test-client examples and the local dashboard run offline afterward. Most examples are self-contained with named in-memory templates. From Day5's token exercise onward, keep the supplied app.py, templates/ and static/ beside your script; project-based examples use those explicit dependencies. Run snippets in a fresh folder and do not name a script flask.py."))
    final=DAYS["37.5"]["parts"][5]["sections"]
    final.extend([sec("sh","python -m pip install -r requirements.txt\npython app.py\n# Open http://127.0.0.1:5000 ; Ctrl+C stops the server."),
        sec("p","Download the complete docs/python-week37 folder from the repository: app.py, requirements.txt, templates/ and static/. GitHub Pages serves these source files and the course; Flask runs on your own computer. Notes in this standalone project are fictional/shared/memory-only and never replace Study Hub progress or notes."),
        sec("p","Primary references: https://flask.palletsprojects.com/en/stable/quickstart/ · https://flask.palletsprojects.com/en/stable/testing/ · https://flask.palletsprojects.com/en/stable/tutorial/templates/ · https://flask.palletsprojects.com/en/stable/web-security/ · https://jinja.palletsprojects.com/en/stable/templates/ . Explanations, examples, fictional data and exercises are original; lesson text/code/recorded outputs are embedded for offline reading.")])
    addition="\n".join(json.dumps(k)+": "+json.dumps(v,ensure_ascii=False,indent=2)+"," for k,v in DAYS.items()).replace("</","<\\/")
    prefix=original[:end].rstrip()
    if not prefix.endswith(","):prefix+=","
    temporary=target.with_suffix(".html.tmp")
    temporary.write_bytes((prefix+"\n"+addition+original[end:]).encode("utf-8"));temporary.replace(target)
    print("Added Week37:6days,32parts,64practice prompts,74explained quizzes,96executed examples/solutions; all earlier lessons/application/storage unchanged.")


if __name__=="__main__":
    write()

