# Python Week 35 — Databases & SQL with Python

Six days, **32 parts**, **64 practice prompts**, **74 explained quiz questions**
and **96 executed examples/solutions**. Day 7 uses the existing Review & rest
system. The website embeds all lesson text, code and recorded outputs for
offline reading. No application function, existing lesson, progress identifier,
localStorage schema, backup or sync mechanism is changed.

## Study order

1. **5 parts:** database/SQL/Python roles; copy identity and keys; relationships
   and foreign-key enforcement; normalisation; executable constraints.
2. **5 parts:** SELECT/WHERE; grouped predicates, IN/BETWEEN/LIKE; NULL/counts;
   DISTINCT/order/ties/limits; logical reasoning and computed expressions.
   Includes ten numbered query questions.
3. **6 parts:** INNER JOIN and multiplicity; LEFT JOIN and zero-event parents;
   RIGHT JOIN with a portable rewrite; grouping/HAVING; subqueries/EXISTS;
   three-table reports and denominator reconciliation.
4. **5 parts:** cursors/resources; value binding and controlled identifiers;
   literal search/input/errors; file modes and persistence; verified backups.
5. **5 parts:** focused pandas SQL reads; nullable dtypes/group semantics;
   safe staging exports and to_sql limitations; SQL/pandas result parity;
   repeated scoped timing and correct chunk aggregation.
6. **6 parts:** targeted CRUD; atomic transactions/rollback; performance and
   partial unique indexes; versioned migrations; bounded atomic CSV import;
   full library milestone with a recovery drill.

Do not rush a part. Predict each output, explain it, run the example, solve
both exercises without revealing solutions, then answer its quiz. Mark a part
complete only after you can explain it. Use the existing heading/day notes
and next/previous controls.

## Local environment

The library CLI uses Python's standard library, including sqlite3.
Python runs in your terminal, not inside the website.

Day 5 and analysis.py additionally use pandas:

    python -m pip install "pandas>=3,<4"

Initial installation requires internet; practice then works offline.
Verified with Python 3.12.14, SQLite 3.53.1 and pandas 3.0.1.
RIGHT JOIN needs SQLite 3.39 or later; its lesson includes a LEFT JOIN rewrite.
Timing values and query-plan wording reflect one verified authoring run and
can differ on another machine. No universal speedup is promised.

Examples use isolated in-memory databases or owned temporary directories.
Temporary data disappears on close/cleanup. Use a stable folder for your own
long-term practice project and create verified backups before migrations.

## Run the full milestone

Download and keep library_db.py, analysis.py, books-import.csv and this README
together. In that folder, run the following in order. These are example dates,
not the computer's current date.

    python library_db.py library.db init
    python library_db.py library.db report
    python library_db.py library.db import-books books-import.csv
    python library_db.py library.db borrow 3 4 2026-01-11
    python library_db.py library.db return 5 2026-01-12
    python library_db.py library.db rename 4 "Quiet Reading — revised"
    python library_db.py library.db backup library-backup-01.db
    python analysis.py library.db
    python library_db.py library.db --help

Use a new database filename for another init, and a new backup filename for
each backup. init refuses any existing file; normal opens use mode=rw or
mode=ro and cannot create a typo database. The supplied CSV is insert-only:
reimporting the same IDs fails rather than replacing existing records.

To inspect a backup without changing it:

    python library_db.py library-backup-01.db report

### Fictional data and expected reconciliation

All records and names in this project were invented for learning. No external
dataset, personal records or credentials are included.

- Initial catalogue: 4 copies, 4 members and 4 historical events.
- Open events: 2 (loan IDs 2 and 3).
- Member event/open counts: Asha 2/1, Ben 1/1, Chandra 1/0, Dipa 0/0.
- Initial catalogue page total: 840.
- Page total over loan-event matches: 900. This is a different unit, since
  copy 1 appears twice and unborrowed copy 4 is absent.
- After importing: 6 copies, still 4 events.
- After borrow and return above: 5 historical events, still 2 open events.
  Dipa has 1 event, 0 open.
- SQL and pandas reports preserve all members, including zero-event members.

### Entity model

    books.id   <--- loans.book_id
    members.id <--- loans.member_id

One books row is one physical copy. Duplicate titles can represent separate
copies. One loans row is one historical event. Members keep current names.
author is a display label, not a complete author/edition identity model.

## Boundaries and transaction policy

- Each connection enables and verifies foreign keys before transactions.
- The examples/project explicitly use isolation_level=None with Python's
  legacy transaction-control mode. They issue BEGIN IMMEDIATE/COMMIT/ROLLBACK
  for grouped writes. Do not silently mix this with autocommit=False or
  another implicit transaction policy.
- COMMIT is inside the protected operation; failure rolls back any remaining
  active transaction. The helper rejects nested BEGIN usage.
- All supplied values are bound. Table/sort identifiers are fixed or chosen
  from a trusted allowlist; placeholders cannot bind identifiers.
- Current open loans are unique per copy using a partial UNIQUE index.
- Book/member foreign keys preserve historical references. Required values,
  integer page storage and broad input bounds have declared constraints.
- Interface dates are real YYYY-MM-DD calendar dates. Return-before-borrow
  is rejected. Returned events remain history; repeat returns fail clearly.
- This teaching model does not validate all historical interval overlap,
  multiple editions/authors, authentication or production multi-user policy.
- A plain SQLite file is not encrypted storage, a password vault, a hosted
  API, access control or automatic cross-device sync.
- It never accesses Study Hub's localStorage, saved progress, Gist token,
  passwords, personal notes or production database.

## Atomic CSV contract

UTF-8/UTF-8 BOM; exact header id,title,author,pages; 1–10000 records; at most
1 MiB; no ragged/blank records. IDs are positive ASCII decimal SQLite-range
integers; pages are ASCII decimal integers from 1 to 10000. Duplicate incoming
IDs and collisions with stored IDs fail. Titles contain 1–200 characters and
authors 1–120, with nonempty stripped content; accepted text is preserved
without silent normalisation. Input bytes are not rewritten.

Validate the bounded file before writes; use executemany in one transaction.
A collision after an earlier attempted insert rolls the entire batch back.
No automatic deduplication, overwrite, pandas replace or partial success.
The compact inline CSV example demonstrates the transaction mechanism;
the downloadable parser implements this complete contract.

## Migrations and backups

Version 1 creates the known schema. Version 2 adds a non-NULL empty-default
loan note and a composite member/date index. Existing rows and keys survive.
The migration inspects the expected loans column shape, refuses unknown
versions and changes schema/version together with individual execute calls.
user_version alone is not proof an arbitrary file has our schema.

New initialisation applies both versions automatically. For an owned earlier
version-1 practice file, create/verify a new backup before:

    python library_db.py older-library.db migrate

Repeated version-2 migration is a deliberate no-op. Failed migration rolls
back changes. Do not drop/recreate a table to add a field.
Connection.backup creates a new database copy; existing backup destinations
are refused. Verify a restore query, not just that the file exists.
This database backup is separate from the website's JSON backup/import.

## Primary references

These were consulted to check APIs and SQL behaviour. Lesson explanations,
exercises and fictional fixtures are original; remote documents are optional
further reading rather than offline runtime dependencies.

- [Python sqlite3](https://docs.python.org/3/library/sqlite3.html)
- [SQLite SELECT](https://www.sqlite.org/lang_select.html)
- [Foreign keys](https://www.sqlite.org/foreignkeys.html)
- [Transactions](https://www.sqlite.org/lang_transaction.html)
- [Indexes](https://www.sqlite.org/lang_createindex.html)
- [ALTER TABLE](https://www.sqlite.org/lang_altertable.html)
- [PRAGMA user_version](https://www.sqlite.org/pragma.html#pragma_user_version)
- [pandas read_sql_query](https://pandas.pydata.org/docs/reference/api/pandas.read_sql_query.html)
- [pandas to_sql](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html)

## Author verification

All 96 snippets execute with fresh globals and temporary practice folders.
The project acceptance suite checks initial and changed reports, exact row
retention after failures, bound hostile-looking values, import atomicity,
foreign/unique/check rules, migrations, backups, CLI commands, missing-path
refusal and SQL/pandas parity. Browser checks cover every part/quiz, existing
navigation, saved notes/progress, exact-part search, learned-only practice,
review eligibility, 375px dark/light layouts and JavaScript errors. The
existing learning smoke test checks JSON backup/import merge and replace.
