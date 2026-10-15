"""Week37 local, single-user Flask dashboard. Fictional data; memory-only notes."""
from pathlib import Path
import secrets
import hmac
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for

LESSONS = [
    {"id":1,"title":"HTTP request cycle","topic":"Web foundations","minutes":20},
    {"id":2,"title":"SQL joins and counts","topic":"Data foundations","minutes":30},
    {"id":3,"title":"Flask routes and templates","topic":"Web foundations","minutes":25},
    {"id":4,"title":"Forms and validation","topic":"Web applications","minutes":30},
]


def bounded_text(value, minimum, maximum):
    value = value.strip()
    if not minimum <= len(value) <= maximum or any(not c.isprintable() for c in value):
        return None
    return value


def create_app(test_config=None):
    root = Path(__file__).resolve().parent
    app = Flask(__name__,template_folder=str(root/"templates"),static_folder=str(root/"static"))
    app.config.update(
        SECRET_KEY=secrets.token_hex(32),
        MAX_CONTENT_LENGTH=16*1024,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,  # Loopback HTTP only; HTTPS deployment needs True.
        DEMO_NOTES=[],
    )
    if test_config:
        app.config.update(test_config)

    def csrf_token():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_urlsafe(24)
        return session["csrf_token"]

    @app.context_processor
    def template_helpers():
        return {"csrf_token":csrf_token}

    @app.before_request
    def check_post_token():
        if request.method=="POST":
            expected=session.get("csrf_token")
            supplied=request.form.get("csrf_token","")
            if not isinstance(expected,str) or not supplied.isascii() or not hmac.compare_digest(expected,supplied):
                abort(400,description="The form token is missing or stale. Reload the form and try again.")

    def require_demo():
        return bool(session.get("demo_name"))

    @app.get("/")
    def home():
        # This is an incidental per-browser visit drill, not user analytics.
        visits=session.get("visits",0)
        session["visits"]=visits+1 if type(visits) is int and visits>=0 else 1
        return render_template("home.html",lessons=LESSONS,visits=session["visits"])

    @app.get("/lessons")
    def lessons():
        raw=request.args.get("q","")
        if len(raw)>80:
            return render_template("lessons.html",lessons=[],q=raw[:80],
                                   error="Search must be at most 80 characters."),400
        query=raw.strip()
        found=[row for row in LESSONS if query.casefold() in (row["title"]+" "+row["topic"]).casefold()]
        return render_template("lessons.html",lessons=found,q=query,error=None)

    @app.get("/lessons/<int:lesson_id>")
    def lesson_detail(lesson_id):
        row=next((row for row in LESSONS if row["id"]==lesson_id),None)
        if row is None:
            abort(404,description="That fictional lesson does not exist.")
        return render_template("detail.html",lesson=row)

    @app.get("/about")
    def about():
        return render_template("about.html")

    @app.route("/enter",methods=["GET","POST"])
    def enter():
        name=""
        error=None
        if request.method=="POST":
            name=request.form.get("display_name","")
            approved=bounded_text(name,2,40)
            if approved is None:
                error="Use 2–40 visible characters for a fictional display name."
            else:
                # This flag is a demo gate, not verified identity or account login.
                session.clear()
                session["demo_name"]=approved
                flash("Demo space opened. This is not a real account.","success")
                return redirect(url_for("planner"),code=303)
        return render_template("enter.html",name=name[:40],error=error),400 if error else 200

    @app.get("/planner")
    def planner():
        if not require_demo():
            return redirect(url_for("enter"),code=303)
        return render_template("planner.html",lessons=LESSONS,
                               notes=app.config["DEMO_NOTES"],error=None,draft="")

    @app.post("/notes")
    def add_note():
        if not require_demo():
            return redirect(url_for("enter"),code=303)
        draft=request.form.get("body","")
        approved=bounded_text(draft,1,200)
        error=None
        if approved is None:
            error="Write 1–200 visible characters."
        elif len(app.config["DEMO_NOTES"])>=20:
            error="This memory-only practice list is full (20 notes). Clear it to continue."
        if error:
            return render_template("planner.html",lessons=LESSONS,notes=app.config["DEMO_NOTES"],
                                   error=error,draft=draft[:200]),400
        app.config["DEMO_NOTES"].append({"author":session["demo_name"],"body":approved})
        flash("Practice note added in this running process.","success")
        return redirect(url_for("planner"),code=303)

    @app.post("/notes/clear")
    def clear_notes():
        if not require_demo():
            return redirect(url_for("enter"),code=303)
        app.config["DEMO_NOTES"].clear()
        flash("Temporary practice notes cleared.","info")
        return redirect(url_for("planner"),code=303)

    @app.route("/settings",methods=["GET","POST"])
    def settings():
        if not require_demo():
            return redirect(url_for("enter"),code=303)
        error=None
        if request.method=="POST":
            mode=request.form.get("theme","")
            if mode not in {"light","dark"}:
                error="Choose light or dark."
            else:
                session["theme"]=mode
                flash("This browser's demo theme was updated.","success")
                return redirect(url_for("settings"),code=303)
        return render_template("settings.html",error=error),400 if error else 200

    @app.post("/leave")
    def leave():
        session.clear()
        flash("You left the demo space.","info")
        return redirect(url_for("home"),code=303)

    @app.errorhandler(400)
    @app.errorhandler(404)
    @app.errorhandler(405)
    @app.errorhandler(413)
    def request_error(error):
        response=app.make_response((render_template("error.html",code=error.code,message=error.description),error.code))
        if error.code==405 and error.valid_methods:
            response.headers["Allow"]=", ".join(error.valid_methods)
        return response

    @app.after_request
    def response_headers(response):
        response.headers["X-Content-Type-Options"]="nosniff"
        response.headers["Cache-Control"]="no-store"
        return response

    return app


if __name__=="__main__":
    # Local teaching server. Never an internet production deployment command.
    create_app().run(host="127.0.0.1",port=5000,debug=False)
