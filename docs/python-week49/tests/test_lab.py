import csv
import inspect
import io
import json

import pytest

from lab import file_digest, make_demo, write_report
from memory_lab import compare_layouts
from streamkit import (
    CountIterator,
    CountRange,
    Event,
    NonNegativeInt,
    as_rows,
    atomic_text,
    count_calls,
    iter_events,
    open_events,
    parse_row,
    select_categories,
    write_selected,
)


def test_iterator_identity_sticky_exhaustion_and_independent_iterables():
    it = CountIterator(2)
    assert iter(it) is it
    assert next(it) == 0 and next(it) == 1
    for _ in range(2):
        with pytest.raises(StopIteration):
            next(it)
    values = CountRange(3)
    first, second = iter(values), iter(values)
    assert first is not second
    assert next(first) == next(second) == 0
    assert list(values) == list(values) == [0, 1, 2]


@pytest.mark.parametrize("stop", [-1, True, 2.5])
def test_counter_contract_rejects_invalid_stops(stop):
    with pytest.raises(ValueError):
        CountRange(stop)


def test_pipeline_is_lazy_and_prefix_does_not_parse_later_rows():
    text = io.StringIO("event_id,category,minutes\na,study,10\nb,review,bad\n")
    before = parse_row.stats["calls"]
    records = iter_events(text)
    assert parse_row.stats["calls"] == before
    assert next(records).minutes == 10
    assert parse_row.stats["calls"] == before + 1
    with pytest.raises(ValueError, match="ASCII"):
        next(records)


def test_filter_preserves_order_and_validates_even_discarded_rows():
    records = iter_events(
        io.StringIO("event_id,category,minutes\na,break,5\nb,study,10\nc,review,7\n")
    )
    assert [
        row["event_id"] for row in as_rows(select_categories(records, {"study", "review"}))
    ] == ["b", "c"]
    invalid = iter_events(io.StringIO("event_id,category,minutes\na,break,broken\n"))
    with pytest.raises(ValueError):
        list(select_categories(invalid, {"study"}))


@pytest.mark.parametrize(
    "body",
    [
        "minutes,category,event_id\n1,study,a\n",
        "event_id,category,minutes\na,study,1,extra\n",
        "event_id,category,minutes\na,study\n",
        "event_id,category,minutes\na,unknown,2\n",
    ],
)
def test_header_row_width_and_domain_errors_are_strict(body):
    with pytest.raises(ValueError):
        list(iter_events(io.StringIO(body)))


def test_context_closes_input_on_early_exit_and_error(tmp_path):
    path = tmp_path / "source.csv"
    make_demo(path, 3)
    with open_events(path) as records:
        assert next(records).event_id == "demo-0"
    with pytest.raises(ValueError, match="closed"):
        next(records)
    # Rename after release also checks that no input handle was left open on Windows.
    path.rename(tmp_path / "renamed.csv")


def test_atomic_writer_preserves_previous_output_on_failure_and_cleans_up(tmp_path):
    path = tmp_path / "result.txt"
    path.write_text("previous", encoding="utf-8")
    with pytest.raises(RuntimeError, match="failed"), atomic_text(path) as handle:
        handle.write("partial")
        raise RuntimeError("failed")
    assert handle.closed
    assert path.read_text(encoding="utf-8") == "previous"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["result.txt"]
    with atomic_text(path) as handle:
        handle.write("complete")
    assert handle.closed and path.read_text(encoding="utf-8") == "complete"


def test_strict_stream_failure_keeps_existing_csv(tmp_path):
    source, target = tmp_path / "source.csv", tmp_path / "selected.csv"
    source.write_text("event_id,category,minutes\na,study,10\nb,break,no\n", encoding="utf-8")
    target.write_text("previous", encoding="utf-8")
    with pytest.raises(ValueError):
        write_selected(source, target)
    assert target.read_text(encoding="utf-8") == "previous"
    assert not list(tmp_path.glob(".*.tmp"))
    with pytest.raises(ValueError, match="different"):
        write_selected(source, source)


def test_descriptor_validates_later_assignments_and_is_per_instance():
    a, b = Event("a", "study", 10), Event("b", "review", 20)
    a.minutes = 30
    assert (a.minutes, b.minutes) == (30, 20)
    assert isinstance(Event.minutes, NonNegativeInt)
    for value in [-1, True, 1.5, "5"]:
        with pytest.raises(ValueError):
            a.minutes = value
    assert a.minutes == 30 and not hasattr(a, "__dict__")
    with pytest.raises(AttributeError):
        a.extra = "not a declared slot"


def test_parameterized_decorator_preserves_metadata_result_and_exception():
    @count_calls(label="divide")
    def divide(numerator, denominator=1):
        """Divide two inputs."""
        return numerator / denominator

    assert divide(6, denominator=2) == 3
    with pytest.raises(ZeroDivisionError):
        divide(1, 0)
    assert divide.stats == {"label": "divide", "calls": 2, "failures": 1}
    assert divide.__name__ == "divide" and divide.__doc__ == "Divide two inputs."
    assert str(inspect.signature(divide)) == "(numerator, denominator=1)"
    assert divide.__wrapped__(4, 2) == 2


def test_generator_decoration_counts_creation_not_consumption():
    @count_calls(label="generator creation")
    def failing_later():
        yield 1
        raise ValueError("during iteration")

    records = failing_later()
    assert failing_later.stats["calls"] == 1
    assert next(records) == 1
    with pytest.raises(ValueError, match="iteration"):
        next(records)
    assert failing_later.stats["failures"] == 0


def test_memory_experiment_compares_equal_live_batches_in_fresh_processes():
    report = compare_layouts(2000)
    plain, slots = report["measurements"]
    assert plain["count"] == slots["count"] == 2000
    assert plain["peak_bytes"] >= plain["current_bytes"] > 0
    assert slots["peak_bytes"] >= slots["current_bytes"] > 0
    if report["implementation"] == "CPython":
        assert plain["current_bytes"] > slots["current_bytes"]


def test_full_artifacts_reconstruct_counts_totals_and_digest(tmp_path):
    report = write_report(tmp_path, count=101, memory_count=1000)
    with (tmp_path / "selected.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert report["parsed"] == 101
    assert report["written"] == len(rows) == 68
    for category in ["study", "review"]:
        assert report["minutes"][category] == sum(
            int(row["minutes"]) for row in rows if row["category"] == category
        )
    saved = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    assert saved["selected_csv_sha256"] == file_digest(tmp_path / "selected.csv")


def test_report_never_replaces_its_source_artifact(tmp_path):
    source = tmp_path / "report.json"
    make_demo(source, 2)
    before = source.read_bytes()
    with pytest.raises(ValueError, match="source"):
        write_report(tmp_path, source=source, memory_count=10)
    assert source.read_bytes() == before
