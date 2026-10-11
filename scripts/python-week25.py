"""Author Week 25 additively; execute each output in an isolated practice folder."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap

ROOT = Path(__file__).resolve().parent.parent
DAYS = {f"25.{d}": {"parts": []} for d in range(6)}
EXECUTED = 0


def clean(code):
    return textwrap.dedent(code).strip() + "\n"


def output(code):
    global EXECUTED
    with tempfile.TemporaryDirectory(prefix="studyhub-w25-") as folder:
        run = subprocess.run([sys.executable, "-c", clean(code)], cwd=folder,
                             capture_output=True, encoding="utf-8", timeout=35,
                             env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    if run.returncode:
        raise RuntimeError(run.stderr + "\n" + code)
    EXECUTED += 1
    return run.stdout.replace("\r\n", "\n").rstrip()


def s(t, v=None, **extra):
    return {"t": t, **({"v": v} if v is not None else {}), **extra}


def add(day, title, goal, concepts, explanation, syntax, code, walk, mistake,
        task, solution, challenge, challenge_code, key, quizzes):
    parts = DAYS[f"25.{day}"]["parts"]
    index = len(parts)
    questions = []
    for n, (q, answer, wrong1, wrong2, why) in enumerate(quizzes):
        rotation = (index + n) % 3
        options = [answer, wrong1, wrong2]
        for _ in range(rotation):
            options.insert(0, options.pop())
        questions.append({"q": q, "options": options, "correct": rotation, "why": why})
    parts.append({"title": title, "sections": [
        s("h", title), s("key", "Learning objective: " + goal),
        *[s("new", name, note=note) for name, note in concepts],
        s("p", explanation), s("syn", syntax, note="Pattern first; run the complete example below."),
        s("code", clean(code)), s("out", output(code)), s("p", walk),
        s("mis", wrong=mistake[0], right=mistake[1], why=mistake[2]),
        s("ex", task, practiceId=f"25.{day}.{index}.build"),
        s("sol", code=clean(solution), out=output(solution), why="Build check: " + key),
        s("ex", "Mini challenge: " + challenge, practiceId=f"25.{day}.{index}.challenge"),
        s("sol", code=clean(challenge_code), out=output(challenge_code), why="Challenge check: " + key),
        s("try", q=quizzes[0][0], code="# Predict and explain before revealing.",
          a=quizzes[0][1], why=quizzes[0][4]),
        s("checkpoint", lesson={"id": f"course:25.{day}.{index}", "quiz": questions}), s("key", key),
    ]})


add(0, "1. HTTP: a request is a question, a response is an answer",
    "Identify URL, GET, query parameters, headers, status and body before writing a fetcher.",
    [("HTTP; GET; request/response", "HTTP is the exchange protocol. A GET asks for a representation; a response includes a status, headers and a body. A successful exchange can still return an error status."),
     ("requests; Request; prepare", "requests is an installed Python package. Preparing a Request builds its URL/headers without sending it; Session.get sends a request later."),
     ("params; headers; User-Agent", "params encodes query values. Headers carry metadata. User-Agent identifies the client; do not pretend to be another identity to evade restrictions.")],
    "Week 23 taught data formats; Week 24 generated documents. Now separate acquiring a page from parsing its contents. "
    "A URL has a scheme, server address, path and optional query. A fragment such as #details is a browser position, not a new HTTP resource. "
    "GET reads; do not use POST or click purchase/submit buttons as a substitute for reading a listing. This week's Python needs 3.11+ with requests and beautifulsoup4; "
    "Day 4 additionally uses Playwright. The course page and saved-page exercises work offline. Real remote fetching requires internet and an allowed source. "
    "Use owned/local examples first. Prepared requests below make no connection.",
    'request = requests.Request("GET", url, params={"q": "Python notes"}, headers={"User-Agent": "StudyHubPractice/1.0"}).prepare()',
    '''
    import requests
    request = requests.Request("GET", "https://example.org/catalog",
        params={"q": "Python notes", "page": 2},
        headers={"User-Agent": "StudyHubPractice/1.0"}).prepare()
    print(request.method)
    print(request.url)
    print(request.headers["User-Agent"])
    ''',
    "prepare() ले URL बनाउँछ, website खोल्दैन। q भित्रको space encode हुन्छ; page=2 query हो। "
    "Header भने URL query होइन। Actual response पछि status र Content-Type जाँचेर मात्रै body parse गर्छौँ।",
    ('url = base + "?q=" + user_text', 'requests.Request("GET", base, params={"q": user_text}).prepare()',
     "Manual concatenation can mistake & or ? in a value for URL syntax. Let the library encode parameters."),
    "Prepare a GET with category='books & notes' and page=1; print the encoded URL.",
    '''
    import requests
    request = requests.Request("GET", "https://example.org/items",
        params={"category": "books & notes", "page": 1}).prepare()
    print(request.url)
    ''',
    "Use urlsplit to separate a query from a fragment; explain which part requests sends to the server.",
    '''
    from urllib.parse import urlsplit
    url = urlsplit("https://example.org/items?page=2#details")
    print(url.scheme, url.hostname, url.path)
    print("query:", url.query)
    print("fragment:", url.fragment)
    ''',
    "Prepare is not send. Encode query values through params; identify the source and use read operations. Keep acquiring, parsing and storing as distinct jobs.",
    [("Does Request.prepare() fetch the page?", "No", "Yes", "Only for HTTPS", "It constructs the outgoing request; sending is a separate step."),
     ("Where should a search value containing & go?", "In params as a value", "In raw string concatenation", "In the status code", "The query encoder preserves the value instead of interpreting its characters as separators.")])

add(0, "2. Status, content type, bytes and decoded text",
    "Check an HTTP response before treating it as an HTML document.",
    [("Response; status_code; raise_for_status", "Response represents returned data. raise_for_status raises HTTPError for 4xx/5xx; it does not itself reject every other unsuitable status such as 204."),
     ("Content-Type; content; text; encoding", "content is bytes; text is decoded text. Content-Type describes the representation and may carry a charset. Choose encoding using evidence, not a guess that hides corruption."),
     ("200/204/404/429/503", "200 normally has an OK representation; 204 has no content; 404 is not found; 429 means too many requests; 503 is temporarily unavailable. Decide what your application accepts.")],
    "A page may return a login screen with status 200, a JSON error, or an empty body. 'No exception' is not 'usable listing'. "
    "For our HTML workflow require 200 and text/html, then validate its expected elements on Day 2. Headers alone are not a complete schema check. "
    "These Response objects are locally constructed fixtures, not live HTTP responses; that makes outputs predictable. "
    "raise_for_status is useful, but it is not an HTML parser or a content validator. A redirect policy belongs to the fetch stage.",
    'response.raise_for_status()\nif response.status_code != 200: reject\nif content_type != "text/html": reject\nhtml = response.text',
    '''
    import requests
    response = requests.Response()
    response.status_code = 200
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    response.encoding = "utf-8"
    response._content = "<h1>日本語 & Python</h1>".encode("utf-8")
    response.raise_for_status()
    print(response.headers["Content-Type"].split(";", 1)[0])
    print(isinstance(response.content, bytes))
    print(response.text)
    ''',
    "Fixture मा _content आफैँ राखिएको छ—यो test technique हो, production response बनाउनुपर्ने तरिका होइन। "
    "Bytes लाई UTF-8 ले decode गर्दा Japanese ठीक देखिन्छ। HTTP 200 भए पनि आवश्यक listing structure छ कि पछि जाँच्नुपर्छ।",
    ('records = parse(response.text)  # ignore status and type', 'Check status/type, then validate the parsed structure',
     "Otherwise you might save an error or login page as an empty successful dataset."),
    "Construct a 404 fixture, call raise_for_status and catch HTTPError without printing unstable library error details.",
    '''
    import requests
    response = requests.Response()
    response.status_code = 404
    response.url = "https://example.org/missing"
    try:
        response.raise_for_status()
    except requests.HTTPError:
        print("Not found: do not parse as a listing")
    ''',
    "Classify 200 HTML, 200 JSON and 204 as suitable/unsuitable for this particular HTML parser.",
    '''
    cases = [(200, "text/html; charset=utf-8"), (200, "application/json"), (204, "text/html")]
    for status, kind in cases:
        suitable = status == 200 and kind.split(";", 1)[0].strip().lower() == "text/html"
        print(status, kind.split(";", 1)[0], suitable)
    ''',
    "Status, media type, decoding and document structure are four separate checks. Do not turn failure pages into valid empty results.",
    [("Does raise_for_status validate the page's product fields?", "No", "Yes", "Only for 200", "It checks HTTP error status, not domain structure."),
     ("Which attribute is bytes before text decoding?", "content", "text", "status_code", "content exposes the binary body; text applies a character encoding.")])

add(0, "3. Timeouts and exceptions without hiding failures",
    "Distinguish transport failure from HTTP failure and use explicit timeouts.",
    [("timeout=(connect, read)", "Requests accepts separate connect and read timeout seconds. The read timeout limits waiting between received data, not an entire download's total wall time."),
     ("Timeout; ConnectionError; HTTPError", "Timeout and ConnectionError describe transport problems; HTTPError follows an HTTP error response. All are under RequestException, but a broad handler should not pretend every problem is recoverable."),
     ("unittest.mock.patch", "The standard-library test tool temporarily replaces a dependency. Here it simulates a timeout without contacting a website or waiting several seconds.")],
    "Requests has no default timeout when you omit it. Set one explicitly, then classify failure. A timeout is not proof that there are no products. "
    "A 404 does not normally improve by retrying the same address repeatedly. An HTTP response and a network exception are different outcomes. "
    "Week 14's exception handling and Week 17's testing are prerequisites; patch is introduced here specifically to make network examples deterministic. "
    "Later we retry a small set of transient failures with a finite budget. Never use verify=False to 'fix' certificate errors; investigate configuration instead.",
    'try:\n    response = requests.get(url, timeout=(3, 10))\n    response.raise_for_status()\nexcept requests.Timeout:\n    record_failed_attempt()',
    '''
    import requests
    from unittest.mock import patch
    with patch("requests.get", side_effect=requests.Timeout("fixture")) as get:
        try:
            requests.get("https://example.org/catalog", timeout=(3, 10))
        except requests.Timeout:
            print("Fetch failed: timeout; previous data stays")
        print("timeout:", get.call_args.kwargs["timeout"])
    ''',
    "patch भित्र website request हुँदैन। Exception बाट [] फर्काएर 'सब हटेछ' भन्नु गलत हो। "
    "Failure छुट्टै देखाऊ, पुरानो snapshot बचाऊ। Tuple मा connect=3s र read=10s छन्; total runtime guarantee होइन।",
    ('except Exception: return []', 'except requests.Timeout: record failure; keep previous snapshot',
     "A programming bug or timeout is not evidence of an empty catalogue."),
    "Simulate a ConnectionError and report it separately from an HTTPError.",
    '''
    import requests
    from unittest.mock import patch
    with patch("requests.get", side_effect=requests.ConnectionError("fixture")):
        try:
            requests.get("https://example.org/catalog", timeout=(3, 10))
        except requests.ConnectionError:
            print("Connection failed")
        except requests.HTTPError:
            print("HTTP status failed")
    ''',
    "Build a 503 Response fixture; demonstrate that HTTPError follows a response rather than a Timeout.",
    '''
    import requests
    from unittest.mock import patch
    response = requests.Response()
    response.status_code = 503
    with patch("requests.get", return_value=response):
        try:
            result = requests.get("https://example.org/catalog", timeout=(3, 10))
            result.raise_for_status()
        except requests.HTTPError:
            print("Server replied:", result.status_code)
    ''',
    "Timeouts are explicit waiting limits, not a valid empty dataset. Catch known failures, preserve the last good data and report the cause.",
    [("Is timeout=(3,10) a strict 13-second total deadline?", "No", "Yes", "Only for HTML", "Connect and read timeouts have separate meanings; read is not a total response deadline."),
     ("What should a failed fetch do to yesterday's snapshot?", "Keep it and report failure", "Replace it with an empty list", "Mark every item removed", "No fresh observation was obtained.")])

LOCAL_HTTP = '''
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlsplit, parse_qs
import requests

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlsplit(self.path).query)
        page = query.get("page", ["1"])[0]
        body = ("<h1>Practice page " + page + "</h1>").encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass

server = HTTPServer(("127.0.0.1", 0), Handler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
try:
    with requests.Session() as session:
        session.trust_env = False  # local fixture: no machine proxy/.netrc
        session.headers["User-Agent"] = "StudyHubPractice/1.0"
        response = session.get("http://127.0.0.1:" + str(server.server_port),
                               params={"page": 2}, timeout=(3, 5))
        response.raise_for_status()
        print(response.status_code)
        print(response.text)
finally:
    server.shutdown()
    server.server_close()
    thread.join()
'''

add(0, "4. A real request to your own local practice server",
    "Run a genuine request/response round trip offline and close resources.",
    [("Session; context manager", "A Session reuses connections and keeps shared headers/cookies. The with block closes it. Never print authentication cookies or include them in source."),
     ("http.server; localhost; port 0", "A loopback server runs on your computer. Port 0 asks the operating system for a free port, avoiding a fixed-port conflict."),
     ("threading.Thread; shutdown; join", "The fixture's server runs in a background thread so the same script can make a request. Finally shuts it down and waits for the thread. Detailed concurrency arrives later in the course.")],
    "The next example actually sends HTTP, but only to 127.0.0.1 on your own machine. The setup is longer than the request so the example is self-contained. "
    "Focus first on the Session block: headers are shared, params is encoded, timeout is explicit and status is checked. "
    "Handler sends the UTF-8 body's byte length. The code then closes both client and server even if parsing fails. "
    "Threading is fixture scaffolding, not a prerequisite you must master today. Do not copy this server into a public hosting setup.",
    'with requests.Session() as session:\n    session.headers["User-Agent"] = "StudyHubPractice/1.0"\n    response = session.get(local_url, params={"page": 2}, timeout=(3, 5))',
    LOCAL_HTTP,
    "यो वास्तविक HTTP request हो, internet website होइन। Port आफैँ छानिन्छ, त्यसैले output मा random port देखाएका छैनौँ। "
    "session.trust_env=False fixture लाई proxy/credential settings बाट अलग राख्न हो। finally ले server बन्द गर्छ।",
    ('Start a server but leave it running after the example', 'Close Session and use finally for server.shutdown/server_close/thread.join',
     "Resources and ports should be released on both success and failure."),
    "Change the query to page=3 and verify the local response.",
    LOCAL_HTTP.replace('params={"page": 2}', 'params={"page": 3}'),
    "Request the default page without a page parameter; inspect the declared Content-Type.",
    LOCAL_HTTP.replace('params={"page": 2}', 'params={}').replace('print(response.status_code)', 'print(response.headers["Content-Type"])'),
    "Use tiny local servers for reproducible HTTP tests. The client logic is small; isolate and close test infrastructure. Static fixtures are preferable for parser tests.",
    [("Does a request to 127.0.0.1 need a public website?", "No", "Yes", "Only for GET", "It addresses the local computer."),
     ("What is the purpose of Session here?", "Share client configuration and reuse connections", "Execute page JavaScript", "Calculate Excel formulas", "Sessions manage HTTP client state; they are not browsers.")])

add(1, "1. HTML is a tree: tags, attributes and selectors",
    "Extract text and links using BeautifulSoup without running page scripts.",
    [("BeautifulSoup; html.parser", "BeautifulSoup parses markup into searchable objects. html.parser is the built-in parser backend; install beautifulsoup4, import bs4."),
     ("find; select_one; select", "find searches by tag/attributes. select_one returns the first CSS match or None; select returns all matching elements as a list."),
     ("CSS #id, .class and descendant selectors", "#catalog selects an id, .item selects a class and #catalog .item selects item descendants within that container. These selectors locate elements, not Python variables."),
     ("get_text; get(attribute)", "get_text(separator,strip=True) extracts readable descendant text. get('href') reads an attribute and returns None if missing.")],
    "Week 23 explained why HTML needs a different parser from XML. A page contains nested elements and attributes, not just a bag of strings. "
    "Do not use a regex to parse arbitrary HTML. BeautifulSoup tolerates common imperfect markup, but it neither executes JavaScript nor confirms semantic correctness. "
    "Choose stable semantic ids/classes. A selector matching something is not automatically the selector matching your intended table. "
    "Our authored fixture below is included in the lesson, so you can inspect every tag without fetching a real website.",
    'soup = BeautifulSoup(html, "html.parser")\ntitle = soup.select_one("#catalog h1")\nlinks = soup.select("#catalog a.item")',
    '''
    from bs4 import BeautifulSoup
    html = '<section id="catalog"><h1>Python <em>books</em></h1><a class="item featured" href="/book/1">Learn Python</a></section>'
    soup = BeautifulSoup(html, "html.parser")
    print(soup.select_one("#catalog h1").get_text(" ", strip=True))
    print(soup.find("a", class_="item").get("href"))
    print(len(soup.select("#catalog .item")))
    ''',
    "em भित्रको books समेत get_text मा आउँछ। class_ मा underscore Python को class keyword सँग नजुध्न हो। "
    "item featured दुईवटा CSS classes हुन्; .item selector ले यस्तो element पनि भेट्छ।",
    ('soup.select_one(".missing").get_text()', 'node = soup.select_one(".missing"); check node is not None',
     "A missing match returns None. Calling a tag method on it raises AttributeError."),
    "Extract two link labels and href values from an authored navigation fixture.",
    '''
    from bs4 import BeautifulSoup
    soup = BeautifulSoup('<nav><a href="/a">Alpha</a><a href="/b"><b>Beta</b></a></nav>', "html.parser")
    for link in soup.select("nav a"):
        print(link.get_text(" ", strip=True), link.get("href"))
    ''',
    "Find an absent price and return a clear missing-field message rather than inventing zero.",
    '''
    from bs4 import BeautifulSoup
    soup = BeautifulSoup('<article><h2>Book</h2></article>', "html.parser")
    price = soup.select_one(".price")
    print("Missing price" if price is None else price.get_text(strip=True))
    ''',
    "Parse a tree, scope your selectors, check None and distinguish text from attributes. A parser does not execute JavaScript or validate your business rules.",
    [("What does select_one return when no element matches?", "None", "An empty string", "Zero", "Check the result before using tag methods."),
     ("Does BeautifulSoup execute the page's JavaScript?", "No", "Yes", "Only inline scripts", "It parses the supplied markup.")])

CARD_PARSER = '''
from bs4 import BeautifulSoup

def parse_cards(html):
    soup = BeautifulSoup(html, "html.parser")
    root = soup.select_one("#catalog")
    if root is None:
        raise ValueError("Catalogue container missing")
    records, rejected = [], []
    for number, card in enumerate(root.select("article.item"), 1):
        title, price = card.select_one("h2"), card.select_one(".price")
        if title is None or price is None or not title.get_text(strip=True):
            rejected.append(number)
            continue
        records.append({"title": title.get_text(" ", strip=True),
                        "price_text": price.get_text(" ", strip=True)})
    return records, rejected
'''

add(1, "2. Scope each record and report missing fields",
    "Keep a product's title and price together and report rejected records.",
    [("Record-local selection", "Select fields inside each article instead of collecting all titles and prices separately. A missing field then cannot shift every following pair."),
     ("Rejected record; structure contract", "A rejected record is a visible parsing problem. Missing the whole expected container is a different failure from one malformed card; do not convert it to a successful empty list.")],
    "Suppose three titles exist but only two prices. zip(all_titles, all_prices) silently mispairs records and drops one. "
    "Instead, loop over cards and read fields inside that card. Preserve diagnostics so you can inspect the source. "
    "This teaching parser returns valid cards and rejected positions; a monitoring pipeline should refuse to replace a complete snapshot while required records are rejected. "
    "A legitimate empty catalogue needs an explicit empty-state signal you define, not merely zero selector matches.",
    'for card in root.select("article.item"):\n    title = card.select_one("h2")\n    price = card.select_one(".price")\n    validate fields before appending',
    CARD_PARSER + '''
html = '<main id="catalog"><article class="item"><h2>Book</h2><span class="price">12.50</span></article><article class="item"><h2>Pen</h2></article></main>'
records, rejected = parse_cards(html)
print(records)
print("Rejected cards:", rejected)
''',
    "Book र 12.50 एउटै article बाट आएको छ। Pen मा price छैन, त्यसैले card 2 rejected हुन्छ। "
    "त्यसलाई zero price नबनाऊ। Monitoring मा एउटा reject भए पनि नयाँ complete snapshot भनेर publish नगर्नु।",
    ('zip(soup.select("h2"), soup.select(".price"))', 'Read h2 and .price inside each article.item',
     "Independent lists can have unequal length/order when a field is missing."),
    "Parse two complete cards and verify no positions were rejected.",
    CARD_PARSER + '''
html = '<main id="catalog"><article class="item"><h2>A</h2><span class="price">1</span></article><article class="item"><h2>B</h2><span class="price">2</span></article></main>'
records, rejected = parse_cards(html)
print([row["title"] for row in records], rejected)
''',
    "Pass a login page with no #catalog and verify a structural failure, not a successful empty dataset.",
    CARD_PARSER + '''
try:
    parse_cards('<h1>Sign in</h1>')
except ValueError as error:
    print(error)
''',
    "Fields belong to their record. Report missing cards/fields; only replace a snapshot after the expected page and complete records have been validated.",
    [("Why select the price inside each card?", "To preserve field association", "To calculate a timeout", "To execute JavaScript", "Independent field lists can drift when one field is missing."),
     ("Is a login page with zero matching cards a valid empty catalogue?", "No", "Yes", "Only if status is 200", "The expected structure is absent, so acquisition/parsing failed.")])

add(1, "3. Parse a table by its headers and row shape",
    "Turn a simple semantic HTML table into validated dictionaries.",
    [("thead; tbody; th; td", "These elements mark header/body rows and cells. Read the intended table, then check its column contract before interpreting values."),
     ("rowspan/colspan limitation", "A table cell can span several rows/columns. The simple parser here rejects spans; it is not a general spreadsheet-like HTML table engine.")],
    "A pricing table and a layout table can both use table tags. Select the intended #prices table and require exact headers. "
    "Then each body row must have the expected number of cells. Reject spanning cells rather than pretending index positions stay simple. "
    "Text from td is still text; Day 2 Part 4 converts prices with an explicit currency rule. "
    "Do not silently zip three headers against two cells. If a website changes its columns, make that change visible before saving data.",
    'headers = [cell.get_text(strip=True) for cell in table.select("thead th")]\nif headers != expected: raise ValueError\nfor row in table.select("tbody tr"): check cells, then zip',
    '''
    from bs4 import BeautifulSoup
    html = '<table id="prices"><thead><tr><th>Item</th><th>Price</th></tr></thead><tbody><tr><td>Book</td><td>12.50</td></tr><tr><td>Pen</td><td>2.00</td></tr></tbody></table>'
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one("#prices")
    if table is None or table.select("[rowspan], [colspan]"):
        raise ValueError("Unsupported table shape")
    headers = [cell.get_text(" ", strip=True) for cell in table.select("thead th")]
    if headers != ["Item", "Price"]:
        raise ValueError("Unexpected headers")
    records = []
    for row in table.select("tbody tr"):
        cells = [cell.get_text(" ", strip=True) for cell in row.select("td")]
        if len(cells) != len(headers):
            raise ValueError("Unexpected row width")
        records.append(dict(zip(headers, cells)))
    print(records)
    ''',
    "पहिला header contract जाँचिन्छ, त्यसपछि row-width। Price अहिले string हो—अर्को part मा exact money मा बदल्छौँ। "
    "rowspan/colspan देखियो भने यो simplified parser को दायरा बाहिर भएको स्पष्ट error हुन्छ।",
    ('dict(zip(headers, cells))  # ignore lengths', 'Require equal lengths before zip',
     "zip stops at the shortest input; it does not validate row shape."),
    "Demonstrate a malformed row failing a two-column contract.",
    '''
    headers = ["Item", "Price"]
    cells = ["Book"]
    print("Reject row" if len(cells) != len(headers) else dict(zip(headers, cells)))
    ''',
    "Detect a colspan cell and explain why this part must not flatten it as one ordinary column.",
    '''
    from bs4 import BeautifulSoup
    soup = BeautifulSoup('<table><tr><td colspan="2">Total</td></tr></table>', "html.parser")
    print("Spanning cells:", len(soup.select("td[colspan], td[rowspan]")))
    ''',
    "Read a table by a known header contract; reject shape changes and spans you have not implemented. Parsing strings is not numeric validation.",
    [("Does zip reject unequal input lengths?", "No", "Yes", "Only for HTML", "It truncates to the shortest input."),
     ("Does this simple parser support arbitrary rowspan/colspan tables?", "No", "Yes", "Only when prices are numbers", "Spanning cells need a separately designed expansion algorithm.")])

MONEY = '''
import re
from decimal import Decimal

def price_cents(text):
    # Fixture contract: USD prefix, optional grouped commas, exactly 2 decimals.
    value = " ".join(text.split())
    pattern = r"USD (?:[0-9]+|[0-9]{1,3}(?:,[0-9]{3})+)\\.[0-9]{2}"
    if re.fullmatch(pattern, value) is None:
        raise ValueError("Unexpected USD price format")
    return int(Decimal(value[4:].replace(",", "")) * 100)
'''

add(1, "4. Normalize text, but validate money and identity",
    "Convert known price text to exact minor units without losing currency or inventing locale rules.",
    [("Decimal; integer minor units", "Decimal represents decimal values from strings exactly. cents are integer minor units for this USD example; different currencies may have different minor-unit conventions."),
     ("Normalization versus validation", "Normalization standardizes accepted text, such as whitespace. Validation decides whether the value belongs to your accepted format; stripping every nondigit is not validation."),
     ("Stable source id", "A source's record id helps compare observations over time. A title or current display position is not necessarily a stable unique identifier.")],
    "BeautifulSoup decodes HTML entities, but it cannot know whether '1,299.00' and '1.299,00' mean the same amount in your source. "
    "Define the accepted source format: here USD, a space, a nonnegative amount and exactly two decimals. "
    "A fullmatch rejects other currencies, decimal separators and malformed comma groups. Convert with Decimal from the string, then store integer cents. "
    "This uses regex after structural HTML parsing, where a small known text format is appropriate. Keep the currency alongside the amount.",
    'validate full price format\namount = Decimal(validated_numeric_text)\ncents = int(amount * 100)',
    MONEY + '''
print(price_cents("USD 1,299.00"))
print(price_cents("USD\\u00a0 12.50"))
try:
    price_cents("EUR 12,50")
except ValueError:
    print("Reject unknown currency/format")
''',
    "1299 dollars = 129900 cents। NBSP/extra spaces normalized हुन्छन्, तर currency/decimal rule बदलिएको हुँदैन। "
    "Float मा पैसाको गणना नगर; malformed amount लाई digits मात्र बाँकी राखेर plausible number बनाउनु गलत हो।",
    ('int(re.sub(r"\\D", "", price))', 'Validate currency/format, then convert Decimal to minor units',
     "Removing all nondigits can erase signs, decimal separators and currency information."),
    "Convert USD 0.10 and USD 0.20 and add their exact cents.",
    MONEY + '''
print(price_cents("USD 0.10") + price_cents("USD 0.20"))
''',
    "Reject bad comma grouping, a negative price and excess precision using the same contract.",
    MONEY + '''
for text in ["USD 12,34.00", "USD -2.00", "USD 1.234"]:
    try:
        price_cents(text)
    except ValueError:
        print("Rejected:", text)
''',
    "Normalize only accepted variation. Preserve currency and stable identity; validate the complete numeric format and use exact money values.",
    [("Is stripping every nondigit a safe price parser?", "No", "Yes", "Only for dollars", "It loses signs, separators and currency context."),
     ("What is the exact sum of 10 cents and 20 cents?", "30 integer cents", "A guessed float string", "3000 dollars", "Integer minor units keep this arithmetic exact.")])

URL_HELPER = '''
from urllib.parse import urljoin, urldefrag, urlsplit

BASE = "https://example.org/catalog/"

def listing_link(current, href):
    if not href:
        return None
    url = urldefrag(urljoin(current, href))[0]
    parts = urlsplit(url)
    if parts.scheme != "https" or parts.netloc != "example.org":
        return None
    if not parts.path.startswith("/catalog/"):
        return None
    return url
'''

add(2, "1. Relative links, fragments and crawl boundaries",
    "Resolve relative URLs while keeping a small listing crawl within its intended scope.",
    [("urljoin; urldefrag; urlsplit", "urljoin resolves a link against the current page; an absolute href can replace the origin. urldefrag removes the fragment; urlsplit exposes components for checks."),
     ("Origin/path allowlist", "A crawler should check scheme, server and intended path after resolution. This lesson permits exactly https://example.org/catalog/ paths; it is a narrow classroom rule, not a universal URL validator."),
     ("Canonicalization limits", "Removing fragments avoids fetching one document for each anchor. Query parameters may change data, so do not strip every query or merge it blindly.")],
    "The link '?page=2' is relative to the current listing. '/catalog/page2' is rooted at the origin. An absolute https://other.example/... points elsewhere. "
    "urljoin is a resolver, not a permission check. Check the resolved address, not whether the original text starts with '/'. "
    "Skip mailto/javascript links and out-of-scope paths. Never crawl every link found on a page. "
    "A real fetcher must re-check redirect targets; checking only the initial URL is insufficient. We use explicit no-redirect requests in acquisition practice.",
    'resolved = urldefrag(urljoin(current_url, href))[0]\nparts = urlsplit(resolved)\nif scheme/origin/path not allowed: skip',
    URL_HELPER + '''
for href in ["?page=2#top", "../private", "https://other.example/catalog/", "mailto:a@example.org"]:
    print(href, "=>", listing_link(BASE, href))
''',
    "?page=2 query बाँकी छ; #top मात्र हट्यो। ../private catalog बाहिर पर्छ, अर्को server पनि reject हुन्छ। "
    "यो link-filter हो; content permission, redirect र robots जाँच अर्को चरण हुन्।",
    ('urljoin(base, href)  # assume it remains on the same website', 'Resolve, then validate the resulting scheme/origin/path',
     "An absolute href replaces the original origin."),
    "Resolve page2 and ./page3#items within the listing scope.",
    URL_HELPER + '''
for href in ["page2", "./page3#items"]:
    print(listing_link(BASE, href))
''',
    "Keep distinct page=1/page=2 queries but treat two fragments on page=1 as the same document.",
    '''
    from urllib.parse import urldefrag
    urls = ["https://example.org/catalog/?page=1#a", "https://example.org/catalog/?page=1#b", "https://example.org/catalog/?page=2"]
    print(len({urldefrag(url)[0] for url in urls}))
    ''',
    "Resolve first, validate second. Keep meaningful queries, remove document fragments and bound the crawl to a defined source/path.",
    [("Can urljoin return a different host?", "Yes", "No", "Only without HTTPS", "An absolute link supplies its own origin."),
     ("Should page query parameters always be removed?", "No", "Yes", "Only for pagination", "They may identify distinct pages and datasets.")])

PAGINATION = URL_HELPER + '''
from bs4 import BeautifulSoup

PAGES = {
    BASE: '<main id="catalog"><article data-id="A">Book</article><a rel="next" href="?page=2">Next</a></main>',
    BASE + '?page=2': '<main id="catalog"><article data-id="B">Pen</article></main>',
}

def walk_pages(pages, max_pages=3):
    url, visited, ids = BASE, set(), []
    while url is not None:
        if url in visited:
            raise ValueError("Pagination cycle")
        if len(visited) >= max_pages:
            raise ValueError("Page budget exhausted: incomplete crawl")
        visited.add(url)
        soup = BeautifulSoup(pages[url], "html.parser")
        root = soup.select_one("#catalog")
        if root is None:
            raise ValueError("Listing structure missing")
        ids.extend(card["data-id"] for card in root.select("article[data-id]"))
        next_link = root.select_one('a[rel~="next"]')
        if next_link is None:
            url = None
        else:
            target = listing_link(url, next_link.get("href"))
            if target is None:
                raise ValueError("Next link outside scope")
            url = target
    return ids, len(visited)
'''

add(2, "2. Pagination with a visited set and a page budget",
    "Follow next links and distinguish completion from a loop or truncated crawl.",
    [("rel=next", "Some pages annotate the next navigation link with rel='next'. The CSS ~= selector matches a whitespace-separated attribute token; real sources may use a different documented control."),
     ("Visited set; page budget", "Visited URLs detect repeated pages. A maximum page count bounds work; reaching it while another page exists is incomplete acquisition, not successful completion."),
     ("Fixture page map", "A dictionary maps URLs to authored HTML, replacing HTTP acquisition so you can test crawl logic offline.")],
    "First understand the loop with two local HTML strings. Parse a page, collect its records, inspect its next link, resolve it, then continue. "
    "Stop normally only when the expected final-page rule is met. A cycle, missing page fixture or out-of-scope next link is a failure. "
    "A visited set prevents infinite revisits; a page budget handles endlessly changing URLs. In a real crawl add request timeouts, policy checks and delays before each acquisition. "
    "Do not mistake a budget-limited partial result for a complete dataset when comparing removed listings.",
    'while next_url:\n    reject repeats and budget exhaustion\n    parse page\n    validate and resolve next link',
    PAGINATION + '''
ids, count = walk_pages(PAGES)
print(ids)
print("Pages:", count)
''',
    "visited मा URLs राखिन्छन्, product IDs होइन। दुई page पुगेपछि next link छैन, त्यसैले complete। "
    "Budget पुगेको बेला next link बाँकी भए 'सब देखियो' भनेर नमान; failure report गर।",
    ('while next_link: follow forever', 'Track visited URLs and stop with a failure when the finite page budget is exhausted',
     "A broken Next control can cycle or generate infinitely many URLs."),
    "Make page 2 point back to page 1 and verify a cycle is reported.",
    PAGINATION + '''
pages = dict(PAGES)
pages[BASE + '?page=2'] = '<main id="catalog"><a rel="next" href="/catalog/">Next</a></main>'
try:
    walk_pages(pages)
except ValueError as error:
    print(error)
''',
    "Set max_pages=1 for the two-page listing; verify it fails instead of saving only page 1 as complete.",
    PAGINATION + '''
try:
    walk_pages(PAGES, max_pages=1)
except ValueError as error:
    print(error)
''',
    "Completion must be evidence-based. Detect cycles, bound pages and label truncation as incomplete; never infer removals from a partial crawl.",
    [("Is hitting a page budget proof that acquisition is complete?", "No", "Yes", "Only for HTTPS", "There may still be unvisited pages."),
     ("What belongs in the visited set?", "Resolved page URLs", "Only product titles", "Timeout seconds", "The set detects page revisits.")])

DEDUP = '''
def deduplicate(rows):
    by_id = {}
    for row in rows:
        identity = row["id"]
        if identity in by_id and by_id[identity] != row:
            raise ValueError("Conflicting duplicate: " + identity)
        by_id[identity] = row
    return [by_id[key] for key in sorted(by_id)]
'''

add(2, "3. Duplicate listings and conflicting observations",
    "Merge overlapping pages by stable id while refusing inconsistent records.",
    [("Identity-based deduplication", "An id identifies the same listing across pages. Exact repeated observations can be collapsed; identical titles with different ids remain distinct records."),
     ("Conflicting duplicate", "If one run reports different values for the same id, a silent last-write-wins rule can hide inconsistency. This lesson stops and requires inspection."),
     ("Deterministic ordering", "Sorting ids produces predictable output independent of page overlap/order. It does not establish completeness or resolve conflicts.")],
    "Featured listings often repeat on adjacent pages. A set of titles can merge different products, while a set of full dictionaries is not available because dictionaries are unhashable. "
    "Use a dictionary keyed by the source's stable id. Equal repeats are harmless under this contract. Different price/title observations for one id might indicate live changes or broken selectors. "
    "Keep that conflict visible rather than arbitrarily choosing a record. You could design a timestamped observation model later; here a consistent run is required. "
    "Never use a row index as an identity across days.",
    'by_id = {}\nfor row in rows:\n    if id exists with different values: reject\n    by_id[id] = row',
    DEDUP + '''
rows = [{"id": "B", "title": "Book", "cents": 200}, {"id": "A", "title": "Book", "cents": 100}, {"id": "B", "title": "Book", "cents": 200}]
print(deduplicate(rows))
''',
    "A र B को title एउटै भए पनि अलग IDs भएकाले दुई records रहन्छन्। B को exact repeat मात्र घट्छ। "
    "Sorting ले output predictable हुन्छ; source पूरा छ भन्ने प्रमाण होइन।",
    ('by_title[row["title"]] = row', 'by_id[row["id"]] = row, with conflict checks',
     "Titles can collide or change; use a source identity contract."),
    "Reject two different prices for id A.",
    DEDUP + '''
try:
    deduplicate([{"id": "A", "cents": 100}, {"id": "A", "cents": 200}])
except ValueError as error:
    print(error)
''',
    "Show that exact deduplication is idempotent: applying it twice leaves the same result.",
    DEDUP + '''
rows = [{"id": "A", "cents": 100}, {"id": "A", "cents": 100}]
once = deduplicate(rows)
print(deduplicate(once) == once)
''',
    "Deduplicate by stable id; preserve same-title different-id records. Reject conflicts, sort deterministically and keep completeness checks separate.",
    [("Should different IDs with the same title always merge?", "No", "Yes", "Only for books", "A title is not necessarily a unique identity."),
     ("What does this lesson do with conflicting duplicate IDs?", "Reject the run for inspection", "Silently keep the last", "Average every field", "Conflicts can reveal inconsistent acquisition or parsing.")])

add(2, "4. Export CSV/JSON without turning titles into formulas",
    "Preserve validated data in JSON and create a separate spreadsheet-facing CSV representation.",
    [("Spreadsheet formula interpretation", "Some spreadsheet apps interpret fields beginning with =, +, -, @ and certain leading whitespace/control characters as formulas. CSV quoting alone does not ensure literal display."),
     ("Canonical versus display export", "Keep original titles in canonical JSON. A spreadsheet-facing export can prefix risky titles with an apostrophe under an explicit policy; this changes the representation and should be documented."),
     ("Source provenance", "Keep source URL, retrieval time and currency with records so a number can be traced back to the observation that produced it.")],
    "Week 23's DictWriter handles commas and newlines but does not decide how Excel interprets a cell. "
    "Keep validated titles unchanged in JSON; adapt only the spreadsheet presentation. Our conservative classroom display policy prefixes values whose trimmed start is risky. "
    "This is not a universal guarantee for every spreadsheet/import setting; for controlled office reports you can generate explicitly typed text cells using Week 24. "
    "Write UTF-8 with newline='' for real CSV files. Store integer cents and currency rather than a formatted price string as the numeric source of truth.",
    'canonical JSON: preserve original values\nspreadsheet CSV: apply a documented text display policy\nDictWriter: handles CSV quoting, not formula interpretation',
    '''
    import csv, io, json
    row = {"id": "A", "title": "=1+1", "currency": "USD", "cents": 1250}
    def spreadsheet_text(text):
        return "'" + text if text.lstrip().startswith(("=", "+", "-", "@")) or text.startswith(("\\t", "\\r", "\\n")) else text
    display = dict(row, title=spreadsheet_text(row["title"]))
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(row), lineterminator="\\n")
    writer.writeheader()
    writer.writerow(display)
    print(stream.getvalue().strip())
    print(json.dumps(row, ensure_ascii=False, sort_keys=True))
    ''',
    "CSV display मा title अगाडि apostrophe छ, JSON मा original =1+1 नै छ। "
    "CSV quote राख्नु मात्रै spreadsheet formula रोक्ने उपाय होइन। Currency/amount छुट्टै राख।",
    ('CSV quoting makes every imported title safe literal text', 'Separate canonical data from a documented spreadsheet text export',
     "CSV syntax escaping and spreadsheet expression interpretation are different layers."),
    "Round-trip a title containing a comma through DictWriter/DictReader without splitting its text.",
    '''
    import csv, io
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=["id", "title"], lineterminator="\\n")
    writer.writeheader()
    writer.writerow({"id": "A", "title": "Book, revised"})
    stream.seek(0)
    print(next(csv.DictReader(stream)))
    ''',
    "Keep Japanese titles literal when round-tripping canonical JSON.",
    '''
    import json
    row = {"id": "A", "title": "日本語の本", "currency": "USD", "cents": 1250}
    text = json.dumps(row, ensure_ascii=False)
    print(text)
    print(json.loads(text) == row)
    ''',
    "Keep canonical values, exact money and provenance. CSV quoting preserves delimiters; spreadsheet display safety needs its own explicit policy.",
    [("Does CSV quoting alone prevent spreadsheet formula interpretation?", "No", "Yes", "Only for UTF-8", "Quoting is CSV syntax, not spreadsheet cell typing."),
     ("Where should the original title be preserved?", "Canonical stored data", "Only a modified display field", "Nowhere", "Display adaptations should not erase the source observation.")])

def browser_example(html, body):
    return (
        "from playwright.sync_api import sync_playwright\n"
        + "html = " + repr(html) + "\n"
        + "with sync_playwright() as p:\n"
        + "    browser = p.chromium.launch(headless=True)\n"
        + "    try:\n"
        + "        page = browser.new_page()\n"
        + "        page.set_default_timeout(1500)\n"
        + '        page.route("**/*", lambda route: route.abort())\n'
        + "        page.set_content(html)\n"
        + textwrap.indent(clean(body), "        ")
        + "    finally:\n"
        + "        browser.close()\n"
    )


DYNAMIC_HTML = """<main><h1>Own practice catalogue</h1><section id="items"></section>
<script>document.getElementById('items').innerHTML='<article class="item">Book</article>';</script></main>"""

add(3, "1. Source HTML and the rendered DOM are different",
    "Diagnose a JavaScript-rendered listing before deciding whether a browser is necessary.",
    [("DOM; JavaScript rendering", "The DOM is the browser's current document tree. Page JavaScript may add elements after the initial HTML arrives. requests retrieves bytes; it does not build that rendered state."),
     ("Documented API versus hidden implementation", "If a source offers an allowed documented API/export, prefer that structured interface. Seeing a request in browser tools does not itself grant permission to reuse private or restricted endpoints."),
     ("Headless browser", "A browser without a visible window still executes page JavaScript and loads resources. It has greater cost and a broader request footprint than parsing a saved HTML string.")],
    "Zero matches can mean a wrong selector, an error page, genuinely empty data, or client-side rendering. Inspect the response and the browser's rendered Elements tree before choosing a tool. "
    "The fixture contains a tiny authored JavaScript statement that adds an article. The parser sees an empty section; a browser executes the statement. "
    "You do not need to learn general JavaScript today: the script only demonstrates why HTTP text and rendered DOM differ. "
    "BeautifulSoup works well on markup already containing data. A browser is useful only when the required allowed interaction/rendering cannot be obtained from an appropriate structured source.",
    'requests / saved HTML -> original markup\nbrowser -> run JavaScript -> rendered DOM\nBeautifulSoup -> parse the supplied markup',
    '''
    from bs4 import BeautifulSoup
    html = """<section id="items"></section><script>
    document.getElementById('items').innerHTML='<article class="item">Book</article>';
    </script>"""
    soup = BeautifulSoup(html, "html.parser")
    print("Initial articles:", len(soup.select("#items article.item")))
    print("Script present:", soup.find("script") is not None)
    ''',
    "Script text भित्र article लेखिएको छ, तर original HTML tree मा त्यो article छैन। "
    "BeautifulSoup ले script चलाउँदैन। Browser पछि generated elements देखाउन सक्छ; error page भए browser रोज्नु समाधान होइन।",
    ('No matches -> always launch a browser', 'Inspect status, source structure, selectors and rendering before choosing a tool',
     "A missing selector can be an acquisition or layout problem, not a JavaScript problem."),
    "Compare an initial empty section with an already-rendered saved snapshot containing one article.",
    '''
    from bs4 import BeautifulSoup
    initial = '<section id="items"></section>'
    rendered = '<section id="items"><article class="item">Book</article></section>'
    for label, html in [("initial", initial), ("rendered snapshot", rendered)]:
        print(label, len(BeautifulSoup(html, "html.parser").select(".item")))
    ''',
    "Validate that status 200 alone cannot distinguish an HTML listing from a login page.",
    '''
    from bs4 import BeautifulSoup
    for html in ['<h1>Login</h1>', '<main id="catalog"><article class="item">A</article></main>']:
        soup = BeautifulSoup(html, "html.parser")
        print("Catalogue exists:", soup.select_one("#catalog") is not None)
    ''',
    "Diagnose before changing tools. Initial bytes, rendered DOM and authorized structured data are different sources. A headless browser is still a browser, not an access bypass.",
    [("Will requests run the script that adds the product cards?", "No", "Yes", "Only for HTTPS", "Requests is an HTTP client, not a JavaScript browser engine."),
     ("Does a 200 login page prove the listing was acquired?", "No", "Yes", "Only if it contains text", "The listing's expected structure is absent.")])

add(3, "2. Playwright: launch, wait for a result and close",
    "Read an authored dynamic page with an isolated browser and a condition-based wait.",
    [("sync_playwright; chromium.launch", "Playwright's synchronous Python API manages a browser driver. launch(headless=True) opens a fresh automated browser, not your personal Chrome profile."),
     ("browser.new_page; page.set_content", "new_page creates a tab; set_content loads our supplied fixture HTML. A real allowed URL uses page.goto with explicit timeouts and response/policy checks."),
     ("locator; wait_for; inner_text", "A locator describes elements. wait_for(state='visible') waits for a specific condition; inner_text reads rendered text. count is a snapshot, not a wait for future items."),
     ("route.abort; browser.close", "The fixture aborts outgoing network resources so its inline local script is the only rendering input. finally closes the browser even on failure.")],
    "Install playwright and its Chromium binary once using the setup commands below. The supplied HTML and inline script run offline afterward. "
    "Locate one expected article and wait for visible state with a finite timeout. Do not sleep five seconds and hope loading finished. "
    "For a real page, goto('...') getting an HTML document still does not prove the data was rendered; wait for a source-specific completion condition. "
    "The route policy here is deliberately offline and would prevent a real remote page from loading; remove/replace it only for an authorized, explicitly scoped real-source adapter.",
    'with sync_playwright() as p:\n    browser = p.chromium.launch()\n    try:\n        page = browser.new_page()\n        page.set_content(html)\n        page.locator(".item").wait_for(state="visible")\n    finally:\n        browser.close()',
    browser_example(DYNAMIC_HTML, '''
    item = page.locator("#items .item")
    item.wait_for(state="visible")
    print(item.inner_text())
    print("Count:", item.count())
    '''),
    "Original HTML मा article थिएन, तर अब browser ले script चलाएर Book देखायो। "
    "wait_for ले expected element visible भयो कि जाँच्छ। count मात्र call गर्दा पछि आउने item को प्रतीक्षा हुँदैन।",
    ('time.sleep(5); read whatever is present', 'Wait for the expected result/completion condition with a finite timeout',
     "Fixed sleeps are slow when the page is ready and unreliable when it is not."),
    "Read a heading with a role locator instead of relying on a generated CSS class.",
    browser_example(DYNAMIC_HTML, '''
    heading = page.get_by_role("heading", name="Own practice catalogue")
    heading.wait_for(state="visible")
    print(heading.inner_text())
    '''),
    "Catch Playwright's timeout for a missing item and report a failed observation.",
    browser_example('<main><h1>Empty fixture</h1></main>', '''
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    try:
        page.locator(".missing").wait_for(state="visible", timeout=100)
    except PlaywrightTimeoutError:
        print("Expected element missing: preserve previous data")
    '''),
    "Use a fresh browser, explicit readiness conditions, finite waits and finally cleanup. Fixture routing is offline test scaffolding, not a real website policy.",
    [("Does locator.count() wait for products to appear later?", "No", "Yes", "Only when there are none", "It reports current matches; wait for an appropriate condition first."),
     ("Where should browser.close run?", "In finally", "Only after successful parsing", "Never", "Finally releases resources on failure too.")])

BUTTON_HTML = """<main><ul id="items"><li class="item">Book</li></ul>
<button id="more" onclick="document.getElementById('items').insertAdjacentHTML('beforeend','<li class=&quot;item&quot;>Pen</li>');this.disabled=true;">Load more</button></main>"""

add(3, "3. Click an allowed Load more control; verify the change",
    "Use a scoped button locator and wait for the additional record before extracting.",
    [("get_by_role; click; is_enabled", "A role/name locator can identify a button by its visible purpose. click performs actionable interaction; is_enabled reports its current enabled state."),
     ("expect(locator).to_have_count", "Playwright's assertion retries until the count matches or its timeout expires. It is useful for waiting for a known fixture result."),
     ("Interaction boundary", "Only interact with an allowed read-only listing control. A purchase/delete/submit action is a different operation from acquiring displayed catalogue data.")],
    "Some listings hide data behind Load more. Clicking successfully is only an action result; prove the records actually appeared. "
    "Our authored button adds one item and disables itself. Wait for two items before reading their text. "
    "The JavaScript in the fixture is provided input, not a new Python feature. The browser runs it; our Python only chooses a button and observes the DOM. "
    "A source can use a spinner or explicit completion attribute instead of count; pick the condition from the actual source contract rather than using arbitrary sleeps.",
    'page.get_by_role("button", name="Load more").click()\nexpect(page.locator("#items .item")).to_have_count(2)\nread the result',
    browser_example(BUTTON_HTML, '''
    from playwright.sync_api import expect
    button = page.get_by_role("button", name="Load more")
    button.click()
    expect(page.locator("#items .item")).to_have_count(2)
    print(page.locator("#items .item").all_inner_texts())
    print("Can load more:", button.is_enabled())
    '''),
    "Button click पछि दुई items आएको पुष्टि छ, अनि text पढिएको छ। "
    "Disabled button अन्तिम page संकेत हो—यो हाम्रो fixture को contract हो, सबै website को universal rule होइन।",
    ('button.click(); assume the data arrived', 'Click, then wait for the source-specific data/completion signal',
     "UI interaction can trigger asynchronous work; actionability is not dataset completeness."),
    "Verify that an initially disabled fixture button should not be clicked.",
    browser_example('<button disabled>Load more</button><p>End of listing</p>', '''
    button = page.get_by_role("button", name="Load more")
    print("Fetch another batch:", button.is_enabled())
    '''),
    "After rendering, parse the browser's HTML snapshot with the same BeautifulSoup parser style.",
    browser_example(BUTTON_HTML, '''
    from bs4 import BeautifulSoup
    from playwright.sync_api import expect
    page.get_by_role("button", name="Load more").click()
    expect(page.locator("#items .item")).to_have_count(2)
    soup = BeautifulSoup(page.content(), "html.parser")
    print([node.get_text(strip=True) for node in soup.select("#items .item")])
    '''),
    "Action success and data readiness are separate. Use allowed read controls, wait for the known result, and reuse parser validation on a rendered snapshot.",
    [("Does a successful button click prove all records loaded?", "No", "Yes", "Only in headless mode", "You must verify the resulting data/completion state."),
     ("Which fixture control is appropriate to click?", "Load more listing data", "Buy now", "Delete account", "The lesson acquires read-only listing observations.")])

MULTI_BUTTON = """<main><ul id="items"><li class="item">Book</li></ul>
<button id="more" onclick="const names=['Pen','Notebook'];const i=Number(this.dataset.index||0);document.getElementById('items').insertAdjacentHTML('beforeend','<li class=&quot;item&quot;>'+names[i]+'</li>');this.dataset.index=String(i+1);if(i+1===names.length)this.disabled=true;">Load more</button></main>"""

add(3, "4. Bound dynamic acquisition and capture one stable snapshot",
    "Stop a dynamic listing using a tested end rule and a finite click budget.",
    [("Click budget; no-progress failure", "Bound interactions to avoid endlessly clicking a broken/infinite control. If expected progress does not arrive, fail rather than save a partial snapshot."),
     ("Rendered snapshot", "page.content() captures the current DOM as HTML. Save acquisition metadata separately; the snapshot does not itself prove that every page/batch was acquired."),
     ("Browser versus HTTP cost", "A browser can request scripts/images/analytics as well as documents. Rate/policy design must account for resource traffic, not just Python's goto calls.")],
    "Each click in this owned fixture adds exactly one item; after two clicks the button is disabled. We set a maximum of three clicks and wait for count growth after every click. "
    "If a real source has variable batch sizes, define a suitable completion marker instead of copying this exact +1 assumption. "
    "A still-enabled button after budget exhaustion means incomplete work. Close the browser and retain the prior snapshot. "
    "Do not try to solve access denial with stealth, CAPTCHA bypass or rotating identities; use a permitted source/interface.",
    'for each allowed click within budget:\n    capture count; click; wait for progress\nif more remains: report incomplete\ncapture and validate final snapshot',
    browser_example(MULTI_BUTTON, '''
    from playwright.sync_api import expect
    button, items = page.get_by_role("button", name="Load more"), page.locator("#items .item")
    for _ in range(3):
        if not button.is_enabled():
            break
        before = items.count()
        button.click()
        expect(items).to_have_count(before + 1)
    if button.is_enabled():
        raise ValueError("Click budget exhausted")
    print(items.all_inner_texts())
    print("Complete:", not button.is_enabled())
    '''),
    "Book बाट Pen अनि Notebook थपिन्छन्। Click budget भन्दा पहिले button disabled भएर fixture पूरा भएको प्रमाण मिल्यो। "
    "Budget पुगेको मात्रै completion होइन। Source को documented end condition चाहिन्छ।",
    ('for _ in range(10): click(); save partial data', 'Require an end signal; otherwise classify the run as incomplete',
     "A fixed number of clicks can silently truncate a longer listing."),
    "Use only one click and report that the two-batch fixture is incomplete.",
    browser_example(MULTI_BUTTON, '''
    from playwright.sync_api import expect
    button = page.get_by_role("button", name="Load more")
    button.click()
    expect(page.locator(".item")).to_have_count(2)
    print("Incomplete:", button.is_enabled())
    '''),
    "Capture the completed DOM and verify all three item labels using BeautifulSoup.",
    browser_example(MULTI_BUTTON, '''
    from playwright.sync_api import expect
    from bs4 import BeautifulSoup
    button = page.get_by_role("button", name="Load more")
    for expected in [2, 3]:
        button.click()
        expect(page.locator(".item")).to_have_count(expected)
    snapshot = page.content()
    soup = BeautifulSoup(snapshot, "html.parser")
    print([node.get_text(strip=True) for node in soup.select("#items .item")])
    '''),
    "Bound interactions and verify progress plus completion. Save validated snapshots with provenance; do not call budget exhaustion success.",
    [("If Load more remains enabled at the click limit, is the run complete?", "No", "Yes", "Only when the count is positive", "Remaining batches may still exist."),
     ("Is a browser request footprint only one HTML request?", "No", "Yes", "Only in headless mode", "Scripts and other subresources may also be fetched.")])

ROBOTS = '''
from urllib.robotparser import RobotFileParser

agent = "StudyHubPractice"
robots = RobotFileParser()
robots.parse([
    "User-agent: StudyHubPractice",
    "Disallow: /private/",
    "Allow: /catalog/",
    "Crawl-delay: 2",
    "Request-rate: 1/2",
])
'''

add(4, "1. Choose an allowed source and interpret robots.txt",
    "Check a source's crawl policy without mistaking it for authorization.",
    [("robots.txt", "A site can publish crawler rules at its origin's /robots.txt. These are crawl instructions; an Allow rule does not grant access rights or override terms or restrictions."),
     ("RobotFileParser; parse; can_fetch", "The standard-library parser can read supplied lines and answer whether a user agent may fetch a URL under that policy. parse avoids fetching a remote policy in our offline fixture."),
     ("crawl_delay; request_rate", "These parser methods expose delay/rate hints when the policy includes supported values. They do not automatically slow requests; your acquisition code must implement pacing.")],
    "Begin with an owned practice page or a source that permits your intended use. Prefer a documented API/export when available. "
    "Respect stated terms and crawl restrictions; collect only the fields you need. Do not access private/login-protected data by circumventing controls. "
    "The supplied robots fixture permits the catalogue and disallows private paths. We query it using the same agent identity as the HTTP client. "
    "RobotFileParser is a practical parser, not a complete authority on every crawler's rule interpretation. For complex directives confirm the source's intended policy rather than assuming all tools behave identically.",
    'robots = RobotFileParser()\nrobots.parse(policy_lines)\nif not robots.can_fetch(agent, url): stop',
    ROBOTS + '''
print("Catalogue:", robots.can_fetch(agent, "https://example.org/catalog/"))
print("Private:", robots.can_fetch(agent, "https://example.org/private/"))
print("Delay:", robots.crawl_delay(agent))
rate = robots.request_rate(agent)
print("Rate:", rate.requests, "request per", rate.seconds, "seconds")
''',
    "can_fetch ले यो robots policy अन्तर्गत crawl rule बताउँछ, permission document होइन। "
    "Delay/rate आफैँ लागू हुँदैन; अर्को part मा आफ्नो loop ले त्यसलाई पालना गर्नुपर्छ।",
    ('robots allows it -> all uses are authorized', 'Confirm allowed use separately and obey the published crawl rules',
     "Crawl instructions and authorization are different questions."),
    "List only the URLs allowed by the supplied policy.",
    ROBOTS + '''
urls = ["https://example.org/catalog/page1", "https://example.org/private/profile"]
print([url for url in urls if robots.can_fetch(agent, url)])
''',
    "Change the policy to Disallow: / and verify a catalogue crawl stops.",
    '''
    from urllib.robotparser import RobotFileParser
    robots = RobotFileParser()
    robots.parse(["User-agent: *", "Disallow: /"])
    print("Can crawl:", robots.can_fetch("StudyHubPractice", "https://example.org/catalog/"))
    ''',
    "Choose an allowed source first. robots is a crawl policy, not permission or access control. Identify the crawler honestly and implement its pacing rules.",
    [("Does robots Allow override a source's access restrictions?", "No", "Yes", "Only for public HTML", "Crawl policy does not grant rights or bypass access restrictions."),
     ("Does crawl_delay automatically pause requests?", "No", "Yes", "Only in a Session", "The parser returns policy information; your loop must apply it.")])

add(4, "2. Unknown policy and redirects: stop and inspect",
    "Apply an explicit conservative policy when acquisition rules cannot be verified.",
    [("Unknown-policy state", "A failed/malformed robots acquisition is not the same as a verified permissive policy. This classroom workflow pauses for manual confirmation rather than inventing permission."),
     ("allow_redirects=False", "Requests normally follows GET redirects. This option lets you inspect a redirect without automatically requesting a new target; re-check origin, policy and permissions before following."),
     ("403 versus 429", "403 means the request is forbidden; do not solve it by identity tricks. 429 means rate limiting; honor the server's delay or stop. Different causes need different decisions.")],
    "Fetch a real robots file once per permitted origin with an explicit timeout and record its status/time. In this lesson we simulate those results rather than crawling a third party. "
    "Our policy accepts only a verified 200 text policy; every other result pauses for source-specific confirmation. "
    "This is a deliberately conservative learning rule, not a claim that every crawler standard treats missing robots the same way. "
    "A redirect can change the destination even after you validated the first URL. Prevent automatic following until the new target has been checked. "
    "A browser's subresources and navigation need equivalent scope thought; the classroom browser exercises have no remote requests.",
    'get(url, timeout=(3,10), allow_redirects=False)\nclassify status; do not auto-follow unknown destinations\nunknown policy -> pause for confirmation',
    '''
    def policy_ready(status, text):
        return status == 200 and isinstance(text, str) and text.strip().startswith("User-agent:")
    for status, text in [(200, "User-agent: *\\nDisallow: /private/"), (404, ""), (503, ""), (200, "<h1>Login</h1>")]:
        print(status, "inspect rules" if policy_ready(status, text) else "pause: unverified policy")
    ''',
    "404 वा 503 लाई allow-all बनाएको छैन। यो lesson को conservative rule हो। "
    "200 login HTML पनि robots होइन। Real policy parsing/confirmation पछि मात्रै listing request गर।",
    ('Policy fetch failed -> permit everything', 'Record unknown policy and pause for source-specific confirmation',
     "Failure to verify a rule is not a verified rule permitting the operation."),
    "Prepare a redirect response fixture and confirm the client was told not to follow it automatically.",
    '''
    import requests
    from unittest.mock import patch
    response = requests.Response()
    response.status_code = 302
    response.headers["Location"] = "https://other.example/catalog/"
    with patch("requests.get", return_value=response) as get:
        result = requests.get("https://example.org/catalog/", timeout=(3, 10), allow_redirects=False)
        print("Redirect:", result.status_code, result.headers["Location"])
        print("Auto-follow:", get.call_args.kwargs["allow_redirects"])
    ''',
    "Map a 403, 429 and 503 to distinct actions without making any network requests.",
    '''
    actions = {403: "Stop: access refused", 429: "Honor Retry-After or stop", 503: "Finite delayed retry if appropriate"}
    for status in [403, 429, 503]:
        print(status, actions[status])
    ''',
    "Keep allowed, denied and unknown distinct. Inspect redirects before following and never turn access denial into a request for evasion.",
    [("What does this classroom policy do with an unverified robots response?", "Pause for confirmation", "Assume allow-all", "Retry forever", "It avoids converting unknown policy into permission."),
     ("What does allow_redirects=False accomplish?", "Prevents automatic redirect following", "Disables TLS validation", "Runs page scripts", "You can inspect and validate the target before another request.")])

PACE = '''
class FakeClock:
    def __init__(self):
        self.now = 0.0
        self.waits = []
    def sleep(self, seconds):
        self.waits.append(seconds)
        self.now += seconds

def paced_starts(count, interval, clock):
    starts, last = [], None
    for _ in range(count):
        if last is not None:
            clock.sleep(max(0.0, interval - (clock.now - last)))
        last = clock.now
        starts.append(last)
    return starts
'''

add(4, "3. Per-origin pacing and a testable clock",
    "Space request starts using a monotonic clock and the stricter of local/source limits.",
    [("time.monotonic", "A monotonic clock measures elapsed time without moving backwards when the system's wall-clock date changes. Use it for wait intervals; store UTC wall time separately for provenance."),
     ("Per-origin interval", "Pacing belongs to the destination origin and should include retries as well as pages. A slow loop over page one is not enough if every retry fires immediately."),
     ("Injected clock/sleeper", "Passing a clock and sleeper into a helper lets a test simulate waiting instantly while production uses time.monotonic/time.sleep.")],
    "For a single sequential crawler choose the maximum of your conservative local interval, crawl-delay and any simplified request-rate spacing. "
    "For a rate of R requests in S seconds, a steady spacing of S/R seconds avoids a burst in this simple one-worker design. "
    "This helper demonstrates the mechanics with a fake clock: no actual waiting occurs in the printed example. "
    "Real production code uses monotonic time and sleep, and coordinates workers so they do not each independently violate a shared origin limit. "
    "Concurrency/scheduling details belong to later weeks; start with one small sequential crawler.",
    'interval = max(local_minimum, crawl_delay, rate_seconds / rate_requests)\nwait until last_start + interval\nrecord actual next start',
    PACE + '''
clock = FakeClock()
interval = max(1.0, 2.0, 2 / 1)
print("Starts:", paced_starts(3, interval, clock))
print("Waits:", clock.waits)
''',
    "Fake clock ले 0, 2, 4 seconds मा starts देखाउँछ; real दुई seconds कुरेको छैन। "
    "यो test र production sleep फरक हो। Retry पनि same origin pacing अन्तर्गत हुनुपर्छ।",
    ('Start every worker with its own independent unrestricted retry loop', 'Share origin pacing and count retries as requests',
     "Several individually polite loops can still overload one destination together."),
    "Use a stricter local minimum of 3 seconds and verify it wins over a 2-second source hint.",
    PACE + '''
clock = FakeClock()
print(paced_starts(3, max(3.0, 2.0), clock))
''',
    "Show how 2 requests per 10 seconds produces a 5-second steady spacing in this one-worker model.",
    PACE + '''
clock = FakeClock()
print(paced_starts(3, 10 / 2, clock))
''',
    "Pace by origin using elapsed time, honor the stricter limit and include retries. Fake clocks verify delay logic without making tests slow.",
    [("Which clock suits elapsed request pacing?", "time.monotonic", "A manually formatted date string", "A product id", "Monotonic time is meant for elapsed intervals."),
     ("Should retries bypass rate limits?", "No", "Yes", "Only after a timeout", "Retries are additional requests to the same destination.")])

RETRY_AFTER = '''
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

def retry_seconds(header, now):
    if header.isascii() and header.isdigit():
        return int(header)
    target = parsedate_to_datetime(header)
    if target.tzinfo is None:
        raise ValueError("Retry date needs a timezone")
    return max(0, int((target - now).total_seconds()))

now = datetime(2026, 10, 12, 12, 0, 0, tzinfo=timezone.utc)
'''

add(4, "4. 429, Retry-After and a finite waiting budget",
    "Interpret a server's retry instruction without retrying earlier than requested.",
    [("Retry-After", "This response header can specify nonnegative whole seconds or an HTTP date. It can accompany rate limiting or service unavailability; missing/invalid values need an explicit fallback policy."),
     ("Waiting budget", "If the requested wait exceeds your run budget, stop and resume later instead of shortening the wait and retrying early."),
     ("HTTP-date; parsedate_to_datetime", "The email.utils parser understands HTTP-style dates. Use timezone-aware UTC times for comparisons; use monotonic time for the actual waiting interval.")],
    "A 429 is feedback to reduce requests, not a reason to spin harder. Parse a valid Retry-After and wait at least that long, or stop. "
    "Our timestamp is fixed so the date example is reproducible; live code uses datetime.now(timezone.utc). "
    "If the server says 120 seconds and your remaining budget is 30, a min(delay,30) sleep violates the instruction. Stop instead. "
    "For a missing/malformed header choose a conservative finite fallback, report it and keep a retry attempt limit. "
    "Do not log secret headers or cookie values while diagnosing a rate limit.",
    'delay = parse_retry_after(header)\nif delay > remaining_budget: stop\nelse: wait at least delay, then retry within attempt limit',
    RETRY_AFTER + '''
for header in ["5", "Mon, 12 Oct 2026 12:00:10 GMT"]:
    print(header, "=>", retry_seconds(header, now))
delay, budget = retry_seconds("120", now), 30
print("Action:", "stop and resume later" if delay > budget else "wait")
''',
    "Integer header 5 seconds हो, HTTP date 10 seconds पछि छ। 120-second instruction लाई 30 मा काटेर फेरि request गरेको छैन। "
    "Long wait भए current run stop गरेर last good snapshot जोगाऊ।",
    ('sleep(min(server_delay, remaining_budget)); retry', 'If server_delay exceeds budget, stop rather than retry early',
     "Capping the wait then retrying can violate the requested minimum delay."),
    "Use a past Retry-After date and verify it produces no negative wait.",
    RETRY_AFTER + '''
print(retry_seconds("Mon, 12 Oct 2026 11:59:50 GMT", now))
''',
    "Report an invalid Retry-After instead of silently converting it to immediate retries.",
    RETRY_AFTER + '''
try:
    retry_seconds("soon", now)
except (ValueError, TypeError):
    print("Invalid Retry-After: apply conservative finite fallback or stop")
''',
    "Respect Retry-After or stop. Distinguish attempt limits from waiting budgets; do not shorten a required delay just to finish a run.",
    [("If the server asks for 120 seconds but the run budget is 30, what should you do?", "Stop and resume later", "Wait 30 and retry", "Ignore the header", "Stopping avoids retrying before the server's requested delay."),
     ("Can Retry-After be an HTTP date?", "Yes", "No", "Only an HTML tag", "The header supports both seconds and a date.")])

RETRY = '''
import requests

def fetch_html(get, url, wait, attempts=3):
    if attempts < 1:
        raise ValueError("Need at least one attempt")
    for attempt in range(attempts):
        try:
            response = get(url, timeout=(3, 10), allow_redirects=False)
        except (requests.Timeout, requests.ConnectionError):
            if attempt == attempts - 1:
                raise
        else:
            if response.status_code in (502, 503, 504):
                if attempt == attempts - 1:
                    response.raise_for_status()
            else:
                response.raise_for_status()
                media = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
                if response.status_code != 200 or media != "text/html":
                    raise ValueError("Expected 200 HTML")
                return response.text
        wait(2 ** attempt)
    raise RuntimeError("Unreachable")
'''

add(5, "1. Finite retries for transient failures, not every error",
    "Retry a small transient set without overwriting state or hiding schema/access errors.",
    [("Backoff; attempt budget", "Backoff increases delays between failed attempts; an attempt budget bounds the total requests. Our fixture logs requested waits rather than sleeping."),
     ("Dependency injection: get and wait", "Passing fetch and wait callables lets tests use local fixtures; real callers must integrate robots, origin pacing and Retry-After into their acquisition adapter."),
     ("Failure classification", "Timeouts/connection failures and selected 502/503/504 statuses are candidates for bounded retries. 403, 404, unexpected types and parser errors do not automatically improve by retrying.")],
    "This small helper teaches a finite retry loop for an idempotent GET. It retries timeout/connection errors and three chosen server statuses. "
    "Other HTTP errors raise immediately; 429 is deliberately not retried here because Day 5's Retry-After-aware pacing must be integrated first. "
    "The wait callable is where a real adapter enforces the stricter origin/server delay, not a bypass of those rules. "
    "Do not claim a retry makes the crawl reliable by itself: content validation, complete-page evidence and durable last-good state remain separate requirements.",
    'for attempt in range(limit):\n    try fetch\n    classify transient/permanent outcome\n    wait under policy before another attempt\nraise on final failure',
    RETRY + '''
from unittest.mock import Mock
response = requests.Response()
response.status_code = 200
response.headers["Content-Type"] = "text/html; charset=utf-8"
response.encoding = "utf-8"
response._content = b"<h1>Book</h1>"
get = Mock(side_effect=[requests.Timeout("fixture"), response])
waits = []
print(fetch_html(get, "https://example.org/catalog/", waits.append))
print("Attempts:", get.call_count, "waits:", waits)
''',
    "पहिलो Timeout, दोस्रो success: दुई attempts र एक wait। Fixture मा wait list मात्र हो। "
    "Production मा requests.get सिधै जोड्नुअघि robots/pacing/429 handling जोड्नुपर्छ। Schema error मा repeat गरेर गलत state save नगर।",
    ('Retry every exception forever', 'Retry only chosen transient failures within a finite policy-aware budget',
     "Permanent errors and programming bugs should remain visible, not loop indefinitely."),
    "Simulate a 404 and verify the helper tries only once.",
    RETRY + '''
from unittest.mock import Mock
response = requests.Response()
response.status_code = 404
get = Mock(return_value=response)
try:
    fetch_html(get, "https://example.org/missing", lambda seconds: None)
except requests.HTTPError:
    print("Attempts:", get.call_count)
''',
    "Exhaust two timeout attempts and confirm there is no wait after the final failed request.",
    RETRY + '''
from unittest.mock import Mock
get = Mock(side_effect=requests.Timeout("fixture"))
waits = []
try:
    fetch_html(get, "https://example.org/catalog/", waits.append, attempts=2)
except requests.Timeout:
    print("Attempts:", get.call_count, "waits:", waits)
''',
    "A retry is another request: honor policy, bound attempts, do not retry permanent errors blindly, and never treat failure as a successful empty observation.",
    [("Does this teaching helper retry a 404?", "No", "Yes", "Forever", "The same absent resource is not in its transient-status set."),
     ("What happens when the last timeout attempt fails?", "The failure propagates", "An empty successful result is returned", "The count restarts", "Failure stays distinct from a valid dataset.")])

CACHE = '''
import hashlib
import json
from pathlib import Path
import tempfile

def cache_key(url):
    return hashlib.sha256(url.encode("utf-8")).hexdigest()

def save_cache(folder, url, html, saved_at):
    entry = {"url": url, "html": html, "saved_at": saved_at, "parser_version": 1}
    path = folder / (cache_key(url) + ".json")
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(entry, ensure_ascii=False), encoding="utf-8")
    temporary.replace(path)
    return path
'''

add(5, "2. Cache provenance and detect layout changes",
    "Reuse saved HTML honestly and distinguish a cached observation from a fresh one.",
    [("SHA-256 URL cache key", "Hash a complete URL into a filename-safe key. The hash is a stable identifier for this cache, not encryption or permission to store sensitive pages."),
     ("Freshness; saved_at; parser_version", "Store when the HTML was obtained and the parser version. Cached content is an older observation; re-parsing it does not make its acquisition time new."),
     ("Atomic replacement; layout failure", "Write a temporary file then replace the target after serialization succeeds. If required selectors/schema change, fail and keep last-good results for inspection.")],
    "Caching reduces repeat requests and lets you debug parsing offline. Include the full query in the key so page=1 and page=2 do not overwrite each other. "
    "The example stores a fixed observation time; real acquisition records its actual UTC time. A parser-version number lets you trace changes in extraction logic. "
    "Choose an explicit freshness policy for a real tracker; never label yesterday's cached HTML as 'just fetched'. "
    "Keep caches small and scoped to allowed nonsensitive material. Do not export session cookies or private HTML to this public Study Hub repository.",
    'entry = {url, html, saved_at, parser_version}\nwrite temporary -> replace\non reuse: retain acquisition time and mark cache hit',
    CACHE + '''
with tempfile.TemporaryDirectory() as name:
    folder = Path(name)
    url = "https://example.org/catalog/?page=1"
    path = save_cache(folder, url, "<main id='catalog'>Book</main>", "2026-10-12T12:00:00Z")
    entry = json.loads(path.read_text(encoding="utf-8"))
    print(entry["url"], entry["saved_at"])
    print("Cache hit:", path.exists(), "parser:", entry["parser_version"])
''',
    "Cache लाई filename-safe hash दिइएको छ; secret encrypt भएको होइन। saved_at पुरानै observation time रहन्छ। "
    "Layout change भए cached HTML बाट diagnose गर्न मिल्छ; खाली result बनाएर prior state overwrite नगर।",
    ('Read cache and replace saved_at with now to call it fresh', 'Keep original acquisition time and identify cache reuse',
     "Re-reading stored bytes is not a fresh source observation."),
    "Verify different pagination queries receive different cache keys.",
    CACHE + '''
print(cache_key("https://example.org/catalog/?page=1") != cache_key("https://example.org/catalog/?page=2"))
''',
    "Reject a changed listing container using the known parser contract.",
    CARD_PARSER + '''
try:
    parse_cards('<main id="new-catalog"><article>Book</article></main>')
except ValueError as error:
    print("Layout change:", error)
''',
    "A cache saves requests, not time travel. Retain source/time/parser provenance, key by complete URLs and fail visibly on layout changes.",
    [("Does re-reading yesterday's cached HTML make it a fresh observation?", "No", "Yes", "Only after parsing", "Acquisition time is unchanged."),
     ("Should page=1 and page=2 share one cache key?", "No", "Yes", "Only for JSON", "Their queries may represent different documents.")])

PROJECT = clean(r'''
import argparse
from datetime import datetime
from decimal import Decimal
import json
from pathlib import Path
import re
import sys
from bs4 import BeautifulSoup

SOURCE = "own-practice-catalogue"

def validate_records(rows):
    if not isinstance(rows, list):
        raise ValueError("Records must be a list")
    by_id = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"id", "title", "currency", "cents"}:
            raise ValueError("Record schema mismatch")
        identity = row["id"]
        if not isinstance(identity, str) or re.fullmatch(r"[A-Z0-9-]{1,40}", identity) is None:
            raise ValueError("Invalid id")
        if not isinstance(row["title"], str) or not row["title"].strip() or len(row["title"]) > 180:
            raise ValueError("Invalid title")
        if row["currency"] != "USD" or type(row["cents"]) is not int or not 0 <= row["cents"] <= 100_000_000:
            raise ValueError("Invalid currency/amount")
        if identity in by_id and by_id[identity] != row:
            raise ValueError("Conflicting duplicate: " + identity)
        by_id[identity] = row
    return [by_id[key] for key in sorted(by_id)]

def parse_page(text, index, total):
    soup = BeautifulSoup(text, "html.parser")
    root = soup.select_one("#catalog")
    if root is None or root.get("data-page") != str(index) or root.get("data-pages") != str(total):
        raise ValueError("Missing or inconsistent page marker")
    cards = root.select("article.item")
    empty = root.get("data-empty") == "true"
    if empty == bool(cards):
        raise ValueError("Ambiguous empty-page state")
    records = []
    for card in cards:
        title, price = card.select_one("h2"), card.select_one(".price")
        if title is None or price is None:
            raise ValueError("Required card field missing")
        value = " ".join(price.get_text(" ", strip=True).split())
        if re.fullmatch(r"USD (?:[0-9]+|[0-9]{1,3}(?:,[0-9]{3})+)\.[0-9]{2}", value) is None or len(value) > 24:
            raise ValueError("Unsupported price text")
        cents = int(Decimal(value[4:].replace(",", "")) * 100)
        records.append({"id": card.get("data-id"), "title": title.get_text(" ", strip=True),
                        "currency": "USD", "cents": cents})
    return validate_records(records)

def collect(folder):
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or type(manifest.get("schema")) is not int or manifest["schema"] != 1:
        raise ValueError("Manifest schema mismatch")
    if manifest.get("source") != SOURCE or manifest.get("complete") is not True:
        raise ValueError("Unverified or incomplete fixture set")
    captured = manifest.get("captured_at")
    if not isinstance(captured, str) or datetime.fromisoformat(captured.replace("Z", "+00:00")).tzinfo is None:
        raise ValueError("Need a timezone-aware acquisition time")
    pages = manifest.get("pages")
    if not isinstance(pages, list) or not 1 <= len(pages) <= 10:
        raise ValueError("Need 1 to 10 pages")
    if any(not isinstance(name, str) or re.fullmatch(r"page[1-9][0-9]?\.html", name) is None for name in pages):
        raise ValueError("Invalid fixture filename")
    if len(set(pages)) != len(pages):
        raise ValueError("Duplicate page filename")
    rows = []
    for index, name in enumerate(pages, 1):
        path = folder / name
        if path.is_symlink():
            raise ValueError("Fixture must be a regular local copy")
        rows.extend(parse_page(path.read_text(encoding="utf-8"), index, len(pages)))
    return validate_records(rows), captured, pages

def read_state(path):
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or type(data.get("schema")) is not int or data["schema"] != 1 or data.get("source") != SOURCE:
        raise ValueError("Previous snapshot schema/source mismatch")
    return validate_records(data.get("records"))

def changes(previous, current):
    old, new = ({row["id"]: row for row in rows} for rows in (previous, current))
    report = []
    for identity in sorted(old.keys() | new.keys()):
        if identity not in old:
            report.append(("added", identity))
        elif identity not in new:
            report.append(("missing", identity))
        elif old[identity] != new[identity]:
            report.append(("changed", identity))
    return report

def main(argv=None):
    parser = argparse.ArgumentParser(description="Track complete owned local HTML fixture sets; no network.")
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("state", type=Path)
    args = parser.parse_args(argv)
    temporary = None
    try:
        if args.state.resolve() == (args.input_dir / "manifest.json").resolve() or args.state.suffix.lower() != ".json":
            raise ValueError("Use a separate .json snapshot filename")
        current, captured, pages = collect(args.input_dir)
        previous = read_state(args.state)
        report = changes(previous, current)
        state = {"schema": 1, "source": SOURCE, "captured_at": captured,
                 "parser_version": 1, "pages": pages, "records": current, "changes": report}
        args.state.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.state.with_name(args.state.name + ".tmp")
        # Exclusive creation avoids silently overwriting an unrelated temporary file.
        with temporary.open("x", encoding="utf-8") as stream:
            json.dump(state, stream, ensure_ascii=False, indent=2, allow_nan=False)
        temporary.replace(args.state)
    except (OSError, ValueError, TypeError, ArithmeticError) as error:
        print("FAILED:", error, file=sys.stderr)
        return 1
    print("Validated records:", len(current))
    print("Changes:", len(report))
    for kind, identity in report:
        print(kind + ":", identity)
    return 0
''')


def fixture_manifest(time):
    return {"schema": 1, "source": "own-practice-catalogue", "complete": True,
            "captured_at": time, "pages": ["page1.html", "page2.html"]}


def page_html(index, identity, title, price):
    return (f'<main id="catalog" data-page="{index}" data-pages="2">'
            f'<article class="item" data-id="{identity}"><h2>{title}</h2>'
            f'<span class="price">USD {price}</span></article></main>')


FIXTURES = {
    "run1": {"manifest.json": json.dumps(fixture_manifest("2026-10-12T12:00:00Z"), indent=2),
             "page1.html": page_html(1, "A", "Python book", "12.50"),
             "page2.html": page_html(2, "B", "Pen", "2.00")},
    "run2": {"manifest.json": json.dumps(fixture_manifest("2026-10-13T12:00:00Z"), indent=2),
             "page1.html": page_html(1, "A", "Python book", "10.00"),
             "page2.html": page_html(2, "C", "Notebook", "4.00")},
}

FIXTURE_SETUP = (
    "\nimport tempfile\n"
    + "fixtures = " + repr(FIXTURES) + "\n"
    + "def write_fixtures(root):\n"
    + "    for run, files in fixtures.items():\n"
    + "        folder = root / run\n"
    + "        folder.mkdir()\n"
    + "        for name, text in files.items():\n"
    + '            (folder / name).write_text(text, encoding="utf-8")\n'
)

add(5, "3. Complete project: a validated local price-change tracker",
    "Parse two-page snapshots, validate records, compare stable ids and preserve state on failure.",
    [("Acquisition adapter versus parser/state pipeline", "The project starts from owned saved HTML and a manifest. Remote acquisition is a separate adapter that must implement previous days' scope/policy/pacing/retry rules before handing over a verified complete set."),
     ("Manifest and page markers", "The authored fixture contract lists every page and its acquisition time. Each page declares its ordinal/total. These fixture assertions teach completeness checking; ordinary websites do not universally provide these markers."),
     ("Change report: added/changed/missing", "Compare stable ids and validated values. Missing means absent from this verified observation, not necessarily deleted from the real business."),
     ("Last-good snapshot; atomic commit", "Validate all pages and the previous state's schema before writing a new snapshot. A failed run returns a nonzero status and does not replace the previous valid snapshot.")],
    "Read this project in layers: validate_records checks domain data, parse_page checks HTML, collect checks the complete fixture set, changes compares observations, and main handles CLI plus saving. "
    "All library concepts already appeared this week or in Weeks 14/17/23. The complete code is deliberately longer than a toy scraper so the contracts are visible. "
    "Start with the two supplied run folders; the example creates them for you. There are no network calls, logins or secret credentials. "
    "Acquisition times are fixture facts in the manifest, not made-up 'now' values. A changed price/title produces changed; an absent id produces missing only after every declared page was successfully validated. "
    "Scheduling the project and adding notifications belong to Week 26. A remote adapter is an extension exercise, not an untested claim that this local project crawls arbitrary websites.",
    'local manifest/pages -> collect -> validate all records\nread and validate previous state -> compare ids\nserialize temporary -> atomically replace snapshot\nnonzero exit on failure',
    PROJECT + FIXTURE_SETUP + '''
with tempfile.TemporaryDirectory() as name:
    root = Path(name)
    write_fixtures(root)
    state = root / "snapshot.json"
    assert main([str(root / "run1"), str(state)]) == 0
    assert main([str(root / "run2"), str(state)]) == 0
    print("Saved IDs:", [row["id"] for row in read_state(state)])
''',
    "पहिलो run मा A/B added। दोस्रो run मा A price बदलेको छ, B नयाँ observation मा छैन, C थपियो। "
    "B लाई real business बाट permanently deleted भनेर घोषणा गरिएको छैन। सबै pages validation पछि मात्रै snapshot replace हुन्छ। "
    "Code लाई section अनुसार पढ; functions पहिले Week 9, error handling Week 14 र JSON/CLI Weeks 23–24 मा पढेका हौँ।",
    ('Parse whatever pages worked and replace snapshot', 'Require every declared page and every required field to validate before commit',
     "Partial acquisition or missing selectors can create false removal/change reports."),
    "Run the same verified fixture twice; demonstrate that the second run reports no changes.",
    PROJECT + FIXTURE_SETUP + '''
with tempfile.TemporaryDirectory() as name:
    root = Path(name)
    write_fixtures(root)
    state = root / "snapshot.json"
    assert main([str(root / "run1"), str(state)]) == 0
    assert main([str(root / "run1"), str(state)]) == 0
''',
    "Reject a boolean amount and conflicting observations before any save.",
    PROJECT + '''
for rows in [
    [{"id": "A", "title": "Book", "currency": "USD", "cents": True}],
    [{"id": "A", "title": "Book", "currency": "USD", "cents": 100},
     {"id": "A", "title": "Book", "currency": "USD", "cents": 200}],
]:
    try:
        validate_records(rows)
    except ValueError as error:
        print(error)
''',
    "Master each layer before adding live acquisition. Validate complete observations, keep exact money/identity/provenance, commit only after success and report missing rather than inventing deletion.",
    [("Does this project automatically crawl a remote website?", "No; it parses owned saved fixture sets", "Yes; every site", "Only protected pages", "Acquisition is a separate explicit adapter, not hidden inside the parser."),
     ("When may the new snapshot replace the old one?", "After the complete input and state validate", "After the first successful page", "After any timeout", "The old state must remain intact when acquisition/parsing fails.")])

add(5, "4. Whole-week retrieval and failure tests",
    "Prove normal and failed runs behave correctly, then explain every stage without a template.",
    [("Failure invariant", "An invariant is a rule that should hold across all supported paths. Here invalid/incomplete input must leave the prior snapshot byte-for-byte unchanged."),
     ("Fixture matrix", "Test normal, empty, malformed, missing-page, conflicting-id and layout-change inputs. Fixtures are meaningful when they target different failure causes, not just duplicate the happy path."),
     ("No-change versus no-observation", "A successful identical dataset yields no changes. A failed fetch yields no new observation; these are different outcomes even if both produce no change rows.")],
    "Before calling a scraper finished, test its failures. Can it confuse a login page with an empty catalogue? Can it lose a good snapshot because one page times out? "
    "This final part tests explicit empty-page markers, invalid fields and complete/incomplete manifest rules. "
    "Then answer the full-week questions without opening examples: explain transport, parsing, record identity, pacing, browser readiness, cache age and atomic state. "
    "For the larger project failure exercise, change one input at a time and verify both exit status and old snapshot bytes; the supplied project test file performs those checks. "
    "Return to weak parts rather than marking a day complete only because code ran once.",
    'assert valid input produces expected records\nassert invalid input raises/returns failure\nassert previous snapshot bytes stay unchanged\nassert repeated valid input produces no changes',
    PROJECT + '''
empty = '<main id="catalog" data-page="1" data-pages="1" data-empty="true"></main>'
print("Explicit empty:", parse_page(empty, 1, 1))
try:
    parse_page('<main id="catalog" data-page="1" data-pages="1"></main>', 1, 1)
except ValueError as error:
    print("Missing empty marker:", error)
''',
    "खाली result valid हुन explicit fixture marker चाहियो। खाली selectors मात्रै sufficient छैन। "
    "No-change valid run र failure एउटै होइनन्। बुझेर प्रश्नको कारण पनि बोल; answer memorize मात्र नगर।",
    ('No rows returned -> always mark the catalogue empty', 'Require an explicit validated empty/completion rule for this source',
     "Missing layout or incomplete loading can also produce zero matching rows."),
    "List six different rejection tests and implement one for a changed page marker.",
    PROJECT + '''
tests = ["missing field", "wrong page marker", "missing page file", "conflicting id", "incomplete manifest", "invalid old state"]
print("Test cases:", len(tests))
try:
    parse_page('<main id="catalog" data-page="2" data-pages="2" data-empty="true"></main>', 1, 2)
except ValueError as error:
    print(error)
''',
    "Verify one identical snapshot reports no changes, but an observed price/title change does.",
    PROJECT + '''
before = [{"id": "A", "title": "Book", "currency": "USD", "cents": 1250}]
after = [{"id": "A", "title": "Book", "currency": "USD", "cents": 1000}]
print("Identical:", changes(before, before))
print("Changed:", changes(before, after))
''',
    "Week 25 mastery: acquire deliberately, parse structurally, validate domain data, prove completeness, pace responsibly, classify errors, preserve provenance and protect last-good state.",
    [
        ("Does prepare send an HTTP request?", "No", "Yes", "Only for HTTPS", "It constructs a request object."),
        ("Does status 200 guarantee the intended listing?", "No", "Yes", "Only for HTML", "The expected structure still needs validation."),
        ("Does Requests execute page scripts?", "No", "Yes", "Only inline scripts", "A browser engine is a separate tool."),
        ("How should fields be selected?", "Within each record container", "From unrelated global lists", "By title length", "Record-local selection preserves association."),
        ("What does a still-present next link at the page limit mean?", "Incomplete crawl", "All pages read", "Valid empty listing", "The budget is a limit, not completion evidence."),
        ("Is a title always a stable unique id?", "No", "Yes", "Only for products", "Titles can collide or change."),
        ("Does robots Allow grant all access permissions?", "No", "Yes", "Only if cached", "It is crawl policy, not an authorization grant."),
        ("How should a too-long Retry-After be handled?", "Stop and resume later", "Retry earlier", "Discard the header", "Respect the minimum wait rather than shortening it."),
        ("Does count automatically wait for future browser items?", "No", "Yes", "Only when zero", "Use a defined readiness condition."),
        ("Does cached HTML become fresh when re-parsed?", "No", "Yes", "Only with a newer parser", "Acquisition time does not change."),
        ("What should failed acquisition do to prior state?", "Preserve it and report failure", "Replace it with zero rows", "Mark all records removed", "No new complete observation was obtained."),
        ("Is a missing listing definitely permanently deleted?", "No", "Yes", "Only if IDs were used", "Missing is an observation; business deletion needs more evidence."),
    ])

DAYS["25.0"]["parts"][0]["sections"].insert(3, s("sh",
    "python -m pip install requests beautifulsoup4",
    note="One-time installation in your practice environment. After setup, these examples use fixtures or a loopback server; the course page remains offline."))
DAYS["25.3"]["parts"][1]["sections"].insert(3, s("sh",
    "python -m pip install playwright\npython -m playwright install chromium",
    note="One-time browser setup needs internet. The supplied browser examples load authored local HTML with external requests aborted."))
DAYS["25.5"]["parts"][2]["sections"].append(s("sh",
    "python price_tracker.py sample-run1 snapshot.json\npython price_tracker.py sample-run2 snapshot.json\npython price_tracker.py --help",
    note="Use the complete project and the authored sample-run1/sample-run2 folders. Save them locally from the accompanying project files; they contain no remote acquisition. Scheduling comes in Week 26."))
DAYS["25.5"]["parts"][-1]["sections"].append(s("p",
    "Optional primary references: https://requests.readthedocs.io/en/latest/user/quickstart/ · https://requests.readthedocs.io/en/latest/user/advanced/#timeouts · "
    "https://www.crummy.com/software/BeautifulSoup/bs4/doc/ · https://docs.python.org/3/library/urllib.parse.html · https://docs.python.org/3/library/urllib.robotparser.html · "
    "https://playwright.dev/python/docs/library · https://playwright.dev/python/docs/locators · https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/429. "
    "The original explanations, complete authored fixtures, examples, outputs, practice and solutions are included in this course for offline study."))


def write():
    target = ROOT / "study-hub.html"
    original = target.read_bytes().decode("utf-8")
    start = original.index("const DAY_TEACH = {")
    end = original.index("\n};\n\nconst REST_DAY", start)
    if any(('"' + key + '":') in original[start:end] for key in DAYS):
        raise RuntimeError("Week 25 exists; refusing to overwrite.")
    addition = "\n".join(json.dumps(k) + ": " + json.dumps(v, ensure_ascii=False, indent=2) + "," for k, v in DAYS.items())
    # An HTML script end tag inside lesson-string fixtures must not close the app script.
    addition = addition.replace("</", "<\\/")
    prefix = original[:end].rstrip()
    if not prefix.endswith(","):
        prefix += ","
    result = prefix + "\n" + addition + original[end:]
    temporary = target.with_suffix(".html.tmp")
    temporary.write_bytes(result.encode("utf-8"))
    temporary.replace(target)
    project_root = ROOT / "docs" / "python-week25"
    project_root.mkdir(exist_ok=True)
    (project_root / "price_tracker.py").write_text(
        '"""Week 25 owned local HTML tracker. Python 3.11+; install beautifulsoup4. No network."""\n'
        + PROJECT + '\nif __name__ == "__main__":\n    sys.exit(main())\n', encoding="utf-8")
    for name, files in FIXTURES.items():
        folder = project_root / ("sample-" + name)
        folder.mkdir(exist_ok=True)
        for filename, text in files.items():
            (folder / filename).write_text(text, encoding="utf-8")
    parts = [part for day in DAYS.values() for part in day["parts"]]
    quizzes = sum(len(section["lesson"]["quiz"]) for part in parts for section in part["sections"] if section["t"] == "checkpoint")
    print(f"Added Week 25: 6 days, {len(parts)} parts, {len(parts)*2} practice prompts, {quizzes} questions, {EXECUTED} verified outputs.")


if __name__ == "__main__":
    write()
