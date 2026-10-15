"""Week36: API -> validated complete collection -> SQLite and a new report bundle."""
import argparse
from contextlib import closing
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import sqlite3
from tempfile import TemporaryDirectory
from api_client import APIClient, APIError, validate_item
from mock_api import DemoAPI, PRACTICE_TOKEN


def publish(rows, destination, *, provider, repository=None):
    destination = Path(destination)
    if destination.exists() or not destination.parent.is_dir():
        raise ValueError("Choose a NEW output folder in an existing parent")
    validated = [validate_item(row) for row in rows]
    if len(validated)>10000 or len({r["id"] for r in validated})!=len(validated):
        raise APIError("Require at most10000unique validated items")
    if provider not in {"mock","github"}:
        raise ValueError("Unknown provider")
    payload = json.dumps(validated,indent=2,ensure_ascii=False,allow_nan=False)+"\n"
    manifest = {"provider":provider,"repository":repository,
                "collected_at_utc":datetime.now(timezone.utc).isoformat(),
                "items":len(validated),"sha256_items_json":hashlib.sha256(payload.encode()).hexdigest(),
                "scope":"Completed requested pagination; not a transactionally frozen remote snapshot"}
    with TemporaryDirectory(prefix="studyhub-api-report-",dir=destination.parent) as temp:
        folder = Path(temp)
        (folder/"items.json").write_text(payload,encoding="utf-8",newline="\n")
        with (folder/"items.csv").open("w",encoding="utf-8",newline="") as handle:
            writer=csv.DictWriter(handle,fieldnames=["id","title","state","comments","kind"])
            writer.writeheader();writer.writerows(validated)
        with closing(sqlite3.connect(folder/"collection.sqlite",isolation_level=None)) as con:
            con.execute("""CREATE TABLE items(
                id INTEGER PRIMARY KEY,title TEXT NOT NULL,
                state TEXT NOT NULL CHECK(state IN ('open','closed')),
                comments INTEGER NOT NULL CHECK(typeof(comments)='integer' AND comments>=0),
                kind TEXT NOT NULL CHECK(kind IN ('issue','pull_request')))""")
            con.execute("BEGIN IMMEDIATE")
            try:
                con.executemany("INSERT INTO items VALUES(?,?,?,?,?)",
                    [(r["id"],r["title"],r["state"],r["comments"],r["kind"]) for r in validated])
                con.execute("COMMIT")
            except BaseException:
                if con.in_transaction:con.execute("ROLLBACK")
                raise
            groups=[dict(zip(["kind","state","items","comments"],row)) for row in con.execute(
                "SELECT kind,state,COUNT(*),SUM(comments) FROM items GROUP BY kind,state ORDER BY kind,state")]
            count,comments=con.execute("SELECT COUNT(*),COALESCE(SUM(comments),0) FROM items").fetchone()
        facts={"items":count,"comments":comments,"groups":groups}
        (folder/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
        (folder/"summary.json").write_text(json.dumps(facts,indent=2),encoding="utf-8")
        lines=["# API collection report",f"Provider: {provider}",
               f"Validated returned items: {count}; recorded comments across those items: {comments}.",
               "","## Grouped evidence"]
        lines += [f"- {g['kind']} / {g['state']}: {g['items']} items, {g['comments']} recorded comments." for g in groups]
        lines += ["","## Scope and limitations",
                  "Issue and pull-request records are identified separately; do not call their mixed total an issue-only count.",
                  "This is the completed bounded request sequence at the recorded time, not a frozen historical census.",
                  "Remote pages can change between calls; duplicate IDs stop collection rather than silently discarding evidence.",
                  "Comments are the endpoint's recorded count, not every form of discussion or review activity.",
                  "No author identities, tokens, request headers or raw error bodies are stored.",
                  "items.csv is a data interchange file, not spreadsheet-sanitised text; import title as text in spreadsheet tools.",
                  "The mock dataset is fictional. GitHub mode uses live public repository records and needs network access.",
                  "","## Reproduction",
                  "Keep the source files and requirements.txt. Use a new destination for each run.",
                  "manifest.json records provider, retrieval time, scope and the SHA-256 of items.json.",
                  "SQLite and JSON outputs are local artifacts, unrelated to Study Hub browser storage.",""]
        (folder/"report.md").write_text("\n".join(lines),encoding="utf-8")
        os.rename(folder,destination)
    return facts


def main(argv=None):
    parser=argparse.ArgumentParser(description="Week36 offline API drill; GitHub collection is explicit opt-in")
    parser.add_argument("destination",type=Path)
    parser.add_argument("--github",metavar="OWNER/REPO")
    parser.add_argument("--max-pages",type=int,default=10)
    args=parser.parse_args(argv)
    if args.destination.exists() or not args.destination.parent.is_dir():
        parser.exit(1,"Collection stopped: choose a new destination\n")
    try:
        if args.github:
            # Only explicit live mode loads a local .env. Values are never printed.
            from dotenv import load_dotenv
            load_dotenv(Path(__file__).with_name(".env"),override=False)
            token=os.environ.get("STUDYHUB_API_TOKEN","")
            if not token:
                raise ValueError("Set STUDYHUB_API_TOKEN locally for optional authenticated GitHub mode")
            with APIClient("https://api.github.com",token,jitter=random.random) as api:
                rows=api.collect_github(args.github,max_pages=args.max_pages)
            facts=publish(rows,args.destination,provider="github",repository=args.github)
        else:
            with DemoAPI() as base, APIClient(base,PRACTICE_TOKEN,jitter=random.random) as api:
                rows=api.collect_mock(max_pages=args.max_pages)
            facts=publish(rows,args.destination,provider="mock")
    except (APIError,ValueError,OSError,sqlite3.Error) as error:
        parser.exit(1,"Collection stopped: "+str(error)+"\n")
    print(f"Published6 files; items={facts['items']}; recorded comments={facts['comments']}")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
