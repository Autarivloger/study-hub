"""Test cleaning decisions and output preservation on fictional, owned inputs."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
from unittest.mock import patch
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("cleaning_pipeline", ROOT / "docs/python-week29/cleaning_pipeline.py")
project = importlib.util.module_from_spec(spec)
spec.loader.exec_module(project)
sample = (ROOT / "docs/python-week29/messy_students.csv").read_text(encoding="utf-8")

def reject(action):
    try:
        action()
    except (ValueError, OSError):
        return
    raise AssertionError("Invalid operation accepted")

def canonical(frame):
    return frame.to_csv(index=False, date_format="%Y-%m-%d", lineterminator="\n")

with tempfile.TemporaryDirectory(prefix="studyhub-w29-tests-") as folder:
    root = Path(folder)
    source, bundle = root / "raw.csv", root / "run-01"
    source.write_text(sample, encoding="utf-8", newline="\n")
    original_bytes = source.read_bytes()
    raw = project.load_raw(source)
    original_frame = raw.copy()
    clean, report = project.cleaning_pipeline(raw)
    assert clean["id"].tolist() == ["001", "002", "003"]
    assert clean["name"].tolist() == ["Asha Rai", "Bina", "Chandra"]
    assert clean["region"].tolist() == ["NP", "JP", "JP"]
    assert clean["score"].tolist() == [90.0, 82.5, 75.0]
    assert clean["updated"].dt.strftime("%Y-%m-%d").tolist() == ["2026-01-03", "2026-01-02", "2026-01-02"]
    assert str(clean["score"].dtype) == "Float64" and str(clean["region"].dtype) == "category"
    assert report["input_rows"] == 7 and report["kept_rows"] == 3
    assert report["removed_duplicate_records"] == [1, 4]
    assert report["imputed_score_records"] == [3] and report["score_fill_value"] == 82.5
    reasons = {row["record"]: row["reasons"] for row in report["quarantined"]}
    assert reasons[5] == ["score_outside_0_100"]
    assert set(reasons[6]) == {"unknown_region", "invalid_or_missing_updated_date", "score_not_numeric"}
    assert raw.equals(original_frame) and source.read_bytes() == original_bytes
    assert len(raw) == len(clean) + len(report["quarantined"]) + len(report["removed_duplicate_records"])
    changes = {(item["record"], item["column"]): item for item in report["cell_changes"]}
    assert changes[1, "id"]["before"] == " 001 " and changes[1, "id"]["after"] == "001"
    assert changes[1, "name"]["after"] == "Asha Rai"
    assert changes[3, "score"] == {"record": 3, "column": "score", "before": None, "after": "82.5", "rule": "median_fill"}
    assert changes[6, "score"]["after"] is None
    assert changes[6, "updated"]["after"] is None
    json.dumps(report, allow_nan=False)

    project.publish_bundle(clean, report, bundle)
    saved_csv = (bundle / "clean.csv").read_bytes()
    saved_report = (bundle / "report.json").read_bytes()
    assert json.loads(saved_report)["score_fill_value"] == 82.5
    again, again_report = project.cleaning_pipeline(project.load_raw(bundle / "clean.csv"))
    assert canonical(again) == canonical(clean)
    assert not again_report["imputed_score_records"] and not again_report["cell_changes"]
    reject(lambda: project.publish_bundle(clean, report, bundle))
    assert (bundle / "clean.csv").read_bytes() == saved_csv and (bundle / "report.json").read_bytes() == saved_report

    bad_schema = raw.rename(columns={"id": "student"})
    reject(lambda: project.cleaning_pipeline(bad_schema))
    reject(lambda: project.cleaning_pipeline(pd.DataFrame({"id": [1]})))
    unrelated = root / ".cleaning-unrelated"
    unrelated.mkdir()
    (unrelated / "keep.txt").write_text("other work", encoding="utf-8")
    unpublished = root / "failed"
    with patch.object(project.os, "rename", side_effect=OSError("simulated publishing failure")):
        reject(lambda: project.publish_bundle(clean, report, unpublished))
    assert not unpublished.exists()
    assert sorted(path.name for path in root.glob(".cleaning-*")) == [unrelated.name]
    assert (unrelated / "keep.txt").read_text(encoding="utf-8") == "other work"
    reject(lambda: project.publish_bundle(clean, {"bad": float("nan")}, unpublished))
    reject(lambda: project.publish_bundle(clean, report, root / "absent" / "bundle"))
    assert not unpublished.exists()

    def run():
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return project.main([str(source), str(root / "cli-run")])
    assert run() == 0
    assert source.read_bytes() == original_bytes
    cli_before = (root / "cli-run" / "clean.csv").read_bytes()
    assert run() == 1  # refuses an existing destination
    assert (root / "cli-run" / "clean.csv").read_bytes() == cli_before

    header = "id,name,region,score,updated\n"
    for invalid in ["", "id,id,region,score,updated\n", header + "001,Asha,NP,80\n",
                    header + '001,"unclosed,NP,80,2026-01-01\n', "id,name,score,updated\n"]:
        source.write_text(invalid, encoding="utf-8", newline="\n")
        reject(lambda: project.load_raw(source))
    source.write_bytes(b"\xff\xfeinvalid")
    reject(lambda: project.load_raw(source))
    source.write_text(header, encoding="utf-8")
    reject(lambda: project.cleaning_pipeline(project.load_raw(source)))
    source.write_text(header + "001,Asha,NP,,2026-01-01\n", encoding="utf-8")
    reject(lambda: project.cleaning_pipeline(project.load_raw(source)))
    # Each known invalid token is quarantined, never median-filled.
    invalid_rows = [
        "002,Bina,NP,oops,2026-01-01",
        "003,Chandra,NP,inf,2026-01-01",
        "004,Dipa,NP,-1,2026-01-01",
        "005,Eka,UNKNOWN,80,2026-01-01",
        "006,Fina,NP,80,2026-02-30",
        "007,Gita,NP,80,2026-1-1",
        "08,Hari,NP,80,2026-01-01",
        "009,   ,NP,80,2026-01-01",
    ]
    source.write_text(header + "001,Asha,NP,80,2026-01-01\n" + "\n".join(invalid_rows) + "\n", encoding="utf-8")
    only_valid, ledger = project.cleaning_pipeline(project.load_raw(source))
    assert only_valid["id"].tolist() == ["001"]
    assert len(ledger["quarantined"]) == 8 and not ledger["imputed_score_records"]
    assert ledger["iqr_inspection"]["decision"] == "zero IQR; no automatic decision"
    source.write_text(header + "001,Asha,NP,150,bad\n", encoding="utf-8")
    reject(lambda: project.cleaning_pipeline(project.load_raw(source)))
    # A invalid latest update must not displace the older valid observation.
    source.write_text(header + "001,Asha,NP,80,2026-01-01\n001,Asha,NP,oops,2026-01-03\n", encoding="utf-8")
    retained, ledger = project.cleaning_pipeline(project.load_raw(source))
    assert retained["score"].tolist() == [80.0] and len(ledger["quarantined"]) == 1
    # Exact duplicates follow the declared same-date later-record tie policy.
    source.write_text(header + "001,Asha,NP,80,2026-01-01\n001,Asha,NP,80,2026-01-01\n", encoding="utf-8-sig")
    retained, ledger = project.cleaning_pipeline(project.load_raw(source))
    assert ledger["removed_duplicate_records"] == [1]
    source.write_text(header + '001,"Asha,\nRai",NP,80,2026-01-01\n\n', encoding="utf-8", newline="\n")
    retained, ledger = project.cleaning_pipeline(project.load_raw(source))
    assert retained["name"].tolist() == ["Asha, Rai"] and ledger["input_rows"] == 1
    for limit, amount in [("MAX_BYTES", 5), ("MAX_ROWS", 0)]:
        with patch.object(project, limit, amount):
            reject(lambda: project.load_raw(source))
    invalid_clean = clean.copy()
    invalid_clean.loc[0, "score"] = 101
    reject(lambda: project.publish_bundle(invalid_clean, report, unpublished))
    assert not unpublished.exists()
    assert (bundle / "clean.csv").read_bytes() == saved_csv

print("PASS: Week29 schema/normalization/conversion/quarantine/latest ties/median provenance/audit/idempotence, malformed/limited inputs and output-bundle failure preservation.")
