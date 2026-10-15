"""Week38 acceptance uses only fictional accounts and owned memory/temp databases."""
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import re
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"docs"/"python-week38"))
from lesson_support import practice,token,register,login,PRACTICE_PASSWORD
from study_app import create_app,local_key
from study_app.extensions import db
from study_app.models import User,Post,Tag,LoginSession,post_tags
from sqlalchemy.exc import IntegrityError
from sqlalchemy import inspect,text
from werkzeug.security import check_password_hash


def count(model):
    return db.session.scalar(db.select(db.func.count()).select_from(model))


with practice() as app:
    a=app.test_client();b=app.test_client()
    assert a.get("/").status_code==200
    assert a.get("/posts/").status_code==303
    assert a.get("/auth/logout").status_code==405
    assert "POST" in a.get("/auth/logout").headers["Allow"]
    assert a.get("/unknown").status_code==404
    css=a.get("/static/style.css");assert css.status_code==200;css.close()
    # Form/token boundaries must not create accounts.
    for candidate in ["","wrong","日本語","x"*129]:
        assert a.post("/auth/register",data={"username":"asha","password":PRACTICE_PASSWORD,"csrf_token":candidate}).status_code==400
    short=a.post("/auth/register",data={"username":"asha","password":"tiny","csrf_token":token(a,"/auth/register")})
    assert short.status_code==400 and 'value="tiny"' not in short.get_data(as_text=True)
    with app.app_context():assert count(User)==0
    assert register(a," Asha ").status_code==303
    with app.app_context():
        original=db.session.scalar(db.select(User).where(User.username=="asha"))
        original_hash=original.password_hash
        assert original_hash!=PRACTICE_PASSWORD and check_password_hash(original_hash,PRACTICE_PASSWORD)
        assert "password" not in User.__table__.columns
    assert register(a,"ASHA").status_code==400
    with app.app_context():
        assert count(User)==1
        assert db.session.scalar(db.select(User.password_hash).where(User.username=="asha"))==original_hash
    assert register(b,"ben").status_code==303 # rollback left later registration usable
    for name in ["unknown","asha"]:
        r=a.post("/auth/login",data={"username":name,"password":"wrong-practice-password","csrf_token":token(a)})
        assert r.status_code==400 and "Invalid username or password." in r.get_data(as_text=True)
    old_token=token(a)
    assert login(a,"asha").status_code==303
    assert login(b,"ben").status_code==303
    with a.session_transaction() as state:
        assert "login_id" in state and all(k not in state for k in ["user_id","password","password_hash","body"])
    assert a.post("/posts/create",data={"title":"Stale","body":"Must not save","csrf_token":old_token}).status_code==400
    # Asha creates one private post, browser-supplied author_id cannot take effect.
    made=a.post("/posts/create",data={"title":"100% focus","body":"<script>window.demoXSS=true</script>\nSecond line",
        "tags":["flask","sql"],"author_id":"2","csrf_token":token(a,"/posts/create")})
    assert made.status_code==303
    location=made.headers["Location"];post_id=int(location.rsplit("/",1)[1])
    html=a.get(location).get_data(as_text=True)
    assert "&lt;script&gt;" in html and "<script>" not in html
    assert "Post created in your local database." in html
    assert "Post created in your local database." not in a.get(location).get_data(as_text=True)
    with app.app_context():
        post=db.session.get(Post,post_id)
        assert post.author.username=="asha" and sorted(t.name for t in post.tags)==["flask","sql"]
        assert count(Post)==1 and count(Tag)==3
    assert "100% focus" not in b.get("/posts/").get_data(as_text=True)
    assert b.get(location).status_code==404 and b.get(location+"/edit").status_code==404
    assert b.post(location+"/edit",data={"title":"Stolen","body":"Should fail","csrf_token":token(b,"/posts/")}).status_code==404
    assert b.post(location+"/delete",data={"csrf_token":token(b,"/posts/")}).status_code==404
    with app.app_context():assert db.session.get(Post,post_id).title=="100% focus"
    # All invalid form variants leave the approved row unchanged.
    for values in [
        {"title":"","body":"Body"},{"title":"x"*101,"body":"Body"},
        {"title":"Good","body":" "},{"title":"Good","body":"x"*2001},
        {"title":"Good","body":"Body","tags":["unknown"]},
        {"title":"Good","body":"Body","tags":["sql","sql"]},
        {"title":"Good","body":"Bad\x00text"},
    ]:
        values={**values,"csrf_token":token(a,location+"/edit")}
        assert a.post(location+"/edit",data=values).status_code==400
        with app.app_context():assert db.session.get(Post,post_id).title=="100% focus"
    foreign=token(b,"/posts/create")
    assert a.post("/posts/create",data={"title":"Wrong session token","body":"Body","csrf_token":foreign}).status_code==400
    assert a.post("/posts/create",data={"title":"Big","body":"x"*40000,"csrf_token":token(a,"/posts/create")}).status_code==413
    with app.app_context():assert count(Post)==1
    # Literal search and pagination operate only on Asha's population.
    assert "100% focus" in a.get("/posts/",query_string={"q":"%"}).get_data(as_text=True)
    assert "No matching posts" in a.get("/posts/",query_string={"q":"' OR 1=1 --"}).get_data(as_text=True)
    for page in ["banana","0","1001","２"]:
        assert a.get("/posts/",query_string={"page":page}).status_code==400
    assert a.get("/posts/",query_string={"q":"x"*81}).status_code==400
    with app.app_context():
        asha=db.session.scalar(db.select(User).where(User.username=="asha"))
        db.session.add_all([Post(author_id=asha.id,title=f"Extra {i}",body="Fictional pagination") for i in range(6)])
        db.session.commit()
    assert "7 matching post(s)" in a.get("/posts/").get_data(as_text=True)
    assert 'rel="next"' not in b.get("/posts/").get_data(as_text=True)
    assert "No matching posts" in b.get("/posts/").get_data(as_text=True)
    # Owned edit and delete with FK association cleanup, shared tags retained.
    changed=a.post(location+"/edit",data={"title":"Updated","body":"Approved update","tags":["practice"],"csrf_token":token(a,location+"/edit")})
    assert changed.status_code==303
    with app.app_context():
        assert db.session.get(Post,post_id).title=="Updated"
        assert [t.name for t in db.session.get(Post,post_id).tags]==["practice"]
    assert a.get(location+"/delete").status_code==405
    assert a.post(location+"/delete",data={"csrf_token":token(a,location)}).status_code==303
    with app.app_context():
        assert db.session.get(Post,post_id) is None and count(Tag)==3
        assert db.session.scalar(db.select(db.func.count()).select_from(post_tags))==0
        assert db.session.scalar(text("PRAGMA foreign_keys"))==1
        db.session.add(Post(author_id=999,title="Invalid author",body="Must fail"))
        try:db.session.commit()
        except IntegrityError:db.session.rollback()
        else:raise AssertionError("Foreign-key enforcement missing")
        assert count(Post)==6
    # Logout revocation rejects replay; another independent Asha login survives.
    other=app.test_client();login(other,"asha")
    old_cookie=a.get_cookie("session").value
    cookie=a.get_cookie("session")
    assert cookie.http_only and cookie.same_site=="Lax" and not cookie.secure
    assert a.post("/auth/logout",data={"csrf_token":token(a,"/posts/")}).status_code==303
    a.set_cookie("session",old_cookie)
    assert a.get("/posts/").status_code==303 and other.get("/posts/").status_code==200
    with other.session_transaction() as state:sid=state["login_id"]
    with app.app_context():db.session.get(LoginSession,sid).expires_at=0;db.session.commit()
    assert other.get("/posts/").status_code==303
    ben_cookie=b.get_cookie("session").value
    b.set_cookie("session",ben_cookie+"tampered")
    assert b.get("/posts/").status_code==303

# File-backed fixture: initialisation refuses existing data, rows/key survive restart.
with TemporaryDirectory(prefix="studyhub-w38-persist-") as temp:
    folder=Path(temp)
    first=create_app(instance_path=temp)
    runner=first.test_cli_runner()
    assert runner.invoke(args=["init-db"]).exit_code==0
    assert runner.invoke(args=["init-db"]).exit_code!=0
    client=first.test_client();assert register(client,"asha").status_code==303;login(client,"asha")
    result=client.post("/posts/create",data={"title":"Survives restart","body":"Persistent SQLite",
        "csrf_token":token(client,"/posts/create")})
    assert result.status_code==303
    old_cookie=client.get_cookie("session").value
    key=(folder/"signing.key").read_bytes()
    assert len(key)==32
    with first.app_context():db.session.remove();db.engine.dispose()
    second=create_app(instance_path=temp)
    assert second.config["SECRET_KEY"]==key and (folder/"signing.key").read_bytes()==key
    reopened=second.test_client();reopened.set_cookie("session",old_cookie)
    assert reopened.get(result.headers["Location"]).status_code==200
    with second.app_context():
        assert db.session.scalar(db.select(Post.title))=="Survives restart"
        assert count(User)==1 and count(Tag)==3
        assert {"users","posts","tags","post_tags","login_sessions"}==set(inspect(db.engine).get_table_names())
        db.session.remove();db.engine.dispose()
    broken=folder/"invalid.key";broken.write_bytes(b"wrong owned test key")
    try:local_key(broken)
    except ValueError:pass
    else:raise AssertionError("Invalid key silently replaced")
    assert broken.read_bytes()==b"wrong owned test key"

print("PASS: Week38 real fictional registration/login/hash-only storage, unique rollback, private CRUD/owner isolation, CSRF/escaping/literal search/field and page limits, FK/tag cleanup, expiry/logout replay revocation, cookie isolation, non-destructive init and persistent database/key restart.")
