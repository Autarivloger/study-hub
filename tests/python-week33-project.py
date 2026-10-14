"""Check source provenance, numerical identities and safe report publication."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import numpy as np
import pandas as pd
from PIL import Image
from scipy import stats

sys.dont_write_bytecode=True
os.environ["PYTHONDONTWRITEBYTECODE"]="1"
ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/"docs"/"python-week33"
spec=importlib.util.spec_from_file_location("iris_report",FOLDER/"statistics_report.py")
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
source=FOLDER/"iris.data"; original=source.read_bytes()
assert hashlib.sha256(original).hexdigest()=="6f608b71a7317216319b4d27b4d9bc84e6abd734eda7872b71a458569e2656c0"
df=module.read_iris(original.decode())
assert len(df)==150 and df["row_id"].tolist()==list(range(1,151))
assert df[module.FEATURES].notna().all().all()
assert df.duplicated(module.FEATURES+["species"]).sum()>0, "Keep actual identical-value records"
before=df.copy(deep=True)
result,table,expected=module.analyse(df)
pd.testing.assert_frame_equal(df,before)
assert result["species_counts"]==dict.fromkeys(module.SPECIES,50)
assert abs(result["welch"]["difference_cm"]+0.93)<1e-12
assert result["welch"]["n_a"]==result["welch"]["n_b"]==50
ci=result["welch"]["marginal_95_ci_cm"]
assert ci[0]<result["welch"]["difference_cm"]<ci[1]<0
a=df.loc[df["species"].eq("Iris-setosa"),"sepal_length_cm"].to_numpy()
b=df.loc[df["species"].eq("Iris-versicolor"),"sepal_length_cm"].to_numpy()
va,vb=a.var(ddof=1)/len(a),b.var(ddof=1)/len(b)
se=np.sqrt(va+vb); dof=(va+vb)**2/(va**2/(len(a)-1)+vb**2/(len(b)-1))
manual_t=(a.mean()-b.mean())/se
assert abs(manual_t-result["welch"]["t"])<1e-10
assert abs(dof-result["welch"]["df"])<1e-10
assert np.allclose(ci,(a.mean()-b.mean())+np.array([-1,1])*stats.t.ppf(.975,dof)*se)
manual_expected=np.outer(table.sum(axis=1),table.sum(axis=0))/150
assert np.allclose(expected,manual_expected) and expected.min()>=5
manual_chi=float(((table.to_numpy()-expected)**2/expected).sum())
assert abs(result["chi_square"]["chi2"]-manual_chi)<1e-10
assert result["chi_square"]["df"]==2 and int(table.to_numpy().sum())==150
for test in ["welch","chi_square"]:
    assert 0<result[test]["p_raw"]<1
    assert result[test]["p_bonferroni_2"]==min(1,2*result[test]["p_raw"])
x=df["petal_length_cm"].to_numpy(); y=df["sepal_length_cm"].to_numpy()
fit=result["descriptive_fit"]; predicted=fit["intercept"]+fit["slope"]*x; residual=y-predicted
assert abs(residual.sum())<1e-10
manual_r2=1-float((residual**2).sum()/((y-y.mean())**2).sum())
assert abs(manual_r2-fit["in_sample_r_squared"])<1e-12
assert abs(fit["pearson_r"]**2-manual_r2)<1e-12
fig=module.overview(df,result,table)
assert len(fig.axes)==4 and len(fig.axes[3].collections)==3
assert np.allclose(fig.axes[3].lines[0].get_ydata(),fit["intercept"]+fit["slope"]*fig.axes[3].lines[0].get_xdata())
module.plt.close(fig)

with tempfile.TemporaryDirectory(prefix="studyhub-w33-test-") as temp:
    folder=Path(temp);destination=folder/"run-01"
    command=[sys.executable,str(FOLDER/"statistics_report.py"),str(source),str(destination)]
    run=subprocess.run(command,capture_output=True,text=True,encoding="utf-8")
    assert run.returncode==0,run.stderr
    assert len(list(destination.iterdir()))==7
    stored=json.loads((destination/"analysis.json").read_text(encoding="utf-8"))
    assert stored["source_sha256"]==hashlib.sha256(original).hexdigest()
    assert stored["welch"]==result["welch"] and stored["chi_square"]==result["chi_square"]
    with Image.open(destination/"overview.png") as picture: assert picture.size==(1500,1200)
    rows=pd.read_csv(destination/"regression_rows.csv")
    assert len(rows)==150 and rows["row_id"].tolist()==list(range(1,151))
    assert np.allclose(rows["sepal_length_cm"],rows["fitted_sepal_cm"]+rows["residual_cm"])
    assert np.allclose(pd.read_csv(destination/"expected.csv",index_col=0).to_numpy(),expected)
    notes=(destination/"interpretation.txt").read_text(encoding="utf-8")
    for phrase in ["not established","marginal95%","exactly two","not a causal","CC BY4.0"]: assert phrase in notes
    saved={p.name:p.read_bytes() for p in destination.iterdir()}
    assert subprocess.run(command,capture_output=True).returncode!=0
    assert saved=={p.name:p.read_bytes() for p in destination.iterdir()}
    assert source.read_bytes()==original
    for bad in ["", "1,2,3,4\n", "nan,3,2,1,Iris-setosa\n", "-1,3,2,1,Iris-setosa\n",
                "inf,3,2,1,Iris-setosa\n", "5,3,2,1,Unknown\n", "5,,2,1,Iris-setosa\n"]:
        try: module.read_iris(bad)
        except ValueError: pass
        else: raise AssertionError("Accepted malformed/unknown data")
    small=df.groupby("species",sort=False).head(3).copy()
    try: module.analyse(small)
    except ValueError: pass
    else: raise AssertionError("Sparse expected cells accepted")
    constant=df.copy();constant.loc[constant["species"].eq("Iris-setosa"),"sepal_length_cm"]=5.
    try: module.analyse(constant)
    except ValueError: pass
    else: raise AssertionError("Degenerate group variance accepted")
    original_save=module.matplotlib.figure.Figure.savefig
    def broken(*args,**kwargs): raise OSError("Simulated export failure")
    module.matplotlib.figure.Figure.savefig=broken
    try:
        try: module.publish(source,folder/"failed")
        except OSError: pass
        else: raise AssertionError("Export failure swallowed")
    finally: module.matplotlib.figure.Figure.savefig=original_save
    assert not (folder/"failed").exists() and not module.plt.get_fignums()
    assert sorted(p.name for p in folder.iterdir())==["run-01"]

print("PASS: real UCI source hash/150 retained plants, hand-checked Welch effect/df/CI, contingency expectations/chi-square, declared family adjustment, OLS residual/R2 identities,7 artifacts, immutable sources, invalid/sparse/degenerate rejection and safe publication cleanup.")
