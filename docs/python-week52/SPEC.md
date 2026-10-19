# StudyLog 1.0 specification

## User and problem

A single learner wants to record intentional study sessions, correct mistakes and
see totals without a hosted account. This is an independent teaching app using
synthetic fixtures. It never reads Study Hub progress, Gists, notes or credentials.

## Version-one boundary

- Add a real ISO date, nonblank subject, integer minutes 1..1440 and optional note.
- Trim subject boundaries; preserve note text. Subject max 80 characters; note max
  1000. Reject unknown fields, booleans/floats/strings as minute counts and NUL notes.
- List at most 100 rows, ordered by date descending and id descending, with offset
  pagination and an optional exact-date filter. The browser shows 10 at a time.
- Edit/delete an explicit session using its current version. A stale operation
  returns 409, a missing session 404. Refresh and review before retrying a conflict.
- Show count, total minutes and per-subject totals, optionally for one exact date.
- Keep records across server restarts. Back up through SQLite's backup API and
  rehearse opening the snapshot separately before relying on it.
- Provide a responsive keyboard-usable browser interface and a JSON API.

## Acceptance examples

Adding Python/25 and Japanese/15 gives two sessions and 40 minutes. Correcting the
first to 30 gives 45 total. Retrying its old version is rejected without changing
the corrected row. A process restart retains the result. A restored snapshot
contains the sessions it captured, even if later rows in the live database change.

## Non-goals and operating assumptions

This version is single-owner, not multiple accounts or per-user authorization.
It has no payments, cloud sync, AI recommendation, background scheduler or login
password database. Offset pages can shift during concurrent changes. A repeated
successful POST creates another record; the UI suppresses accidental double-clicks,
but the API does not promise exactly-once creation across network retries.

Default operation is localhost. A configured bearer token protects all data routes;
the browser keeps it only in page memory. Health and the empty UI shell are public.
Remote/public operation requires transport security, intentional access and proxy
configuration, persistent storage and tested operational controls described in
DEPLOYMENT.md. No external service is provisioned by this project.
