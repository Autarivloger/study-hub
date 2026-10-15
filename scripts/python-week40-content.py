"""Original SQLAlchemy/Alembic lessons, loaded by the Week40 authoring generator."""

def orm(body):
    return '''from sqlalchemy import create_engine, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
class Base(DeclarativeBase):
    pass
class Note(Base):
    __tablename__="notes"
    id:Mapped[int]=mapped_column(primary_key=True)
    title:Mapped[str]=mapped_column(String(100))
engine=create_engine("sqlite://")
Base.metadata.create_all(engine)  # disposable introduction only, not schema migration
try:
    with Session(engine) as session:
'''+textwrap.indent(clean(body),'        ')+'''finally:
    engine.dispose()
'''


def study(body, seed=True):
    return ('from lesson_support import sandbox,query_counter\nfrom orm_api.models import User,Note,Tag,LoginSession,note_tags\n'
            'from sqlalchemy import select,func\nwith sandbox(seed='+str(seed)+') as (engine,sessions):\n'
            '    with sessions() as session:\n'+textwrap.indent(clean(body),'        '))


def fixture(body, seed=True):
    return ('from lesson_support import practice,register,login,PRACTICE_PASSWORD\nwith practice(seed='+str(seed)+') as (app,client,headers):\n'+textwrap.indent(clean(body),'    '))


def migration(body):
    return ('from pathlib import Path\nfrom tempfile import TemporaryDirectory\nfrom sqlalchemy import inspect,text\n'
            'from orm_api.database import make_engine,migrate,revision,migration_config\n'
            'with TemporaryDirectory(prefix="studyhub-w40-migration-") as folder:\n'
            '    engine=make_engine(Path(folder)/"notes.sqlite")\n    try:\n'+textwrap.indent(clean(body),'        ')+'    finally:\n        engine.dispose()\n')


lesson(0,'1. Core and ORM express the same relational task',
 'Choose table expressions or mapped objects while keeping SQL reasoning intact.',
 [('SQLAlchemy Core; ORM','Core builds/executes SQL expressions using tables, columns and rows. The ORM adds mapped classes, identity tracking and a unit of work on top of SQLAlchemy’s engine/expression layer.'),
  ('Engine; dialect; driver','An Engine coordinates a SQL dialect, a DBAPI driver and pooled connectivity. The SQLite dialect translates expressions for SQLite; pysqlite uses Python’s sqlite3 driver.'),
  ('DeclarativeBase; Mapped; mapped_column','Review from Week 38: a declarative base holds mapping metadata, Mapped describes an attribute’s mapped type and mapped_column declares its database column.')],
 'Week 35 taught SQL, Week 38 used Flask-SQLAlchemy and Week 39 used direct sqlite3. This week uses SQLAlchemy directly with FastAPI. '
 'Core suits explicit set-based table work; the ORM suits object graphs and tracked changes. Neither removes keys, constraints, transactions or query planning. '
 'The repeated introductory scaffold defines one tiny Note mapping and a disposable in-memory database. Later helpers expose the complete User/Note/Tag project models. '
 'create_all is appropriate for these new temporary demonstrations, not a general way to evolve an existing database. Day 4 uses versioned migrations. '
 'Pick a layer for the job and test the resulting relational effect rather than treating either layer as magic.',
 'with engine.begin() as connection:\n    connection.execute(Note.__table__.insert(),[{"title":"Core"}])\nwith Session(engine) as session:\n    session.add(Note(title="ORM"));session.commit()',
 orm('with engine.begin() as connection:\n    connection.execute(Note.__table__.insert(),[{"title":"Core insert"}])\nsession.add(Note(title="ORM insert"));session.commit()\nprint(session.scalars(select(Note.title).order_by(Note.id)).all())'),
 'Core and ORM inserted into the same mapped table. The final select returns scalar titles, not independent databases for each layer.',
 ('# Assume ORM data does not obey SQL constraints','Use the same relational constraints whichever layer writes','Both interfaces eventually operate on relational tables.'),
 'Insert two rows through Core and read their titles through the ORM Session.',
 orm('with engine.begin() as c:c.execute(Note.__table__.insert(),[{"title":"A"},{"title":"B"}])\nprint(session.scalars(select(Note.title).order_by(Note.id)).all())'),
 'Insert through the ORM and read an explicit Core row mapping.',
 orm('session.add(Note(title="Mapped object"));session.commit()\nwith engine.connect() as c:\n    row=c.execute(select(Note.__table__.c.title)).mappings().one()\n    print(dict(row))'),
 'Core and ORM are cooperating layers over the same database, not substitutes for relational understanding.',
 [('Does the ORM remove database constraints?','No','Always','Only for SQLite','Both layers use the same constrained tables.'),
  ('What does the Engine coordinate?','Dialect, driver and connectivity','Browser progress only','Password plaintext','It provides the database connectivity/execution foundation.')])

lesson(0,'2. Engine, connection and pool have different lifetimes',
 'Release checked-out connections without rebuilding the engine per query.',
 [('Connection pool; checkout; checkin','A pool reuses DBAPI connections. A Connection checks one out and returns it when closed; it is not the same thing as a long-lived Engine.'),
  ('engine.connect; engine.begin; dispose','connect provides an explicit connection scope; begin also commits/rolls back a transaction. dispose releases idle pooled connections after owned work finishes, not as a per-query ritual.')],
 'Create one engine per application/database configuration, then acquire short-lived connections or sessions for coherent tasks. '
 'File-backed SQLite uses a pool here; the introductory in-memory database has different connection-sharing behaviour and should not be copied blindly into multi-threaded request code. '
 'A bounded pool prevents unbounded connections but does not make SQLite support unlimited simultaneous writes. More connections are not automatically more throughput. '
 'Use context managers to return checked-out resources promptly. dispose does not forcibly make outstanding user-held connections disappear. '
 'The final app owns its engine in lifespan and creates one Session per request.',
 'engine=create_engine(url,pool_size=5,max_overflow=0)\nwith engine.connect() as connection:\n    ...\nengine.dispose()  # owned app/test shutdown',
 migration('with engine.connect() as connection:\n    print(connection.scalar(text("SELECT 7")))\nprint("Checked out after scope:",engine.pool.checkedout())'),
 'The connection is returned to the file-backed engine’s pool after the scope. The pool remains available for later requests.',
 ('def query():\n    engine=create_engine(url)  # rebuild a pool each time','Create the app-owned engine once; scope each connection','Repeated engine creation obscures ownership and wastes resources.'),
 'Open two sequential connection scopes and show neither remains checked out.',
 migration('for _ in range(2):\n    with engine.connect() as c:print(c.scalar(text("SELECT 1")))\nprint(engine.pool.checkedout())'),
 'Inspect only the backend name, not a credential-bearing database URL.',
 migration('print(engine.dialect.name)\nprint("Pool size:",engine.pool.size())'),
 'Keep the engine app-owned and connections task-scoped; pooling is resource reuse, not a concurrency guarantee.',
 [('Should an engine be rebuilt for every query?','No','Always','Only after SELECT','Reuse the configured app engine and release scoped connections.'),
  ('Does a larger pool remove SQLite write contention?','No','Always','Only if max_overflow is zero','Database concurrency rules still apply.')])

lesson(0,'3. Session is a unit of work, not a browser session',
 'Track mapped objects and distinguish flush from commit.',
 [('Session; add; flush; commit','A Session tracks mapped state and a transaction. add makes an object pending; flush sends pending SQL; commit completes the transaction. Flush alone is not durable commit.'),
  ('Autobegin; autoflush','A Session normally starts a transaction when database work begins. It can flush pending work before certain queries, so even a read can reveal an earlier invalid pending write.')],
 'A SQLAlchemy Session is not a login cookie or Study Hub localStorage. It is a scoped unit of database work. '
 'Constructing Note creates a Python object. Adding it schedules persistence; flush obtains generated values while the transaction is still reversible. '
 'Commit makes the approved unit durable; rollback discards it. Closing a Session releases its resources and rolls back unfinished work. '
 'Do not assume a SELECT is harmless if you have invalid pending objects: autoflush can issue writes before that query. '
 'Keep sessions short-lived and never share one mutable Session across independent concurrent requests.',
 'session.add(note)\nsession.flush()\n# generated id exists, but transaction can still roll back\nsession.commit()',
 orm('row=Note(title="Pending")\nprint("Before:",row.id)\nsession.add(row);session.flush()\nprint("After flush:",row.id)\nsession.rollback()\nprint("Rows after rollback:",len(session.scalars(select(Note)).all()))'),
 'Flush assigned an id but rollback removed the insert. An id on a Python object is not proof that its transaction committed.',
 ('session.flush()  # claim data is durably saved','session.commit()  # complete the approved transaction','Flush and commit have different durability boundaries.'),
 'Commit one note and read it in a new Session.',
 orm('session.add(Note(title="Committed"));session.commit()\nwith Session(engine) as other:print(other.scalars(select(Note.title)).all())'),
 'Demonstrate autoflush by adding a note and querying inside the same Session before commit.',
 orm('session.add(Note(title="Autoflush"))\nprint(session.scalars(select(Note.title)).all())\nsession.rollback()\nprint(session.scalars(select(Note.title)).all())'),
 'Track construction, add, flush and commit separately, and name the rollback boundary.',
 [('Does flush alone make a row durable?','No','Always','Only if it has an id','The enclosing transaction can still roll back.'),
  ('Is SQLAlchemy Session the login session?','No','Always','Only in FastAPI','It manages mapped objects/database work, not browser identity.')])

lesson(0,'4. Identity map, expiration and detached objects',
 'Understand object identity within one Session without assuming it is a global cache.',
 [('Identity map; Session.get','A Session maintains one mapped object per database identity while present in its identity map. get can reuse that object; arbitrary filtered queries still normally issue SQL.'),
  ('Expiration; refresh; detach','Commit expires mapped state by default, allowing later access to reload it. Closing detaches objects; unloaded/expired attributes may then need a Session. refresh explicitly reloads current database state.')],
 'Two lookups of the same primary key within one Session can refer to the same Python object. That does not mean every query avoids the database. '
 'A different Session has its own identity map and transaction perspective. Do not use this mechanism as a global application cache. '
 'Default commit expiration is useful but can surprise code trying to serialise objects after closing their Session. '
 'The API uses expire_on_commit=False for its short request scope and constructs public dictionaries before returning; that choice does not promise automatic freshness forever. '
 'Load needed data while the Session is active rather than hiding detached-object problems with a global never-ending Session.',
 'a=session.get(Note,id)\nb=session.get(Note,id)\nprint(a is b)',
 orm('row=Note(title="Identity");session.add(row);session.commit()\nkey=row.id\na=session.get(Note,key);b=session.get(Note,key)\nprint("Same Session object:",a is b)\nwith Session(engine) as other:\n    c=other.get(Note,key)\n    print("Different Session object:",a is c)'),
 'Object identity is scoped to the Session. Matching database ids across sessions do not make their Python objects identical.',
 ('# Session is a permanent globally fresh cache','Use a short Session and reload/refresh intentionally','Identity tracking is not universal query caching or freshness.'),
 'Inspect default expiration after a commit without triggering an attribute reload.',
 orm('from sqlalchemy import inspect\nrow=Note(title="Expires");session.add(row);session.commit()\nprint("Expired:",bool(inspect(row).expired_attributes))'),
 'Show that expire_on_commit=False retains loaded scalar values in a deliberately short Session.',
 orm('with Session(engine,expire_on_commit=False) as other:\n    row=Note(title="Loaded snapshot");other.add(row);other.commit()\nprint(row.title)'),
 'Identity, freshness and lifetime are separate concerns; return deliberate representations rather than uncontrolled detached graphs.',
 [('Is the identity map a global cache across Sessions?','No','Always','Only with integers','Each Session owns its mapped object identity tracking.'),
  ('Does expire_on_commit=False guarantee live forever-fresh values?','No','Always','Only after INSERT','Loaded values can become stale and still have a defined lifetime.')])

lesson(0,'5. Bind values and read result shapes deliberately',
 'Distinguish mapped entities, scalar columns and Core row mappings.',
 [('select; scalars; mappings; one','select builds an expression. scalars returns its first selected column/entity; mappings returns named row mappings. one asserts exactly one result rather than silently accepting a missing/multiple result.'),
  ('Expression parameter binding','Comparing a mapped column to a Python value builds a bound SQL expression. Visitor text stays a value rather than becoming SQL syntax.')],
 'Select a model when you need its mapped object and selected columns when that is all the result needs. '
 'A tuple-like Row, a mapping and a Note object have different interfaces. Know which your execution method returns. '
 'For multiple selected columns, scalars discards all but the first. Use execute(...).all/mappings when every selected value matters. '
 'Bind the search value instead of interpolating it into SQL text. Expressions protect value binding, but raw text() fragments remain your responsibility. '
 'The final app uses owner and id expressions together; binding alone is not authorisation.',
 'session.scalars(select(Note.title)).all()\nsession.execute(select(Note.id,Note.title)).mappings().all()',
 orm('session.add_all([Note(title="HTTP"),Note(title="SQL")]);session.commit()\nprint(session.scalars(select(Note.title).order_by(Note.id)).all())\nprint([dict(r) for r in session.execute(select(Note.id,Note.title).order_by(Note.id)).mappings()])'),
 'The first result is a list of strings; the second keeps both named columns. Choose that shape explicitly.',
 ('sql=f"SELECT * FROM notes WHERE title=\'{title}\'"','select(Note).where(Note.title==title)','Build expressions with bound values rather than inserting user text into SQL source.'),
 'Bind an apostrophe-containing title and retrieve it exactly.',
 orm('value="Learner\'s note";session.add(Note(title=value));session.commit()\nprint(session.scalar(select(Note.title).where(Note.title==value)))'),
 'Show which column scalars returns from a two-column select.',
 orm('session.add(Note(title="Two columns"));session.commit()\nprint(session.scalars(select(Note.id,Note.title)).all())'),
 'Choose both SQL expressions and result shape intentionally; bound values remain data.',
 [('What does scalars return for select(id,title)?','Only the first selected column','Both columns as a dictionary','A new table','scalars extracts the first element from each result row.'),
  ('Does bound parameter use enforce ownership by itself?','No','Always','Only with an ORM','The query must separately include the verified owner predicate.')])

lesson(0,'6. Request-scoped Sessions and the FastAPI refactor',
 'Preserve the HTTP contract while replacing its storage implementation.',
 [('sessionmaker; yielded Session dependency','sessionmaker is a configured Session factory, not a shared Session. The request provider creates one Session, yields it and closes it afterward.'),
  ('Commit before returning; atomic helper','Authentication may already start a transaction through a query. The project’s atomic helper commits that request unit before returning success and rolls back exceptions, rather than opening a conflicting second root transaction.')],
 'The app factory owns engine configuration and the Session factory. The request dependency owns a new Session for that request. '
 'Public schemas, paths, core statuses, strict validation, literal search, owner checks and token revocation remain compatible with Week 39. '
 'The SQL layer changes from sqlite3 calls to mapped models and expressions. Shared tags arrive through additional relationship endpoints rather than changing the original note body contract. '
 'Do not defer a write’s commit until after its success response has already been sent. Build the representation and finish the transaction before returning it. '
 'The project uses synchronous def routes for synchronous ORM/hash work. An AsyncSession design would require its own async driver and per-task lifetime; it is not created by merely adding async def.',
 'with request.app.state.sessions() as session:\n    yield session\n# In a write route: with atomic(session): ...',
 fixture('r=client.post("/v1/notes",headers=headers,json={"title":"ORM refactor","body":"Same client contract"})\nprint(r.status_code,r.headers["Location"])\nprint(sorted(r.json()))\nprint(client.get("/v1/notes",headers=headers).json()["total"])'),
 'The client still receives a 201, member Location and the same public note fields. SQLAlchemy handles the persistence behind that interface.',
 ('global_session=Session(engine)  # share across requests','Create one Session per request from a shared factory','A Session is mutable transactional state, not a thread-safe global resource.'),
 'Verify the existing PATCH False behaviour survives the refactor.',
 fixture('client.patch("/v1/notes/1",headers=headers,json={"completed":True})\nprint(client.patch("/v1/notes/1",headers=headers,json={"completed":False}).json()["completed"])'),
 'Verify logout replay refusal still works after the storage change.',
 fixture('print(client.post("/v1/logout",headers=headers).status_code,client.get("/v1/me",headers=headers).status_code)'),
 'Refactor behind stable contracts, scope each Session and complete approved writes before returning success.',
 [('Should one Session be shared by all concurrent requests?','No','Always','Only with SQLite','Each request needs its own transactional unit.'),
  ('Does adding async def turn a synchronous ORM into an async driver?','No','Always','If it uses Depends','The actual driver and Session interface determine I/O behaviour.')])

lesson(1,'1. Model ownership with keys and relationships',
 'Connect database foreign keys with Python navigation without confusing their jobs.',
 [('ForeignKey; relationship; back_populates','ForeignKey constrains a stored reference. relationship provides object navigation. back_populates pairs the two Python attributes so changes stay coordinated in a Session.'),
  ('User.notes; Note.owner; supplied sandbox','The project’s User owns many Note rows; each Note has one owner. sandbox creates three fictional users, four notes and three shared tags in a disposable migrated database; these placeholder users are not usable login accounts.')],
 'Draw the cardinality first: one user can own zero or many notes, but every note must reference one user. '
 'owner_id is the stored foreign key; owner is a Python mapped relationship. Declaring one does not automatically replace the purpose of the other. '
 'Use explicit back_populates names so you can trace both directions instead of relying on hidden naming. '
 'Mapped non-optional fields imply required values, but actual database rules must still be inspected and enforced. '
 'Our helper owns every file and engine it creates, so direct ORM examples cannot reach real Study Hub notes or accounts.',
 'owner_id:Mapped[int]=mapped_column(ForeignKey("users.id"))\nowner:Mapped[User]=relationship(back_populates="notes")',
 study('user=session.scalar(select(User).where(User.username=="asha"))\nprint(user.username,sorted(n.title for n in user.notes))\nnote=session.scalar(select(Note).where(Note.title=="HTTP"))\nprint(note.owner.username,note.owner_id==user.id)'),
 'Both directions refer to the same ownership relationship. The foreign key supplies integrity; navigation may issue SQL when unloaded.',
 ('owner:Mapped[User]=relationship()  # assume this alone constrains storage','Declare the owner_id foreign key and relationship','Python navigation does not replace a database reference constraint.'),
 'Find a user with no notes and return an empty collection.',
 study('user=session.scalar(select(User).where(User.username=="chen"))\nprint(user.username,len(user.notes))'),
 'Create a note by assigning its owner object and confirm the foreign key after flush.',
 study('owner=session.scalar(select(User).where(User.username=="asha"))\nrow=Note(title="Owned",body="Object assignment",completed=False,created_at="fictional",owner=owner)\nsession.add(row);session.flush()\nprint(row.owner_id==owner.id,row.owner.username)\nsession.rollback()'),
 'Model cardinality, stored references and Python navigation separately, then connect them explicitly.',
 [('What enforces that owner_id refers to a real user?','A database foreign key','Only the attribute name','The note colour','The database constraint protects stored references.'),
  ('Does accessing an unloaded relationship necessarily avoid SQL?','No','Always','Only in a helper','Lazy navigation can issue an additional query.')])

lesson(1,'2. A many-to-many relationship needs an association table',
 'Share tags without duplicating a comma-separated list in each note.',
 [('secondary; association table; composite primary key','secondary tells a relationship which link table connects both entities. The note_tags pair is a composite primary key, preventing duplicate links for the same note and tag.'),
  ('Shared entity versus owned child','A Tag is shared across notes. The link belongs to the association; deleting one note must remove its links without deleting the shared tag itself.')],
 'A note can have several tags and a tag can belong to several notes. A single foreign key on either side cannot represent that pattern alone. '
 'Store each entity once and connect their ids in a link table. This supports indexed joins and duplicate-link constraints. '
 'Do not store "python,api" as a field that every query must split and reinterpret. '
 'The project defines three known shared tags and accepts tag changes through a separate owned member endpoint. '
 'If a link later needs metadata such as assigned_at, consider an association-object model rather than pretending the link has no data.',
 'note_tags=Table("note_tags",Base.metadata,\n    Column("note_id",ForeignKey("notes.id"),primary_key=True),\n    Column("tag_id",ForeignKey("tags.id"),primary_key=True))',
 study('note=session.scalar(select(Note).where(Note.title=="HTTP"))\nprint(note.title,[t.name for t in note.tags])\npython=session.scalar(select(Tag).where(Tag.name=="python"))\nprint(sorted(n.title for n in python.notes))'),
 'One HTTP note has two tags; the python tag is shared with Models. These are separate links to a single shared tag row.',
 ('tags="python,api"  # treat text as a relational link','Use a link table with two foreign keys and a composite key','The association table supports relational integrity and queries.'),
 'Count links independently of the entity counts.',
 study('print("Notes:",session.scalar(select(func.count()).select_from(Note)))\nprint("Tags:",session.scalar(select(func.count()).select_from(Tag)))\nprint("Links:",session.scalar(select(func.count()).select_from(note_tags)))'),
 'Assign an existing shared tag to an untagged note and inspect the resulting names.',
 study('row=session.scalar(select(Note).where(Note.title=="Indexes"))\ntag=session.scalar(select(Tag).where(Tag.name=="database"))\nrow.tags.append(tag);session.flush()\nprint([t.name for t in row.tags]);session.rollback()'),
 'Represent many-to-many membership as constrained links and keep shared entity lifetime separate from one member.',
 [('What prevents duplicate note/tag pairs?','The composite primary key','A comma in a string','The browser checkbox alone','The pair is unique in the association table.'),
  ('Should deleting one note automatically delete its shared tags?','No','Always','Only if it had two tags','Other notes may still reference those tag rows.')])

lesson(1,'3. Constraints express the stored data contract',
 'Pair model declarations with checks that SQLite really enforces.',
 [('CheckConstraint; unique; nullable','CHECK validates a database expression, UNIQUE rejects duplicate key values and NOT NULL rejects missing stored values. String(100) alone does not enforce a 100-character limit in SQLite.'),
  ('Naming convention','Consistent constraint/index names make inspected schemas and migration operations easier to review. Names help management; the actual rule still enforces validity.')],
 'A Pydantic model validates HTTP input, while database constraints protect every write path, including direct scripts. '
 'The title/body checks reject empty/oversized trimmed strings, the Boolean check limits stored completed to 0/1, and username/tag names are unique. '
 'Do not infer SQLite length enforcement from a VARCHAR-looking declaration. Verify the generated CHECK and test a rejected write. '
 'A failed flush requires rollback before the Session can continue normally. We will explore that recovery on Day 5. '
 'Stable constraint names also help reviewers distinguish an intentional schema change from an accidental autogenerate diff.',
 'CheckConstraint("length(trim(title)) BETWEEN 1 AND 100",name="title_length")',
 study('from sqlalchemy import inspect\ninfo=inspect(engine)\nprint(sorted(c["name"] for c in info.get_check_constraints("notes")))\nprint(info.get_unique_constraints("users")[0]["column_names"])'),
 'Inspection shows real named CHECK constraints and the unique username rule, rather than merely trusting Python type annotations.',
 ('mapped_column(String(100))  # assume SQLite rejects longer values','Add appropriate validation and a CHECK constraint','SQLite’s type declaration is not a general string-length validator.'),
 'Attempt a blank title directly, roll back and inspect its original value.',
 study('from sqlalchemy.exc import IntegrityError\nrow=session.get(Note,1);row.title=""\ntry:session.flush()\nexcept IntegrityError:session.rollback();print("CHECK rejected")\nprint(session.get(Note,1).title)'),
 'Inspect the association table’s composite primary key.',
 study('from sqlalchemy import inspect\nprint(inspect(engine).get_pk_constraint("note_tags")["constrained_columns"])'),
 'Validate the database’s actual constraints, not just a model’s apparent types or a form’s limits.',
 [('Does SQLite String(100) alone enforce the length?', 'No','Always','Only with Mapped','Use a meaningful CHECK plus application validation.'),
  ('Why name constraints consistently?','To inspect and manage schema changes clearly','To encrypt their data','To skip validation','Stable names improve review and migration operations.')])

lesson(1,'4. ORM cascades and database cascades are distinct',
 'Delete owned children while preserving shared entities.',
 [('cascade="all, delete-orphan"','An ORM ownership policy can delete a child when removed from its sole parent collection or when its parent is deleted through the ORM. It is inappropriate for independently shared tags.'),
  ('ON DELETE CASCADE; passive_deletes','A database cascade handles foreign-key-dependent row deletion. passive_deletes lets the ORM rely on that database behaviour for unloaded relationships; foreign keys must actually be enabled.')],
 'A User owns Notes and login records, so their lifetime can follow the owner in this local model. A Tag is shared and must not be treated as an owned orphan of one note. '
 'Deleting a note removes note_tags links; it does not remove shared Tag rows. '
 'ORM cascades and database ON DELETE rules cooperate but are not identical. Raw SQL bulk deletion bypasses ORM object-graph logic and relies on database constraints/cascades. '
 'Test both a row count and remaining shared data, especially when adding cascade options. '
 'The API intentionally has no user-delete endpoint; the following ownership-lifetime example uses only a disposable direct ORM sandbox.',
 'notes=relationship(cascade="all, delete-orphan",passive_deletes=True)\n# owned FK uses ondelete="CASCADE"; shared tags do not get delete cascade.',
 study('row=session.get(Note,1)\nsession.delete(row);session.commit()\nprint("Notes:",session.scalar(select(func.count()).select_from(Note)))\nprint("Tags:",session.scalar(select(func.count()).select_from(Tag)))\nprint("Links:",session.scalar(select(func.count()).select_from(note_tags)))'),
 'The deleted note’s links disappear, while all three shared tags remain. Models retains its independent python link.',
 ('tags=relationship(cascade="all, delete")  # for shared tags','Keep tag rows independent; cascade only association links','Deleting shared entities can damage unrelated notes.'),
 'Remove one owned note from its parent collection and verify delete-orphan.',
 study('owner=session.get(User,1)\nowner.notes.remove(next(n for n in owner.notes if n.title=="Models"))\nsession.commit()\nprint(session.scalar(select(func.count()).select_from(Note)),session.scalar(select(func.count()).select_from(Tag)))'),
 'Delete a fictional owner and prove the other owner’s notes and all shared tags survive.',
 study('session.delete(session.get(User,1));session.commit()\nprint(session.scalars(select(Note.title).order_by(Note.id)).all())\nprint(session.scalar(select(func.count()).select_from(Tag)))'),
 'Choose cascade policy from ownership, then prove shared data survives the intended deletion.',
 [('Where is delete-orphan appropriate here?','Notes exclusively owned by one User','Shared Tag rows on every Note','Every relationship automatically','Orphan deletion is an exclusive-ownership lifecycle rule.'),
  ('Can database cascades work if foreign keys are disabled?','Not reliably for the declared FK policy','Always','Only in Python','The database must enforce those foreign-key actions.')])

lesson(1,'5. Manage shared tags through an owned API resource',
 'Validate known links and retain the original note representation contract.',
 [('TagSelection; relationship endpoint','The added PUT /v1/notes/{id}/tags takes a strict {names:[...]} body, rejects duplicates/unknown names and replaces only that owned note’s links.'),
  ('Empty selection versus empty PATCH','An empty names list means remove all tag links and is valid here. That explicit action differs from an empty note PATCH, which the note contract rejects.')],
 'Relationship writes deserve the same identity, owner and transaction rules as scalar writes. '
 'The server resolves known names into Tag objects instead of trusting visitor-provided arbitrary related ids or creating unexpected tags. '
 'Return sorted tag names so callers see a stable representation. The original NoteRead fields stay unchanged. '
 'A cross-owner tag update returns the same 404 policy as cross-owner note updates. '
 'Removing every link is permitted, while deleting a tag from the global catalog is not exposed by this API.',
 'PUT /v1/notes/1/tags\n{"names":["python","api"]}',
 fixture('r=client.put("/v1/notes/1/tags",headers=headers,json={"names":["python","api"]})\nprint(r.status_code,r.json())\nprint(client.get("/v1/notes/1/tags",headers=headers).json())\nprint("tags" in client.get("/v1/notes/1",headers=headers).json())'),
 'The dedicated relation endpoint returns tag names while the ordinary note response remains compatible with Week 39.',
 ('# Trust every supplied tag name and insert it automatically','Resolve only the documented known tag catalog','An explicit relation contract avoids accidental arbitrary related-row creation.'),
 'Reject duplicate and unknown tag names.',
 fixture('for names in [["api","api"],["unknown"]]:\n    print(client.put("/v1/notes/1/tags",headers=headers,json={"names":names}).status_code)'),
 'Clear a note’s tag links and verify the shared catalog remains.',
 fixture('client.put("/v1/notes/1/tags",headers=headers,json={"names":["api"]})\nprint(client.put("/v1/notes/1/tags",headers=headers,json={"names":[]}).json())\nprint(client.get("/v1/tags",headers=headers).json())'),
 'Treat association changes as authorised transactional writes, and distinguish removing a link from deleting shared data.',
 [('What does names:[] mean on this relation endpoint?','Remove this note’s tag links','Delete all shared tags','Do nothing accidentally','An explicit empty replacement clears the selected membership.'),
  ('Can Ben change Asha’s tags with a valid Ben token?','No','Always','If the tag is shared','Shared tags do not remove note ownership restrictions.')])

lesson(1,'6. Verify a relationship model as a whole',
 'Reconcile users, notes and links after coordinated operations.',
 [('Reconciliation; invariants','Reconciliation compares counts and references after work. An invariant such as every note has a real owner should hold through every permitted transition.')],
 'Do not stop at an example that prints one related title. Explain the entire graph and the rules each edge enforces. '
 'Count users, notes, tags and links separately; these counts are not interchangeable. '
 'Verify every note can resolve its owner and every association references actual entities. '
 'Then make a controlled change and compare the preserved parts of the graph. This catches destructive cascade assumptions. '
 'The milestone’s schema now contains the three core domain entities, their association table and revocable login records.',
 '# Counts + reference checks + controlled change + preserved shared data',
 study('counts=[session.scalar(select(func.count()).select_from(model)) for model in [User,Note,Tag,note_tags]]\nprint("Users/notes/tags/links:",counts)\nprint("All notes have owners:",all(n.owner.id==n.owner_id for n in session.scalars(select(Note))))'),
 'The fixture has three users, four notes, three shared tags and three links. One user has zero notes; cardinality permits that.',
 ('assert user_count==note_count  # assume one-to-one','Assert the actual one-to-many/reference invariants','One user can own zero, one or many notes.'),
 'Remove one association and show both linked entities still exist.',
 study('row=session.get(Note,1);tag=next(t for t in row.tags if t.name=="api");tag_id=tag.id\nrow.tags.remove(tag);session.commit()\nprint(session.get(Note,1) is not None,session.get(Tag,tag_id) is not None)'),
 'Join three domain entities and print their connected names.',
 study('rows=session.execute(select(User.username,Note.title,Tag.name).join(User.notes).join(Note.tags).order_by(User.username,Note.title,Tag.name)).all()\nfor row in rows:print(tuple(row))'),
 'A relationship model is ready when its cardinalities, links, constraints and deletion behaviour survive coordinated tests.',
 [('Must user_count equal note_count for one-to-many?','No','Always','Only after commit','The cardinality permits several or zero notes per user.'),
  ('Does removing a many-to-many link require deleting both entities?','No','Always','If it is the last link','The association has a separate lifetime.')])

lesson(2,'1. Filter and order before loading rows',
 'Let the database select the needed owned rows rather than filtering an unrestricted Python list.',
 [('where; order_by; limit; offset','These expression methods build SQL filters, deterministic ordering and page limits before execution. Multiple where predicates combine with AND.'),
  ('is_(False); column expression','Mapped column comparisons produce SQL expressions, not immediate Python Booleans. is_(False) expresses a Boolean database condition; do not use Python is False on the column object.')],
 'Start with the question and its access rule: which incomplete notes belong to this verified owner, in what order, with what maximum size? '
 'Apply those predicates in SQL before transferring rows to Python. Fetching every user’s notes first is wasteful and risks accidental disclosure. '
 'The API’s list query uses a verified owner id and bounded pagination. The direct example uses the known fictional owner id in the sandbox. '
 'Stable order is necessary for meaningful offset pages, though inserts/deletes can still shift later requests. '
 'A column expression is not a Python value; expressions compose a query until the Session executes it.',
 'select(Note).where(Note.owner_id==owner_id,Note.completed.is_(False)).order_by(Note.id).limit(10)',
 study('query=select(Note.title).where(Note.owner_id==1,Note.completed.is_(False)).order_by(Note.id).limit(10)\nprint(session.scalars(query).all())'),
 'Only Asha’s incomplete HTTP note is selected. Ben’s incomplete notes never enter the returned list.',
 ('rows=session.scalars(select(Note)).all()\n# filter ownership afterward','select(Note).where(Note.owner_id==verified_id)','Push the access rule into the query itself.'),
 'Select Ben’s note titles in reverse id order.',
 study('print(session.scalars(select(Note.title).where(Note.owner_id==2).order_by(Note.id.desc())).all())'),
 'Retrieve the second ordered note for Asha as a one-item page.',
 study('print(session.scalars(select(Note.title).where(Note.owner_id==1).order_by(Note.id).offset(1).limit(1)).all())'),
 'Express ownership, filtering, order and limits before execution; avoid unrestricted loads followed by Python access filtering.',
 [('Where should the owner predicate be applied?','In the database query','Only after returning JSON','In CSS','The query should select only authorised rows.'),
  ('What does order_by provide for a page?','An explicit ordering rule','A guarantee no future data changes','Automatic authentication','It defines order but does not freeze later requests.')])

lesson(2,'2. Aggregate with outer joins and the correct count',
 'Include zero-child parents without counting a placeholder row as a child.',
 [('outerjoin; group_by; func.count','An outer join keeps parents with no children. group_by groups matching rows. count(child.id) counts non-null child identifiers; count(*) counts joined rows including an outer placeholder.'),
  ('Database aggregation','Summaries such as totals belong in SQL when individual row objects are unnecessary. It reduces transferred data without changing the need for access rules.')],
 'An inner join omits Chen because Chen has no notes. An outer join preserves Chen with a zero count. '
 'After an outer join, count(*) can count the placeholder row, producing one instead of zero. Count the non-null child key. '
 'Group by the parent id and displayed username explicitly rather than relying on loose backend-specific grouping. '
 'Choose the join direction from the question: all users with their counts differs from only users with notes. '
 'These sandbox summaries are administrative learning queries, not an endpoint exposing every real user’s private statistics.',
 'select(User.username,func.count(Note.id)).outerjoin(User.notes).group_by(User.id,User.username)',
 study('query=select(User.username,func.count(Note.id)).outerjoin(User.notes).group_by(User.id,User.username).order_by(User.username)\nfor row in session.execute(query):print(tuple(row))'),
 'Asha and Ben each have two notes, while Chen remains visible with zero. The selected child-id count handles the missing child correctly.',
 ('func.count()  # assume zero for an outer-joined missing child','func.count(Note.id)','count(*) counts the placeholder joined row; count(child.id) ignores its null id.'),
 'Count all notes without loading their mapped objects.',
 study('print(session.scalar(select(func.count()).select_from(Note)))'),
 'Show only owners with at least two notes using HAVING.',
 study('query=select(User.username,func.count(Note.id)).join(User.notes).group_by(User.id,User.username).having(func.count(Note.id)>=2).order_by(User.username)\nprint([tuple(r) for r in session.execute(query)])'),
 'Use SQL aggregation with a join/count definition that correctly represents zero and multiple children.',
 [('Which count gives zero for a parent with no outer-joined child?','count(child.id)','count(*) always','The parent id string length','The absent child key is null and not counted.'),
  ('What keeps a parent with no matching child?','An outer join','Only an inner join','A CSS wrapper','An outer join preserves the unmatched parent.')])

lesson(2,'3. Joins can multiply rows',
 'Read a three-entity join and deduplicate at the correct layer.',
 [('Join multiplicity; distinct','Joining a note to several tags yields several result rows for that note. SQL DISTINCT can remove repeated selected values when that is the intended result.'),
  ('Entity result versus report rows','A report may intentionally keep each note/tag combination. A list of unique notes should not accidentally repeat the same entity because it matched several tags.')],
 'Draw the join path User -> Note -> note_tags -> Tag. The many-to-many association can create several rows per note. '
 'That multiplication is not a bug by itself: it is the right representation for a report of every note/tag link. '
 'If you want unique notes matching any selected tag, use an appropriate DISTINCT/EXISTS approach rather than assuming the join returns one row per note. '
 'Do not count joined rows as note count without examining multiplicity. '
 'Keep explicit ordering so the displayed report is reproducible and easy to reconcile with the fixture.',
 'select(User.username,Note.title,Tag.name).join(User.notes).join(Note.tags)',
 study('query=select(User.username,Note.title,Tag.name).join(User.notes).join(Note.tags).order_by(Note.id,Tag.name)\nprint([tuple(r) for r in session.execute(query)])\nprint(session.scalars(select(Note.title).join(Note.tags).order_by(Note.id,Tag.name)).all())'),
 'HTTP appears once for api and once for python. A title-only joined result repeats HTTP because there are two matching associations.',
 ('len(joined_rows)  # call this unique note count','Count distinct Note.id when the question asks for unique notes','Join rows and domain entity counts can differ.'),
 'Return unique tagged note titles.',
 study('print(session.scalars(select(Note.title).join(Note.tags).distinct().order_by(Note.title)).all())'),
 'Count distinct tagged note ids without counting links.',
 study('print(session.scalar(select(func.count(func.distinct(Note.id))).join(Note.tags)))'),
 'Choose between relationship-report rows and unique entities consciously; many-to-many joins naturally multiply rows.',
 [('Why does HTTP appear twice in a tag join?','It has two matching tag links','Its id is corrupt','The Session always duplicates inserts','Each joined association contributes a row.'),
  ('What counts unique tagged notes?','count(distinct Note.id)','Every joined row blindly','The number of tag labels','Distinct ids count entities rather than their links.')])

lesson(2,'4. Deliberately create and measure an N+1 query',
 'Count database round trips instead of guessing from a short Python loop.',
 [('N+1 query problem','One query loads N parent rows, then accessing each unloaded child collection triggers another query. A small-looking loop can therefore perform 1+N database round trips.'),
  ('SQLAlchemy event; query_counter','The supplied context helper listens for before_cursor_execute and counts SELECT statements only. It removes its listener afterward and never records SQL parameters or credentials.')],
 'A relationship property looks like a normal Python attribute, but lazy loading may issue SQL when it is first accessed. '
 'The sandbox starts with a fresh Session, so parent collections have not already been loaded by earlier examples. '
 'Measure the exact code path: fetching all users and reading each notes collection. Include users with zero notes because checking their collection can still query. '
 'Do not rely on printed SQL containing password parameters as a debugging habit. A count-only listener is enough for this question. '
 'Round trips are one performance signal; they do not by themselves measure total bytes, row explosion or wall-clock cost.',
 'with query_counter(engine) as counts:\n    users=session.scalars(select(User)).all()\n    sizes=[len(u.notes) for u in users]',
 study('with query_counter(engine) as counts:\n    users=session.scalars(select(User).order_by(User.id)).all()\n    sizes=[len(u.notes) for u in users]\nprint("Child counts:",sizes)\nprint("SELECTs:",counts["selects"])'),
 'One parent query plus three collection queries produces four SELECTs. Even Chen’s empty collection must be checked by the database.',
 ('# Three lines of Python therefore only one SQL query','Instrument the actual database calls in a fresh Session','Python source length does not reveal SQL round trips.'),
 'Read notes without accessing the child collection and count only the parent query.',
 study('with query_counter(engine) as counts:\n    names=session.scalars(select(User.username).order_by(User.id)).all()\nprint(names,counts["selects"])'),
 'Show that a second read of the same already-loaded collection does not repeat its lazy query.',
 study('user=session.get(User,1)\nwith query_counter(engine) as counts:\n    first=len(user.notes);second=len(user.notes)\nprint(first,second,counts["selects"])'),
 'Measure lazy-loading behaviour in a fresh scope; a compact object loop can hide repeated SQL.',
 [('Why can checking an empty collection still issue SQL?','It must establish that no rows exist','It creates a child row','It logs the password','An unloaded collection needs a query even when the result is empty.'),
  ('Does query count alone measure all performance cost?','No','Always','Only on Windows','Rows, bytes, CPU and latency also matter.')])

lesson(2,'5. Fix loading with selectinload and joinedload',
 'Choose a loading strategy that avoids repeated queries without uncontrolled row growth.',
 [('selectinload','This eager loader fetches parents first, then related children with a batched IN query. For this small fixture one collection costs two SELECTs total; larger inputs can require additional batches.'),
  ('joinedload; Result.unique','A joined eager load brings related rows in the parent query. A collection multiplies rows, so call unique on the Result before scalars to assemble unique parent objects.')],
 'For a user list with a collection per user, selectinload is a useful starting point: it keeps the parent result shape clear and batches child loading. '
 'joinedload can work well for small relationships, but several large collections can multiply the transferred rows dramatically. '
 'Count queries and check the result, then consider row volume. Fewer queries are not always faster overall. '
 'Specify the relationship path in query options, not a vague global eager-load-everything policy. '
 'The tag member route uses selectinload(Note.tags), so its response does not accidentally navigate an unloaded collection after the request Session closes.',
 'select(User).options(selectinload(User.notes))\nsession.execute(select(User).options(joinedload(User.notes))).unique().scalars()',
 study('from sqlalchemy.orm import selectinload\nwith query_counter(engine) as counts:\n    users=session.scalars(select(User).options(selectinload(User.notes)).order_by(User.id)).all()\n    sizes=[len(u.notes) for u in users]\nprint(sizes,counts["selects"])'),
 'The same [2,2,0] answer now needs two SELECTs rather than four in this fixture. The benefit comes from the actual loading strategy, not a changed answer.',
 ('session.scalars(select(User).options(joinedload(User.notes))).all()','session.execute(query).unique().scalars().all()','Collection joined loading requires explicit result uniquing.'),
 'Use joinedload with unique and verify one SELECT for this small fixture.',
 study('from sqlalchemy.orm import joinedload\nwith query_counter(engine) as counts:\n    users=session.execute(select(User).options(joinedload(User.notes)).order_by(User.id)).unique().scalars().all()\n    print([len(u.notes) for u in users])\nprint(counts["selects"])'),
 'Eager load note tags and print all names without an N+1 loop.',
 study('from sqlalchemy.orm import selectinload\nwith query_counter(engine) as counts:\n    rows=session.scalars(select(Note).options(selectinload(Note.tags)).order_by(Note.id)).all()\n    print([[t.name for t in n.tags] for n in rows])\nprint(counts["selects"])'),
 'Choose and measure an explicit loading plan, preserving entity results while considering query count and row multiplication.',
 [('How many SELECTs does this small selectin parent/child fixture use?','Two','Always one for all possible sizes','One per child','It batches the children after selecting parents.'),
  ('What does a joinedloaded collection require on the result?','unique()','A new commit','A plaintext password','Join rows must be uniqued into parent entities.')])

lesson(2,'6. Prevent accidental lazy work at response boundaries',
 'Make the required loaded fields explicit and catch unplanned navigation.',
 [('raiseload','raiseload forbids implicit lazy relationship loading for selected paths. Accessing an unloaded prohibited relationship raises an error, making hidden query assumptions visible during development.'),
  ('Public snapshot; Session boundary','Build a small public representation while required state is loaded and the Session is active. Do not return an uncontrolled object graph that may trigger SQL later.')],
 'Once a query’s loading plan is intentional, make accidental extra relationship access visible rather than silently expensive. '
 'Use raiseload in focused tests or query paths where implicit I/O would violate the design. '
 'It is not a database permission control and does not replace owner predicates. It protects an execution assumption. '
 'The API serialises explicit note fields and fetches tags only on the relation endpoint; it never publishes User.password_hash through automatic graph traversal. '
 'A good response boundary has a known shape and known I/O cost instead of depending on which objects happened to stay attached.',
 'select(User).options(raiseload("*"))\n# Access only fields deliberately loaded for this response.',
 study('from sqlalchemy.orm import raiseload\nfrom sqlalchemy.exc import InvalidRequestError\nuser=session.scalar(select(User).where(User.id==1).options(raiseload("*")))\nprint(user.username)\ntry:len(user.notes)\nexcept InvalidRequestError:print("Unplanned lazy load blocked")'),
 'The loaded username is available. Navigating the unloaded notes collection violates the query’s explicit no-lazy policy.',
 ('return an_arbitrary_orm_graph  # let serialization query whatever it touches','Return a deliberate public snapshot with explicit loading','Avoid surprising SQL and private-field exposure during serialisation.'),
 'Build a two-field public user snapshot without a relationship query.',
 study('with query_counter(engine) as counts:\n    user=session.get(User,1)\n    public={"id":user.id,"username":user.username}\nprint(public,counts["selects"])'),
 'Verify the API’s public current-user fields remain limited after refactoring.',
 fixture('print(sorted(client.get("/v1/me",headers=headers).json()))'),
 'Declare loading and public output together so response construction cannot quietly expand I/O or expose internal fields.',
 [('Does raiseload enforce ownership?', 'No','Always','Only with tags','It controls implicit relationship loading, not resource authorisation.'),
  ('Why build explicit public snapshots?','To control exposed fields and required I/O','To remove validation','To bypass transactions','Known output shapes avoid uncontrolled graph traversal.')])

lesson(3,'1. Schema history needs migrations, not repeated create_all',
 'Distinguish initial table creation from controlled evolution of existing data.',
 [('Alembic; revision; upgrade; downgrade','Alembic records ordered schema changes. A revision has an identifier and parent; upgrade applies it and downgrade reverses its declared operations when appropriate.'),
  ('alembic_version; metadata versus history','The version table records applied history. ORM metadata describes the desired current schema. create_all creates missing tables but does not perform arbitrary alterations on existing tables.')],
 'A model edit changes Python declarations, not every existing learner database. Versioned migrations connect desired schema changes to actual stored installations. '
 'Keep migration files immutable after distributing them; importing today’s live model into an old revision would let future model edits rewrite history. '
 'The supplied project has three independent revisions: baseline API tables, shared tags/links and targeted indexes. '
 'Startup migrates only a newly created owned database. It refuses known older or unfamiliar existing schemas rather than silently upgrading or resetting them. '
 'Always stop the app, make and test an owned backup/copy, review the operations and then perform an explicit upgrade.',
 'revision="w40_002"\ndown_revision="w40_001"\ndef upgrade(): ...\ndef downgrade(): ...',
 migration('migrate(engine,"w40_001")\nprint("Applied:",revision(engine))\nprint(sorted(inspect(engine).get_table_names()))'),
 'The baseline creates users, notes, token sessions and Alembic’s version table. Tags are not present until the next revision.',
 ('Base.metadata.create_all(engine)  # assume it evolves every existing table','Use reviewed Alembic revisions for existing-schema changes','create_all is not a general migration engine.'),
 'Apply all three revisions to a fresh temporary database and inspect the head.',
 migration('migrate(engine)\nprint(revision(engine))\nprint(sorted(inspect(engine).get_table_names()))'),
 'Run an already-applied upgrade again and show it stays at head.',
 migration('migrate(engine);first=revision(engine);migrate(engine)\nprint(first,revision(engine))'),
 'Treat model metadata and applied schema history as related but different records of intent and installation state.',
 [('Does create_all alter arbitrary existing columns?', 'No','Always','Only with Mapped','It does not replace a schema migration process.'),
  ('Why avoid importing live models into old revision operations?','Future edits could rewrite historical behaviour','To remove typing','To store a password','Revisions need stable independently declared operations.')])

lesson(3,'2. Evolve through three reviewed revisions',
 'Inspect actual schema changes at each step instead of treating migrations as opaque commands.',
 [('op.create_table; create_index; bulk_insert','Alembic op helpers execute declared schema/data changes. This project’s tag revision inserts a small known catalog, then a later revision adds indexes.'),
  ('Independent migration declarations','Each revision declares only its own historical tables/columns/indexes. The current ORM model is used for comparison, not to silently generate historical operations at runtime.')],
 'Read 001_baseline.py, 002_tags.py and 003_indexes.py in order. Identify what is added and what existing data should remain unchanged. '
 'The baseline establishes accounts/private notes/logins. Revision two adds shared tags and a constrained association table, leaving existing note rows in place. '
 'Revision three adds a composite owner/completed/id index and a tag/note reverse-lookup index. '
 'Record the applied revision after each step and inspect the specific new tables/indexes, not only the command’s exit code. '
 'The examples operate on a temporary database explicitly owned by the lesson; they never run migrations on a real learner’s files.',
 'migrate(engine,"w40_001")\nmigrate(engine,"w40_002")\nmigrate(engine,"w40_003")',
 migration('for target in ["w40_001","w40_002","w40_003"]:\n    migrate(engine,target)\n    names=set(inspect(engine).get_table_names())\n    indexes={i["name"] for i in inspect(engine).get_indexes("notes")}\n    print(revision(engine),"tags" in names,"ix_notes_owner_completed_id" in indexes)'),
 'The sequence shows tags arriving in revision two and the composite filter index in revision three. The baseline tables are retained throughout.',
 ('# Change all old revisions whenever the model changes','Append a new reviewed revision after distributed history','Installed databases depend on the historical sequence remaining stable.'),
 'Inspect the known tag catalog after the second revision.',
 migration('migrate(engine,"w40_002")\nwith engine.connect() as c:print(c.execute(text("SELECT name FROM tags ORDER BY name")).scalars().all())'),
 'Insert a baseline user, upgrade and confirm that row survives.',
 migration('migrate(engine,"w40_001")\nwith engine.begin() as c:c.execute(text("INSERT INTO users(username,password_hash) VALUES(:u,:p)"),{"u":"preserve","p":"fictional-placeholder"})\nmigrate(engine)\nwith engine.connect() as c:print(c.scalar(text("SELECT username FROM users WHERE username=:u"),{"u":"preserve"}))'),
 'Verify the specific schema delta and retained data at every migration step.',
 [('Which revision adds shared tags in this project?','w40_002','Every startup reset','Only the Python model import','The second revision creates tags and links.'),
  ('Should an index-only migration erase existing users?','No','Always','If they have no tags','Its reviewed operations add indexes, not destructive table resets.')])

lesson(3,'3. Autogenerate proposes a diff; a person reviews it',
 'Compare metadata to the database without blindly applying generated operations.',
 [('Autogenerate; compare_metadata; MigrationContext','Alembic can compare current metadata with an inspected database to propose operations. compare_metadata returns a diff for inspection; a revision command can write a candidate migration file.'),
  ('Rename ambiguity; data migration','A column rename can appear as drop/add and lose data if accepted blindly. Backfills, business meaning and rollout order require a deliberate migration design.')],
 'Autogenerate is a useful drafting assistant, not an authority on your data’s meaning. '
 'Compare the known database with Base.metadata, then review types, defaults, constraints, indexes and unexpected drops. '
 'Alembic cannot infer that old_name and new_name represent one renamed field rather than unrelated removed/added fields. '
 'The provided script.py.mako supports generating a revision from an explicitly supplied owned connection. Never point a draft experiment at a real installation casually. '
 'A no-diff result is reassuring about the features compared, but it is not a complete audit of every CHECK, trigger, data rule or application permission.',
 'context=MigrationContext.configure(connection)\ndifferences=compare_metadata(context,Base.metadata)\n# Review, do not auto-approve.',
 migration('from alembic.migration import MigrationContext\nfrom alembic.autogenerate import compare_metadata\nfrom orm_api.models import Base\nmigrate(engine)\nwith engine.connect() as c:\n    changes=compare_metadata(MigrationContext.configure(c),Base.metadata)\nprint("Compared differences:",len(changes))'),
 'The current declared schema matches the compared features of the migrated schema. That does not eliminate separate constraint/data/permission checks.',
 ('# Apply every generated drop/add without review','Review renames, backfills, constraints and destructive operations','The tool compares structures, not the intended meaning of existing data.'),
 'Compare baseline history with current metadata and show pending differences exist.',
 migration('from alembic.migration import MigrationContext\nfrom alembic.autogenerate import compare_metadata\nfrom orm_api.models import Base\nmigrate(engine,"w40_001")\nwith engine.connect() as c:changes=compare_metadata(MigrationContext.configure(c),Base.metadata)\nprint("Pending schema differences:",bool(changes))'),
 'Inspect the supplied migration template without generating a file in the distributed source folder.',
 'from pathlib import Path\nfrom orm_api.database import PROJECT\ntext=(PROJECT/"migrations"/"script.py.mako").read_text(encoding="utf-8")\nprint("upgrade" in text,"downgrade" in text,"Review generated operations" in text)',
 'Use autogenerated diffs as reviewable proposals; schema similarity does not prove safe data evolution.',
 [('Can autogenerate infer every safe rename/backfill?','No','Always','Only with SQLite','Data meaning and migration intent need human review.'),
  ('Does an empty compared diff prove all application permissions?','No','Always','If migrations are at head','It compares supported schema features, not authorisation logic.')])

lesson(3,'4. Roll back one revision on an owned test copy',
 'Prove a reversible index change and recognise a destructive table rollback.',
 [('Downgrade target -1; destructive acknowledgement','-1 selects the previous revision. The project requires explicit allow_destructive=True for any downgrade, because earlier steps may remove tables/data even when the current step only drops indexes.'),
  ('Reversibility versus data recovery','A downgrade can reverse schema operations without restoring data previously lost. Dropping tags and later recreating their tables does not recover old assignments.')],
 'Test the latest revision’s downgrade on a disposable database. It removes two indexes while keeping tables and existing note data. '
 'Then upgrade again and verify the indexes return. This tests the declared pair of operations rather than assuming rollback works. '
 'Rolling back revision two is different: its downgrade drops note_tags and tags, losing those assignments/catalog rows. '
 'Do not advertise downgrade as an automatic backup or a universal undo button. A tested backup is a separate recovery mechanism. '
 'The management command’s explicit flag makes that boundary visible, but the operator must still review the selected revision and stop the server.',
 'migrate(engine,"-1",downgrade=True,allow_destructive=True)\n# Owned disposable/test copy only; review the downgrade first.',
 migration('migrate(engine)\nmigrate(engine,"-1",downgrade=True,allow_destructive=True)\nprint(revision(engine),"tags" in inspect(engine).get_table_names())\nprint("ix_notes_owner_completed_id" in {i["name"] for i in inspect(engine).get_indexes("notes")})\nmigrate(engine)\nprint(revision(engine))'),
 'The database moves from revision three to two, retains tags, loses the index, then returns to head after upgrade.',
 ('# Any downgrade restores every deleted record','Review data-loss effects and test an independent backup','Schema rollback is not historical data recovery.'),
 'Verify a downgrade is refused without the explicit acknowledgement.',
 migration('migrate(engine)\ntry:migrate(engine,"-1",downgrade=True)\nexcept ValueError:print("Explicit acknowledgement required")\nprint(revision(engine))'),
 'Insert a user and prove the latest index downgrade preserves it.',
 migration('migrate(engine)\nwith engine.begin() as c:c.execute(text("INSERT INTO users(username,password_hash) VALUES(:u,:p)"),{"u":"retained","p":"fictional"})\nmigrate(engine,"-1",downgrade=True,allow_destructive=True)\nwith engine.connect() as c:print(c.scalar(text("SELECT count(*) FROM users")))'),
 'Test upgrade/downgrade pairs on owned copies and separate schema reversibility from lost-data recovery.',
 [('Does recreating a dropped link table restore old assignments?','No','Always','Only if named the same','Schema recreation cannot reconstruct deleted relationship data.'),
  ('What does the latest downgrade remove here?','The two new indexes','All users and notes','The signing key','Revision three has index-only reverse operations.')])

lesson(3,'5. Plan an expand, backfill and constrain change',
 'Order schema changes so existing rows can satisfy the new rule.',
 [('Expand/backfill/constrain','First add compatible storage, then populate valid values, then enforce stricter rules after verification. This avoids adding a required column with no value to existing rows.'),
  ('SQLite batch migration','Some SQLite alterations require a table-copy strategy. Alembic batch_alter_table can assist, but foreign keys, data copies and downgrade consequences still need review.')],
 'Imagine adding a required priority field to existing notes. Existing rows need a defined meaning before a NOT NULL rule can safely apply. '
 'Draft a compatible nullable/default stage, backfill a documented value, verify no rows remain invalid, then apply the constraint in a reviewed later step. '
 'Test the proposed SQL/data operation on an owned copy before applying it to an installation. '
 'The executable example practises the pattern on a separate temporary jobs table so the distributed Notes API schema remains exactly its three reviewed revisions. '
 'Do not stamp a legacy Week 39 database as migrated just to bypass history checks; stamping records a version but does not transform or validate its data.',
 '# expand -> backfill -> verify -> constrain\n# Review a SQLite batch migration before a required-column/table-copy change.',
 migration('with engine.begin() as c:\n    c.execute(text("CREATE TABLE jobs(id INTEGER PRIMARY KEY,title TEXT NOT NULL)"))\n    c.execute(text("INSERT INTO jobs(title) VALUES(:t)"),{"t":"Existing row"})\n    c.execute(text("ALTER TABLE jobs ADD COLUMN priority INTEGER"))\n    c.execute(text("UPDATE jobs SET priority=1 WHERE priority IS NULL"))\n    print("Invalid rows before constrain:",c.scalar(text("SELECT count(*) FROM jobs WHERE priority IS NULL")))\n    print(tuple(c.execute(text("SELECT title,priority FROM jobs")).one()))'),
 'The existing row receives the documented priority value before a stricter rule is considered. This example stops before a table-copy constraint migration.',
 ('# Add NOT NULL with no backfill plan on existing rows','Expand compatibly, backfill, verify and only then constrain','Existing data must satisfy the new requirement.'),
 'Write a concrete ordered migration checklist as data, including backup and validation.',
 'steps=["Stop writes and test backup","Add compatible field","Backfill documented values","Verify no invalid rows","Apply reviewed constraint","Run contract/data checks"]\nfor number,step in enumerate(steps,1):print(number,step)',
 'Show that an unknown existing schema is refused and its data remains intact.',
 migration('with engine.begin() as c:\n    c.execute(text("CREATE TABLE unrelated(value TEXT)"));c.execute(text("INSERT INTO unrelated VALUES(\'preserve\')"))\ntry:migrate(engine)\nexcept RuntimeError:print("Unknown schema refused")\nwith engine.connect() as c:print(c.scalar(text("SELECT value FROM unrelated")))'),
 'Safe evolution must account for existing values and recovery, not merely the desired final model.',
 [('When should a new required rule be enforced on old rows?','After a verified compatible backfill','Before deciding existing values','Only in CSS','Existing rows need valid values before stricter storage rules.'),
  ('Does stamping history transform a legacy database?','No','Always','Only with tags','It records history; it does not perform schema/data conversion.')])

lesson(3,'6. Verify migration history and restart policy',
 'Check head, drift and retained data before starting the updated app.',
 [('Explicit upgrade; startup refusal','Known older schemas require a stopped-server management operation. Startup accepts only the expected head and expected table set; unfamiliar history is preserved and refused.'),
  ('Schema drift boundary','The project checks revision/table shape, not every externally edited column/constraint. Use inspection, autogenerate review, data checks and backups for a broader drift audit.')],
 'Before restart, inspect the current revision, run the reviewed upgrade and recheck head plus the relevant data/constraints. '
 'A successful command exit is insufficient if the wrong database path was selected; deliberately choose an owned instance. '
 'The project’s management commands require an already existing instance file rather than silently creating a new empty file due to a path typo. '
 'A new teaching instance automatically receives three migrations. Existing older instances never auto-upgrade as a side effect of a normal page request. '
 'Keep the Week 39 source/runtime folder separate. This week refactors source and gives a safe new practice installation, not an implicit migration of real older accounts.',
 'python manage.py current\npython manage.py upgrade\npython app.py',
 migration('migrate(engine,"w40_002")\nprint("Before:",revision(engine))\nmigrate(engine)\nprint("After:",revision(engine))\nwith engine.connect() as c:print("Foreign keys:",c.scalar(text("PRAGMA foreign_keys")))'),
 'The explicit operation moves the known history to head while per-connection foreign-key enforcement remains enabled.',
 ('# Ignore revision mismatch and run the new model anyway','Stop, review and explicitly upgrade the correct owned instance','Model/schema mismatch can cause failures or corrupt assumptions.'),
 'Check the full expected table set at head.',
 migration('migrate(engine)\nexpected={"users","notes","token_sessions","tags","note_tags","alembic_version"}\nprint(set(inspect(engine).get_table_names())==expected)'),
 'Verify a new sandbox is already at the reviewed head.',
 study('from orm_api.database import revision,HEAD\nprint(revision(engine)==HEAD)'),
 'Require known history and deliberate upgrade/restart checks; never silently reset or stamp unfamiliar existing data.',
 [('Should opening a page silently upgrade an older real schema?','No','Always','If it has a version table','Schema changes need a reviewed explicit operational step.'),
  ('Does a revision/table-set check audit every possible drift?','No','Always','Only in SQLite','It is a limited safeguard, not complete schema/data verification.')])

lesson(4,'1. Define one atomic business change',
 'Commit related writes together and roll them back together on failure.',
 [('Session.begin context; atomicity','A begin context commits if its body completes and rolls back if it raises. Atomicity means this unit succeeds or fails together, not that every concurrent business conflict disappears.'),
  ('Read-started transaction','SQLAlchemy autobegin may already start a transaction during authentication or lookup. Do not blindly start a second root begin block inside that active transaction.')],
 'Decide the business boundary before choosing where to commit. Changing a note and its tag links should not leave half of the intended operation durable. '
 'For a fresh standalone Session, with session.begin is a clear transaction frame. '
 'In the API, identity lookup already uses that request Session. Its atomic helper commits or rolls back the active unit instead of opening another root transaction. '
 'Commit inside the route before returning a successful response. A cleanup-only commit could discover a failure after a response was already sent. '
 'A read-only request can close its unfinished read transaction without committing any write.',
 'with session.begin():\n    # all approved related writes\n    ...',
 study('with session.begin():\n    row=session.get(Note,1)\n    row.title="One approved unit"\n    row.completed=True\nprint(session.get(Note,1).title,session.get(Note,1).completed)'),
 'Both fields complete in one transaction. No extra commit inside the block divides that business unit into smaller durable pieces.',
 ('update_title();session.commit();update_links()  # pretend all-or-nothing','Commit the coherent change only after all required steps pass','An early commit cannot be rolled back by a later failure.'),
 'Change two notes together and verify both results after commit.',
 study('with session.begin():\n    session.get(Note,1).completed=True\n    session.get(Note,3).completed=True\nprint(session.get(Note,1).completed,session.get(Note,3).completed)'),
 'Raise an expected learning error inside a begin block and verify both fields retain their original values.',
 study('try:\n    with session.begin():\n        row=session.get(Note,1);row.title="Unapproved";row.completed=True\n        raise ValueError("Fictional rejection")\nexcept ValueError:print("Whole unit rolled back")\nrow=session.get(Note,1);print(row.title,row.completed)'),
 'Choose a coherent transaction boundary and complete it before reporting success.',
 [('Can a later rollback undo an earlier completed commit?','No','Always','If it used ORM objects','Commit already completed that earlier transaction.'),
  ('Why not blindly call begin after authentication queried?','Autobegin may already have started a transaction','Because authentication removes all transactions','Because Python cannot use contexts','Use the actual active request unit deliberately.')])

lesson(4,'2. Recover a failed Session with rollback',
 'Handle an integrity failure without continuing to use failed transactional state.',
 [('IntegrityError; PendingRollbackError','A failed flush can leave the Session needing an explicit rollback. Further database work before recovery can raise PendingRollbackError rather than working normally.'),
  ('Failure-state cleanup','Rollback restores the transactional boundary; it is not permission to swallow the error or falsely report success. Translate only expected failures into a meaningful public result.')],
 'A uniqueness or CHECK failure is not merely a printed warning. It changes the usable state of the current Session. '
 'Catch the expected IntegrityError, roll back and then perform new work only after recovery. '
 'Avoid catching every exception as Username unavailable; programming bugs and operational outages need different handling. The registration route’s limited write scope makes its expected uniqueness translation clear. '
 'Do not print exception parameters if they can contain private input or password verifiers. '
 'A recovered Session should still see the original valid row, proving that the failed attempt did not silently damage it.',
 'try:session.flush()\nexcept IntegrityError:\n    session.rollback()\n    # report the rejected operation truthfully',
 study('from sqlalchemy.exc import IntegrityError,PendingRollbackError\nsession.add(User(username="asha",password_hash="fictional"))\ntry:session.flush()\nexcept IntegrityError:\n    print("Duplicate rejected")\n    try:session.scalar(select(func.count()).select_from(User))\n    except PendingRollbackError:print("Rollback required")\n    session.rollback()\nprint("Users after recovery:",session.scalar(select(func.count()).select_from(User)))'),
 'The failure is not ignored. A query before recovery is blocked, rollback restores usability and the original three users remain.',
 ('except IntegrityError: pass\n# keep querying the failed Session','except IntegrityError: session.rollback()','Session state must be recovered before new work.'),
 'Reject an empty body at database level and verify the stored original afterward.',
 study('from sqlalchemy.exc import IntegrityError\nsession.get(Note,1).body=""\ntry:session.flush()\nexcept IntegrityError:session.rollback()\nprint(session.get(Note,1).body)'),
 'Verify the API returns a duplicate-name conflict and still accepts a later valid login.',
 fixture('print(register(client,"asha").status_code)\nprint(client.get("/v1/me",headers=login(client,"asha")).status_code)'),
 'An expected failure needs rollback and an honest result; a failed Session is not ready for unrelated new queries.',
 [('What restores a failed flush’s Session boundary?','rollback()','Ignoring the exception','Printing Saved','Explicit rollback recovers the transactional state.'),
  ('Should raw integrity exception parameters be returned publicly?','No','Always','If the site is offline','They may include internal schema or private values.')])

lesson(4,'3. Prove foreign keys and duplicate-link integrity',
 'Test database rules through direct writes that bypass the API models.',
 [('Connection event; PRAGMA foreign_keys','SQLite requires foreign-key enforcement on each relevant connection. The engine’s connect listener applies the setting; one successful setting on a different connection is insufficient.'),
  ('Duplicate association; referential integrity','A link must point to existing note/tag rows and its pair must be unique. Validate those rules with actual failed writes, not only schema names.')],
 'Pydantic can reject a bad request while a maintenance script still writes directly. Database integrity is the last shared boundary across those paths. '
 'The model’s nonnullable owner foreign key rejects an unknown owner when SQLite enforcement is active. '
 'The association table’s composite key rejects a repeated note/tag pair. '
 'Each rejected direct operation is rolled back so the following verification uses a clean Session. '
 'Constraint checks should preserve the original counts and links after the rejection.',
 'ForeignKey("users.id",ondelete="CASCADE")\n# enable enforcement on every connection',
 study('from sqlalchemy.exc import IntegrityError\nrow=Note(owner_id=999,title="Unknown owner",body="Rejected",completed=False,created_at="fictional")\nsession.add(row)\ntry:session.flush()\nexcept IntegrityError:session.rollback();print("Foreign key rejected")\nprint("Notes retained:",session.scalar(select(func.count()).select_from(Note)))'),
 'The unmapped owner id is rejected by storage, and the four original valid notes remain.',
 ('# Validate foreign keys only in a browser form','Declare/enforce/test database references too','Other write paths can bypass the UI and HTTP models.'),
 'Attempt to insert an existing association pair and inspect the unchanged link count.',
 study('from sqlalchemy.exc import IntegrityError\npair=session.execute(select(note_tags).limit(1)).mappings().one()\ntry:session.execute(note_tags.insert(),dict(pair));session.commit()\nexcept IntegrityError:session.rollback();print("Duplicate pair rejected")\nprint(session.scalar(select(func.count()).select_from(note_tags)))'),
 'Inspect foreign-key enforcement through two independently acquired connection scopes.',
 migration('for _ in range(2):\n    with engine.connect() as c:print(c.scalar(text("PRAGMA foreign_keys")))'),
 'Integrity requires actual per-connection enforcement and failure-path tests beyond the request-validation layer.',
 [('Why enable foreign keys per connection?','SQLite enforcement is connection-specific','It changes HTML styling','It creates users automatically','A separate pooled connection needs the same enforcement setting.'),
  ('Which database rule rejects a repeated note/tag pair?','The association composite primary key','Only the username unique rule','The number of API routes','The pair of foreign keys is itself the primary key.')])

lesson(4,'4. Savepoints isolate a recoverable inner failure',
 'Keep an approved outer transaction while rejecting one nested attempt.',
 [('Savepoint; begin_nested','A savepoint marks a point inside a transaction. Session.begin_nested creates one; its rollback can reject the inner work while the outer transaction remains active.'),
  ('Pre-savepoint flush','begin_nested flushes pending state before creating the savepoint. Invalid pending outer work can therefore fail before the nested boundary exists.')],
 'Sometimes a batch should retain approved work while skipping one expected conflicting item. A savepoint can define that smaller recoverable boundary. '
 'Use it intentionally; it is not a reason to swallow every exception or accept a partly completed business operation that should be atomic. '
 'The example adds one valid user outside the savepoint and attempts a duplicate inside it. '
 'Catch the expected integrity failure outside the nested context, let its rollback complete and then commit the outer scope. '
 'Our engine explicitly controls SQLite BEGIN so SELECTs, DDL and savepoints follow a coherent transaction policy instead of legacy sqlite3 surprises.',
 'with session.begin():\n    approved_work()\n    try:\n        with session.begin_nested(): risky_item()\n    except IntegrityError: handle_expected_conflict()',
 study('from sqlalchemy.exc import IntegrityError\nwith session.begin():\n    session.add(User(username="dina",password_hash="fictional"))\n    try:\n        with session.begin_nested():\n            session.add(User(username="asha",password_hash="fictional"));session.flush()\n    except IntegrityError:print("Inner duplicate rolled back")\nprint(session.scalars(select(User.username).order_by(User.username)).all())'),
 'Dina survives the approved outer transaction, while the duplicate Asha attempt does not. The original Asha account remains unchanged.',
 ('# Assume begin_nested never flushes earlier pending work','Flush/validate outer work and understand the pre-savepoint flush','The nested API flushes pending changes before creating its savepoint.'),
 'Roll back an explicit nested edit and preserve the approved outer title.',
 study('with session.begin():\n    row=session.get(Note,1);row.title="Outer approved";session.flush()\n    try:\n        with session.begin_nested():\n            row.title="Inner rejected";session.flush();raise ValueError("Reject inner edit")\n    except ValueError:pass\nprint(session.get(Note,1).title)'),
 'Show an outer exception still rolls back everything, even after a successful savepoint.',
 study('try:\n    with session.begin():\n        with session.begin_nested():session.get(Note,1).title="Nested success"\n        raise ValueError("Outer rejection")\nexcept ValueError:pass\nprint(session.get(Note,1).title)'),
 'Savepoints are scoped partial rollback tools inside a deliberately chosen business transaction, not substitutes for atomicity decisions.',
 [('Can an outer rollback undo a released savepoint’s changes?', 'Yes','Never','Only without SQLite','The outer transaction still owns the final durability boundary.'),
  ('Does begin_nested flush pending state first?', 'Yes','Never','Only when empty','Understand that boundary before relying on its isolation.')])


def versioned(body):
    return '''from sqlalchemy import create_engine,String
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column,Session
from sqlalchemy.orm.exc import StaleDataError
class Base(DeclarativeBase):pass
class Item(Base):
    __tablename__="versioned_items"
    id:Mapped[int]=mapped_column(primary_key=True)
    title:Mapped[str]=mapped_column(String)
    version:Mapped[int]=mapped_column(default=1)
    __mapper_args__={"version_id_col":version}
engine=create_engine("sqlite://")
Base.metadata.create_all(engine)
try:
    with Session(engine) as seed:
        seed.add(Item(title="Original"));seed.commit()
'''+textwrap.indent(clean(body),'    ')+'finally:\n    engine.dispose()\n'


lesson(4,'5. Transactions do not automatically solve lost updates',
 'Recognise stale edits and practise optimistic version checking separately.',
 [('Lost update; optimistic version column','A stale writer can overwrite a more recent edit if no conflict policy exists. SQLAlchemy version_id_col includes a tracked row version in ORM UPDATE/DELETE checks and raises StaleDataError if the expected version no longer matches.'),
  ('StaleDataError; scope limitation','Version checking applies to mapped-instance flush operations, not every bulk/raw SQL operation. The main Notes API retains Week 39 last-writer behaviour; this separate model teaches a possible future improvement.')],
 'Atomic commit means all of one unit is durable together; it does not mean a stale client’s intended edit is automatically merged correctly. '
 'For collaborative editing, choose a conflict strategy such as a revision/ETag condition and a documented retry/merge policy. '
 'The standalone example loads a stale object, closes that reader, applies a newer edit in another Session, then tries to save the stale object. '
 'Closing the first read scope keeps this deterministic example focused on stale state rather than SQLite lock scheduling. '
 'Do not claim the Notes API implements optimistic conflict protection merely because this optional learning example demonstrates it.',
 '__mapper_args__={"version_id_col":version}\n# Handle StaleDataError as a conflict, not a successful save.',
 versioned('with Session(engine) as reader:stale=reader.get(Item,1)\nwith Session(engine) as writer:\n    writer.get(Item,1).title="Newer edit";writer.commit()\nwith Session(engine) as late:\n    stale.title="Stale overwrite";late.add(stale)\n    try:late.commit()\n    except StaleDataError:late.rollback();print("Stale update rejected")\nwith Session(engine) as check:print(check.get(Item,1).title)'),
 'The stale version cannot overwrite the newer row, so Newer edit survives. This is version checking rather than a benchmark of concurrent locking.',
 ('# Every transaction automatically merges stale client intent','Choose and test an explicit conflict policy','Atomicity and conflict detection solve different problems.'),
 'Make a fresh mapped update and show the version increments.',
 versioned('with Session(engine) as s:\n    row=s.get(Item,1);before=row.version;row.title="Fresh";s.commit()\n    print(before,row.version)'),
 'Explain the main API’s current update policy as an explicit statement.',
 'policy={"main_notes_api":"last-writer behaviour; no version field/ETag contract","separate_example":"mapped-instance optimistic version check"}\nfor key,value in policy.items():print(key+": "+value)',
 'Separate atomicity, locking and stale-edit detection, and describe which policy the actual application implements.',
 [('Does atomic commit automatically merge stale edits correctly?','No','Always','Only with a pool','Conflict detection/merge policy needs separate design.'),
  ('Does this main Notes API add a version/ETag contract?','No','Always','Only after login','The optional separate model demonstrates the concept without changing the API contract.')])

lesson(4,'6. Prove transaction and ownership boundaries together',
 'Verify that a failed authorised operation cannot partially mutate stored data.',
 [('Failure acceptance test','After an invalid or unauthorised request, compare the original representation and relationships. Status alone may miss an earlier unintended mutation.'),
  ('Contract-preserving storage refactor','Request formats, status semantics, owner scoping and token policy should survive a storage refactor even though SQL execution and object lifetimes change.')],
 'Combine the rules rather than testing each in isolation only. A valid token does not authorise another owner’s tags, and a valid note body cannot change owner_id. '
 'Try rejected scalar and relationship writes, then read as the owner and compare the original data. '
 'Follow a successful write with a new Session read to prove the route committed before returning. '
 'Keep the API’s error output free of raw private validation inputs and ORM exception parameters. '
 'These checks are part of the completed project’s acceptance suite and use only fictional accounts in temporary instances.',
 '# Reject -> owner reads unchanged data -> new Session sees approved committed writes.',
 fixture('client.put("/v1/notes/1/tags",headers=headers,json={"names":["api"]})\nben=login(client,"ben")\nr=client.put("/v1/notes/1/tags",headers=ben,json={"names":["database"]})\nprint(r.status_code,client.get("/v1/notes/1/tags",headers=headers).json())\nprint(client.patch("/v1/notes/1",headers=headers,json={"owner_id":2}).status_code)'),
 'A shared catalog does not make another person’s note editable. Both association ownership and writable-field limits remain enforced.',
 ('# Success status alone proves the whole data invariant','Assert relevant committed and preserved state too','Status is one part of the acceptance contract.'),
 'Verify a successful API update is visible through a fresh ORM Session.',
 fixture('from orm_api.models import Note\nclient.patch("/v1/notes/1",headers=headers,json={"title":"Durably approved"})\nwith app.state.sessions() as s:print(s.get(Note,1).title)'),
 'Send a unique short fictional secret and verify it is absent from the validation response.',
 fixture('marker="x7Q!z"\nr=client.post("/v1/users",json={"username":"new_user","password":marker})\nprint(r.status_code,marker not in r.text)',False),
 'A correct transaction boundary includes approved commit, rejected-write preservation and unchanged authorisation policy.',
 [('Can a shared tag catalog authorise editing another owner’s note?','No','Always','Only if the tag exists','The note’s ownership still controls the association write.'),
  ('When should a write success be returned?','After its commit succeeds','Before attempting commit','Whenever the form was valid','Persistence can still fail after input validation.')])

lesson(5,'1. Inspect a query plan before adding an index',
 'Connect predicates and ordering to a measured database access path.',
 [('Index; EXPLAIN QUERY PLAN','An index provides an alternative lookup/order path with storage and write cost. SQLite EXPLAIN QUERY PLAN describes a chosen access strategy; it does not itself time a query.'),
  ('Composite index; leading columns','An index on owner/completed/id fits equality filters on owner/completed and then ordered ids. Column order matters; an index does not accelerate every possible filter on its columns.')],
 'Begin with a real query and representative data, not a rule to index every field. '
 'The supplied experiment inserts 20,000 fictional measurements and runs the same bounded owner/completed query before and after one composite index. '
 'It inspects plans, checks identical rows and records seven execution samples per case. '
 'A plan using an index can still be a poor overall query; selectivity, row count, sorting and result size matter. '
 'The Notes project has an owner/id listing index and an owner/completed/id index for the more selective filtered workload demonstrated directly in the lessons.',
 'EXPLAIN QUERY PLAN SELECT id FROM measurements\nWHERE owner=? AND done=? ORDER BY id LIMIT 20',
 'from lesson_support import index_experiment\nr=index_experiment()\nprint("Before scan:",r["before_scan"])\nprint("After named index:",r["after_index"])\nprint("Same rows:",r["same_rows"],"Returned:",r["rows"])',
 'The experiment verifies an actual scan-to-index plan change while preserving the result. It does not infer performance solely from the index name existing.',
 ('# Add indexes everywhere without examining queries','Inspect the target predicate/order and compare actual plans','Indexes cost storage and write maintenance and must fit a workload.'),
 'Inspect the project’s notes index names after its third migration.',
 study('from sqlalchemy import inspect\nprint(sorted(i["name"] for i in inspect(engine).get_indexes("notes")))'),
 'Run the experiment and assert result correctness independently of timing.',
 'from lesson_support import index_experiment\nr=index_experiment()\nassert r["same_rows"] and r["rows"]==20\nprint("Index change preserved the answer")',
 'Use a real query, representative data, a chosen plan and an identical-result check before claiming an index helped.',
 [('Does EXPLAIN QUERY PLAN directly measure elapsed time?','No','Always','Only after login','It reports the selected access strategy.'),
  ('Does a composite index help every arbitrary column filter equally?','No','Always','Only on SQLite','Leading columns and the actual predicate/order matter.')])

lesson(5,'2. Measure elapsed time without promising a fixed speedup',
 'Compare repeated samples and report the limits of a local microbenchmark.',
 [('perf_counter; median; warm cache','perf_counter measures elapsed intervals. Median reduces sensitivity to one outlier. Repeated local queries warm caches, so this experiment does not represent every cold or concurrent workload.'),
  ('Correctness before speed','Both implementations must return the same intended rows. A faster query that leaks another owner’s data or omits required results is not an optimisation.')],
 'The helper measures the actual database execute/fetch interval seven times before and after the index and reports the median. '
 'The displayed output is one verified run on this authoring machine, not a universal performance target. Your timings will vary. '
 'The experiment is small, local and mostly warm-cache; network latency, concurrent writes and large result transfer are outside it. '
 'Report the plan change and correctness alongside timing. Do not force a flaky test assertion that every run must achieve a particular speed ratio. '
 'Use repeatable workload measurements to decide whether the index’s read benefit justifies its write/storage cost.',
 'start=perf_counter()\nrows=connection.execute(query,parameters).all()\nelapsed_ms=(perf_counter()-start)*1000',
 'from lesson_support import index_experiment\nr=index_experiment()\nprint("Sample median milliseconds:",round(r["before_ms"],4),round(r["after_ms"],4))\nprint("Same result:",r["same_rows"])',
 'These measured numbers belong to one local run. The invariant is the identical result and observed access path, not a promised constant multiplier.',
 ('assert indexed_time < baseline_time/100  # fixed universal claim','Compare repeated representative samples and document variability','Machine load, caches and workload shape change measured timing.'),
 'Verify the timing samples are valid nonnegative intervals without demanding a fixed ratio.',
 'from lesson_support import index_experiment\nr=index_experiment()\nprint(r["before_ms"]>=0,r["after_ms"]>=0,r["same_rows"])',
 'Write the benchmark limitations explicitly as a concise report.',
 'report={"rows":20000,"samples_per_case":7,"statistic":"median execute/fetch milliseconds","limits":"local warm-cache microbenchmark; no concurrent/network workload"}\nfor key,value in report.items():print(key+":",value)',
 'Measure representative work repeatedly, preserve correctness and state the scope of any performance result.',
 [('Why avoid an exact universal timing assertion?','Timings depend on workload and machine state','Because queries never take time','Because indexes cannot help','Microbenchmark results are not fixed cross-machine constants.'),
  ('What must remain identical after optimisation?','The authorised intended result','Only the CSS','The SQL source text','Performance work must preserve correctness and access rules.')])

lesson(5,'3. Reduce round trips and unnecessary data transfer',
 'Compare selecting a few columns with loading full objects and lazy graphs.',
 [('Projection; scalar query; payload volume','Projection selects only needed columns. If a report needs title and completed, loading bodies, password verifiers or every relationship is unnecessary work and can increase exposure risk.'),
  ('Query count versus row/byte count','One huge join can transfer far more data than two smaller batched queries. Count-only improvements need row/volume reasoning as well.')],
 'Choose where work happens: filter, count, order and limit in SQL when possible, then perform only required application formatting in Python. '
 'A summary can use aggregate SQL rather than loading every Note object just to call len. '
 'Use narrow projections for reports; use entity objects when tracked mutation or explicit relationship navigation is genuinely needed. '
 'Keep public response models separate from internal projection choices so an optimisation does not add private columns to the API. '
 'Do not sacrifice ownership predicates or validation in exchange for a smaller query-count number.',
 'select(Note.title,Note.completed).where(Note.owner_id==user_id).order_by(Note.id)',
 study('query=select(Note.title,Note.completed).where(Note.owner_id==1).order_by(Note.id)\nprint([dict(row) for row in session.execute(query).mappings()])\nprint("Owned count:",session.scalar(select(func.count()).select_from(Note).where(Note.owner_id==1)))'),
 'The report loads only two required columns for Asha’s notes. The count is calculated by SQL instead of materialising another graph.',
 ('len(session.scalars(select(Note)).all())  # count every loaded object','session.scalar(select(func.count()).select_from(Note))','Ask the database for a count when individual entities are unnecessary.'),
 'Return only known tag names, not entire related note bodies.',
 study('print(session.scalars(select(Tag.name).order_by(Tag.name)).all())'),
 'Count Asha’s incomplete notes without loading the rows.',
 study('print(session.scalar(select(func.count()).select_from(Note).where(Note.owner_id==1,Note.completed.is_(False))))'),
 'Optimise the amount and location of work, not just the number of Python lines or SQL calls.',
 [('What is projection?','Selecting only the needed columns','Changing a password hash','Deleting related rows','A narrower result can reduce transfer and object work.'),
  ('Is one enormous join always better than two batched queries?','No','Always','Only with tags','Row multiplication and transferred volume can outweigh query-count savings.')])

lesson(5,'4. Bulk operations trade object lifecycle for set-based work',
 'Use expression-based bulk changes deliberately and preserve constraints/ownership.',
 [('Bulk INSERT; parameter list','Executing insert(Model) with a list of dictionaries can batch a set of row values. It does not automatically provide the same object graph/lifecycle behaviour as constructing and tracking every instance.'),
  ('Bulk UPDATE/DELETE; synchronisation','Set-based operations can affect many rows without normal per-object navigation. ORM synchronisation and database cascades/constraints need deliberate consideration; versioned-instance guarantees do not automatically cover arbitrary bulk SQL.')],
 'For a controlled import, a batch insert can reduce Python object overhead. Validate the source data and keep the batch transaction boundary clear. '
 'A set-based owner-filtered update can express one coherent change without loading each note. '
 'Do not omit ownership because a bulk statement looks administrative. Do not assume ORM delete-orphan hooks run for a raw/bulk delete. '
 'Database constraints and foreign-key cascades remain necessary for paths that bypass object-graph operations. '
 'The API retains explicit member CRUD; these bulk examples are direct sandbox lessons rather than newly exposed unrestricted bulk endpoints.',
 'session.execute(insert(Note),list_of_validated_dicts)\nsession.execute(update(Note).where(Note.owner_id==owner).values(completed=True))',
 study('from sqlalchemy import update\nresult=session.execute(update(Note).where(Note.owner_id==1).values(completed=True))\nsession.commit()\nprint("Affected:",result.rowcount)\nprint(session.scalars(select(Note.completed).where(Note.owner_id==2).order_by(Note.id)).all())'),
 'Only Asha’s two rows change. Ben’s incomplete values remain False, proving the set-based write kept its owner predicate.',
 ('session.execute(update(Note).values(completed=True))  # forget owner scope','Add the intended owner predicate and verify unaffected rows','A bulk write magnifies the consequence of a missing access condition.'),
 'Insert two validated sandbox notes in one parameter-list operation.',
 study('from sqlalchemy import insert\nrows=[{"owner_id":1,"title":title,"body":"Validated batch","completed":False,"created_at":"fictional"} for title in ["Batch A","Batch B"]]\nsession.execute(insert(Note),rows);session.commit()\nprint(session.scalar(select(func.count()).select_from(Note)))'),
 'Bulk-delete Asha’s notes and prove shared tags survive database cascades.',
 study('from sqlalchemy import delete\nsession.execute(delete(Note).where(Note.owner_id==1));session.commit()\nprint(session.scalar(select(func.count()).select_from(Note)),session.scalar(select(func.count()).select_from(Tag)),session.scalar(select(func.count()).select_from(note_tags)))'),
 'Use set-based work for a clear workload while preserving validation, owner scope, database integrity and honest lifecycle assumptions.',
 [('Do arbitrary bulk statements guarantee per-object delete-orphan processing?','No','Always','Only for two rows','Set-based SQL can bypass normal object-graph lifecycle operations.'),
  ('What must a per-owner bulk update retain?','The verified owner predicate','Only a title length','A CSS class','Bulk speed does not remove access-control requirements.')])

lesson(5,'5. Profile the complete refactor and verify its contract',
 'Combine query evidence, migrations and client-visible behaviour before declaring success.',
 [('Layered acceptance evidence','Direct ORM checks cover relationships/cascades/query plans, request tests cover API/auth contracts, and a real local browser covers the offline explorer, controls and responsive layout.'),
  ('Refactor regression boundary','Preserve earlier lessons/application storage and the original API interface while adding new isolated lesson/project files. Verify both old behaviour and the new database implementation.')],
 'Start with the promised invariants: private CRUD, strict models, meaningful statuses, password hashing, verified/revocable tokens and persistent data. '
 'Add relationship checks for known tags, cross-owner refusal and link deletion without shared-tag deletion. '
 'Add schema checks for three revisions, preserved data, reviewed downgrade and refusal of unknown history. '
 'Then measure N+1 versus eager loading and the scan/index experiment, preserving exact answers. '
 'A browser check alone cannot establish these storage/security properties, and a unit test alone cannot prove the local explorer works on a phone-width layout.',
 '# Preserve contract + prove schema/relationships + measure query work + test local UI.',
 fixture('client.put("/v1/notes/1/tags",headers=headers,json={"names":["api","python"]})\nprint(client.get("/v1/notes/1/tags",headers=headers).json())\nprint(client.delete("/v1/notes/1",headers=headers).status_code)\nprint(client.get("/v1/tags",headers=headers).json())'),
 'The member’s association links disappear after deletion, but its shared tag catalog remains usable.',
 ('# The page looks fine, so migrations and isolation must work','Use the test boundary that actually enforces each claim','Different tests supply different evidence.'),
 'Verify the migrated schema and loaded graph agree on known tag names.',
 study('from orm_api.database import revision\nprint(revision(engine),session.scalars(select(Tag.name).order_by(Tag.name)).all())'),
 'Verify public docs/schema and the protected identity boundary are still distinct.',
 fixture('print(client.get("/docs").status_code,client.get("/openapi.json").status_code,client.get("/v1/me").status_code)',False),
 'Refactor confidence comes from compatible client behaviour plus explicit database, loading, migration and UI evidence.',
 [('Can a screenshot prove migration data preservation?','No','Always','Only on mobile','That needs database/history/data assertions.'),
  ('What should a storage refactor preserve for existing clients?','The documented interface contract','Every internal implementation detail','A private database in public Git','Clients rely on paths, inputs, outputs and semantics.')])

lesson(5,'6. Milestone: the SQLAlchemy Notes API',
 'Run the refactored API with relationships, reviewed migrations and measured queries.',
 [('Complete Week 40 milestone','The local project refactors Week 39 CRUD/auth onto scoped SQLAlchemy Sessions, preserves its base contract, adds shared-tag relationships, three Alembic revisions and measured query-loading/index experiments.'),
  ('Source refactor versus real data conversion','Week 39 remains intact. This week creates a new separate practice instance; it does not secretly migrate, stamp, overwrite or read a real older instance. A real data conversion needs a reviewed backup/copy migration plan.')],
 'Keep docs/python-week40 together, including migrations, alembic.ini, orm_api/static and lesson_support.py. Install requirements once and run python app.py. '
 'Open http://127.0.0.1:8001/docs. The original local explorer reads the generated schema and now includes the relation endpoints. '
 'Register fictional users, perform private CRUD, assign known tags, clear links and verify other-owner requests fail. '
 'Inspect current migration history and practise upgrade/downgrade only on an owned disposable copy after reviewing the data-loss effects. '
 'Run the query counter and index experiment; explain why query count, transferred rows and measured time are related but different. '
 'The project remains a loopback teaching server with the Week 39 operational limits. GitHub Pages hosts lessons/source, not this Python process. Next week’s roadmap adds testing, quality and operational readiness in depth.',
 'python -m pip install -r requirements.txt\npython app.py\n# http://127.0.0.1:8001/docs\n# Stop server before explicit manage.py operations.',
 fixture('register(client,"asha");headers=login(client,"asha")\nr=client.post("/v1/notes",headers=headers,json={"title":"Week 40 milestone","body":"Contracts, relationships and measured queries"})\nurl=r.headers["Location"];print("Create/read:",r.status_code,client.get(url,headers=headers).status_code)\nprint("Tags:",client.put(url+"/tags",headers=headers,json={"names":["api","database"]}).json())\nprint("Patch False:",client.patch(url,headers=headers,json={"completed":False}).json()["completed"])\nprint("Delete/read:",client.delete(url,headers=headers).status_code,client.get(url,headers=headers).status_code)\nprint("Logout/replay:",client.post("/v1/logout",headers=headers).status_code,client.get("/v1/me",headers=headers).status_code)',False),
 'This flow uses the real ORM, transaction, auth, ownership, relation and response code against an owned temporary migrated instance.',
 ('# Publish instance/database and signing key with the course','Publish source; keep ignored runtime artifacts private','The teaching server’s runtime data is not course distribution content.'),
 'Reconcile the direct ORM sandbox’s three core entity counts and links.',
 study('print([session.scalar(select(func.count()).select_from(model)) for model in [User,Note,Tag,note_tags]])'),
 'Run the independent index experiment as a final correctness/plan check.',
 'from lesson_support import index_experiment\nr=index_experiment()\nprint(r["same_rows"],r["before_scan"],r["after_index"],r["rows"])',
 'A dependable database refactor preserves contracts, models ownership correctly, evolves schema deliberately and supports performance claims with measured evidence.',
 [('Does ORM convenience remove SQL reasoning?','No','Always','Only with SQLite','Constraints, joins, transactions and plans still matter.'),
  ('Is Session a safe global object for all requests?','No','Always','If the pool has five connections','It is mutable transactional state with a scoped lifetime.'),
  ('Does flush equal durable commit?','No','Always','If an id exists','The transaction can still roll back.'),
  ('What stores a many-to-many membership?','A constrained association table','A comma-separated password','Only the CSS','Foreign-key pairs represent links between shared entities.'),
  ('Should deleting a note delete shared tags?','No','Always','If it has two tags','Only its association links should be removed.'),
  ('What fixes this small N+1 collection example?','An explicit selectin eager load','Renaming the Python loop','Disabling owner checks','It batches child loading while preserving the answer.'),
  ('Does create_all replace Alembic evolution?','No','Always','Only after commit','Versioned existing-schema changes need migration operations.'),
  ('Does autogenerate safely infer every rename?','No','Always','Only with named constraints','Review data meaning, backfills and destructive proposals.'),
  ('Can a downgrade recover all dropped data?','No','Always','If its function exists','Schema reversal is not restoration of historical values.'),
  ('Does a transaction automatically detect every stale edit?','No','Always','If it uses a pool','Conflict policy is separate from atomic commit.'),
  ('What must an optimisation preserve?','The authorised correct result','Only the query count','A fixed universal speed ratio','Measure work without changing intended data/access semantics.'),
  ('Does this addition change Study Hub progress storage?','No','Always','Only with migrations','It adds lesson data and a separate local project.')])
