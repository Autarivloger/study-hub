# Cybersecurity Week 5 — Web and application security foundations

Seven English lessons,36 reasoned self-checks, first-use explanations and a
fictional offline request lab. Existing Study Hub notes, navigation and answer
reveal are reused; all prior lessons and application/storage code stay intact.

## Study order

1. HTTP request/response: methods, routes, statuses, headers, cookies, sessions,
   expected application result and Python's role in approved observation tables.
2. Application boundaries: frontend/backend/API/database, trusted identity,
   bounded field contracts, format/business validation and output contexts.
3. Authorisation: owner/resource/action checks, deny-by-default, least privilege,
   ID-reference limitations and positive/negative access matrices.
4. Database interpretation: fixed query structure, supported value binding,
   legitimate punctuation, structural allowlists, database privilege/failures
   and Python's role in repeatable defensive checks.
5. Browser risks: XSS versus CSRF, suitable plain-text output, intent evidence,
   SameSite/HttpOnly/CORS limitations and an original plain-English orientation
   to OWASP Top10:2025 category IDs.
6. Local lab: predict/inspect allowed owner reads/edits, guest/non-owner denial,
   unknown records, invalid intent/input, unchanged denied writes and literal
   text handling. Distinguish the simulator from actual server mechanisms.
7. Review: a complete save-note journey, alternate failures, fixture/expected
   state, six-case test pack and twelve closed-notes retrieval questions.

## Open the local request lab

Use the **Local request lab** reference link in Week5 Day6 or Day7. It opens
request-lab.html alongside the published site. For offline use, download the
project folder and double-click request-lab.html in this directory. Downloading
only study-hub.html does not include the separate companion file; the full
lesson explanations and scenarios are still embedded in that main file.

The companion page has no dependencies, installation, backend or network calls.
All users/credentials are fictional. It uses only in-memory notes and resets
them on reload or Reset lab. It does not access Study Hub's storage or progress.

Model policy:

- Maya ownsN1; Ravi ownsN2. Guest has no authenticated model session.
- Authenticated owners may read/edit their own record; unknown IDs return404.
- Edits require the selected valid pretend intent evidence and app origin.
- Text must be nonblank and at most200 Unicode code points.
- Refused operations preserve both notes; allowed edits change only the target.
- Values stay plain text. No SQL or arbitrary HTML is executed.
- A trace names the first failed condition; model HTTP-like status codes do not
  represent network responses. A real application may choose different error
  disclosure/order while still enforcing all required boundaries.

The model is not a secure login/database implementation. Its public selectors
and pretend evidence explain decisions; real sessions and CSRF tokens require
maintained backend/framework mechanisms. The lab is deliberately not vulnerable
and does not exercise real users' resources or external services.

## Sources

- [MDN HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview)
- [MDN status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status)
- [MDN cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies)
- [OWASP input validation](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [OWASP authorisation](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- [OWASP SQL-injection prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [Python parameter binding](https://docs.python.org/3/library/sqlite3.html)
- [OWASP XSS prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP CSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [MDN CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS)
- [MDN textContent](https://developer.mozilla.org/en-US/docs/Web/API/Node/textContent)
- [OWASP Top10:2025](https://top10.owasp.org/2025/)

Explanations, scenarios, questions and the lab are original. Category IDs are a
learning map, not an exhaustive security test. The new lesson material remains
cybersecurity reasoning; Python's supporting role is explained without adding
Python coding worksheets.

## Verification

Static checks compare the28 earlier cybersecurity lessons and every byte of
application/storage/other-course code outside the teaching map with773dacc.
Isolated browser tests use fictional data for all seven lesson views,36 answer
show/hide checks, notes saving/hiding/refresh, previous/next week boundaries,
old quizzes and375px mobile themes. The companion page is tested through its
actual controls for allowed/denied reads/writes, stopping stage, unchanged
refused data, Unicode limits, literal markup, reset/reload and both themes.
Existing backup/import merge/replace tests verify retained progress using
fictional browser data. No real credential or personal browser profile is read.
