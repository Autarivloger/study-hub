# Python Week 36 — HTTP, APIs & consuming web services

Six teaching days, **32 parts**, **64 practice prompts**, **74 explained quiz
questions** and **96 executed examples/solutions**. Existing Day 7 Review &
rest, notes, completion, search, learned-only practice and spaced review
collect the new material through the current application.

All earlier lessons, application functions and browser storage remain
unchanged. This is a separate local Python practice project.

## Study order

1. **5 parts:** client/server cycle; URL/DNS/HTTPS; method semantics;
   status/headers/body; browser Network and prepared-request inspection.
2. **6 parts:** GET params; POST JSON; PUT/DELETE/204; sessions; stage timeouts;
   bounded streaming and response closure.
3. **5 parts:** authentication versus authorisation; bearer origin/header;
   runtime environment; ignored local .env; real provider documentation.
4. **6 parts:** status-specific decisions; JSON/schema checks; bounded GET
   retries; backoff/jitter/Retry-After; rates and uncertain writes; fault drills.
5. **5 parts:** page/cursor contracts; complete continuation; metadata/row/item
   bounds; duplicate IDs and remote drift; reconciled SQLite evidence.
6. **5 parts:** typed client interface; separated responsibilities; complete
   resilient client; atomic report publication; end-to-end milestone.

Predict before running. Explain each output, solve the two exercises without
opening solutions, then use the quiz. Spread a part over more than one sitting
when needed; the calendar is not a reason to skip a concept.

## First setup — keep these files together

Download mock_api.py, api_client.py, collector.py, requirements.txt,
.gitignore, .env.example and this README into one new practice folder.
The snippets importing mock_api/APIClient rely on these explicitly supplied
support modules. They do not rely on a previous snippet's state.

    python -m pip install -r requirements.txt
    python collector.py api-run-01

Initial installation needs internet. Afterward the default fixture and
collection run entirely locally; all lesson text/code/recorded outputs also
remain embedded in study-hub.html for offline reading.

Verified environment: Python 3.12.14, Requests 2.34.2, python-dotenv 1.2.4.
Python executes in your terminal, not inside the website. No real credential
was read or used during authoring or automated tests.

The default command publishes:

    items.json
    items.csv
    collection.sqlite
    summary.json
    manifest.json
    report.md

Choose api-run-02 for another run. An existing destination is refused before
collection. Failed collection/validation/export publishes no partial bundle
and preserves earlier runs.

### Fixture facts

All source records, tasks and credentials are fictional. Default mode
starts a fresh API bound only to numeric loopback 127.0.0.1 on a free port.
practice-only-token is a public fake value that works only on this fixture.
It is not a usable GitHub token.

- Six records in three pages of two.
- IDs 1–6; 5 issue records and 1 pull-request record.
- Four open records and two closed records.
- 18 recorded comments across all six; 17 on issues and 1 on the PR.
- Kind/state groups: issues closed 2/8 comments, issues open 3/9 comments,
  pull requests open 1/1 comment.

The report's mixed total must not be labelled an issue-only count.
The SQLite table stores only id, title, state, comments and kind.
It contains no token, request header or personal browser progress.

### Inspect the local API in a browser

    python mock_api.py

It prints a loopback URL; append /health, open it in a browser, open Developer
Tools → Network and reload. Inspect method, path, status and response.
Stop the helper with Ctrl+C. Snippets instead use DemoAPI as a context
manager, which starts and closes a fresh server automatically.

Local drills include GET, POST, PUT and DELETE. Write methods affect only
temporary fictional tasks and never write to GitHub.

## Failure drills

    python collector.py api-run-incomplete --max-pages 2

This intentionally fails: the fixture requires three pages. No incomplete
four-record report should be published. A cap is a failure guard, not a
replacement for the provider's terminal signal.

Other controlled routes include /bad-json, /wrong-shape, /redirect,
/unavailable, /flaky, /rate and /slow. They demonstrate representation errors,
unexpected shapes, redirects, bounded retries, server waits and read timeouts.

## Optional authenticated public GitHub collection

This is explicitly opt-in and requires internet. Do it only after reading
the provider documentation and understanding the local drill.

1. Choose a public repository and inspect the documented endpoint/permissions.
   The collector makes read-only GET requests, not issue creation or updates.
2. Supply STUDYHUB_API_TOKEN locally through the process environment, or make
   a local .env beside collector.py from the blank .env.example template.
   Never put the real value in a public file, screenshot, report or chat.
3. Keep the supplied .gitignore in this folder before adding a real .env.
   Existing process configuration wins over .env because override=False.
4. Run with an actual owner/repository in place of OWNER/REPO:

       python collector.py api-live-01 --github OWNER/REPO --max-pages 10

5. Read the manifest and report; verify the declared population and limits.

Public GitHub data can also be read without authentication under different
rate limits; this optional mode deliberately requires a locally configured
credential for the authenticated-client exercise. Use the permissions
documented for the chosen public read endpoint and avoid unnecessary writes.
The authoring/tests do not use your real account or authenticate against it.

The live endpoint is /repos/{owner}/{repo}/issues with state=all,
sort=created, direction=asc, per_page=100. It can return both issue and PR
records. A pull_request field identifies the latter; classification is
preserved. The provider id is used as the local key.

Next links are checked for exact HTTPS origin, endpoint and unchanged fixed
filters plus the next page. The client reconstructs the approved request;
it never blindly forwards the bearer session to an arbitrary next URL.
Changed/unsupported link structure stops for review.

The default 10-page bound may not fit a large repository. Exceeding a page
or item bound fails without publishing a partial result. Review the scope
and use an appropriate bounded run; do not label a prefix as complete.

## Client policies and limits

- Fixed approved origin: exact https://api.github.com or the numeric local
  fixture origin. No arbitrary external authenticated destination.
- HTTPS certificate verification remains on for real network traffic.
  No verify=False workaround.
- Sessions use trust_env=False to avoid ambient .netrc/proxy discovery in
  this scoped teaching tool. Configure corporate proxies/trust explicitly
  if needed; do not disable verification.
- GET only in the resilient collector. Write drills are separate and local.
  A timed-out POST may already have succeeded; no blind write retries.
- Explicit connect/read timeout tuple. This is **not a total download or
  whole-workflow deadline**.
- At most 1–5 total attempts. Selected transient GET statuses and scoped
  network failures may retry; TLS failures,401, ordinary403,404, redirects,
  malformed JSON and schema errors stop.
- Retry-After seconds/HTTP dates are respected. If a required wait exceeds
  the remaining accumulated wait budget, stop rather than retry early.
  Unknown/malformed wait hints stop for review.
- GitHub rate403with an exhausted/reset hint is handled separately from
  ordinary forbidden access. Retry hints and documented response headers
  take precedence over guessed fixed quotas.
- Exponential fallback plus bounded jitter; no unnecessary sleep after the
  final attempt. The maximum wait budget is accumulated sleep, not all
  network/processing time.
- Declared page/item bounds, required envelopes, validated field types and
  duplicate cursor/id refusal. No silent schema coercion or deduplication.
- JSON parsing does **not** enforce a strict response-byte bound. A lesson
  separately demonstrates bounded streamed-body reading for a larger client.
- Completion means reaching the requested continuation endpoint, **not a
  transactionally frozen remote census**. Remote pages may change and unique
  returned ids do not prove no missing records.

## Storage and evidence

Finish collection and validation before publication. Bound SQL inserts and a
transaction create the local database. All outputs are staged in a newly
owned temporary folder beside the destination and published by rename only
after successful writes. Existing destinations are refused.

The manifest records provider, optional repository, UTC retrieval time,
scope and a SHA-256 fingerprint of the saved selected-field JSON. The hash
checks saved bytes; it does not establish provider accuracy.

Only approved item fields are stored; no raw auth/error headers, token,
author identity or full raw HTTP response is exported. Comment totals refer
to the endpoint's field, not all possible discussion/review activity.
CSV preserves approved titles as text data; import the title column as text
in a spreadsheet so formula-like external text is not executed.

SQLite here is local practice storage. It does not encrypt Study Hub secrets,
sync your learning progress or replace the site's JSON backup/import.

## Primary references

Original explanations, exercises and fictional data were checked against
these optional primary references. The documents are not runtime dependencies.

- [Requests quickstart](https://requests.readthedocs.io/en/latest/user/quickstart/)
- [Requests advanced usage](https://requests.readthedocs.io/en/latest/user/advanced/)
- [HTTP methods](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods)
- [Retry-After](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Retry-After)
- [GitHub repository issues endpoint](https://docs.github.com/en/rest/issues/issues#list-repository-issues)
- [GitHub pagination](https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api)
- [GitHub rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api)
- [GitHub API best practices](https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api)

## Verification

All 96 examples/solutions execute against fresh supplied fictional fixtures.
Dependency files are copied into an isolated temporary practice folder for
each snippet. Network practice uses loopback only.
Acceptance tests cover real local methods, malformed/empty representations,
retry budgets/hints, auth failure, duplicate/cyclic/incomplete pages, validated
provider next links using synthetic responses, sanitised failures, complete
SQLite reports, JSON hash, refusal to overwrite and export cleanup.
Browser tests cover every new part/quiz, navigation, search, notes/progress,
learned-only practice/review, mobile themes and console errors.
The existing learning smoke suite verifies JSON backup/import merge/replace.
