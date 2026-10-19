import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from security_lab import (MAX_BYTES, SAMPLE, analyse, deduplicate, digest,
                          load_fixture, login_window, timeline, utc_time,
                          validate_rows)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.document = load_fixture()
        self.rows = self.document["events"]

    def test_known_fixture_and_immutability(self):
        before = copy.deepcopy(self.document)
        result = analyse(self.document)
        self.assertEqual((result["deliveries"], result["unique_events"], result["failure_count"]), (12, 11, 4))
        self.assertEqual(result["duplicates"], [{"record": "L04", "kept": "L03"}])
        self.assertEqual(result["unknown_time_records"], ["L11"])
        self.assertEqual(result["review_accounts"], ["maya"])
        self.assertEqual(result["ordered_event_ids"], ["A01", "A02", "A04", "A03", "A10", "N01", "P01", "P02", "E01", "Z01"])
        self.assertEqual(self.document, before)

    def test_bad_rows_are_retained_as_errors(self):
        for update in ({"status": True}, {"status": "403"}, {"status": 99},
                       {"write_performed": "false"}, {"account": []},
                       {"source": ""}, {"event_id": "x\n"}, {"action": "x" * 201}):
            with self.subTest(update=update):
                row = {**self.rows[0], **update}
                good, bad = validate_rows([row])
                self.assertFalse(good)
                self.assertEqual(bad[0]["row"], 1)
        good, bad = validate_rows([None, self.rows[0], self.rows[0]])
        self.assertEqual((len(good), len(bad)), (1, 2))

    def test_conflict_group_is_not_arbitrarily_counted(self):
        row = {**self.rows[0], "record": "NEW", "result": "accepted"}
        unique, duplicates, conflicts = deduplicate([self.rows[0], row])
        self.assertEqual((unique, duplicates), ([], []))
        self.assertEqual(conflicts[0]["records"], ["L01", "NEW"])

    def test_event_identity_includes_source(self):
        other = {**self.rows[0], "record": "NEW", "source": "other"}
        self.assertEqual(len(deduplicate([self.rows[0], other])[0]), 2)

    def test_time_offsets_unknowns_and_half_open_window(self):
        self.assertEqual(utc_time("2026-10-01T09:00:00+09:00"), utc_time("2026-10-01T00:00:00Z"))
        for value in ("2026-10-01 09:01:30", "not a date", None, "2026-02-30T00:00:00Z"):
            self.assertIsNone(utc_time(value))
        start = "2026-10-01T00:00:00Z"
        end = "2026-10-01T00:03:00Z"
        rows = [{**self.rows[0], "event_time": value, "record": str(i)}
                for i, value in enumerate([start, end, "unknown"])]
        selected, unknown = login_window(rows, start, end)
        self.assertEqual([r["record"] for r in selected], ["0"])
        self.assertEqual(unknown, ["2"])
        for bounds in ((end, start), (start, start), ("2026-10-01", end)):
            with self.assertRaises(ValueError):
                login_window(rows, *bounds)

    def test_alert_and_delivery_are_not_additional_failures(self):
        rows = deduplicate(validate_rows(self.rows)[0])[0]
        selected, unknown = login_window(rows, "2026-10-01T00:00:00Z", "2026-10-01T00:03:00Z")
        self.assertEqual({r["event_id"] for r in selected}, {"A01", "A02", "A03", "A04"})
        self.assertFalse(unknown)
        early = [r for r in rows if utc_time(r["received_time"]) <= utc_time("2026-10-01T00:07:00Z")]
        self.assertEqual(len(login_window(early, "2026-10-01T00:00:00Z", "2026-10-01T00:03:00Z")[0]), 3)

    def test_loader_errors_and_unchanged_source(self):
        original = SAMPLE.read_bytes()
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "fixture.json"
            for text in ('[]', '{}', '{"events":[],"events":[],"context":{}}',
                         '{"events":[],"context":{},"x":NaN}',
                         '{"events":[],"context":{"limitations":"bad"}}',
                         json.dumps({"events": [{}] * 1001, "context": {}})):
                p.write_text(text, encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_fixture(p)
            p.write_bytes(b"x" * (MAX_BYTES + 1))
            with self.assertRaises(ValueError):
                load_fixture(p)
            p.write_bytes(b"\xff")
            with self.assertRaises(UnicodeError):
                load_fixture(p)
        self.assertEqual(SAMPLE.read_bytes(), original)

    def test_digest_and_repeatable_report(self):
        self.assertEqual(digest(), hashlib.sha256(SAMPLE.read_bytes()).hexdigest())
        self.assertEqual(analyse(self.document), analyse(self.document))
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "copy.json"
            p.write_bytes(SAMPLE.read_bytes() + b"\n")
            self.assertNotEqual(digest(p), digest())
            self.assertEqual(analyse(load_fixture(p)), analyse(self.document))


if __name__ == "__main__":
    unittest.main()
