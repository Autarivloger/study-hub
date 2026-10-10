"""Week 23 practice CLI. Python 3.11+, standard library only.
Small local student tables; explicit version-2 schema and UTF-8 policy.
Use a new destination filename. Not concurrent-write coordination.
"""
import argparse
import csv
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import xml.etree.ElementTree as ET

FIELDS = ["id", "name", "score"]
MAX_BYTES = 1_000_000

def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result

def reject_constant(value):
    raise ValueError("non-finite JSON constant")

def valid_xml_text(text):
    return all(ch in "\t\n\r" or 0x20 <= ord(ch) <= 0xD7FF
               or 0xE000 <= ord(ch) <= 0xFFFD
               or 0x10000 <= ord(ch) <= 0x10FFFF for ch in text)

def validate_rows(rows):
    if not isinstance(rows, list) or len(rows) > 10000:
        raise ValueError("array of at most 10000 students required")
    result, seen = [], set()
    for number, row in enumerate(rows, 1):
        if not isinstance(row, dict) or set(row) != set(FIELDS):
            raise ValueError(f"record {number}: fields must be id/name/score")
        identifier, name, score = row["id"], row["name"], row["score"]
        if not isinstance(identifier, str) or re.fullmatch(r"[A-Za-z0-9_-]{1,32}", identifier) is None:
            raise ValueError(f"record {number}: invalid text id")
        if identifier in seen:
            raise ValueError(f"record {number}: duplicate id")
        if not isinstance(name, str) or not name.strip() or len(name) > 200 or not valid_xml_text(name):
            raise ValueError(f"record {number}: invalid name")
        if type(score) is not int or not 0 <= score <= 100:
            raise ValueError(f"record {number}: score must be integer 0..100")
        seen.add(identifier)
        result.append({"id": identifier, "name": name.strip(), "score": score})
    return result

def parse_score(value, number):
    if not isinstance(value, str) or re.fullmatch(r"[0-9]{1,3}", value.strip()) is None:
        raise ValueError(f"record {number}: score needs ASCII integer text")
    return int(value.strip())

def read_rows(path, kind):
    path = Path(path)
    with path.open("rb") as handle:
        raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("input exceeds 1 MB policy")
    text = raw.decode("utf-8-sig")
    if kind == "csv":
        reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
        if reader.fieldnames != FIELDS:
            raise ValueError("CSV header must be id,name,score")
        rows = []
        for number, row in enumerate(reader, 1):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"record {number}: incomplete or extra columns")
            rows.append({"id": row["id"], "name": row["name"],
                         "score": parse_score(row["score"], number)})
    elif kind == "json":
        document = json.loads(text, object_pairs_hook=unique_object,
                              parse_constant=reject_constant)
        if not isinstance(document, dict) or set(document) != {"version", "students"}:
            raise ValueError("JSON envelope fields")
        if type(document["version"]) is not int or document["version"] != 2:
            raise ValueError("JSON version 2 required")
        rows = document["students"]
    elif kind == "xml":
        if "<!DOCTYPE" in text or "<!ENTITY" in text:
            raise ValueError("DTD/entity declarations not supported")
        root = ET.fromstring(text)
        if root.tag != "students" or root.attrib != {"version": "2"} or (root.text or "").strip():
            raise ValueError("XML students version 2 required")
        rows = []
        for number, element in enumerate(root, 1):
            if element.tag != "student" or set(element.attrib) != {"id"}:
                raise ValueError(f"record {number}: XML student/id required")
            children = list(element)
            if len(children) != 2 or {child.tag for child in children} != {"name", "score"}:
                raise ValueError(f"record {number}: XML name/score children required")
            if (element.text or "").strip() or (element.tail or "").strip():
                raise ValueError(f"record {number}: mixed XML text")
            if any(child.attrib or len(child) or (child.tail or "").strip() for child in children):
                raise ValueError(f"record {number}: unsupported XML child content")
            rows.append({"id": element.get("id"), "name": element.findtext("name"),
                         "score": parse_score(element.findtext("score"), number)})
    else:
        raise ValueError("unsupported format")
    return validate_rows(rows)

def render_rows(rows, kind):
    rows = validate_rows(rows)
    if kind == "json":
        return json.dumps({"version": 2, "students": rows}, ensure_ascii=False,
                          allow_nan=False, indent=2) + "\n"
    if kind == "csv":
        buffer = io.StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        return buffer.getvalue()
    if kind == "xml":
        root = ET.Element("students", {"version": "2"})
        for row in rows:
            element = ET.SubElement(root, "student", {"id": row["id"]})
            ET.SubElement(element, "name").text = row["name"]
            ET.SubElement(element, "score").text = str(row["score"])
        return ET.tostring(root, encoding="unicode") + "\n"
    raise ValueError("unsupported format")

def convert(source, destination, input_format, output_format):
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve():
        raise ValueError("input and output must differ")
    if destination.exists():
        raise ValueError("output already exists; choose a new filename")
    rows = read_rows(source, input_format)
    text = render_rows(rows, output_format)
    # Unique temporary sibling; replace only after successful writing.
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="",
                dir=destination.parent, prefix=".convert-", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(text)
        # This teaching CLI assumes one writer; it is not concurrent-write coordination.
        temporary.replace(destination)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    return len(rows)

def main(argv=None):
    parser = argparse.ArgumentParser(description="Convert a validated student table")
    parser.add_argument("source")
    parser.add_argument("destination")
    parser.add_argument("--input-format", required=True, choices=["csv", "json", "xml"])
    parser.add_argument("--output-format", required=True, choices=["csv", "json", "xml"])
    args = parser.parse_args(argv)
    try:
        count = convert(args.source, args.destination, args.input_format, args.output_format)
    except (OSError, ValueError, csv.Error, ET.ParseError) as error:
        print("Conversion failed:", error, file=sys.stderr)
        return 1
    print(f"Converted {count} records")
    return 0

if __name__ == "__main__":
    sys.exit(main())
