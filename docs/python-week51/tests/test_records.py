import doctest
import json
from itertools import product

import pytest

from bench import benchmark, memory_peak, profile_summary, slow_unique
from studyhub_records import core, running_totals, totals_by_category, unique_in_order
from studyhub_records.cli import main, write_report


def test_stable_unique_and_generator():
    values = ["b", "a", "b", "A", "", "a"]
    saved = values.copy()
    assert unique_in_order(iter(values)) == ["b", "a", "A", ""]
    assert values == saved
    assert unique_in_order([]) == []


def test_exhaustive_reference_equivalence():
    for length in range(6):
        for values in product(["a", "b", ""], repeat=length):
            assert unique_in_order(iter(values)) == slow_unique(values)


@pytest.mark.parametrize("values", [["a", 1], [None], [False]])
def test_labels_reject_wrong_types(values):
    with pytest.raises(TypeError):
        unique_in_order(values)


def test_totals_order_ownership_and_generator():
    rows = [("Python", 20), ("SQL", 10), ("Python", 0), ("Python", 5)]
    original = rows.copy()
    assert totals_by_category(iter(rows)) == {"Python": 25, "SQL": 10}
    assert list(totals_by_category(rows)) == ["Python", "SQL"]
    assert rows == original
    assert totals_by_category([]) == {}


@pytest.mark.parametrize(
    "rows,error",
    [
        ([("", 1)], ValueError),
        ([("  ", 1)], ValueError),
        ([("a", -1)], ValueError),
        ([("a", True)], TypeError),
        ([("a", 1.5)], TypeError),
        ([(1, 1)], TypeError),
        ([["a", 1]], TypeError),
        ([("a",)], TypeError),
    ],
)
def test_bad_records(rows, error):
    with pytest.raises(error):
        totals_by_category(rows)


def test_running_totals_reference():
    for length in range(5):
        for values in product([0, 1, 3], repeat=length):
            assert running_totals(iter(values)) == [sum(values[: i + 1]) for i in range(length)]
    assert running_totals([10**40, 1]) == [10**40, 10**40 + 1]


@pytest.mark.parametrize(
    "values,error", [([True], TypeError), ([1.0], TypeError), ([-1], ValueError)]
)
def test_bad_prefix_input(values, error):
    with pytest.raises(error):
        running_totals(values)


def test_doctests():
    assert doctest.testmod(core).failed == 0


def test_cli_success_and_replace(tmp_path, capsys):
    source, output = tmp_path / "input.csv", tmp_path / "result.json"
    source.write_text("category,minutes\nPython,20\nSQL,5\nPython,10\n", encoding="utf-8")
    output.write_text("old", encoding="utf-8")
    assert main([str(source), "--output", str(output)]) == 0
    assert json.loads(output.read_text(encoding="utf-8")) == {
        "rows": 3,
        "totals": {"Python": 30, "SQL": 5},
    }
    assert "Processed 3" in capsys.readouterr().out
    assert not list(tmp_path.glob(".studyhub51-*.tmp"))


@pytest.mark.parametrize(
    "text",
    [
        "category,minutes\na,-1\n",
        "category,minutes\na,1.5\n",
        "category,minutes\na,\n",
        "category,minutes\na,1,extra\n",
        "minutes,category\n1,a\n",
        "category,minutes\n ,1\n",
    ],
)
def test_cli_invalid_preserves_previous_output(tmp_path, text):
    source, output = tmp_path / "input.csv", tmp_path / "result.json"
    source.write_text(text, encoding="utf-8")
    output.write_bytes(b"previous report\n")
    assert main([str(source), "--output", str(output)]) == 2
    assert output.read_bytes() == b"previous report\n"


def test_input_not_overwritten(tmp_path):
    source = tmp_path / "input.csv"
    source.write_bytes(b"category,minutes\na,1\n")
    assert main([str(source), "--output", str(source)]) == 2
    assert source.read_bytes() == b"category,minutes\na,1\n"


def test_replace_failure_cleans_temp_and_preserves_existing(tmp_path, monkeypatch):
    from studyhub_records import cli

    output = tmp_path / "result.json"
    output.write_bytes(b"old")

    def fail(*args):
        raise PermissionError("simulated replacement failure")

    monkeypatch.setattr(cli.os, "replace", fail)
    with pytest.raises(PermissionError):
        write_report(output, {"rows": 1})
    assert output.read_bytes() == b"old"
    assert not list(tmp_path.glob(".studyhub51-*.tmp"))


def test_benchmark_contract_not_a_speed_threshold():
    report = benchmark(size=40, repeats=3)
    assert report["equal_results"]
    assert report["input_items"] == 80
    assert all(len(x) == 3 and all(t > 0 for t in x) for x in report["seconds"].values())
    assert report["observed_ratio"] > 0
    assert profile_summary(["a", "a"])[0]["calls"] == 1
    assert memory_peak(unique_in_order, ["a", "b", "a"])["result_items"] == 2
