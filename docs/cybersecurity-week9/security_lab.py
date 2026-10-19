"""Read-only analysis of this course's small, synthetic JSON evidence fixture.

No network access, device discovery, account access or remediation actions.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

SAMPLE = Path(__file__).with_name("sample-events.json")
MAX_BYTES = 100_000
MAX_RECORDS = 1_000


def _unique_keys(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError("Duplicate JSON key: " + name)
        result[name] = value
    return result


def _finite_json(value):
    raise ValueError("Non-finite JSON number: " + value)


def load_fixture(path=SAMPLE):
    """Read at most MAX_BYTES+1; reject an oversized or malformed document."""
    with Path(path).open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("Fixture exceeds byte limit")
    document = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_keys,
                          parse_constant=_finite_json)
    if not isinstance(document, dict) or not isinstance(document.get("events"), list):
        raise ValueError("Expected an object with an events list")
    if len(document["events"]) > MAX_RECORDS:
        raise ValueError("Fixture exceeds record limit")
    if not isinstance(document.get("context"), dict):
        raise ValueError("Expected context metadata")
    limits = document["context"].get("limitations", [])
    if not isinstance(limits, list) or any(not isinstance(item, str) for item in limits):
        raise ValueError("Context limitations must be a list of strings")
    return document


def validate_rows(rows):
    """Return accepted copies and referenced errors; never change the input."""
    accepted, rejected, labels = [], [], set()
    required = ("record", "source", "event_id", "event_time", "received_time", "action")
    for number, row in enumerate(rows, 1):
        reason = None
        if not isinstance(row, dict):
            reason = "expected an object"
        elif any(not isinstance(row.get(k), str) or not row[k].strip() for k in required):
            reason = "required fields must be nonblank strings"
        elif any(len(row[k]) > 200 or any(ord(c) < 32 for c in row[k]) for k in required):
            reason = "required field length/control-character limit"
        elif row["record"] in labels:
            reason = "duplicate delivery label"
        elif "status" in row and (type(row["status"]) is not int or not 100 <= row["status"] <= 599):
            reason = "status must be an integer from 100 to 599"
        elif "write_performed" in row and type(row["write_performed"]) is not bool:
            reason = "write_performed must be a boolean"
        elif "account" in row and (not isinstance(row["account"], str) or not row["account"].strip()
                                   or len(row["account"]) > 200
                                   or any(ord(c) < 32 for c in row["account"])):
            reason = "account must be a bounded nonblank text label"
        if reason:
            rejected.append({"row": number, "reason": reason})
        else:
            labels.add(row["record"])
            accepted.append(dict(row))
    return accepted, rejected


def deduplicate(rows):
    """Group by documented source/event_id; quarantine conflicting groups.

    Only record, received_time and annotation are delivery metadata in THIS
    fixture contract. All other fields participate in payload equality.
    """
    groups = {}
    delivery = {"record", "received_time", "annotation"}
    for row in rows:
        groups.setdefault((row["source"], row["event_id"]), []).append(row)
    unique, duplicates, conflicts = [], [], []
    for key, copies in groups.items():
        payloads = [{k: v for k, v in row.items() if k not in delivery} for row in copies]
        if any(payload != payloads[0] for payload in payloads[1:]):
            conflicts.append({"source": key[0], "event_id": key[1],
                              "records": [row["record"] for row in copies]})
            continue
        unique.append(copies[0])
        duplicates.extend({"record": row["record"], "kept": copies[0]["record"]}
                          for row in copies[1:])
    return unique, duplicates, conflicts


def utc_time(value):
    """An offset-free/invalid time stays unknown; never guess a local zone."""
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            return None
        return parsed.astimezone(timezone.utc)
    except (ValueError, TypeError, OverflowError):
        return None


def timeline(rows):
    known, unknown = [], []
    for row in rows:
        instant = utc_time(row["event_time"])
        if instant is None:
            unknown.append(row)
        else:
            known.append((instant, row))
    known.sort(key=lambda pair: (pair[0], pair[1]["source"], pair[1]["event_id"]))
    return [row for _, row in known], unknown


def login_window(rows, start, end):
    """Require validated, unique rows and explicit aware half-open bounds."""
    begin, stop = utc_time(start), utc_time(end)
    if begin is None or stop is None or begin >= stop:
        raise ValueError("Window needs increasing offset-bearing times")
    selected, unknown = [], []
    for row in rows:
        if row["source"] != "auth" or row["action"] != "login.failed":
            continue
        instant = utc_time(row["event_time"])
        if instant is None:
            unknown.append(row["record"])
        elif begin <= instant < stop:
            selected.append(row)
    return selected, unknown


def digest(path=SAMPLE):
    """SHA-256 over original file bytes, streamed in fixed chunks."""
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(65_536), b""):
            value.update(chunk)
    return value.hexdigest()


def analyse(document):
    accepted, rejected = validate_rows(document["events"])
    unique, duplicates, conflicts = deduplicate(accepted)
    ordered, unknown = timeline(unique)
    failures, unknown_failures = login_window(unique, "2026-10-01T00:00:00Z",
                                             "2026-10-01T00:03:00Z")
    by_account = Counter(row.get("account", "<missing>") for row in failures)
    # Missing/malformed account labels must be resolved before account grouping
    # outside this known fixture; this helper does not authenticate identities.
    return {
        "scope": "Prepared Week7 fixture; no real account observations",
        "deliveries": len(document["events"]), "accepted_deliveries": len(accepted),
        "rejected": rejected, "unique_events": len(unique),
        "duplicates": duplicates, "conflicts": conflicts,
        "ordered_event_ids": [row["event_id"] for row in ordered],
        "unknown_time_records": [row["record"] for row in unknown],
        "failure_window": "[2026-10-01T00:00:00Z, 2026-10-01T00:03:00Z)",
        "failure_count": len(failures),
        "failure_records": [row["record"] for row in failures],
        "unknown_failure_times": unknown_failures,
        "review_accounts": sorted(name for name, count in by_account.items() if count >= 3),
        "conclusion": "Threshold requests review; account compromise is not established",
        "limitations": document["context"].get("limitations", []),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=SAMPLE)
    args = parser.parse_args()
    try:
        report = analyse(load_fixture(args.input))
    except (OSError, UnicodeError, ValueError, TypeError) as error:
        parser.exit(2, "Cannot analyse fixture: " + str(error) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=True, allow_nan=False))


if __name__ == "__main__":
    main()
