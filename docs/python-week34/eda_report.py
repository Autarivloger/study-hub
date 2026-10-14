"""Week34: audited offline exploratory analysis of a pinned penguin CSV."""
import argparse
import hashlib
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import csv
import io
COLS=["species","island","bill_length_mm","bill_depth_mm","flipper_length_mm","body_mass_g","sex","year"]
MEASURES=["bill_length_mm","bill_depth_mm","flipper_length_mm","body_mass_g"]
SPECIES=["Adelie","Chinstrap","Gentoo"]
ISLANDS=["Biscoe","Dream","Torgersen"]

def load_tokens(text):
    rows=list(csv.reader(io.StringIO(text),strict=True))
    if not rows or rows[0]!=COLS or len(rows)<2 or len(rows)>10001:
        raise ValueError("Require documented header and1–10000 records")
    if any(len(row)!=len(COLS) for row in rows[1:]): raise ValueError("Ragged source rows")
    return pd.DataFrame(rows[1:],columns=COLS,dtype="string")

def clean_tokens(raw):
    if raw.columns.tolist()!=COLS: raise ValueError("Wrong raw schema")
    clean=raw.copy().reset_index(drop=True); changes=[]
    for col in COLS:
        for pos,old in enumerate(raw[col]):
            new=old.strip()
            if new!=old: changes.append([pos+1,col,old,new,"strip surrounding whitespace"])
            clean.loc[pos,col]=new
    for col,allowed in [("species",SPECIES),("island",ISLANDS)]:
        if not clean[col].isin(allowed).all(): raise ValueError("Unknown required category: "+col)
    for col in MEASURES:
        values=[]
        for pos,token in enumerate(clean[col]):
            if token=="NA":
                values.append(float("nan")); changes.append([pos+1,col,token,"<NA>","documented unknown, retained"])
            else:
                try: value=float(token)
                except ValueError as error: raise ValueError(f"Invalid {col}, record {pos+1}") from error
                if not np.isfinite(value) or not 0<value<=1_000_000:
                    raise ValueError(f"Invalid finite positive {col}, record {pos+1}")
                values.append(value)
        clean[col]=pd.Series(values,dtype=float)
    sex=[]
    for pos,token in enumerate(clean["sex"]):
        if token=="NA":
            sex.append(pd.NA); changes.append([pos+1,"sex",token,"<NA>","documented unknown, retained"])
        else:
            value=token.casefold()
            if value not in ["female","male"]: raise ValueError("Unknown sex token")
            if value!=token: changes.append([pos+1,"sex",token,value,"declared sex casefold rule"])
            sex.append(value)
    clean["sex"]=pd.Series(sex,dtype="string")
    if not clean["year"].isin(["2007","2008","2009"]).all(): raise ValueError("Expected source collection years2007–2009")
    clean["year"]=clean["year"].astype(int)
    clean.insert(0,"_source_record",np.arange(1,len(clean)+1))
    duplicate=clean.duplicated(COLS,keep=False)
    g=clean.groupby("species")["body_mass_g"]
    q1=g.transform(lambda s:s.quantile(.25)); q3=g.transform(lambda s:s.quantile(.75)); iqr=q3-q1
    flag=(clean["body_mass_g"].lt(q1-1.5*iqr)|clean["body_mass_g"].gt(q3+1.5*iqr)).fillna(False)
    clean["duplicate_value_candidate"]=duplicate
    clean["mass_iqr_flag"]=flag
    audit=pd.DataFrame(changes,columns=["source_record","column","old_token","new_token","rule"])
    decisions={"source_rows":len(raw),"retained_rows":len(clean),"deleted_rows":0,"imputed_values":0,
        "unknown_counts":{col:int(clean[col].isna().sum()) for col in COLS},
        "duplicate_candidate_rows":int(duplicate.sum()),"iqr_flag_rows":int(flag.sum()),
        "policy":"NA retained; malformed input stops; flags and equal-value candidates retained; no invented identity"}
    return clean,audit,decisions
def group_mass(df,keys):
    result=df.groupby(keys,dropna=False)["body_mass_g"].agg(["size","count","mean","median","std"])
    result["unknown_mass"]=result["size"]-result["count"]
    return result

def summarize(df):
    pairs=df.dropna(subset=["flipper_length_mm","body_mass_g"])
    if len(pairs)<3 or pairs["flipper_length_mm"].nunique()<2 or pairs["body_mass_g"].nunique()<2:
        raise ValueError("Report needs at least3 variable known flipper/mass pairs")
    profile=pd.DataFrame({"known":df[COLS].notna().sum(),"unknown":df[COLS].isna().sum(),
        "distinct_known":df[COLS].nunique(dropna=True)})
    categories=[]
    for col in ["species","island","sex","year"]:
        for name,n in df[col].astype("string").fillna("Unknown").value_counts().items(): categories.append([col,name,int(n)])
    support=pd.crosstab(df["species"],df["island"]).reindex(index=SPECIES,columns=ISLANDS,fill_value=0)
    known=df[MEASURES].notna().astype(int); counts=known.T.dot(known)
    both=df.dropna(subset=["sex","body_mass_g"])
    means=both.groupby(["species","sex"])["body_mass_g"].mean().unstack().reindex(index=SPECIES,columns=["female","male"])
    standardised=pd.DataFrame({"equal_known_sex_weight_mean_g":.5*means["female"]+.5*means["male"]})
    sensitivity=pd.concat([group_mass(df,["species"]).assign(rule="all known mass"),
        group_mass(both,["species"]).assign(rule="known sex and mass")]).reset_index()
    tables={"profile":profile,"category_counts":pd.DataFrame(categories,columns=["column","category","count"]),
        "species_mass":group_mass(df,["species"]),"species_sex_mass":group_mass(df,["species","sex"]),
        "support_species_island":support,"year_species_mass":group_mass(df,["year","species"]),
        "correlation":df[MEASURES].corr(min_periods=3),"pair_counts":counts,
        "sensitivity":sensitivity,"standardised_mass":standardised}
    species=tables["species_mass"]
    winner=species["mean"].idxmax()
    facts={"rows":len(df),"known_mass":int(df["body_mass_g"].notna().sum()),"unknown_mass":int(df["body_mass_g"].isna().sum()),
        "unknown_sex":int(df["sex"].isna().sum()),"known_sex_mass":len(both),"flipper_mass_pairs":len(pairs),
        "species_rows":{s:int(n) for s,n in df.groupby("species").size().items()},
        "species_known_mass":{s:int(n) for s,n in species["count"].items()},
        "species_mean_mass_g":{s:float(v) if pd.notna(v) else None for s,v in species["mean"].items()},
        "species_median_mass_g":{s:float(v) if pd.notna(v) else None for s,v in species["median"].items()},
        "largest_observed_mean_species":winner,"pooled_flipper_mass_r":float(pairs[["flipper_length_mm","body_mass_g"]].corr().iloc[0,1]),
        "within_species_flipper_mass_r":{s:float(p[["flipper_length_mm","body_mass_g"]].corr().iloc[0,1])
            if len(p)>=3 and p["flipper_length_mm"].nunique()>1 and p["body_mass_g"].nunique()>1 else None
            for s,p in pairs.groupby("species")},
        "year_labels":[int(v) for v in sorted(df["year"].unique())],
        "interpretation":"Descriptive historical recorded sample; no island causal effect, matched-bird growth or Antarctic census claim"}
    return tables,facts

def overview(df,tables):
    fig,axs=plt.subplots(4,2,figsize=(12,14),layout="constrained")
    known=df["body_mass_g"].dropna()
    axs[0,0].hist(known,bins=15); axs[0,0].set(title="1. Known mass distribution",xlabel="Mass g",ylabel="Records")
    present=[s for s in SPECIES if df.loc[df["species"].eq(s),"body_mass_g"].notna().any()]
    axs[0,1].boxplot([df.loc[df["species"].eq(s),"body_mass_g"].dropna() for s in present],tick_labels=present)
    axs[0,1].set(title="2. Known mass by species",ylabel="Mass g")
    pairs=df.dropna(subset=["flipper_length_mm","body_mass_g"])
    for s,part in pairs.groupby("species"):
        axs[1,0].scatter(part["flipper_length_mm"],part["body_mass_g"],label=s,s=15)
    axs[1,0].set(title="3. Complete coordinate pairs",xlabel="Flipper mm",ylabel="Mass g"); axs[1,0].legend(fontsize=8)
    profile=tables["profile"]; axs[1,1].barh(profile.index,profile["unknown"]); axs[1,1].set(title="4. Unknowns retained",xlabel="Records")
    means=df.dropna(subset=["sex","body_mass_g"]).groupby(["species","sex"])["body_mass_g"].mean().unstack().reindex(index=SPECIES,columns=["female","male"])
    x=np.arange(3)
    axs[2,0].bar(x-.18,means["female"],.35,label="female"); axs[2,0].bar(x+.18,means["male"],.35,label="male")
    axs[2,0].set(xticks=x,xticklabels=SPECIES,title="5. Recorded-sex known-mass means",ylabel="Mass g"); axs[2,0].legend(fontsize=8)
    support=tables["support_species_island"]; values=support.to_numpy()
    axs[2,1].imshow(values,cmap="Blues"); axs[2,1].set(xticks=np.arange(3),xticklabels=ISLANDS,yticks=np.arange(3),yticklabels=SPECIES,title="6. Observed comparison support")
    for (r,c),v in np.ndenumerate(values): axs[2,1].text(c,r,str(v),ha="center",va="center",color="white" if v>values.max()/2 else "black")
    annual=tables["year_species_mass"].reset_index()
    for s,part in annual.groupby("species"):
        axs[3,0].plot(part["year"],part["mean"],marker="o",label=s)
    axs[3,0].set(title="7. Year summaries, not matched growth",xlabel="Collection year",ylabel="Mean known mass g",xticks=sorted(df["year"].unique()))
    corr=tables["correlation"].to_numpy(dtype=float)
    image=axs[3,1].imshow(np.ma.masked_invalid(corr),vmin=-1,vmax=1,cmap="RdBu_r")
    axs[3,1].set(title="8. Descriptive correlations; pair n supplied",xticks=np.arange(4),xticklabels=["Bill L","Bill D","Flipper","Mass"],yticks=np.arange(4),yticklabels=["Bill L","Bill D","Flipper","Mass"])
    fig.colorbar(image,ax=axs[3,1],label="Pearson r")
    fig.suptitle(f"Palmer Penguins: {len(df)} recorded rows; descriptive EDA, unknown values retained")
    return fig

def narrative(facts,tables,decisions,digest):
    winner=facts["largest_observed_mean_species"]
    estimates="; ".join(f"{s}: {facts['species_mean_mass_g'][s]:.1f}g, n={facts['species_known_mass'][s]}"
        for s in facts["species_mean_mass_g"] if facts["species_mean_mass_g"][s] is not None)
    return "\n".join([
        "# Palmer Penguins — descriptive EDA report",
        "## Executive summary",
        f"Among {facts['known_mass']} known-mass records from {facts['rows']} source rows, {winner} has the largest observed species mean. Recorded means: {estimates}. "
        +f"Mass is unknown in {facts['unknown_mass']} rows and recorded sex in {facts['unknown_sex']}. "
        +"These historical observations do not isolate an island effect, establish matched-bird growth or describe an Antarctic census. Check collection/identity metadata and comparison support before causal or population claims.",
        "## Five questions and evidence",
        "1. Which evidence is available? profile.csv and category_counts.csv reconcile source/known/unknown counts.",
        "2. How does mass vary? species_mass.csv and overview panels1–2 show distributions and centres; no automatic outlier removal.",
        f"3. How do flippers and mass relate? {facts['flipper_mass_pairs']} complete pairs; pooled Pearson r={facts['pooled_flipper_mass_r']:.4f}. Pair counts and species-specific coefficients are supplied; association is not cause.",
        "4. How do species/recorded-sex groups compare? species_sex_mass.csv retains group counts and unknown-sex evidence. standardised_mass.csv answers an explicitly equal-known-sex-weight target, not a population or causal effect.",
        "5. Which island comparisons are supported? support_species_island.csv reports recorded combinations; a zero count is not a0g outcome or biological impossibility.",
        "## Eight-panel reading guide",
        "1. Histogram: known mass in grams; unknown outcomes excluded from this picture but retained in the ledger.",
        "2. Boxes: species distributions, not proof that all individuals in one species exceed every other individual.",
        "3. Scatter: coordinates stay paired; species clusters can drive pooled association.",
        "4. Missingness: documented unknowns, not zeros or proven invalid records.",
        "5. Recorded-sex means: use known sex+mass only; subgroup counts are in the CSV.",
        "6. Support: species/island mixture limits island-effect interpretation; absent cells remain unobserved outcomes.",
        "7. Collection years: repeated cross-sectional summaries, not verified individual trajectories; inspect year/species counts.",
        "8. Correlations: fixed-1 to1 scale, pairwise known observations; undefined values remain undefined.",
        "## Decisions and sensitivity",
        f"Retained {decisions['retained_rows']} of {decisions['source_rows']} rows; deleted {decisions['deleted_rows']}; imputed values {decisions['imputed_values']}. "
        +f"Retained IQR-flag rows:{decisions['iqr_flag_rows']}; equal-value candidate rows:{decisions['duplicate_candidate_rows']}. Neither is automatic error or identity evidence.",
        f"Known sex+mass subset:{facts['known_sex_mass']} rows, compared with all {facts['known_mass']} known masses in sensitivity.csv. Compare both mean and median ordering and subgroup counts; do not silently select a preferred result.",
        "The source's simplified table lacks identity metadata for independently checking matched individuals or every sampling assumption. Unknown-value mechanisms are not identified by the missingness display.",
        "No causal test, automatic significance search or verified random-population inference is claimed. Reasonable follow-up includes raw metadata review and new comparisons with appropriate support/design.",
        "## Provenance and reproduction",
        "Source: Horst, Hill & Gorman (2020), palmerpenguins; data collected by Kristen Gorman and Palmer Station LTER. https://allisonhorst.github.io/palmerpenguins/ ; https://doi.org/10.1371/journal.pone.0090081 ; CC0 data terms. See SOURCE.md.",
        "Input SHA-256: "+digest,
        "Reproduce with the retained CSV, this script and the documented environment. Use a fresh output bundle; keep raw bytes and earlier reports.",
        ""]) 

def publish(source,destination):
    source=Path(source); destination=Path(destination)
    if destination.exists() or not destination.parent.is_dir(): raise ValueError("Choose a new bundle in an existing parent")
    blob=source.read_bytes()
    if len(blob)>1024*1024: raise ValueError("Learning input exceeds1MiB")
    raw=load_tokens(blob.decode("utf-8-sig")); df,audit,decisions=clean_tokens(raw); tables,facts=summarize(df)
    digest=hashlib.sha256(blob).hexdigest(); facts["source_sha256"]=digest
    facts["source_url"]="https://allisonhorst.github.io/palmerpenguins/"
    report=narrative(facts,tables,decisions,digest)
    with TemporaryDirectory(prefix="studyhub-penguin-eda-",dir=destination.parent) as temp:
        folder=Path(temp)
        df.to_csv(folder/"cleaned.csv",index=False,lineterminator="\n")
        audit.to_csv(folder/"audit_changes.csv",index=False,lineterminator="\n")
        for name,frame in tables.items():
            include_index=name not in ["category_counts","sensitivity"]
            frame.to_csv(folder/(name+".csv"),index=include_index,lineterminator="\n")
        df.loc[df["duplicate_value_candidate"]|df["mass_iqr_flag"]].to_csv(folder/"review_flags.csv",index=False,lineterminator="\n")
        (folder/"decisions.json").write_text(json.dumps(decisions,indent=2,allow_nan=False),encoding="utf-8")
        (folder/"summary.json").write_text(json.dumps(facts,indent=2,allow_nan=False),encoding="utf-8")
        (folder/"report.md").write_text(report,encoding="utf-8")
        fig=overview(df,tables)
        try: fig.savefig(folder/"overview.png",dpi=150,facecolor="white")
        finally: plt.close(fig)
        os.rename(folder,destination)
    return facts

def main(argv=None):
    parser=argparse.ArgumentParser(description="Week34 audited offline penguin EDA")
    parser.add_argument("source"); parser.add_argument("destination");args=parser.parse_args(argv)
    try: facts=publish(args.source,args.destination)
    except (ValueError,OSError,csv.Error) as error: parser.exit(1,"EDA report stopped: "+str(error)+"\n")
    print("Published17 files; source rows",facts["rows"],"known mass",facts["known_mass"])
    return 0

if __name__=="__main__": raise SystemExit(main())
