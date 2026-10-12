"""Week29 schema-specific audited cleaning practice. Python3.11+, pandas3.x."""
import argparse
import csv
from io import StringIO
import json
import os
from pathlib import Path
import sys
import tempfile
import numpy as np
import pandas as pd

COLUMNS = ["id", "name", "region", "score", "updated"]
MAX_BYTES, MAX_ROWS = 5 * 1024 * 1024, 10_000
ALIASES = {"np": "NP", "nepal": "NP", "jp": "JP", "japan": "JP"}

def load_raw(path):
    with Path(path).open("rb") as handle:
        data = handle.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("Input exceeds 5 MiB")
    try:
        text = data.decode("utf-8-sig")
        reader = csv.reader(StringIO(text, newline=""), strict=True)
        header = next(reader, None)
        if header is None or len(header) != len(set(header)) or set(header) != set(COLUMNS):
            raise ValueError("Require exactly id,name,region,score,updated with unique headers")
        rows = 0
        for record in reader:
            if not record:
                continue
            rows += 1
            if len(record) != len(COLUMNS) or rows > MAX_ROWS:
                raise ValueError("Ragged or oversized CSV")
    except (UnicodeDecodeError, csv.Error) as error:
        raise ValueError("Expected well-formed UTF-8 comma CSV") from error
    raw = pd.read_csv(StringIO(text), dtype="string", keep_default_na=False,
                      na_values=[""], skip_blank_lines=True)
    if raw.shape != (rows, len(COLUMNS)) or raw.columns.tolist() != header:
        raise ValueError("Parser/header mismatch")
    return raw[COLUMNS]

def normalize_text(raw):
    if not raw.columns.is_unique or set(raw.columns) != set(COLUMNS):
        raise ValueError("Unexpected source schema")
    if len(raw) > MAX_ROWS or not all(isinstance(dtype, pd.StringDtype) for dtype in raw.dtypes):
        raise ValueError("Require bounded raw string columns")
    out = raw[COLUMNS].reset_index(drop=True).copy()
    out["_source_record"] = range(1, len(out) + 1)
    for column in COLUMNS:
        out[column] = out[column].str.strip()
    out["name"] = out["name"].str.normalize("NFC").str.replace(r"\s+", " ", regex=True)
    tokens = out["region"].str.casefold()
    out["region"] = tokens.map(ALIASES).fillna(tokens).astype("string")
    out["score"] = out["score"].mask(out["score"].eq("").fillna(False), pd.NA)
    return out

def convert_types(normalized):
    out = normalized.copy()
    out["score"] = pd.to_numeric(out["score"], errors="coerce").astype("Float64")
    out["updated"] = pd.to_datetime(out["updated"], format="%Y-%m-%d", errors="coerce")
    return out

def rejection_reasons(normalized, typed):
    finite = pd.Series(np.isfinite(typed["score"].to_numpy(dtype=float, na_value=np.nan)), index=typed.index)
    rules = {
        "id_requires_three_ASCII_digits": ~normalized["id"].str.fullmatch(r"[0-9]{3}").fillna(False),
        "name_required": normalized["name"].isna() | normalized["name"].eq("").fillna(False),
        "unknown_region": ~normalized["region"].isin(["NP", "JP"]),
        "invalid_or_missing_updated_date": typed["updated"].isna() | ~normalized["updated"].str.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}").fillna(False),
        "score_not_numeric": normalized["score"].notna() & typed["score"].isna(),
        "score_nonfinite": typed["score"].notna() & ~finite,
        "score_outside_0_100": finite & ~typed["score"].between(0, 100).fillna(False),
    }
    reasons = {i: [] for i in typed.index}
    for reason, mask in rules.items():
        for i in typed.index[mask]:
            reasons[i].append(reason)
    return reasons

def validate_clean(clean):
    if clean.empty or clean.columns.tolist() != COLUMNS:
        raise ValueError("Require a nonempty canonical result")
    if not clean["id"].is_unique or not clean["id"].str.fullmatch(r"[0-9]{3}").fillna(False).all():
        raise ValueError("Invalid or repeated result ID")
    if not clean["name"].notna().all() or not clean["name"].str.strip().ne("").fillna(False).all():
        raise ValueError("Invalid result name")
    if not clean["region"].isin(["NP", "JP"]).all() or clean["updated"].isna().any():
        raise ValueError("Invalid result region/date")
    finite = np.isfinite(clean["score"].to_numpy(dtype=float, na_value=np.nan))
    if not finite.all() or not clean["score"].between(0, 100).fillna(False).all():
        raise ValueError("Invalid result score")

def cleaning_pipeline(raw):
    normalized = normalize_text(raw)
    typed = convert_types(normalized)
    reasons = rejection_reasons(normalized, typed)
    rejected = [i for i in typed.index if reasons[i]]
    accepted = typed.loc[[i for i in typed.index if not reasons[i]]].copy()
    ordered = accepted.sort_values(["id", "updated", "_source_record"], ascending=[True, False, False])
    repeated = ordered.duplicated("id", keep="first")
    removed = ordered.loc[repeated]
    latest = ordered.loc[~repeated].copy()
    if latest.empty:
        raise ValueError("No valid records remain")
    missing = latest["score"].isna()
    fill_value = None
    if missing.any():
        median = latest["score"].median()
        if pd.isna(median):
            raise ValueError("No observed retained scores to estimate a median")
        fill_value = float(median)
        latest["score"] = latest["score"].fillna(fill_value)
    estimated_records = latest.loc[missing, "_source_record"].astype(int).tolist()
    typed.loc[latest.index, "score"] = latest["score"]
    staged = typed[COLUMNS].copy()
    staged["updated"] = typed["updated"].dt.strftime("%Y-%m-%d").astype("string")
    staged["score"] = typed["score"].astype("string")
    source = raw[COLUMNS].reset_index(drop=True)
    changes = []
    for i in staged.index:
        for column in COLUMNS:
            old = None if pd.isna(source.at[i, column]) else str(source.at[i, column])
            new = None if pd.isna(staged.at[i, column]) else str(staged.at[i, column])
            if old != new:
                rule = "normalize_text"
                if column in ("score", "updated"):
                    rule = "convert_type"
                if column == "score" and int(typed.at[i, "_source_record"]) in estimated_records:
                    rule = "median_fill"
                changes.append({"record": i + 1, "column": column, "before": old, "after": new, "rule": rule})
    clean = latest[COLUMNS].reset_index(drop=True)
    clean["region"] = clean["region"].astype(pd.CategoricalDtype(["NP", "JP"]))
    validate_clean(clean)
    q1, q3 = clean["score"].quantile([0.25, 0.75], interpolation="linear")
    iqr = float(q3 - q1)
    lower, upper = float(q1 - 1.5 * iqr), float(q3 + 1.5 * iqr)
    flags = [] if iqr == 0 else clean.loc[(clean["score"] < lower) | (clean["score"] > upper), "id"].tolist()
    report = {
        "input_rows": len(raw), "kept_rows": len(clean),
        "quarantined": [{"record": i + 1, "reasons": reasons[i]} for i in rejected],
        "removed_duplicate_records": removed["_source_record"].astype(int).tolist(),
        "imputed_score_records": estimated_records, "score_fill_value": fill_value,
        "cell_changes": changes,
        "iqr_inspection": {"computed_on": "final scores, including disclosed estimates",
                           "iqr": iqr, "lower": lower, "upper": upper, "ids": flags,
                           "decision": "inspect only" if iqr > 0 else "zero IQR; no automatic decision"},
        "policy": {"schema": "three-digit text id; required name; region NP/JP; score finite0..100; updated YYYY-MM-DD",
                   "missing": "empty/whitespace-only scores only; invalid known tokens quarantined",
                   "latest": "newest valid date, then later input record for same-day ties",
                   "fill": "median of known retained scores; stop if estimation has no observations",
                   "audit": "source-to-final-staged cell changes include quarantined and superseded records",
                   "record": "one-based parsed observation position, not physical CSV line number",
                   "limits": {"bytes": MAX_BYTES, "rows": MAX_ROWS}},
    }
    assert len(raw) == len(clean) + len(rejected) + len(removed)
    return clean, report

def publish_bundle(clean, report, destination):
    """Publish one new directory; never overwrite an existing output bundle."""
    destination = Path(destination)
    if destination.exists():
        raise ValueError("Output already exists; choose a new bundle directory")
    validate_clean(clean)
    payload = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    csv_text = clean.to_csv(index=False, date_format="%Y-%m-%d", lineterminator="\n")
    with tempfile.TemporaryDirectory(prefix=".cleaning-", dir=destination.parent) as folder:
        stage = Path(folder)
        (stage / "clean.csv").write_text(csv_text, encoding="utf-8", newline="\n")
        (stage / "report.json").write_text(payload, encoding="utf-8", newline="\n")
        os.rename(stage, destination)

def main(argv=None):
    parser = argparse.ArgumentParser(description="Clean the supplied student schema into a new output bundle")
    parser.add_argument("raw_csv")
    parser.add_argument("new_bundle")
    args = parser.parse_args(argv)
    try:
        raw = load_raw(args.raw_csv)
        clean, report = cleaning_pipeline(raw)
        report["input_name"] = Path(args.raw_csv).name
        publish_bundle(clean, report, args.new_bundle)
    except (OSError, ValueError, pd.errors.ParserError) as error:
        print("No new bundle:", error, file=sys.stderr)
        return 1
    print("Published new bundle; raw CSV unchanged")
    return 0

if __name__ == "__main__":
    sys.exit(main())
