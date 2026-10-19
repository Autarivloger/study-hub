# Week 9 — Python for security evidence

Original, standard-library-only teaching lab for Python 3.12+. It reuses the exact
fictional Week 7 JSON fixture. It does not inspect your computer, network,
accounts, browser storage or credentials. It sends no requests and changes no
source records. Use this small supplied dataset to learn evidence reasoning.

## Open the lab

Download the repository, then open PowerShell in `docs/cybersecurity-week9`.
Run each command separately:

```powershell
python --version
python -m unittest -v
python security_lab.py
```

The report prints to the terminal. There is no automatic output file. For lesson
snippets, create a separate `practice.py` **in this folder**, paste one complete
example, and run `python practice.py`. Do not name it `json.py`, `datetime.py`,
`hashlib.py` or `security_lab.py`, because that can hide a module you need.
There are no dependencies to install and no network requirement. The website
displays recorded output; it does not execute Python in the browser.

## What each helper does

- `load_fixture(path=SAMPLE)`: reads at most 100,001 bytes; accepts at most 1,000
  deliveries; rejects invalid document structure, non-finite numbers and repeated
  JSON keys. These are lab limits, not a full hostile-file processing service.
- `validate_rows(rows)`: checks required text fields, delivery labels and types
  used by this analysis. Returns accepted copies and row-numbered errors.
  Unknown extra metadata stays intact. Validation is not authenticity checking.
- `deduplicate(rows)`: key `(source, event_id)`; record/received_time/annotation
  are delivery metadata only under this prepared fixture's contract. Equal
  payload copies count once; conflicting groups are excluded and reported.
- `utc_time(value)` / `timeline(rows)`: offsets to UTC; missing/invalid offsets
  stay unknown. This does not establish actual clock accuracy.
- `login_window(rows,start,end)`: pass validated, deduplicated rows; count auth
  `login.failed` events in an explicit `[start,end)` interval. Unknown failure
  times are returned separately. It does not perform deduplication itself.
- `digest(path=SAMPLE)`: stream SHA-256 over bytes; use a separately trusted
  reference if authenticity/integrity against an earlier source is the question.
- `analyse(document)`: combines these helpers, retains caveats and reports review
  accounts at a toy threshold of three failures. It is not an intrusion verdict,
  a general SOC rule, or automatic containment/remediation.

The supplied fixture yields 12 deliveries, 11 unique events, 10 known-time events,
one unknown-time record and four unique failures in the stated three-minute
window. L04 repeats L03's source event. L12 arrives late. L11 lacks a timezone.
The earlier alert saw three failures; the later collection contains four.

## Independent exercise

Copy the fixture into a temporary practice folder and make one change at a time:
an extra identical delivery with a new record label; a conflicting copy; an
offset-free failure time; a new event exactly at the interval end. Predict both
counts and quality flags before running `python security_lab.py --input PATH`.
Never replace the reference fixture or record real passwords/tokens in notes.
The program does not follow event text as instructions or open URLs from it.

## Limits and references

The fixture and the analysis code are both public teaching material; a digest
stored beside them does not establish independent trust. A changed delivery
order can change which equal copy is retained; the event count remains the same.
Every deduplication decision requires the source's real event-identity contract.
Thresholds and account labels do not establish a human identity, attack intent,
compromise or absence of harm. Public sharing needs a separately reviewed,
minimal report; never publish raw real logs by analogy with this fake dataset.

- https://docs.python.org/3/library/json.html
- https://docs.python.org/3/library/datetime.html
- https://docs.python.org/3/library/hashlib.html
- https://docs.python.org/3/library/unittest.html
- https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
