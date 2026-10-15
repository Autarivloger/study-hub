"""Acceptance tests for the independent, fictional Week37 Flask dashboard."""
from pathlib import Path
import re
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"docs"/"python-week37"))
from app import create_app,bounded_text


def token(client,path="/enter"):
    response=client.get(path)
    assert response.status_code==200
    match=re.search(r'name="csrf_token" value="([^"]+)"',response.get_data(as_text=True))
    assert match,"Expected the actual rendered form token"
    return match.group(1)


def enter(client,name="Asha"):
    r=client.post("/enter",data={"display_name":name,"csrf_token":token(client)})
    assert r.status_code==303 and r.headers["Location"]=="/planner"
    return r


app=create_app({"TESTING":True})
client=app.test_client()
for path in ["/","/lessons","/lessons/1","/about","/enter"]:
    response=client.get(path)
    assert response.status_code==200
    html=response.get_data(as_text=True)
    assert '<meta name="viewport"' in html and 'id="main"' in html and 'class="site-header"' in html
    assert "<script" not in html.lower()
css=client.get("/static/style.css")
assert css.status_code==200 and css.mimetype=="text/css"
assert "@media(max-width:700px)" in css.get_data(as_text=True)
css.close()
assert client.get("/static/missing.css").status_code==404
assert client.get("/lessons/999").status_code==404
assert client.get("/lessons/nope").status_code==404
assert client.get("/unknown").status_code==404
assert client.get("/notes").status_code==405
assert "POST" in client.get("/notes").headers["Allow"]
assert client.get("/leave").status_code==405
assert client.get("/planner").status_code==303
assert client.get("/settings").status_code==303

# Read-only query boundaries and escaping, without mutations.
html=client.get("/lessons?q=HTTP").get_data(as_text=True)
assert "HTTP request cycle" in html and "SQL joins and counts" not in html
assert "No matching lessons" in client.get("/lessons?q=unfindable").get_data(as_text=True)
assert client.get("/lessons",query_string={"q":"x"*81}).status_code==400
html=client.get("/lessons",query_string={"q":'<script>alert("x")</script>'}).get_data(as_text=True)
assert "<script>" not in html and "&lt;script&gt;" in html
assert app.config["DEMO_NOTES"]==[]
assert bounded_text("  Good note  ",1,200)=="Good note"
assert bounded_text("Bad\nline",1,200) is None
assert bounded_text("Bad\x7ftext",1,200) is None
assert bounded_text("   ",1,200) is None

# Validate the full real entry form contract, not a disabled security fixture.
first=token(client)
before=len(app.config["DEMO_NOTES"])
for payload in [
    {"display_name":"Asha"},
    {"display_name":"Asha","csrf_token":"wrong"},
    {"display_name":"Asha","csrf_token":"日本語"},
    {"display_name":"A","csrf_token":first},
    {"display_name":"x"*41,"csrf_token":first},
    {"display_name":"New\nline","csrf_token":first},
]:
    assert client.post("/enter",data=payload).status_code==400
    with client.session_transaction() as values:assert "demo_name" not in values
assert len(app.config["DEMO_NOTES"])==before
name='<b>Asha</b>'
enter(client,name)
planner=client.get("/planner").get_data(as_text=True)
assert "&lt;b&gt;Asha&lt;/b&gt;" in planner and "<b>Asha</b>" not in planner
with client.session_transaction() as values:assert values["demo_name"]==name
# A token from before successful entry was cleared and is now stale.
assert client.post("/notes",data={"body":"No stale write","csrf_token":first}).status_code==400

# Invalid fields and missing/cross-session tokens do not change server notes.
for body in [""," ","x"*201,"New\nline","\x00"]:
    r=client.post("/notes",data={"body":body,"csrf_token":token(client,"/planner")})
    assert r.status_code==400 and len(app.config["DEMO_NOTES"])==0
assert client.post("/notes",data={"body":"Missing token"}).status_code==400
other=app.test_client()
other_token=token(other)
assert client.post("/notes",data={"body":"Wrong session","csrf_token":other_token}).status_code==400
assert app.config["DEMO_NOTES"]==[]

body='<script>window.demoXSS=true</script>'
r=client.post("/notes",data={"body":body,"csrf_token":token(client,"/planner")})
assert r.status_code==303 and r.headers["Location"]=="/planner"
first_page=client.get("/planner").get_data(as_text=True)
assert "Practice note added in this running process." in first_page
assert "&lt;script&gt;" in first_page and "<script>" not in first_page
assert app.config["DEMO_NOTES"]==[{"author":name,"body":body}]
assert "Practice note added in this running process." not in client.get("/planner").get_data(as_text=True)
assert len(app.config["DEMO_NOTES"])==1 # GET refresh does not add

# Allowlisted per-browser theme and cookie properties.
assert client.post("/settings",data={"theme":"dark","csrf_token":token(client,"/settings")}).status_code==303
assert 'data-theme="dark"' in client.get("/settings").get_data(as_text=True)
assert client.post("/settings",data={"theme":"evil","csrf_token":token(client,"/settings")}).status_code==400
assert 'data-theme="dark"' in client.get("/settings").get_data(as_text=True)
assert 'data-theme="light"' in other.get("/").get_data(as_text=True)
cookie=client.get_cookie("session")
assert cookie.http_only and cookie.same_site=="Lax"
assert not cookie.secure # Explicit local HTTP demonstration

# Request budget and list capacity leave approved state unchanged.
count=len(app.config["DEMO_NOTES"])
r=client.post("/notes",data={"body":"x"*20000,"csrf_token":token(client,"/planner")})
assert r.status_code==413 and len(app.config["DEMO_NOTES"])==count
while len(app.config["DEMO_NOTES"])<20:
    r=client.post("/notes",data={"body":"Fictional short practice","csrf_token":token(client,"/planner")})
    assert r.status_code==303
assert client.post("/notes",data={"body":"One too many","csrf_token":token(client,"/planner")}).status_code==400
assert len(app.config["DEMO_NOTES"])==20
# A separate entered demo sees the deliberately shared, labelled process list.
enter(other,"Ben")
assert "Temporary notes (20/20)" in other.get("/planner").get_data(as_text=True)
assert "shared by demo visitors" in other.get("/planner").get_data(as_text=True)
assert other.post("/notes/clear",data={"csrf_token":token(other,"/planner")}).status_code==303
assert app.config["DEMO_NOTES"]==[]

# Leave affects one current session, not another.
stale=token(client,"/planner")
assert client.post("/leave",data={"csrf_token":stale}).status_code==303
assert client.get("/planner").status_code==303
assert other.get("/planner").status_code==200
with client.session_transaction() as values:
    assert "demo_name" not in values and "theme" not in values
assert client.post("/notes",data={"body":"After leave","csrf_token":stale}).status_code==400

# Signed-cookie tampering cannot set a gate or retain a trusted theme.
cookie=other.get_cookie("session").value
other.set_cookie("session",cookie+"tampered")
assert other.get("/planner").status_code==303
with other.session_transaction() as values:assert "demo_name" not in values

# Fresh factory instances reset the deliberately temporary state/key.
new=create_app({"TESTING":True})
assert new.config["DEMO_NOTES"]==[]
assert new.config["SECRET_KEY"]!=app.config["SECRET_KEY"]
assert new.config["MAX_CONTENT_LENGTH"]==16*1024
assert not new.debug
expected={"home","lessons","lesson_detail","about","enter","planner","add_note","clear_notes","settings","leave","static"}
assert expected <= {r.endpoint for r in new.url_map.iter_rules()}
for path in ["/","/about","/enter"]:
    r=new.test_client().get(path)
    assert r.headers["X-Content-Type-Options"]=="nosniff" and r.headers["Cache-Control"]=="no-store"
print("PASS: Week37 public/gated routes, real CSRF entry/note/settings/leave flow, escaped data, invalid drafts/no mutation, PRG/flash, signed-cookie isolation/tampering, process-only reset/shared-note scope, 20-note/body limits and local templates/static assets.")
