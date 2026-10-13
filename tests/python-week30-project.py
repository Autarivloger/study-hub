"""Verify meaningful report values, input invariants, errors and publication."""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys
import tempfile
import pandas as pd

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "docs" / "python-week30"
spec = importlib.util.spec_from_file_location("sales_report",FOLDER/"sales_report.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def load():
    return (module.load_table(FOLDER/"sale_lines.csv",["line_id","date","product_id","customer_id","units","unit_price_minor"]),
            module.load_table(FOLDER/"products.csv",["product_id","product"]),
            module.load_table(FOLDER/"customers.csv",["customer_id","region"]))


def report(data=None,start="2025-01-01",end="2025-04-01"):
    return module.build_reports(*(data or load()),start,end)


def refused(data,start="2025-01-01",end="2025-04-01"):
    try:
        report(data,start,end)
    except (ValueError,pd.errors.MergeError):
        return
    raise AssertionError("Invalid input accepted")


data = load()
before = [frame.copy(deep=True) for frame in data]
reports,summary = report(data)
for old,new in zip(before,data):
    pd.testing.assert_frame_equal(old,new)
assert summary["sale_lines"] == 8 and summary["revenue_minor"] == 110000
assert reports["enriched"]["line_id"].tolist() == data[0]["line_id"].tolist()
assert reports["monthly"]["revenue_minor"].tolist() == [30000,25000,55000]
growth = reports["monthly"]["growth_pct"]
assert pd.isna(growth.iloc[0]) and abs(growth.iloc[1]+100/6)<1e-9 and growth.iloc[2]==120
assert len(reports["daily"])==90
assert reports["daily"]["rolling7_mean_minor"].iloc[:6].isna().all()
assert abs(reports["daily"]["rolling7_mean_minor"].iloc[6]-20000/7)<1e-9
region = reports["enriched"].groupby("region")["revenue_minor"].sum()
assert region.to_dict()=={"JP":50000,"NP":60000}
assert reports["top_products"].groupby("region").head(1)["product"].tolist()==["Book","Book"]
retention = reports["retention_pct"]
assert retention.loc[pd.Period("2025-01",freq="M")].tolist()==[100,50,100]
assert retention.loc[pd.Period("2025-02",freq="M"),1]==100
assert pd.isna(retention.loc[pd.Period("2025-02",freq="M"),2])
assert retention.loc[pd.Period("2025-03",freq="M"),0]==100
assert retention.loc[pd.Period("2025-03",freq="M"),[1,2]].isna().all()

# Every failure is a concrete data-contract boundary; no guesses are repaired.
for position,key in [(0,"line_id"),(1,"product_id"),(2,"customer_id")]:
    changed=list(load());changed[position]=pd.concat([changed[position],changed[position].iloc[[0]]],ignore_index=True)
    refused(changed)
    changed=list(load());changed[position].loc[0,key]=""
    refused(changed)
for field,value in [("product_id","MISSING"),("customer_id","MISSING"),("date","2025-02-30"),
                    ("date","2025-01-1"),("date","2025-04-01"),("units","0"),("units","-2"),
                    ("units","1.5"),("unit_price_minor","NaN"),("unit_price_minor","1000001")]:
    changed=list(load());changed[0].loc[0,field]=value
    refused(changed)
for start,end in [("2025-01-02","2025-04-01"),("2025-01-01","2025-01-01"),
                  ("2025-01-01 12:00","2025-04-01"),("2025-01-01","2027-02-01")]:
    refused(load(),start,end)

# Complete feed with no February events establishes a zero month, but March's
# percentage growth from that zero remains undefined.
changed=list(load());changed[0]=changed[0][~changed[0]["date"].str.startswith("2025-02")]
zero,_ = report(changed)
assert zero["monthly"]["revenue_minor"].tolist()==[30000,0,55000]
assert zero["monthly"]["growth_pct"].iloc[1]==-100 and pd.isna(zero["monthly"]["growth_pct"].iloc[2])

with tempfile.TemporaryDirectory(prefix="studyhub-w30-test-") as temp:
    folder=Path(temp)
    paths=[FOLDER/name for name in ["sale_lines.csv","products.csv","customers.csv"]]
    source_bytes=[path.read_bytes() for path in paths]
    destination=folder/"run-01"
    command=[sys.executable,str(FOLDER/"sales_report.py"),*[str(p) for p in paths],str(destination),
             "--start","2025-01-01","--end","2025-04-01","--complete-feed"]
    run=subprocess.run(command,capture_output=True,text=True)
    assert run.returncode==0,run.stderr
    assert len(list(destination.iterdir()))==7
    assert json.loads((destination/"summary.json").read_text(encoding="utf-8"))["revenue_minor"]==110000
    stored=pd.read_csv(destination/"monthly.csv")
    assert stored["revenue_minor"].tolist()==[30000,25000,55000]
    saved={path.name:path.read_bytes() for path in destination.iterdir()}
    rerun=subprocess.run(command,capture_output=True,text=True)
    assert rerun.returncode!=0
    assert saved=={path.name:path.read_bytes() for path in destination.iterdir()}
    assert source_bytes==[path.read_bytes() for path in paths]
    assert sorted(path.name for path in folder.iterdir())==["run-01"]
    no_contract=subprocess.run(command[:-1],capture_output=True,text=True)
    assert no_contract.returncode!=0
    bad=folder/"bad.csv";bad.write_text("id,id\nA,B\n",encoding="utf-8")
    try:
        module.load_table(bad,["id"])
    except ValueError:
        pass
    else:
        raise AssertionError("Duplicate CSV headers accepted")
    bad.write_text("id,value\nA,10,extra\n",encoding="utf-8")
    try:
        module.load_table(bad,["id","value"])
    except ValueError:
        pass
    else:
        raise AssertionError("Ragged CSV accepted")

print("PASS: Week30 actual revenue, joins, growth/zero-base, daily rolling, retention/future cells, immutable inputs, invalid-source rejection, CLI coverage contract and new-bundle preservation.")
