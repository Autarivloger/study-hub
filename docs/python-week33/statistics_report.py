"""Week33 local UCI Iris statistics; conditional exploratory teaching report."""
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
from scipy import stats
import csv
import io

FEATURES=["sepal_length_cm","sepal_width_cm","petal_length_cm","petal_width_cm"]
SPECIES=["Iris-setosa","Iris-versicolor","Iris-virginica"]

def read_iris(text):
    rows=[row for row in csv.reader(io.StringIO(text),strict=True) if row]
    if not rows or len(rows)>10000 or any(len(row)!=5 for row in rows):
        raise ValueError("Expected1–10000 five-field Iris rows")
    df=pd.DataFrame(rows,columns=FEATURES+["species"])
    if not df["species"].isin(SPECIES).all(): raise ValueError("Unknown species")
    for col in FEATURES:
        values=pd.to_numeric(df[col],errors="raise")
        if not (np.isfinite(values)&values.gt(0)&values.le(100)).all():
            raise ValueError("Need finite positive measurements<=100cm")
        df[col]=values.astype(float)
    df.insert(0,"row_id",np.arange(1,len(df)+1))
    return df

def analyse(df):
    for name in SPECIES:
        sample=df.loc[df["species"].eq(name),"sepal_length_cm"]
        if len(sample)<3 or sample.std(ddof=1)<=0: raise ValueError("Need variable groups of at least3")
    a=df.loc[df["species"].eq(SPECIES[0]),"sepal_length_cm"].to_numpy()
    b=df.loc[df["species"].eq(SPECIES[1]),"sepal_length_cm"].to_numpy()
    welch=stats.ttest_ind(a,b,equal_var=False,alternative="two-sided",nan_policy="raise")
    ci=welch.confidence_interval(0.95)
    band=np.where(df["sepal_width_cm"].ge(3.0),"wide","narrow")
    table=pd.crosstab(df["species"],band).reindex(index=SPECIES,columns=["narrow","wide"],fill_value=0)
    if (table.sum(axis=0)==0).any(): raise ValueError("Empty contingency margin")
    chi=stats.chi2_contingency(table.to_numpy(),correction=False)
    if (chi.expected_freq<5).any(): raise ValueError("Sparse expectations: choose a suitable method before testing")
    x=df["petal_length_cm"].to_numpy(); y=df["sepal_length_cm"].to_numpy()
    if np.ptp(x)==0 or np.ptp(y)==0: raise ValueError("Need varying regression coordinates")
    fit=stats.linregress(x,y)
    result={"n":len(df),"species_counts":{k:int(v) for k,v in df.groupby("species").size().items()},
        "welch":{"contrast":"setosa minus versicolor mean sepal length, cm","n_a":len(a),"n_b":len(b),
            "difference_cm":float(a.mean()-b.mean()),"t":float(welch.statistic),"df":float(welch.df),
            "p_raw":float(welch.pvalue),"p_bonferroni_2":min(1.,2*float(welch.pvalue)),
            "marginal_95_ci_cm":[float(ci.low),float(ci.high)]},
        "chi_square":{"threshold_cm":3.0,"chi2":float(chi.statistic),"df":int(chi.dof),
            "minimum_expected":float(chi.expected_freq.min()),"p_raw":float(chi.pvalue),
            "p_bonferroni_2":min(1.,2*float(chi.pvalue)),
            "cramers_v":float(np.sqrt(chi.statistic/(len(df)*min(table.shape[0]-1,table.shape[1]-1))))},
        "descriptive_fit":{"x":"petal length, cm","y":"sepal length, cm", "slope":float(fit.slope),
            "intercept":float(fit.intercept),"pearson_r":float(fit.rvalue),"in_sample_r_squared":float(fit.rvalue**2),
            "spearman_rho":float(stats.spearmanr(x,y).statistic),
            "within_species_pearson":{name:float(stats.pearsonr(part["petal_length_cm"],part["sepal_length_cm"]).statistic)
                for name,part in df.groupby("species")}}}
    return result,table,chi.expected_freq

def overview(df,result,table):
    fig,axs=plt.subplots(2,2,figsize=(10,8),layout="constrained")
    edges=np.histogram_bin_edges(df["sepal_length_cm"],bins=15)
    for name,part in df.groupby("species"):
        short=name.replace("Iris-","")
        axs[0,0].hist(part["sepal_length_cm"],bins=edges,histtype="step",label=short)
        axs[1,1].scatter(part["petal_length_cm"],part["sepal_length_cm"],label=short,s=18)
    axs[0,0].set(title="Recorded sepal-length distributions",xlabel="Sepal length (cm)",ylabel="Plants"); axs[0,0].legend(fontsize=8)
    axs[0,1].boxplot([df.loc[df["species"].eq(s),"sepal_length_cm"] for s in SPECIES],tick_labels=[s.replace("Iris-","") for s in SPECIES])
    axs[0,1].set(title="All three recorded species",ylabel="Sepal length (cm)")
    axs[1,0].imshow(table.to_numpy(),cmap="Blues")
    axs[1,0].set(xticks=[0,1],xticklabels=["Width<3cm","Width>=3cm"],yticks=[0,1,2],yticklabels=[s.replace("Iris-","") for s in SPECIES],title="Observed counts; expected counts supplied")
    for (row,col),value in np.ndenumerate(table.to_numpy()): axs[1,0].text(col,row,str(value),ha="center",va="center",color="white" if value>table.to_numpy().max()/2 else "black")
    fit=result["descriptive_fit"]; x=np.array([df["petal_length_cm"].min(),df["petal_length_cm"].max()])
    axs[1,1].plot(x,fit["intercept"]+fit["slope"]*x,color="black",linestyle="--",label="Pooled OLS")
    axs[1,1].set(title="Pooled fit mixes species; not a causal effect",xlabel="Petal length (cm)",ylabel="Sepal length (cm)")
    fig.suptitle(f"UCI Iris: {len(df)} recorded plants; conditional exploratory analysis")
    return fig

def publish(source,destination):
    source=Path(source); destination=Path(destination)
    if destination.exists() or not destination.parent.is_dir(): raise ValueError("Choose a new bundle in an existing parent")
    raw=source.read_bytes()
    if len(raw)>1024*1024: raise ValueError("Learning input exceeds1MiB")
    df=read_iris(raw.decode("utf-8-sig")); result,table,expected=analyse(df)
    result["source_sha256"]=hashlib.sha256(raw).hexdigest()
    result["source_url"]="https://archive.ics.uci.edu/dataset/53/iris"
    result["analysis_status"]="Exploratory conditional teaching analysis; no random-target-population or causal guarantee"
    notes=["UCI IRIS — CONDITIONAL EXPLORATORY STATISTICS REPORT",
        "Source: Fisher,R.(1936). Iris [Dataset]. UCI. https://doi.org/10.24432/C56C76 ; CC BY4.0.",
        f"Rows:{len(df)}; counts:{result['species_counts']}; four measurements in centimetres, no unknown fields accepted.",
        "Identical feature rows are retained: measurement equality does not identify duplicate specimens.",
        "The supplied historical iris.data snapshot retains the UCI-noted record discrepancies. Source hash:"+result["source_sha256"],
        "Historical collection is not established here as a random sample of a modern target; independence/model assumptions remain conditional.",
        "Test1: Welch two-sided setosa-minus-versicolor mean sepal length, not a causal intervention.",
        f"Difference cm:{result['welch']['difference_cm']:.6g}; marginal95% CI:{result['welch']['marginal_95_ci_cm']}; raw p:{result['welch']['p_raw']:.6g}; Bonferroni2 p:{result['welch']['p_bonferroni_2']:.6g}.",
        "Test2: species versus sepal width>=3cm, a fixed teaching threshold, Pearson chi-square with correction=False.",
        f"Minimum expected count:{result['chi_square']['minimum_expected']:.6g}; Cramer's V:{result['chi_square']['cramers_v']:.6g}; raw p:{result['chi_square']['p_raw']:.6g}; Bonferroni2 p:{result['chi_square']['p_bonferroni_2']:.6g}.",
        "Family: exactly two teaching tests; adjustment does not repair bias or make the marginal interval simultaneous.",
        "Correlations and OLS are descriptive exploration, not additional confirmatory significance claims. Within-species coefficients are retained in analysis.json.",
        f"Pooled slope:{result['descriptive_fit']['slope']:.6g} cm/cm; in-sample R squared:{result['descriptive_fit']['in_sample_r_squared']:.6g}.",
        "R squared is not percent correct predictions. Species composition, measurement version and source design limit interpretation.",
        "Do not report tiny positive p-values as exact zero, tune thresholds silently, remove inconvenient records, or infer causation."]
    with TemporaryDirectory(prefix="studyhub-statistics-",dir=destination.parent) as temp:
        folder=Path(temp); fig=overview(df,result,table)
        try: fig.savefig(folder/"overview.png",dpi=150,facecolor="white")
        finally: plt.close(fig)
        df.groupby("species")[FEATURES].agg(["count","mean","median","std","min","max"]).to_csv(folder/"descriptive.csv",lineterminator="\n")
        table.to_csv(folder/"contingency.csv",lineterminator="\n")
        pd.DataFrame(expected,index=table.index,columns=table.columns).to_csv(folder/"expected.csv",lineterminator="\n")
        fit=result["descriptive_fit"]; regression=df[["row_id","species","petal_length_cm","sepal_length_cm"]].copy()
        regression["fitted_sepal_cm"]=fit["intercept"]+fit["slope"]*regression["petal_length_cm"]
        regression["residual_cm"]=regression["sepal_length_cm"]-regression["fitted_sepal_cm"]
        regression.to_csv(folder/"regression_rows.csv",index=False,lineterminator="\n")
        (folder/"analysis.json").write_text(json.dumps(result,indent=2,allow_nan=False),encoding="utf-8")
        (folder/"interpretation.txt").write_text("\n".join(notes)+"\n",encoding="utf-8")
        os.rename(folder,destination)
    return result

def main(argv=None):
    parser=argparse.ArgumentParser(description="Week33 local Iris statistics report")
    parser.add_argument("source"); parser.add_argument("destination"); args=parser.parse_args(argv)
    try: result=publish(args.source,args.destination)
    except (ValueError,OSError,csv.Error) as error: parser.exit(1,"Statistics report stopped: "+str(error)+"\n")
    print("Published7 files; recorded plants",result["n"],"declared tests",2)
    return 0

if __name__=="__main__": raise SystemExit(main())
