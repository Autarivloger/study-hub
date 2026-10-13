"""Week30 fictional complete-feed sales analytics. Python3.11+, pandas3.x."""

import argparse
import csv
import io
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import pandas as pd


def load_table(path, columns):
    raw = Path(path).read_bytes()
    if len(raw) > 5 * 1024 * 1024:
        raise ValueError("CSV exceeds this exercise's 5 MiB limit")
    text = raw.decode("utf-8-sig")
    rows = list(csv.reader(io.StringIO(text), strict=True))
    if not rows or len(set(rows[0])) != len(rows[0]) or set(rows[0]) != set(columns):
        raise ValueError("Missing, duplicate or unexpected CSV headers")
    if len(rows) > 10001 or any(len(row) != len(rows[0]) for row in rows[1:]):
        raise ValueError("CSV row count/width violates the learning contract")
    return pd.read_csv(io.StringIO(text), dtype="string", keep_default_na=False)


def require_keys(frame, key, unique):
    if frame[key].isna().any() or frame[key].str.strip().eq("").any():
        raise ValueError(f"Missing key: {key}")
    if unique and frame[key].duplicated().any():
        raise ValueError(f"Duplicate key: {key}")


def build_reports(lines, products, customers, start, end):
    lines, products, customers = lines.copy(), products.copy(), customers.copy()
    schemas = [(lines, {"line_id","date","product_id","customer_id","units","unit_price_minor"}),
               (products, {"product_id","product"}), (customers, {"customer_id","region"})]
    for frame, columns in schemas:
        if not frame.columns.is_unique or set(frame.columns) != columns or frame.empty:
            raise ValueError("Unexpected or empty input table")
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    if start.tzinfo is not None or end.tzinfo is not None or start.day != 1 or end.day != 1:
        raise ValueError("Use naive month-start calendar boundaries")
    if start != start.normalize() or end != end.normalize() or end <= start:
        raise ValueError("Expected an increasing midnight month-start window")
    months = pd.date_range(start, end, freq="MS", inclusive="left")
    if len(months) > 24:
        raise ValueError("This learning report supports up to24 complete months")
    require_keys(lines, "line_id", True)
    for key in ["product_id","customer_id"]:
        require_keys(lines,key,False)
    require_keys(products,"product_id",True)
    require_keys(customers,"customer_id",True)
    for frame, field in [(products,"product"),(customers,"region")]:
        if frame[field].isna().any() or frame[field].str.strip().eq("").any():
            raise ValueError("Lookup descriptions must be known")
    if not lines["date"].str.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}").fillna(False).all():
        raise ValueError("Dates must use YYYY-MM-DD")
    lines["date"] = pd.to_datetime(lines["date"],format="%Y-%m-%d",errors="raise")
    if not (lines["date"].ge(start)&lines["date"].lt(end)).all():
        raise ValueError("Sale date lies outside the declared complete window")
    for column in ["units","unit_price_minor"]:
        valid = lines[column].str.fullmatch(r"[0-9]{1,7}").fillna(False)
        if not valid.all():
            raise ValueError("Amounts must be nonnegative integer tokens")
        lines[column] = pd.to_numeric(lines[column],errors="raise").astype("int64")
        if not lines[column].between(1,1_000_000).all():
            raise ValueError("This exercise requires positive units/prices <=1000000")
    lines["revenue_minor"] = lines["units"] * lines["unit_price_minor"]
    out = lines
    for lookup, key in [(products,"product_id"),(customers,"customer_id")]:
        out = out.merge(lookup,on=key,how="left",validate="many_to_one",indicator=True)
        if not out["_merge"].eq("both").all():
            raise ValueError(f"Unmatched foreign key: {key}")
        out = out.drop(columns="_merge")
    assert out["line_id"].tolist() == lines["line_id"].tolist()
    assert int(out["revenue_minor"].sum()) == int(lines["revenue_minor"].sum())
    indexed = out.set_index("date").sort_index()
    # Caller contract: all events captured for every day in [start,end).
    daily = indexed["revenue_minor"].resample("D").sum().reindex(
        pd.date_range(start,end,freq="D",inclusive="left"),fill_value=0)
    daily_report = daily.rename("revenue_minor").to_frame()
    daily_report["rolling7_mean_minor"] = daily.rolling(7,min_periods=7).mean()
    monthly = daily.resample("MS",closed="left",label="left").sum().reindex(months,fill_value=0)
    monthly_report = monthly.rename("revenue_minor").to_frame()
    previous = monthly.shift(1)
    monthly_report["change_minor"] = monthly-previous
    monthly_report["growth_pct"] = 100*(monthly-previous)/previous.where(previous.gt(0))
    top = out.groupby(["region","product_id","product"],as_index=False,observed=True).agg(
        revenue_minor=("revenue_minor","sum"),units=("units","sum"))
    top = top.sort_values(["region","revenue_minor","product_id"],ascending=[True,False,True])
    top["rank_in_region"] = top.groupby("region").cumcount()+1
    activity = out.assign(month=out["date"].dt.to_period("M"))
    activity["cohort"] = activity.groupby("customer_id")["month"].transform("min")
    activity["age"] = ((activity["month"].dt.year-activity["cohort"].dt.year)*12
                       +activity["month"].dt.month-activity["cohort"].dt.month)
    counts = activity.groupby(["cohort","age"])["customer_id"].nunique().unstack("age")
    counts = counts.reindex(columns=range(len(months))).astype("float64")
    last = months[-1].to_period("M")
    for cohort in counts.index:
        for age in counts.columns:
            counts.loc[cohort,age] = (0 if pd.isna(counts.loc[cohort,age]) else counts.loc[cohort,age]) if cohort+int(age)<=last else float("nan")
    retention = 100*counts.div(counts[0],axis=0)
    assert int(monthly.sum()) == int(out["revenue_minor"].sum())
    assert retention.stack().dropna().between(0,100).all()
    summary = {"sale_lines":len(out),"revenue_minor":int(monthly.sum()),
               "start_inclusive":str(start.date()),"end_exclusive":str(end.date()),
               "coverage_policy":"Caller declares complete event feed; absent events are zero",
               "currency_policy":"One fictional currency; integer minor units; positive sales only",
               "price_policy":"Recorded transaction price, not current catalog price",
               "cohort_policy":"First observed purchase in this window, not proven acquisition"}
    return {"enriched":out,"daily":daily_report,"monthly":monthly_report,
            "top_products":top,"cohort_counts":counts,"retention_pct":retention},summary


def publish(reports, summary, destination):
    destination = Path(destination)
    if destination.exists() or not destination.parent.is_dir():
        raise ValueError("Choose a new bundle name in an existing parent directory")
    with TemporaryDirectory(prefix="studyhub-sales-",dir=destination.parent) as temp:
        folder = Path(temp)
        for name,frame in reports.items():
            include_index = name in {"daily","monthly","cohort_counts","retention_pct"}
            frame.to_csv(folder/(name+".csv"),index=include_index,date_format="%Y-%m-%d",lineterminator="\n")
        (folder/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False,allow_nan=False),encoding="utf-8")
        os.rename(folder,destination)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Week30 complete-feed sales analytics practice")
    parser.add_argument("lines");parser.add_argument("products");parser.add_argument("customers")
    parser.add_argument("destination");parser.add_argument("--start",required=True)
    parser.add_argument("--end",required=True,help="Exclusive complete-month boundary")
    parser.add_argument("--complete-feed",action="store_true",required=True,
                        help="Confirm every event in the window is represented")
    args = parser.parse_args(argv)
    try:
        lines = load_table(args.lines,["line_id","date","product_id","customer_id","units","unit_price_minor"])
        products = load_table(args.products,["product_id","product"])
        customers = load_table(args.customers,["customer_id","region"])
        reports,summary = build_reports(lines,products,customers,args.start,args.end)
        publish(reports,summary,args.destination)
    except (ValueError,OSError,csv.Error) as error:
        parser.exit(1,"Report stopped: "+str(error)+"\n")
    print("Published",len(reports)+1,"files; sale lines",summary["sale_lines"],"revenue minor units",summary["revenue_minor"])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
