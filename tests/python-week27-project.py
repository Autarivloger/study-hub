"""Verify mathematical contracts and preserved files using fictional score inputs."""
import ast
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
PROJECT = ROOT / "docs/python-week27/grade_analysis.py"
spec = importlib.util.spec_from_file_location("grade_analysis", PROJECT)
grade = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grade)
tree = ast.parse(PROJECT.read_text(encoding="utf-8"))
assert not any(isinstance(node, (ast.For, ast.While, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)) for node in ast.walk(tree)), "Project contains a Python loop"

scores = np.array([[80., 90., 100.], [60., 70., 80.], [40., 50., 60.]])
before = scores.copy()
report = grade.analyse(scores)
np.testing.assert_allclose(report["student_means"], [90., 70., 50.])
np.testing.assert_allclose(report["assignment_means"], [60., 70., 80.])
np.testing.assert_allclose(report["student_min"], [80., 60., 40.])
np.testing.assert_allclose(report["assignment_max"], [80., 90., 100.])
np.testing.assert_allclose(report["student_std"], np.sqrt(200/3))
np.testing.assert_allclose(report["curved_scores"], [[85., 95., 100.], [65., 75., 85.], [45., 55., 65.]])
np.testing.assert_allclose(report["normalized_columns"], [[1., 1., 1.], [.5, .5, .5], [0., 0., 0.]])
assert np.array_equal(scores, before), "Analysis mutated source"
assert report["raw_pass_flags"] == [True, True, False]
assert report["policy"]["std_ddof"] == 0
constant = grade.analyse(np.full((3, 2), 98.))
assert constant["student_z"] == [0., 0., 0.]
assert constant["normalized_columns"] == [[0., 0.], [0., 0.], [0., 0.]]
assert constant["curved_scores"] == [[100., 100.], [100., 100.], [100., 100.]]
outliers = grade.analyse(np.array([[90., 90.]] * 4 + [[0., 0.]]), threshold=2)
assert outliers["inspect_student_indexes"] == [4]
np.testing.assert_allclose(outliers["student_z"], [.5, .5, .5, .5, -2.])
for invalid in [np.array([[np.nan]]), np.array([[np.inf]]), np.array([[-1.]]),
                np.array([[101.]]), np.empty((0, 2)), np.array([1., 2.]),
                np.array([[True]]), np.array([["50"]]), np.array([[1j]])]:
    try:
        grade.validate_scores(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid score domain accepted")
for options in [{"curve": np.nan}, {"curve": 101}, {"threshold": 0},
                {"threshold": np.inf}, {"pass_score": -1}]:
    try:
        grade.analyse(scores, **options)
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid policy accepted")

with tempfile.TemporaryDirectory(prefix="studyhub-w27-project-") as name:
    root = Path(name)
    source, target = root / "scores.csv", root / "report.json"
    source.write_text("80,90,100\n60,70,80\n40,50,60\n", encoding="utf-8")
    source_bytes = source.read_bytes()
    def run(*extra):
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            code = grade.main([str(source), str(target), *extra])
        return code, output.getvalue(), errors.getvalue()
    assert run()[0] == 0
    assert source.read_bytes() == source_bytes
    stored = json.loads(target.read_text(encoding="utf-8"))
    assert stored["shape"] == [3, 3] and stored["input_name"] == "scores.csv"
    good = target.read_bytes()
    for text in ["", "10,20\n30\n", "nan,20\n", "inf,20\n", "101,20\n",
                 "-1,20\n", "score,score\n", "10,,20\n", "# comment\n10,20\n"]:
        source.write_text(text, encoding="utf-8")
        code, _, errors = run()
        assert code == 1 and errors.startswith("FAILED:")
        assert target.read_bytes() == good, "Rejected input replaced old report"
    for text, shape in [("75\n", (1, 1)), ("50,60,70\n", (1, 3)), ("50\n60\n70\n", (3, 1))]:
        source.write_text(text, encoding="utf-8")
        assert grade.load_scores(source).shape == shape
    source.write_bytes(source_bytes)
    assert run("--curve", "nan")[0] == 1
    assert target.read_bytes() == good
    # Unrelated temporary files must not be overwritten or removed.
    temporary = target.with_name(target.name + ".tmp")
    temporary.write_text("other owner", encoding="utf-8")
    assert run()[0] == 1
    assert temporary.read_text() == "other owner"
    assert target.read_bytes() == good
    temporary.unlink()
    with contextlib.redirect_stderr(io.StringIO()):
        assert grade.main([str(source), str(source)]) == 1
    assert source.read_bytes() == source_bytes
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            grade.main(["--help"])
        except SystemExit as error:
            assert error.code == 0

print("PASS: exact means/axes/spread/curve/normalization; zero-spread and outlier rules; no Python project loops; invalid numeric domains/policies/CSV rejected; one row/column retained; input and prior report/unrelated temp preserved; CLI help.")
