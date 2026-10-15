"""Append only Week38 teaching data after executing every authored snippet."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap

ROOT = Path(__file__).resolve().parents[1]
DAYS = {f"38.{d}": {"parts": []} for d in range(6)}
JOBS = []


def clean(code):
    return textwrap.dedent(code).strip() + "\n"


def sec(t, v=None, **extra):
    return {"t": t, **({"v": v} if v is not None else {}), **extra}


def lesson(day, title, goal, terms, explanation, syntax, example, walkthrough,
           mistake, task, solution, challenge, challenge_code, takeaway, quizzes):
    parts = DAYS[f"38.{day}"]["parts"]
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
        sec("p", explanation), sec("syn", syntax, note="Python/HTML pattern. Run in a fresh practice folder. Where lesson_support is imported, keep the supplied study_app package and helper beside the snippet."),
        sec("code", clean(example)), output, sec("p", walkthrough),
        sec("mis", wrong=mistake[0], right=mistake[1], why=mistake[2]),
        sec("ex", task, practiceId=f"38.{day}.{index}.build"), build,
        sec("ex", "Mini challenge: " + challenge, practiceId=f"38.{day}.{index}.challenge"), stretch,
        sec("try", q=quizzes[0][0], code="# Predict, then explain before revealing.", a=quizzes[0][1], why=quizzes[0][4]),
        sec("checkpoint", lesson={"id": f"course:38.{day}.{index}", "quiz": questions}), sec("key", takeaway)
    ]})
    JOBS.extend([(clean(example), output), (clean(solution), build), (clean(challenge_code), stretch)])


BASIC='''from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String,CheckConstraint,func,inspect
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
class Base(DeclarativeBase):
    pass
db=SQLAlchemy(model_class=Base)
class Note(db.Model):
    __tablename__="notes"
    id:Mapped[int]=mapped_column(primary_key=True)
    title:Mapped[str]=mapped_column(String(100),nullable=False)
    __table_args__=(CheckConstraint("length(trim(title)) BETWEEN 1 AND 100"),)
app=Flask(__name__)
app.config.update(TESTING=True,SQLALCHEMY_DATABASE_URI="sqlite:///:memory:")
db.init_app(app)
'''


def orm(body,seed=False):
    setup="with app.app_context():\n    db.create_all()\n"
    if seed:setup+='    db.session.add_all([Note(title="SQL"),Note(title="Flask"),Note(title="HTTP")]);db.session.commit()\n'
    return BASIC+setup+textwrap.indent(clean(body),"    ")


def fixture(body,seed=True):
    return 'from lesson_support import practice,token,register,login,PRACTICE_PASSWORD\nfrom study_app.extensions import db\nfrom study_app.models import User,Post,Tag,LoginSession\nwith practice(seed='+str(seed)+') as app:\n'+textwrap.indent(clean(body),"    ")


lesson(0,"1. ORM objects represent rows, not a new kind of magic",
    "Connect an ordinary Python object to a relational row without forgetting SQL.",
    [("ORM; SQLAlchemy; Flask-SQLAlchemy","An Object Relational Mapper maps classes/objects to tables/rows. SQLAlchemy builds queries and manages mapped objects; Flask-SQLAlchemy integrates its engine/session lifecycle with Flask."),
     ("DeclarativeBase; Mapped; mapped_column","A declarative base holds model metadata. Mapped[str] describes a mapped attribute; mapped_column declares database details. Type hints communicate mapping intent, not complete input validation."),
     ("Extension and model","db is an extension object; Note is a model class. Constructing Note(title=...) creates a Python object. add/commit later turn it into a stored row.")],
    "Week 35 taught tables, keys, constraints and transactions. Those ideas still apply; an ORM changes how you express them in Python. "
    "The repeated introductory scaffold defines one notes table in an isolated in-memory database. It does not open Study Hub's data. "
    "Note(title='First idea') is initially just an object. Adding it to the unit of work and committing persists the row. "
    "SQLAlchemy still sends SQL to SQLite. Understanding the generated query and database constraints remains useful. "
    "Read the scaffold once: imports/base, model, Flask config, extension binding and application context. Later parts unpack each new API.",
    'class Note(db.Model):\n    id:Mapped[int]=mapped_column(primary_key=True)\n    title:Mapped[str]=mapped_column(String(100),nullable=False)',
    orm('note=Note(title="First idea")\nprint("Before insert id:",note.id)\ndb.session.add(note);db.session.commit()\nprint("Stored:",note.id,note.title)'),
    "The uninserted object has no generated id. After commit, SQLite supplies id1. The title remains ordinary text, not HTML or SQL code.",
    ('# Assume constructing Note automatically saves it', 'db.session.add(note)\ndb.session.commit()', "Construction, scheduling and persistence are different stages."),
    "Create one note object, commit it and print its generated id.",
    orm('row=Note(title="Explain the mapping");db.session.add(row);db.session.commit();print(row.id,row.title)'),
    "Insert two independent objects and show their distinct identities.",
    orm('a=Note(title="A");b=Note(title="B");db.session.add_all([a,b]);db.session.commit();print(a.id,b.id)'),
    "ORM convenience does not remove relational reasoning, explicit validation or transaction boundaries.",
    [("Does creating a model object immediately persist it?","No","Always","Only if it has a title","The session must flush/commit the pending object."),
     ("Does an ORM remove the need to understand SQL?","No","Always","Only for SQLite","It still executes relational operations and constraints.")])

lesson(0,"2. Configure the extension and the database URI",
    "Separate model metadata, engine configuration and the application instance.",
    [("SQLALCHEMY_DATABASE_URI; init_app","The URI selects the database connection. db.init_app(app) binds an unbound extension to one app after configuration. A relative SQLite URI in Flask-SQLAlchemy resolves under the app's instance folder."),
     ("Engine versus Session","The engine manages database connectivity. The ORM Session tracks a unit of work and mapped objects. Neither is Flask's browser-cookie session.")],
    "Create one unbound extension and initialise it after loading app config. This supports a factory and independent test databases. "
    "The examples use sqlite:///:memory:, which is disposable. The final project uses an ignored local instance/journal.sqlite file. "
    "Do not paste a database credential into a public template or log a credential-bearing connection string. This local SQLite project needs no remote database password. "
    "Changing a config string after initialisation does not reliably reconfigure an existing engine; select the intended config before init_app. "
    "Persistent app data and browser state must have deliberately different owners and lifetimes.",
    'app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///:memory:"\ndb.init_app(app)',
    orm('print("Backend:",db.engine.dialect.name)\nprint("Tables:",inspect(db.engine).get_table_names())'),
    "The configured backend is SQLite and the model metadata created notes. No disk path or private credential is printed.",
    ('db.init_app(app)\n# Set the intended URI afterward', 'app.config["SQLALCHEMY_DATABASE_URI"]=uri\ndb.init_app(app)', "Load database configuration before constructing the engine binding."),
    "Inspect the notes table's declared column names.",
    orm('print([column["name"] for column in inspect(db.engine).get_columns("notes")])'),
    "Demonstrate that a new in-memory app starts with zero notes.",
    orm('print(db.session.scalar(db.select(func.count()).select_from(Note)))'),
    "Configure first, bind second and name the lifetime of the selected database.",
    [("Where does a relative Flask-SQLAlchemy SQLite URI resolve?","The app instance folder","Always the current terminal directory","The browser cookie","Its Flask integration uses the instance directory."),
     ("Is db.session the same as Flask session?","No","Always","If logged in","One manages ORM work; the other is browser-returned signed state.")])

lesson(0,"3. Application context scopes database work",
    "Use models in a request, CLI command or explicit app context.",
    [("app.app_context; scoped session","Flask-SQLAlchemy chooses the active app through application context. Requests and Flask CLI commands supply it; standalone scripts/tests can enter app.app_context explicitly."),
     ("Teardown; remove; dispose","The scoped session is cleaned up with its app context. remove releases that unit-of-work session; dispose closes an engine's pooled connectivity when an owned test app is finished.")],
    "The extension can serve different app instances. It must know which app's configuration/engine to use. "
    "A context identifies that app; it is not a fake login and does not set the current user. "
    "Use a context for one coherent standalone database task. Do not keep a global context alive forever as a workaround for a lifecycle error. "
    "The scaffold deliberately wraps examples in with app.app_context. A real view already runs inside a suitable context. "
    "Do not return detached lazy relationships to unrelated background work without explicitly managing their data/session needs.",
    'with app.app_context():\n    rows=db.session.scalars(db.select(Note)).all()',
    BASIC+'try:\n    db.session.execute(db.select(Note))\nexcept RuntimeError:\n    print("No active application context")\nwith app.app_context():\n    db.create_all()\n    print("Inside context:",db.session.scalar(db.select(func.count()).select_from(Note)))\n',
    "The first operation cannot choose an active app. The explicit context makes the in-memory table and query available.",
    ('app.app_context().push()  # leave a global context forever', 'with app.app_context():\n    # complete one scoped task', "Structured context lifetime makes cleanup and ownership understandable."),
    "Insert and query within the same explicit application context.",
    orm('db.session.add(Note(title="Scoped work"));db.session.commit();print(db.session.scalar(db.select(Note.title)))'),
    "Inspect an engine inside context and print only its backend, not a connection string.",
    orm('print(db.engine.dialect.name=="sqlite")'),
    "Use the current app's scoped database session rather than confusing app context with authentication.",
    [("Does entering app_context authenticate a visitor?","No","Always","Only for CLI","It selects application context, not user identity."),
     ("Do normal Flask requests already provide application context?","Yes","Never","Only for GET","Flask establishes request/application context for view handling.")])

lesson(0,"4. Constraints still protect mapped tables",
    "Pair application validation with meaningful database rules.",
    [("nullable=False; unique; CheckConstraint","These rules constrain stored data, independent of the form UI. SQLite VARCHAR lengths are not automatically enforced just because String(100) is declared; use validation and an appropriate CHECK."),
     ("IntegrityError; rollback","A failed constraint flush/commit raises SQLAlchemy IntegrityError. Roll back before using the failed ORM session for new work.")],
    "An ORM model is not a substitute for a schema contract. Required values, uniqueness and relationships still need database rules. "
    "The scaffold's title CHECK rejects empty/oversized trimmed titles. String(100) documents storage intent but is not a SQLite length guarantee alone. "
    "A rejected commit leaves the session in a failed transaction state until rollback. Catch the expected integrity failure and restore that boundary. "
    "Do not catch it and print Saved. A useful interface reports a rejection without echoing raw database parameters. "
    "The final project similarly validates fields before writes and keeps owner ids as required foreign keys.",
    'try:\n    db.session.commit()\nexcept IntegrityError:\n    db.session.rollback()\n    # Report a sanitised rejected operation.',
    orm('from sqlalchemy.exc import IntegrityError\ndb.session.add(Note(title=""))\ntry:db.session.commit()\nexcept IntegrityError:\n    db.session.rollback();print("Invalid title rejected")\nprint("Rows:",db.session.scalar(db.select(func.count()).select_from(Note)))'),
    "No row is saved. Rollback makes the scoped session usable for the next query.",
    ('except IntegrityError:\n    print("Saved")', 'except IntegrityError:\n    db.session.rollback()\n    print("Rejected")', "A failed transaction needs cleanup and an honest result."),
    "Reject a title longer than 100 characters and retain zero rows.",
    orm('from sqlalchemy.exc import IntegrityError\ndb.session.add(Note(title="x"*101))\ntry:db.session.commit()\nexcept IntegrityError:db.session.rollback();print("Length rule rejected")\nprint(db.session.scalar(db.select(func.count()).select_from(Note)))'),
    "After a failed insert and rollback, save a valid note successfully.",
    orm('from sqlalchemy.exc import IntegrityError\ndb.session.add(Note(title=" "))\ntry:db.session.commit()\nexcept IntegrityError:db.session.rollback()\ndb.session.add(Note(title="Recovered"));db.session.commit();print(db.session.scalar(db.select(Note.title)))'),
    "Validate before writing and let database constraints enforce shared rules; roll back failed units of work.",
    [("Does SQLite String(100)alone guarantee length enforcement?","No","Always","Only for ASCII","Use the explicit CHECK and interface validation."),
     ("What is needed after an integrity failure?","Rollback before new ORM work","Print success","Delete every table","The failed transaction must be reset.")])

lesson(0,"5. create_all is initialisation, not a migration",
    "Create a known new schema without erasing an existing one.",
    [("Metadata; create_all; migration","Metadata describes known models. create_all creates missing tables; it does not add changed columns to existing tables. A reviewed migration changes an existing schema."),
     ("Non-destructive init policy","The final init-db command refuses a database that already has tables. It does not reset accounts/posts to match changed model code.")],
    "Import model modules before create_all so their metadata exists. Calling it before those imports cannot create unseen tables. "
    "Once a local app has saved records, do not solve a new-column requirement by dropping the database. "
    "Week 35's migration principles still apply: inspect, back up, review one versioned change and verify retained rows. Alembic-style tools can implement that as the project grows. "
    "The demonstration creates a table, appends a column to its metadata, then proves create_all did not alter the stored table. "
    "This is a disposable schema experiment; the public local project only initialises a new database and refuses reinitialisation.",
    'db.create_all() # new missing tables only\n# Existing-schema changes require a reviewed migration.',
    orm('from sqlalchemy import Column\nNote.__table__.append_column(Column("optional_note",String(50)))\ndb.create_all()\nprint("Metadata columns:",list(Note.__table__.columns.keys()))\nprint("Stored columns:",[c["name"] for c in inspect(db.engine).get_columns("notes")])'),
    "The new metadata field does not appear in SQLite. That difference is why create_all is not a migration mechanism.",
    ('# Delete journal.sqlite whenever a model changes', '# Back up and apply a reviewed schema migration', "Model evolution must preserve existing records."),
    "Call create_all twice and show a previously saved row still exists.",
    orm('db.session.add(Note(title="Retain this"));db.session.commit();db.create_all();print(db.session.scalar(db.select(Note.title)))'),
    "Inspect the database table list before claiming initialisation is safe on an empty database.",
    orm('print("Already initialised:",bool(inspect(db.engine).get_table_names()))'),
    "Initialise new schemas deliberately; never confuse metadata changes with applied migrations.",
    [("Does create_all add every new model column to an existing table?","No","Always","Only for Text","It creates missing tables, not general alterations."),
     ("Should an existing journal be deleted to evolve its schema?","No","Always","If it is local","Use a backup and reviewed migration.")])

lesson(0,"6. Select rows, scalar columns and counts deliberately",
    "Choose the correct result shape in modern SQLAlchemy queries.",
    [("select; scalars; scalar; session.get","select builds a statement. scalars returns its first-column values or mapped objects. scalar returns one scalar value. session.get(Model,id) looks up a primary-key identity or returns None."),
     ("Result shape; deterministic order","Selecting a model and selecting two columns produce different result shapes. Use explicit ordering before expecting a stable display or top-N result.")],
    "Use db.select rather than copying the legacy Model.query interface into new code. "
    "scalars(select(Note)) returns Note objects; scalars(select(Note.title)) returns strings. Selecting id and title with execute returns result rows. "
    "A count is one scalar result, not len of an unbounded downloaded list. "
    "session.get can return None for an absent id. Do not index or dereference it blindly. "
    "Explicit order_by matters just as it did in raw SQL; an ORM is not a promise of insertion-order results.",
    'db.session.scalars(db.select(Note).order_by(Note.id)).all()\ndb.session.get(Note,1)',
    orm('objects=db.session.scalars(db.select(Note).order_by(Note.id)).all()\nprint([row.title for row in objects])\nprint(db.session.execute(db.select(Note.id,Note.title).order_by(Note.id)).all())\nprint("Missing:",db.session.get(Note,99) is None)',True),
    "The first result contains mapped objects projected to titles for display. The second contains selected column pairs. The absent key is explicitly checked.",
    ('rows=db.session.scalars(db.select(Note.id,Note.title)).all() # expect full pairs', 'rows=db.session.execute(db.select(Note.id,Note.title)).all()', "scalars selects only the first result column."),
    "Return titles in alphabetical order with scalars.",
    orm('print(db.session.scalars(db.select(Note.title).order_by(Note.title)).all())',True),
    "Return a count using func.count without loading all objects.",
    orm('print(db.session.scalar(db.select(func.count()).select_from(Note)))',True),
    "Know the statement's selected columns and the result accessor's shape before using its output.",
    [("What does scalars(select(Note.title))return?","Title values","Every selected row pair","HTTP responses","scalars exposes the first selected column."),
     ("What can session.get return for an unknown key?","None","A new saved row automatically","Always an exception","Handle missing identity explicitly.")])

lesson(1,"1. Create records through one deliberate commit",
    "Build valid mapped objects and commit a complete logical change.",
    [("Unit of work; add_all; flush","The session tracks pending inserts/changes. flush sends SQL inside the current transaction; commit finishes the transaction. A flushed id is not proof that the operation is durable.")],
    "Construct an approved object, add it and commit. For several related rows, keep them in one coherent operation. "
    "flush can obtain generated ids before commit so related inserts can use them. A later rollback still removes those uncommitted rows. "
    "Do not commit inside every small helper if the caller needs several helpers to succeed or fail together. "
    "Validate inputs before adding them; database constraints remain the final shared boundary. "
    "These first CRUD exercises use the one-table scaffold; owner-scoped web routes are added after relationships and authentication are explained.",
    'db.session.add_all([Note(title="A"),Note(title="B")])\ndb.session.commit()',
    orm('row=Note(title="First approved note");db.session.add(row);db.session.flush();print("Flushed id:",row.id)\ndb.session.rollback();print("After rollback:",db.session.scalar(db.select(func.count()).select_from(Note)))'),
    "An id was allocated within the transaction, but rollback left no saved note. Durability is not established by an id alone.",
    ('db.session.flush() # assume permanently saved', 'db.session.commit() # finish the intended transaction', "Flush and commit have different guarantees."),
    "Save two valid records as one batch and verify both titles.",
    orm('db.session.add_all([Note(title="Plan"),Note(title="Review")]);db.session.commit();print(db.session.scalars(db.select(Note.title).order_by(Note.id)).all())'),
    "Add one valid and one invalid note, then show rollback prevents partial success.",
    orm('from sqlalchemy.exc import IntegrityError\ndb.session.add_all([Note(title="Valid first"),Note(title="")])\ntry:db.session.commit()\nexcept IntegrityError:db.session.rollback();print("Whole batch rejected")\nprint(db.session.scalar(db.select(func.count()).select_from(Note)))'),
    "Let the logical operation define the commit boundary; a generated id is not a saved-result certificate.",
    [("Does flush make the data durable?","No","Always","If an id exists","It runs inside the still-active transaction."),
     ("Should one failed row leave a hidden partial batch here?","No","Always","Only for SQLite","The batch is one transaction and rolls back.")])

lesson(1,"2. Read with precise filters and safe values",
    "Build parameterised ORM comparisons instead of concatenating SQL.",
    [("where; expression binding; contains(autoescape=True)","Mapped-column comparisons build SQL expressions with bound values. contains supports literal substring search when autoescape=True, so %and _remain data rather than LIKE wildcards.")],
    "A title supplied by a user is a value, not SQL syntax. Compare Note.title==termrather than constructing a SQL string. "
    "A successful empty result means the query ran and no approved row matched. An exception is not the same answer. "
    "Literal substring search and SQL wildcard search have different semantics. The final list UI promises a literal title search. "
    "Parameter binding protects statement structure; it does not enforce access control. Later every post query also requires the authenticated author id. "
    "Raw SQL can still be useful, but an f-string inside text(...)can reintroduce injection even in an ORM project.",
    'db.select(Note).where(Note.title==term)\nNote.title.contains(term,autoescape=True)',
    orm('term="x\\\' OR 1=1 --"\nprint("Bound hostile-looking value:",db.session.scalars(db.select(Note.title).where(Note.title==term)).all())\nprint("All rows:",db.session.scalar(db.select(func.count()).select_from(Note)))',True),
    "The value matches nothing and does not turn into an ORclause. All three original notes remain.",
    ('text(f"SELECT * FROM notes WHERE title=\\\'{term}\\\'")', 'db.select(Note).where(Note.title==term)', "ORM use does not excuse raw SQL interpolation."),
    "Find the exact Flask note.",
    orm('print(db.session.scalars(db.select(Note.title).where(Note.title=="Flask")).all())',True),
    "Insert a title containing a literal percent and search for that percent without matching every row.",
    orm('db.session.add(Note(title="100% focus"));db.session.commit()\nprint(db.session.scalars(db.select(Note.title).where(Note.title.contains("%",autoescape=True))).all())',True),
    "Bind values and state the search semantics; add ownership as a separate required predicate.",
    [("Does using an ORM make interpolated raw SQL safe?","No","Always","Only for text()","Raw string construction can still inject SQL syntax."),
     ("Does safe value binding automatically enforce record ownership?","No","Always","Only for ids","Authorisation needs its own query condition.")])

lesson(1,"3. Update only the intended object",
    "Look up a record, validate a replacement and commit its change.",
    [("Dirty tracking; identity map","The ORM tracks changed attributes on a loaded mapped object. The identity map keeps one Python identity for a given row within the current session, not across all requests/users.")],
    "Load the note by its primary key, handle missing data, assign a validated title and commit. "
    "Do not assume a numeric id is enough to authorise a web edit. The final owned_post helper requires id and authenticated owner together. "
    "A tracked object's new value can be visible in Python before commit; that does not mean another connection has observed a durable change. "
    "Avoid accepting hidden author_idfields from a browser to choose ownership. The server determines that from the signed-in account. "
    "The exercise focuses on one-table mutation; the web implementation later applies the same unit-of-work boundary with owner checks.",
    'row=db.session.get(Note,note_id)\nif row is None: # handle missing\n    ...\nrow.title=approved_title\ndb.session.commit()',
    orm('row=db.session.get(Note,1);row.title="SQL relationships";db.session.commit()\nprint([(r.id,r.title) for r in db.session.scalars(db.select(Note).order_by(Note.id))])',True),
    "Only note1changes. The other two rows retain their titles.",
    ('# Trust a posted author_id to transfer ownership', '# Derive the owner from the authenticated user, never from form data', "A visitor can edit hidden form values."),
    "Handle id99without trying to assign an attribute on None.",
    orm('row=db.session.get(Note,99);print("Not found" if row is None else row.title)',True),
    "Change a loaded title, roll back and query its original stored value.",
    orm('row=db.session.get(Note,1);row.title="Temporary";db.session.rollback();print(db.session.get(Note,1).title)',True),
    "Tracked state changes still need validation, ownership and a clear commit/rollback result.",
    [("Does assigning an attribute prove durable persistence?","No","Always","Only for strings","A transaction must successfully commit."),
     ("Should a form choose its post's author_id?","No","Always","If hidden","The authenticated server-side user determines ownership.")])

lesson(1,"4. Delete a record without deleting shared meaning",
    "Remove the intended row and understand relationship cleanup.",
    [("session.delete; association cleanup","delete schedules a mapped row for removal on commit. Many-to-many link rows can be removed while shared tag records remain; deletion policy must match the entity relationship.")],
    "A delete is a write and should be an explicit POST with token and owner checks in a browser application. A GET detail URL must not delete anything. "
    "The one-table example proves which row survives a committed delete. "
    "Later, deleting a post removes its tag links but not shared tags used by other posts. Do not cascade-delete shared vocabulary by accident. "
    "A failed delete must leave the session cleaned up through rollback before new work. "
    "The final UI provides an explicit delete action under a details disclosure; it is not triggered by visiting a list/detail page.",
    'row=db.session.get(Note,note_id)\ndb.session.delete(row)\ndb.session.commit()',
    orm('row=db.session.get(Note,2);db.session.delete(row);db.session.commit();print(db.session.scalars(db.select(Note.title).order_by(Note.id)).all())',True),
    "Only Flask was removed. SQL and HTTP remain, matching their distinct row identities.",
    ('@app.get("/delete/<int:id>")  # side effect on normal GET', '# Use a token-protected POST and an owner-scoped lookup', "Reads and intentional destructive writes have different contracts."),
    "Delete note1and verify its identity lookup now returns None.",
    orm('db.session.delete(db.session.get(Note,1));db.session.commit();print(db.session.get(Note,1) is None)',True),
    "Schedule a delete then roll back; verify all three rows remain.",
    orm('db.session.delete(db.session.get(Note,1));db.session.flush();db.session.rollback();print(db.session.scalar(db.select(func.count()).select_from(Note)))',True),
    "Delete exactly the intended entity and preserve unrelated/shared records.",
    [("Should a normal GET delete a post?","No","Always","If the id is valid","A delete must be an explicit protected write."),
     ("Should deleting one post delete shared tag objects?","No","Always","If they were selected","Only that post's association rows should disappear.")])

lesson(1,"5. Pagination and bounded list responses",
    "Return a manageable ordered page without confusing it with the complete dataset.",
    [("limit; offset; db.paginate","limit/offset choose a slice under an explicit order. Flask-SQLAlchemy paginate adds items, total and next/previous metadata; page input and maximum page size still need validation.")],
    "A database-backed page should not render every record just because the table eventually becomes large. "
    "Choose a stable order and a bounded page size. A page of five is not proof that only five records exist. "
    "The final app uses five owner-filtered posts per page and validates page as an ASCII integer within its declared range. "
    "Apply ownership/search filters before slicing/counting; otherwise totals can reveal or mix another account's data. "
    "Pagination over changing data is not an atomic snapshot, just as last week's API pages were not a frozen census.",
    'statement=db.select(Post).where(Post.author_id=current_id).order_by(Post.id.desc())\npage=db.paginate(statement,page=1,per_page=5,max_per_page=5)',
    orm('statement=db.select(Note).order_by(Note.id)\npage=db.paginate(statement,page=1,per_page=2,max_per_page=2)\nprint("Items:",[r.title for r in page.items],"Total:",page.total,"Next:",page.has_next)',True),
    "The page contains two rows while total is 3. Its continuation metadata says another page is available.",
    ('# Slice all users first, then try to hide other owners in the template', '# Apply owner/search filters in the SQL statement before pagination', "The query population and total must already be authorised."),
    "Read the second page and show only HTTP remains.",
    orm('page=db.paginate(db.select(Note).order_by(Note.id),page=2,per_page=2,max_per_page=2);print([r.title for r in page.items],page.has_next)',True),
    "Filter titles to Flask before counting/paginating.",
    orm('page=db.paginate(db.select(Note).where(Note.title=="Flask").order_by(Note.id),page=1,per_page=2);print(page.total,[r.title for r in page.items])',True),
    "Bound display work and apply the correct population filter before both rows and totals.",
    [("Does one page's size equal the whole-table count automatically?","No","Always","If sorted","Use explicit total/continuation information."),
     ("When should ownership filtering occur?","Before pagination/counts","Only in the HTML loop","After rendering","The database query must select the authorised population.")])

lesson(1,"6. Transactions recover from errors without hidden partial saves",
    "Treat related ORM writes as one unit and report actual outcomes.",
    [("Autobegin; transaction boundary","ORM work commonly starts a transaction automatically. Do not blindly begin another after a query. Group the operation and commit once; on failure roll back the unit before continuing."),
     ("Commit failure versus validation failure","Reject invalid form fields before mutation; catch expected database integrity failures around commit. Unexpected failures should remain visible to development tests rather than being disguised as success.")],
    "The session coordinates pending changes; the database determines whether the transaction can commit. "
    "A batch containing an invalid row must not leave an earlier valid row behind if the operation promises all-or-nothing. "
    "After rollback, query the database to prove the outcome. A message alone is not evidence that old rows survived. "
    "Do not introduce a broad except Exception:return successaround a route. It hides both integrity failures and programming bugs. "
    "The final project's duplicate username path explicitly rolls back so another valid registration can work afterward.",
    'try:db.session.commit()\nexcept IntegrityError:\n    db.session.rollback()\n    # Display a sanitised rejection.',
    orm('from sqlalchemy.exc import IntegrityError\noriginal=db.session.scalar(db.select(func.count()).select_from(Note))\ndb.session.add_all([Note(title="New valid"),Note(title="")])\ntry:db.session.commit()\nexcept IntegrityError:db.session.rollback();print("Rejected batch")\nprint("Prior count preserved:",db.session.scalar(db.select(func.count()).select_from(Note))==original)',True),
    "The failed batch leaves exactly the original three notes. The session can query again after rollback.",
    ('except Exception:\n    return "Saved"', 'except IntegrityError:\n    db.session.rollback()\n    return "Rejected",400', "An operation's response must agree with its committed state."),
    "Perform a valid two-object insert and confirm the total moves from 3 to 5.",
    orm('db.session.add_all([Note(title="A"),Note(title="B")]);db.session.commit();print(db.session.scalar(db.select(func.count()).select_from(Note)))',True),
    "Rollback an update and insert together so neither attempted change survives.",
    orm('db.session.get(Note,1).title="Changed";db.session.add(Note(title="New"));db.session.flush();db.session.rollback();print(db.session.get(Note,1).title,db.session.scalar(db.select(func.count()).select_from(Note)))',True),
    "Choose one logical transaction boundary and verify both successful and failed database states.",
    [("Should a failed batch secretly retain its first new row?","No","Always","If it was valid","The logical operation is atomic."),
     ("Should a broad exception handler report successful saving?","No","Always","Only in local apps","It would hide the actual operation outcome.")])


def rel(body):
    return fixture("with app.app_context():\n"+textwrap.indent(clean(body),"    "))


lesson(2,"1. One author has many posts",
    "Map a foreign-key relationship and distinguish an object reference from a stored key.",
    [("ForeignKey; relationship; back_populates","Post.author_id is the stored user key; Post.author and User.posts are ORM navigation attributes. back_populates names the reverse relationship so object changes stay coordinated."),
     ("Public lesson_support fixture","Keep lesson_support.py and the supplied study_app package beside these examples. practice(seed=True) creates an isolated in-memory app with fictional Asha/Ben accounts and three posts; no real accounts or files are read. Its prebuilt password hashes are explained on Day 4.")],
    "A post belongs to one user; a user can own several posts. Put the foreign key on posts, the many side. "
    "Do not repeat the current username as the authoritative ownership key on every post. The user id survives a display-name change. "
    "A relationship helps Python navigate that stored relationship; it is not a browser permission check. "
    "The fixture gives Asha two posts and Ben one. Enter the app context before querying its ORM session. "
    "The final web route restricts both id and author; a navigation property alone does not enforce that restriction.",
    'author_id:Mapped[int]=mapped_column(ForeignKey("users.id"))\nauthor:Mapped[User]=relationship(back_populates="posts")',
    rel('asha=db.session.scalar(db.select(User).where(User.username=="asha"))\nprint(asha.username,[p.title for p in sorted(asha.posts,key=lambda p:p.id)])\npost=db.session.get(Post,1);print(post.author_id==asha.id,post.author.username)'),
    "The foreign-key id and object reference describe the same author. Asha's collection contains two distinct post records.",
    ('# Treat relationship access as a permission system', '# Use the relationship for navigation; enforce ownership in each query/route', "An ORM relationship does not authenticate the caller."),
    "Find Ben and show his single post title.",
    rel('ben=db.session.scalar(db.select(User).where(User.username=="ben"));print([p.title for p in ben.posts])'),
    "Select post ids and author ids to expose the stored relational keys.",
    rel('print(db.session.execute(db.select(Post.id,Post.author_id).order_by(Post.id)).all())'),
    "Relationships model data connections; authenticated access rules remain an explicit application responsibility.",
    [("Where is the one-to-many foreign key stored?","On posts.author_id","Only in a cookie","On every CSS class","The many-side row refers to its author."),
     ("Does relationship()automatically block another visitor's reads?","No","Always","Only for many-to-many","Authorisation must be checked separately.")])

lesson(2,"2. Many-to-many tags use an association table",
    "Share tags without storing comma-separated lists or duplicate identities.",
    [("Association table; composite primary key; secondary","post_tags stores pairs of post_id/tag_id. Its composite key prevents the same link twice. relationship(secondary=...) navigates the association."),
     ("Shared tag identity","A tag can label many posts and one post can have many tags. Removing a link is different from deleting the shared tag record.")],
    "A comma-separated tag string is awkward to validate and join. Give each tag a row and connect it through a link table. "
    "The project's three allowed tags are flask, sql and practice. The UI submits tag names but the server resolves them to known Tag objects. "
    "Appending to post.tags schedules an association change. It does not duplicate the tag's identity. "
    "The association's foreign keys enforce valid parent rows; the composite primary key rejects repeated links. "
    "Do not delete shared Tag objects just because one post is removed.",
    'post.tags=[known_flask_tag,known_sql_tag]\n# association key: (post_id,tag_id)',
    rel('post=db.session.get(Post,1)\ntag=db.session.scalar(db.select(Tag).where(Tag.name=="flask"))\npost.tags.append(tag);db.session.commit()\nprint(post.title,[t.name for t in post.tags])\nprint("Tag has posts:",[p.title for p in tag.posts])'),
    "One association connects the existing Routes post to the existing flask tag. The tag remains a reusable row.",
    ('post.tags_text="flask,sql"  # use text as relational membership', 'post.tags=[flask_tag,sql_tag]', "Store membership through explicit validated relationships."),
    "Attach two known tags to one post and print their ordered names.",
    rel('post=db.session.get(Post,1);post.tags=db.session.scalars(db.select(Tag).where(Tag.name.in_(["flask","sql"]))).all();db.session.commit();print(sorted(t.name for t in post.tags))'),
    "Remove one tag link and verify all three tag rows still exist.",
    rel('post=db.session.get(Post,1);tag=db.session.scalar(db.select(Tag).where(Tag.name=="sql"));post.tags.append(tag);db.session.commit();post.tags.remove(tag);db.session.commit();print(len(post.tags),db.session.scalar(db.select(db.func.count()).select_from(Tag)))'),
    "Association rows represent membership; shared vocabulary has a separate lifecycle.",
    [("What does one post_tags row represent?","One post/tag link","A duplicated full account","A password","It relates existing records."),
     ("Should removing a tag link remove the shared tag?","No","Always","Only for SQL","Other posts can still use that tag.")])

lesson(2,"3. Joins and grouped counts must preserve the intended unit",
    "Express relational analyses through mapped columns without double-counting.",
    [("join; outerjoin; func.count(child.id)","Joins form matching rows. After an outer join, count a child's non-NULL key rather than every result row when zero-match parents must count as zero."),
     ("Group by identity","Group by stable keys plus required labels. Adding another one-to-many join can multiply rows and inflate totals; inspect cardinality before summing.")],
    "Week 35's join reasoning still applies. An ORM expression can produce the same count inflation as handwritten SQL. "
    "Count posts per author with User.id and username as grouping fields. Asha has two and Ben one. "
    "For zero-event evidence, the empty tag associations initially give every tag zero posts. COUNT(Post.id) correctly excludes unmatched placeholders. "
    "Do not join author→posts→tags and assume every joined row is a unique post. One post with two tags creates two joined pairs. "
    "Use distinct post keys or pre-aggregate at the right unit when that is the question.",
    'db.select(User.username,func.count(Post.id)).outerjoin(User.posts).group_by(User.id,User.username)',
    rel('from sqlalchemy import func\nq=db.select(User.username,func.count(Post.id)).outerjoin(User.posts).group_by(User.id,User.username).order_by(User.id)\nprint(db.session.execute(q).all())\nq=db.select(Tag.name,func.count(Post.id)).outerjoin(Tag.posts).group_by(Tag.id,Tag.name).order_by(Tag.name)\nprint(db.session.execute(q).all())'),
    "Author counts reconcile to three posts. The tag report retains all three existing tag rows with zero links.",
    ('func.count()  # assume unmatched outer-join parent means zero', 'func.count(Post.id)', "A null-extended result row is not an actual child."),
    "Count distinct author ids present in the posts table.",
    rel('from sqlalchemy import func\nprint(db.session.scalar(db.select(func.count(func.distinct(Post.author_id)))))'),
    "Join posts to authors and display title/current username in post-id order.",
    rel('q=db.select(Post.title,User.username).join(Post.author).order_by(Post.id);print(db.session.execute(q).all())'),
    "Use entity keys and denominator checks even when the query is written with ORM attributes.",
    [("Can ORM joins multiply a parent measurement?","Yes","Never","Only raw SQL","Relational cardinality is unchanged."),
     ("Which count excludes a missing child placeholder?","count(Post.id)","count(*)always","The length of a username","A missing child's key is NULL.")])

lesson(2,"4. Loading strategies and the N+1query pattern",
    "Fetch related data deliberately instead of issuing one hidden query per card.",
    [("Lazy load; selectinload; N+1","A relationship may load when first accessed. Iterating many parents and then their children can issue one initial query plus one per parent. selectinload batches related collection loading."),
     ("Query instrumentation","A test-only before_cursor_execute listener can count statements without printing SQL parameters. Measure a known scope and remove the listener afterward.")],
    "A page can look correct yet quietly make many database calls. Inspect loading behaviour rather than guessing from the template loop. "
    "For a post list showing tags, selectinload(Post.tags)loads the page's tag collections in another planned query. "
    "It is not a reason to fetch every row in every table. Apply owner filters and pagination first. "
    "The example counts only the selected read scope after fixture initialisation. It never prints password hashes or bind parameters. "
    "Exact query count depends on the chosen relationship strategy/data; the shown two-query pattern is the verified scope here.",
    'db.select(Post).options(selectinload(Post.tags)).order_by(Post.id)',
    rel('from sqlalchemy import event\nfrom sqlalchemy.orm import selectinload\ncalls=[]\ndef count_query(*args):calls.append(1)\nevent.listen(db.engine,"before_cursor_execute",count_query)\ntry:\n    rows=db.session.scalars(db.select(Post).options(selectinload(Post.tags)).order_by(Post.id)).all()\n    print([(p.title,len(p.tags)) for p in rows])\n    print("Statements in read scope:",len(calls))\nfinally:event.remove(db.engine,"before_cursor_execute",count_query)'),
    "The query gets three parent posts then their collections without a separate tag query per post.",
    ('# Optimise by dumping every user and post into memory', '# Filter/paginate the authorised rows, then load required relationships', "A loading strategy must respect both scope and resource use."),
    "Load users and posts with selectinload and print per-author post counts.",
    rel('from sqlalchemy.orm import selectinload\nusers=db.session.scalars(db.select(User).options(selectinload(User.posts)).order_by(User.id)).all();print([(u.username,len(u.posts)) for u in users])'),
    "Return only post titles when no related data is needed.",
    rel('print(db.session.scalars(db.select(Post.title).order_by(Post.id)).all())'),
    "Choose the required data and loading strategy together; do not trade access scope for fewer queries.",
    [("What does N+1describe?","An initial query plus repeated per-parent loads","A password length rule","A route count","Lazy access can trigger repeated relationship queries."),
     ("Should a performance fix remove owner filtering?","No","Always","Only in tests","Correct authorised scope remains mandatory.")])

lesson(2,"5. Foreign keys and delete behaviour are still real database rules",
    "Verify invalid references and retain shared tags after post deletion.",
    [("SQLite connection event; foreign_keys pragma","SQLite requires enforcement on each connection. The factory attaches a connect listener to its own engine and enables foreign keys before schema/data work."),
     ("Association cascade versus parent deletion","The link table's ondelete=CASCADEremoves links for a deleted post/tag when enforced. Shared Tag objects are not themselves deleted when a post disappears.")],
    "Declaring ForeignKeyis not enough if the database engine is not enforcing it. The project enables SQLite's rule on each owned connection. "
    "A post for nonexistent author99must be rejected and rolled back, not accepted until the first relationship access fails. "
    "Deleting a post can remove association rows while leaving the shared tags for reuse. "
    "The application does not implement account deletion this week; do not assume an unspecified cascade policy or build a destructive reset command. "
    "Validate the actual database outcome, not just an ORM diagram.",
    'ForeignKey("posts.id",ondelete="CASCADE")\n# Enable SQLite foreign keys on each engine connection.',
    rel('from sqlalchemy.exc import IntegrityError\ndb.session.add(Post(author_id=99,title="Invalid author",body="Must fail"))\ntry:db.session.commit()\nexcept IntegrityError:db.session.rollback();print("Unknown author rejected")\nprint(db.session.scalar(db.select(db.func.count()).select_from(Post)))'),
    "The invalid row is absent and the original three posts remain after rollback.",
    ('# Assume a relationship declaration enables SQLite enforcement', '# Enable and test the database foreign-key rule per connection', "The storage engine must actually enforce the declared constraint."),
    "Attach a tag, delete the post and prove the tags remain.",
    rel('post=db.session.get(Post,1);post.tags.append(db.session.scalar(db.select(Tag).where(Tag.name=="flask")));db.session.commit();db.session.delete(post);db.session.commit();print("Posts/tags:",db.session.scalar(db.select(db.func.count()).select_from(Post)),db.session.scalar(db.select(db.func.count()).select_from(Tag)))'),
    "Inspect the enabled foreign-key pragma through the project's engine.",
    rel('from sqlalchemy import text\nprint(db.session.scalar(text("PRAGMA foreign_keys")))'),
    "Schema declarations, engine enforcement and application deletion policy must agree.",
    [("Does SQLite always enforce declared foreign keys without setup?","No","Always","Only on disk","Enable/check enforcement on each connection."),
     ("Does deleting one post remove every tag?","No","Always","If there are three tags","Only its membership links are removed.")])

lesson(2,"6. Plan ownership in queries before building account UI",
    "Define the row population the server will permit for one account.",
    [("Owner-scoped statement","The required predicate pairs the requested post id with the trusted authenticated user id. A missing match can return404without revealing whether an inaccessible row exists."),
     ("Mass assignment","Blindly passing every submitted field into a model can let a visitor choose owner/privilege fields. Select approved editable fields and derive ownership on the server.")],
    "We know the schema: now decide which user can access which row before adding convenient edit links. "
    "Asha's list contains only her two posts. Ben's id3must not appear even if a URL is manually changed. "
    "The trusted owner in this fixture comes from a known account query; real routes derive it from validated server-side login state on Day 4. "
    "Checking only the visible list is insufficient: detail, edit GET, edit POST and delete POST all need the same rule. "
    "Do not let an author_idfield in submitted JSON/form data transfer a post to another account.",
    'db.select(Post).where(Post.id==requested_id,Post.author_id=current_user.id)',
    rel('asha=db.session.scalar(db.select(User).where(User.username=="asha"))\nallowed=db.session.scalars(db.select(Post).where(Post.author_id==asha.id).order_by(Post.id)).all()\nprint("Asha titles:",[p.title for p in allowed])\nrequested=db.session.scalar(db.select(Post).where(Post.id==3,Post.author_id==asha.id));print("Other owner accessible:",requested is not None)'),
    "The other-owner lookup returns None under the combined predicate. The same predicate will support every object-level web operation.",
    ('db.session.get(Post,requested_id) # only check id', 'db.select(Post).where(Post.id==requested_id,Post.author_id=current_user.id)', "Knowing a row's id is not permission to use it."),
    "List Ben's permitted post ids.",
    rel('ben=db.session.scalar(db.select(User).where(User.username=="ben"));print(db.session.scalars(db.select(Post.id).where(Post.author_id==ben.id).order_by(Post.id)).all())'),
    "Build an approved editable-field dictionary and show author_id is excluded.",
    '''submitted={"title":"Routes","body":"A clear explanation","author_id":99}
approved={key:submitted[key] for key in ("title","body")}
print(sorted(approved),"author_id" in approved)''',
    "Define ownership once in a reusable lookup and apply it to every object operation.",
    [("Is a numeric post id enough to authorise access?","No","Always","Only if hidden","The server must check the authenticated owner's relationship."),
     ("Which submitted fields should the browser choose?","Approved content fields only","Any author/privilege field","The signing key","Ownership is derived by the server.")])

lesson(3,"1. Password hashing is not encryption or plain SHA256",
    "Store a purpose-built salted password hash and verify through its library API.",
    [("Password KDF; salt; generate_password_hash","Werkzeug uses a password-hashing algorithm with a work factor and random salt. Store its encoded result; do not use plain text, reversible encryption or a fast unsalted digest as a password verifier."),
     ("check_password_hash","Verify a candidate with the encoded stored verifier. Do not hash the candidate again and compare two strings, because new salts intentionally change them.")],
    "A password belongs in memory only as long as needed to verify/derive its stored verifier. The database column stores password_hash, never the original string. "
    "A random salt means the same fictional password produces different encoded results; both can still verify the correct candidate. "
    "The following example uses a public practice-only passphrase, not any real account credential. It prints booleans instead of the full hashes. "
    "Do not trim a password silently or log submitted values. Our teaching input contract accepts12–128characters exactly. "
    "A hash reduces harm from verifier disclosure but does not make a public database safe or replace access control.",
    'stored=generate_password_hash(candidate)\ncheck_password_hash(stored,candidate)',
    '''from werkzeug.security import generate_password_hash,check_password_hash
practice="fictional-learning-passphrase"
a=generate_password_hash(practice);b=generate_password_hash(practice)
print("Different salted outputs:",a!=b)
print("Correct:",check_password_hash(a,practice),"Wrong:",check_password_hash(a,"wrong-practice-value"))
print("Not plaintext:",a!=practice)''',
    "Different encoded hashes are expected. Verification uses the stored algorithm/salt information rather than a new random hash comparison.",
    ('stored=password  # plaintext', 'stored=generate_password_hash(password)', "Use the library's password verifier format, not raw credentials."),
    "Hash one fictional candidate and verify a different one fails.",
    '''from werkzeug.security import generate_password_hash,check_password_hash
stored=generate_password_hash("fictional-one-passphrase")
print(check_password_hash(stored,"fictional-other-passphrase"))''',
    "Show that boundary spaces are part of a supplied password rather than silently stripped.",
    '''from werkzeug.security import generate_password_hash,check_password_hash
candidate=" practice-only-spaces "
stored=generate_password_hash(candidate)
print(check_password_hash(stored,candidate),check_password_hash(stored,candidate.strip()))''',
    "Keep raw credentials transient and use a purpose-built salted password verifier.",
    [("Should two newly generated hashes of the same password always match?","No","Always","Only locally","Random salts deliberately produce different encodings."),
     ("How is a candidate verified?","check_password_hash(stored,candidate)","Compare two fresh random hashes","Decode the original password","The verifier API uses the stored algorithm/salt.")])

lesson(3,"2. Usernames need a declared identity policy",
    "Normalise a login identifier deliberately while preserving password meaning.",
    [("Username canonicalisation; unique constraint","This local project uses3–32ASCII letters/digits/underscores, trims outer whitespace and lowercases the username. A database UNIQUEconstraint enforces the canonical identity across concurrent writers."),
     ("Registration collision; rollback","A precheck can improve feedback but cannot prevent a race. Catch the database uniqueness failure and roll back before continuing.")],
    "Choose a clear beginner policy rather than claiming to solve every multilingual identity/collation issue. "
    "Ashaand ashaare the same canonical username in this project. The password is not lowercased or trimmed. "
    "The form's pattern/minlength hints do not replace server validation. Scripts can submit any value. "
    "A duplicate registration returns a useful rejection and does not overwrite the existing password hash. "
    "The project has no email verification or password recovery; it is a local practice account system with a deliberately limited scope.",
    'name=username_value(request.form.get("username",""))\n# UNIQUE(users.username) protects canonical stored identities.',
    '''from study_app.security import username_value
for value in [" Asha ","ASHA","a","two names","日本語"]:
    print(repr(value),username_value(value))''',
    "The two Asha spellings become asha. Short, spaced and non-ASCII usernames are rejected under this explicit teaching contract.",
    ('password=password.strip().lower()', 'username=username_value(raw_name)\n# Password stays exactly as submitted.', "Identifier normalisation is not password normalisation."),
    "Register Ashaand then ASHA; verify only one account is stored.",
    fixture('client=app.test_client();print(register(client,"Asha").status_code,register(client,"ASHA").status_code)\nwith app.app_context():print(db.session.scalar(db.select(db.func.count()).select_from(User)))',False),
    "After duplicate rejection, register a different valid account successfully.",
    fixture('client=app.test_client();register(client,"asha");register(client,"asha");print(register(client,"ben").status_code)\nwith app.app_context():print(db.session.scalar(db.select(db.func.count()).select_from(User)))',False),
    "Normalise only the declared identifier, enforce uniqueness in storage and preserve existing accounts on collision.",
    [("Can a precheck alone prevent concurrent duplicate registration?","No","Always","If using Flask","A UNIQUEconstraint and commit handling remain necessary."),
     ("Should the username policy silently transform the password too?","No","Always","Only for uppercase","Password input retains its exact meaning.")])

lesson(3,"3. Register without storing or redisplaying a raw password",
    "Validate a real form, commit the new account and redirect to sign-in.",
    [("Registration boundary; credential redisplay","Validate the token and fields, derive a hash, commit the account and redirect. On error retain only a bounded username; never populate the password field from submitted data.")],
    "The real project form includes the session-bound token from Week 37. A missing token is rejected before account creation. "
    "The server validates the canonical username and password length, hashes the exact password and catches a uniqueness failure. "
    "Success returns303to sign-in instead of automatically claiming a verified external identity. "
    "No user is pre-created by init-db. The public helper registers only fictional accounts in isolated memory during examples. "
    "The example confirms stored data is a verifier without printing the password or encoded hash.",
    'db.session.add(User(username=name,password_hash=generate_password_hash(password)))\ndb.session.commit()\nreturn redirect(url_for("auth.login"),code=303)',
    fixture('client=app.test_client();response=register(client,"asha");print(response.status_code,response.headers["Location"])\nwith app.app_context():\n    user=db.session.scalar(db.select(User).where(User.username=="asha"))\n    print("Verifier stored:",user.password_hash!=PRACTICE_PASSWORD)\n    print("No plaintext password column:","password" not in User.__table__.columns)',False),
    "The new account redirects to sign-in. The schema has password_hash rather than a plaintext password field.",
    ('<input type="password" value="{{ submitted_password }}">', '<input type="password" name="password" autocomplete="new-password">', "Do not redisplay an entered credential after rejection."),
    "Submit registration without a token and prove no account is created.",
    fixture('client=app.test_client();r=client.post("/auth/register",data={"username":"asha","password":PRACTICE_PASSWORD});print(r.status_code)\nwith app.app_context():print(db.session.scalar(db.select(db.func.count()).select_from(User)))',False),
    "Submit a short fictional password with a valid token and verify the response does not echo it.",
    fixture('client=app.test_client();r=client.post("/auth/register",data={"username":"asha","password":"tiny","csrf_token":token(client,"/auth/register")});print(r.status_code,\'value="tiny"\' not in r.get_data(as_text=True))',False),
    "A registration operation validates, hashes, commits or rejects; it never preserves raw credentials in display/storage.",
    [("Should a failed form refill the password field?","No","Always","If escaped","Do not put the submitted credential back into HTML."),
     ("Does init-dbcreate a hidden default account?","No","Always","Only locally","It creates schema/tags; users register explicitly.")])

lesson(3,"4. Login verifies credentials and rotates session state",
    "Authenticate against the stored verifier and establish a new server login record.",
    [("Generic failure; dummy verifier","The interface uses one Invalid username or passwordmessage. For a normally sized unknown-account candidate it checks a dummy verifier too, reducing an obvious missing-user fast path without promising perfect timing indistinguishability."),
     ("Session fixation boundary; login id","A successful login clears old cookie fields and stores a new unpredictable login identifier. The database links that server record to user_id and an expiry, rather than trusting a posted user id.")],
    "The login form has the same token and bounded-input requirements as registration. It does not treat a display name as proof of identity. "
    "Find the canonical username, verify the submitted candidate with check_password_hash and fail generically if either identity or verifier is wrong. "
    "Success creates a new one-hour server LoginSessionand places only its identifier in the signed cookie. Passwords/hashes are not cookie data. "
    "Clearing previous session fields also replaces the old form-token state. Render a fresh form after login. "
    "This local app has no sign-in throttling/MFA/password reset and is not an internet deployment recipe; those are separate controls to design before public account hosting.",
    'if user is None or not check_password_hash(stored,candidate):\n    # same generic login rejection\nsession.clear();session["login_id"]=new_identifier',
    fixture('client=app.test_client();bad=client.post("/auth/login",data={"username":"asha","password":"wrong-practice-password","csrf_token":token(client)});print("Wrong:",bad.status_code,"Generic:","Invalid username or password." in bad.get_data(as_text=True))\ngood=login(client,"asha");print("Correct:",good.status_code,good.headers["Location"])\nwith client.session_transaction() as values:print("Login id set:",bool(values.get("login_id")),"Password absent:","password" not in values)'),
    "Only the correct candidate opens a server-backed login. The cookie gets an identifier rather than a password or author_idchosen by the browser.",
    ('session["user_id"]=request.form["user_id"] # trust submitted identity', '# Resolve the verified account, then create a server login session', "Identity comes from successful credential verification."),
    "Try an unknown username and a wrong known-account password; verify both show the same failure message.",
    fixture('client=app.test_client()\nfor name in ["unknown","asha"]:\n    r=client.post("/auth/login",data={"username":name,"password":"wrong-practice-password","csrf_token":token(client)});print(r.status_code,"Invalid username or password." in r.get_data(as_text=True))'),
    "Set a stale test session field, log in and show it was cleared.",
    fixture('client=app.test_client()\nwith client.session_transaction() as values:values["unrelated"]="old state"\nlogin(client,"asha")\nwith client.session_transaction() as values:print("unrelated" in values,bool(values.get("login_id")))'),
    "Authentication verifies a credential; establish fresh minimal session state from that verified account.",
    [("Should a posted user_idchoose who is signed in?","No","Always","If numeric","The server resolves the verified identity."),
     ("Does the cookie contain the password verifier?","No","Always","If signed","It stores a login identifier and nonsecret form/feedback state.")])

lesson(3,"5. Load the current user and protect routes on the server",
    "Resolve a valid server login record for each request before private data queries.",
    [("g.user; before_app_request; login_required","A request loader checks the signed-cookie login id against the database and expiry, then assigns the request-local user. A decorator with wrapsredirects unauthenticated requests before private views execute."),
     ("Expired or deleted session","A missing/expired server session does not authenticate even if an old cookie still has a correctly signed id. Clear stale browser state and require sign-in.")],
    "Do not trust the mere presence of a login_idcookie value. The server must still find a valid unexpired record and its user. "
    "g.userlives only for that request; it is not a module-global current user shared by every visitor. "
    "login_requiredprotects private routes even if the visitor types a URL directly. A hidden menu link cannot provide that guarantee. "
    "The loader clears stale state rather than calling a missing user record authenticated. "
    "Protecting the route authenticates the visitor; the next day adds object-level authorisation for each requested post.",
    'if g.user is None:return redirect(url_for("auth.login"),code=303)\n# Private view then applies its owner predicate.',
    fixture('client=app.test_client();before=client.get("/posts/");print("Anonymous:",before.status_code,before.headers["Location"])\nlogin(client,"asha");print("Signed in:",client.get("/posts/").status_code)'),
    "The same private endpoint redirects without login and responds after verification. It still must restrict its rows to the signed-in owner.",
    ('# Hide My posts link and assume the URL is protected', '# Check login state in a server-side route decorator', "Direct requests bypass navigation styling."),
    "Expire a real server session in the test database and show the next private request redirects.",
    fixture('client=app.test_client();login(client,"asha")\nwith client.session_transaction() as values:identifier=values["login_id"]\nwith app.app_context():db.session.get(LoginSession,identifier).expires_at=0;db.session.commit()\nprint(client.get("/posts/").status_code)'),
    "Use a separate fresh client to show one browser's successful login does not log in another.",
    fixture('a=app.test_client();b=app.test_client();login(a,"asha");print(a.get("/posts/").status_code,b.get("/posts/").status_code)'),
    "Authentication state is verified server-side per request and scoped to the actual browser login.",
    [("Is login_idpresence alone enough to authenticate?","No","Always","If a string","The database session and expiry must still validate."),
     ("Is g.usera permanent global account for every visitor?","No","Always","Only after login","It is request-local state.")])

lesson(3,"6. Logout revokes the current server login",
    "Make an old signed cookie unusable after its login record is deleted.",
    [("Server revocation versus clearing a cookie","Removing the current LoginSessionrow revokes that login id. Clearing browser state alone would not necessarily reject a replayed old signed cookie."),
     ("Multiple logins per account","Each successful login has its own random server record. Logging out one does not automatically revoke a different browser's record unless an explicit all-sessions policy is implemented.")],
    "Week 37's flag demo cleared only a cookie session. This project adds a database-backed revocation boundary. "
    "Logout is a token-protected POST that deletes the current login record, commits, clears cookie state and redirects. "
    "A copied old cookie's signature can still be valid, but the deleted server record makes it unauthenticated. "
    "A second separately authenticated browser keeps its own login record. State the policy instead of accidentally invalidating every account session. "
    "Expired records are rejected too; a production system should also define periodic cleanup, expiry renewal and account-recovery policies.",
    'db.session.delete(current_login)\ndb.session.commit()\nsession.clear()',
    fixture('client=app.test_client();login(client,"asha");old=client.get_cookie("session").value\nr=client.post("/auth/logout",data={"csrf_token":token(client,"/posts/")});print("Logout:",r.status_code)\nclient.set_cookie("session",old);print("Replayed old cookie:",client.get("/posts/").status_code)'),
    "The replayed cookie cannot reopen the private list because its server-side login record was revoked.",
    ('session.clear() # assume any old signed cookie is globally revoked', '# Delete/revoke the corresponding server login record too', "Browser cleanup and server-side revocation are separate operations."),
    "Log two clients into Asha, log one out and verify the other still works.",
    fixture('a=app.test_client();b=app.test_client();login(a,"asha");login(b,"asha");a.post("/auth/logout",data={"csrf_token":token(a,"/posts/")});print(a.get("/posts/").status_code,b.get("/posts/").status_code)'),
    "Verify GET /auth/logoutdoes not perform the POST-only operation.",
    fixture('client=app.test_client();login(client,"asha");print(client.get("/auth/logout").status_code,client.get("/posts/").status_code)'),
    "Revocation is an explicit server policy, not merely removing a cookie from the current browser.",
    [("Can deleting the server login record invalidate replay of its old cookie?","Yes","Never","Only if the username changes","The loader can no longer resolve a valid login."),
     ("Does one logout revoke a different browser's login here?","No","Always","If the account matches","Each browser login has a separate server record.")])

lesson(4,"1. Authentication is not object-level authorisation",
    "Apply the same owner predicate to detail, edit and delete.",
    [("Object-level access control; IDOR","Changing a URL id must not expose another account's object. An owner-scoped query checks requested id and g.user.id together; a route-level login check alone is insufficient."),
     ("Consistent404policy","This project returns404for both missing and inaccessible post ids. It avoids confirming another account's record existence through the ordinary detail response.")],
    "Asha is authenticated, but that does not grant her access to Ben's posts. "
    "Every protected object operation calls the same owned_post helper: select the requested id and current author's key together. "
    "Do not rely on the list page to hide other ids. A visitor can type or script a direct detail/edit/delete request. "
    "The example signs in through the real credential form and deliberately requests Ben's id3. "
    "Test both reads and writes; protecting edit GETwhile leaving edit POSTunscoped is an incomplete control.",
    'db.select(Post).where(Post.id==post_id,Post.author_id==g.user.id)',
    fixture('client=app.test_client();login(client,"asha")\nprint("Own detail:",client.get("/posts/1").status_code)\nprint("Other detail:",client.get("/posts/3").status_code)\nprint("Other edit:",client.get("/posts/3/edit").status_code)\nr=client.post("/posts/3/delete",data={"csrf_token":token(client,"/posts/")});print("Other delete:",r.status_code)'),
    "Asha can read her post1but cannot view/edit/delete Ben's post3. The delete also supplied a valid Asha token, proving token validity is not ownership.",
    ('if logged_in: return db.session.get(Post,post_id)', '# Require both a valid login and a matching author predicate', "Authentication does not authorise every object."),
    "Request an inaccessible post edit with a valid token and prove its original title remains.",
    fixture('client=app.test_client();login(client,"asha");r=client.post("/posts/3/edit",data={"title":"Changed by wrong owner","body":"Should fail","csrf_token":token(client,"/posts/")});print(r.status_code)\nwith app.app_context():print(db.session.get(Post,3).title)'),
    "Show the same404status for missing999and inaccessible3.",
    fixture('client=app.test_client();login(client,"asha");print(client.get("/posts/999").status_code,client.get("/posts/3").status_code)'),
    "A login check and an owner check answer different questions; enforce both on every object path.",
    [("Does a valid login allow every post id?","No","Always","If CSRF passes","Ownership is a separate required predicate."),
     ("Should edit POSTbe protected even if edit GETalready checks?","Yes","Never","Only if the UI exposes it","A client can submit directly without first loading the form.")])

lesson(4,"2. CSRF validation is separate from ownership and field validation",
    "Reject missing/stale/cross-session tokens before any database mutation.",
    [("Form intent; ASCII token boundary","Every state-changing project POSTchecks a random token matching the signed-cookie session. Missing, oversized, Unicode or wrong values are rejected before the view's write path."),
     ("Three independent checks","CSRF verifies form/session intent; authentication resolves the account; authorisation checks the object. A valid token does not validate title/body or grant another owner's access.")],
    "Browsers can send cookies automatically. A POSTmethod and a signed login cookie do not alone implement request-intent checking. "
    "The project reuses Week 37's explicit token pattern and rotates it when login clears old session state. "
    "A missing token prevents a create even when the other fields are valid and the visitor is signed in. "
    "A valid token still needs valid title/body/tags and an owner-scoped target. "
    "These local mechanics are a teaching implementation; mature public deployments need an integrated threat model, rate controls and secure configuration as well.",
    'if not matching_session_token:abort(400)\n# Then authenticate, validate fields and authorise the target.',
    fixture('client=app.test_client();login(client,"asha");r=client.post("/posts/create",data={"title":"Valid title","body":"Valid body"});print(r.status_code)\nwith app.app_context():print("Posts retained:",db.session.scalar(db.select(db.func.count()).select_from(Post)))'),
    "All three prior posts remain. The missing form token is not silently bypassed just because a login exists.",
    ('# Treat a valid CSRF token as permission to edit any id', '# Check token, current account, editable fields and object ownership', "Each control has a distinct responsibility."),
    "Attempt to use Asha's token from a separately signed-in Ben client.",
    fixture('a=app.test_client();b=app.test_client();login(a,"asha");login(b,"ben");foreign=token(a,"/posts/create");r=b.post("/posts/create",data={"title":"Cross token","body":"Rejected","csrf_token":foreign});print(r.status_code)'),
    "Supply a Unicode token and confirm a handled400rather than a comparison error.",
    fixture('client=app.test_client();login(client,"asha");print(client.post("/posts/create",data={"title":"Title","body":"Body","csrf_token":"日本語"}).status_code)'),
    "Do not combine separate security questions into one flag or disable checks for convenient testing.",
    [("Does a valid token authorise another owner's post?","No","Always","Only for delete","Object ownership must still match."),
     ("Should missing tokens create a partial saved row?","No","Always","If title is valid","The check runs before mutation.")])

lesson(4,"3. Escape stored text as well as fresh form input",
    "Treat database content as untrusted data when rendering it.",
    [("Stored XSS; autoescaping","A stored record can contain script-like text. Database storage does not make it trusted HTML. Jinja's normal .htmltemplates escape that data unless deliberately overridden."),
     ("Bounded redisplay; multiline body","The project retains bounded drafts and renders body text with CSS white-space:pre-wrap, rather than converting it into arbitrary markup.")],
    "An attack-like title saved successfully is still just text. The read page must not execute it later. "
    "Do not mark post.bodyas safeor concatenate it into HTML just because the ORM returned it. "
    "Keep template source trusted, pass title/bodyas context data and let normal HTML autoescaping work. "
    "Multiline notes need not become rich HTML; pre-wrapcan preserve line breaks while keeping text escaped. "
    "This is one HTML text context. Untrusted URL/script/style contexts have separate policies and are not offered as user-editable fields here.",
    '<h1>{{ post.title }}</h1><p class="post-body">{{ post.body }}</p>',
    fixture('client=app.test_client();login(client,"asha")\nr=client.post("/posts/create",data={"title":"<b>Literal title</b>","body":"<script>window.bad=true</script>","csrf_token":token(client,"/posts/create")},follow_redirects=True)\ntext=r.get_data(as_text=True);print(r.status_code,"&lt;script&gt;" in text,"<script>" not in text,"&lt;b&gt;" in text)'),
    "The view stores approved text and the template escapes it when rendering. No actual script element appears in the returned page.",
    ('{{ post.body|safe }}', '{{ post.body }}', "The database is not a trust boundary that turns entered text into safe HTML."),
    "Submit an oversized draft containing angle brackets and verify failure/no new row.",
    fixture('client=app.test_client();login(client,"asha");r=client.post("/posts/create",data={"title":"<b>"+"x"*101,"body":"Body","csrf_token":token(client,"/posts/create")});print(r.status_code,"&lt;b&gt;" in r.get_data(as_text=True))\nwith app.app_context():print(db.session.scalar(db.select(db.func.count()).select_from(Post)))'),
    "Store a multiline body through the model and show its line break remains plain text data.",
    rel('post=db.session.get(Post,1);post.body="First line\\nSecond line";db.session.commit();print(post.body.splitlines())'),
    "Validation and escaping solve different problems; accepted stored content still needs safe presentation.",
    [("Does storing a string in SQLite make it trusted markup?","No","Always","If the author owns it","Stored user data remains untrusted for rendering."),
     ("How does the project preserve body line breaks?","Plain escaped text plus CSS pre-wrap","Mark every body safe","Execute it as a template","No user HTML interpretation is needed.")])

lesson(4,"4. Parameter binding, search semantics and mass assignment",
    "Keep SQL structure and ownership under server control.",
    [("ORM expression parameters; raw text danger","Model-column comparisons bind values. Interpolating a value into raw SQL reintroduces structure injection; do not claim an ORM makes every string safe."),
     ("Explicit editable fields","The create/edit route accepts title, body and known tags. It ignores a posted author_id and sets/keeps owner identity from the verified account.")],
    "Literal search should treat a percent sign as text, not an undocumented wildcard. The final list query uses contains(...,autoescape=True). "
    "A value looking like SQL syntax cannot bypass the owner predicate through a mapped comparison. "
    "The same principle applies to write fields: a hidden input can be changed, so it must not determine account ownership. "
    "The demonstration attempts to create a post with author_id2while signed in as Asha. The stored author remains Asha. "
    "This is a concrete approved-field policy, not a general invitation to pass request.forminto a model constructor.",
    'Post(title=approved_title,body=approved_body,author_id=g.user.id,tags=known_tags)',
    fixture('client=app.test_client();login(client,"asha")\nr=client.post("/posts/create",data={"title":"Owned by verified user","body":"Bounded text","author_id":"2","csrf_token":token(client,"/posts/create")});print(r.status_code)\nwith app.app_context():\n    post=db.session.scalar(db.select(Post).where(Post.title=="Owned by verified user"));print(post.author.username)'),
    "The browser's attempted owner choice is not an approved field. The server derives ownership from the validated login.",
    ('Post(**request.form)  # blindly trust all fields', 'Post(title=title,body=body,author_id=g.user.id,tags=tags)', "Approve content fields and derive protected fields on the server."),
    "Search for a hostile-looking SQL string and verify Ben's private title does not appear.",
    fixture('client=app.test_client();login(client,"asha");r=client.get("/posts/",query_string={"q":"\\\' OR 1=1 --"});text=r.get_data(as_text=True);print(r.status_code,"Ben private" not in text)'),
    "Submit an unknown tag and verify the rejected create leaves the post count unchanged.",
    fixture('client=app.test_client();login(client,"asha");r=client.post("/posts/create",data={"title":"Valid","body":"Body","tags":["unknown"],"csrf_token":token(client,"/posts/create")});print(r.status_code)\nwith app.app_context():print(db.session.scalar(db.select(db.func.count()).select_from(Post)))'),
    "Constrain statement structure, object ownership and editable fields independently.",
    [("Can a hidden author_idfield be trusted?","No","Always","If numeric","Visitors can modify hidden form data."),
     ("Does autoescape=Truefor contains make %literal here?","Yes","No","Only for passwords","It escapes LIKE wildcard characters for the declared literal search.")])

lesson(4,"5. Cookies, keys and local database files have different exposure risks",
    "Keep runtime data out of public source while describing the local account scope honestly.",
    [("Persistent signing key; ignored instance directory","The local project creates an ignored instance signing.keyand SQLite file. The key persists across restarts so cookie validation remains stable; it is separate from password hashes."),
     ("Cookie integrity versus confidentiality","Default Flask session contents are signed, not encrypted. This project stores a random login id/token/feedback there, not password hashes or private post bodies.")],
    "A user's password hash does not belong in the cookie, and a signing key does not belong in a public repository. They serve different purposes. "
    "The runtime key is generated only inside the chosen local instance folder and an existing valid key is preserved. Invalid key files fail rather than being silently replaced. "
    "The ignored directory prevents normal accidental source commits but is not operating-system encryption or a guarantee against a compromised machine. "
    "Use fictional accounts in this local learning app. Do not expose the development server to the internet as a finished secure service. "
    "No part of this project reads the user's GitHub token, existing passwords or Study Hub browser storage.",
    'instance/journal.sqlite\ninstance/signing.key\n# Both are local runtime artifacts excluded from source commits.',
    fixture('client=app.test_client();login(client,"asha")\nwith client.session_transaction() as values:\n    print("Login identifier present:",bool(values.get("login_id")))\n    print("No credential/body fields:",all(k not in values for k in ["password","password_hash","body"]))\ncookie=client.get_cookie("session");print(cookie.http_only,cookie.same_site)'),
    "Only nonsecret session identifiers/intent/feedback belong in the signed cookie. HttpOnly and SameSite have roles but do not encrypt its contents.",
    ('# Publish signing.keybecause passwords are hashed', '# Keep key/database local and ignored; hashes do not make runtime files public-safe', "A signing key can permit session tampering; a database contains private records."),
    "Verify the project's config keeps the local HTTP cookie policy explicit.",
    fixture('print(app.config["SESSION_COOKIE_HTTPONLY"],app.config["SESSION_COOKIE_SAMESITE"],app.config["SESSION_COOKIE_SECURE"])',False),
    "Show tampering with a signed cookie does not authenticate the modified value.",
    fixture('client=app.test_client();login(client,"asha");cookie=client.get_cookie("session").value;client.set_cookie("session",cookie+"tampered");print(client.get("/posts/").status_code)'),
    "Treat source, runtime keys, account verifiers and private data as different artifacts with deliberate handling.",
    [("Does password hashing make the signing key safe to publish?","No","Always","Only for local apps","The key has a separate session-integrity role."),
     ("Does .gitignoreencrypt a local database?","No","Always","If nested","It affects source tracking, not filesystem confidentiality.")])

lesson(4,"6. Audit the actual object and session boundaries",
    "Use a permission matrix and failure assertions before trusting a feature.",
    [("Access matrix; negative tests","For each operation test anonymous, own-account and other-account requests, including both GETand POSTwhere relevant. Verify data state after rejection, not just a friendly message."),
     ("Scope audit","This local teaching app does not implement email verification, MFA, password reset, login throttling or a reviewed public deployment. Name missing controls instead of calling a short feature checklist fully secure.")],
    "A meaningful audit turns claims into tested behaviour. For a post, list read/edit/delete and test each identity/ownership case. "
    "Supply a valid token in the wrong-owner write test so it reaches the ownership boundary; otherwise a token failure could hide a missing author check. "
    "After rejection, inspect Ben's post to prove it still exists unchanged. "
    "Replay a revoked cookie and test an expired server session too. The signed-cookie signature is not the only authentication condition. "
    "An audit records both verified controls and explicit deployment limitations. It is not a claim that no future bug can exist.",
    '# Operation x identity: anonymous / owner / other owner\n# Test status and unchanged storage after every denied write.',
    fixture('client=app.test_client();login(client,"asha");csrf=token(client,"/posts/")\nchecks=[("read",client.get("/posts/3").status_code),("edit",client.get("/posts/3/edit").status_code),("delete",client.post("/posts/3/delete",data={"csrf_token":csrf}).status_code)]\nprint(checks)\nwith app.app_context():print("Other post retained:",db.session.get(Post,3).title=="Ben private")'),
    "All three requests are inaccessible while the database record remains intact. Valid CSRF did not override ownership.",
    ('# Test only the owner happy path and call access control complete', '# Test anonymous, owner and other-owner read/write cases', "Negative cases expose object-level gaps."),
    "Test an anonymous read and a signed-in own read in one matrix.",
    fixture('a=app.test_client();b=app.test_client();login(b,"asha");print({"anonymous":a.get("/posts/1").status_code,"owner":b.get("/posts/1").status_code,"other":b.get("/posts/3").status_code})'),
    "Record three controls the local project intentionally does not implement.",
    '''not_implemented=["Email verification","Multi-factor authentication","Internet production deployment"]
print(not_implemented)''',
    "Test the exact boundary your claim describes and report what remains outside the project's scope.",
    [("Why use a valid token in a wrong-owner test?","To reach the owner check","To grant ownership","To reveal the password","A CSRF failure alone would not prove the object rule."),
     ("Does passing a finite test suite prove no security bug can exist?","No","Always","Only on localhost","Tests establish the checked behaviours and limits.")])

lesson(5,"1. Application factories isolate configuration and data",
    "Construct apps with explicit test/local config rather than one global runtime database.",
    [("create_app; LocalConfig; test override","The factory loads a config class, applies explicit overrides, configures the signing key, initialises the extension and registers routes. Tests choose an isolated in-memory database and public fake key."),
     ("Instance path; persistent local artifacts","Normal runs use a local ignored instance folder. Test fixtures supply their own temporary instance path, so examples never open existing learner account databases or key files.")],
    "The same source should support local practice and isolated tests without editing a global database string between runs. "
    "Load config before db.init_appand avoid a global current app or current user. "
    "A test override explicitly selects memory and a fake signing key. Normal local mode uses its ignored instance file and persistent random key. "
    "The example creates two independent in-memory apps and proves a record added to one is absent from the other. "
    "Configuration separation is a practical architecture tool, not a replacement for validating deployment settings.",
    'app=create_app({"TESTING":True,"SECRET_KEY":"test-only","SQLALCHEMY_DATABASE_URI":"sqlite:///:memory:"})',
    '''from lesson_support import practice
from study_app.extensions import db
from study_app.models import User
from werkzeug.security import generate_password_hash
with practice() as first,practice() as second:
    with first.app_context():
        db.session.add(User(username="only_first",password_hash=generate_password_hash("fictional-first-passphrase")));db.session.commit()
        print("First users:",db.session.scalar(db.select(db.func.count()).select_from(User)))
    with second.app_context():
        print("Second users:",db.session.scalar(db.select(db.func.count()).select_from(User)))''',
    "The model metadata is shared source, but engine/database/session scopes belong to their active app. No learner runtime file was used.",
    ('# Edit one global DATABASE_URIin source for every test', '# Pass isolated test config to an application factory', "Tests must not target real saved learner data."),
    "Inspect the explicit testing flag in a practice fixture.",
    fixture('print(app.testing,app.config["SQLALCHEMY_DATABASE_URI"]=="sqlite:///:memory:")',False),
    "Create a fresh practice fixture and confirm there are no accounts before registration.",
    rel('print(db.session.scalar(db.select(db.func.count()).select_from(User)))').replace('practice(seed=True)','practice(seed=False)'),
    "Choose configuration and resource ownership explicitly at construction time.",
    [("Should examples reuse a learner's real journal.sqlite?","No","Always","Only for counts","Use isolated memory/temp resources."),
     ("When is database config loaded?","Before extension initialisation","After every query","In a template loop","The engine uses configuration during binding.")])

lesson(5,"2. Blueprints group routes without duplicating the app",
    "Separate authentication and post features while keeping one extension/factory.",
    [("Blueprint; url_prefix; namespaced endpoint","A blueprint records related routes, then the factory registers it. auth.loginand posts.indexare endpoint names; prefixes such as /authand /postsorganise their URL paths."),
     ("Local imports; circular dependency","An unbound dbextension can live in extensions.py. Models/views import it; the factory imports/registers blueprints after initialisation, reducing circular imports.")],
    "A growing app needs modules, not multiple unrelated global Flask apps. "
    "auth.pyowns registration/login/logout and current-user loading; posts.pyowns owner-scoped CRUD. "
    "Models define schema/relationships, security helpers validate small boundaries, and templates remain presentation resources. "
    "Do not instantiate a new SQLAlchemyextension in every view module or register the same business operation twice. "
    "Blueprint organisation does not itself make a route protected; the decorator and owned lookup still implement behaviour.",
    'auth=Blueprint("auth",__name__,url_prefix="/auth")\napp.register_blueprint(auth)\nurl_for("auth.login")',
    fixture('from flask import url_for\nwith app.test_request_context():\n    print(url_for("auth.login"),url_for("posts.create"))\nprint(sorted(app.blueprints))',False),
    "One app has two feature blueprints and one database extension. Namespaced endpoint names keep link building unambiguous.",
    ('# Create a different global Flask app inside each feature file', '# Register feature blueprints in one configured factory', "Separate modules should compose one application."),
    "Inspect the blueprint endpoint for logout without performing the operation.",
    fixture('print([r.endpoint for r in app.url_map.iter_rules() if r.rule=="/auth/logout"])',False),
    "List the module responsibilities in a small mapping.",
    '''responsibilities={"extensions.py":"One unbound db extension","models.py":"Schema/relationships","auth.py":"Credential/session flow","posts.py":"Owner-scoped CRUD","__init__.py":"App factory/config"}
print(sorted(responsibilities))''',
    "Organise feature boundaries while keeping each security/data rule explicit and shared once.",
    [("Does a blueprint automatically authorise its views?","No","Always","If named auth","It organises registration; route logic implements access rules."),
     ("How many dbextensions should these feature modules share?","One configured extension","A fresh one per route","None","One unbound extension can be initialised by the factory.")])

lesson(5,"3. Trace a complete request through the modular project",
    "Follow token, user load, ownership, validation, commit and rendered response.",
    [("Request pipeline; helper responsibility","The project's POSTtoken check runs before writes; current-user loading resolves a server login; the view applies ownership/field rules; commit changes the database; PRGreturns a read destination."),
     ("Source map","study_app/__init__.pyconfigures/registers; auth.pyhandles accounts; posts.pyhandles CRUD; models.pydefines schema; security.pyholds token/input helpers. This avoids duplicated account logic.")],
    "Read one vertical path through the source before trying to understand every function at once. "
    "For editing, inspect the real rendered form, capture its token, submit only editable fields, resolve owned_postand commit the validated title/body/tags. "
    "If any earlier boundary rejects the request, no update should commit. The follow-up detail GETmust apply ownership again. "
    "The example updates Asha's post with a known tag and verifies its database state. It uses real login and token flow rather than setting g.user by hand. "
    "The full implementation is downloadable as small modules; the next part gives the persistent local run commands.",
    'POST form -> token -> load user -> owned_post -> field checks -> commit ->303-> owner-filtered GET',
    fixture('client=app.test_client();login(client,"asha")\nr=client.post("/posts/1/edit",data={"title":"Routes understood","body":"A view returns a response.","tags":["flask"],"csrf_token":token(client,"/posts/1/edit")},follow_redirects=True)\nprint(r.status_code,"Routes understood" in r.get_data(as_text=True))\nwith app.app_context():\n    post=db.session.get(Post,1);print(post.author.username,post.title,[t.name for t in post.tags])'),
    "The record keeps Asha as author and updates only the approved fields. The returned page is the redirect's safe read result.",
    ('# Scatter separate slightly different owner checks across every feature', '# Reuse one owned_postlookup for detail/edit/delete', "Duplicated access rules drift and create gaps."),
    "Create, read and delete a new Asha post through actual views and verify no unintended rows disappear.",
    fixture('client=app.test_client();login(client,"asha");created=client.post("/posts/create",data={"title":"Temporary","body":"Practice full CRUD","csrf_token":token(client,"/posts/create")});location=created.headers["Location"];print(client.get(location).status_code)\npost_id=int(location.rsplit("/",1)[1]);deleted=client.post(location+"/delete",data={"csrf_token":token(client,location)});print(deleted.status_code,client.get(location).status_code)\nwith app.app_context():print(db.session.scalar(db.select(db.func.count()).select_from(Post)))'),
    "Verify a valid token plus empty edit body rejects the operation without changing the old title.",
    fixture('client=app.test_client();login(client,"asha");r=client.post("/posts/1/edit",data={"title":"Attempted title","body":" ","csrf_token":token(client,"/posts/1/edit")});print(r.status_code)\nwith app.app_context():print(db.session.get(Post,1).title)'),
    "Trace a request boundary by boundary and verify committed state rather than relying on a success-looking page.",
    [("Does the redirect target need owner filtering again?","Yes","Never","Only after login","Every object read must enforce its own access rule."),
     ("Which layer owns the record-ownership lookup?","The server query helper","The hidden form field","The CSS class","The server derives the authenticated owner.")])

lesson(5,"4. Initialise and reopen a persistent local journal",
    "Run the project with an ignored local database and stable runtime signing key.",
    [("Flask CLI init-db; no pre-created accounts","The explicit command creates a new schema and three known tags. It refuses existing tables; it never seeds a hidden default username/password."),
     ("Persistent runtime key versus test key","Normal local mode creates/preserves a random instance signing key. Tests override it only in isolated fixtures. Never commit the real instance directory.")],
    "Keep the complete project folder, install requirements, run python -m flask --app study_app init-db and then python app.py. "
    "Register a new fictional practice account in the browser. Create a post, stop/restart the server, sign in again and verify the record remains. "
    "SQLite persists posts/accounts; the stable local key lets valid unexpired cookie/session records survive a normal restart. Logout still revokes the server login. "
    "Do not rerun init-db as a reset. It refuses existing tables. Changed schemas require a reviewed migration, not a delete-and-recreate shortcut. "
    "For a local backup exercise, stop the app and preserve the ignored database/key together in a protected local backup location; do not upload those runtime files to GitHub.",
    'python -m pip install -r requirements.txt\npython -m flask --app study_app init-db\npython app.py\n# Open http://127.0.0.1:5000',
    '''from tempfile import TemporaryDirectory
from study_app import create_app
from study_app.extensions import db
from study_app.models import Post
from lesson_support import register,login,token
with TemporaryDirectory() as folder:
    first=create_app(instance_path=folder)
    result=first.test_cli_runner().invoke(args=["init-db"])
    print("Initialised:",result.exit_code==0)
    c=first.test_client();register(c,"asha");login(c,"asha")
    c.post("/posts/create",data={"title":"Survives restart","body":"Stored in local SQLite","csrf_token":token(c,"/posts/create")})
    with first.app_context():db.session.remove();db.engine.dispose()
    second=create_app(instance_path=folder)
    with second.app_context():
        print("Saved title:",db.session.scalar(db.select(Post.title)))
        db.session.remove();db.engine.dispose()
    print("Key persisted:",first.config["SECRET_KEY"]==second.config["SECRET_KEY"])
''',
    "This demonstration creates its own temporary instance directory, not a real user folder. The second app reads the same owned database/key and finds the saved record.",
    ('# Drop existing tables when init-db finds data', '# Refuse reinitialisation and plan a reviewed migration', "A setup command must not erase existing accounts/posts."),
    "Run init-db twice on an owned temporary instance and prove the second call refuses.",
    '''from tempfile import TemporaryDirectory
from study_app import create_app
from study_app.extensions import db
with TemporaryDirectory() as folder:
    app=create_app(instance_path=folder)
    runner=app.test_cli_runner()
    print(runner.invoke(args=["init-db"]).exit_code,runner.invoke(args=["init-db"]).exit_code)
    with app.app_context():db.session.remove();db.engine.dispose()
''',
    "Inspect the freshly initialised database and confirm only schema/tags, no user accounts, are present.",
    fixture('with app.app_context():print("Users:",db.session.scalar(db.select(db.func.count()).select_from(User)),"Tags:",db.session.scalar(db.select(db.func.count()).select_from(Tag)))',False),
    "Local persistence needs owned runtime artifacts and a non-destructive initialisation/migration policy.",
    [("Does init-dbreset an existing journal?","No","Always","If no one is signed in","It refuses a database that already has tables."),
     ("Should a real local signing.keybe committed?","No","Always","Because passwords are hashed","It is a runtime session-integrity secret, not source.")])

lesson(5,"5. Build an acceptance suite with two real local accounts",
    "Verify CRUD isolation, persistence and failure cleanup before declaring the project done.",
    [("Two-client acceptance suite","Register/login two independent fictional users, create separate records, attempt wrong-owner operations with valid tokens and compare stored state afterward."),
     ("Layered verification","Unit checks cover validators/hashes; request tests cover forms/access/session behaviour; a real loopback browser covers navigation, CSS, labels and mobile layout. Different tests answer different questions.")],
    "A happy-path screenshot cannot prove account isolation. The acceptance suite must try the operations a different owner is not allowed to perform. "
    "Also test duplicate usernames, malformed tokens, invalid field lengths, tags, literal search, revoked-cookie replay and server-session expiry. "
    "A file-backed temporary instance proves restart persistence without reading any existing real journal. "
    "Use only fictional practice credentials and never dump cookies/hashes into logs. "
    "After sufficient checks pass, stop adding repetitive tests and use the app to learn the whole request/data flow.",
    '# Test owner success + other-owner denial + unchanged database after rejection.',
    fixture('a=app.test_client();b=app.test_client();login(a,"asha");login(b,"ben")\nprint("Asha own/Ben other:",a.get("/posts/1").status_code,b.get("/posts/1").status_code)\nprint("Ben own/Asha other:",b.get("/posts/3").status_code,a.get("/posts/3").status_code)\nb.post("/posts/1/delete",data={"csrf_token":token(b,"/posts/")})\nwith app.app_context():print("Both original owners retained:",db.session.get(Post,1).author.username,db.session.get(Post,3).author.username)'),
    "Both own reads succeed, cross-owner reads fail and a cross-owner delete preserves Asha's record.",
    ('# Test only redirects and skip stored-state assertions', '# Verify the rejected write left the original row unchanged', "A status alone may not prove there was no side effect."),
    "Verify a successful page has local CSSand the expected accessible main target.",
    fixture('client=app.test_client();text=client.get("/").get_data(as_text=True);r=client.get("/static/style.css");print(\'id="main"\' in text,r.status_code);r.close()',False),
    "Check that registration helper source exposes only a known fictional credential label, not a real account input.",
    '''from lesson_support import PRACTICE_PASSWORD
print("Fictional fixture only:",PRACTICE_PASSWORD=="fictional-learning-passphrase")''',
    "Test the stated guarantees with controlled local data, then explain their limits honestly.",
    [("Does a screenshot prove a cross-owner delete is blocked?","No","Always","If styled","That needs a request plus stored-state test."),
     ("Should verification use a real learner password?","No","Always","Only once","Fictional isolated accounts are enough to exercise the behaviour.")])

lesson(5,"6. Milestone: a database-backed multi-user Flask journal",
    "Run accounts, private posts, relationships and modular routes together.",
    [("Complete local milestone","The project combines ORM models/relationships, full post CRUD, registration/login/logout, per-user access, CSRF, escaping, bound expressions, pagination and two blueprints."),
     ("Deployment boundary","It runs locally with a SQLite instance directory. GitHub Pages publishes these lessons/source but cannot execute Flask. Public deployment requires additional operational/account controls, not simply changing the listen address.")],
    "Download docs/python-week38 as a complete folder, including lesson_support.py for executable examples and study_app/templates/static for the local app. "
    "Initialise once, run locally, register two fictional accounts and practise the whole flow in separate browser sessions. "
    "Create/edit/delete your own posts, select known tags and search literally. Try an inaccessible id and observe the consistent 404 response. "
    "Stop/restart and verify persisted records. Sign out and confirm the revoked old server login no longer grants access. "
    "The app does not add account management to the existing Study Hub website or change its localStorage/sync structure. It is the week’s local Python project. "
    "You should now explain where identity is verified, where ownership is enforced, when a transaction commits, how relationships load and why source/runtime files stay separate.",
    'python -m flask --app study_app init-db\npython app.py\n# Register -> Sign in -> Create -> Read -> Edit -> Delete -> Sign out',
    fixture('client=app.test_client();register(client,"asha");login(client,"asha")\ncreated=client.post("/posts/create",data={"title":"My ORM milestone","body":"Identity and ownership are different.","tags":["flask","sql"],"csrf_token":token(client,"/posts/create")})\nlocation=created.headers["Location"];print("Create/read:",created.status_code,client.get(location).status_code)\nchanged=client.post(location+"/edit",data={"title":"Milestone understood","body":"Commit approved changes.","tags":["practice"],"csrf_token":token(client,location+"/edit")});print("Edit:",changed.status_code)\nremoved=client.post(location+"/delete",data={"csrf_token":token(client,location)});print("Delete/read:",removed.status_code,client.get(location).status_code)\nprint("Logout:",client.post("/auth/logout",data={"csrf_token":token(client,"/posts/")}).status_code)',False),
    "This is a complete account/form/CRUD acceptance flow on its own temporary fixture. It never contacts a public account service or reads real credentials.",
    ('# Upload runtime database/key and call static hosting a Flask backend', '# Publish source/lessons; run the Python project locally with private runtime artifacts', "Source distribution and executing a backend are different operations."),
    "Register two fictional accounts and verify each receives an empty private list before creating posts.",
    fixture('a=app.test_client();b=app.test_client();register(a,"asha");register(b,"ben");login(a,"asha");login(b,"ben");print("Asha empty:","No matching posts" in a.get("/posts/").get_data(as_text=True));print("Ben empty:","No matching posts" in b.get("/posts/").get_data(as_text=True))',False),
    "Finish with a database reconciliation of users, posts and three known tags in the seeded fixture.",
    rel('print("Users/posts/tags:",db.session.scalar(db.select(db.func.count()).select_from(User)),db.session.scalar(db.select(db.func.count()).select_from(Post)),db.session.scalar(db.select(db.func.count()).select_from(Tag)))'),
    "A dependable local multi-user app connects identity, ownership, relational data, validated writes and explicit operational scope.",
    [("Does ORM object construction alone commit a row?","No","Always","If it has an id","Persistence needs a completed transaction."),
     ("Does create_allperform general existing-schema migrations?","No","Always","Only for SQLite","Use reviewed migrations instead."),
     ("What identifies a post's owner?","A server-derived author foreign key","A hidden visitor-chosen field","Its CSS class","The verified current account defines ownership."),
     ("Should password hashes be compared by generating another salted string?","No","Always","If stored locally","Use check_password_hash."),
     ("Does login alone authorise every post?","No","Always","Only for CRUD","Each object path needs an owner predicate."),
     ("Is a CSRF token a replacement for ownership checks?","No","Always","For deletes","The controls answer different questions."),
     ("What happens when a stored login is revoked?","Its old cookie no longer authenticates","It remains valid because signed","Every database is erased","The loader requires a valid server record."),
     ("Should deleting one post delete shared tags?","No","Always","If the post had three tags","Only relevant association links are removed."),
     ("What stores private posts durably here?","The local SQLite database","The signed cookie body","A public template","Browser session data is deliberately small."),
     ("Does a blueprint itself enforce authentication?","No","Always","If called auth","It organises routes; explicit logic enforces rules."),
     ("Should instance files enter a public source commit?","No","Always","If passwords are hashed","Runtime keys/data remain local and ignored."),
     ("Does this course change Study Hub progress storage?","No","Always","Only for Flask","It adds teaching data and a separate local project.")])


FOLDER=ROOT/"docs"/"python-week38"


def write():
    target=ROOT/"study-hub.html";original=target.read_bytes().decode("utf-8")
    start=original.index("const DAY_TEACH = {");end=original.index("\n};\n\nconst REST_DAY",start)
    if any(('"'+key+'":') in original[start:end] for key in DAYS):
        if "--refresh" not in sys.argv:raise RuntimeError("Week38 exists; refusing overwrite")
        first=original.index('\n"38.0": {',start)
        if not all(('"'+key+'":') in original[first:end] for key in DAYS):raise RuntimeError("Unexpected Week38 block")
        original=original[:first]+original[end:];end=original.index("\n};\n\nconst REST_DAY",start)
    assert [len(day["parts"]) for day in DAYS.values()]==[6]*6
    public=[FOLDER/"lesson_support.py",*sorted((FOLDER/"study_app").glob("*.py")),
            *sorted((FOLDER/"study_app"/"templates").glob("*.html")),FOLDER/"study_app"/"static"/"style.css"]
    files={str(p.relative_to(FOLDER)).replace("\\","/"):p.read_text(encoding="utf-8") for p in public}
    bootstrap='import sys\nfrom pathlib import Path\nfor name,source in '+repr(files)+'.items():\n    p=Path(name);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(source,encoding="utf-8")\nfor name in list(sys.modules):\n    if name=="lesson_support" or name=="study_app" or name.startswith("study_app."):sys.modules.pop(name,None)\nsys.path.insert(0,str(Path.cwd()))\n'
    with tempfile.TemporaryDirectory(prefix="studyhub-w38-verify-") as temp:
        manifest=Path(temp)/"examples.json";result=Path(temp)/"results.json"
        manifest.write_text(json.dumps([bootstrap+code for code,_ in JOBS]),encoding="utf-8")
        subprocess.run([sys.executable,str(ROOT/"scripts"/"python-example-worker.py"),str(manifest),str(result)],check=True,timeout=300,
            env={**os.environ,"MPLBACKEND":"Agg","OPENBLAS_NUM_THREADS":"1","PYTHONDONTWRITEBYTECODE":"1"})
        results=json.loads(result.read_text(encoding="utf-8"))
    for (_,destination),result in zip(JOBS,results,strict=True):
        destination["v" if destination["t"]=="out" else "out"]=result["out"]
    DAYS["38.0"]["parts"][0]["sections"].insert(3,sec("sh",'python -m pip install -r requirements.txt'))
    DAYS["38.0"]["parts"][0]["sections"].insert(4,sec("tip","Verified with Python3.12.14, Flask3.1.3, Flask-SQLAlchemy3.1.1 and SQLAlchemy2.1.4. Install requirements once; lesson reading and all local fixtures run offline afterward. Days 1–2 use complete in-memory scaffolds. For lesson_support imports, keep that public helper and the full study_app package alongside the snippet. All example accounts/passwords are fictional; temporary databases and keys are owned test resources, never real learner data."))
    final=DAYS["38.5"]["parts"][5]["sections"]
    final.extend([sec("sh","python -m pip install -r requirements.txt\npython -m flask --app study_app init-db\npython app.py\n# Open http://127.0.0.1:5000 ; Ctrl+C stops the local server."),
        sec("p","Project: docs/python-week38 in the repository. Keep app.py, requirements.txt, lesson_support.py and the entire study_app/ folder. Register fictional practice accounts locally. instance/ database/signing-key files are ignored runtime artifacts; do not publish them. GitHub Pages hosts course/source only, not this Flask Python server."),
        sec("p","Primary references: https://flask-sqlalchemy.palletsprojects.com/en/stable/quickstart/ · https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html · https://docs.sqlalchemy.org/en/20/orm/session_basics.html · https://flask.palletsprojects.com/en/stable/tutorial/views/ · https://flask.palletsprojects.com/en/stable/blueprints/ · https://flask.palletsprojects.com/en/stable/web-security/ · https://werkzeug.palletsprojects.com/en/stable/utils/ . Original explanations, fictional fixtures, examples and exercises are embedded for offline reading; source links are optional further reading.")])
    addition="\n".join(json.dumps(k)+": "+json.dumps(v,ensure_ascii=False,indent=2)+"," for k,v in DAYS.items()).replace("</","<\\/")
    prefix=original[:end].rstrip()
    if not prefix.endswith(","):prefix+=","
    temporary=target.with_suffix(".html.tmp")
    temporary.write_bytes((prefix+"\n"+addition+original[end:]).encode("utf-8"));temporary.replace(target)
    print("Added Week38:6days,36parts,72practice prompts,82explained quizzes,108executed examples/solutions; all earlier lessons/application/storage unchanged.")


if __name__=="__main__":
    write()

