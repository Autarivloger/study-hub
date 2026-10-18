"""Small, bounded-state CSV pipeline for the Week 49 language project."""

import csv
import os
import tempfile
from collections import Counter
from contextlib import contextmanager
from functools import wraps
from pathlib import Path

CATEGORIES = frozenset({"study", "review", "break"})
FIELDS = ["event_id", "category", "minutes"]


class CountIterator:
    def __init__(self, stop):
        if type(stop) is not int or stop < 0:
            raise ValueError("stop must be a nonnegative integer")
        self.stop, self.position = stop, 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.position >= self.stop:
            raise StopIteration
        value = self.position
        self.position += 1
        return value


class CountRange:
    def __init__(self, stop):
        if type(stop) is not int or stop < 0:
            raise ValueError("stop must be a nonnegative integer")
        self.stop = stop

    def __iter__(self):
        return CountIterator(self.stop)


def count_calls(*, label):
    """Count ordinary function invocations; this is not an iteration or thread monitor."""

    def decorate(function):
        stats = {"label": label, "calls": 0, "failures": 0}

        @wraps(function)
        def wrapped(*args, **kwargs):
            stats["calls"] += 1
            try:
                return function(*args, **kwargs)
            except Exception:
                stats["failures"] += 1
                raise

        wrapped.stats = stats
        return wrapped

    return decorate


class NonNegativeInt:
    def __set_name__(self, owner, name):
        self.name, self.storage = name, "_" + name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return getattr(instance, self.storage)

    def __set__(self, instance, value):
        if type(value) is not int or value < 0:
            raise ValueError(f"{self.name} must be a nonnegative integer")
        setattr(instance, self.storage, value)


class Event:
    __slots__ = ("_category", "_event_id", "_minutes")
    minutes = NonNegativeInt()

    def __init__(self, event_id, category, minutes):
        if not isinstance(event_id, str) or not event_id or len(event_id) > 64:
            raise ValueError("event_id must contain 1–64 characters")
        if category not in CATEGORIES:
            raise ValueError("category must be study, review or break")
        self._event_id, self._category = event_id, category
        self.minutes = minutes

    @property
    def event_id(self):
        return self._event_id

    @property
    def category(self):
        return self._category

    def as_row(self):
        return {"event_id": self.event_id, "category": self.category, "minutes": self.minutes}


@count_calls(label="parse_row")
def parse_row(row):
    """Validate one event; ASCII decimal minutes avoid accepting float or signed text."""
    if set(row) != set(FIELDS) or any(not isinstance(row[name], str) for name in FIELDS):
        raise ValueError("each row must have exactly the three required text fields")
    text = row["minutes"].strip()
    if not text or not text.isascii() or not text.isdecimal() or len(text) > 9:
        raise ValueError("minutes must be 1–9 ASCII decimal digits")
    return Event(row["event_id"].strip(), row["category"].strip(), int(text))


def iter_events(handle):
    """Single-use generator. Parsing happens on consumption, inside the owner's with."""
    reader = csv.DictReader(handle, strict=True)
    if reader.fieldnames != FIELDS:
        raise ValueError("CSV header must be event_id,category,minutes in that order")
    for row in reader:
        yield parse_row(row)


def select_categories(events, allowed):
    allowed = frozenset(allowed)
    if not allowed or not allowed <= CATEGORIES:
        raise ValueError("choose at least one known category")
    for event in events:
        if event.category in allowed:
            yield event


def as_rows(events):
    for event in events:
        yield event.as_row()


@contextmanager
def open_events(path):
    """Own the input file; consumers must finish while this context is active."""
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        yield iter_events(handle)


@contextmanager
def atomic_text(path):
    """Replace one output only after a successful flush/close; not a multi-file transaction."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=path.parent,
            prefix="." + path.name + ".",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            yield handle
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def write_selected(source, destination, allowed=("study", "review")):
    """Parse/validate -> filter -> project -> write. Strict errors preserve prior output."""
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve():
        raise ValueError("input and output must be different paths")
    counts, minutes = Counter(), Counter()
    before = parse_row.stats["calls"]
    with open_events(source) as events, atomic_text(destination) as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        selected = select_categories(events, allowed)
        for row in as_rows(selected):
            writer.writerow(row)
            counts[row["category"]] += 1
            minutes[row["category"]] += row["minutes"]
    return {
        "parsed": parse_row.stats["calls"] - before,
        "written": sum(counts.values()),
        "counts": dict(sorted(counts.items())),
        "minutes": dict(sorted(minutes.items())),
    }
