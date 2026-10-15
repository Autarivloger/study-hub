"""Public fictional fixtures; no access to real accounts, key files or databases."""
from contextlib import contextmanager
from tempfile import TemporaryDirectory
from study_app import create_app
from study_app.extensions import db
from study_app.models import User,Post,Tag
from werkzeug.security import generate_password_hash
import re

PRACTICE_PASSWORD="fictional-learning-passphrase"


@contextmanager
def practice(*,seed=False):
    with TemporaryDirectory(prefix="studyhub-w38-example-") as folder:
        app=create_app({"TESTING":True,"SECRET_KEY":"public-test-key-not-deployment",
                        "SQLALCHEMY_DATABASE_URI":"sqlite:///:memory:"},instance_path=folder)
        with app.app_context():
            db.create_all()
            db.session.add_all([Tag(name=v) for v in ["flask","sql","practice"]])
            if seed:
                a=User(username="asha",password_hash=generate_password_hash(PRACTICE_PASSWORD))
                b=User(username="ben",password_hash=generate_password_hash(PRACTICE_PASSWORD))
                db.session.add_all([a,b]);db.session.flush()
                db.session.add_all([Post(author_id=a.id,title="Routes",body="A request selects a view."),
                                    Post(author_id=a.id,title="Queries",body="Bind values."),
                                    Post(author_id=b.id,title="Ben private",body="Only Ben can access this.")])
            db.session.commit()
        try:
            yield app
        finally:
            with app.app_context():
                db.session.remove();db.engine.dispose()


def token(client,path="/auth/login"):
    response=client.get(path)
    match=re.search(r'name="csrf_token" value="([^"]+)"',response.get_data(as_text=True))
    if not match:raise AssertionError("Expected a real rendered form token")
    return match.group(1)


def register(client,username):
    return client.post("/auth/register",data={"username":username,"password":PRACTICE_PASSWORD,
                                            "csrf_token":token(client,"/auth/register")})


def login(client,username):
    return client.post("/auth/login",data={"username":username,"password":PRACTICE_PASSWORD,
                                         "csrf_token":token(client)})
