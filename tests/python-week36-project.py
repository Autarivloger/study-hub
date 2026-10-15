"""Week36 acceptance: loopback HTTP + controlled failure/provider fixtures only."""
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch
import requests

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/"docs"/"python-week36"
sys.path.insert(0,str(FOLDER))
from mock_api import DemoAPI,PRACTICE_TOKEN,ITEMS
from api_client import APIClient,APIError,retry_delay,validate_item
import collector


def fails(kind, operation):
    try:operation()
    except kind as error:return error
    raise AssertionError("Expected failure: "+repr(operation))


def response(status=200,payload=None,headers=None,raw=None):
    result=requests.Response()
    result.status_code=status
    result.headers.update({"Content-Type":"application/json",**(headers or {})})
    result._content=raw if raw is not None else json.dumps(payload).encode()
    result._content_consumed=True
    return result


class Scripted:
    """No network; preserve calls for exact retry/pagination assertions."""
    def __init__(self, events):
        self.events=list(events);self.calls=[]
    def get(self,url,**kwargs):
        self.calls.append((url,kwargs))
        event=self.events.pop(0)
        if isinstance(event,Exception):raise event
        return event
    def close(self):pass


def fake_client(events,**kwargs):
    client=APIClient("https://api.github.com",PRACTICE_TOKEN,**kwargs)
    client.session.close()
    client.session=Scripted(events)
    return client


# Actual local HTTP: methods/encoding/auth/timeout/body/status contracts.
with DemoAPI() as base,requests.Session() as session:
    session.trust_env=False
    with session.get(base+"/echo",params={"q":"日本語 & Python","tag":["a","b"]},timeout=(1,1)) as r:
        assert r.json()["query"]=={"q":["日本語 & Python"],"tag":["a","b"]}
    with session.post(base+"/tasks",json={"title":"A Reader's Guide"},timeout=(1,1)) as r:
        assert r.status_code==201 and r.json()=={"id":1,"title":"A Reader's Guide"}
    with session.put(base+"/tasks/1",json={"title":"Revised"},timeout=(1,1)) as r:
        assert r.status_code==200 and r.json()["title"]=="Revised"
    with session.delete(base+"/tasks/1",timeout=(1,1)) as r:
        assert r.status_code==204 and r.content==b""
    with session.delete(base+"/tasks/1",timeout=(1,1)) as r:assert r.status_code==404
    with session.post(base+"/tasks",data={"title":"wrong representation"},timeout=(1,1)) as r:assert r.status_code==400
    fails(requests.Timeout,lambda:session.get(base+"/slow",timeout=(1,0.01)))
    with APIClient(base,PRACTICE_TOKEN) as api:
        rows=api.collect_mock()
        assert rows==ITEMS
        assert api.get_json("/flaky")[0]=={"ok":True}
        for path in ["/bad-json","/redirect","/empty","/missing"]:
            err=fails(APIError,lambda path=path:api.get_json(path))
            assert PRACTICE_TOKEN not in str(err)
        fails(APIError,lambda:api.collect_mock(max_pages=2))
        fails(APIError,lambda:api.collect_mock(max_items=5))
        fails(ValueError,lambda:api.collect_mock(max_pages=True))
    with APIClient(base,"wrong-practice-token") as api:
        assert "401" in str(fails(APIError,lambda:api.collect_mock()))

# Strict fields and scope, no secret/env reads.
for changes in [{"id":True},{"id":0},{"id":2**63},{"comments":True},{"comments":-1},
                {"state":"pending"},{"title":""},{"title":"x"*1001},{"kind":"other"}]:
    fails(APIError,lambda changes=changes:validate_item({**ITEMS[0],**changes}))
source={**ITEMS[0],"ignored":"not stored"}
assert validate_item(source)==ITEMS[0] and source["ignored"]=="not stored"
for base in ["http://example.org","https://example.org","https://api.github.com/evil",
             "https://api.github.com?token=x","http://localhost:1234","http://127.0.0.1:1234/path"]:
    fails(ValueError,lambda base=base:APIClient(base,PRACTICE_TOKEN))
fails(ValueError,lambda:APIClient("https://api.github.com","bad\nheader"))
now=datetime(2026,1,1,tzinfo=timezone.utc)
assert retry_delay("3",now=now)==3
assert retry_delay("Thu, 01 Jan 2026 00:00:05 GMT",now=now)==5
assert retry_delay("Wed, 31 Dec 2025 23:59:59 GMT",now=now)==0
fails(APIError,lambda:retry_delay("soon"))

# Retry waits and stopping, using synthetic responses and recorded sleeps.
waits=[]
with fake_client([response(503,{},{"Retry-After":"2"}),response(200,{"ok":True})],sleep=waits.append) as api:
    assert api.get_json("/health")[0]["ok"] and waits==[2.0] and len(api.session.calls)==2
    assert api.session.calls[0][1]["allow_redirects"] is False
    assert api.session.calls[0][1]["timeout"]==(3.05,10)
waits=[]
with fake_client([requests.Timeout(),requests.ConnectionError(),response(200,{"ok":True})],
                 sleep=waits.append,jitter=lambda:0.25) as api:
    assert api.get_json("/health")[0]["ok"] and waits==[0.75,1.25]
waits=[]
with fake_client([response(429,{},{"Retry-After":"120"})],sleep=waits.append,max_wait=10) as api:
    assert "budget" in str(fails(APIError,lambda:api.get_json("/health")))
    assert waits==[] and len(api.session.calls)==1
waits=[]
with fake_client([response(503,{},{"Retry-After":"0"})]*3,sleep=waits.append) as api:
    fails(APIError,lambda:api.get_json("/health"))
    assert len(api.session.calls)==3 and waits==[0,0]  # no final sleep
for event in [response(401,{}),response(403,{}),response(404,{}),response(302,{},{"Location":"https://example.org"}),
              requests.exceptions.SSLError("fictional TLS failure")]:
    with fake_client([event],sleep=lambda _:(_ for _ in ()).throw(AssertionError("Unexpected retry"))) as api:
        fails(APIError,lambda:api.get_json("/health"))
        assert len(api.session.calls)==1
with patch("api_client.time.time",return_value=1000):
    waits=[]
    with fake_client([response(403,{},{"X-RateLimit-Remaining":"0","X-RateLimit-Reset":"1002"}),
                      response(200,{"ok":True})],sleep=waits.append) as api:
        assert api.get_json("/health")[0]["ok"] and waits==[2]
    with fake_client([response(403,{},{"X-RateLimit-Remaining":"0","X-RateLimit-Reset":"nan"})]) as api:
        fails(APIError,lambda:api.get_json("/health"))

# Page-envelope, repeat, duplicate and exact trusted GitHub Link contracts.
envelope=lambda items,nxt:response(200,{"items":items,"next_cursor":nxt})
cases=[
    [response(200,{"items":[]})],
    [envelope([ITEMS[0]],"c2"),envelope([ITEMS[1]],"c2")],
    [envelope([ITEMS[0]],"c2"),envelope([ITEMS[0]],None)],
    [response(200,[])],
]
for events in cases:
    with fake_client(events) as api:fails(APIError,lambda:api.collect_mock())
path="/repos/example/demo/issues"
query="?state=all&per_page=100&sort=created&direction=asc&page=2"
next_url="https://api.github.com"+path+query
github_rows=[{"id":101,"title":"Issue","state":"open","comments":2},
             {"id":102,"title":"PR","state":"closed","comments":3,"pull_request":{}}]
with fake_client([response(200,github_rows[:1],{"Link":"<"+next_url+">; rel=\"next\""}),
                  response(200,github_rows[1:])]) as api:
    rows=api.collect_github("example/demo")
    assert [r["kind"] for r in rows]==["issue","pull_request"]
    assert api.session.calls[1][0]=="https://api.github.com"+path
    assert api.session.calls[1][1]["params"]["page"]==2
for bad in [next_url.replace("api.github.com","example.org"),
            next_url.replace("/example/demo/","/another/demo/"),
            next_url.replace("page=2","page=1"),
            next_url.replace("state=all","state=open"),
            next_url+"#fragment"]:
    with fake_client([response(200,github_rows[:1],{"Link":"<"+bad+">; rel=\"next\""})]) as api:
        fails(APIError,lambda:api.collect_github("example/demo"))
        assert len(api.session.calls)==1
with fake_client([response(200,github_rows[:1],{"Link":"<"+next_url+">; rel=\"next\""}),
                  response(200,github_rows[:1])]) as api:
    fails(APIError,lambda:api.collect_github("example/demo"))

# Publish evidence, verify actual SQL counts/hash and preserve old/failed runs.
with TemporaryDirectory(prefix="studyhub-w36-project-") as folder:
    folder=Path(folder);target=folder/"run-01"
    facts=collector.publish(ITEMS,target,provider="mock")
    assert facts["items"]==6 and facts["comments"]==18
    assert facts["groups"]==[
        {"kind":"issue","state":"closed","items":2,"comments":8},
        {"kind":"issue","state":"open","items":3,"comments":9},
        {"kind":"pull_request","state":"open","items":1,"comments":1}]
    assert sorted(p.name for p in target.iterdir())==["collection.sqlite","items.csv","items.json","manifest.json","report.md","summary.json"]
    manifest=json.loads((target/"manifest.json").read_text())
    assert hashlib.sha256((target/"items.json").read_bytes()).hexdigest()==manifest["sha256_items_json"]
    with closing(sqlite3.connect(target/"collection.sqlite")) as con:
        assert con.execute("SELECT COUNT(*),SUM(comments) FROM items").fetchone()==(6,18)
        assert con.execute("SELECT COUNT(*) FROM items WHERE kind='issue'").fetchone()[0]==5
    report=(target/"report.md").read_text()
    for marker in ["not a frozen historical census","Issue and pull-request","recorded comments","SHA-256"]:assert marker in report
    for file in target.iterdir():assert PRACTICE_TOKEN.encode() not in file.read_bytes()
    original={p.name:p.read_bytes() for p in target.iterdir()}
    fails(ValueError,lambda:collector.publish(ITEMS,target,provider="mock"))
    assert original=={p.name:p.read_bytes() for p in target.iterdir()}
    bad=folder/"invalid"
    fails(APIError,lambda:collector.publish(ITEMS+[ITEMS[0]],bad,provider="mock"))
    assert not bad.exists()
    # Simulate an export failure after the operation owns its staging folder.
    real_write=Path.write_text
    def broken_write(self,*args,**kwargs):
        if self.name=="summary.json":raise OSError("Simulated export failure")
        return real_write(self,*args,**kwargs)
    before=set(folder.iterdir())
    with patch.object(Path,"write_text",broken_write):
        fails(OSError,lambda:collector.publish(ITEMS,folder/"failed-export",provider="mock"))
    assert set(folder.iterdir())==before
    empty=collector.publish([],folder/"empty",provider="mock")
    assert empty=={"items":0,"comments":0,"groups":[]}

    # Copy only public support files into a temporary CLI folder. No real .env.
    cli_folder=folder/"cli";cli_folder.mkdir()
    for name in ["mock_api.py","api_client.py","collector.py"]:
        shutil.copyfile(FOLDER/name,cli_folder/name)
    environment={"SystemRoot":os.environ.get("SystemRoot",r"C:\Windows"),
                 "TEMP":str(folder),"TMP":str(folder),"PYTHONDONTWRITEBYTECODE":"1"}
    def cli(destination,*args,good=True):
        result=subprocess.run([sys.executable,str(cli_folder/"collector.py"),str(destination),*map(str,args)],
            capture_output=True,text=True,encoding="utf-8",env=environment,cwd=cli_folder)
        assert (result.returncode==0) is good,result.stderr
        assert PRACTICE_TOKEN not in result.stdout+result.stderr
        return result
    cli(folder/"cli-run")
    assert json.loads((folder/"cli-run"/"summary.json").read_text())["items"]==6
    cli(folder/"cli-run",good=False)
    cli(folder/"too-short","--max-pages",2,good=False)
    assert not (folder/"too-short").exists()
    cli(folder/"live-missing","--github","example/demo",good=False)
    assert not (folder/"live-missing").exists()

print("PASS: Week36 actual loopback methods/encoding/auth/timeouts, 3-page complete collection, malformed/redirect/schema failures, bounded retry/wait/rate policies, cursor/id/link validation with no external requests, 6 artifacts/6 items/18 comments, exact JSON hash, atomic failure cleanup, non-overwrite and credential-free CLI tests.")
