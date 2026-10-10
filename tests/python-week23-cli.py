"""Exercise the actual command-line program, including failures before output."""
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile

PROJECT = Path(__file__).resolve().parent.parent / "docs" / "python-week23-data-converter.py"
passed = 0


def run(source, output, input_format, output_format, expected=0):
    global passed
    result = subprocess.run(
        [sys.executable, "-X", "utf8", str(PROJECT), str(source), str(output),
         "--input-format", input_format, "--output-format", output_format],
        capture_output=True, encoding="utf-8", timeout=8,
    )
    assert result.returncode == expected, (result.returncode, result.stderr)
    if expected:
        assert result.stderr.startswith("Conversion failed:")
    else:
        assert "Converted" in result.stdout
    passed += 1


with tempfile.TemporaryDirectory(prefix="studyhub-w23-cli-") as folder:
    folder = Path(folder)
    csv = folder / "source.csv"
    csv.write_text('id,name,score\n007,"सीता & Hari",90\n008,東京,80\n', encoding="utf-8")
    paths = {"csv": csv, "json": folder / "source.json", "xml": folder / "source.xml"}
    run(csv, paths["json"], "csv", "json")
    run(csv, paths["xml"], "csv", "xml")
    expected = {"version": 2, "students": [
        {"id": "007", "name": "सीता & Hari", "score": 90},
        {"id": "008", "name": "東京", "score": 80},
    ]}
    for before, after in itertools.permutations(paths, 2):
        target = folder / (before + "-to-" + after + "." + after)
        run(paths[before], target, before, after)
        canonical = folder / (before + "-to-" + after + "-canonical.json")
        run(target, canonical, after, "json")
        assert json.loads(canonical.read_text(encoding="utf-8")) == expected
    bad_cases = [
        ("csv", b"\xff"),
        ("csv", b"id,name,score\n007,Sita,101\n"),
        ("csv", b"id,name,score\n007,Sita,90\n007,Hari,80\n"),
        ("csv", b"id,name,score\n007,Sita\n"),
        ("csv", b"id,name,score\n007,Sita,90,extra\n"),
        ("csv", b"id,id,score\n007,Sita,90\n"),
        ("csv", b"id,name,score\n007,Sita,90.5\n"),
        ("csv", b"x" * 1_000_001),
        ("json", b'{"version":2,"students":[],"students":[]}'),
        ("json", b'{"version":true,"students":[]}'),
        ("json", b'{"version":3,"students":[]}'),
        ("json", b'{"version":2,"students":[{"id":"007","name":"Sita","score":true}]}'),
        ("json", b'{"version":2,"students":[{"id":"007","name":"Sita","score":NaN}]}'),
        ("json", b'{"version":2,"students":[{"id":"007","name":"\\ud800","score":90}]}'),
        ("xml", b"<students>"),
        ("xml", b'<students version="3"/>'),
        ("xml", b'<!DOCTYPE students [<!ENTITY x "hi">]><students version="2"/>'),
        ("xml", b'<students version="2"><student id="007"><name>Sita</name><score>90</score><extra/></student></students>'),
        ("xml", b'<students version="2"><student id="007"><name>Sita</name><name>Hari</name></student></students>'),
    ]
    for index, (kind, content) in enumerate(bad_cases):
        source = folder / ("bad-" + str(index) + "." + kind)
        target = folder / ("bad-output-" + str(index) + ".json")
        source.write_bytes(content)
        run(source, target, kind, "json", expected=1)
        assert not target.exists()
        assert source.read_bytes() == content
    keep = folder / "existing.json"
    keep.write_text("KEEP", encoding="utf-8")
    run(csv, keep, "csv", "json", expected=1)
    assert keep.read_text(encoding="utf-8") == "KEEP"
    original = csv.read_bytes()
    run(csv, csv, "csv", "csv", expected=1)
    assert csv.read_bytes() == original
    assert not list(folder.glob(".convert-*.tmp"))

print(f"PASS: actual CLI {passed} conversions/rejections; six format directions; Unicode/IDs, malformed data, output/source preservation and temporary cleanup.")
