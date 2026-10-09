"""Week 22 teaching project. Python 3.10+. No external dependencies.
Run normally (not python -O) to execute the assertion checks.
Format: naive timestamps, IPv4, status 100..599, one record per line.
This teaching implementation retains valid/rejected rows in memory.
"""
import re
from collections import Counter
from datetime import datetime
from ipaddress import ip_address

LOG_PATTERN = re.compile(
    r"(?P<time>[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}) "
    r"(?P<level>INFO|WARN|ERROR) "
    r"ip=(?P<ip>[0-9.]+) "
    r"status=(?P<status>[0-9]{3}) "
    r"type=(?P<type>[A-Za-z_]+) "
    r"message=(?P<message>.*)"
)

def parse_line(line):
    if len(line) > 4096:
        raise ValueError("line too long")
    found = LOG_PATTERN.fullmatch(line)
    if found is None:
        raise ValueError("bad log format")
    row = found.groupdict()
    stamp = datetime.fromisoformat(row["time"])
    address = ip_address(row["ip"])
    if address.version != 4:
        raise ValueError("IPv4 required")
    status = int(row["status"])
    if not 100 <= status <= 599:
        raise ValueError("invalid status")
    row["ip"] = str(address)
    row["status"] = status
    row["hour"] = stamp.strftime("%Y-%m-%dT%H")
    return row

def analyse(lines):
    rows, rejected = [], []
    for number, line in enumerate(lines, 1):
        try:
            rows.append(parse_line(line.rstrip("\r\n")))
        except ValueError as error:
            rejected.append((number, str(error)))
    errors = Counter(row["type"] for row in rows if row["level"] == "ERROR")
    hours = Counter(row["hour"] for row in rows)
    offending = Counter(row["ip"] for row in rows if row["status"] >= 400)
    top_ips = sorted(offending.items(), key=lambda item: (-item[1], item[0]))
    return rows, rejected, errors, hours, top_ips

sample = [
    "2026-10-10T09:00:00 INFO ip=192.0.2.1 status=200 type=ok message=ready",
    "2026-10-10T09:10:00 ERROR ip=192.0.2.2 status=500 type=disk message=disk full",
    "2026-10-10T10:00:00 WARN ip=192.0.2.1 status=404 type=missing message=not found",
    "2026-10-10T10:05:00 ERROR ip=192.0.2.2 status=503 type=disk message=retry later",
    "2026-02-31T10:00:00 INFO ip=192.0.2.3 status=200 type=ok message=bad date",
    "malformed line",
]

if __name__ == "__main__":
    rows, rejected, errors, hours, top_ips = analyse(sample)
    print("valid:", len(rows), "rejected:", len(rejected))
    print("errors by type:", sorted(errors.items()))
    print("requests by hour:", sorted(hours.items()))
    print("IPs with status >= 400:", top_ips)
    print("rejected line numbers:", [number for number, reason in rejected])
    good = "2026-10-10T09:00:00 INFO ip=192.0.2.1 status=200 type=ok message=ready"
    bad_values = [
        good.replace("192.0.2.1", "999.0.0.1"),
        good.replace("status=200", "status=999"),
        good.replace("2026-10-10", "2026-02-31"),
        "malformed line",
        "x" * 4097,
    ]
    for value in bad_values:
        try:
            parse_line(value)
        except ValueError:
            continue
        raise AssertionError("bad input was accepted")
    assert parse_line(good)["status"] == 200
    print("five rejection checks and one valid record passed")
    rows, rejected, errors, hours, top_ips = analyse(sample)
    assert len(rows) == 4 and len(rejected) == 2
    assert errors == {"disk": 2}
    assert hours == {"2026-10-10T09": 2, "2026-10-10T10": 2}
    assert top_ips == [("192.0.2.2", 2), ("192.0.2.1", 1)]
    assert [number for number, reason in rejected] == [5, 6]
    print("all report expectations passed")
