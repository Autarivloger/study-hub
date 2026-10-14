"""Week32 original fictional EDA; local validated CSV to an offline report."""
import argparse
import csv
import io
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import plotly.express as px

def load_sessions(path):
    raw=Path(path).read_bytes()
    if len(raw)>1024*1024: raise ValueError("Learning CSV exceeds1MiB")
    text=raw.decode("utf-8-sig")
    rows=list(csv.reader(io.StringIO(text),strict=True))
    columns=["session_id","learner","track","mode","day","minutes","score","tasks"]
    if not rows or rows[0]!=columns or len(rows)<2 or len(rows)>10001:
        raise ValueError("Expected the documented exact header and1–10000 records")
    if any(len(row)!=len(columns) for row in rows[1:]): raise ValueError("Ragged CSV")
    df=pd.read_csv(io.StringIO(text),dtype="string",keep_default_na=False)
    for col in ["session_id","learner","track","mode"]:
        if df[col].str.strip().eq("").any(): raise ValueError("Blank identity/category")
    if df["session_id"].duplicated().any(): raise ValueError("Duplicate session IDs")
    if not df["track"].isin(["Python","Japanese","Security"]).all(): raise ValueError("Unknown track")
    if not df["mode"].isin(["Solo","Guided"]).all(): raise ValueError("Unknown mode")
    for col,low,high in [("day",1,31),("minutes",1,240),("tasks",0,100),("score",0,100)]:
        token=df[col]
        missing=token.eq("") if col=="score" else pd.Series(False,index=df.index)
        if not (missing|token.str.fullmatch(r"[0-9]+(?:\.[0-9]+)?")).all():
            raise ValueError("Invalid numeric token: "+col)
        values=pd.to_numeric(token.mask(missing),errors="raise").astype("float64")
        if not values.dropna().between(low,high).all(): raise ValueError("Out of bounds: "+col)
        if col in ["day","tasks"] and not values.mod(1).eq(0).all(): raise ValueError("Integer required: "+col)
        df[col]=values
    if df.duplicated(["learner","day"]).any(): raise ValueError("Ambiguous learner/day pair")
    if df["score"].notna().sum()<3: raise ValueError("Need at least3 known scores")
    return df
ORDER=["Python","Japanese","Security"]
NUMERIC=["minutes","score","tasks"]
def draw_panel(index,df,ax):
    if index==0:
        sns.histplot(data=df,x="minutes",bins=[0,15,30,45,60],ax=ax)
        ax.set(title="1. Session duration",xlabel="Minutes",ylabel="Session rows")
    elif index==1:
        sns.ecdfplot(data=df,x="score",ax=ax)
        ax.set(title="2. Observed score thresholds",xlabel="Score",ylabel="Known-score proportion")
    elif index==2:
        sns.boxplot(data=df,x="track",y="score",order=ORDER,color="#a8cfe5",ax=ax)
        ax.set(title="3. Score distribution by track",ylabel="Score")
    elif index==3:
        sns.countplot(data=df,x="track",order=ORDER,color="#0072B2",ax=ax)
        ax.set(title="4. Session counts",ylabel="Session rows")
    elif index==4:
        sns.barplot(data=df,x="mode",y="score",order=["Solo","Guided"],estimator="mean",errorbar=None,color="#0072B2",ax=ax)
        ax.set(title="5. Mode means, not a treatment effect",ylabel="Mean known score",ylim=(0,100))
    elif index==5:
        sns.scatterplot(data=df,x="minutes",y="score",hue="track",style="track",hue_order=ORDER,ax=ax)
        ax.set(title="6. Paired complete observations",xlabel="Minutes",ylabel="Score")
    elif index==6:
        sns.lineplot(data=df,x="day",y="score",estimator="mean",errorbar=None,marker="o",ax=ax)
        ax.set(title="7. Descriptive day means",xticks=[1,2],ylabel="Mean known score")
    else:
        sns.heatmap(df[NUMERIC].corr(min_periods=3),annot=True,fmt=".2f",vmin=-1,vmax=1,center=0,cmap="vlag",ax=ax)
        ax.set_title("8. Pearson association, not cause")
    if index in [2,3]: ax.tick_params(axis="x",labelrotation=15)

def overview(df):
    fig,axs=plt.subplots(4,2,figsize=(11,14),layout="constrained")
    for index,ax in enumerate(axs.flat): draw_panel(index,df,ax)
    fig.suptitle(f"Fictional sessions:{len(df)} rows, {df['learner'].nunique()} learners, {df['score'].isna().sum()} unknown scores")
    return fig

def interactive(df):
    return px.scatter(df,x="minutes",y="score",color="track",symbol="track",
        hover_data=["session_id","mode","day","tasks"],
        labels={"minutes":"Minutes per session","score":"Score (out of100)"},
        title="Fictional complete pairs; hover and legend controls")

def evidence(df):
    known=df[NUMERIC].notna().astype(int)
    return {"sessions":len(df),"learners":int(df["learner"].nunique()),
        "known_scores":int(df["score"].notna().sum()),"unknown_scores":int(df["score"].isna().sum()),
        "complete_pairs":int(df[["minutes","score"]].notna().all(axis=1).sum()),
        "track_sessions":{str(k):int(v) for k,v in df.groupby("track").size().items()},
        "known_by_day":{str(int(k)):int(v) for k,v in df.groupby("day")["score"].count().items()},
        "mean_score":float(df["score"].mean()),
        "pair_counts":known.T.dot(known).to_dict(),
        "score_at_most65_share":float(df["score"].dropna().le(65).mean())}

def publish(df,destination):
    destination=Path(destination)
    if destination.exists() or not destination.parent.is_dir(): raise ValueError("Choose a new bundle in an existing parent")
    facts=evidence(df)
    notes=[
        "FICTIONAL EXPLORATION — no real learners or causal study",
        f"Source:{facts['sessions']} session rows, {facts['learners']} distinct learner IDs, {facts['known_scores']} known scores, {facts['unknown_scores']} unknown scores.",
        "1. Duration histogram: session minutes in explicit0/15/30/45/60 bins. The project requires minutes<=60 for this view, so none are silently excluded.",
        f"2. Score ECDF: observed share at most65 is {facts['score_at_most65_share']:.3f}, among known scores only.",
        "3. Track boxes: quartile summaries of known session scores; different tracks are not equivalent randomised groups.",
        "4. Session counts: "+json.dumps(facts["track_sessions"])+". These count sessions, not unique learners.",
        f"5. Mode means: overall known-score mean is {facts['mean_score']:.3f}. Mode comparison is descriptive, not a treatment effect; in the supplied fixture mode coincides with day.",
        f"6. Scatter: {facts['complete_pairs']} complete minutes/score pairs; the unknown outcome stays missing, not zero.",
        "7. Day means: known-score contributor counts "+json.dumps(facts["known_by_day"])+". Repeated learners and missing outcomes limit interpretation.",
        "8. Correlation: Pearson linear association with a fixed-1 to1 scale; undefined cells remain undefined. Exact pair counts are in summary.json.",
        "Limits: synthetic small repeated-measures sample; no causal, significance, forecast or real-world teaching-quality conclusion.",
        "Interactive HTML contains all embedded data; hidden traces are not private. It bundles Plotly.js for offline rendering."]
    if df["minutes"].gt(60).any(): raise ValueError("Project histogram contract requires minutes<=60")
    with TemporaryDirectory(prefix="studyhub-eda-",dir=destination.parent) as temp:
        folder=Path(temp)
        with matplotlib.rc_context({"font.size":10,"axes.spines.top":False,"axes.spines.right":False}):
            for index in range(8):
                fig,ax=plt.subplots(figsize=(6,4),layout="constrained")
                try:
                    draw_panel(index,df,ax); fig.savefig(folder/f"chart-{index+1}.png",dpi=150,facecolor="white")
                finally: plt.close(fig)
            fig=overview(df)
            try: fig.savefig(folder/"overview.png",dpi=150,facecolor="white")
            finally: plt.close(fig)
        interactive(df).write_html(folder/"interactive.html",include_plotlyjs=True,full_html=True,auto_open=False,config={"responsive":True})
        df.to_csv(folder/"prepared_sessions.csv",index=False,lineterminator="\n")
        (folder/"summary.json").write_text(json.dumps(facts,indent=2,allow_nan=False),encoding="utf-8")
        (folder/"interpretation.txt").write_text("\n".join(notes)+"\n",encoding="utf-8")
        os.rename(folder,destination)
    return facts

def main(argv=None):
    parser=argparse.ArgumentParser(description="Week32 offline fictional Seaborn/Plotly exploration")
    parser.add_argument("source"); parser.add_argument("destination"); args=parser.parse_args(argv)
    try: facts=publish(load_sessions(args.source),args.destination)
    except (ValueError,OSError,csv.Error) as error: parser.exit(1,"Exploration stopped: "+str(error)+"\n")
    print("Published13 files; sessions",facts["sessions"],"known scores",facts["known_scores"])
    return 0

if __name__=="__main__": raise SystemExit(main())
