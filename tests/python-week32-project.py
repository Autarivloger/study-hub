"""Validate observed values, missingness, chart contents and publication."""
import importlib.util
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import pandas as pd
from PIL import Image

sys.dont_write_bytecode=True
os.environ["PYTHONDONTWRITEBYTECODE"]="1"
ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/"docs"/"python-week32"
spec=importlib.util.spec_from_file_location("eda_report",FOLDER/"exploration_report.py")
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
source=FOLDER/"practice_sessions.csv"; original=source.read_bytes()
df=module.load_sessions(source)
facts=module.evidence(df)
assert facts["sessions"]==24 and facts["learners"]==12
assert facts["known_scores"]==23 and facts["unknown_scores"]==1 and facts["complete_pairs"]==23
assert facts["track_sessions"]=={"Japanese":8,"Python":8,"Security":8}
assert facts["known_by_day"]=={"1":12,"2":11}
assert abs(facts["mean_score"]-1345/23)<1e-10
assert abs(facts["score_at_most65_share"]-18/23)<1e-10
assert facts["pair_counts"]["score"]["minutes"]==23
assert facts["pair_counts"]["tasks"]["minutes"]==24
fig=module.overview(df)
axes=fig.axes[:8]
assert [bar.get_height() for bar in axes[0].patches]==[0,8,14,2]
assert [bar.get_height() for bar in axes[3].patches]==[8,8,8]
assert axes[6].lines[0].get_ydata().tolist()==[57,661/11]
module.plt.close(fig)
plot=module.interactive(df)
assert sum(pd.notna(trace.y).sum() for trace in plot.data)==23

with tempfile.TemporaryDirectory(prefix="studyhub-w32-test-") as temp:
    folder=Path(temp); destination=folder/"run-01"
    command=[sys.executable,str(FOLDER/"exploration_report.py"),str(source),str(destination)]
    result=subprocess.run(command,capture_output=True,text=True,encoding="utf-8")
    assert result.returncode==0,result.stderr
    assert len(list(destination.iterdir()))==13
    for index in range(1,9):
        with Image.open(destination/f"chart-{index}.png") as picture: assert picture.size==(900,600)
    assert json.loads((destination/"summary.json").read_text(encoding="utf-8"))==json.loads(json.dumps(facts))
    prepared=pd.read_csv(destination/"prepared_sessions.csv")
    assert prepared["score"].isna().sum()==1 and len(prepared)==24
    notes=(destination/"interpretation.txt").read_text(encoding="utf-8")
    for index in range(1,9): assert f"{index}. " in notes
    assert "not a treatment effect" in notes and "unknown outcome" in notes
    html=(destination/"interactive.html").read_text(encoding="utf-8")
    class Scripts(HTMLParser):
        def __init__(self): super().__init__(); self.external=[]
        def handle_starttag(self,tag,attrs):
            if tag=="script" and dict(attrs).get("src"): self.external.append(dict(attrs)["src"])
    parser=Scripts();parser.feed(html)
    assert not parser.external and "plotly.js v" in html.lower()
    outputs={p.name:p.read_bytes() for p in destination.iterdir()}
    assert subprocess.run(command,capture_output=True).returncode!=0
    assert outputs=={p.name:p.read_bytes() for p in destination.iterdir()}
    assert source.read_bytes()==original
    # Concrete source boundaries, including a blank score accepted while
    # malformed, infinite and out-of-range values are refused.
    for field,value in [("score","NaN"),("score","101"),("minutes","inf"),("minutes","0"),
                        ("day","1.5"),("tasks","-1"),("track","Other"),("learner","")]:
        changed=pd.read_csv(source,keep_default_na=False,dtype=str); changed.loc[0,field]=value
        path=folder/"bad.csv";changed.to_csv(path,index=False)
        try: module.load_sessions(path)
        except ValueError: pass
        else: raise AssertionError(f"Accepted {field}={value}")
    changed=pd.read_csv(source,keep_default_na=False,dtype=str)
    changed.loc[1,"session_id"]=changed.loc[0,"session_id"]
    changed.to_csv(folder/"bad.csv",index=False)
    try: module.load_sessions(folder/"bad.csv")
    except ValueError: pass
    else: raise AssertionError("Duplicate ID accepted")
    changed=df.copy();changed.loc[0,"minutes"]=70
    try: module.publish(changed,folder/"clipped")
    except ValueError: pass
    else: raise AssertionError("Histogram would silently exclude a source value")
    assert not (folder/"clipped").exists()
    saved=module.matplotlib.figure.Figure.savefig
    def broken(*args,**kwargs): raise OSError("Simulated export failure")
    module.matplotlib.figure.Figure.savefig=broken
    try:
        try: module.publish(df,folder/"failed")
        except OSError: pass
        else: raise AssertionError("Export error swallowed")
    finally: module.matplotlib.figure.Figure.savefig=saved
    assert not (folder/"failed").exists() and not module.plt.get_fignums()
    assert sorted(p.name for p in folder.iterdir())==["bad.csv","run-01"]

print("PASS:24 sessions/12 repeated learners/23 scores, exact means/bins/pair counts,8 charts/13 artifacts, inline offline HTML, unknown retention, immutable sources, overwrite/invalid/clipping refusal and export failure cleanup.")
