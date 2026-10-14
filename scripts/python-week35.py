"""Append only Week35 teaching data after executing every authored snippet."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap

ROOT = Path(__file__).resolve().parents[1]
DAYS = {f"35.{d}": {"parts": []} for d in range(6)}
JOBS = []


def clean(code):
    return textwrap.dedent(code).strip() + "\n"


def sec(t, v=None, **extra):
    return {"t": t, **({"v": v} if v is not None else {}), **extra}


def lesson(day, title, goal, terms, explanation, syntax, example, walkthrough,
           mistake, task, solution, challenge, challenge_code, takeaway, quizzes):
    parts = DAYS[f"35.{day}"]["parts"]
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
        sec("p", explanation), sec("syn", syntax, note="SQL pattern where shown; run the complete Python example in a fresh practice folder."),
        sec("code", clean(example)), output, sec("p", walkthrough),
        sec("mis", wrong=mistake[0], right=mistake[1], why=mistake[2]),
        sec("ex", task, practiceId=f"35.{day}.{index}.build"), build,
        sec("ex", "Mini challenge: " + challenge, practiceId=f"35.{day}.{index}.challenge"), stretch,
        sec("try", q=quizzes[0][0], code="# Predict, then explain before revealing.", a=quizzes[0][1], why=quizzes[0][4]),
        sec("checkpoint", lesson={"id": f"course:35.{day}.{index}", "quiz": questions}), sec("key", takeaway)
    ]})
    JOBS.extend([(clean(example), output), (clean(solution), build), (clean(challenge_code), stretch)])


BASIC = '''import sqlite3
con = sqlite3.connect(":memory:", isolation_level=None)
con.executescript("""
CREATE TABLE books(id INTEGER PRIMARY KEY, title TEXT NOT NULL,
    author TEXT NOT NULL, pages INTEGER NOT NULL CHECK(pages > 0));
INSERT INTO books VALUES
    (1,'Python Steps','Mira',180),(2,'Data Stories','Ken',240),
    (3,'SQL Garden','Mira',300),(4,'Quiet Reading','Aya',120);
""")
'''
SETUP = BASIC + '''con.execute("PRAGMA foreign_keys=ON")
con.executescript("""
CREATE TABLE members(id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE loans(id INTEGER PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES books(id),
    member_id INTEGER NOT NULL REFERENCES members(id),
    borrowed_on TEXT NOT NULL, returned_on TEXT);
INSERT INTO members VALUES (1,'Asha'),(2,'Ben'),(3,'Chandra'),(4,'Dipa');
INSERT INTO loans VALUES
    (1,1,1,'2026-01-01','2026-01-05'),(2,1,2,'2026-01-06',NULL),
    (3,2,1,'2026-01-07',NULL),(4,3,3,'2026-01-08','2026-01-10');
""")
'''


def demo(body, setup=SETUP):
    return setup + clean(body) + "con.close()\n"


lesson(0, "1. A database stores facts; SQL asks for results",
    "Distinguish a database file, a table, a query and the Python code sending it.",
    [("Relational database; SQL", "A relational database organises related facts into tables. SQL defines, queries and changes those tables; Python supplies the surrounding program."),
     ("sqlite3; connect; :memory:", "sqlite3 is Python's standard-library SQLite interface. connect(':memory:') creates an isolated temporary database, unrelated to your website or personal files."),
     ("execute; fetchall; close", "execute sends one SQL statement and returns a cursor, an object that retrieves results. fetchall returns a list of row tuples. close releases the connection; it does not save uncommitted changes."),
     ("Teaching setup: executescript; isolation_level=None", "executescript runs a fixed author-written setup script, never user input. isolation_level=None disables Python's legacy implicit transaction opening. Statements commit automatically unless we explicitly BEGIN; Day6 teaches grouped transactions. On Python3.12+ this uses the default LEGACY_TRANSACTION_CONTROL mode; do not mix transaction policies blindly.")],
    "A CSV is useful for exchange; a database can also enforce rules, relate tables and filter a question without loading every row into Python. "
    "A table has named columns and rows. A query produces a result table; it need not change the stored table. "
    "CREATE TABLE defines the shape, INSERT adds a fictional row and SELECT requests two fields. A tuple in the output is one row, in the selected column order. "
    "SQL keywords are conventionally uppercase; they are not Python function names. The SQL text is inside a Python string. "
    "Every example is self-contained. Run it locally in Python. The website displays lessons and outputs offline; it does not run a database server or alter browser progress storage.",
    'connection.execute("SELECT column FROM table_name").fetchall()',
    '''import sqlite3
con = sqlite3.connect(":memory:", isolation_level=None)
con.execute("CREATE TABLE books(id INTEGER PRIMARY KEY, title TEXT)")
con.execute("INSERT INTO books VALUES(1, 'Python Steps')")
print(con.execute("SELECT id,title FROM books").fetchall())
con.close()''',
    "CREATE establishes two columns. INSERT supplies a matching row. SELECT chooses id then title, so fetchall returns [(1, 'Python Steps')]. ':memory:' disappears when this connection closes. A file persists committed data; Day4 practises that.",
    ('SELECT title FROM books  # bare Python', 'con.execute("SELECT title FROM books").fetchall()', "SQL must be sent as text through the interface."),
    "Create a one-column topics table, insert SQL and select it.",
    '''import sqlite3
con=sqlite3.connect(":memory:", isolation_level=None)
con.execute("CREATE TABLE topics(name TEXT)")
con.execute("INSERT INTO topics VALUES('SQL')")
print(con.execute("SELECT name FROM topics").fetchall())
con.close()''',
    "Insert a second topic and return both alphabetically. ORDER BY specifies order; Day2 explains it fully.",
    '''import sqlite3
con=sqlite3.connect(":memory:", isolation_level=None)
con.executescript("CREATE TABLE topics(name TEXT); INSERT INTO topics VALUES('SQL'),('Python');")
print(con.execute("SELECT name FROM topics ORDER BY name").fetchall())
con.close()''',
    "A database stores rows; SQL asks questions; sqlite3 connects Python to SQLite. Use temporary practice data first.",
    [("Does ':memory:' modify Study Hub progress?", "No", "Always", "Only in dark mode", "A temporary SQLite connection is unrelated to browser localStorage."),
     ("What does fetchall return here?", "A list of result-row tuples", "SQL source code", "A database password", "Each tuple follows the SELECT column order.")])

lesson(0, "2. Tables, columns and primary keys",
    "Design rows around a clear entity and choose a stable key.",
    [("Schema; CREATE TABLE", "A schema declares tables, columns and rules. CREATE TABLE defines structure; it does not insert records."),
     ("INTEGER PRIMARY KEY; TEXT; affinity", "An INTEGER PRIMARY KEY uniquely identifies a row in this table. TEXT stores text. Ordinary SQLite uses flexible type affinity; an INTEGER declaration alone is not strict validation."),
     ("NOT NULL; CHECK; PRAGMA table_info", "NOT NULL rejects missing required values; CHECK rejects false rules such as pages>0. Combine them to forbid unknowns. PRAGMA table_info inspects column position, name, type, required flag, default and key flag.")],
    "Our fictional library has four physical book copies. Each books.id identifies one copy; a title is not a key because two copies can share a title. "
    "The repeated setup creates and populates books so every snippet runs independently. It is fixed trusted SQL. "
    "A row has an id, title, author display label and page count. Use a stable key that remains unchanged when a description changes. "
    "Pages must be known and positive. Ordinary SQLite affinity can still accept unexpected storage classes; the final project's CHECK also uses typeof(pages), and its Python importer validates integers. "
    "Inspection confirms a declaration, not that every possible dirty input has been excluded.",
    'CREATE TABLE books(id INTEGER PRIMARY KEY, title TEXT NOT NULL, pages INTEGER NOT NULL CHECK(pages>0));',
    demo('print(con.execute("SELECT id,title,pages FROM books ORDER BY id").fetchall())\nprint([(r[1],r[2],r[5]) for r in con.execute("PRAGMA table_info(books)")])', BASIC),
    "id is the stable copy key. The inspection returns column name/type/key status; ORDER BY id makes the displayed row order intentional.",
    ('CREATE TABLE books(title TEXT PRIMARY KEY)', 'CREATE TABLE books(id INTEGER PRIMARY KEY, title TEXT NOT NULL)', "Titles can repeat and change."),
    "Show each copy's id and author, ordered by id.",
    demo('print(con.execute("SELECT id,author FROM books ORDER BY id").fetchall())', BASIC),
    "Add another Python Steps copy with id5 and show both. WHERE filters rows; Day2 expands it.",
    demo('con.execute("INSERT INTO books VALUES(5,\'Python Steps\',\'Mira\',180)")\nprint(con.execute("SELECT id,title FROM books WHERE title=\'Python Steps\' ORDER BY id").fetchall())', BASIC),
    "Choose what one row represents before its key. Names and titles are usually not reliable identities.",
    [("What does books.id identify here?", "One physical copy", "A title shared by all copies", "An author", "We chose the copy as the entity."),
     ("Does INTEGER alone guarantee strictly integer values?", "No", "Always", "Only for negatives", "Ordinary affinity needs appropriate validation and constraints.")])

lesson(0, "3. Relationships and foreign keys",
    "Connect copies and members through individual loan events.",
    [("Foreign key; REFERENCES", "A child column points to a parent key: loans.book_id references books.id; loans.member_id references members.id."),
     ("One-to-many; event table", "One copy can have many historical loans; one member can borrow many copies. Each loans row is one event connecting one member and one copy."),
     ("PRAGMA foreign_keys=ON; fetchone", "Enable and check foreign-key enforcement on each connection before transactions. fetchone retrieves one row or None when no row remains."),
     ("NULL; Python None", "SQL NULL is an unknown or absent value, mapped to Python None. In this schema returned_on=NULL means still open, not the text 'NULL'.")],
    "Do not store a comma-separated list of borrowers inside a book row: that loses separate event dates and is difficult to validate. "
    "books stores copy facts, members stores member facts and loans stores event facts. Loan1 and loan2 concern the same copy at different times. "
    "The expanded setup includes all three tables, REFERENCES rules and four fictional loans. Dates use fixed YYYY-MM-DD text. "
    "A copy with no loan still exists. A NULL return date denotes an open event; a known return date closes it. "
    "Foreign keys prevent references to nonexistent parents when enforcement is on. They do not alone prevent two simultaneous open loans; Day6 adds that separate rule.",
    'loans.book_id -> books.id\nloans.member_id -> members.id\nPRAGMA foreign_keys=ON;',
    demo('print("FK enforcement:",con.execute("PRAGMA foreign_keys").fetchone()[0])\nprint(con.execute("SELECT id,book_id,member_id,returned_on FROM loans ORDER BY id").fetchall())'),
    "Repeated book_id1 is valid history, not a duplicate loan key. Each loan has its own id. None is Python's display of SQL NULL.",
    ('# Treat a repeated current name as loan identity', '# Use member_id REFERENCES members(id)', "Renaming a person must not change their historical identity."),
    "Find historical loan ids and members for book1.",
    demo('print(con.execute("SELECT id,member_id FROM loans WHERE book_id=1 ORDER BY id").fetchall())'),
    "Count all three tables separately. Equal counts here do not prove a one-to-one relationship.",
    demo('for name in ("books","members","loans"):\n    # Names are from this fixed trusted tuple, not visitor input.\n    print(name,con.execute("SELECT COUNT(*) FROM "+name).fetchone()[0])'),
    "Separate entities from events; enable and verify foreign keys on each new connection.",
    [("Can one copy have several historical loans?", "Yes", "Never", "Only with disabled keys", "A one-to-many history is expected."),
     ("Where is foreign-key enforcement enabled?", "On each connection before transactions", "Once on the website", "In a member name", "New connections do not inherit this setting automatically.")])

lesson(0, "4. Normalisation prevents update anomalies",
    "Place each fact with the entity or event it describes.",
    [("Normalisation; update anomaly", "Normalisation organises facts to reduce inconsistent repetition. An update anomaly occurs when repeated copies of one fact are changed inconsistently."),
     ("Functional dependency", "A key determines an entity's attributes: member_id determines the current member name. A loan id determines that event's book, member and dates.")],
    "Writing Asha's current name into every loan would require several updates for one spelling correction. A missed copy would disagree. "
    "members stores the current name once; loans points to the stable member id. A join later retrieves the current name. "
    "This beginner schema is not a complete publishing catalogue. Works, editions, copies and multiple authors might deserve separate tables in a larger system. "
    "Here author is a display label, not an independently validated author identity. A historical name snapshot would also be a different requirement from a current name. "
    "Decide which facts should stay historical and which should follow current identity before splitting tables.",
    'members(id,name)\nbooks(id,title,author,pages)\nloans(id,book_id,member_id,borrowed_on,returned_on)',
    demo('con.execute("UPDATE members SET name=\'Asha Rai\' WHERE id=1")\nprint(con.execute("SELECT id,name FROM members WHERE id=1").fetchall())\nprint(con.execute("SELECT id,member_id FROM loans WHERE member_id=1 ORDER BY id").fetchall())'),
    "One member row changes; both events still reference member1. UPDATE chooses a change and WHERE chooses its target. Day6 teaches safe write groups.",
    ('# Keep separately editable current names in every loan', '# Store current name in members; loans keeps member_id', "One current fact should not disagree across repeated copies."),
    "Rename Ben using member id2; show loan2 still refers to id2.",
    demo('con.execute("UPDATE members SET name=\'Ben K.\' WHERE id=2")\nprint(con.execute("SELECT id,name FROM members WHERE id=2").fetchall())\nprint(con.execute("SELECT id,member_id FROM loans WHERE id=2").fetchall())'),
    "Change a copy's display title while retaining its id and historical references.",
    demo('con.execute("UPDATE books SET title=\'Python First Steps\' WHERE id=1")\nprint(con.execute("SELECT id,title FROM books WHERE id=1").fetchall())\nprint(con.execute("SELECT id,book_id FROM loans WHERE book_id=1 ORDER BY id").fetchall())'),
    "Keep current facts once; keep event facts with the event. Document deliberately stored historical snapshots.",
    [("Where does the current member name belong here?", "members", "Each loan as a separate editable copy", "An SQL password", "Stable ids reach one current name."),
     ("Is this a complete publishing catalogue?", "No", "For every library", "Only with four books", "Richer identities require a richer model.")])

lesson(0, "5. Constraints are executable data rules",
    "Predict rejected writes and inspect the surviving database.",
    [("IntegrityError", "sqlite3.IntegrityError reports a violated database rule: duplicate key, missing required value, failed CHECK or foreign-key violation."),
     ("Validation versus constraint", "Python validation gives helpful input messages. Database constraints enforce shared rules for correctly connected writers. Both have a role.")],
    "Try adding a second copy with id1: the primary key rejects it. Missing title violates NOT NULL; pages0 violates CHECK; book99 violates the enabled foreign key. "
    "Catch the specific integrity exception and explain the rejected operation. Do not catch everything and print saved. "
    "These examples use automatic statement transactions; a failed statement does not undo earlier committed setup rows. A group of dependent writes needs an explicit transaction. "
    "Constraints cover only declared rules. The simple setup does not yet validate real calendar dates or prevent overlapping open loans. "
    "The final interface validates dates and adds an active-loan unique index.",
    'try:\n    con.execute("INSERT ...")\nexcept sqlite3.IntegrityError:\n    # Explain rejection.',
    demo('try:\n    con.execute("INSERT INTO books VALUES(1,\'Another copy\',\'Mira\',200)")\nexcept sqlite3.IntegrityError:\n    print("Duplicate copy ID rejected")\nprint("Books retained:",con.execute("SELECT COUNT(*) FROM books").fetchone()[0])'),
    "The rejected INSERT added nothing. Four books remain. A specific catch does not hide unrelated programming errors.",
    ('except Exception:\n    print("Saved")', 'except sqlite3.IntegrityError:\n    print("Rejected: data rule failed")', "Success must match actual committed state."),
    "Attempt pages0 with a new id; catch the rejection and show no id5 exists.",
    demo('try:\n    con.execute("INSERT INTO books VALUES(5,\'Bad pages\',\'Mira\',0)")\nexcept sqlite3.IntegrityError:\n    print("Positive-page rule rejected the row")\nprint(con.execute("SELECT id FROM books WHERE id=5").fetchall())'),
    "Try a loan for nonexistent book99; show that four loans remain.",
    demo('try:\n    con.execute("INSERT INTO loans VALUES(5,99,1,\'2026-01-11\',NULL)")\nexcept sqlite3.IntegrityError:\n    print("Unknown book rejected")\nprint(con.execute("SELECT COUNT(*) FROM loans").fetchone()[0])'),
    "A rejected statement is not a saved record. Inspect state and distinguish declared rules from unimplemented requirements.",
    [("Which exception reports a violated SQLite data rule?", "sqlite3.IntegrityError", "FileNotFoundError", "StopIteration", "Constraint failures are integrity errors."),
     ("Does a foreign key stop two active loans for one copy?", "No", "Always", "Only on Mondays", "It checks parent existence, not availability.")])

lesson(1, "1. SELECT columns and filter rows with WHERE",
    "Answer focused questions without retrieving unnecessary columns.",
    [("SELECT; FROM; WHERE", "SELECT names output expressions, FROM names the source and WHERE retains rows whose condition is true. Filtering is not deletion."),
     ("Projection; comparison; AS", "Projection chooses columns; filtering chooses rows. Comparisons include =, <>, > and <=. AS gives a result-column alias without renaming storage.")],
    "Which copies have at least200pages? Select id and title, then filter pages>=200. "
    "SELECT * helps quick inspection but couples a report to all future columns. Name required fields in an interface. "
    "SQL uses = for equality; Python uses ==. A quoted 'Mira' is a value; books is a table identifier. "
    "The repeated fictional setup still has four books, four members and four loan events. Outputs are ordered deliberately. "
    "Read the source, row condition, selected fields and ordering separately. SELECT appears first in the text, but that is not the entire logical processing sequence.",
    "SELECT id,title FROM books WHERE pages>=200 ORDER BY id;",
    demo('print(con.execute("SELECT id,title FROM books WHERE pages>=200 ORDER BY id").fetchall())\nprint(con.execute("SELECT title,pages AS page_count FROM books WHERE author=\'Mira\' ORDER BY id").fetchall())'),
    "Data Stories and SQL Garden meet the threshold. The author query asks a different question. AS changes the result label, not the schema.",
    ('SELECT * FROM books; -- assume only long books', 'SELECT id,title FROM books WHERE pages>=200 ORDER BY id;', "Name the output fields and row rule."),
    "Q1: list all titles by id. Q2: list titles with fewer than200pages.",
    demo('print("Q1",con.execute("SELECT title FROM books ORDER BY id").fetchall())\nprint("Q2",con.execute("SELECT title FROM books WHERE pages<200 ORDER BY id").fetchall())'),
    "Q3: select ids with exactly240pages. Q4: select ids not authored by Mira.",
    demo('print("Q3",con.execute("SELECT id FROM books WHERE pages=240 ORDER BY id").fetchall())\nprint("Q4",con.execute("SELECT id FROM books WHERE author<>\'Mira\' ORDER BY id").fetchall())'),
    "SELECT chooses output; WHERE chooses rows. A filtered result does not erase source data.",
    [("Does WHERE delete nonmatching rows?", "No", "Always", "Only for ids", "A SELECT reads results."),
     ("What does AS page_count do?", "Labels a result column", "Renames a stored table", "Adds a book", "The alias belongs to this result.")])

lesson(1, "2. Combine conditions without changing the question",
    "Use AND, OR, IN, BETWEEN and LIKE with deliberate grouping.",
    [("AND; OR; parentheses", "AND requires both conditions; OR requires at least one. AND binds more tightly, so group alternatives with parentheses."),
     ("IN; BETWEEN; LIKE", "IN checks listed values. BETWEEN includes both endpoints. LIKE uses % for any run of characters and _ for one character; it is a pattern operator, not universal Unicode-aware search.")],
    "Mira or Ken with at least200pages needs parentheses around the author alternatives; otherwise AND binds only to Ken's condition. "
    "IN shortens several equality alternatives. BETWEEN180AND240 includes both endpoints. "
    "LIKE 'SQL%' means titles beginning with SQL in this ASCII fixture. Case behaviour and collation differ by engine; do not infer universal Japanese or Nepali search rules. "
    "Fixed literals here are author-written; Day4 binds user-supplied values. "
    "A bound LIKE pattern still has wildcard semantics. An interface promising literal substring search must escape % and _ deliberately.",
    "WHERE (author='Mira' OR author='Ken') AND pages>=200\nWHERE pages BETWEEN 180 AND 240\nWHERE title LIKE 'SQL%'",
    demo('print(con.execute("SELECT id FROM books WHERE (author=\'Mira\' OR author=\'Ken\') AND pages>=200 ORDER BY id").fetchall())\nprint(con.execute("SELECT id FROM books WHERE pages BETWEEN 180 AND 240 ORDER BY id").fetchall())'),
    "The first result has ids2and3: the threshold applies to either author. The interval includes180and240.",
    ("WHERE author='Mira' OR author='Ken' AND pages>=200", "WHERE (author='Mira' OR author='Ken') AND pages>=200", "Without grouping, Mira's short copy qualifies."),
    "Q5: list ids for Aya or Ken using IN. Q6: list titles beginning SQL using LIKE.",
    demo('print("Q5",con.execute("SELECT id FROM books WHERE author IN (\'Aya\',\'Ken\') ORDER BY id").fetchall())\nprint("Q6",con.execute("SELECT title FROM books WHERE title LIKE \'SQL%\' ORDER BY id").fetchall())'),
    "Q7: list ids with180through300pages inclusive, excluding author Ken.",
    demo('print("Q7",con.execute("SELECT id FROM books WHERE pages BETWEEN 180 AND 300 AND author<>\'Ken\' ORDER BY id").fetchall())'),
    "Translate the whole condition into words and test boundary cases.",
    [("Does BETWEEN180AND240 include180?", "Yes", "No", "Only for TEXT", "Both endpoints are included."),
     ("Does parameter binding remove LIKE wildcards?", "No", "Always", "For short strings", "Binding protects SQL structure, not pattern meaning.")])

lesson(1, "3. NULL is neither zero nor the word NULL",
    "Write missing-value predicates and distinguish count denominators.",
    [("IS NULL; three-valued logic", "Comparisons involving NULL are normally unknown. WHERE keeps true rows, so returned_on=NULL does not find open loans. Use IS NULL or IS NOT NULL."),
     ("COUNT(*); COUNT(column); COALESCE", "COUNT(*) counts rows; COUNT(column) counts non-NULL values. COALESCE returns the first non-NULL expression for display or a declared calculation without changing stored data.")],
    "Two of four loan events remain open, represented by NULL in returned_on. That is not zero or the text 'NULL'. "
    "returned_on=NULL yields unknown rather than true and finds no rows. IS NULL states the intended test. "
    "COUNT(returned_on) counts known return dates; COUNT(*) counts all loan events. After a LEFT JOIN the distinction becomes especially important. "
    "COALESCE(returned_on,'OPEN') makes display readable without inventing a real return date or updating the source. "
    "NOT IN can surprise you if a subquery contains NULL. Day3 uses NOT EXISTS for the no-matching-loan question.",
    "SELECT id FROM loans WHERE returned_on IS NULL;\nSELECT COUNT(*),COUNT(returned_on) FROM loans;",
    demo('print("Wrong:",con.execute("SELECT id FROM loans WHERE returned_on=NULL").fetchall())\nprint("Open:",con.execute("SELECT id FROM loans WHERE returned_on IS NULL ORDER BY id").fetchall())\nprint("Events/returns:",con.execute("SELECT COUNT(*),COUNT(returned_on) FROM loans").fetchone())'),
    "The wrong predicate returns no rows despite two open events. (4,2) means four events, two known return dates.",
    ('WHERE returned_on = NULL', 'WHERE returned_on IS NULL', "NULL does not use ordinary equality tests."),
    "Q8: list closed loan ids in order.",
    demo('print("Q8",con.execute("SELECT id FROM loans WHERE returned_on IS NOT NULL ORDER BY id").fetchall())'),
    "Display every id and its date or OPEN; prove the underlying open count is still2.",
    demo('print(con.execute("SELECT id,COALESCE(returned_on,\'OPEN\') FROM loans ORDER BY id").fetchall())\nprint(con.execute("SELECT COUNT(*) FROM loans WHERE returned_on IS NULL").fetchone()[0])'),
    "Use IS NULL for missingness and name a count's denominator before interpreting it.",
    [("Which predicate finds open loans?", "returned_on IS NULL", "returned_on = NULL", "returned_on = 'NULL'", "Open means a SQL NULL return date here."),
     ("What does COUNT(returned_on) count?", "Known return-date values", "Every event", "Member ids", "COUNT(expression) ignores NULL.")])

lesson(1, "4. DISTINCT, ORDER BY and LIMIT need a clear unit",
    "Produce reproducible top results without merging identities.",
    [("DISTINCT", "DISTINCT removes duplicate selected result rows across all selected columns. It does not establish that two entities are the same."),
     ("ORDER BY; DESC; LIMIT; OFFSET", "ORDER BY specifies result order; DESC reverses a key. LIMIT caps rows and OFFSET skips rows. Add a stable tie-breaker for top-N results.")],
    "DISTINCT author asks which author labels occur; DISTINCT id,author still retains each different id. "
    "Do not use DISTINCT reflexively to hide a broken join. First identify what one result row represents. "
    "For the longest two copies, sort pages descending then id ascending before LIMIT2. Without ordering, first does not mean longest. "
    "A second key resolves ties reproducibly. OFFSET supports simple paging in a stable snapshot, but concurrent edits can shift later pages. "
    "SQLite's default ascending ordering places NULL first; choose explicit missingness behaviour when an interface depends on it.",
    "SELECT DISTINCT author FROM books ORDER BY author;\nSELECT id,title FROM books ORDER BY pages DESC,id LIMIT 2;",
    demo('print(con.execute("SELECT DISTINCT author FROM books ORDER BY author").fetchall())\nprint(con.execute("SELECT id,title FROM books ORDER BY pages DESC,id LIMIT 2").fetchall())'),
    "Three author labels remain. SQL Garden then Data Stories are the top two under the chosen ranking.",
    ('SELECT title FROM books LIMIT 2; -- assume longest', 'SELECT title FROM books ORDER BY pages DESC,id LIMIT 2;', "LIMIT is not a ranking."),
    "Q9: distinct page counts ascending. Q10: the shortest copy with an id tie-breaker.",
    demo('print("Q9",con.execute("SELECT DISTINCT pages FROM books ORDER BY pages").fetchall())\nprint("Q10",con.execute("SELECT id,title FROM books ORDER BY pages,id LIMIT 1").fetchall())'),
    "Add another300-page copy with id5; show that top ties sort3then5.",
    demo('con.execute("INSERT INTO books VALUES(5,\'More SQL\',\'Aya\',300)")\nprint(con.execute("SELECT id,pages FROM books ORDER BY pages DESC,id LIMIT 2").fetchall())'),
    "Define identity, ranking and tie-breaking explicitly.",
    [("Does LIMIT2 alone mean the two longest?", "No", "Always", "With four books", "Ranking requires ORDER BY."),
     ("What does DISTINCT id,author deduplicate?", "Whole selected pairs", "Author only", "Copies with the same title", "DISTINCT considers the entire selected row.")])

lesson(1, "5. Read a query in logical stages",
    "Combine selection, predicates and ranking and explain surviving rows.",
    [("Logical stages", "For these queries think FROM, WHERE, SELECT, DISTINCT, ORDER BY, LIMIT. This is reasoning order, not a promise about physical optimiser execution."),
     ("Computed column; integer division", "A SELECT expression produces an output value without changing storage. SQLite integer/integer division truncates; pages/10.0 makes fractional intent explicit.")],
    "Start with the question, choose the source and conditions, then output and order. Give calculations readable aliases. "
    "Use a real divisor when the result should include fractions. The example compares5/2with5/2.0 so the difference is visible. "
    "Do not assume a SELECT alias is universally available in WHERE across SQL engines. Repeat a simple expression or use a subquery later. "
    "The optimiser can evaluate a query differently from this logical explanation. Correctness follows semantics, not a belief that it scans top to bottom. "
    "Before progressing, answer the ten numbered questions from earlier parts without solutions, then change thresholds and predict new outputs.",
    "SELECT id,title,pages/10.0 AS tens FROM books WHERE pages>=180 ORDER BY tens DESC,id LIMIT 2;",
    demo('print(con.execute("SELECT id,title,pages/10.0 AS tens FROM books WHERE pages>=180 ORDER BY tens DESC,id LIMIT 2").fetchall())\nprint("Integer/real:",con.execute("SELECT 5/2,5/2.0").fetchone())'),
    "The filter leaves ids 1, 2 and 3; ranking chooses 3 then 2. SELECT 5/2 returns 2, while 5/2.0 returns 2.5.",
    ('SELECT pages/10 AS tens FROM books; -- expect fractions', 'SELECT pages/10.0 AS tens FROM books;', "A real operand gives fractional division."),
    "Show title and pages/100.0 for all copies, ordered by pages then id.",
    demo('print(con.execute("SELECT title,pages/100.0 AS hundreds FROM books ORDER BY pages,id").fetchall())'),
    "Return the longest Mira copy; explain why author filtering happens before limiting the result.",
    demo('print(con.execute("SELECT id,title FROM books WHERE author=\'Mira\' ORDER BY pages DESC,id LIMIT 1").fetchall())'),
    "Explain source, row rule, output unit and ranking before running. Logical reasoning is not a physical execution plan.",
    [("What is SQLite SELECT5/2 here?", "2", "2.5", "NULL", "Both operands are integers."),
     ("Does a SELECT expression overwrite pages?", "No", "Always", "Only when aliased", "Changing storage requires a write statement.")])

lesson(2, "1. INNER JOIN matches facts without changing their identity",
    "Join an event to its copy using the declared key relationship.",
    [("INNER JOIN; ON; table alias", "INNER JOIN keeps matching pairs according to ON. books AS b gives the table a short name; b.id qualifies its column so it cannot be confused with loans.id."),
     ("Join cardinality; row multiplication", "The output contains matching pairs, not necessarily one row per parent. One book with two loans creates two joined rows. Missing or incorrect ON conditions can multiply unrelated rows.")],
    "We want readable loan history: each loan event plus its book title. loans.book_id matches books.id; loan id is the event identity. "
    "Do not join books.id=loans.id merely because both columns are named id. They refer to different entities. "
    "Python Steps appears twice because it has two historical events. That is expected multiplicity, not an error to remove with DISTINCT. "
    "INNER JOIN excludes copies without any matching loan, such as Quiet Reading. Start from the question's unit before picking a join. "
    "A join reads a result; it does not permanently merge the tables or alter their foreign keys.",
    "SELECT l.id,b.title FROM loans AS l INNER JOIN books AS b ON b.id=l.book_id ORDER BY l.id;",
    demo('rows=con.execute("SELECT l.id,b.id,b.title FROM loans AS l INNER JOIN books AS b ON b.id=l.book_id ORDER BY l.id").fetchall()\nprint(rows)\nprint("Event rows:",len(rows))'),
    "Four events remain. The repeated title retains separate loan ids. Book4 is absent because it has no matching event.",
    ('ON b.id=l.id', 'ON b.id=l.book_id', "Match the foreign key to its parent, not unrelated ids."),
    "Join loans to members and display event id and member name.",
    demo('print(con.execute("SELECT l.id,m.name FROM loans AS l JOIN members AS m ON m.id=l.member_id ORDER BY l.id").fetchall())'),
    "Count joined rows for copy1 and contrast them with the number of distinct copies in that result.",
    demo('print(con.execute("SELECT COUNT(*),COUNT(DISTINCT b.id) FROM books AS b JOIN loans AS l ON l.book_id=b.id WHERE b.id=1").fetchone())'),
    "A join's unit is a matching pair. Check multiplicity before counting or summing parent facts.",
    [("Why does Python Steps appear twice in history?", "It has two loan events", "The primary key is broken", "SELECT copied the book permanently", "History is one row per event."),
     ("Which columns link a loan to its copy?", "loans.book_id and books.id", "loans.id and books.id", "members.name and books.title", "The foreign-key relationship supplies the match.")])

lesson(2, "2. LEFT JOIN keeps zero-event parents",
    "Count every member, including members who never borrowed.",
    [("LEFT JOIN; null-extended row", "LEFT JOIN retains all left-side rows. A left row with no match gets NULLs for right-side fields, making one placeholder result row."),
     ("COUNT(child.id); ON versus WHERE", "Count the child's non-NULL key for matched events. Put an optional child restriction in ON when unmatched parents must survive; a WHERE child predicate can remove them.")],
    "Dipa has no loans. An INNER JOIN report omits her, while a member-first LEFT JOIN preserves her with NULL loan fields. "
    "COUNT(*) would count that placeholder as one result row. COUNT(l.id) correctly counts zero matching events. "
    "To report open events for every member, put returned_on IS NULL inside ON. A post-join WHERE can remove a member who has only closed loans. "
    "Even WHERE returned_on IS NULL is subtle: it keeps an unmatched placeholder but removes a matched closed-only member. "
    "The desired question is all members with the count of matching open events, so the match condition must include open status.",
    "SELECT m.id,m.name,COUNT(l.id) FROM members AS m LEFT JOIN loans AS l ON l.member_id=m.id GROUP BY m.id,m.name ORDER BY m.id;",
    demo('print(con.execute("SELECT m.id,m.name,COUNT(*),COUNT(l.id) FROM members AS m LEFT JOIN loans AS l ON l.member_id=m.id GROUP BY m.id,m.name ORDER BY m.id").fetchall())'),
    "Dipa's tuple has placeholder count1but actual event count0. Asha has two actual events; the count is not a count of distinct people.",
    ('COUNT(*) AS matching_loans', 'COUNT(l.id) AS matching_loans', "Null-extended placeholders must not count as child events."),
    "Return every member's open-loan count, using the status restriction in ON.",
    demo('print(con.execute("SELECT m.id,COUNT(l.id) FROM members AS m LEFT JOIN loans AS l ON l.member_id=m.id AND l.returned_on IS NULL GROUP BY m.id ORDER BY m.id").fetchall())'),
    "Compare the ids preserved by an open predicate in ON with the same predicate in WHERE.",
    demo('print("ON",con.execute("SELECT DISTINCT m.id FROM members AS m LEFT JOIN loans AS l ON l.member_id=m.id AND l.returned_on IS NULL ORDER BY m.id").fetchall())\nprint("WHERE",con.execute("SELECT DISTINCT m.id FROM members AS m LEFT JOIN loans AS l ON l.member_id=m.id WHERE l.returned_on IS NULL ORDER BY m.id").fetchall())'),
    "Preserve the parent population deliberately; count child keys and place child restrictions according to the question.",
    [("Which count gives Dipa zero loans?", "COUNT(l.id)", "COUNT(*)", "COUNT(m.id)", "The unmatched child key is NULL."),
     ("Where does an open-only match condition belong to retain all members?", "In ON", "Only in LIMIT", "In a title string", "ON limits matches without removing left-side parents.")])

lesson(2, "3. RIGHT JOIN and portable preservation",
    "Understand the preserved side and rewrite it as a LEFT JOIN.",
    [("RIGHT JOIN; version requirement", "RIGHT JOIN preserves the right table and was added in SQLite3.39.0. An equivalent swapped LEFT JOIN works on older SQLite and makes the retained population easy to read."),
     ("SQL dialect", "Engines implement different SQL features and details. sqlite3.sqlite_version reports the SQLite library version; it is different from your Python version.")],
    "The roadmap includes RIGHT JOIN, so learn its meaning without making your offline practice depend on a recent runtime. "
    "loans RIGHT JOIN members preserves members. Swap the order to members LEFT JOIN loans and retain the same ON relationship. "
    "Always list and order output columns explicitly; SELECT * can have different column order after the rewrite. "
    "The example executes the portable form and, where supported, compares it with RIGHT JOIN. It prints a stable equivalence result instead of a machine-dependent version string. "
    "Neither form solves count inflation automatically. Parent and child units remain the same as the previous part.",
    "loans AS l RIGHT JOIN members AS m ON l.member_id=m.id\n-- equivalent preservation:\nmembers AS m LEFT JOIN loans AS l ON l.member_id=m.id",
    demo('left=con.execute("SELECT m.id,l.id FROM members AS m LEFT JOIN loans AS l ON l.member_id=m.id ORDER BY m.id,l.id").fetchall()\nif sqlite3.sqlite_version_info >= (3,39,0):\n    right=con.execute("SELECT m.id,l.id FROM loans AS l RIGHT JOIN members AS m ON l.member_id=m.id ORDER BY m.id,l.id").fetchall()\n    print("Equivalent:",left==right)\nelse:\n    print("RIGHT JOIN unavailable; portable LEFT JOIN used")\nprint(left)'),
    "Dipa survives as (4,None). Choosing an older compatible spelling changes neither the intended preserved members nor the matching relationship.",
    ('# Assume Python version alone guarantees RIGHT JOIN', '# Check SQLite version or use the swapped LEFT JOIN', "SQLite is a separately versioned library."),
    "Preserve every copy when joining to loans, using the portable LEFT JOIN.",
    demo('print(con.execute("SELECT b.id,l.id FROM books AS b LEFT JOIN loans AS l ON l.book_id=b.id ORDER BY b.id,l.id").fetchall())'),
    "Using the preserved-copy result, count matching events per copy, including book4with0.",
    demo('print(con.execute("SELECT b.id,COUNT(l.id) FROM books AS b LEFT JOIN loans AS l ON l.book_id=b.id GROUP BY b.id ORDER BY b.id").fetchall())'),
    "Preservation matters more than left/right spelling. Know your engine and write explicit result columns.",
    [("What does A RIGHT JOIN B preserve?", "B rows", "Only A rows", "No unmatched rows", "RIGHT identifies the preserved side."),
     ("Which portable spelling preserves members?", "members LEFT JOIN loans", "members INNER JOIN loans", "loans LEFT JOIN members", "Put the population you need on the left.")])

lesson(2, "4. GROUP BY summarises; HAVING filters groups",
    "Calculate one result per author with a clear denominator.",
    [("GROUP BY; SUM; AVG; MIN; MAX", "GROUP BY creates groups for aggregate summaries. SUM adds known values, AVG averages known values, MIN/MAX select extremes. Empty-group aggregates other than COUNT can be NULL."),
     ("HAVING; bare-column trap", "WHERE filters source rows before grouping; HAVING filters resulting groups. Select grouping columns and aggregate expressions instead of SQLite's permissive but ambiguous ungrouped bare columns.")],
    "Ask how many copies each author label has and their mean page count. Group books by author, not by copy id. "
    "Mira has two copies averaging240pages; Aya and Ken each have one. HAVING COUNT(*)>=2retains Mira. "
    "Filtering pages>=200 first changes the input population: Mira then has only the300-page copy. That is a different question. "
    "Do not select a random title beside an author mean. It does not identify a typical or longest copy unless your query explicitly defines that relationship. "
    "The author field is a label in this small schema; group results describe these recorded copies, not every work by those people.",
    "SELECT author,COUNT(*) AS copies,AVG(pages) AS mean_pages FROM books GROUP BY author HAVING COUNT(*)>=2 ORDER BY author;",
    demo('print(con.execute("SELECT author,COUNT(*),AVG(pages),MIN(pages),MAX(pages) FROM books GROUP BY author ORDER BY author").fetchall())\nprint(con.execute("SELECT author,COUNT(*) FROM books GROUP BY author HAVING COUNT(*)>=2 ORDER BY author").fetchall())'),
    "The first result summarises all recorded copies. The second asks for groups with at least two, retaining only Mira.",
    ('SELECT author,title,AVG(pages) FROM books GROUP BY author;', 'SELECT author,COUNT(*),AVG(pages) FROM books GROUP BY author;', "A bare title is not an explanation of the grouped mean."),
    "Compute total pages by author, ordered by total descending then author.",
    demo('print(con.execute("SELECT author,SUM(pages) AS total FROM books GROUP BY author ORDER BY total DESC,author").fetchall())'),
    "Filter to copies of at least200pages, then retain authors whose remaining mean is at least250.",
    demo('print(con.execute("SELECT author,COUNT(*),AVG(pages) FROM books WHERE pages>=200 GROUP BY author HAVING AVG(pages)>=250 ORDER BY author").fetchall())'),
    "WHERE changes group inputs; HAVING selects group outputs. State both populations.",
    [("Which clause filters aggregate groups?", "HAVING", "WHERE AVG(pages)>200", "LIMIT alone", "HAVING is evaluated for grouped results."),
     ("Should an arbitrary ungrouped title explain an author's mean?", "No", "Always", "If the query runs", "Permissive syntax does not make that title meaningful.")])

lesson(2, "5. Subqueries and EXISTS answer a second question",
    "Use a scalar summary and correlated existence checks appropriately.",
    [("Scalar subquery", "A query in parentheses can supply one summary value, such as the overall average. The outer query compares each row with that value."),
     ("EXISTS; NOT EXISTS; correlated subquery", "EXISTS checks whether a matching subquery returns any row. A correlated subquery references the current outer row. NOT EXISTS finds parents without matching events and avoids NOT IN's NULL trap.")],
    "Find copies longer than the catalogue average. The inner AVG produces one value; the outer WHERE compares each copy with it. "
    "For copies never borrowed, do not compare a title list. Ask whether any loan row references that copy's key. "
    "NOT EXISTS keeps book4because its correlated search finds no event. EXISTS can keep a copy once even if it has several matching events. "
    "SELECT1inside EXISTS only indicates that a match exists; it is not counting events. "
    "A subquery is not automatically faster or slower than a join. Choose correct semantics, inspect a real plan and measure realistic work when performance matters.",
    "SELECT id FROM books WHERE pages>(SELECT AVG(pages) FROM books);\nSELECT b.id FROM books AS b WHERE NOT EXISTS(SELECT 1 FROM loans AS l WHERE l.book_id=b.id);",
    demo('print("Above average:",con.execute("SELECT id FROM books WHERE pages>(SELECT AVG(pages) FROM books) ORDER BY id").fetchall())\nprint("Never borrowed:",con.execute("SELECT b.id,b.title FROM books AS b WHERE NOT EXISTS(SELECT 1 FROM loans AS l WHERE l.book_id=b.id) ORDER BY b.id").fetchall())'),
    "The average is210pages, so ids2and3qualify. Only id4has no loan history. EXISTS does not duplicate book1for its two events.",
    ('# Assume NOT IN is safe when its subquery can return NULL', 'WHERE NOT EXISTS(SELECT 1 FROM loans AS l WHERE l.book_id=b.id)', "The existence question expresses the intended key relationship directly."),
    "Find member ids with no historical loan using NOT EXISTS.",
    demo('print(con.execute("SELECT m.id FROM members AS m WHERE NOT EXISTS(SELECT 1 FROM loans AS l WHERE l.member_id=m.id) ORDER BY m.id").fetchall())'),
    "Return each copy once if it has at least one open loan.",
    demo('print(con.execute("SELECT b.id FROM books AS b WHERE EXISTS(SELECT 1 FROM loans AS l WHERE l.book_id=b.id AND l.returned_on IS NULL) ORDER BY b.id").fetchall())'),
    "Use a scalar subquery for one summary; use EXISTS for matching presence without unwanted row multiplication.",
    [("Does EXISTS count matching events?", "No; it tests presence", "Yes, all events", "Only NULL events", "It asks whether at least one row exists."),
     ("Why does NOT EXISTS keep book4?", "No loan references that copy", "Its title sorts last", "It has zero pages", "The correlated key match has no event.")])

lesson(2, "6. Three-table analysis without double-counting",
    "Reconcile book, member and event units in a readable report.",
    [("Three-table join; CASE WHEN", "Two key joins connect loans to books and members. CASE WHEN chooses an expression conditionally; SUM(CASE...) can count events satisfying a declared status rule."),
     ("SUM after a join", "A parent measurement repeats for every child match. SUM(book.pages) over loan events describes pages associated with events, not unique catalogue pages.")],
    "Join all three tables to display each event with its copy title and current member name. The event id stays in the output so its unit is visible. "
    "Catalogue pages sum to840, but summing pages after joining loans gives900because book1's180pages appears twice and unborrowed book4's120pages is absent. "
    "Neither number is inherently wrong: they answer different questions. Name the unit and do not label event-associated pages as catalogue size. "
    "SUM(DISTINCT pages) is not a general repair: two different copies can have the same page count. Aggregate at the desired key level. "
    "For member reports, include zero-event members using LEFT JOIN, count l.id and use CASE with l.id IS NOT NULL to avoid treating placeholders as open loans.",
    "SELECT l.id,b.title,m.name FROM loans AS l JOIN books AS b ON b.id=l.book_id JOIN members AS m ON m.id=l.member_id ORDER BY l.id;",
    demo('print(con.execute("SELECT l.id,b.title,m.name FROM loans AS l JOIN books AS b ON b.id=l.book_id JOIN members AS m ON m.id=l.member_id ORDER BY l.id").fetchall())\nprint("Catalogue:",con.execute("SELECT SUM(pages) FROM books").fetchone()[0])\nprint("Loan-event associated:",con.execute("SELECT SUM(b.pages) FROM loans AS l JOIN books AS b ON b.id=l.book_id").fetchone()[0])'),
    "Asha, Ben and Chandra have events, while Dipa has none. Event-associated pages900must not be reported as840catalogue pages.",
    ('SELECT SUM(DISTINCT b.pages) -- assume unique copies', 'SELECT SUM(pages) FROM books; -- catalogue unit', "Distinct values are not distinct entity keys."),
    "Return every member's total events and open events, including Dipa with zeros.",
    demo('query="""SELECT m.id,m.name,COUNT(l.id),\nSUM(CASE WHEN l.id IS NOT NULL AND l.returned_on IS NULL THEN 1 ELSE 0 END)\nFROM members AS m LEFT JOIN loans AS l ON l.member_id=m.id\nGROUP BY m.id,m.name ORDER BY m.id"""\nprint(con.execute(query).fetchall())'),
    "Count distinct copies ever borrowed and compare with total catalogue copies.",
    demo('print("Ever borrowed:",con.execute("SELECT COUNT(DISTINCT book_id) FROM loans").fetchone()[0])\nprint("Catalogue:",con.execute("SELECT COUNT(*) FROM books").fetchone()[0])'),
    "Keep entity keys in mind through every join. Reconcile report counts with independent source-table counts.",
    [("What is SUM(pages) over loan matches measuring?", "Pages associated with loan events", "Unique catalogue pages automatically", "Member ages", "A copy's pages repeat for each matched event."),
     ("Why include l.id IS NOT NULL in the open CASE?", "Exclude unmatched placeholders", "Hide real open events", "Disable foreign keys", "A placeholder's return date is also NULL.")])

lesson(3, "1. Connections, cursors and predictable resource cleanup",
    "Read results safely and close connections even when an operation fails.",
    [("Cursor; fetchone; fetchmany; iteration", "A cursor tracks a result stream. fetchone returns one remaining row or None; fetchmany(n) returns up to n rows; iteration processes remaining rows without building one huge list."),
     ("sqlite3.Row; row_factory; contextlib.closing", "Set row_factory to sqlite3.Row before executing queries to access columns by name. closing(con) guarantees close on scope exit; a connection's own with block manages transactions, not closure.")],
    "A connection represents your access to a database. A cursor represents a statement's result position. Reading consumes that position. "
    "fetchall after fetchone returns only what remains, not the original full result again. Execute the query anew when you need a new result stream. "
    "Row objects allow row['title'] instead of remembering a tuple offset. Give computed columns readable aliases. "
    "Use contextlib.closing to release connections reliably. A plain with con block is not a promise to close the connection. "
    "Our explicit transaction policy still applies: closing releases resources, while COMMIT or ROLLBACK decides grouped write outcomes.",
    'with closing(sqlite3.connect(":memory:", isolation_level=None)) as con:\n    con.row_factory=sqlite3.Row\n    row=con.execute("SELECT 1 AS value").fetchone()',
    demo('con.row_factory=sqlite3.Row\ncur=con.execute("SELECT id,title FROM books ORDER BY id")\nfirst=cur.fetchone()\nprint("First:",first["id"],first["title"])\nprint("Next batch:",[r["id"] for r in cur.fetchmany(2)])\nprint("Remainder:",[r["id"] for r in cur])'),
    "The first read consumes id1; fetchmany consumes2and3; iteration yields4. None would mean no remaining row, not a row whose column happens to be NULL.",
    ('with con:\n    pass  # assume closed', 'with closing(con):\n    pass  # always closed on exit', "Connection context management and closing solve different problems."),
    "Fetch a nonexistent copy id99; handle None before indexing it.",
    demo('row=con.execute("SELECT title FROM books WHERE id=99").fetchone()\nprint("Not found" if row is None else row[0])'),
    "Use closing for a new temporary connection and a named-column result.",
    '''import sqlite3
from contextlib import closing
with closing(sqlite3.connect(":memory:", isolation_level=None)) as con:
    con.row_factory=sqlite3.Row
    row=con.execute("SELECT 7 AS total").fetchone()
    print(row["total"])
print("Connection scope finished")''',
    "A cursor has position; a connection has lifetime; a transaction has a commit boundary. Keep those three ideas separate.",
    [("What remains after fetchone consumes id1?", "Rows2,3,4", "All four rows again", "No rows", "The cursor advances when rows are fetched."),
     ("Does with con automatically close it?", "No", "Always", "Only after SELECT", "Use closing or finally for resource closure.")])

lesson(3, "2. Bind values; never assemble user input into SQL",
    "Use qmark and named parameters while keeping identifiers controlled.",
    [("Parameter binding; qmark; named parameters", "Use ? with a sequence or :name with a dict. The driver sends values separately from SQL structure. A single-item tuple needs a comma: (value,)."),
     ("SQL injection; identifier allowlist", "Concatenated input can become SQL syntax. Parameters bind values, not table names, column names or ASC/DESC. Select identifiers from a fixed trusted mapping instead.")],
    "A search term can contain apostrophes without being a command. Binding treats the entire value as data, including text that resembles OR1=1. "
    "Do not place quotes around the ? placeholder. The driver handles representation and escaping for the bound value. "
    "execute accepts one statement, but that alone is not injection protection: changing a WHERE expression inside one SELECT is already harmful. "
    "The example passes a hostile-looking title to a bound equality query. It matches no rows, while all four stored copies remain. "
    "Keep SQL structure fixed. If a user selects a sort option, translate it through a developer-owned allowlist rather than binding ORDER BY ? or concatenating arbitrary input.",
    'con.execute("SELECT id FROM books WHERE title=?", (title,))\ncon.execute("SELECT id FROM books WHERE pages>=:minimum", {"minimum":200})',
    demo('title="x\' OR 1=1 --"\nprint("Bound result:",con.execute("SELECT id FROM books WHERE title=?", (title,)).fetchall())\nprint("Catalogue intact:",con.execute("SELECT COUNT(*) FROM books").fetchone()[0])\nprint("Named:",con.execute("SELECT id FROM books WHERE pages>=:minimum ORDER BY id",{"minimum":200}).fetchall())'),
    "The malicious-looking text is a title value. It does not become a WHERE clause. Named and qmark styles both separate values from statement syntax.",
    ('query="SELECT id FROM books WHERE title=\\\'"+title+"\\\'"', 'con.execute("SELECT id FROM books WHERE title=?", (title,))', "Data belongs in bound parameters, not SQL construction."),
    "Insert and find a title containing an apostrophe using bound parameters for every value.",
    demo('title="A Reader\'s Guide"\ncon.execute("INSERT INTO books VALUES(?,?,?,?)",(5,title,"Aya",150))\nprint(con.execute("SELECT id,title FROM books WHERE title=?",(title,)).fetchall())'),
    "Map a user sort label to a trusted SQL fragment and sort the result.",
    demo('allowed={"longest":"pages DESC,id","title":"title,id"}\nchoice="longest"\nif choice not in allowed:\n    raise ValueError("Unknown sort option")\nquery="SELECT id,title FROM books ORDER BY "+allowed[choice]\nprint(con.execute(query).fetchall())'),
    "Bind values on every path. Controlled identifiers require a fixed allowlist; binding is not encryption or authentication.",
    [("Can ? stand for a table name?", "No", "Always", "Only in SELECT", "Placeholders bind values, not SQL identifiers."),
     ("Which is a one-value parameter tuple?", "(title,)", "(title)", "title+", "The comma creates the tuple; parentheses alone do not.")])

lesson(3, "3. A small search interface with useful failure messages",
    "Separate input validation, query execution and missing-result handling.",
    [("Interface boundary; literal LIKE escaping", "Validate an input's meaning before querying. To promise literal substring search, escape backslash, % and _ and declare ESCAPE explicitly; still bind the resulting pattern."),
     ("OperationalError versus IntegrityError", "OperationalError can report an inaccessible/locked database or invalid SQL; IntegrityError indicates a constraint violation. Do not disguise either as an empty search result.")],
    "A function should express a user task rather than expose arbitrary SQL. find_books(term) accepts a bounded nonempty string and returns selected fields. "
    "If the interface says literal substring, SQL Garden should be searchable without making % mean all titles. Escape pattern characters, then bind the pattern. "
    "An empty result is a legitimate answer to a successful query. A syntax error or unreadable file is not the same answer. "
    "Validate before writing; use constraints for shared rules; catch expected failures at the interface boundary. Let unexpected coding errors remain visible during development. "
    "The solution is local and offline. It needs no token and no network. None of this moves your website's notes into a database.",
    'pattern="%"+escaped_term+"%"\ncon.execute("SELECT id,title FROM books WHERE title LIKE ? ESCAPE \'\\\\\'", (pattern,))',
    demo(r'''def find_books(term):
    term=term.strip()
    if not 1<=len(term)<=80:
        raise ValueError("Search requires1–80characters")
    escaped=term.replace("\\","\\\\").replace("%","\\%").replace("_","\\_")
    return con.execute("SELECT id,title FROM books WHERE title LIKE ? ESCAPE '\\' ORDER BY id",("%"+escaped+"%",)).fetchall()
print(find_books("SQL"))
print(find_books("%"))'''),
    "SQL matches SQL Garden. A literal percent matches nothing in this fixture, rather than all four books. The SQL statement remains fixed and the pattern remains bound.",
    ('except sqlite3.Error:\n    return []  # claim no matches', '# Report query failure distinctly from a successful empty result', "A failed query did not establish that no records match."),
    "Implement exact-id lookup that returns a title or a clear not-found message; reject nonpositive ids.",
    demo('def title_for(book_id):\n    if type(book_id) is not int or book_id<=0:\n        raise ValueError("Positive integer ID required")\n    row=con.execute("SELECT title FROM books WHERE id=?",(book_id,)).fetchone()\n    return "Not found" if row is None else row[0]\nprint(title_for(1));print(title_for(99))'),
    "Show that a malformed fixed SQL statement raises an operational failure instead of quietly becoming an empty result.",
    demo('try:\n    con.execute("SELECT missing_column FROM books").fetchall()\nexcept sqlite3.OperationalError:\n    print("Query failed: inspect SQL; this is not a no-match result")'),
    "Define the interface's search semantics, bind data and report failures honestly.",
    [("Is a database error equivalent to no matching rows?", "No", "Always", "For small tables", "The failed query has not answered the question."),
     ("Does a literal percent search mean all books here?", "No", "Always", "Only for TEXT", "The interface escapes LIKE wildcard characters.")])

lesson(3, "4. File persistence and opening the intended database",
    "Reopen committed data and avoid creating empty files on path mistakes.",
    [("Database file; URI mode=rw/mode=ro", "A file path persists committed data after close. SQLite URI mode=rw opens an existing database without creating one; mode=ro opens read-only. uri=True enables URI interpretation."),
     ("Path.resolve; as_uri; TemporaryDirectory", "resolve creates an absolute path, as_uri encodes it as a file URI and TemporaryDirectory owns a disposable test folder. On Windows it handles drive letters and spaces correctly.")],
    "sqlite3.connect('typo.db') normally creates a new empty database if that path does not exist. A later 'no such table' can hide the original path mistake. "
    "Create a new database only in an explicit initialisation step. Routine operations should open an existing owned file with mode=rw or mode=ro. "
    "This example writes a row, closes the connection and reopens it read-only. The chosen automatic-statement transaction policy commits the write before close. "
    "The temporary folder is for reproducible practice, not a suggested home for long-term data. Choose a stable local folder for your own project. "
    "A file database is local persistence, not automatic cross-device sync or password secrecy. Study Hub's existing browser sync remains separate.",
    'uri=Path("library.db").resolve().as_uri()+"?mode=rw"\ncon=sqlite3.connect(uri,uri=True,isolation_level=None)',
    '''import sqlite3
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory
with TemporaryDirectory() as folder:
    path=Path(folder)/"practice.db"
    with closing(sqlite3.connect(path,isolation_level=None)) as con:
        con.execute("CREATE TABLE notes(id INTEGER PRIMARY KEY,body TEXT)")
        con.execute("INSERT INTO notes VALUES(?,?)",(1,"Keep learning"))
    with closing(sqlite3.connect(path.as_uri()+"?mode=ro",uri=True,isolation_level=None)) as con:
        print(con.execute("SELECT body FROM notes WHERE id=?",(1,)).fetchone()[0])
    print("Persisted after close:",path.exists())''',
    "The second connection reads the committed row from the same file. The path exists until the owned temporary folder is cleaned up.",
    ('sqlite3.connect("probably-the-right-name.db")  # may create a typo file', 'sqlite3.connect(path.as_uri()+"?mode=rw",uri=True)', "Existing-file mode turns a wrong path into a visible failure."),
    "Attempt mode=rw on a nonexistent path; show that the operation fails and no new file appears.",
    '''import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory
with TemporaryDirectory() as folder:
    path=Path(folder)/"missing.db"
    try:
        sqlite3.connect(path.as_uri()+"?mode=rw",uri=True)
    except sqlite3.OperationalError:
        print("Missing database refused")
    print("File created:",path.exists())''',
    "Create a file, reopen read-only and show that an INSERT is rejected.",
    '''import sqlite3
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory
with TemporaryDirectory() as folder:
    path=Path(folder)/"practice.db"
    with closing(sqlite3.connect(path,isolation_level=None)) as con:
        con.execute("CREATE TABLE demo(value INTEGER)")
    with closing(sqlite3.connect(path.as_uri()+"?mode=ro",uri=True)) as con:
        try:
            con.execute("INSERT INTO demo VALUES(1)")
        except sqlite3.OperationalError:
            print("Read-only write rejected")''',
    "Creating a database and opening an existing one are different intentions. Make the path and mode explicit.",
    [("Can a normal connect('typo.db') create a new file?", "Yes", "Never", "Only online", "Creation is the normal behaviour when a file is absent."),
     ("Does mode=ro allow INSERT?", "No", "Always", "Only for one row", "It opens the database read-only.")])

lesson(3, "5. Back up a live database with the database API",
    "Produce a separate consistent SQLite backup and verify its contents.",
    [("Connection.backup", "source.backup(target) copies an SQLite database through SQLite's backup API. It handles database state more appropriately than copying an arbitrary live file, especially when journal/WAL files are involved."),
     ("Exclusive destination; recovery drill", "Create a new destination with an exclusive operation so an existing backup cannot be silently replaced. Reopen the copy and verify expected schema, counts and a sample query.")],
    "A backup is useful only if you can open and verify it. Use the SQLite backup API with a separate destination and close both connections. "
    "Blindly copying one active .db file may omit state associated with write-ahead logging or capture an unsuitable moment. The API operates through SQLite. "
    "A real backup interface must refuse an existing destination before opening it for writing. The project reserves the destination exclusively and removes only its own failed new file. "
    "The example backs up an in-memory fixture to a new temporary file, then verifies four loan rows. "
    "This is a backup of the standalone Python library. Study Hub's existing JSON backup/import remains the right tool for its browser learning progress.",
    "source.backup(target)\n# Close, reopen the copy and verify a known query.",
    demo('from contextlib import closing\nfrom pathlib import Path\nfrom tempfile import TemporaryDirectory\nwith TemporaryDirectory() as folder:\n    path=Path(folder)/"backup.db"\n    with path.open("xb"):\n        pass\n    with closing(sqlite3.connect(path,isolation_level=None)) as target:\n        con.backup(target)\n    with closing(sqlite3.connect(path)) as check:\n        print("Backup loans:",check.execute("SELECT COUNT(*) FROM loans").fetchone()[0])'),
    "The source stays open while SQLite creates the copy. A new connection reads the verified backup independently.",
    ('# Overwrite a previous backup without checking', 'with destination.open("xb"):\n    pass  # refuse if already present', "A new backup should not erase the previous recovery point."),
    "Back up the fixture and verify the first title in the copy.",
    demo('from contextlib import closing\nfrom pathlib import Path\nfrom tempfile import TemporaryDirectory\nwith TemporaryDirectory() as folder:\n    path=Path(folder)/"copy.db"\n    with closing(sqlite3.connect(path)) as target:\n        con.backup(target)\n    with closing(sqlite3.connect(path)) as check:\n        print(check.execute("SELECT title FROM books WHERE id=1").fetchone()[0])'),
    "Demonstrate that exclusive creation refuses a previously saved backup marker without changing its bytes.",
    '''from pathlib import Path
from tempfile import TemporaryDirectory
with TemporaryDirectory() as folder:
    path=Path(folder)/"existing-backup"
    path.write_bytes(b"previous recovery point")
    try:
        with path.open("xb"):
            pass
    except FileExistsError:
        print("Existing backup preserved")
    print(path.read_bytes()==b"previous recovery point")''',
    "Use the backup API, protect existing destinations and test a restore query.",
    [("What should follow creation of a backup?", "Reopen and verify it", "Delete the source immediately", "Assume no errors forever", "A recovery point needs a recovery check."),
     ("Does this library backup replace Study Hub JSON backup?", "No", "Always", "Only for Japanese", "They store separate applications and data formats.")])

lesson(4, "1. Read a focused SQL result into pandas",
    "Move only the result needed for an analysis into a DataFrame.",
    [("pd.read_sql_query; params", "pandas.read_sql_query executes a SELECT and builds a DataFrame from the result. params passes values through the database driver's binding mechanism; it does not interpolate SQL strings."),
     ("SQL pushdown", "Filtering, selecting and aggregating in SQL before transfer is pushdown. It can reduce memory and transfer work, but performance still depends on data, indexes and the query.")],
    "pandas and SQL are complementary tools. Keep relational filtering and large group summaries close to stored data; use pandas for suitable in-memory transformations and presentation. "
    "The example requests only long-copy ids, titles and pages. It binds minimum200through params and orders explicitly. "
    "read_sql_query returns a DataFrame, not a live editable database table. Changing that frame does not automatically update SQLite. "
    "Use to_dict('records') to display a stable list of row dictionaries, avoiding display-width differences in terminal table formatting. "
    "The analysis connection can be read-only when no writes are required. pandas needs an initial installation; the supplied Python sqlite3 project itself uses only the standard library.",
    'df=pd.read_sql_query("SELECT id,title,pages FROM books WHERE pages>=? ORDER BY id",con,params=(200,))',
    demo('import pandas as pd\nframe=pd.read_sql_query("SELECT id,title,pages FROM books WHERE pages>=? ORDER BY id",con,params=(200,))\nprint(frame.to_dict("records"))\nframe.loc[frame["id"].eq(2),"pages"]=999\nprint("Stored pages:",con.execute("SELECT pages FROM books WHERE id=2").fetchone()[0])'),
    "The frame has copies2and3. Editing its copy2value to999does not change the database, which remains240pages.",
    ('query=f"SELECT * FROM books WHERE pages>={minimum}"', 'pd.read_sql_query("SELECT id,pages FROM books WHERE pages>=?",con,params=(minimum,))', "Bind supplied values and select only needed columns."),
    "Read only copies by Mira using params, and print ordered id/title dictionaries.",
    demo('import pandas as pd\nframe=pd.read_sql_query("SELECT id,title FROM books WHERE author=? ORDER BY id",con,params=("Mira",))\nprint(frame.to_dict("records"))'),
    "Request the mean pages per author in SQL and receive the aggregate DataFrame.",
    demo('import pandas as pd\nframe=pd.read_sql_query("SELECT author,COUNT(*) AS copies,AVG(pages) AS mean_pages FROM books GROUP BY author ORDER BY author",con)\nprint(frame.to_dict("records"))'),
    "A query result is a DataFrame snapshot. Choose where to compute and keep input values bound.",
    [("Does editing the returned DataFrame update SQLite automatically?", "No", "Always", "Only numeric columns", "A separate write operation is required."),
     ("How are supplied values passed to read_sql_query?", "params", "String concatenation", "A password in SQL", "params uses the database binding mechanism.")])

lesson(4, "2. SQL NULL and pandas missing values need explicit dtypes",
    "Preserve nullable counts and avoid silently losing missing groups.",
    [("dtype; nullable Int64; parse_dates", "read_sql_query accepts dtype mappings and parse_dates. pandas Int64 supports missing integer values, unlike a plain NumPy integer array. Date parsing is an explicit interpretation of SQL text."),
     ("groupby dropna=False; size versus count", "pandas groupby normally drops missing grouping keys. dropna=False retains them. size counts rows, while count counts known values, mirroring SQL COUNT(*) versus COUNT(column).")],
    "SQL NULL arrives as a pandas missing value whose representation depends on dtype and conversion. Inspect the intended meaning, not just the printed token. "
    "Here returned_on is a date string or NULL. parse_dates turns known strings into timestamps and missing dates into NaT; it does not invent a return date. "
    "An open event has no return date, so count(returned_on) is not the open count. Use isna to count open events under this schema. "
    "If grouping by a field that can be NULL, match SQL semantics with dropna=False. Otherwise pandas may silently omit an unknown group. "
    "The synthetic scores exercise below is deliberately separate from the fictional library, so no one mistakes score missingness for a library fact.",
    'pd.read_sql_query(query,con,dtype={"id":"Int64"},parse_dates=["returned_on"])\nframe.groupby("group",dropna=False)["value"].agg(["size","count"])',
    demo('import pandas as pd\nframe=pd.read_sql_query("SELECT id,returned_on FROM loans ORDER BY id",con,dtype={"id":"Int64"},parse_dates=["returned_on"])\nprint("Nullable id:",str(frame["id"].dtype))\nprint("Events:",len(frame),"Known returns:",int(frame["returned_on"].notna().sum()),"Open:",int(frame["returned_on"].isna().sum()))'),
    "All four rows remain. Two dates are known and two are missing. A parsed date column is an analysis choice; the source still stores the declared ISO strings.",
    ('frame.groupby("group")  # assume NULL group retained', 'frame.groupby("group",dropna=False)', "Default pandas grouping differs from SQL NULL grouping."),
    "Read loan ids and member ids with explicit nullable integer dtypes; count events per member in pandas.",
    demo('import pandas as pd\nframe=pd.read_sql_query("SELECT id,member_id FROM loans ORDER BY id",con,dtype={"id":"Int64","member_id":"Int64"})\nprint(frame.groupby("member_id",dropna=False).size().to_dict())'),
    "Use a synthetic nullable grouping field and prove both SQL and pandas retain three rows when missing groups are included.",
    demo('import pandas as pd\ncon.executescript("CREATE TABLE scores(team TEXT,value INTEGER); INSERT INTO scores VALUES(\'A\',1),(\'A\',NULL),(NULL,3);")\nframe=pd.read_sql_query("SELECT team,value FROM scores",con)\nprint("SQL",con.execute("SELECT team,COUNT(*),COUNT(value) FROM scores GROUP BY team ORDER BY team").fetchall())\nprint("pandas grouped rows",int(frame.groupby("team",dropna=False).size().sum()))'),
    "Align missing-value and grouping semantics before claiming SQL and pandas agree.",
    [("Does groupby retain missing keys by default?", "No", "Always", "Only integers", "Use dropna=False when the missing group belongs in the population."),
     ("What counts known return dates in pandas?", "returned_on.notna().sum()", "len(frame) always", "The largest loan id", "A known-date count excludes missing dates.")])

lesson(4, "3. to_sql is a transfer tool, not schema management",
    "Export a new staging table without replacing constrained application tables.",
    [("DataFrame.to_sql; index=False", "to_sql writes a DataFrame to a SQL table. index=False avoids exporting pandas' index as an extra column. if_exists='fail' refuses an existing table."),
     ("fail; append; replace; raw sqlite3 transaction caveat", "append inserts into an existing table; replace drops and recreates it, losing its former schema rules and indexes. With a raw sqlite3 connection, pandas' to_sql insertion cannot be rolled back as part of your outer operation; do not rely on it for a larger atomic migration/import.")],
    "pandas can create a convenient staging table for analysis. It is not the owner of the application's schema history. "
    "Write a new imported_books table with if_exists='fail' and index=False, then inspect the exported columns. "
    "Do not call replace on books or loans: generated inferred tables do not preserve your carefully declared foreign keys, checks or indexes. "
    "For a validated atomic import into managed tables, use bound executemany inside an explicit sqlite3 transaction, as Day6 demonstrates. "
    "append is also a write: duplicate keys or wrong values must still be considered. A working small demonstration is not evidence of all-or-nothing behaviour across a multi-step pandas workflow.",
    'frame.to_sql("imported_books",con,if_exists="fail",index=False)\n# Use managed SQL migrations and transactions for application tables.',
    demo('import pandas as pd\nframe=pd.DataFrame({"id":[10,11],"title":["Tables First","Query Practice"]})\nframe.to_sql("imported_books",con,if_exists="fail",index=False)\nprint(con.execute("SELECT id,title FROM imported_books ORDER BY id").fetchall())\nprint([r[1] for r in con.execute("PRAGMA table_info(imported_books)")])'),
    "The export has only id and title because the pandas index was not written. It is a separate staging table, not a replacement library schema.",
    ('frame.to_sql("books",con,if_exists="replace")', 'frame.to_sql("new_analysis_stage",con,if_exists="fail",index=False)', "Replacing an application table can discard its rules and data."),
    "Export a fresh one-row staging frame, then refuse a second write with the same table name.",
    demo('import pandas as pd\nframe=pd.DataFrame({"value":[7]})\nframe.to_sql("stage",con,if_exists="fail",index=False)\ntry:\n    frame.to_sql("stage",con,if_exists="fail",index=False)\nexcept ValueError:\n    print("Existing staging table refused")\nprint(con.execute("SELECT value FROM stage").fetchall())'),
    "Create a constrained SQL table yourself and use bound executemany to insert rows from a DataFrame.",
    demo('import pandas as pd\nframe=pd.DataFrame({"id":[10,11],"pages":[100,200]})\ncon.execute("CREATE TABLE imported_counts(id INTEGER PRIMARY KEY,pages INTEGER NOT NULL CHECK(pages>0))")\nrows=list(frame.itertuples(index=False,name=None))\ncon.executemany("INSERT INTO imported_counts(id,pages) VALUES(?,?)",rows)\nprint(con.execute("SELECT id,pages FROM imported_counts ORDER BY id").fetchall())'),
    "Use pandas for intentional transfer; keep managed constraints, migrations and transaction boundaries under explicit control.",
    [("What is dangerous about to_sql(if_exists='replace') on books?", "It drops and recreates the table", "It only changes display colours", "It guarantees every constraint remains", "Recreating inferred schema can erase managed rules."),
     ("Does raw sqlite3 to_sql promise rollback inside your larger operation?", "No", "Always", "Only with index=False", "Use explicit SQL transaction imports for the managed atomic operation.")])

lesson(4, "4. Reproduce the same analysis in SQL and pandas",
    "Check values, ordering and denominators before comparing tools.",
    [("Semantic parity; assert_frame_equal", "Two analyses agree only when they use the same source, row filters, NULL rules, grouping, ordering and dtypes. pandas.testing.assert_frame_equal checks the resulting tables."),
     ("Aggregate before transfer", "A database GROUP BY can return one row per group instead of every event. pandas can perform the same task after transfer; compare equivalent work, not mismatched populations.")],
    "We have already summarised copies by author in SQL. Now reproduce count, mean and total pages in pandas from the same four rows. "
    "Use identical output column names and ordering, and deliberately align integer/real dtypes before equality assertions. "
    "If results disagree, inspect filters and denominators first. A fast wrong query is not an optimisation. "
    "A separate member-count exercise retains zero-loan members by reindexing onto the member population; a loans-only groupby does not invent Dipa's zero. "
    "For large tables, returning group summaries can greatly reduce transfer. For small data, Python and driver overhead may dominate, so do not promise a universal winner.",
    'sql=pd.read_sql_query("SELECT author,COUNT(*) AS copies,AVG(pages) AS mean_pages,SUM(pages) AS total_pages FROM books GROUP BY author ORDER BY author",con)',
    demo('import pandas as pd\nsql=pd.read_sql_query("SELECT author,COUNT(*) AS copies,AVG(pages) AS mean_pages,SUM(pages) AS total_pages FROM books GROUP BY author ORDER BY author",con)\nraw=pd.read_sql_query("SELECT author,pages FROM books",con)\npy=raw.groupby("author",as_index=False).agg(copies=("pages","size"),mean_pages=("pages","mean"),total_pages=("pages","sum")).sort_values("author").reset_index(drop=True)\npd.testing.assert_frame_equal(sql,py)\nprint("Same analysis:",True)\nprint(sql.to_dict("records"))'),
    "Both tools answer the same copy-level question. The assertion checks full ordered tables, not just a matching grand total.",
    ('# Compare a loans-only groupby with an all-members LEFT JOIN', '# Align the parent population, null rules and keys first', "A missing zero-event group is a population difference."),
    "Compare the SQL total catalogue pages with pandas' sum over the same copies.",
    demo('import pandas as pd\nframe=pd.read_sql_query("SELECT id,pages FROM books ORDER BY id",con)\nsql=con.execute("SELECT SUM(pages) FROM books").fetchone()[0]\nprint(int(frame["pages"].sum()),sql,int(frame["pages"].sum())==sql)'),
    "Produce all member loan counts in pandas, reindexing to member ids1through4and filling absent event counts with0.",
    demo('import pandas as pd\nmembers=pd.read_sql_query("SELECT id FROM members ORDER BY id",con)\nloans=pd.read_sql_query("SELECT member_id FROM loans",con)\ncounts=loans.groupby("member_id").size().reindex(members["id"],fill_value=0)\nprint(counts.to_dict())\nprint(con.execute("SELECT m.id,COUNT(l.id) FROM members AS m LEFT JOIN loans AS l ON l.member_id=m.id GROUP BY m.id ORDER BY m.id").fetchall())'),
    "Choose tools after verifying semantic parity. Units and zero-event populations matter more than syntax preference.",
    [("What must match before a SQL/pandas comparison?", "Population and calculation semantics", "Only column colours", "Only row count", "NULL handling, filters, groups and order affect results."),
     ("Will a loans-only groupby include Dipa automatically?", "No", "Always", "If sorted", "The parent population must be supplied to include zero-event members.")])

lesson(4, "5. Measure equivalent work and reduce transfer",
    "Design an honest small performance experiment without universal speed claims.",
    [("perf_counter; repeat; median", "perf_counter measures elapsed time. Repeat a clearly bounded operation and summarise timings, including which data transfer and computation stages were timed."),
     ("Benchmark scope; chunksize", "Database location, cache, data size, query plan and client overhead affect timings. read_sql_query(chunksize=n) yields frames for streaming, but group means must combine sums/counts rather than averaging chunk means blindly.")],
    "Compare returning one aggregate with fetching and averaging every value. These answer the same mean but transfer different amounts of data. "
    "Use an explicit synthetic20000-row numeric table, five repeats and median elapsed seconds. Build data outside the timed region. "
    "For fairness, both functions start with a query and return the final scalar. Verify equality before interpreting timings. "
    "The printed times are one authoring run, not a target to memorise. Caches and machine load change them; this local in-memory test does not prove remote-server performance. "
    "Streaming bounds transfer batches, not necessarily every later operation's memory. For a global mean, combine total sum and count across chunks; unequal chunk sizes make mean-of-means incorrect.",
    "t0=perf_counter()\nanswer=operation()\nelapsed=perf_counter()-t0\n# Check equal answers; repeat; disclose transfer and timing boundaries.",
    '''import sqlite3
from contextlib import closing
from statistics import median
from time import perf_counter
import pandas as pd
with closing(sqlite3.connect(":memory:",isolation_level=None)) as con:
    con.execute("CREATE TABLE measurements(value INTEGER NOT NULL)")
    con.executemany("INSERT INTO measurements VALUES(?)",((i%100,) for i in range(20000)))
    def in_sql():
        return con.execute("SELECT AVG(value) FROM measurements").fetchone()[0]
    def in_pandas():
        return float(pd.read_sql_query("SELECT value FROM measurements",con)["value"].mean())
    assert in_sql()==in_pandas()==49.5
    for name,operation in [("SQL aggregate",in_sql),("Transfer+pandas",in_pandas)]:
        times=[]
        for _ in range(5):
            start=perf_counter();result=operation();times.append(perf_counter()-start)
        print(name,"answer",result,"median seconds",round(median(times),6))
    print("Transferred result rows: SQL1; pandas20000")
''',
    "The mean agrees before timing is interpreted. SQL returns one row; pandas transfers20000. Recorded durations vary when you rerun; no fixed speedup is promised.",
    ('overall=sum(chunk_means)/len(chunk_means)', 'overall=total_sum/total_known_count', "Unequal chunk sizes require weighting by known counts."),
    "Stream the library page column in chunks of3and combine sums/counts to recover mean210.",
    demo('import pandas as pd\ntotal=0;known=0\nfor chunk in pd.read_sql_query("SELECT pages FROM books ORDER BY id",con,chunksize=3):\n    total+=int(chunk["pages"].sum());known+=int(chunk["pages"].count())\nprint("Combined mean:",total/known)'),
    "Show why averaging chunk means is wrong for page chunks[180,240,300]and[120].",
    demo('import pandas as pd\nchunks=list(pd.read_sql_query("SELECT pages FROM books ORDER BY id",con,chunksize=3))\nwrong=sum(float(c["pages"].mean()) for c in chunks)/len(chunks)\nright=sum(float(c["pages"].sum()) for c in chunks)/sum(int(c["pages"].count()) for c in chunks)\nprint("Mean of means:",wrong,"Correct mean:",right)'),
    "Verify answers first; time equivalent boundaries; disclose one-run variability and transfer size.",
    [("Is one timing a universal SQL speed guarantee?", "No", "Always", "If printed to six decimals", "Environment, data, plan and cache change timings."),
     ("How do unequal chunks combine into one mean?", "Total sum divided by total known count", "Unweighted mean of chunk means", "Use only the last chunk", "Each measured row needs the intended weight.")])

lesson(5, "1. CREATE, INSERT, UPDATE and DELETE with precise targets",
    "Write explicit columns, bound values and verify affected rows.",
    [("CRUD; executemany; rowcount; lastrowid", "CRUD means create/read/update/delete. executemany repeats one bound statement for a sequence of value tuples. rowcount reports affected rows for ordinary writes; lastrowid identifies the most recent successful execute INSERT's row id."),
     ("ON DELETE RESTRICT; storage-class checks", "A restrictive relationship blocks deleting a referenced parent. CHECK(typeof(pages)='integer' AND pages>0) can supplement SQLite affinity when integer storage is required.")],
    "Reads are familiar; writes need equally clear scope. Name INSERT columns so later schema additions do not silently shift your values. "
    "Bind values even for a simple title edit. Verify rowcount is1when the task requires exactly one copy. A successful UPDATE matching zero rows did not rename a book. "
    "DELETE without WHERE affects all qualifying table rows, subject to constraints. Preview the same key predicate before deleting from a practice database. "
    "Foreign keys can preserve historical references by refusing a parent deletion; a returned loan remains history and still references its copy. "
    "executemany alone does not promise all rows are atomic under our automatic-statement policy. The next part groups dependent writes explicitly.",
    'INSERT INTO books(id,title,author,pages) VALUES(?,?,?,?);\nUPDATE books SET title=? WHERE id=?;\nDELETE FROM books WHERE id=?;',
    demo('cur=con.execute("INSERT INTO books(title,author,pages) VALUES(?,?,?)",("New Copy","Aya",160))\nnew_id=cur.lastrowid\nchanged=con.execute("UPDATE books SET title=? WHERE id=?",("Revised Copy",new_id))\nprint("Inserted id:",new_id,"Updated:",changed.rowcount)\nprint(con.execute("SELECT id,title FROM books WHERE id=?",(new_id,)).fetchall())\nprint("Deleted:",con.execute("DELETE FROM books WHERE id=?",(new_id,)).rowcount)'),
    "A new unreferenced copy gets id5, is renamed by that key and is deleted by the same key. Existing loan history stays intact.",
    ('UPDATE books SET title=?;', 'UPDATE books SET title=? WHERE id=?;', "A missing predicate changes every row, not one selected copy."),
    "Attempt to rename id99and report zero affected rows without claiming success.",
    demo('cur=con.execute("UPDATE books SET title=? WHERE id=?",("No such copy",99))\nprint("Updated:",cur.rowcount)\nprint("Unknown copy" if cur.rowcount==0 else "Renamed")'),
    "Try to delete referenced copy1and confirm it is retained.",
    demo('try:\n    con.execute("DELETE FROM books WHERE id=?",(1,))\nexcept sqlite3.IntegrityError:\n    print("Referenced copy deletion rejected")\nprint(con.execute("SELECT id FROM books WHERE id=1").fetchall())'),
    "Every write needs deliberate columns, bound values, target keys and state verification.",
    [("Does UPDATE matching zero rows prove a rename succeeded?", "No", "Always", "Only after close", "Check the affected-row count."),
     ("Does executemany alone make this policy's whole batch atomic?", "No", "Always", "If using tuples", "Explicit transaction boundaries group the statements.")])

lesson(5, "2. Transactions make a complete operation succeed or fail",
    "Commit all related writes together and roll back failed operations.",
    [("BEGIN IMMEDIATE; COMMIT; ROLLBACK", "BEGIN IMMEDIATE starts an explicit write transaction and can fail if another writer holds a conflicting lock. COMMIT saves the group; ROLLBACK reverses the group's uncommitted changes."),
     ("in_transaction; executescript caveat", "in_transaction tells whether SQLite currently has an active transaction. Under legacy transaction control executescript can commit a pending transaction before running; use individual execute calls inside explicit migrations."),
     ("ACID; writer limits", "Atomicity groups changes, consistency respects declared rules, isolation governs concurrent visibility and durability concerns committed persistence under supported storage assumptions. SQLite allows multiple readers but only one writer at a time.")],
    "A two-book import should not save its first row and then fail halfway. Under our explicit isolation_level=None policy, start a transaction before the batch. "
    "The example inserts id5then hits duplicate id1. The exception path rolls back id5too, leaving the original four books. "
    "Place COMMIT inside the try so a commit-time failure also reaches cleanup. If the engine already ended a transaction after an error, check in_transaction before issuing ROLLBACK. "
    "Do not mix arbitrary executescript calls into this boundary. Use one execute per fixed DDL statement for managed migrations. "
    "A short timeout handles waiting, not infinite retries or guaranteed availability. Keep writes short and report a locked database clearly; do not leave a transaction open while waiting for a person's input.",
    'con.execute("BEGIN IMMEDIATE")\ntry:\n    # related writes\n    con.execute("COMMIT")\nexcept BaseException:\n    if con.in_transaction: con.execute("ROLLBACK")\n    raise',
    demo('con.execute("BEGIN IMMEDIATE")\ntry:\n    con.executemany("INSERT INTO books(id,title,author,pages) VALUES(?,?,?,?)",[(5,"Good new copy","Aya",150),(1,"Duplicate key","Ken",200)])\n    con.execute("COMMIT")\nexcept sqlite3.IntegrityError:\n    if con.in_transaction:\n        con.execute("ROLLBACK")\n    print("Whole import rolled back")\nprint("Copies:",con.execute("SELECT COUNT(*) FROM books").fetchone()[0])\nprint("ID5:",con.execute("SELECT id FROM books WHERE id=5").fetchall())'),
    "The first insert happened inside the transaction but was not committed. A later failure cancels the whole import. Original setup rows were committed before this boundary.",
    ('# Catch a later error and commit the first successful row anyway', '# ROLLBACK the whole logical operation, then report failure', "Partial success violates an all-or-nothing import contract."),
    "Commit two valid new copies in one transaction and verify the count becomes6.",
    demo('con.execute("BEGIN IMMEDIATE")\ntry:\n    con.executemany("INSERT INTO books VALUES(?,?,?,?)",[(5,"New A","Aya",150),(6,"New B","Ken",160)])\n    con.execute("COMMIT")\nexcept BaseException:\n    if con.in_transaction:con.execute("ROLLBACK")\n    raise\nprint(con.execute("SELECT COUNT(*) FROM books").fetchone()[0])'),
    "Rename copy1inside a transaction, deliberately roll back and confirm its old title remains.",
    demo('con.execute("BEGIN IMMEDIATE")\ncon.execute("UPDATE books SET title=? WHERE id=?",("Temporary title",1))\ncon.execute("ROLLBACK")\nprint(con.execute("SELECT title FROM books WHERE id=1").fetchone()[0])'),
    "Choose the logical operation boundary first; keep BEGIN, writes, COMMIT and failure rollback coherent.",
    [("After a rolled-back two-row import, should its first new row remain?", "No", "Always", "If it had a title", "Atomic failure reverses all uncommitted writes in that operation."),
     ("Should COMMIT be inside the protected try?", "Yes", "Never", "Only for SELECT", "Commit itself can fail and needs a cleanup path.")])

lesson(5, "3. Indexes support lookups and enforce active-loan uniqueness",
    "Inspect access paths and distinguish a performance index from a data rule.",
    [("CREATE INDEX; EXPLAIN QUERY PLAN", "An index stores an additional search structure. EXPLAIN QUERY PLAN describes a chosen access strategy; its wording is diagnostic and can change across versions."),
     ("Composite index; partial UNIQUE index", "A composite index covers multiple keys in order. A partial index includes only rows satisfying its WHERE. UNIQUE on book_id WHERE returned_on IS NULL prevents two open loans for one copy while retaining returned history.")],
    "An index can avoid scanning every event for a selective lookup, but costs storage and write maintenance. Index measured query needs, not every column. "
    "The example uses a separate synthetic10000-event table so the plan can show a meaningful member lookup. The returned result is checked before and after indexing. "
    "Do not memorise SCAN/SEARCH wording or promise a timing improvement on every small table. Day5's timing method can compare real work on your machine. "
    "The active-loan index is different: its uniqueness is a correctness rule. Existing duplicate open rows would make its creation fail; review them instead of deleting history silently. "
    "Our fixture already has only one open event for each checked-out copy. After creating the rule, another open loan for copy1is rejected even if the Python interface forgets a precheck.",
    "CREATE INDEX events_member ON events(member_id);\nCREATE UNIQUE INDEX one_open_loan ON loans(book_id) WHERE returned_on IS NULL;",
    demo('from time import perf_counter\nfrom statistics import median\ncon.execute("CREATE TABLE events(id INTEGER PRIMARY KEY,member_id INTEGER NOT NULL)")\ncon.executemany("INSERT INTO events VALUES(?,?)",((i,i%100) for i in range(1,10001)))\nquery="SELECT COUNT(*) FROM events WHERE member_id=?"\ndef measured():\n    times=[]\n    for _ in range(7):\n        start=perf_counter()\n        answer=con.execute(query,(42,)).fetchone()[0]\n        times.append(perf_counter()-start)\n    return answer,round(median(times),6)\nprint("Before plan:",con.execute("EXPLAIN QUERY PLAN "+query,(42,)).fetchall())\nbefore,before_time=measured()\ncon.execute("CREATE INDEX events_member ON events(member_id)")\nprint("After plan:",con.execute("EXPLAIN QUERY PLAN "+query,(42,)).fetchall())\nafter,after_time=measured()\nprint("Same count:",before==after,before)\nprint("Median seconds before/after:",before_time,after_time)'),
    "The result stays 100 events. The plan changes from a scan to an indexed lookup in the verified runtime. Seven-repeat medians time query execution and fetching the final count, excluding index creation. Times, plan wording and diagnostic ids can vary; this is not a universal speed guarantee.",
    ('# Assume all indexes guarantee a fixed speedup', '# Check equal results, inspect plan, repeat timings on realistic data', "An index is an access option with maintenance costs."),
    "Create the partial unique active-loan rule; attempt a second open loan for copy1and prove it is rejected.",
    demo('con.execute("CREATE UNIQUE INDEX one_open_loan ON loans(book_id) WHERE returned_on IS NULL")\ntry:\n    con.execute("INSERT INTO loans(book_id,member_id,borrowed_on) VALUES(?,?,?)",(1,3,"2026-01-11"))\nexcept sqlite3.IntegrityError:\n    print("Already checked out: rejected")\nprint(con.execute("SELECT COUNT(*) FROM loans").fetchone()[0])'),
    "Use the same rule, return current loan2, then borrow copy1again successfully.",
    demo('con.execute("CREATE UNIQUE INDEX one_open_loan ON loans(book_id) WHERE returned_on IS NULL")\ncon.execute("BEGIN IMMEDIATE")\ntry:\n    con.execute("UPDATE loans SET returned_on=? WHERE id=?",("2026-01-11",2))\n    con.execute("INSERT INTO loans(book_id,member_id,borrowed_on) VALUES(?,?,?)",(1,3,"2026-01-12"))\n    con.execute("COMMIT")\nexcept BaseException:\n    if con.in_transaction:con.execute("ROLLBACK")\n    raise\nprint(con.execute("SELECT id,returned_on FROM loans WHERE book_id=1 ORDER BY id").fetchall())'),
    "Measure performance indexes; enforce uniqueness rules at the database boundary when they define valid state.",
    [("Does the partial unique index forbid historical repeated loans?", "No", "Always", "Only for member1", "Only rows with returned_on IS NULL participate."),
     ("What must remain the same after adding a performance index?", "Query meaning and results", "Diagnostic plan text", "Measured nanoseconds", "An access-path change must not change the answer.")])

lesson(5, "4. Migrations change a known schema without erasing history",
    "Apply a versioned, transactional schema change and preserve old rows.",
    [("Migration; ALTER TABLE ADD COLUMN; PRAGMA user_version", "A migration is a reviewed change from one known schema version to another. user_version is an application-controlled integer marker, not proof that an arbitrary database has the expected shape."),
     ("Version check; backup before migration", "Inspect the owned schema and current version, create a separate backup, then change schema and version in the same transaction. Refuse unknown versions instead of guessing.")],
    "Suppose version1needs a loan note. Dropping and recreating loans would risk destroying history and its relationships. "
    "ALTER TABLE ADD COLUMN note TEXT NOT NULL DEFAULT '' preserves existing rows and gives them a defined initial value. "
    "The project validates its expected column shape, begins an explicit transaction, adds the column and supporting index, and advances user_version to2only on success. "
    "A repeat at version2is a deliberate no-op. An unknown version stops for review. The marker is not a licence to alter any file that happens to contain the number1. "
    "Make a verified backup before changing your own persistent database. These examples only change disposable fixtures; website localStorage has no migration in this task.",
    "BEGIN IMMEDIATE;\nALTER TABLE loans ADD COLUMN note TEXT NOT NULL DEFAULT '';\nPRAGMA user_version=2;\nCOMMIT;",
    demo('con.execute("PRAGMA user_version=1")\ncon.execute("BEGIN IMMEDIATE")\ntry:\n    con.execute("ALTER TABLE loans ADD COLUMN note TEXT NOT NULL DEFAULT \'\'")\n    con.execute("CREATE INDEX loans_member_date ON loans(member_id,borrowed_on)")\n    con.execute("PRAGMA user_version=2")\n    con.execute("COMMIT")\nexcept BaseException:\n    if con.in_transaction:con.execute("ROLLBACK")\n    raise\nprint("Version:",con.execute("PRAGMA user_version").fetchone()[0])\nprint("Preserved events:",con.execute("SELECT id,note FROM loans ORDER BY id").fetchall())'),
    "All four events remain with empty notes. Schema and marker change in the same transaction; no table is dropped.",
    ('DROP TABLE loans; -- recreate and hope history survives', "ALTER TABLE loans ADD COLUMN note TEXT NOT NULL DEFAULT '';", "An additive migration preserves existing events and key relationships."),
    "Start a migration, add a column, deliberately trigger a duplicate-column error and roll back. Confirm the added column and version change did not survive.",
    demo('con.execute("PRAGMA user_version=1")\ncon.execute("BEGIN IMMEDIATE")\ntry:\n    con.execute("ALTER TABLE loans ADD COLUMN note TEXT")\n    con.execute("ALTER TABLE loans ADD COLUMN note TEXT")\n    con.execute("PRAGMA user_version=2")\n    con.execute("COMMIT")\nexcept sqlite3.OperationalError:\n    if con.in_transaction:con.execute("ROLLBACK")\n    print("Migration rolled back")\nprint("Version:",con.execute("PRAGMA user_version").fetchone()[0])\nprint("Has note:",any(r[1]=="note" for r in con.execute("PRAGMA table_info(loans)")))'),
    "Refuse schema version99before any schema changes, proving that data remains.",
    demo('con.execute("PRAGMA user_version=99")\nversion=con.execute("PRAGMA user_version").fetchone()[0]\nif version not in (1,2):\n    print("Unknown version refused")\nprint("Events retained:",con.execute("SELECT COUNT(*) FROM loans").fetchone()[0])'),
    "Versioned migrations preserve evidence: inspect, back up, apply one known step atomically and verify retained records.",
    [("Is user_version alone proof of the right schema?", "No", "Always", "If it equals1", "The marker belongs to the application and can be set independently."),
     ("Should a failed migration advance the version?", "No", "Always", "Only when adding columns", "The schema change and marker must succeed together.")])

lesson(5, "5. Import CSV through validation and one transaction",
    "Preserve raw input and reject a partial import.",
    [("CSV boundary; DictReader versus strict row checks", "A CSV import needs a declared header, widths, encoding and allowed values. Parse and validate the entire bounded teaching input before managed writes; then insert with parameters in one transaction."),
     ("Idempotency policy; duplicate rejection", "This project's import is insert-only: existing IDs fail the whole import. It is not an upsert or a repeat-safe merge. Choose such behaviour explicitly; never silently replace existing rows.")],
    "A successful parser is not enough to establish valid book records. Require id,title,author,pages, bounded nonempty text, positive integer ids and valid page counts. "
    "The project accepts UTF-8 or UTF-8 BOM, at most1MiB and10000records. It rejects ragged rows, duplicate incoming ids, unsupported numeric tokens and empty required text. "
    "It preserves accepted title/author text rather than silently trimming it during import. The source file is never rewritten. "
    "Even after validation, an id may collide with a stored copy. Bound executemany runs inside one transaction so that collision cannot leave an earlier new row behind. "
    "The compact example focuses on collision rollback using a fixed validated in-memory CSV; the downloadable project's parser implements the full boundary contract.",
    "validated_rows=parse_books_csv(raw_bytes)\nwith transaction(con):\n    con.executemany('INSERT INTO books(id,title,author,pages) VALUES(?,?,?,?)',validated_rows)",
    demo('import csv,io\ntext="id,title,author,pages\\n5,Good New Copy,Aya,150\\n1,Existing ID,Ken,160\\n"\nrecords=list(csv.DictReader(io.StringIO(text)))\nrows=[(int(r["id"]),r["title"],r["author"],int(r["pages"])) for r in records]\ncon.execute("BEGIN IMMEDIATE")\ntry:\n    con.executemany("INSERT INTO books(id,title,author,pages) VALUES(?,?,?,?)",rows)\n    con.execute("COMMIT")\nexcept sqlite3.IntegrityError:\n    if con.in_transaction:con.execute("ROLLBACK")\n    print("Whole collision import refused")\nprint("Books:",con.execute("SELECT COUNT(*) FROM books").fetchone()[0])\nprint("New id5 exists:",con.execute("SELECT id FROM books WHERE id=5").fetchone() is not None)'),
    "CSV parsing completes before writes. The existing-id collision happens after id5's attempted insert but rollback leaves only the original four books.",
    ('# Replace an existing row without informing the user', '# Insert-only contract: report collision and roll back the batch', "An import must not silently change previous records."),
    "Import two validated fixture rows with ids5and6in one transaction; show the imported titles.",
    demo('rows=[(5,"Small Databases","Aya",220),(6,"Reading Together","Ken",160)]\ncon.execute("BEGIN IMMEDIATE")\ntry:\n    con.executemany("INSERT INTO books(id,title,author,pages) VALUES(?,?,?,?)",rows)\n    con.execute("COMMIT")\nexcept BaseException:\n    if con.in_transaction:con.execute("ROLLBACK")\n    raise\nprint(con.execute("SELECT id,title FROM books WHERE id IN (5,6) ORDER BY id").fetchall())'),
    "Validate positive ASCII integer tokens without accepting2.5,-1orTrueas a book id.",
    '''tokens=["5","2.5","-1","True","０５"]
for token in tokens:
    valid=token.isascii() and token.isdecimal() and 1<=int(token)<=2**63-1
    print(repr(token),valid)''',
    "Declare import limits and merge policy; preserve input; validate first; commit every inserted record together.",
    [("What happens if the second imported ID already exists?", "The whole import rolls back", "Keep the first row silently", "Replace all old books", "The project promises insert-only atomic imports."),
     ("Does this import silently normalise title text?", "No", "Always", "Only when offline", "Accepted source text is retained; invalid boundaries are rejected.")])

PROJECT=(ROOT/"docs"/"python-week35"/"library_db.py").read_text(encoding="utf-8")
PROJECT_CORE=PROJECT.rsplit('\nif __name__ == "__main__":',1)[0]
CAPSTONE=PROJECT_CORE+'''
from tempfile import TemporaryDirectory
with TemporaryDirectory() as folder:
    database=Path(folder)/"library.db"
    initialise(database)
    with closing(connect(database)) as con:
        before=report(con)
        new_loan=borrow(con,3,4,"2026-01-11")
        return_book(con,new_loan,"2026-01-12")
        backup(con,Path(folder)/"backup.db")
        after=report(con)
        print("Schema:",after["schema_version"])
        print("Books / events before:",before["books"],before["loans"])
        print("Books / events after:",after["books"],after["loans"])
        print("Member event counts:",[(m["name"],m["loan_count"],m["open_count"]) for m in after["members"]])
    with closing(connect(Path(folder)/"backup.db",readonly=True)) as restored:
        print("Backup history matches:",report(restored)==after)
'''

lesson(5, "6. Milestone: an offline SQLite library with a Python interface",
    "Assemble schema, bound operations, atomic imports, backups and analysis into one working project.",
    [("Library project boundary", "library_db.py is a standalone local command-line practice app with fictional records. It never reads website localStorage, tokens, passwords or your learning notes."),
     ("contextmanager; transaction helper", "A function decorated with contextmanager can yield inside a with block and run cleanup afterward. Here transaction(con) begins once, yields to the operation, commits or rolls back on failure, and rejects unsupported nesting."),
     ("iso_day; insert-only CLI; report", "The interface validates real ISO calendar dates, IDs and bounded inputs; a partial unique index enforces one open event per copy. report uses three-table history and all-member counts. init refuses an existing file; backups use a new destination.")],
    "Keep library_db.py, books-import.csv, analysis.py and README.md from docs/python-week35. Start in a fresh practice folder and follow the README commands. "
    "The complete example below includes the project implementation followed by a temporary recovery drill, so it is self-contained and safe to run again. "
    "Version1creates the three constrained tables and active-loan rule; version2adds notes and an indexed member/date lookup without losing events. "
    "A borrower change is a new event, not an overwritten history row. Returning an already closed loan fails clearly; a return earlier than borrowing is rejected. "
    "The date interface validates individual calendar dates. This teaching scope does not claim to prevent every historical interval overlap entered through other tools; its database rule concerns currently open events. "
    "Bound SQL protects values, not secrets at rest. SQLite here is not an encrypted vault, web login, remote sync service or replacement for Study Hub's existing backup. "
    "The optional pandas analysis reads the database read-only, matches SQL member totals including zero-event members and returns an ordered report. Everything runs offline after initial pandas installation.",
    "python library_db.py library.db init\npython library_db.py library.db report\npython library_db.py library.db borrow 3 4 2026-01-11\npython library_db.py library.db backup library-backup-01.db",
    CAPSTONE,
    "The drill starts with4events, creates and returns a fifth event, then proves the backup has exactly the same report. Dipa now has one closed event. Copy and event totals remain distinct. This code is long because it assembles the previously explained pieces; read one function at a time.",
    ('# Store personal secrets or website tokens in the practice project', '# Use only fictional local practice records; keep learning storage separate', "A database does not make publicly committed content private."),
    "Build a minimal bound Python function add_copy(title,pages) on the fresh fixture. Insert a fictional copy and return its generated id; validate before writing.",
    demo('def add_copy(title,pages):\n    if not title.strip() or type(pages) is not int or pages<=0:\n        raise ValueError("Require a title and positive integer pages")\n    cur=con.execute("INSERT INTO books(title,author,pages) VALUES(?,?,?)",(title,"Practice author",pages))\n    return cur.lastrowid\nnew_id=add_copy("My SQL Practice",200)\nprint(new_id,con.execute("SELECT title,pages FROM books WHERE id=?",(new_id,)).fetchone())'),
    "Run an acceptance check: enforce one open loan per copy, deliberately attempt duplicate checkout inside a transaction, then verify every original event remains.",
    demo('con.execute("CREATE UNIQUE INDEX one_open_loan ON loans(book_id) WHERE returned_on IS NULL")\ncon.execute("BEGIN IMMEDIATE")\ntry:\n    con.execute("UPDATE members SET name=? WHERE id=?",("Temporary name",1))\n    con.execute("INSERT INTO loans(book_id,member_id,borrowed_on) VALUES(?,?,?)",(1,3,"2026-01-11"))\n    con.execute("COMMIT")\nexcept sqlite3.IntegrityError:\n    if con.in_transaction:con.execute("ROLLBACK")\nprint("Name preserved:",con.execute("SELECT name FROM members WHERE id=1").fetchone()[0]=="Asha")\nprint("Events preserved:",con.execute("SELECT COUNT(*) FROM loans").fetchone()[0]==4)'),
    "A working database project has a declared unit, constraints, bound input, explicit transactions, versioned schema, verified backups and honest reports.",
    [("Where do routine opens use mode=rw?", "An existing owned database path", "A new typo path", "An arbitrary remote URL", "Only init is allowed to create a practice database."),
     ("What protects against two current checkouts of one copy?", "The partial UNIQUE index", "A SELECT precheck alone", "A title string", "The database enforces the active-book rule."),
     ("Should migration version2erase old loans?", "No", "Always", "Only closed events", "An additive migration retains history."),
     ("How should user-supplied titles enter SQL?", "Bound parameters", "Concatenation", "Inside table names", "Values remain separate from SQL structure."),
     ("Does COUNT(*) after a LEFT JOIN always count actual loans?", "No", "Always", "Only for zero-event members", "A placeholder can contribute one row; count child ids."),
     ("Does SQL NULL equal the text NULL?", "No", "Always", "After close", "A missing value and a text token differ."),
     ("What happens to a failed managed CSV import?", "The batch rolls back", "Earlier inserted rows remain by contract", "All old rows are replaced", "The import is atomic and insert-only."),
     ("What should happen to an existing init destination?", "Refuse it", "Overwrite it", "Delete its tables silently", "Initialisation reserves a new file exclusively."),
     ("How do you validate a backup?", "Reopen it and compare known queries", "Check only its filename", "Delete the original first", "The drill checks recoverable database contents."),
     ("Can to_sql replace be used blindly on managed tables?", "No", "Always", "When the index is hidden", "It drops/recreates inferred schema."),
     ("Does this project encrypt Study Hub passwords?", "No", "Always", "Only offline", "The fictional teaching app has no credential access or encryption feature."),
     ("What does a correct SQL/pandas comparison require?", "Matching semantics and populations", "Only similar timing", "Only one matching total", "Filters, NULL rules, groups, zeros and order must agree.")])


def write():
    target=ROOT/"study-hub.html"
    original=target.read_bytes().decode("utf-8")
    start=original.index("const DAY_TEACH = {")
    end=original.index("\n};\n\nconst REST_DAY",start)
    if any(('"'+key+'":') in original[start:end] for key in DAYS):
        if "--refresh" not in sys.argv:
            raise RuntimeError("Week35 exists; refuse overwriting it without explicit author refresh")
        first=original.index('\n"35.0": {',start)
        tail=original[first:end]
        if not all(('"'+key+'":') in tail for key in DAYS):
            raise RuntimeError("Unexpected Week35 block")
        original=original[:first]+original[end:]
        end=original.index("\n};\n\nconst REST_DAY",start)
    assert [len(day["parts"]) for day in DAYS.values()]==[5,5,6,5,5,6]
    with tempfile.TemporaryDirectory(prefix="studyhub-w35-verify-") as temp:
        manifest=Path(temp)/"examples.json"; result=Path(temp)/"results.json"
        manifest.write_text(json.dumps([code for code,_ in JOBS]),encoding="utf-8")
        subprocess.run([sys.executable,str(ROOT/"scripts"/"python-example-worker.py"),str(manifest),str(result)],
            check=True,timeout=300,env={**os.environ,"MPLBACKEND":"Agg","OPENBLAS_NUM_THREADS":"1","OMP_NUM_THREADS":"1","PYTHONDONTWRITEBYTECODE":"1"})
        results=json.loads(result.read_text(encoding="utf-8"))
    for (_,destination),result in zip(JOBS,results,strict=True):
        destination["v" if destination["t"]=="out" else "out"]=result["out"]
    DAYS["35.0"]["parts"][0]["sections"].insert(3,sec("tip","Days1–4 and the final library CLI use the standard library only. Day5 needs pandas: reuse your existing environment. Verified with Python3.12.14, SQLite3.53.1 and pandas3.0.1. Initial package installation needs internet; lessons, supplied outputs and local practice run offline afterward. Timing and query-plan outputs are recorded examples and may vary."))
    final=DAYS["35.5"]["parts"][5]["sections"]
    final.extend([
        sec("sh",'python library_db.py library.db init\npython library_db.py library.db report\npython library_db.py library.db import-books books-import.csv\npython library_db.py library.db borrow 3 4 2026-01-11\npython library_db.py library.db return 5 2026-01-12\npython library_db.py library.db backup library-backup-01.db\npython analysis.py library.db'),
        sec("p","Project files: docs/python-week35/library_db.py, books-import.csv, analysis.py and README.md in the repository. Download and keep them together. Run the commands in a new practice folder, in the displayed order; use new names for another init or backup. Command filenames are relative to that folder. These commands do not touch website data."),
        sec("p","Primary references: https://docs.python.org/3/library/sqlite3.html · https://www.sqlite.org/lang_select.html · https://www.sqlite.org/foreignkeys.html · https://www.sqlite.org/lang_transaction.html · https://www.sqlite.org/lang_createindex.html · https://www.sqlite.org/lang_altertable.html · https://pandas.pydata.org/docs/reference/api/pandas.read_sql_query.html · https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html . Explanations, exercises and fictional data are original; all learning text and executed outputs are embedded for offline reading.")
    ])
    addition="\n".join(json.dumps(k)+": "+json.dumps(v,ensure_ascii=False,indent=2)+"," for k,v in DAYS.items()).replace("</","<\\/")
    prefix=original[:end].rstrip()
    if not prefix.endswith(","):prefix+=","
    temporary=target.with_suffix(".html.tmp")
    temporary.write_bytes((prefix+"\n"+addition+original[end:]).encode("utf-8"))
    temporary.replace(target)
    print("Added Week35:6days,32parts,64practice prompts,74explained quiz questions,96executed examples/solutions; all previous application/storage code unchanged.")


if __name__=="__main__":
    write()
