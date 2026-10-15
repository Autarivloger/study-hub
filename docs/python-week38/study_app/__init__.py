from pathlib import Path
import secrets
import sqlite3
import click
from flask import Flask,render_template,request
from sqlalchemy import event,inspect
from werkzeug.security import generate_password_hash
from .config import LocalConfig
from .extensions import db
from .security import check_csrf,csrf_token


def local_key(path):
    try:
        with path.open("xb") as handle:
            handle.write(secrets.token_bytes(32))
    except FileExistsError:
        pass
    value=path.read_bytes()
    if len(value)!=32:
        raise ValueError("Invalid local signing-key file; do not silently replace it")
    return value


def create_app(test_config=None,*,instance_path=None):
    arguments={"instance_path":str(Path(instance_path).resolve())} if instance_path else {}
    app=Flask(__name__,instance_relative_config=True,**arguments)
    app.config.from_object(LocalConfig)
    if test_config:app.config.update(test_config)
    if not app.config.get("SECRET_KEY"):
        Path(app.instance_path).mkdir(parents=True,exist_ok=True)
        app.config["SECRET_KEY"]=local_key(Path(app.instance_path)/"signing.key")
    app.config["DUMMY_PASSWORD_HASH"]=generate_password_hash("public-dummy-not-an-account")
    db.init_app(app)
    # Enable foreign keys on every SQLite connection belonging to this app engine.
    with app.app_context():
        @event.listens_for(db.engine,"connect")
        def sqlite_rules(connection,record):
            if isinstance(connection,sqlite3.Connection):
                cursor=connection.cursor();cursor.execute("PRAGMA foreign_keys=ON");cursor.close()
    from . import models,auth,posts
    app.before_request(lambda:check_csrf(request))
    app.register_blueprint(auth.bp)
    app.register_blueprint(posts.bp)

    @app.context_processor
    def helpers():return {"csrf_token":csrf_token}

    @app.get("/")
    def home():return render_template("home.html")

    @app.errorhandler(400)
    @app.errorhandler(404)
    @app.errorhandler(405)
    @app.errorhandler(413)
    def invalid(error):
        response=app.make_response((render_template("error.html",code=error.code,message=error.description),error.code))
        if error.code==405 and error.valid_methods:response.headers["Allow"]=", ".join(error.valid_methods)
        return response

    @app.after_request
    def headers(response):
        response.headers["Cache-Control"]="no-store"
        response.headers["X-Content-Type-Options"]="nosniff"
        return response

    @app.cli.command("init-db")
    def init_db():
        if inspect(db.engine).get_table_names():
            raise click.ClickException("Database already has tables; refusing reinitialisation. Use a reviewed migration.")
        db.create_all()
        db.session.add_all([models.Tag(name=value) for value in ["flask","sql","practice"]])
        db.session.commit()
        click.echo("Created new local journal schema and three tags. No accounts were pre-created.")

    return app
