"""Verify actual evidence, token decisions and preservation in the EDA project."""
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

sys.dont_write_bytecode=True
os.environ["PYTHONDONTWRITEBYTECODE"]="1"
ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/"docs"/"python-week34"
spec=importlib.util.spec_from_file_location("penguin_eda",FOLDER/"eda_report.py")
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
source=FOLDER/"penguins.csv"; original=source.read_bytes()
digest="f204db2c753b0937caac3cb35258562c14f073e4bbc76be24b4c51ce22767a93"
assert hashlib.sha256(original).hexdigest()==digest
raw=module.load_tokens(original.decode());before=raw.copy(deep=True)
df,audit,decisions=module.clean_tokens(raw)
pd.testing.assert_frame_equal(raw,before)
assert len(raw)==len(df)==344 and df["_source_record"].tolist()==list(range(1,345))
assert decisions["deleted_rows"]==decisions["imputed_values"]==0
assert len(audit)==19 and set(audit["rule"])=={"documented unknown, retained"}
for col in module.MEASURES: assert df[col].isna().sum()==2
assert df["sex"].isna().sum()==11
tables,facts=module.summarize(df)
assert facts["rows"]==344 and facts["known_mass"]==342 and facts["unknown_mass"]==2
assert facts["known_sex_mass"]==333 and facts["unknown_sex"]==11 and facts["flipper_mass_pairs"]==342
assert facts["species_rows"]=={"Adelie":152,"Chinstrap":68,"Gentoo":124}
assert facts["species_known_mass"]=={"Adelie":151,"Chinstrap":68,"Gentoo":123}
assert facts["year_labels"]==[2007,2008,2009]
assert np.allclose([facts["species_mean_mass_g"][s] for s in module.SPECIES],
                   [3700.662251655629,3733.0882352941176,5076.016260162602])
assert facts["species_median_mass_g"]=={"Adelie":3700.,"Chinstrap":3700.,"Gentoo":5000.}
assert facts["largest_observed_mean_species"]=="Gentoo"
assert tables["support_species_island"].to_numpy().tolist()==[[44,56,52],[0,68,0],[124,0,0]]
assert (tables["pair_counts"].to_numpy()==342).all()
assert (tables["profile"]["known"]+tables["profile"]["unknown"]).eq(344).all()
assert tables["year_species_mass"]["size"].sum()==344
assert tables["year_species_mass"]["count"].sum()==342
assert tables["sensitivity"].groupby("rule")["count"].sum().to_dict()=={"all known mass":342,"known sex and mass":333}
known=df.dropna(subset=["sex","body_mass_g"])
for species in module.SPECIES:
    group=known.loc[known["species"].eq(species)]
    expected=.5*group.loc[group["sex"].eq("female"),"body_mass_g"].mean()+.5*group.loc[group["sex"].eq("male"),"body_mass_g"].mean()
    assert np.isclose(tables["standardised_mass"].loc[species,"equal_known_sex_weight_mean_g"],expected)
fig=module.overview(df,tables)
assert len(fig.axes)==9  # eight panels plus the correlation colourbar
assert len(fig.axes[2].collections)==3
assert sum(len(c.get_offsets()) for c in fig.axes[2].collections)==342
module.plt.close(fig)

with tempfile.TemporaryDirectory(prefix="studyhub-w34-test-") as temp:
    folder=Path(temp); destination=folder/"run-01"
    command=[sys.executable,str(FOLDER/"eda_report.py"),str(source),str(destination)]
    run=subprocess.run(command,capture_output=True,text=True,encoding="utf-8")
    assert run.returncode==0,run.stderr
    assert len(list(destination.iterdir()))==17
    saved=json.loads((destination/"summary.json").read_text(encoding="utf-8"))
    assert saved["source_sha256"]==digest and saved["known_mass"]==342
    clean=pd.read_csv(destination/"cleaned.csv")
    assert len(clean)==344 and clean["body_mass_g"].isna().sum()==2 and clean["sex"].isna().sum()==11
    assert len(pd.read_csv(destination/"audit_changes.csv"))==19
    assert pd.read_csv(destination/"review_flags.csv")["_source_record"].isin(range(1,345)).all()
    with Image.open(destination/"overview.png") as image: assert image.size==(1800,2100)
    text=(destination/"report.md").read_text(encoding="utf-8")
    for marker in ["342","344","5076.0g, n=123","not isolate an island effect","No causal test","CC0","sensitivity.csv"]: assert marker in text
    files={p.name:p.read_bytes() for p in destination.iterdir()}
    assert subprocess.run(command,capture_output=True).returncode!=0
    assert files=={p.name:p.read_bytes() for p in destination.iterdir()} and source.read_bytes()==original
    # The declared formatting rules are recorded, not silently applied.
    changed=raw.copy();changed.loc[0,"sex"]=" MALE "
    fixed,changes,_=module.clean_tokens(changed)
    assert fixed.loc[0,"sex"]=="male" and len(changes)==21
    assert set(changes.loc[changes["source_record"].eq(1),"rule"])=={"strip surrounding whitespace","declared sex casefold rule"}
    for col,value in [("body_mass_g","heavy"),("body_mass_g","inf"),("body_mass_g","-5"),
                      ("bill_length_mm",""),("species","Unknown"),("island","NA"),
                      ("sex","maybe"),("year","2010"),("year","NA")]:
        changed=raw.copy();changed.loc[0,col]=value
        try: module.clean_tokens(changed)
        except ValueError: pass
        else: raise AssertionError(f"Accepted invalid {col}={value}")
    for text in ["",original.decode().replace("species,island","island,species",1),"species,island\nA,B\n",
                 ",".join(module.COLS)+"\nA,B\n"]:
        try: module.load_tokens(text)
        except ValueError: pass
        else: raise AssertionError("Wrong schema/width accepted")
    # A positively weighted subgroup without evidence remains unestimated.
    missing_group=df.copy();missing_group.loc[missing_group["species"].eq("Gentoo")&missing_group["sex"].eq("female").fillna(False),"body_mass_g"]=np.nan
    altered,_=module.summarize(missing_group)
    assert pd.isna(altered["standardised_mass"].loc["Gentoo","equal_known_sex_weight_mean_g"])
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

print("PASS: exact source/344 retained records/342 masses/333 sex-mass rows,19 audited NA actions, actual species means/support/pair counts/standardisation,17 artifacts, invalid-source and overwrite rejection, missing-support preservation and export-failure cleanup.")
