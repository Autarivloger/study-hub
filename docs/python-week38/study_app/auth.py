from functools import wraps
import secrets
import time
from flask import Blueprint,abort,current_app,flash,g,redirect,render_template,request,session,url_for
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash,generate_password_hash
from .extensions import db
from .models import LoginSession,User
from .security import username_value

bp=Blueprint("auth",__name__,url_prefix="/auth")


@bp.before_app_request
def load_user():
    g.user=None
    identifier=session.get("login_id")
    if not isinstance(identifier,str) or len(identifier)!=64:
        return
    login=db.session.get(LoginSession,identifier)
    if login is None or login.expires_at<=int(time.time()):
        session.clear()
        return
    g.user=db.session.get(User,login.user_id)
    if g.user is None:
        session.clear()


def login_required(view):
    @wraps(view)
    def wrapped(*args,**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"),code=303)
        return view(*args,**kwargs)
    return wrapped


@bp.route("/register",methods=["GET","POST"])
def register():
    error=None
    username=""
    if request.method=="POST":
        username=request.form.get("username","")
        name=username_value(username)
        password=request.form.get("password","") # Deliberately never strip a password.
        if name is None or not 12<=len(password)<=128:
            error="Use a 3–32 character ASCII username and a 12–128 character practice password."
        else:
            db.session.add(User(username=name,password_hash=generate_password_hash(password)))
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                error="That username is unavailable."
            else:
                flash("Practice account created. Sign in.","success")
                return redirect(url_for("auth.login"),code=303)
    return render_template("auth.html",mode="register",username=username[:32],error=error),400 if error else 200


@bp.route("/login",methods=["GET","POST"])
def login():
    error=None
    username=""
    if request.method=="POST":
        username=request.form.get("username","")
        name=username_value(username)
        password=request.form.get("password","")
        user=None if name is None else db.session.scalar(db.select(User).where(User.username==name))
        stored=user.password_hash if user else current_app.config["DUMMY_PASSWORD_HASH"]
        checked=check_password_hash(stored,password) if len(password)<=128 else False
        if user is None or not checked:
            error="Invalid username or password."
        else:
            old=session.get("login_id")
            if isinstance(old,str):
                previous=db.session.get(LoginSession,old)
                if previous is not None:db.session.delete(previous)
            identifier=secrets.token_hex(32)
            db.session.add(LoginSession(id=identifier,user_id=user.id,expires_at=int(time.time())+3600))
            db.session.commit()
            session.clear()
            session["login_id"]=identifier
            flash("Signed in to the local practice journal.","success")
            return redirect(url_for("posts.index"),code=303)
    return render_template("auth.html",mode="login",username=username[:32],error=error),400 if error else 200


@bp.post("/logout")
@login_required
def logout():
    record=db.session.get(LoginSession,session.get("login_id"))
    if record is not None:
        db.session.delete(record)
        db.session.commit()
    session.clear()
    flash("This login session was revoked.","info")
    return redirect(url_for("home"),code=303)
