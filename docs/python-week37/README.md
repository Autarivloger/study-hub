# Python Week 37 — Flask: your first web application

Six teaching days, **32 parts**, **64 practice prompts**, **74 explained quiz
questions** and **96 executed examples/solutions**. Existing Day 7 Review &
rest, notes, completion, search and learned-only review/practice use the new
material through the current application.

All earlier teaching content and application/storage code remain unchanged.
This Flask dashboard is a separate local practice project, not a migration of
Study Hub into a Python server.

## Study sequence

1. **5 parts:** request-to-view cycle; bodies/status/headers; test client;
   request context; local development-server workflow.
2. **5 parts:** five meaningful routes/endpoints; path converters/existence;
   url_for; query strings/methods; redirects/error statuses.
3. **5 parts:** trusted templates/data; named HTML resources; loops/empty
   states; conditions/filters; escaping and context boundaries.
4. **5 parts:** base/child inheritance; shared navigation/includes; static
   CSS; responsive semantic UI; shared context and inherited error pages.
5. **6 parts:** GET search forms; POST fields/server validation; retained
   drafts/errors; Post/Redirect/Get; flash feedback; matching form tokens.
6. **6 parts:** signed-cookie sessions; preference/state scope; honest demo
   gate; leave/session isolation; complete app; end-to-end dashboard.

Explain the objective, predict outputs, run the example, solve both exercises,
then answer the quiz. Take as long as needed; never treat a part's calendar
label as a reason to skip practice.

## Run the local dashboard

Keep the complete folder structure:

    python-week37/
      app.py
      requirements.txt
      README.md
      templates/
        base.html
        home.html
        lessons.html
        detail.html
        enter.html
        planner.html
        settings.html
        about.html
        error.html
      static/
        style.css

From this folder:

    python -m pip install -r requirements.txt
    python app.py

Open **http://127.0.0.1:5000** on the same computer. Stop with Ctrl+C.
If port 5000 is already used:

    python -m flask --app app run --host 127.0.0.1 --port 5001

Then open http://127.0.0.1:5001. The built-in server is for local practice,
not an internet production deployment. Debug is off in the supplied entry
point. Do not name a practice script flask.py, which can shadow the package.

Verified with Python 3.12.14 and Flask 3.1.3.
Initial installation needs internet; all runtime assets and data are local,
with no CDN, web font, browser JavaScript or external API dependency.
Python executes locally, not inside the Study Hub HTML page.

**GitHub Pages does not execute Flask Python.** It continues serving the
offline course and source files. Download the project, then run Python.

### Using the examples

Most examples are complete snippets using Flask's in-process test client or
Jinja DictLoader. They do not open a port or need a previous snippet's state.
Test-request contexts teach selected context behaviours; they do not execute
the whole route pipeline.

From Day 5's token exercise onward, examples that import create_app require
the supplied app.py, templates/ and static/ alongside the snippet.
The long Day 6 app example embeds the actual Python implementation but still
uses the supplied HTML/CSS resources. Preserve their structure.
Author verification copies these public project resources into a fresh
temporary practice folder for each snippet.

## Browser practice

1. Open Home and note that the sample counter counts this session's home
   loads, including refreshes. It is not unique-user analytics.
2. Search Lessons for HTTP, open its detail page, and try an empty result.
3. Open Planner before entering; it redirects to the entry form.
4. Use a **fictional** display name such as Asha. No password is requested.
5. Add a short fictional practice note; inspect POST → 303 → GET in Network.
6. Try an invalid note and confirm feedback/no new note.
7. Change the local demo theme in Settings and refresh.
8. Leave the demo; a new direct Planner request redirects again.
9. Narrow the browser to a phone width, use keyboard Tab, and inspect labels,
   focus, the skip link, wrapping and the shared navigation.

This source project has more than five distinct routes: home, lesson list,
lesson detail, about, entry, planner, note creation/clear, settings and leave.
All main pages/error templates inherit the same base layout.

## State and honest boundaries

- The four lesson cards are fictional fixtures, not replacements for the
  Study Hub curriculum.
- The display-name gate is a **demo session flag**, not identity verification
  or a secure real account. No password, registration, database, individual
  ownership or full authorisation system is implemented this week.
- Notes are a bounded list of at most 20 entries, each 1–200 printable
  characters after outer whitespace trimming. They live in **server-process
  memory**, are shared by demo visitors in that process, and disappear when
  the app restarts. Use fictional text only.
- Display name, small theme preference and the incidental visit counter
  use Flask's default signed-cookie session. Cookie contents are **not
  encrypted**. Do not put passwords, API tokens or large documents there.
- The signing key is randomly generated per app instance/process; it is
  never read from a real existing credential. A restart changes it and old
  session cookies stop validating.
- Public fixed test keys in lesson snippets are for isolated tests only,
  not a reusable production secret.
- New app instances get independent note lists and keys. Two browser
  clients have independent cookie sessions but share a running app's notes.
- Leaving clears that current session, not all process notes. Clearing a
  browser cookie is not a complete server-side credential-revocation design.
- Week 38 handles fuller persistence/accounts/authorisation separately.
- Nothing here reads, moves, clears or syncs Study Hub notes, localStorage,
  progress, backup/import data or Gist credentials.

## Request and rendering rules

- Local GET search is read-only, bounded to 80 query characters and
  bookmarkable. Unknown detail ids return a helpful inherited 404 page.
- Form fields have labels/browser hints and matching server checks.
  Invalid forms return 400 with bounded escaped drafts and do not mutate
  approved state. Controls remain usable at 375px.
- Every state-changing project POST checks an unpredictable token matched
  to its signed-cookie session before view processing. Missing, cross-session,
  stale or malformed tokens fail before writes.
- The explicit token mechanism is a focused teaching scaffold, not a claim
  to cover every production form/security requirement. Do not disable it to
  make a test pass.
- Input display remains autoescaped through normal .html templates; no
  visitor notes are interpreted as template source or marked safe.
- Successful form writes use 303 redirects and short flash messages in the
  shared layout. PRG helps normal refresh navigation but does not provide
  exactly-once write semantics.
- Cookies use HttpOnly and SameSite=Lax. Secure=False is deliberate only
  because this demonstration uses loopback HTTP; actual HTTPS hosting needs
  an appropriate deployment/cookie configuration.
- Request bodies are capped at 16 KiB, with a useful 413 response. This is
  a local learning bound, not a full production resource policy.
- Error pages preserve 400/404/405/413 statuses. A valid method request with
  missing/invalid token may fail the token check before its view is reached.
- Local CSS is served through Flask's static endpoint. No remote assets
  or scripts are needed. Signed-cookie theme choices are allowlisted.

## Verification

All 96 lesson examples/solutions were executed with fresh globals and
temporary resources. Prior application code and every previous lesson are
compared with the baseline before adding Week 37.

Project tests cover route/method/resource contracts, field boundaries,
real token flow, unchanged state after invalid POST, stale/cross-session
tokens, Unicode token rejection, escaped names/notes/query drafts, PRG,
one-time flash feedback, cookie separation/tampering, bounded memory notes,
request limits, leave/restart behaviour and template/static resources.
Real local-browser checks cover the dashboard's full form/theme flow and
desktop/mobile rendering. Study Hub browser checks cover every part/quiz,
navigation, notes/progress/refresh, exact-part search, learned-only practice
and review, mobile dark/light modes and JavaScript errors. The existing
learning smoke test verifies actual JSON backup/import merge and replace.

## Primary references

Original explanations, examples, exercises, templates, design and fictional
fixtures were checked against these optional references:

- [Flask quickstart](https://flask.palletsprojects.com/en/stable/quickstart/)
- [Flask testing](https://flask.palletsprojects.com/en/stable/testing/)
- [Flask template tutorial](https://flask.palletsprojects.com/en/stable/tutorial/templates/)
- [Flask security considerations](https://flask.palletsprojects.com/en/stable/web-security/)
- [Jinja template reference](https://jinja.palletsprojects.com/en/stable/templates/)
