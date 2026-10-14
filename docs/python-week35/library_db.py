"""Week 35: an offline library with explicit SQL, transactions and migrations.

This standalone teaching project never reads Study Hub's browser storage.
"""
import argparse
from contextlib import contextmanager, closing
import csv
from datetime import date
import io
import json
from pathlib import Path
import sqlite3
import sys

VERSION = 2
SCHEMA = (
    """CREATE TABLE books(
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL CHECK(length(trim(title)) BETWEEN 1 AND 200),
        author TEXT NOT NULL CHECK(length(trim(author)) BETWEEN 1 AND 120),
        pages INTEGER NOT NULL CHECK(typeof(pages)='integer' AND pages BETWEEN 1 AND 10000))""",
    """CREATE TABLE members(
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL CHECK(length(trim(name)) BETWEEN 1 AND 120))""",
    """CREATE TABLE loans(
        id INTEGER PRIMARY KEY,
        book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE RESTRICT,
        member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE RESTRICT,
        borrowed_on TEXT NOT NULL,
        returned_on TEXT,
        CHECK(returned_on IS NULL OR returned_on >= borrowed_on))""",
    "CREATE UNIQUE INDEX one_open_loan ON loans(book_id) WHERE returned_on IS NULL",
)
BOOKS = [(1, "Python Steps", "Mira", 180), (2, "Data Stories", "Ken", 240),
         (3, "SQL Garden", "Mira", 300), (4, "Quiet Reading", "Aya", 120)]
MEMBERS = [(1, "Asha"), (2, "Ben"), (3, "Chandra"), (4, "Dipa")]
LOANS = [(1, 1, 1, "2026-01-01", "2026-01-05"),
         (2, 1, 2, "2026-01-06", None),
         (3, 2, 1, "2026-01-07", None),
         (4, 3, 3, "2026-01-08", "2026-01-10")]
CSV_HEADER = ["id", "title", "author", "pages"]


@contextmanager
def transaction(con):
    """One explicit transaction; a failed COMMIT also triggers rollback."""
    if con.in_transaction:
        raise ValueError("Nested transactions require a separate savepoint design")
    con.execute("BEGIN IMMEDIATE")
    try:
        yield
        con.execute("COMMIT")
    except BaseException:
        if con.in_transaction:
            con.execute("ROLLBACK")
        raise


def connect(path, *, readonly=False):
    """Open an existing file, never accidentally create one on a typo."""
    path = Path(path).resolve()
    con = sqlite3.connect(path.as_uri() + ("?mode=ro" if readonly else "?mode=rw"),
                          uri=True, isolation_level=None, timeout=5)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    if con.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
        con.close()
        raise RuntimeError("Foreign-key enforcement unavailable")
    return con


def require_version(con, version=VERSION):
    if con.execute("PRAGMA user_version").fetchone()[0] != version:
        raise ValueError("Unexpected schema version; inspect and migrate the owned teaching DB")


def migrate(con):
    """Known version 1 -> 2; keep old tables/rows; never drop/recreate them."""
    version = con.execute("PRAGMA user_version").fetchone()[0]
    if version == VERSION:
        return False
    if version != 1:
        raise ValueError("Only the documented version-1 library schema can migrate")
    # user_version is our marker, not proof that an arbitrary file has our schema.
    columns = [row[1] for row in con.execute("PRAGMA table_info(loans)")]
    if columns != ["id", "book_id", "member_id", "borrowed_on", "returned_on"]:
        raise ValueError("Version marker does not match the expected loans schema")
    with transaction(con):
        con.execute("ALTER TABLE loans ADD COLUMN note TEXT NOT NULL DEFAULT ''")
        con.execute("CREATE INDEX loans_member_date ON loans(member_id, borrowed_on)")
        con.execute("PRAGMA user_version=2")
    return True


def initialise(path):
    """Reserve a new local file exclusively; never replace an existing file."""
    path = Path(path)
    with path.open("xb"):
        pass
    try:
        with closing(connect(path)) as con:
            with transaction(con):
                for statement in SCHEMA:
                    con.execute(statement)
                con.executemany("INSERT INTO books(id,title,author,pages) VALUES(?,?,?,?)", BOOKS)
                con.executemany("INSERT INTO members(id,name) VALUES(?,?)", MEMBERS)
                con.executemany("INSERT INTO loans(id,book_id,member_id,borrowed_on,returned_on) VALUES(?,?,?,?,?)", LOANS)
                con.execute("PRAGMA user_version=1")
            migrate(con)
    except BaseException:
        # Only the file just exclusively created by this call is ours to remove.
        path.unlink(missing_ok=True)
        raise


def iso_day(value):
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError("Use a real calendar date in YYYY-MM-DD form")
    return value


def positive_id(value):
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 2**63 - 1:
        raise ValueError("Require a positive SQLite integer ID")
    return value


def borrow(con, book_id, member_id, when):
    require_version(con)
    book_id, member_id = positive_id(book_id), positive_id(member_id)
    when = iso_day(when)
    with transaction(con):
        # The partial UNIQUE index arbitrates competing active checkouts.
        cursor = con.execute("INSERT INTO loans(book_id,member_id,borrowed_on) VALUES(?,?,?)",
                             (book_id, member_id, when))
        result = cursor.lastrowid
    return result


def return_book(con, loan_id, when):
    require_version(con)
    loan_id, when = positive_id(loan_id), iso_day(when)
    with transaction(con):
        cursor = con.execute("UPDATE loans SET returned_on=? WHERE id=? AND returned_on IS NULL",
                             (when, loan_id))
        if cursor.rowcount != 1:
            raise ValueError("No open loan with that ID")


def rename_book(con, book_id, title):
    require_version(con)
    book_id = positive_id(book_id)
    title = title.strip()
    if not 1 <= len(title) <= 200:
        raise ValueError("Title must contain 1–200 characters")
    with transaction(con):
        if con.execute("UPDATE books SET title=? WHERE id=?", (title, book_id)).rowcount != 1:
            raise ValueError("Unknown book ID")


def parse_books_csv(blob):
    if len(blob) > 1024 * 1024:
        raise ValueError("Teaching CSV limit is 1 MiB")
    rows = list(csv.reader(io.StringIO(blob.decode("utf-8-sig"), newline=""), strict=True))
    if not rows or rows[0] != CSV_HEADER or not 1 <= len(rows) - 1 <= 10000:
        raise ValueError("Require id,title,author,pages and 1–10000 records")
    result, seen = [], set()
    for position, row in enumerate(rows[1:], 2):
        if len(row) != 4:
            raise ValueError(f"CSV record {position}: wrong width")
        raw_id, title, author, raw_pages = row
        if not raw_id.isascii() or not raw_id.isdecimal() or not raw_pages.isascii() or not raw_pages.isdecimal():
            raise ValueError(f"CSV record {position}: IDs/pages must be ASCII integers")
        book_id, pages = int(raw_id), int(raw_pages)
        positive_id(book_id)
        if book_id in seen or not 1 <= pages <= 10000:
            raise ValueError(f"CSV record {position}: duplicate ID or invalid pages")
        # Do not silently rewrite the user's title/author tokens during import.
        if not 1 <= len(title.strip()) <= 200 or len(title) > 200 or not 1 <= len(author.strip()) <= 120 or len(author) > 120:
            raise ValueError(f"CSV record {position}: invalid title/author")
        seen.add(book_id)
        result.append((book_id, title, author, pages))
    return result


def import_books(con, source):
    require_version(con)
    with Path(source).open("rb") as handle:
        blob = handle.read(1024 * 1024 + 1)
    rows = parse_books_csv(blob)
    with transaction(con):
        con.executemany("INSERT INTO books(id,title,author,pages) VALUES(?,?,?,?)", rows)
    return len(rows)


REPORT_SQL = """SELECT m.id,m.name,COUNT(l.id) AS loan_count,
    SUM(CASE WHEN l.id IS NOT NULL AND l.returned_on IS NULL THEN 1 ELSE 0 END) AS open_count
    FROM members AS m LEFT JOIN loans AS l ON l.member_id=m.id
    GROUP BY m.id,m.name ORDER BY m.id"""
HISTORY_SQL = """SELECT l.id,b.title,m.name,l.borrowed_on,l.returned_on
    FROM loans AS l JOIN books AS b ON b.id=l.book_id
    JOIN members AS m ON m.id=l.member_id ORDER BY l.id"""


def report(con):
    require_version(con)
    return {"schema_version": VERSION,
            "books": con.execute("SELECT COUNT(*) FROM books").fetchone()[0],
            "loans": con.execute("SELECT COUNT(*) FROM loans").fetchone()[0],
            "members": [dict(row) for row in con.execute(REPORT_SQL)],
            "history": [dict(row) for row in con.execute(HISTORY_SQL)]}


def backup(con, destination):
    destination = Path(destination)
    with destination.open("xb"):
        pass
    try:
        with closing(sqlite3.connect(destination, isolation_level=None)) as target:
            con.backup(target)
    except BaseException:
        destination.unlink(missing_ok=True)
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description="Week35 offline library; practice DB only")
    parser.add_argument("database", type=Path)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="create a NEW database with fictional demo data")
    sub.add_parser("report")
    sub.add_parser("migrate")
    p = sub.add_parser("borrow"); p.add_argument("book", type=int); p.add_argument("member", type=int); p.add_argument("day")
    p = sub.add_parser("return"); p.add_argument("loan", type=int); p.add_argument("day")
    p = sub.add_parser("rename"); p.add_argument("book", type=int); p.add_argument("title")
    p = sub.add_parser("import-books"); p.add_argument("csv", type=Path)
    p = sub.add_parser("backup"); p.add_argument("destination", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            initialise(args.database)
            print("Created fictional library: 4 books, 4 members, 4 loans; schema 2")
        else:
            with closing(connect(args.database, readonly=args.command in {"report", "backup"})) as con:
                if args.command == "report":
                    print(json.dumps(report(con), indent=2, ensure_ascii=False))
                elif args.command == "migrate":
                    print("Migrated" if migrate(con) else "Already at schema 2")
                elif args.command == "borrow":
                    print("New loan:", borrow(con, args.book, args.member, args.day))
                elif args.command == "return":
                    return_book(con, args.loan, args.day); print("Loan returned")
                elif args.command == "rename":
                    rename_book(con, args.book, args.title); print("Book renamed")
                elif args.command == "import-books":
                    print("Imported books:", import_books(con, args.csv))
                elif args.command == "backup":
                    backup(con, args.destination); print("Created new backup")
    except (ValueError, OSError, sqlite3.Error, csv.Error, UnicodeError) as error:
        parser.exit(1, "Library stopped: " + str(error) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
