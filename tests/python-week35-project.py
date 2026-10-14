"""Acceptance checks for Week35's independent, fictional SQLite project."""
from contextlib import closing
import importlib.util
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "docs" / "python-week35"
sys.path.insert(0, str(FOLDER))
import library_db as app
import analysis


def fails(exception, operation):
    try:
        operation()
    except exception:
        return
    raise AssertionError("Expected failure: " + repr(operation))


def state(con):
    return {name: [tuple(row) for row in con.execute("SELECT * FROM " + name + " ORDER BY id")]
            for name in ("books", "members", "loans")}


def version_one(path):
    con = sqlite3.connect(path, isolation_level=None)
    con.execute("PRAGMA foreign_keys=ON")
    for statement in app.SCHEMA:
        con.execute(statement)
    con.executemany("INSERT INTO books VALUES(?,?,?,?)", app.BOOKS)
    con.executemany("INSERT INTO members VALUES(?,?)", app.MEMBERS)
    con.executemany("INSERT INTO loans VALUES(?,?,?,?,?)", app.LOANS)
    con.execute("PRAGMA user_version=1")
    return con


with TemporaryDirectory(prefix="studyhub-week35-test-") as temp:
    folder = Path(temp)
    database = folder / "library.db"
    app.initialise(database)
    original_file = database.read_bytes()
    fails(FileExistsError, lambda: app.initialise(database))
    assert database.read_bytes() == original_file
    missing = folder / "typo.db"
    fails(sqlite3.OperationalError, lambda: app.connect(missing))
    assert not missing.exists()

    with closing(app.connect(database)) as con:
        assert con.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        initial = app.report(con)
        assert initial["schema_version"] == 2 and initial["books"] == 4 and initial["loans"] == 4
        assert [(m["loan_count"], m["open_count"]) for m in initial["members"]] == [(2, 1), (1, 1), (1, 0), (0, 0)]
        assert con.execute("SELECT SUM(pages) FROM books").fetchone()[0] == 840
        assert con.execute("SELECT SUM(b.pages) FROM loans AS l JOIN books AS b ON b.id=l.book_id").fetchone()[0] == 900
        assert analysis.compare(con)["event_total"] == 4
        before = state(con)
        # Foreign-key, active uniqueness, calendar and return ordering boundaries.
        fails(sqlite3.IntegrityError, lambda: app.borrow(con, 99, 1, "2026-01-11"))
        fails(sqlite3.IntegrityError, lambda: app.borrow(con, 3, 99, "2026-01-11"))
        fails(sqlite3.IntegrityError, lambda: app.borrow(con, 1, 4, "2026-01-11"))
        fails(ValueError, lambda: app.borrow(con, 3, 4, "2026-02-30"))
        fails(ValueError, lambda: app.borrow(con, 3, 4, "20260111"))
        fails(ValueError, lambda: app.borrow(con, True, 4, "2026-01-11"))
        fails(sqlite3.IntegrityError, lambda: app.return_book(con, 2, "2026-01-01"))
        fails(ValueError, lambda: app.return_book(con, 1, "2026-01-11"))
        fails(ValueError, lambda: app.return_book(con, 99, "2026-01-11"))
        assert state(con) == before and not con.in_transaction
        # A mid-operation failure must reverse a preceding valid change.
        try:
            with app.transaction(con):
                con.execute("UPDATE members SET name='Temporary' WHERE id=1")
                con.execute("INSERT INTO books VALUES(1,'Collision','Aya',150)")
        except sqlite3.IntegrityError:
            pass
        assert state(con) == before and not con.in_transaction
        with app.transaction(con):
            fails(ValueError, lambda: app.transaction(con).__enter__())
        hostile = "A Reader's Guide'); DROP TABLE loans; --"
        app.rename_book(con, 4, hostile)
        assert con.execute("SELECT title FROM books WHERE id=4").fetchone()[0] == hostile
        assert con.execute("SELECT COUNT(*) FROM loans").fetchone()[0] == 4
        fails(ValueError, lambda: app.rename_book(con, 99, "Missing"))
        fails(ValueError, lambda: app.rename_book(con, 4, "   "))
        fails(sqlite3.IntegrityError, lambda: con.execute("DELETE FROM books WHERE id=1"))
        fails(sqlite3.IntegrityError, lambda: con.execute("INSERT INTO books VALUES(9,'Bad pages','Aya',2.5)"))

        # Bounded insert-only import preserves exact accepted source tokens.
        source = folder / "books.csv"
        source.write_bytes((FOLDER / "books-import.csv").read_bytes())
        source_bytes = source.read_bytes()
        assert app.import_books(con, source) == 2
        assert source.read_bytes() == source_bytes
        before = state(con)
        fails(sqlite3.IntegrityError, lambda: app.import_books(con, source))
        assert state(con) == before
        source.write_text("id,title,author,pages\n7,First good,Aya,200\n1,Collision,Ken,160\n", encoding="utf-8")
        fails(sqlite3.IntegrityError, lambda: app.import_books(con, source))
        assert state(con) == before and not con.in_transaction
        for blob in [
            b"", b"id,title,author,pages\n", b"title,id,author,pages\nX,7,Y,100\n",
            b"id,title,author,pages\n7,X,Y\n", b"id,title,author,pages\n\n",
            b"id,title,author,pages\n7,X,Y,2.5\n",
            b"id,title,author,pages\n-1,X,Y,100\n",
            b"id,title,author,pages\n7,X,Y,0\n",
            b"id,title,author,pages\n7,X,Y,10001\n",
            b"id,title,author,pages\n7, ,Y,100\n",
            b"id,title,author,pages\n7,X,Y,100\n7,Z,Y,100\n",
            b"id,title,author,pages\n9223372036854775808,X,Y,100\n",
            ("id,title,author,pages\n7," + "X"*201 + ",Y,100\n").encode(),
            b"x"*(1024*1024+1),
        ]:
            fails(ValueError, lambda blob=blob: app.parse_books_csv(blob))
        accepted = app.parse_books_csv(b"\xef\xbb\xbfid,title,author,pages\n7, Keep spaces ,Aya,100\n")
        assert accepted == [(7, " Keep spaces ", "Aya", 100)]
        assert state(con) == before

        new_loan = app.borrow(con, 3, 4, "2026-01-11")
        assert new_loan == 5
        assert analysis.compare(con)["open_total"] == 3
        app.return_book(con, new_loan, "2026-01-12")
        facts = app.report(con)
        assert facts["books"] == 6 and facts["loans"] == 5
        assert facts["members"][-1]["loan_count"] == 1 and facts["members"][-1]["open_count"] == 0
        assert analysis.compare(con)["event_total"] == 5 and analysis.compare(con)["open_total"] == 2
        backup = folder / "backup.db"
        app.backup(con, backup)
        bytes_before = backup.read_bytes()
        fails(FileExistsError, lambda: app.backup(con, backup))
        assert backup.read_bytes() == bytes_before
        with closing(app.connect(backup, readonly=True)) as restored:
            assert app.report(restored) == facts
            fails(sqlite3.OperationalError, lambda: restored.execute("DELETE FROM loans"))
        current = state(con)
        assert app.migrate(con) is False and state(con) == current
        # SQL/pandas parity includes a wholly empty child population.
        with app.transaction(con):
            con.execute("DELETE FROM loans")
        assert analysis.compare(con)["event_total"] == analysis.compare(con)["open_total"] == 0
        assert len(analysis.compare(con)["members"]) == 4

    # Additive migration preserves exact old fields and handles failure atomically.
    with closing(version_one(folder / "older.db")) as con:
        old = state(con)
        assert app.migrate(con) is True
        assert [tuple(row)[:5] for row in con.execute("SELECT * FROM loans ORDER BY id")] == old["loans"]
        assert con.execute("SELECT COUNT(*) FROM loans WHERE note=''").fetchone()[0] == 4
        assert con.execute("PRAGMA user_version").fetchone()[0] == 2
    with closing(version_one(folder / "failed-migration.db")) as con:
        con.execute("CREATE TABLE loans_member_date(value INTEGER)")
        old = state(con)
        fails(sqlite3.OperationalError, lambda: app.migrate(con))
        assert state(con) == old and con.execute("PRAGMA user_version").fetchone()[0] == 1
        assert not any(r[1] == "note" for r in con.execute("PRAGMA table_info(loans)"))
        con.execute("PRAGMA user_version=99")
        fails(ValueError, lambda: app.migrate(con))
        assert state(con) == old
    with closing(sqlite3.connect(":memory:", isolation_level=None)) as con:
        con.execute("PRAGMA user_version=1")
        fails(ValueError, lambda: app.migrate(con))
    # Failed initialization and backup remove only their newly reserved outputs.
    old_migrate = app.migrate
    def broken_migrate(con):
        raise OSError("Simulated migration failure")
    app.migrate = broken_migrate
    failed = folder / "failed-init.db"
    try:
        fails(OSError, lambda: app.initialise(failed))
        assert not failed.exists()
    finally:
        app.migrate = old_migrate
    class BrokenBackup:
        def backup(self, target):
            raise OSError("Simulated backup failure")
    failed = folder / "failed-backup.db"
    fails(OSError, lambda: app.backup(BrokenBackup(), failed))
    assert not failed.exists()

    # Exercise the actual documented CLI sequence, not just imported helpers.
    cli_db = folder / "cli.db"
    def cli(*args, good=True):
        run = subprocess.run([sys.executable, str(FOLDER/"library_db.py"), str(cli_db), *map(str,args)],
                             capture_output=True, text=True, encoding="utf-8")
        assert (run.returncode == 0) is good, run.stderr
        return run.stdout
    cli("init")
    cli("init", good=False)
    assert json.loads(cli("report"))["loans"] == 4
    cli("import-books", FOLDER/"books-import.csv")
    cli("borrow", 3, 4, "2026-01-11")
    cli("borrow", 3, 1, "2026-01-11", good=False)
    cli("return", 5, "2026-01-12")
    cli("return", 5, "2026-01-13", good=False)
    cli("rename", 4, "Quiet Reading revised")
    cli("backup", folder/"cli-backup.db")
    cli("migrate")
    result = subprocess.run([sys.executable,str(FOLDER/"analysis.py"),str(cli_db)],capture_output=True,text=True,encoding="utf-8")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["event_total"] == 5
    assert json.loads(cli("report"))["books"] == 6

print("PASS: Week35 library CLI, SQL/pandas parity including zero events, bound hostile values, FK/active-unique/page/date rules, atomic insert-only CSV import, migration success/failure, persistent reopen/read-only/path refusal, verified non-overwriting backups and failure cleanup.")
