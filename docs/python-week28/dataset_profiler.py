"""Week28 read-only CSV profiler. Python3.11+, pandas3.x, NumPy."""
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

MAX_BYTES = 5 * 1024 * 1024
MAX_ROWS = 10_000
MAX_COLUMNS = 100

def load_csv(path):
    """Read one bounded UTF-8 comma-separated snapshot; preserve text identifiers."""
    with Path(path).open("rb") as handle:
        raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("CSV exceeds 5 MiB; use a separately designed chunked profiler")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError("Expected UTF-8 CSV") from error
    try:
        reader = csv.reader(StringIO(text, newline=""), strict=True)
        header = next(reader, None)
        if not header or any(not name.strip() for name in header):
            raise ValueError("Require a nonempty header with named columns")
        if len(header) > MAX_COLUMNS:
            raise ValueError("Too many columns")
        if len(header) != len(set(header)):
            raise ValueError("Duplicate headers would make column reports ambiguous")
        rows = 0
        for record in reader:
            if not record:  # physically empty lines are not observations
                continue
            if len(record) != len(header):
                raise ValueError("Ragged CSV record")
            rows += 1
            if rows > MAX_ROWS:
                raise ValueError("Too many rows")
    except csv.Error as error:
        raise ValueError("Malformed CSV") from error
    df = pd.read_csv(StringIO(text), dtype="string", keep_default_na=False,
                     na_values=[""], skip_blank_lines=True)
    if df.shape != (rows, len(header)) or df.columns.tolist() != header:
        raise ValueError("Parser shape/header mismatch")
    return df

def profile(df):
    """Observe text fields; numeric-looking candidates are not verified business types."""
    if not df.columns.is_unique or not all(isinstance(name, str) for name in df.columns):
        raise ValueError("Require unique text column names")
    if len(df) > MAX_ROWS or len(df.columns) > MAX_COLUMNS:
        raise ValueError("Table exceeds profiling limits")
    if not all(isinstance(dtype, pd.StringDtype) for dtype in df.dtypes):
        raise ValueError("Expected explicitly loaded string columns")
    rows = len(df)
    columns = {}
    for name in df.columns:
        series = df[name]
        missing = int(series.isna().sum())
        known = int(series.count())
        unique = int(series.nunique())
        counts = series.value_counts(dropna=True).head(5)
        numeric = pd.to_numeric(series, errors="coerce")
        array = numeric.to_numpy(dtype=float, na_value=np.nan)
        finite_mask = np.isfinite(array)
        finite = array[finite_mask]
        parsed = int(numeric.notna().sum())
        nonfinite = int((numeric.notna().to_numpy(dtype=bool) & ~finite_mask).sum())
        failed = known - parsed
        mean = None
        if finite.size:
            # Scaling before summing avoids overflow from a large finite total.
            mean = float(np.sum(finite / finite.size))
            if not np.isfinite(mean):
                mean = None
        flags = []
        if missing:
            flags.append("missing_values")
        if known == 0:
            flags.append("all_missing_or_no_rows")
        elif unique == 1:
            flags.append("constant_observed_value")
        if bool((series.str.strip() != series).fillna(False).any()):
            flags.append("surrounding_whitespace")
        if bool(series.str.match(r"^[+-]?0\d").fillna(False).any()):
            flags.append("leading_zero_numeric_text")
        if parsed and failed:
            flags.append("mixed_numeric_and_other_text")
        if nonfinite:
            flags.append("nonfinite_numeric_text")
        if name.strip() != name:
            flags.append("header_surrounding_whitespace")
        columns[name] = {
            "storage_dtype": str(series.dtype),
            "observed": known, "missing": missing,
            "missing_percent": None if rows == 0 else round(missing / rows * 100, 2),
            "unique_nonmissing": unique,
            "top_nonmissing": [{"value": str(value), "count": int(count)} for value, count in counts.items()],
            "numeric_candidate": {
                "parsed_nonmissing": parsed, "failed_nonmissing": failed,
                "finite": int(finite.size), "nonfinite": nonfinite,
                "min": None if not finite.size else float(finite.min()),
                "max": None if not finite.size else float(finite.max()),
                "mean": mean,
            },
            "inspect_flags": flags,
        }
    return {
        "shape": [rows, len(df.columns)],
        "duplicate_rows_after_first": int(df.duplicated().sum()),
        "policy": {"missing": "empty fields only; literal NA/NULL preserved",
                   "input": "UTF-8 comma CSV; unique headers; blank physical lines skipped",
                   "numeric": "approximate float candidates only; never change source types",
                   "flags": "inspection signals, not instructions to delete",
                   "limits": {"bytes": MAX_BYTES, "rows": MAX_ROWS, "columns": MAX_COLUMNS}},
        "columns": columns,
    }

def write_report(report, destination):
    """Serialize first; replace only after writing an owned temporary file."""
    destination = Path(destination)
    payload = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         dir=destination.parent, prefix=destination.name + ".",
                                         suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(payload)
        os.replace(temporary, destination)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()

def main(argv=None):
    parser = argparse.ArgumentParser(description="Profile a bounded local CSV without cleaning it")
    parser.add_argument("csv_path")
    parser.add_argument("report_path")
    args = parser.parse_args(argv)
    source, destination = Path(args.csv_path), Path(args.report_path)
    try:
        if source.resolve() == destination.resolve():
            raise ValueError("Choose an output path different from the source")
        if destination.suffix.lower() != ".json":
            raise ValueError("Choose a .json report output")
        report = profile(load_csv(source))
        report["input_name"] = source.name
        write_report(report, destination)
    except (OSError, ValueError, pd.errors.ParserError) as error:
        print("No new report:", error, file=sys.stderr)
        return 1
    print("Report saved; input unchanged")
    return 0

if __name__ == "__main__":
    sys.exit(main())
