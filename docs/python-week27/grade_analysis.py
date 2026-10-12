"""Week27 vectorized grade-analysis practice. Python3.11+/NumPy2.x; plain numeric CSV."""
import argparse
import io
import json
from pathlib import Path
import sys
import numpy as np

def validate_scores(scores):
    values = np.asarray(scores)
    if values.ndim != 2 or not 1 <= values.shape[0] <= 10_000 or not 1 <= values.shape[1] <= 200:
        raise ValueError("Need a nonempty student-by-assignment table within practice limits")
    if values.dtype.kind not in "iuf":
        raise ValueError("Need real numeric scores, not booleans/objects/text")
    values = values.astype(np.float64, copy=True)
    if not np.isfinite(values).all() or ((values < 0) | (values > 100)).any():
        raise ValueError("Every score must be finite and in 0..100")
    return values

def analyse(scores, curve=5.0, threshold=2.0, pass_score=60.0):
    values = validate_scores(scores)
    if not np.isfinite(curve) or not -100 <= curve <= 100:
        raise ValueError("Curve must be finite and in -100..100")
    if not np.isfinite(threshold) or threshold <= 0:
        raise ValueError("Z threshold must be finite and positive")
    if not np.isfinite(pass_score) or not 0 <= pass_score <= 100:
        raise ValueError("Pass score must be finite and in 0..100")
    student_means = values.mean(axis=1)
    assignment_means = values.mean(axis=0)
    spread = student_means.std(ddof=0)
    z = np.zeros(student_means.shape, dtype=np.float64)
    np.divide(student_means-student_means.mean(), spread, out=z, where=spread>0)
    flags = np.absolute(z) >= threshold
    curved = np.clip(values + curve, 0, 100)
    low = values.min(axis=0, keepdims=True)
    ranges = values.max(axis=0, keepdims=True)-low
    normalized = np.zeros(values.shape, dtype=np.float64)
    np.divide(values-low, ranges, out=normalized, where=ranges!=0)
    return {
        "schema": 1,
        "orientation": "rows=students; columns=assignments; indexes are zero-based",
        "shape": list(values.shape),
        "policy": {"curve_points": float(curve), "clip_range": [0, 100],
                   "pass_score": float(pass_score), "z_threshold": float(threshold),
                   "std_ddof": 0, "constant_column_normalized_value": 0.0,
                   "zero_spread_z_value": 0.0, "missing_scores": "reject",
                   "outlier_basis": "raw student means; inspect only"},
        "student_means": student_means.tolist(),
        "student_min": values.min(axis=1).tolist(),
        "student_max": values.max(axis=1).tolist(),
        "student_std": values.std(axis=1, ddof=0).tolist(),
        "assignment_means": assignment_means.tolist(),
        "assignment_min": values.min(axis=0).tolist(),
        "assignment_max": values.max(axis=0).tolist(),
        "assignment_std": values.std(axis=0, ddof=0).tolist(),
        "class_mean": float(values.mean()),
        "student_z": z.tolist(),
        "inspect_student_indexes": np.flatnonzero(flags).tolist(),
        "raw_pass_flags": (student_means >= pass_score).tolist(),
        "curved_scores": curved.tolist(),
        "curved_student_means": curved.mean(axis=1).tolist(),
        "normalized_columns": normalized.tolist(),
    }

def load_scores(path):
    with path.open("rb") as stream:
        raw = stream.read(2_000_001)
    if len(raw) > 2_000_000:
        raise ValueError("Practice input exceeds 2 MB")
    text = raw.decode("utf-8-sig")
    if not text.strip():
        raise ValueError("Empty score file")
    # Contract: plain rectangular numeric CSV; no headers, quotes, labels or comments.
    values = np.loadtxt(io.StringIO(text), delimiter=",", comments=None,
                        dtype=np.float64, ndmin=2)
    return validate_scores(values)

def save_report(path, report):
    encoded = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)
    temporary = path.with_name(path.name + ".tmp")
    owned = False
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            owned = True
            stream.write(encoded)
        temporary.replace(path)
        owned = False
    finally:
        if owned:
            temporary.unlink(missing_ok=True)

def main(argv=None):
    parser = argparse.ArgumentParser(description="Vectorized grade analysis of plain numeric CSV", allow_abbrev=False)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--curve", type=float, default=5.0)
    parser.add_argument("--z-threshold", type=float, default=2.0)
    parser.add_argument("--pass-score", type=float, default=60.0)
    args = parser.parse_args(argv)
    try:
        if args.input.resolve() == args.output.resolve() or args.output.suffix.lower() != ".json":
            raise ValueError("Choose a separate .json output path")
        scores = load_scores(args.input)
        report = analyse(scores, args.curve, args.z_threshold, args.pass_score)
        report["input_name"] = args.input.name
        save_report(args.output, report)
    except (OSError, UnicodeError, ValueError, TypeError, ArithmeticError) as error:
        print("FAILED:", error, file=sys.stderr)
        return 1
    print("Students:", report["shape"][0], "Assignments:", report["shape"][1])
    print("Raw class mean:", round(report["class_mean"], 2))
    print("Inspect indexes:", report["inspect_student_indexes"])
    print("Report saved")
    return 0

if __name__ == "__main__":
    sys.exit(main())
