"""Engine/session lifetime, explicit commits and reviewed Alembic operations."""
from contextlib import contextmanager
from pathlib import Path
import secrets
from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import URL, create_engine, event, inspect
from sqlalchemy.orm import sessionmaker

HEAD = "w40_003"
REVISIONS = {"w40_001", "w40_002", HEAD}
PROJECT = Path(__file__).resolve().parents[1]


def make_engine(path):
    engine = create_engine(URL.create("sqlite+pysqlite", database=str(Path(path).resolve())),
                           connect_args={"check_same_thread": False, "timeout": 3},
                           pool_size=5, max_overflow=0, pool_pre_ping=True)

    @event.listens_for(engine, "connect")
    def configure(connection, record):
        # SQLAlchemy owns BEGIN, including SELECT/DDL; sqlite3 legacy mode does not.
        connection.isolation_level = None
        cursor = connection.cursor(); cursor.execute("PRAGMA foreign_keys=ON"); cursor.close()

    @event.listens_for(engine, "begin")
    def begin(connection):
        connection.exec_driver_sql("BEGIN")
    return engine


def migration_config(connection):
    config = Config(str(PROJECT / "alembic.ini"))
    config.set_main_option("script_location", str(PROJECT / "migrations"))
    config.attributes["connection"] = connection
    return config


def revision(engine):
    with engine.connect() as connection:
        return MigrationContext.configure(connection).get_current_revision()


def verify_known(connection):
    tables = set(inspect(connection).get_table_names())
    current = MigrationContext.configure(connection).get_current_revision()
    if not tables:
        return None
    if current not in REVISIONS or "alembic_version" not in tables:
        raise RuntimeError("Unfamiliar schema/history; preserve files and review a migration")
    required = {"users", "notes", "token_sessions", "alembic_version"}
    if current in {"w40_002", HEAD}:
        required |= {"tags", "note_tags"}
    if tables != required:
        raise RuntimeError("Unexpected schema tables; no automatic reset attempted")
    return current


def migrate(engine, target="head", *, downgrade=False, allow_destructive=False):
    if downgrade and not allow_destructive:
        raise ValueError("Downgrade requires explicit allow_destructive=True on an owned backup/test copy")
    with engine.begin() as connection:
        verify_known(connection)
        config = migration_config(connection)
        if downgrade:
            command.downgrade(config, target)
        else:
            command.upgrade(config, target)


def initialise(folder):
    folder = Path(folder).resolve(); folder.mkdir(parents=True, exist_ok=True)
    path = folder / "notes.sqlite"
    created = False
    try:
        with path.open("xb"):
            created = True
    except FileExistsError:
        pass
    engine = make_engine(path)
    try:
        if created:
            migrate(engine)
        else:
            with engine.connect() as connection:
                if verify_known(connection) != HEAD:
                    raise RuntimeError("Known older schema; stop server and explicitly run manage.py upgrade")
        key_path = folder / "signing.key"
        try:
            with key_path.open("xb") as file:
                file.write(secrets.token_bytes(32))
        except FileExistsError:
            pass
        key = key_path.read_bytes()
        if len(key) != 32:
            raise RuntimeError("Invalid signing key; existing runtime files preserved")
        return engine, sessionmaker(engine, expire_on_commit=False), key
    except BaseException:
        engine.dispose()
        # Leave even newly created files for investigation; never reset an old instance.
        raise


@contextmanager
def atomic(session):
    """Commit inside the route before returning, including an auth-started transaction."""
    try:
        yield session
        session.commit()
    except BaseException:
        session.rollback()
        raise
