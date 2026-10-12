"""Exercise real CSV/report boundaries using owned temporary fictional fixtures."""
import contextlib
import importlib.util
import io
import json
import math
from pathlib import Path
import tempfile
from unittest.mock import patch
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("dataset_profiler", ROOT / "docs/python-week28/dataset_profiler.py")
project = importlib.util.module_from_spec(spec)
spec.loader.exec_module(project)

def reject(action):
    try:
        action()
    except (ValueError, OSError):
        return
    raise AssertionError("Invalid input accepted")

with tempfile.TemporaryDirectory(prefix="studyhub-w28-tests-") as folder:
    root = Path(folder)
    source, destination = root / "students.csv", root / "report.json"
    source.write_text('id,name,score,region\n001,"Asha, Rai",80,NP\n002,Bina,,NA\n003,Chandra,90,JP\n001,"Asha, Rai",80,NP\n',
                      encoding="utf-8")
    original = source.read_bytes()
    df = project.load_csv(source)
    before = df.copy()
    report = project.profile(df)
    assert report["shape"] == [4, 4]
    assert report["duplicate_rows_after_first"] == 1
    assert report["columns"]["id"]["top_nonmissing"][0] == {"value": "001", "count": 2}
    assert "leading_zero_numeric_text" in report["columns"]["id"]["inspect_flags"]
    assert report["columns"]["score"]["missing"] == 1
    assert report["columns"]["score"]["missing_percent"] == 25
    assert report["columns"]["region"]["missing"] == 0
    assert math.isclose(report["columns"]["score"]["numeric_candidate"]["mean"], 250 / 3)
    assert df.equals(before) and source.read_bytes() == original
    json.dumps(report, allow_nan=False)

    def run():
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return project.main([str(source), str(destination)])
    assert run() == 0
    stored = json.loads(destination.read_text(encoding="utf-8"))
    assert stored["shape"] == [4, 4] and stored["input_name"] == "students.csv"
    assert source.read_bytes() == original
    previous = destination.read_bytes()
    unrelated = root / "report.json.unrelated.tmp"
    unrelated.write_text("belongs to someone else", encoding="utf-8")
    for invalid in ["", "id,id\n001,002\n", "id,score\n001,80,extra\n",
                    "id,score\n001\n", 'id,score\n"unclosed,80\n', ",score\n001,80\n"]:
        source.write_text(invalid, encoding="utf-8")
        reject(lambda: project.load_csv(source))
        assert run() == 1
        assert destination.read_bytes() == previous
        assert unrelated.read_text(encoding="utf-8") == "belongs to someone else"
    source.write_bytes(b"\xff\xfeinvalid")
    reject(lambda: project.load_csv(source))
    source.write_text("id,score\n", encoding="utf-8")
    empty = project.profile(project.load_csv(source))
    assert empty["shape"] == [0, 2]
    assert empty["columns"]["score"]["missing_percent"] is None
    source.write_text("id,label\n001,NA\n002,NULL\n003,\n", encoding="utf-8-sig")
    df = project.load_csv(source)
    assert df["id"].tolist() == ["001", "002", "003"]
    assert df["label"].isna().tolist() == [False, False, True]
    source.write_text('id,note\n001,"hello,\nworld"\n\n002,ok\n', encoding="utf-8", newline="\n")
    df = project.load_csv(source)
    assert df.shape == (2, 2) and df.loc[0, "note"] == "hello,\nworld"
    source.write_text("value\n10\ninf\n-inf\nunknown\n", encoding="utf-8")
    mixed = project.profile(project.load_csv(source))["columns"]["value"]
    assert mixed["numeric_candidate"] == {
        "parsed_nonmissing": 3, "failed_nonmissing": 1, "finite": 1, "nonfinite": 2,
        "min": 10.0, "max": 10.0, "mean": 10.0}
    assert "nonfinite_numeric_text" in mixed["inspect_flags"]
    assert "mixed_numeric_and_other_text" in mixed["inspect_flags"]
    source.write_text(" name ,constant\n Asha ,x\nBina,x\n", encoding="utf-8")
    flags = project.profile(project.load_csv(source))["columns"]
    assert "surrounding_whitespace" in flags[" name "]["inspect_flags"]
    assert "header_surrounding_whitespace" in flags[" name "]["inspect_flags"]
    assert "constant_observed_value" in flags["constant"]["inspect_flags"]
    source.write_text("value\n1e308\n1e308\n", encoding="utf-8")
    huge = project.profile(project.load_csv(source))
    assert math.isclose(huge["columns"]["value"]["numeric_candidate"]["mean"], 1e308)
    json.dumps(huge, allow_nan=False)
    source.write_text("category\n" + "".join(f"word{i}\n" for i in range(8)), encoding="utf-8")
    categories = project.profile(project.load_csv(source))["columns"]["category"]
    assert categories["unique_nonmissing"] == 8 and len(categories["top_nonmissing"]) == 5
    for limit, value in [("MAX_BYTES", 5), ("MAX_ROWS", 1), ("MAX_COLUMNS", 0)]:
        with patch.object(project, limit, value):
            reject(lambda: project.load_csv(source))
    reject(lambda: project.profile(pd.DataFrame([[1, 2]], columns=["x", "x"])))
    reject(lambda: project.profile(pd.DataFrame({"x": [1, 2]})))
    with contextlib.redirect_stderr(io.StringIO()):
        assert project.main([str(source), str(source)]) == 1
        assert project.main([str(source), str(root / "report.csv")]) == 1
    # Serialize failures and replacement failures preserve prior report and unrelated files.
    reject(lambda: project.write_report({"bad": float("nan")}, destination))
    assert destination.read_bytes() == previous
    with patch.object(project.os, "replace", side_effect=OSError("simulated replacement failure")):
        reject(lambda: project.write_report({"valid": True}, destination))
    assert destination.read_bytes() == previous
    assert sorted(path.name for path in root.glob("*.tmp")) == [unrelated.name]
    reject(lambda: project.write_report(report, root / "absent" / "report.json"))
    assert destination.read_bytes() == previous

print("PASS: Week28 profiler semantics, ID/NA policy, quoted/BOM/empty/malformed/limited input, finite statistics, nonmutation and atomic failure preservation.")
