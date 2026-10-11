"""Meaningful CLI/state rejection tests; no external websites or personal files."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "docs" / "python-week25"
spec = importlib.util.spec_from_file_location("price_tracker", SOURCE / "price_tracker.py")
tracker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tracker)

with tempfile.TemporaryDirectory(prefix="studyhub-w25-project-") as folder:
    root = Path(folder)
    run1, run2 = root / "run1", root / "run2"
    shutil.copytree(SOURCE / "sample-run1", run1)
    shutil.copytree(SOURCE / "sample-run2", run2)
    state = root / "snapshot.json"
    with contextlib.redirect_stdout(io.StringIO()):
        assert tracker.main([str(run1), str(state)]) == 0
    first = json.loads(state.read_text(encoding="utf-8"))
    assert first["changes"] == [["added", "A"], ["added", "B"]]
    with contextlib.redirect_stdout(io.StringIO()):
        assert tracker.main([str(run2), str(state)]) == 0
    second = json.loads(state.read_text(encoding="utf-8"))
    assert second["changes"] == [["changed", "A"], ["missing", "B"], ["added", "C"]]
    with contextlib.redirect_stdout(io.StringIO()):
        assert tracker.main([str(run2), str(state)]) == 0
    assert json.loads(state.read_text(encoding="utf-8"))["changes"] == []
    good = state.read_bytes()
    cases = [
        ("missing field", lambda p: (p / "page1.html").write_text('<main id="catalog" data-page="1" data-pages="2"><article class="item" data-id="A"><h2>Book</h2></article></main>', encoding="utf-8")),
        ("missing page", lambda p: (p / "page2.html").unlink()),
        ("layout changed", lambda p: (p / "page1.html").write_text("<h1>Login</h1>", encoding="utf-8")),
        ("conflicting id", lambda p: (p / "page2.html").write_text((p / "page2.html").read_text(encoding="utf-8").replace('data-id="C"', 'data-id="A"'), encoding="utf-8")),
        ("wrong page marker", lambda p: (p / "page2.html").write_text((p / "page2.html").read_text(encoding="utf-8").replace('data-page="2"', 'data-page="1"'), encoding="utf-8")),
        ("unsupported price", lambda p: (p / "page1.html").write_text((p / "page1.html").read_text(encoding="utf-8").replace("USD 10.00", "EUR 10,00"), encoding="utf-8")),
        ("incomplete set", lambda p: (p / "manifest.json").write_text((p / "manifest.json").read_text(encoding="utf-8").replace('"complete": true', '"complete": false'), encoding="utf-8")),
        ("path escape", lambda p: (p / "manifest.json").write_text((p / "manifest.json").read_text(encoding="utf-8").replace("page2.html", "../outside.html"), encoding="utf-8")),
    ]
    for number, (name, mutate) in enumerate(cases):
        bad = root / ("bad" + str(number))
        shutil.copytree(run2, bad)
        mutate(bad)
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            assert tracker.main([str(bad), str(state)]) == 1, name
        assert stderr.getvalue().startswith("FAILED:"), name
        assert state.read_bytes() == good, "Lost prior snapshot: " + name
    state.write_text('{"schema":true,"source":"own-practice-catalogue","records":[]}', encoding="utf-8")
    invalid = state.read_bytes()
    with contextlib.redirect_stderr(io.StringIO()):
        assert tracker.main([str(run2), str(state)]) == 1
    assert state.read_bytes() == invalid
    state.write_bytes(good)
    temporary = state.with_name(state.name + ".tmp")
    temporary.write_text("Keep unrelated file", encoding="utf-8")
    with contextlib.redirect_stderr(io.StringIO()):
        assert tracker.main([str(run2), str(state)]) == 1
    assert temporary.read_text(encoding="utf-8") == "Keep unrelated file"
    assert state.read_bytes() == good

print("PASS: valid runs, exact price/id changes, repeated no-change run; eight acquisition/parser failures preserve old bytes; invalid old state and unrelated temp files preserved; no network.")
