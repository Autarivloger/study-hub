"""Add Week 23 only; run all examples before the atomic content write."""
import json
import os
from pathlib import Path
import subprocess
import sys
import textwrap
import tempfile

ROOT = Path(__file__).resolve().parent.parent
days = {f"23.{d}": {"parts": []} for d in range(6)}
executed = 0


def clean(code):
    return textwrap.dedent(code).strip() + "\n"


def output(code):
    global executed
    with tempfile.TemporaryDirectory(prefix="studyhub-w23-") as folder:
        run = subprocess.run(
            [sys.executable, "-c", clean(code)], capture_output=True,
            encoding="utf-8", timeout=8, cwd=folder,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
    if run.returncode:
        raise RuntimeError(run.stderr + "\n" + code)
    executed += 1
    return run.stdout.replace("\r\n", "\n").rstrip()


def section(kind, value=None, **extra):
    result = {"t": kind, **extra}
    if value is not None:
        result["v"] = value
    return result


def question(prompt, answer, wrong1, wrong2, why, rotation):
    options = [answer, wrong1, wrong2]
    for _ in range(rotation % 3):
        options.insert(0, options.pop())
    return {"q": prompt, "options": options, "correct": rotation % 3, "why": why}


def add(day, title, goal, concepts, explanation, syntax, code, walkthrough,
        mistake, task, solution, challenge, challenge_code, key, quizzes):
    parts = days[f"23.{day}"]["parts"]
    index = len(parts)
    qs = [question(*q, index + n) for n, q in enumerate(quizzes)]
    sections = [
        section("h", title),
        section("key", "Learning objective: " + goal),
        *[section("new", name, note=note) for name, note in concepts],
        section("p", explanation),
        section("syn", syntax.replace(r"\n", "\n"), note="Read the pattern, then trace the complete example below."),
        section("code", clean(code)),
        section("out", output(code)),
        section("p", walkthrough),
        section("mis", wrong=mistake[0], right=mistake[1], why=mistake[2]),
        section("ex", task, practiceId=f"23.{day}.{index}.build"),
        section("sol", code=clean(solution), out=output(solution),
                why="Build walkthrough: " + key),
        section("ex", "Mini challenge: " + challenge,
                practiceId=f"23.{day}.{index}.challenge"),
        section("sol", code=clean(challenge_code), out=output(challenge_code),
                why="Challenge check: " + key),
        section("try", q=quizzes[0][0], code="# Explain your prediction before revealing.",
                a=quizzes[0][1], why=quizzes[0][4]),
        section("checkpoint", lesson={"id": f"course:23.{day}.{index}", "quiz": qs}),
        section("key", key),
    ]
    parts.append({"title": title, "sections": sections})


add(0, "1. CSV records: delimiters, quoting and text values",
    "Read a table correctly without splitting quoted commas.",
    [
        ("CSV; record; field", "Comma-separated values describe tabular records. A delimiter separates fields; a quoted field can contain that delimiter and even a newline."),
        ("csv.reader; io.StringIO", "csv.reader interprets CSV quoting rules and yields lists of field strings. StringIO presents example text as an in-memory text file."),
        ("newline='' for CSV files", "Open CSV files with newline='' so the csv module handles line endings and embedded newlines correctly, including on Windows."),
    ],
    "Week 22 showed why regex is not a complete CSV parser. This week builds a reliable import/export workflow. "
    "Use Python 3.11+ for the whole week because Day 4 uses built-in tomllib. Most examples use only the standard library; "
    "PyYAML and python-dotenv are optional local practice dependencies on Day 4. Reading this website always works offline. "
    "CSV has no automatic schema: the characters 007 are text until your program deliberately converts them. "
    "A quoted comma belongs inside a field. Doubled quote characters inside a quoted field represent one literal quote.",
    'reader = csv.reader(handle)\nfor row in reader:\n    print(row)\n# real file: open("people.csv", newline="", encoding="utf-8")',
    r'''
    import csv
    import io
    text = 'name,city,id\nSita,"Kathmandu, Nepal",007\nHari,"says ""hello""",008\n'
    for row in csv.reader(io.StringIO(text, newline="")):
        print(row)
    ''',
    "पहिलो record headers हुन्; त्यसपछि data आउँछ। Kathmandu, Nepal मा comma भए पनि quoted भएकाले एउटै field हुन्छ। "
    "007 string भएकाले अगाडिको zero बच्यो। ID लाई integer बनाउने हो कि text राख्ने हो भन्ने निर्णय schema ले गर्छ।",
    ("line.split(',') parses every CSV row",
     "csv.reader interprets quoting and separators",
     "A comma or newline can be part of a quoted field, so splitting physical lines or commas loses the CSV structure."),
    "Read a quoted field containing a newline and prove it is one CSV record with two fields.",
    r'''
    import csv
    import io
    text = 'name,note\nSita,"first line\nsecond line"\n'
    rows = list(csv.reader(io.StringIO(text, newline="")))
    print(len(rows), len(rows[1]))
    print(repr(rows[1][1]))
    ''',
    "Read IDs 007 and 010; show their text values before and after int conversion. Explain why contact IDs should often stay strings.",
    r'''
    import csv
    import io
    rows = list(csv.reader(io.StringIO("007,010\n")))
    print(rows[0])
    print([int(value) for value in rows[0]])
    ''',
    "Use a CSV parser, preserve quoted fields and choose conversions intentionally. CSV field text is not a typed database column. Keep meaningful leading zeros.",
    [
        ("What does csv.reader return for 007 by default?", "The string '007'", "The integer 7", "A float", "Default reader fields are strings; conversion is explicit."),
        ("Can a quoted CSV field contain a newline?", "Yes", "No", "Only with JSON", "CSV records need not correspond one-to-one with physical lines."),
    ])

add(0, "2. DictReader: named columns and row-shape checks",
    "Use header names and reject extra, missing or duplicate fields.",
    [
        ("csv.DictReader", "DictReader uses the first record as field names and returns dictionaries for subsequent records."),
        ("fieldnames; restkey; restval", "fieldnames reveals the header; restkey collects extra values; restval supplies missing values. Neither automatically establishes valid row shape."),
        ("Header validation", "Check required names, duplicates and unexpected columns before reading rows. Duplicate headers can hide one field behind another."),
    ],
    "Named fields avoid remembering that score is column 2. However, DictReader is a parser, not a validator. "
    "By default, extra values appear under the None key and missing values become None. Inspect both before conversion. "
    "Blank fields are empty strings, distinct from a missing column. Validate the header separately; silently overwriting duplicate names loses information.",
    'reader = csv.DictReader(handle)\ncheck reader.fieldnames\nfor row in reader:\n    check shape before converting row["score"]',
    r'''
    import csv
    import io
    reader = csv.DictReader(io.StringIO("name,score\nSita,90\nHari\nMina,80,extra\n"))
    print(reader.fieldnames)
    for row in reader:
        if None in row or any(value is None for value in row.values()):
            print("bad shape", row["name"])
        else:
            print(row["name"], row["score"])
    ''',
    "Header ले name र score keys बनाउँछ। Hari को score missing छ; Mina को extra column छ। "
    "दुवै reject गर्छौँ। नाम आएपछि पनि values strings नै हुन्। Parser ले table पढ्छ, application ले आफ्नो नियम जाँच्छ।",
    ("Trust every DictReader row merely because it is a dict",
     "Validate headers, extra fields, missing values and domain rules",
     "A parsed dictionary can still have lost duplicate-header data or incomplete fields."),
    "Validate headers exactly ['name','score']; reject name,name and name,score,extra before processing rows.",
    r'''
    import csv
    import io
    for text in ("name,score\n", "name,name\n", "name,score,extra\n"):
        reader = csv.DictReader(io.StringIO(text))
        print(reader.fieldnames, reader.fieldnames == ["name", "score"])
    ''',
    "Contrast a blank score with a missing score; print repr for each and retain the distinction.",
    r'''
    import csv
    import io
    for row in csv.DictReader(io.StringIO("name,score\nSita,\nHari\n")):
        print(row["name"], repr(row["score"]))
    ''',
    "A dictionary result is not evidence of valid input. Check the header before rows, retain missing-versus-blank distinctions, and never ignore surplus columns silently.",
    [
        ("What does a missing CSV column become by default in DictReader?", "None", "Always an empty string", "Zero", "Missing values use restval, which defaults to None."),
        ("Why check duplicate headers first?", "One key can overwrite another column's value.", "They always raise automatically.", "They improve sorting.", "Dictionary keys cannot preserve two separate columns with the same name."),
    ])

add(0, "3. Clean and validate rows; calculate a column average",
    "Convert scores safely and retain a useful rejection report.",
    [
        ("Validation pipeline", "Parse structure, normalise chosen fields, convert types, then enforce domain constraints. Each stage answers a different question."),
        ("Record number vs physical line number", "enumerate on parsed rows counts CSV records. reader.line_num counts physical lines consumed; quoted multiline fields make these different."),
    ],
    "For this score table, names must be nonempty and scores must be integer text in 0..100. Strip name/score edges, "
    "but do not lowercase personal names or remove internal spaces without a policy. Catch only ValueError from conversion/domain checks. "
    "Retain rejected record numbers and reasons. An empty accepted list has no average; do not divide by zero or invent a score.",
    'clean name → convert score with int → check 0 <= score <= 100\naverage = total / count only when count > 0',
    r'''
    import csv
    import io
    accepted, rejected = [], []
    text = "name,score\n Sita ,90\nHari,80\nMina,oops\nRam,101\n"
    for number, row in enumerate(csv.DictReader(io.StringIO(text)), 1):
        try:
            if None in row or any(value is None for value in row.values()):
                raise ValueError("row shape")
            name = row["name"].strip()
            score = int(row["score"].strip())
            if not name or not 0 <= score <= 100:
                raise ValueError("name or score range")
            accepted.append({"name": name, "score": score})
        except ValueError:
            rejected.append(number)
    print(accepted)
    print("rejected records:", rejected)
    if accepted:
        print("average:", sum(row["score"] for row in accepted) / len(accepted))
    ''',
    "पहिले structure जाँचियो, त्यसपछि trim र int conversion। Mina को text संख्या होइन; Ram को 101 range बाहिर छ। "
    "Sita र Hari मात्र accepted भएकाले average 85 हुन्छ। Rejection report मा parsed data-record number राखिएको छ, file line होइन।",
    ("Compute average before excluding invalid rows",
     "Validate each row, then aggregate accepted records only",
     "Invalid values can cause a conversion error or corrupt the computed result."),
    "Write a reusable checked_score function. Test 0, 100, 101 and 'bad'; print accepted or rejected.",
    r'''
    def checked_score(text):
        score = int(text.strip())
        if not 0 <= score <= 100:
            raise ValueError("out of range")
        return score
    for value in ("0", "100", "101", "bad"):
        try:
            print(value, checked_score(value))
        except ValueError:
            print(value, "rejected")
    ''',
    "Calculate an average for [90,80], then handle an empty collection with None instead of zero or division by zero.",
    r'''
    def average(scores):
        return sum(scores) / len(scores) if scores else None
    print(average([90, 80]))
    print(average([]))
    ''',
    "Normalisation, conversion and validation are separate. Preserve rejected record positions. Aggregate only valid values and define the empty-result policy explicitly.",
    [
        ("Is score 101 valid under our policy?", "No", "Yes, because it is an int", "Only in CSV", "The score must satisfy the 0..100 domain rule."),
        ("Do parsed CSV record numbers always equal physical line numbers?", "No", "Yes", "Only after int conversion", "A quoted field can span several physical lines."),
    ])

add(0, "4. Writers, dialects, UTF-8 and a real file round trip",
    "Write a clean table with explicit columns and preserve Unicode and IDs.",
    [
        ("csv.writer; csv.DictWriter; writeheader", "writer writes sequences; DictWriter writes mappings in the specified fieldnames order. writeheader emits those names as the header record."),
        ("delimiter; quoting dialect", "A dialect is a collection of CSV formatting rules. Choose the known delimiter explicitly; a heuristic Sniffer is not a guarantee."),
        ("utf-8-sig; BOM", "A UTF-8 byte-order mark can appear in spreadsheet exports. Reading as utf-8-sig removes an optional initial BOM; ordinary UTF-8 preserves all normal Unicode text."),
        ("TemporaryDirectory; Path", "TemporaryDirectory gives these file examples an isolated disposable folder; Path composes file paths. The context closes and cleans up the practice folder automatically."),
    ],
    "Write one clean row per validated record. Fix column order using fieldnames rather than trusting arbitrary dictionary insertion. "
    "newline='' lets csv manage line endings. Use UTF-8 for Nepali/Japanese text; use utf-8-sig when a known input may have a BOM. "
    "For a spreadsheet semicolon export, pass delimiter=';'. DictWriter raises on unexpected fields by default, which helps detect lost schema agreement.",
    'with open(path, "w", newline="", encoding="utf-8") as handle:\n    writer = csv.DictWriter(handle, fieldnames=["id", "name"])\n    writer.writeheader()\n    writer.writerows(records)',
    r'''
    import csv
    import tempfile
    from pathlib import Path
    records = [{"id": "007", "name": "सीता"}, {"id": "008", "name": "東京"}]
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "people.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["id", "name"])
            writer.writeheader()
            writer.writerows(records)
        with path.open(newline="", encoding="utf-8") as handle:
            restored = list(csv.DictReader(handle))
        print(restored == records)
        print(restored[0]["id"], restored[0]["name"])
    ''',
    "Temporary folder प्रयोग भएकाले example चलाउँदा आफ्नो file मेटिँदैन। Header र rows त्यही क्रमले लेखिन्छन्। "
    "Read-back equality ले IDs र Unicode text सुरक्षित गएको जाँच्छ। Real app मा output path आफ्नो practice folder मा छान।",
    ("Open CSV files with platform-default encoding/newline handling",
     "Specify UTF-8 and newline='' for CSV text files",
     "Explicit encoding avoids platform-dependent corruption; newline control delegates CSV line handling to its parser."),
    "Read a semicolon-delimited table containing a quoted semicolon; write a comma-delimited clean version.",
    r'''
    import csv
    import io
    reader = csv.DictReader(io.StringIO('id;name\n007;"Sita; Hari"\n'), delimiter=";")
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=["id", "name"], lineterminator="\n")
    writer.writeheader()
    writer.writerows(reader)
    print(buffer.getvalue(), end="")
    ''',
    "Decode a BOM-prefixed CSV byte string as utf-8-sig and prove the first header is id, without a hidden BOM character.",
    r'''
    import csv
    import io
    raw = b"\xef\xbb\xbfid,name\n007,Sita\n"
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    print(reader.fieldnames)
    print(next(reader))
    ''',
    "Explicit columns, delimiters, newline handling and encoding make a round trip predictable. Keep identifiers as text and check equality after reading your output.",
    [
        ("What fixes DictWriter column order?", "fieldnames", "The longest value", "The filename extension", "The fieldnames sequence determines written columns."),
        ("Why use utf-8-sig for a known BOM-bearing input?", "It removes an optional initial UTF-8 BOM.", "It encrypts the table.", "It turns every ID into int.", "Otherwise the first field name may contain an invisible BOM character."),
    ])

add(1, "1. JSON: objects, arrays and the dumps/loads pair",
    "Distinguish Python values from JSON text and round-trip a nested record.",
    [
        ("Serialisation; deserialisation", "Serialisation encodes Python values as interchange text; deserialisation parses that text back into values."),
        ("json.dumps; json.loads", "dumps returns a JSON string; loads parses a JSON string. The s helps remember string, unlike the file-oriented dump/load pair."),
        ("JSON object/array/null/boolean", "JSON objects become dicts, arrays become lists, null becomes None, and true/false become True/False. Object keys must be strings in portable schemas."),
    ],
    "JSON is a data format, not Python source. It uses double-quoted strings, true/false and null; not Python's single-quoted repr, True or None. "
    "A Python dictionary is a value, while its dumps result is text. Parse with json.loads, never eval. "
    "Portable data uses string keys and explicit shapes; tuples turn into JSON arrays and return as lists.",
    'text = json.dumps(value, ensure_ascii=False, indent=2)\nrestored = json.loads(text)',
    r'''
    import json
    contact = {"name": "सीता", "phones": ["007"], "active": True, "note": None}
    text = json.dumps(contact, ensure_ascii=False, sort_keys=True)
    print(text)
    restored = json.loads(text)
    print(restored == contact)
    print(type(text).__name__, type(restored).__name__)
    ''',
    "dumps पछि result str हो; loads पछि dict भयो। ensure_ascii=False ले नेपाली text पढ्न सजिलो बनाउँछ, encryption गर्दैन। "
    "JSON null र true फेरि Python None र True बन्छन्। Sort_keys यहाँ reproducible display का लागि मात्र हो।",
    ("str(data) is valid portable JSON", "json.dumps(data) produces JSON text",
     "Python repr may contain single quotes, True and None, which are not JSON syntax."),
    "Parse a JSON array with true and null; print the Python value and element types.",
    r'''
    import json
    values = json.loads('[true, null, "007"]')
    print(values)
    print([type(value).__name__ for value in values])
    ''',
    "Round-trip a tuple and explain why equality with the original tuple is not preserved.",
    r'''
    import json
    original = (1, 2)
    restored = json.loads(json.dumps(original))
    print(original, restored)
    print(original == restored)
    ''',
    "JSON text and Python objects are different layers. dumps/loads operate on strings. Some Python types change shape, so choose an explicit portable schema.",
    [
        ("What does json.dumps return?", "str", "dict", "An open file", "It serialises the value into JSON text."),
        ("What does JSON null become in Python?", "None", "'null' always", "Zero", "null maps to Python's None value."),
    ])

add(1, "2. dump/load files: Unicode, failures and safe replacement",
    "Save one whole document without damaging an existing file on serialisation failure.",
    [
        ("json.dump; json.load", "dump writes one JSON document to an open file; load reads one document from an open file."),
        ("Temporary output + replace", "Serialise first, write a temporary file in the destination directory, then replace the destination after success. This avoids truncating the old file before serialisation finishes."),
        ("JSONDecodeError; UnicodeDecodeError", "A JSON syntax error and a text-encoding error are different failures. Report them rather than silently overwriting bad input with defaults."),
    ],
    "dump and load are useful for an opened UTF-8 file. Do not repeatedly append separate JSON objects to one file and call it a valid JSON document. "
    "For important data, first produce the complete text with dumps, then write a temporary sibling and replace the destination. "
    "This protects the old document from serialisation failure; full durability, concurrent writers and crash recovery require additional design. "
    "Never respond to a failed load by automatically saving an empty dataset over the old one.",
    'text = json.dumps(data, ensure_ascii=False, allow_nan=False)\nwrite temporary sibling → replace only after successful write',
    r'''
    import json
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as folder:
        target = Path(folder) / "contacts.json"
        data = {"contacts": [{"id": "007", "name": "सीता"}]}
        text = json.dumps(data, ensure_ascii=False, allow_nan=False)
        temporary = target.with_suffix(".json.tmp")
        temporary.write_text(text, encoding="utf-8")
        temporary.replace(target)
        with target.open(encoding="utf-8") as handle:
            print(json.load(handle) == data)
    ''',
    "पहिले serialisation सफल हुन्छ, त्यसपछि मात्रै file लेखिन्छ। Temporary sibling पूरा लेखिएपछि replace हुन्छ। "
    "यो practice example मा folder isolated छ। आफूले save गरेको document load गरेर equality जाँच। "
    "File-save logic नै progress storage हो भन्ने नसम्झ; Study Hub को storage यहाँ बदलिएको छैन।",
    ("Open the existing file in w mode before checking whether data can be serialised",
     "Serialise first; write a temporary sibling; replace after success",
     "Opening in w truncates immediately. If serialisation then fails, the old data may already be gone."),
    "Use dump/load with StringIO to demonstrate the file interface without touching a real file.",
    r'''
    import json
    import io
    handle = io.StringIO()
    json.dump({"name": "Sita", "score": 90}, handle)
    handle.seek(0)
    print(json.load(handle))
    ''',
    "Catch JSON syntax failure from a trailing comma, and separately catch UTF-8 decoding failure from invalid bytes.",
    r'''
    import json
    try:
        json.loads('{"score": 90,}')
    except json.JSONDecodeError:
        print("JSON syntax rejected")
    try:
        b"\xff".decode("utf-8")
    except UnicodeDecodeError:
        print("UTF-8 decoding rejected")
    ''',
    "One document per JSON file. Keep syntax errors, decoding errors and I/O errors distinct. Preserve old files on failed saves; a parse failure is not permission to erase data.",
    [
        ("Which pair reads/writes opened files?", "dump/load", "dumps/loads", "repr/eval", "The file pair accepts file-like handles."),
        ("Is appending two separate dump results one valid JSON document?", "No", "Yes", "Only with indent=2", "JSON is not automatically framed; use one array/document or a deliberately different format."),
    ])

add(1, "3. Strict JSON and validation after parsing",
    "Reject duplicate keys and non-finite values, then verify the expected schema.",
    [
        ("allow_nan=False", "Python's default encoder permits NaN/Infinity extensions. allow_nan=False rejects them when writing standards-compatible JSON."),
        ("parse_constant; object_pairs_hook", "parse_constant can reject non-finite numeric constants on input; object_pairs_hook receives key/value pairs and can detect duplicate object keys."),
        ("bool is a subclass of int", "isinstance(True, int) is True. If a schema requires an actual integer, use type(value) is int to reject booleans."),
    ],
    "Valid JSON syntax does not guarantee an object with the right fields. It can be a list, a string or an object with invalid values. "
    "Python accepts duplicate keys with the last value winning unless you intervene. A strict importer can reject duplicates instead of silently losing data. "
    "Use precise type/range checks after parsing. A boolean is not an acceptable score merely because Python treats bool as an int subclass.",
    'json.loads(text, object_pairs_hook=unique_object, parse_constant=reject_constant)\nif type(score) is not int: raise ValueError(...)',
    r'''
    import json
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate key")
            result[key] = value
        return result
    def reject_constant(value):
        raise ValueError("non-finite constant")
    for text in ('{"score":90}', '{"score":90,"score":80}', '{"score":NaN}'):
        try:
            print(json.loads(text, object_pairs_hook=unique_object,
                             parse_constant=reject_constant))
        except ValueError:
            print("rejected")
    print(isinstance(True, int), type(True) is int)
    ''',
    "Hook ले duplicate key दोस्रो पटक आएपछि reject गर्छ। parse_constant ले NaN रोक्छ। "
    "यी JSON parsing policies हुन्; score 0..100 rule अझै छुट्टै चाहिन्छ। "
    "True लाई integer score मान्ने गल्ती रोक्न exact type check प्रयोग गरिएको छ।",
    ("Parsed JSON is automatically safe and schema-valid",
     "Apply a declared schema and strict parsing policy",
     "Parsing identifies values; it does not decide which types, keys or ranges your application permits."),
    "Validate scores 90, True and 101 as actual integers in 0..100.",
    r'''
    def valid_score(value):
        return type(value) is int and 0 <= value <= 100
    for value in (90, True, 101):
        print(repr(value), valid_score(value))
    ''',
    "Attempt to serialise infinity with allow_nan=False and catch the intended error.",
    r'''
    import json
    try:
        json.dumps({"value": float("inf")}, allow_nan=False)
    except ValueError:
        print("non-finite output rejected")
    ''',
    "Strict parsing prevents silent duplicate-key loss and non-finite extensions. Domain validation follows parsing. Reject booleans where actual integers are required.",
    [
        ("What does a default JSON duplicate-key decode usually retain?", "The last value for the key", "Both values under one key", "It always raises", "A duplicate-key hook is needed if your policy rejects this."),
        ("Why use type(score) is int here?", "To reject booleans as scores.", "To make JSON faster.", "To convert strings.", "bool is an int subclass, so isinstance alone is broader than the schema."),
    ])

add(1, "4. Custom encoders: dates and explicit type decisions",
    "Encode unsupported values deliberately without hiding mistakes.",
    [
        ("default callback; JSONEncoder.default", "A default callback handles otherwise unsupported values. A JSONEncoder subclass can override default; delegate unsupported cases to the parent to raise TypeError."),
        ("ISO date representation", "Encode a date as a documented YYYY-MM-DD string, then explicitly parse that field on restoration. JSON does not remember Python date objects."),
    ],
    "Dates and ordinary custom objects are not automatically JSON values. Decide a schema instead of using default=str for everything. "
    "A generic string fallback can hide an unexpected object. For a date field, ISO text is clear and portable. "
    "Use Week 19 method overriding to customise an encoder; defer unknown types to super().default so a bug stays visible. "
    "A parsed string becomes a date only when your schema explicitly says to parse that field.",
    'class Encoder(json.JSONEncoder):\n    def default(self, value):\n        if isinstance(value, date): return value.isoformat()\n        return super().default(value)',
    r'''
    import json
    from datetime import date
    class DateEncoder(json.JSONEncoder):
        def default(self, value):
            if type(value) is date:
                return value.isoformat()
            return super().default(value)
    text = json.dumps({"birthday": date(2000, 1, 2)}, cls=DateEncoder)
    print(text)
    restored = json.loads(text)
    print(type(restored["birthday"]).__name__)
    print(date.fromisoformat(restored["birthday"]).year)
    ''',
    "Encoder ले date मात्र चिन्छ र ISO string दिन्छ। loads पछि birthday str हो, date होइन। "
    "fromisoformat ले documented field मात्र restore गर्छ। Unknown object आए parent method ले TypeError उठाउनुपर्छ, silently string होइन।",
    ("default=str silently encodes every unexpected object",
     "Handle supported types explicitly and raise on unsupported ones",
     "A catch-all fallback can conceal data modelling mistakes and loses type meaning."),
    "Use a default function for dates and prove a set is still rejected.",
    r'''
    import json
    from datetime import date
    def encode(value):
        if type(value) is date:
            return value.isoformat()
        raise TypeError("unsupported type")
    print(json.dumps({"day": date(2026, 10, 10)}, default=encode))
    try:
        json.dumps({"items": {1, 2}}, default=encode)
    except TypeError:
        print("set rejected")
    ''',
    "Model money as integer minor units and an explicit currency string rather than assuming a binary float preserves decimal money.",
    r'''
    import json
    invoice = {"currency": "NPR", "amount_minor": 1999}
    restored = json.loads(json.dumps(invoice))
    print(restored)
    print(type(restored["amount_minor"]).__name__)
    ''',
    "Custom encoding needs a documented restoration policy. Unknown types should fail clearly. Date strings and integer minor units are explicit representations, not magical preservation of Python types.",
    [
        ("Does JSON remember that an ISO string originally came from date?", "No", "Yes", "Only with indent", "Restoration follows your schema, not the string's appearance alone."),
        ("What should an encoder do with an unsupported unexpected type?", "Raise TypeError through the parent/default policy.", "Always stringify it.", "Drop the field silently.", "Visible failure exposes a schema mismatch."),
    ])

add(2, "1. Read the JSON shape before indexing",
    "Trace dictionaries and lists one level at a time and preserve meaningful falsey values.",
    [
        ("Data shape; nested path", "A shape describes where objects, arrays and scalar values occur. A path may alternate dictionary keys and list indexes."),
        ("Missing vs null vs empty vs zero", "A missing key, None, empty list and zero can have different meanings. A truthiness fallback such as value or default merges these cases."),
        ("Sentinel object", "A unique object() value can distinguish a missing key from an explicitly stored None when dict.get is used."),
    ],
    "An API response is just data once fetched. This lesson uses saved fixture JSON and requires no network. "
    "Write the path on paper: root dict → data dict → users list → first user dict → name string. "
    "Do not chain indexes before checking shape. A field score=0 is valid here; replacing it with a default because it is falsey would corrupt meaning.",
    'root["data"]["users"][0]["name"]\nmissing = object()\nvalue = mapping.get("field", missing)',
    r'''
    import json
    root = json.loads('{"data":{"users":[{"name":"Sita","score":0}]},"next":null}')
    users = root["data"]["users"]
    print(type(root).__name__, type(users).__name__)
    print(users[0]["name"], users[0]["score"])
    missing = object()
    print(root.get("absent", missing) is missing)
    print(root.get("next", missing) is None)
    print(users[0]["score"] or 99)
    ''',
    "User array मा index 0 पछि dict name key आउँछ। Explicit null को अर्थ None हो; missing key भने अलग sentinel हो। "
    "अन्तिम line मा 0 or 99 ले 99 दिएको देख: यो score को सही fallback होइन। "
    "Data contract अनुसार missing मात्र default गर्ने कि null पनि गर्ने भन्ने कुरा छुट्टै लेख।",
    ("score = record.get('score') or 99", "Use an explicit missing/null policy that preserves score 0",
     "Truthiness also treats zero, False and empty collections as absent."),
    "Check a missing score, an explicit None and score 0 separately without merging them.",
    r'''
    missing = object()
    for row in ({}, {"score": None}, {"score": 0}):
        value = row.get("score", missing)
        if value is missing:
            print("missing")
        elif value is None:
            print("null")
        else:
            print("score", value)
    ''',
    "Read nested users with no users present; avoid indexing position 0 on an empty list.",
    r'''
    root = {"data": {"users": []}}
    users = root["data"]["users"]
    print(users[0]["name"] if users else "no users")
    ''',
    "Trace keys and indexes according to shape. Missing, null, empty and zero are different states. Avoid truthiness defaults when zero or False is valid data.",
    [
        ("What is wrong with score or 99 when score=0 is valid?", "It replaces valid zero with 99.", "Nothing", "It validates the score.", "Zero is falsey but not necessarily missing."),
        ("What follows a list in a nested path?", "An index or iteration, not an assumed dictionary key", "Always ['name']", "json.dumps", "A list contains positional values; inspect those before dictionary access."),
    ])

add(2, "2. Safe traversal: report invalid shapes instead of hiding them",
    "Handle optional paths while rejecting a wrong container type.",
    [
        ("Optional path vs malformed shape", "A documented absent field can have a default. A present field of the wrong type should usually be reported as invalid, not silently treated as missing."),
        ("isinstance(container, dict/list)", "Check a container's type before calling dictionary methods or iterating it as a list of records."),
    ],
    "root.get('data', {}).get('users', []) is short, but it fails if data is None or a list. "
    "Repeated get calls are not general schema validation. A named read_users function can establish each expected container. "
    "This example permits missing data/users as an empty collection but rejects null or wrong types when present. "
    "That is a declared policy, not the only possible API contract.",
    'if not isinstance(root, dict): raise ValueError(...)\ncheck each present container\nreturn validated list',
    r'''
    def read_users(root):
        if not isinstance(root, dict):
            raise ValueError("root must be an object")
        data = root.get("data", {})
        if not isinstance(data, dict):
            raise ValueError("data must be an object")
        users = data.get("users", [])
        if not isinstance(users, list):
            raise ValueError("users must be an array")
        if any(not isinstance(user, dict) for user in users):
            raise ValueError("each user must be an object")
        return users
    for root in ({}, {"data": {"users": [{"name": "Sita"}]}}, {"data": None}):
        try:
            print(read_users(root))
        except ValueError as error:
            print(error)
    ''',
    "हरेक स्तरमा आफ्नो type check छ। Missing data मा हाम्रो policy empty users हो। "
    "तर data:null आएको छ भने present-but-invalid मानिन्छ। यसरी malformed response लाई सामान्य empty result भनेर लुकाइँदैन।",
    ("Catch every exception and return []", "Validate each container and report the intended ValueError",
     "A blanket fallback hides wrong types, programming errors and unexpected data contracts."),
    "Write read_items requiring an object with an items list. Reject items=None and items='text'.",
    r'''
    def read_items(root):
        if not isinstance(root, dict) or not isinstance(root.get("items"), list):
            raise ValueError("items array required")
        return root["items"]
    for root in ({"items": []}, {"items": None}, {"items": "text"}):
        try:
            print(read_items(root))
        except ValueError:
            print("invalid shape")
    ''',
    "Validate a profile/name path as a nonempty string and reject a list or a blank name.",
    r'''
    def read_name(root):
        if not isinstance(root, dict) or not isinstance(root.get("profile"), dict):
            raise ValueError("profile object required")
        name = root["profile"].get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("nonempty name required")
        return name.strip()
    for root in ({"profile": {"name": " Sita "}}, {"profile": []},
                 {"profile": {"name": " "}}):
        try:
            print(read_name(root))
        except ValueError:
            print("rejected")
    ''',
    "Default only what the contract permits. Check container types and field types in named functions; report malformed data instead of concealing it behind an empty result.",
    [
        ("Is chained get enough if a present parent is null?", "No", "Yes", "Only with indent", "None is not a dict and has no get method."),
        ("Why avoid except Exception: return [] for parsing?", "It hides malformed shapes and unrelated bugs.", "It is too strict.", "It preserves every field.", "Catch only expected failures and communicate the rejection."),
    ])

add(2, "3. Flatten nested records without changing their meaning",
    "Choose one output row per item and repeat its parent identifiers deliberately.",
    [
        ("Row grain", "The grain states what one row represents. Here one row is one purchased item within an order, not one customer or one whole order."),
        ("One-to-many relationship", "One customer can have multiple orders and each order multiple items. Flattening repeats parent identifiers to retain these relationships."),
        ("Empty-child policy", "No items means no item rows in this report. A separate order report is needed if empty orders must still be counted."),
    ],
    "Start with a three-level saved response: customer → orders → items. Write nested loops from the outside inward. "
    "Copy customer_id and order_id into each item row so its origin is not lost. Do not zip independent arrays and assume they align. "
    "Flattening is a deliberate projection: only selected fields survive. Keep the original document when other fields matter.",
    'for customer in customers:\n    for order in customer["orders"]:\n        for item in order["items"]:\n            rows.append(parent identifiers + item fields)',
    r'''
    data = {"customers": [
        {"id": "C1", "orders": [
            {"id": "O1", "items": [{"sku": "B1", "qty": 2}, {"sku": "P1", "qty": 1}]},
            {"id": "O2", "items": []}
        ]}
    ]}
    rows = []
    for customer in data["customers"]:
        for order in customer["orders"]:
            for item in order["items"]:
                rows.append({"customer_id": customer["id"], "order_id": order["id"],
                             "sku": item["sku"], "quantity": item["qty"]})
    for row in rows:
        print(row)
    print("item rows:", len(rows))
    ''',
    "Outer loop customer, त्यसपछि order र item हो। हरेक row मा parent IDs repeat भएको छ, त्यसैले origin थाहा हुन्छ। "
    "O2 empty भएकाले item rows मा आउँदैन। यसको अर्थ O2 थिएन होइन; हाम्रो report को grain item हो।",
    ("One flattened row always represents one parent", "Define the row grain before flattening",
     "A one-to-many child array can create several output rows for one parent or none for an empty child collection."),
    "Flatten a school/classes/students structure into class_id and student_name rows.",
    r'''
    school = {"classes": [
        {"id": "A", "students": [{"name": "Sita"}, {"name": "Hari"}]},
        {"id": "B", "students": [{"name": "Mina"}]}
    ]}
    rows = [{"class_id": group["id"], "student_name": student["name"]}
            for group in school["classes"] for student in group["students"]]
    print(rows)
    ''',
    "Count orders separately from item rows, including an empty order, and explain the difference.",
    r'''
    orders = [{"id": "O1", "items": [1, 2]}, {"id": "O2", "items": []}]
    print("orders:", len(orders))
    print("item rows:", sum(len(order["items"]) for order in orders))
    print("empty orders:", sum(not order["items"] for order in orders))
    ''',
    "Choose row grain explicitly, carry parent IDs, and state how empty child arrays are handled. Flattening can lose fields; retain the original when the projection is not sufficient.",
    [
        ("What does one row represent in the worked order example?", "One item within an order", "One customer", "Every order regardless of items", "The innermost loop emits one row per item."),
        ("Why repeat customer/order IDs in item rows?", "To preserve each item's parent relationship.", "To encrypt data.", "To remove duplicates automatically.", "Without those fields the flattened rows lose their origin."),
    ])

add(2, "4. Contact-manager JSON: validate, save and restore",
    "Give a small app a versioned JSON document while preserving text identifiers.",
    [
        ("Versioned envelope", "Wrap records in an object with schema_version and contacts. This lets future code identify the layout instead of guessing."),
        ("Uniqueness constraint", "IDs must be unique within the dataset; a parser alone does not enforce that rule."),
    ],
    "Your contact manager can store an envelope with schema_version=1 and contacts containing id, name and phones. "
    "IDs and phone numbers remain strings; they are identifiers, not arithmetic values. Validate required types and uniqueness before saving. "
    "A malformed old file should be reported and retained, not replaced by an empty address book. "
    "This is a practice program, separate from Study Hub's existing storage schema.",
    '{"schema_version": 1, "contacts": [{"id": "007", "name": "Sita", "phones": ["0123"]}]}',
    r'''
    import json
    def validate(document):
        if not isinstance(document, dict) or type(document.get("schema_version")) is not int or document["schema_version"] != 1:
            raise ValueError("unsupported schema")
        contacts = document.get("contacts")
        if not isinstance(contacts, list):
            raise ValueError("contacts array required")
        seen = set()
        for contact in contacts:
            if not isinstance(contact, dict) or set(contact) != {"id", "name", "phones"}:
                raise ValueError("contact fields")
            if any(not isinstance(contact[key], str) or not contact[key].strip() for key in ("id", "name")):
                raise ValueError("id and name required")
            if contact["id"] in seen:
                raise ValueError("duplicate id")
            phones = contact["phones"]
            if not isinstance(phones, list) or any(not isinstance(p, str) for p in phones):
                raise ValueError("phone strings required")
            seen.add(contact["id"])
        return document
    data = {"schema_version": 1, "contacts": [{"id": "007", "name": "Sita", "phones": ["0123"]}]}
    validate(data)
    restored = validate(json.loads(json.dumps(data)))
    print(restored == data)
    print(restored["contacts"][0]["phones"])
    ''',
    "Version पहिले जाँचिन्छ, त्यसपछि list र contact fields। ID duplicates set मा रोकिएका छन्। "
    "Phones strings भएकाले leading zero बच्यो। JSON syntax valid हुँदा पनि गलत structure reject हुन्छ। "
    "यो आफ्नै practice app मा प्रयोग गर्ने schema हो, हाम्रो website को progress format मा migration होइन।",
    ("Convert every contact ID and phone to int", "Keep textual identifiers as strings",
     "Leading zeros and formatting can be meaningful; arithmetic conversion destroys them."),
    "Reject duplicate contact IDs before writing any output file.",
    r'''
    contacts = [{"id": "007"}, {"id": "007"}]
    seen = set()
    try:
        for contact in contacts:
            if contact["id"] in seen:
                raise ValueError("duplicate contact id")
            seen.add(contact["id"])
    except ValueError as error:
        print(error)
    ''',
    "Save and restore a versioned contact envelope in an isolated temporary folder with UTF-8.",
    r'''
    import json
    import tempfile
    from pathlib import Path
    data = {"schema_version": 1, "contacts": [{"id": "007", "name": "सीता", "phones": []}]}
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "contacts.json"
        text = json.dumps(data, ensure_ascii=False, allow_nan=False)
        temp = path.with_suffix(".json.tmp")
        temp.write_text(text, encoding="utf-8")
        temp.replace(path)
        restored = json.loads(path.read_text(encoding="utf-8"))
        print(restored == data)
    ''',
    "Version the practice document, validate uniqueness and types before saving, and preserve identifiers as text. Keep a failed input file for diagnosis instead of erasing it.",
    [
        ("Should a phone number usually be converted to int for storage?", "No; it is a textual identifier.", "Yes, to remove zeroes.", "Only in JSON", "Text preserves formatting and leading zeros."),
        ("Why put schema_version around the records?", "To identify the document layout for controlled changes.", "To encrypt contacts.", "To avoid validation.", "Versioning makes evolution explicit; it does not replace validation."),
    ])

add(3, "1. INI settings with configparser",
    "Separate human-editable settings from code and convert values explicitly.",
    [
        ("configparser.ConfigParser", "A standard-library parser for section/key INI configuration. Values are normally stored as strings."),
        ("read_string; getint; getboolean", "read_string parses INI text; typed getters convert known settings. getboolean understands values such as yes/no and true/false."),
        ("Interpolation; interpolation=None", "Default INI interpolation gives % special meaning. Disable it when literal values should not use interpolation."),
    ],
    "Configuration is an input contract, not just a place to move constants. Our app section contains retries and debug. "
    "Read the types you need, then enforce a range such as retries 0..5. bool('false') is True because the string is nonempty; "
    "use the parser's boolean getter. ConfigParser lowercases option names by default. A local config file is plain text, not encryption.",
    'config = configparser.ConfigParser(interpolation=None)\nconfig.read_string(text)\nretries = config.getint("app", "retries")\ndebug = config.getboolean("app", "debug")',
    r'''
    import configparser
    config = configparser.ConfigParser(interpolation=None)
    config.read_string("[app]\nretries = 3\ndebug = false\nlabel = 50% done\n")
    retries = config.getint("app", "retries")
    if not 0 <= retries <= 5:
        raise ValueError("retry range")
    print(type(config["app"]["retries"]).__name__, retries)
    print(config.getboolean("app", "debug"))
    print(config["app"]["label"])
    ''',
    "INI मा 3 पनि पहिले string हुन्छ। getint ले integer र getboolean ले सही False निकाल्छ। "
    "interpolation=None भएकाले 50% literal text बच्यो। App-specific range parser ले आफैँ जाँच्दैन।",
    ("debug = bool(config['app']['debug'])", "debug = config.getboolean('app', 'debug')",
     "Any nonempty string, including 'false', is truthy; getboolean interprets the intended setting."),
    "Parse yes/no settings and compare getboolean with Python's ordinary bool on the string 'no'.",
    r'''
    import configparser
    config = configparser.ConfigParser()
    config.read_string("[app]\ndebug=no\n")
    print(bool(config["app"]["debug"]))
    print(config.getboolean("app", "debug"))
    ''',
    "Read an INI file from a temporary folder and verify that a section and expected setting were loaded.",
    r'''
    import configparser
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "settings.ini"
        path.write_text("[app]\nretries=2\n", encoding="utf-8")
        config = configparser.ConfigParser()
        loaded = config.read(path, encoding="utf-8")
        print(len(loaded), config.getint("app", "retries"))
    ''',
    "INI values start as strings. Use typed getters, validate ranges, choose an interpolation policy, and check required files/sections rather than assuming successful loading.",
    [
        ("What is bool('false')?", "True", "False", "A parse error", "It is a nonempty string; use an intentional boolean conversion."),
        ("Does getint enforce retries <= 5?", "No; that range is your application rule.", "Yes", "Only with interpolation", "A numeric conversion and a domain range are different checks."),
    ])

add(3, "2. TOML: typed settings with tomllib",
    "Read typed configuration with Python 3.11+ and validate its domain.",
    [
        ("TOML tables and arrays", "A [section] creates a table; TOML also has typed strings, integers, booleans and arrays. The resulting structure is nested Python dictionaries/lists."),
        ("tomllib.loads; tomllib.load", "Built into Python 3.11+. loads accepts a TOML string; load reads a binary file. tomllib reads TOML; it does not write it."),
        ("TOMLDecodeError", "Malformed TOML raises a parse exception. A successfully parsed value may still violate your application's schema."),
    ],
    "Use TOML when human-readable configuration benefits from explicit types. Unlike basic INI values, retries is already an int and debug a bool. "
    "Read real TOML files in binary mode ('rb'); the module handles encoding. "
    "These examples use basic TOML 1.0 syntax supported in Python 3.11/3.12, not newer-version features. "
    "Do not promise tomllib.dump—it does not exist.",
    'settings = tomllib.loads(text)\nwith open("settings.toml", "rb") as handle:\n    settings = tomllib.load(handle)',
    r'''
    import tomllib
    text = '[app]\nname="Study"\nretries=3\ndebug=false\nlanguages=["python","japanese"]\n'
    config = tomllib.loads(text)
    app = config["app"]
    print(app["name"], app["retries"], app["debug"])
    print(type(app["retries"]).__name__, type(app["debug"]).__name__)
    print(app["languages"])
    ''',
    "TOML table app nested dict हो। Integer र boolean को type parser बाटै आउँछ। "
    "तर retries=100 valid TOML हुन सक्छ; app ले range अझै जाँच्नुपर्छ। "
    "Built-in module Python 3.11 भन्दा पुरानो version मा छैन।",
    ("tomllib.dump writes your edited settings", "tomllib only reads TOML",
     "Use a deliberately chosen TOML writer package if you need writing; the standard library module has no dump function."),
    "Load a TOML file in binary mode from a temporary folder and inspect the parsed port.",
    r'''
    import tomllib
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "settings.toml"
        path.write_text("[server]\nport=8000\n", encoding="utf-8")
        with path.open("rb") as handle:
            print(tomllib.load(handle)["server"]["port"])
    ''',
    "Reject a malformed TOML integer, then separately reject a well-formed but out-of-range retry value.",
    r'''
    import tomllib
    try:
        tomllib.loads("retries = ???")
    except tomllib.TOMLDecodeError:
        print("syntax rejected")
    config = tomllib.loads("retries=100")
    print("valid application range:", type(config["retries"]) is int and 0 <= config["retries"] <= 5)
    ''',
    "tomllib is Python 3.11+ and read-only. load expects a binary handle; loads expects text. Typed parsing still needs schema and domain checks.",
    [
        ("Which mode does tomllib.load expect for a real file?", "rb", "w", "a", "The file-oriented reader consumes binary input."),
        ("Is retries=100 invalid TOML syntax?", "No; it may only violate the app's range rule.", "Yes, always.", "Only if debug=false.", "TOML syntax validity does not decide application-specific limits."),
    ])

add(3, "3. YAML: optional PyYAML and safe data loading",
    "Read basic YAML through safe_load and verify its resulting types.",
    [
        ("YAML mapping, sequence and indentation", "YAML can represent nested mappings/lists with indentation. Indentation affects structure; tabs and guessing are not a good editing strategy."),
        ("PyYAML; yaml.safe_load; yaml.safe_dump", "PyYAML is an optional installed package, not the standard library. safe_load avoids arbitrary Python-object construction; safe_dump emits basic data."),
        ("Scalar interpretation", "PyYAML may interpret unquoted words such as yes/no/on/off as booleans. Quote values intended to remain text, especially identifiers."),
    ],
    "Install PyYAML only if practising this optional format: python -m pip install PyYAML. "
    "The initial installation needs a connection; running these local examples after installation can be offline. "
    "Use safe_load rather than unsafe object-loading recipes. 'Safe' here is about allowed construction, not a guarantee against all resource exhaustion or a replacement for schema checks. "
    "An empty YAML document yields None. Keep identifiers quoted and inspect resulting types.",
    'data = yaml.safe_load(text)\ntext = yaml.safe_dump(data, allow_unicode=True, sort_keys=True)',
    r'''
    import yaml
    text = 'app:\n  name: Study\n  retries: 3\n  debug: false\n  code: "007"\n'
    config = yaml.safe_load(text)
    print(config["app"])
    print(yaml.safe_load("label: yes")["label"])
    print(yaml.safe_load('label: "yes"')["label"])
    restored = yaml.safe_load(yaml.safe_dump(config, allow_unicode=True))
    print(restored == config)
    ''',
    "Indentation ले app भित्रका settings राखेको छ। Quoted 007 text नै रहन्छ। "
    "Unquoted yes boolean हुन सक्छ; quoted yes string हुन्छ। Print गर्दा उस्तै देखिन सक्ने values को type पनि जाँच्ने बानी बसाल। "
    "Package installed नभए import error आउँछ; website पढ्न package चाहिँदैन।",
    ("yaml.load arbitrary documents with a Python-object loader",
     "Use yaml.safe_load for basic data and then validate the schema",
     "Unrestricted object construction can execute unintended behaviour; safe loading still needs data and size policies."),
    "Compare empty YAML, an empty mapping and an empty list.",
    r'''
    import yaml
    for text in ("", "{}", "[]"):
        value = yaml.safe_load(text)
        print(repr(value), type(value).__name__)
    ''',
    "Round-trip Nepali text and a quoted string ID through safe_dump/safe_load; assert equality.",
    r'''
    import yaml
    data = {"id": "007", "name": "सीता"}
    text = yaml.safe_dump(data, allow_unicode=True)
    restored = yaml.safe_load(text)
    assert restored == data
    print(restored)
    ''',
    "YAML is an optional package exercise. Use safe_load, quote textual identifiers, inspect scalar types, and validate the result. Safe construction is not a complete security or schema guarantee.",
    [
        ("Is PyYAML built into Python's standard library?", "No", "Yes", "Only on Windows", "Install the optional package for these local examples."),
        ("What does safe_load('') return?", "None", "Always {}", "Always []", "An empty document is null-like; do not assume it is a mapping."),
    ])

add(3, "4. .env files: strings, precedence and private settings",
    "Read development settings without printing credentials or assuming .env is secret storage.",
    [
        ("python-dotenv; dotenv_values", "The optional python-dotenv package parses .env settings. dotenv_values returns a mapping without modifying process environment variables."),
        ("load_dotenv; override=False", "load_dotenv populates the environment; by default an existing environment variable wins. Pass an explicit file path so loading location is predictable."),
        ("os.environ; environment precedence", "Environment variables are strings supplied to a process. Convert and validate them; choose whether deployment settings or a local file wins."),
    ],
    "Install python-dotenv for this optional practice part: python -m pip install python-dotenv. "
    "A .env file is plain text, not encrypted storage. In a private local Python app, keep it out of Git and use an example file with placeholders. "
    "Never place real tokens in public HTML/JS, public repository files, or this lesson's examples: visitors can read downloaded frontend files. "
    "These snippets use only demo limits, no credentials. Loading a config file does not hide secrets in a static website.",
    'settings = dotenv_values(stream=StringIO(text), interpolate=False)\n# explicit file:\nload_dotenv(path, override=False)',
    r'''
    from dotenv import dotenv_values
    from io import StringIO
    settings = dotenv_values(stream=StringIO("STUDY_LIMIT=20\nSTUDY_DEBUG=false\n"), interpolate=False)
    limit = int(settings["STUDY_LIMIT"])
    debug = settings["STUDY_DEBUG"].lower() == "true"
    if not 1 <= limit <= 100:
        raise ValueError("limit range")
    print(limit, type(limit).__name__)
    print(debug)
    ''',
    "Values strings छन्, त्यसैले limit int बनायौँ। false लाई bool('false') बाट नबनाऊ। "
    "यो दुई accepted boolean values भएको demo हो; real loader मा unknown values reject गर्ने validation राख। "
    "dotenv_values ले environment बदल्दैन। Secret राख्ने file public push भए secret हुँदैन।",
    ("Put a real token in public JS or commit .env, then hide it with CSS",
     "Keep private credentials out of public frontend files and repository history",
     "Anyone can read public source/downloaded files. A .env extension or hidden UI is not encryption."),
    "Parse true/false text with a function that rejects an unexpected value such as 'maybe'.",
    r'''
    def parse_bool(value):
        value = value.strip().lower()
        if value not in {"true", "false"}:
            raise ValueError("true or false required")
        return value == "true"
    for value in ("true", "false", "maybe"):
        try:
            print(value, parse_bool(value))
        except ValueError:
            print(value, "rejected")
    ''',
    "Show that an existing demo environment value wins with load_dotenv's default override=False. Use only a temporary demo file.",
    r'''
    import os
    import tempfile
    from pathlib import Path
    from dotenv import load_dotenv
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "demo.env"
        path.write_text("STUDY_DEMO_LIMIT=20\n", encoding="utf-8")
        os.environ["STUDY_DEMO_LIMIT"] = "30"
        load_dotenv(path, override=False)
        print(os.environ["STUDY_DEMO_LIMIT"])
    ''',
    "A .env file is plaintext configuration for a local process. Declare precedence, convert and validate strings, use explicit paths, and keep real secrets out of public source and logs.",
    [
        ("Does the .env filename encrypt its contents?", "No", "Yes", "Only if gitignored", "Git exclusion avoids publication but is not encryption."),
        ("With override=False, which value wins when already present?", "The existing environment value", "Always the file value", "The alphabetically first value", "load_dotenv preserves existing environment variables by default."),
    ])

add(4, "1. XML: elements, attributes and text",
    "Read a small well-formed XML feed without treating it as a flat delimiter format.",
    [
        ("XML element; attribute; text", "An XML element has a tag, attributes and possibly child elements/text. Matching opening/closing tags forms a tree."),
        ("xml.etree.ElementTree; fromstring", "ElementTree is the standard-library XML API. fromstring parses XML text into the root Element."),
        ("find; findall; findtext; get", "find returns the first matching child or None; findall returns a list; findtext gets child text; get reads an attribute."),
    ],
    "Our feed contains books with an id attribute and title/pages children. Read the tree according to that schema. "
    "Do not assume title is always present; missing children need a stated policy. Attribute values and element text are strings. "
    "This lesson uses small local fixtures; do not treat the example parser as a hardened public XML import service.",
    'root = ET.fromstring(text)\nfor element in root.findall("book"):\n    identifier = element.get("id")\n    title = element.findtext("title")',
    r'''
    import xml.etree.ElementTree as ET
    text = '<library><book id="007"><title>Python</title><pages>120</pages></book></library>'
    root = ET.fromstring(text)
    print(root.tag)
    for book in root.findall("book"):
        print(book.get("id"), book.findtext("title"), int(book.findtext("pages")))
    print(root.find("missing") is None)
    ''',
    "Root library हो। findall('book') ले child books दिन्छ। id attribute get बाट र title/pages child text findtext बाट पढिन्छ। "
    "Pages लाई int बनाउनु conversion हो; negative वा missing pages को rule validation मा जाँचिन्छ।",
    ("Use regex to reconstruct arbitrary nested XML", "Parse a tree and validate expected fields",
     "XML has nesting, escaping, attributes and namespaces; a flat regex recipe does not implement its grammar."),
    "Parse two entry elements into dictionaries with id and title fields.",
    r'''
    import xml.etree.ElementTree as ET
    root = ET.fromstring('<feed><entry id="A"><title>One</title></entry><entry id="B"><title>Two</title></entry></feed>')
    rows = [{"id": item.get("id"), "title": item.findtext("title")}
            for item in root.findall("entry")]
    print(rows)
    ''',
    "Reject a book with no title. Check None explicitly instead of relying on an Element's truthiness.",
    r'''
    import xml.etree.ElementTree as ET
    book = ET.fromstring('<book id="007"><pages>120</pages></book>')
    title = book.find("title")
    if title is None:
        print("title missing")
    else:
        print(title.text)
    ''',
    "Read attributes and child text through the tree API. Handle missing children explicitly; find may return None. Parsing structure and validating values are separate.",
    [
        ("How do you read an id attribute?", "element.get('id')", "element.findtext('id') always", "element.id()", "get reads attributes; findtext reads child element text."),
        ("What can find return when no child matches?", "None", "Always an empty Element", "Zero", "Check absence before accessing .text."),
    ])

add(4, "2. Write XML and let the serializer escape text",
    "Construct elements without interpolating raw user text into markup.",
    [
        ("ET.Element; ET.SubElement", "Element creates a node; SubElement creates and attaches a child to a parent."),
        ("ET.tostring; encoding='unicode'", "tostring serialises a tree. Unicode mode returns str; byte encoding modes return bytes."),
        ("Element text vs markup", "Assign data to .text so the serializer escapes characters such as & and <. String-concatenating raw data into XML can break structure."),
    ],
    "Construct a fixed schema tree, put attributes in a dictionary and assign content to .text. "
    "Do not use f'<name>{user_text}</name>' for arbitrary text. The serializer handles XML syntax escaping; "
    "it does not prove that every possible control character is legal XML or that your domain values are valid. "
    "Our examples use ordinary valid text, then parse the output back to check content.",
    'root = ET.Element("students")\nstudent = ET.SubElement(root, "student", {"id": "007"})\nET.SubElement(student, "name").text = name',
    r'''
    import xml.etree.ElementTree as ET
    root = ET.Element("students")
    student = ET.SubElement(root, "student", {"id": "007"})
    ET.SubElement(student, "name").text = "Sita & Hari <team>"
    text = ET.tostring(root, encoding="unicode")
    print(text)
    restored = ET.fromstring(text)
    print(restored.findtext("student/name"))
    ''',
    "Content text राख्दा ampersand र angle brackets escape हुन्छन्। Parse गरेपछि original name फिर्ता आउँछ। "
    "Encoding='unicode' मा result str हो; encoding='utf-8' मा bytes हुन्छ। File write mode त्यसअनुसार मिलाऊ।",
    ("Concatenate raw names into XML tags", "Assign names to Element.text and serialise the tree",
     "Raw & or < can create malformed markup or unintended structure."),
    "Serialise a Nepali name as UTF-8 bytes and parse it back, retaining a text ID.",
    r'''
    import xml.etree.ElementTree as ET
    root = ET.Element("person", {"id": "007"})
    root.text = "सीता"
    encoded = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    restored = ET.fromstring(encoded)
    print(type(encoded).__name__)
    print(restored.get("id"), restored.text)
    ''',
    "Write/read an XML tree through a temporary file; check that escaped text returns unchanged.",
    r'''
    import tempfile
    from pathlib import Path
    import xml.etree.ElementTree as ET
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "person.xml"
        root = ET.Element("person")
        root.text = "A & B"
        ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
        print(ET.parse(path).getroot().text)
    ''',
    "Construct the tree, assign data as text/attributes, then serialise. Escaping preserves syntax; schema validity and legal-character policies still belong to your application.",
    [
        ("What type does tostring(..., encoding='unicode') return?", "str", "bytes", "dict", "Unicode mode produces a text string; byte encodings produce bytes."),
        ("Why assign data to .text?", "The serializer escapes markup-sensitive characters.", "It encrypts the data.", "It creates extra nested tags.", "Data text should not become raw markup."),
    ])

add(4, "3. Namespaces and field validation in an XML feed",
    "Use namespace URIs and reject missing or impossible values.",
    [
        ("XML namespace; {uri}local-name", "A namespaced tag is identified by its URI plus local name. Prefix spelling is only a document alias, not the identity."),
        ("Namespace mapping in findall", "Pass a prefix-to-URI dictionary to findall/findtext and use that chosen prefix in the search expression."),
        ("Element absence vs empty element", "Use element is None for absence. An existing element without children can be falsey on older Python versions; truthiness is not a reliable presence test."),
    ],
    "A default namespace makes book become {urn:study}book, so findall('book') alone no longer finds it. "
    "Choose your own search prefix, map it to the URI and read fields under that mapping. "
    "Validate required names and pages > 0; report invalid records. An empty <title/> exists but may have text None, "
    "so check the text as well as element existence.",
    'ns = {"s": "urn:study"}\nroot.findall("s:book", ns)\nbook.findtext("s:title", namespaces=ns)',
    r'''
    import xml.etree.ElementTree as ET
    root = ET.fromstring('<library xmlns="urn:study"><book id="007"><title>Python</title><pages>120</pages></book></library>')
    ns = {"s": "urn:study"}
    print(len(root.findall("book")), len(root.findall("s:book", ns)))
    for book in root.findall("s:book", ns):
        title = book.findtext("s:title", namespaces=ns)
        pages = book.findtext("s:pages", namespaces=ns)
        if not title or pages is None or int(pages) <= 0:
            raise ValueError("invalid book fields")
        print(book.get("id"), title, int(pages))
    ''',
    "Default namespace भए plain tag search खाली आयो। s prefix हाम्रो code को alias हो; URI मिल्नु मुख्य कुरा हो। "
    "Title text खाली भयो वा pages invalid भए parsed tree हुँदा पनि record reject गर्नुपर्छ।",
    ("Match XML namespace identity by prefix spelling only", "Map a chosen prefix to the namespace URI",
     "Different prefixes can name the same URI; prefixes themselves are not the semantic identity."),
    "Read a prefixed feed using a different code-side prefix that points to the same URI.",
    r'''
    import xml.etree.ElementTree as ET
    root = ET.fromstring('<x:feed xmlns:x="urn:demo"><x:title>Study</x:title></x:feed>')
    print(root.findtext("d:title", namespaces={"d": "urn:demo"}))
    ''',
    "Distinguish a missing title element from a present empty title element without truthiness tests.",
    r'''
    import xml.etree.ElementTree as ET
    for text in ("<book/>", "<book><title/></book>"):
        title = ET.fromstring(text).find("title")
        print("missing" if title is None else "present with text " + repr(title.text))
    ''',
    "Namespaces are URI-based. Use explicit mappings in searches and explicit None checks for presence. Validate required text and numeric domain rules after tree parsing.",
    [
        ("Why may findall('book') miss a default-namespaced book?", "Its tag includes a namespace URI.", "All XML is case-insensitive.", "It has an attribute.", "The expanded tag is not the unqualified name book."),
        ("Which presence check is reliable for a find result?", "element is None", "not element in every Python version", "len(element)==0 means missing", "An existing childless Element can have misleading truthiness."),
    ])

add(4, "4. XML errors and why HTML needs a different parser",
    "Catch malformed XML and use HTMLParser for a modest HTML text exercise.",
    [
        ("ET.ParseError", "Malformed XML raises ParseError. XML requires well-formed nesting; HTML uses different syntax and error handling."),
        ("HTMLParser; handle_data", "A standard-library HTML event parser can invoke a subclass's handle_data for text. It is not an XML parser or a complete browser."),
        ("Small trusted fixtures vs hardened import", "For unfamiliar/untrusted XML, resource limits and deliberately hardened XML tooling matter. The teaching examples use small local files; do not assume arbitrary DTD/entity input is safe."),
    ],
    "XML and HTML are not interchangeable just because both have angle brackets. XML requires well-formed structure; "
    "HTML commonly contains void tags and omitted closing tags. Use HTMLParser for this small text-collection task. "
    "Collecting text is not sanitisation or faithful browser-visible text extraction: spacing, scripts and hidden content need additional policy. "
    "Keep parsing errors visible and preserve the original input for diagnosis.",
    'try: root = ET.fromstring(text)\nexcept ET.ParseError: report invalid XML\n# HTML uses HTMLParser, not ElementTree.fromstring',
    r'''
    import xml.etree.ElementTree as ET
    from html.parser import HTMLParser
    try:
        ET.fromstring("<root><item></root>")
    except ET.ParseError:
        print("malformed XML rejected")
    class TextCollector(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.parts = []
        def handle_data(self, data):
            self.parts.append(data)
    parser = TextCollector()
    parser.feed("<p>Study &amp; practise.</p>")
    parser.close()
    print("".join(parser.parts))
    ''',
    "Mismatched XML tags मा ParseError आउँछ। HTMLParser subclass ले data chunks जम्मा गर्छ; "
    "&amp; ordinary text मा & बन्छ। यो text extraction demo हो, security sanitizer होइन। "
    "Input गलत हुँदा empty data save गरेर पुरानो original नहटाऊ।",
    ("Feed every HTML page to ElementTree as though it were well-formed XML",
     "Choose a parser that understands the input format",
     "HTML's syntax and recovery rules differ from XML's well-formedness requirements."),
    "Parse valid and invalid small XML strings, printing the root tag or a rejection.",
    r'''
    import xml.etree.ElementTree as ET
    for text in ("<root/>", "<root><x></root>"):
        try:
            print(ET.fromstring(text).tag)
        except ET.ParseError:
            print("XML rejected")
    ''',
    "Collect text from an HTML paragraph with a bold child. Keep existing text spacing rather than inserting spaces into every character chunk.",
    r'''
    from html.parser import HTMLParser
    class TextCollector(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.parts = []
        def handle_data(self, data):
            self.parts.append(data)
    parser = TextCollector()
    parser.feed("<p>Learn <b>Python</b> daily.</p>")
    parser.close()
    print("".join(parser.parts))
    ''',
    "Use the correct parser, expose intended parse failures and retain originals. Text extraction is not sanitisation; a small local XML exercise is not a hardened arbitrary-input service.",
    [
        ("Are XML and HTML parsing rules identical?", "No", "Yes", "Only with UTF-8", "They have different grammars and error handling."),
        ("Does handle_data collection sanitise HTML?", "No", "Yes", "Only if joined with spaces", "It collects text callbacks, not a complete security or visibility policy."),
    ])

add(5, "1. Choose a format from the data and the job",
    "Compare tables, nested documents, configuration and transactional storage.",
    [
        ("Interchange vs storage requirements", "A portable export format and a live storage system serve different needs. CSV/JSON exports do not supply database transactions, indexing or concurrent-write coordination."),
        ("Projection and lossy conversion", "A conversion may discard nesting, types, comments or empty/missing distinctions. State the supported schema and what survives."),
    ],
    "CSV fits a flat table with fixed columns; JSON fits nested documents and many APIs; XML fits tree/attribute contracts used by feeds and established systems. "
    "INI/TOML/YAML suit configuration; .env supplies local process strings. A database is useful for constrained updates, queries, indexes and concurrency "
    "rather than repeatedly rewriting a large document. Database implementation comes later in the course. "
    "There is no universal converter for all possible CSV/JSON/XML documents. Our toolkit supports one declared student table only.",
    'Choose: row grain + types + required fields + consumer contract + update needs\nThen choose the format; do not decide from the filename alone.',
    r'''
    import csv
    import io
    import json
    student = {"id": "007", "name": "Sita", "score": 90}
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=["id", "name", "score"], lineterminator="\n")
    writer.writeheader()
    writer.writerow(student)
    restored_csv = next(csv.DictReader(io.StringIO(buffer.getvalue())))
    restored_json = json.loads(json.dumps(student))
    print(type(restored_csv["score"]).__name__, type(restored_json["score"]).__name__)
    restored_csv["score"] = int(restored_csv["score"])
    print(restored_csv == restored_json)
    ''',
    "CSV मा score read-back string भयो; JSON मा integer बच्यो। हाम्रो schema अनुसार int conversion गरेपछि equality मिल्यो। "
    "त्यही conversion नियम नभए दुई format को result समान हुँदैन। Nested phone arrays CSV मा flatten गर्दा अर्को schema चाहिन्छ।",
    ("Any JSON document can be converted to CSV without a schema or information loss",
     "Declare a supported table projection and its losses",
     "CSV cannot directly preserve every arbitrary nested structure and type."),
    "Show that a JSON phone list stays nested. Produce one flat row per phone, retaining the owner ID.",
    r'''
    import json
    person = json.loads('{"id":"007","phones":["0123","0456"]}')
    rows = [{"owner_id": person["id"], "phone": phone} for phone in person["phones"]]
    print(rows)
    ''',
    "Write a small decision mapping for exporting scores, storing nested contacts and handling concurrent stock updates. Explain why their needs differ.",
    r'''
    choices = {
        "flat score export": "CSV with an explicit score schema",
        "nested contact document": "JSON with a versioned envelope",
        "concurrent stock updates": "database with transactions and constraints",
    }
    for job, choice in choices.items():
        print(job + ": " + choice)
    ''',
    "Choose from the shape, consumer and update requirements. Export files are not transactional databases. Explicit schemas make conversions reproducible and reveal losses.",
    [
        ("Is an arbitrary nested JSON-to-CSV conversion automatically lossless?", "No", "Yes", "Only with UTF-8", "A table projection must define how nested and missing values are represented."),
        ("Which requirement particularly favours a database?", "Coordinated transactional updates and queries", "A single tiny static export", "A .csv extension", "Transactions and indexing address live storage needs beyond a text export."),
    ])

add(5, "2. Schema evolution: a controlled migration",
    "Migrate an older practice document without mutating its original.",
    [
        ("Schema migration", "A migration is an explicit transformation from one supported layout/version to another. Validate input and output, and keep a backup of the original."),
        ("Pure transformation", "A pure migration returns new data instead of changing the caller's original object or silently rewriting its file."),
    ],
    "In a separate student practice app, version 1 stores points and version 2 stores score. "
    "Read version exactly, reject unsupported versions, validate old field shapes, then build a fresh version-2 document. "
    "Do not guess version from a key's presence, and do not silently turn missing points into zero. "
    "The example never migrates Study Hub's localStorage; its existing maps stay unchanged.",
    'read version → validate old document → construct new document → validate new document → save separately/back up original',
    r'''
    import json
    def migrate(document):
        if not isinstance(document, dict) or type(document.get("version")) is not int or document["version"] != 1:
            raise ValueError("version 1 required")
        records = document.get("students")
        if not isinstance(records, list):
            raise ValueError("students array required")
        rows = []
        for row in records:
            if not isinstance(row, dict) or set(row) != {"id", "name", "points"}:
                raise ValueError("old fields")
            if any(not isinstance(row[key], str) or not row[key].strip() for key in ("id", "name")):
                raise ValueError("text fields")
            if type(row["points"]) is not int or not 0 <= row["points"] <= 100:
                raise ValueError("points range")
            rows.append({"id": row["id"], "name": row["name"], "score": row["points"]})
        if len({row["id"] for row in rows}) != len(rows):
            raise ValueError("duplicate ids")
        return {"version": 2, "students": rows}
    old = {"version": 1, "students": [{"id": "007", "name": "Sita", "points": 90}]}
    snapshot = json.dumps(old, sort_keys=True)
    print(migrate(old))
    print(json.dumps(old, sort_keys=True) == snapshot)
    ''',
    "Migration ले old dict मा score थपेर points मेट्दैन; नयाँ rows बनाउँछ। Snapshot comparison ले original unchanged भएको देखाउँछ। "
    "Version field exact integer हुनुपर्छ; boolean True लाई version 1 भनेर स्वीकारिँदैन। "
    "Save छुट्टै step भएपछि validation failure ले original file छुँदैन।",
    ("Modify the original file while guessing its layout", "Validate a recognised version and build a new document",
     "Unrecognised layouts and failed partial rewrites can destroy meaningful data."),
    "Make a tiny non-mutating points-to-score transformation and assert that the source still has points.",
    r'''
    old = {"id": "007", "points": 90}
    new = {"id": old["id"], "score": old["points"]}
    assert old == {"id": "007", "points": 90}
    print(old)
    print(new)
    ''',
    "Check versions 1, True and 3 with an exact-integer policy; reject booleans and unsupported layouts.",
    r'''
    for version in (1, True, 3):
        recognised = type(version) is int and version in {1, 2}
        print(repr(version), recognised)
    ''',
    "Versioning requires explicit recognised layouts, validation and backups. Transform in memory without mutating the original, then save only a validated result.",
    [
        ("Should a migration guess layout and overwrite immediately?", "No", "Yes", "Only for JSON", "Recognise and validate the version; preserve a recoverable original."),
        ("Why return new rows instead of mutating source rows?", "So a failed transformation leaves the original available.", "To skip validation.", "To encrypt fields.", "Separating transformation from saving makes errors recoverable."),
    ])

PROJECT = clean(r'''
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
''')

SAMPLE = clean(r'''
records = [{"id": "007", "name": "सीता & Hari", "score": 90},
           {"id": "008", "name": "東京", "score": 80}]
''')

DEMO = clean(r'''
with tempfile.TemporaryDirectory() as folder:
    folder = Path(folder)
    paths = {}
    for kind in ("csv", "json", "xml"):
        paths[kind] = folder / ("input." + kind)
        paths[kind].write_text(render_rows(records, kind), encoding="utf-8")
    for input_format in ("csv", "json", "xml"):
        for output_format in ("csv", "json", "xml"):
            if input_format == output_format:
                continue
            destination = folder / (input_format + "-to-" + output_format + "." + output_format)
            count = convert(paths[input_format], destination, input_format, output_format)
            assert count == 2
            assert read_rows(destination, output_format) == records
            print(input_format + " -> " + output_format + ": passed")
''')

FAILURES = clean(r'''
with tempfile.TemporaryDirectory() as folder:
    folder = Path(folder)
    output = folder / "result.json"
    bad = folder / "bad.csv"
    bad.write_text("id,name,score\n007,Sita,101\n", encoding="utf-8")
    try:
        convert(bad, output, "csv", "json")
    except ValueError:
        print("invalid score rejected")
    assert not output.exists()
    bad.write_bytes(b"\xff")
    try:
        convert(bad, output, "csv", "json")
    except UnicodeDecodeError:
        print("invalid UTF-8 rejected")
    assert not output.exists()
    good = folder / "good.csv"
    good.write_text(render_rows(records, "csv"), encoding="utf-8")
    output.write_text("KEEP", encoding="utf-8")
    try:
        convert(good, output, "csv", "json")
    except ValueError:
        print("existing output protected")
    assert output.read_text(encoding="utf-8") == "KEEP"
''')

CLI_DEMO = clean(r'''
with tempfile.TemporaryDirectory() as folder:
    source = Path(folder) / "scores.csv"
    destination = Path(folder) / "scores.json"
    source.write_text(render_rows(records, "csv"), encoding="utf-8")
    code = main([str(source), str(destination), "--input-format", "csv",
                 "--output-format", "json"])
    print("exit status:", code)
    print("round trip:", read_rows(destination, "json") == records)
''')

add(5, "3. Complete project: a validated conversion CLI",
    "Convert a declared student schema among CSV, JSON and XML, with clear errors and protected output.",
    [
        ("argparse.ArgumentParser; add_argument; parse_args", "argparse defines command-line positional inputs and options, parses them, and generates help. Passing a list to main enables reproducible examples without typing commands."),
        ("choices; required=True", "choices restricts a format option to csv/json/xml; required=True makes the user supply it. The file extension alone does not decide the format."),
        ("sys.stderr; exit status", "Error messages go to stderr; main returns 1 for a conversion failure and 0 for success. sys.exit(main()) exposes that result to the shell."),
        ("NamedTemporaryFile; unlink; finally", "A uniquely named temporary sibling avoids a fixed temporary filename. After writing, replace publishes the output; finally removes a leftover temporary file on failure."),
        ("XML 1.0 character policy", "The project checks XML-compatible text ranges because content is exported to all three formats. Numeric hexadecimal ranges are code-point limits, not a new text encoding."),
    ],
    "This is a schema-specific toolkit, not an arbitrary-document converter. One row has a 1..32-character ASCII letter/digit/_/- ID, "
    "a nonempty name of at most 200 characters, and an actual integer score 0..100. Names have outer whitespace trimmed; IDs stay text. "
    "CSV has exact id,name,score headers; JSON is {version:2, students:[...]}; XML is a students/version=2 tree. "
    "Duplicate IDs, JSON duplicate keys, unsupported fields and invalid types are rejected. "
    "The input policy is UTF-8 with an optional BOM, at most 1 MB and 10000 records; errors='ignore' is never used. "
    "The CLI refuses a same input/output path or an already-existing destination. It validates and renders before writing a unique temporary sibling. "
    "This teaching implementation is for a small local file and one writer; it is not a concurrent transaction system or a hardened public importer. "
    "DTD/entity declarations are unsupported in this small XML contract.",
    'python data_converter.py scores.csv scores.json --input-format csv --output-format json\npython data_converter.py scores.json scores.xml --input-format json --output-format xml\npython data_converter.py --help',
    PROJECT + SAMPLE + DEMO,
    "Code लाई पाँच चरणमा पढ: validate_rows → read_rows → render_rows → convert → main। "
    "read_rows ले bytes limit, UTF-8 decode र format parser चलाउँछ; सबै routes अन्ततः एउटै row validator मा पुग्छन्। "
    "render_rows ले एउटै canonical records बाट output बनाउँछ। convert ले पुराना files नछोई validation पूरा गर्छ, "
    "temporary output सफल भएपछि replace गर्छ। main ले user options र readable errors सम्हाल्छ। "
    "Demo मा छ वटा फरक-format directions चल्छन् र हरेक output फेरि पढेर original records सँग equality जाँचिन्छ। "
    "पूरा source docs/python-week23-data-converter.py मा पनि छ; अभ्यासको copy data_converter.py भनेर save गर्न सक्छौ।",
    ("Write a destination first, ignore decoding errors, then hope conversion worked",
     "Decode strictly, validate the schema, render, and publish output only after success",
     "Ignoring encoding errors silently loses characters. Writing too early can destroy an old file even when conversion is invalid."),
    "Prove that invalid score and bad UTF-8 create no output, and an existing destination remains unchanged.",
    PROJECT + SAMPLE + FAILURES,
    "Call main with an explicit list of CLI arguments, convert CSV to JSON, and verify exit status 0 plus complete record equality.",
    PROJECT + SAMPLE + CLI_DEMO,
    "Use one canonical validated model across formats. Preserve Unicode and text IDs; reject bad data explicitly. Validate before writing and check both output contents and failure-state preservation.",
    [
        ("Does this CLI convert every possible XML/JSON schema?", "No; only its declared student table.", "Yes", "Only if files are small", "Each format adapter implements one explicit agreed schema."),
        ("What happens if the destination already exists?", "Conversion is refused and it stays unchanged.", "It is erased automatically.", "Its rows are merged silently.", "The teaching CLI requires a new output filename."),
    ])

add(5, "4. Whole-week review: retrieval, round trips and rejection tests",
    "Rebuild a small adapter, explain its schema, and test the failure paths.",
    [
        ("Round-trip test", "Encode, parse and compare the canonical values, not byte formatting alone. Whitespace/key order can change while values remain equal."),
        ("Failure-state test", "A rejected conversion should leave the source and existing output unchanged and avoid a misleading partial result."),
    ],
    "Use as many study sessions as you need. Day 7 remains your existing review/rest day. "
    "First explain reader/DictReader, dump/dumps/load/loads, nested path/container checks and configuration precedence. "
    "Then rebuild one format adapter without a template. Add tests for empty valid tables, Unicode names, leading-zero IDs, "
    "missing/extra fields, duplicate IDs, invalid scores, wrong versions and malformed input. "
    "All exercises and answers are stored in the page for offline study; only optional package installation needs an initial connection.",
    'parse → validate canonical model → serialise → parse again → compare values\nFor rejection: assert no new output and preserved existing files.',
    r'''
    import json
    data = {"name": "Sita", "score": 90}
    compact = json.dumps(data, separators=(",", ":"))
    pretty = json.dumps(data, indent=2)
    print(compact == pretty)
    print(json.loads(compact) == json.loads(pretty))
    ''',
    "पहिलो comparison text formatting को हो, त्यसैले False। दोस्रो parsed values को हो, त्यसैले True। "
    "Round-trip test ले हाम्रो schema को values सही फर्किए कि हेर्छ; byte-identical output मात्र माग्दैन। "
    "असफल conversions मा source/output दुवै सुरक्षित छन् कि छुट्टै assert गर।",
    ("Only compare pretty printed text or test one valid example",
     "Compare canonical values and test meaningful rejection boundaries",
     "Equivalent documents can have different formatting; invalid inputs can reveal destructive save behaviour."),
    "Using the project validator, reject duplicate IDs, boolean scores, out-of-range scores and unknown fields. Confirm an empty table is valid.",
    PROJECT + clean(r'''
    bad_sets = [
        [{"id": "007", "name": "Sita", "score": 90},
         {"id": "007", "name": "Hari", "score": 80}],
        [{"id": "007", "name": "Sita", "score": True}],
        [{"id": "007", "name": "Sita", "score": 101}],
        [{"id": "007", "name": "Sita", "score": 90, "extra": 1}],
    ]
    for rows in bad_sets:
        try:
            validate_rows(rows)
        except ValueError:
            print("invalid rows rejected")
        else:
            raise AssertionError("invalid rows accepted")
    assert validate_rows([]) == []
    print("empty table accepted")
    '''),
    "Round-trip an empty table through each format and preserve a BOM-bearing CSV ID 007. Explain why an empty document and an empty table differ.",
    PROJECT + clean(r'''
    with tempfile.TemporaryDirectory() as folder:
        for kind in ("csv", "json", "xml"):
            path = Path(folder) / ("empty." + kind)
            path.write_text(render_rows([], kind), encoding="utf-8")
            assert read_rows(path, kind) == []
            print(kind, "empty table passed")
        path = Path(folder) / "bom.csv"
        path.write_bytes(b"\xef\xbb\xbfid,name,score\n007,Sita,90\n")
        print(read_rows(path, "csv")[0]["id"])
    '''),
    "Week 23 mastery: read/write CSV and JSON, validate nested shapes, select typed config APIs, parse XML/HTML appropriately, explain schema versioning, and build a conversion CLI with protected failure paths. Revisit any weak part before Week 24.",
    [
        ("Which CSV tool handles quoted delimiters?", "csv.reader/DictReader", "split(',') in every case", "json.loads", "The csv parser implements CSV quoting rules."),
        ("What is the s in dumps/loads useful for remembering?", "String-oriented JSON operations", "Secret encryption", "Schema validation", "The file-oriented pair is dump/load."),
        ("Are parsed JSON values automatically schema-valid?", "No", "Yes", "Only with indent", "Check types, fields, uniqueness and ranges separately."),
        ("Why is score or default risky?", "It discards valid zero.", "It always raises.", "It converts strings to int.", "Falsey values and missing values need not mean the same thing."),
        ("What must flattening define first?", "What one output row represents", "Only the output filename", "A regex for every tag", "Grain and parent relationships determine the projection."),
        ("Which INI method interprets true/false text?", "getboolean", "bool on any string", "getint", "Nonempty 'false' is truthy under ordinary bool."),
        ("Does tomllib write TOML?", "No; it is a reader.", "Yes, with dump.", "Only in binary mode.", "Writing requires a separately selected library."),
        ("Is a .env file encrypted secret storage?", "No", "Yes", "Only if named .env", "It is plaintext; keep real credentials out of public files and history."),
        ("How should missing XML elements be checked?", "element is None", "not element reliably in all versions", "len(element)==0 means absent", "Presence and childless-element truthiness are not the same."),
        ("What should happen before writing conversion output?", "Validate and render the complete supported data.", "Erase old output immediately.", "Ignore UTF-8 errors.", "Failure must not produce a misleading partial file or corrupt an old one."),
    ])

days["23.3"]["parts"][2]["sections"].insert(3, section("sh", "python -m pip install PyYAML",
    note="Optional YAML practice setup. Install once using your own Python environment; these examples then run locally. Do not install anything to read the offline page."))
days["23.3"]["parts"][3]["sections"].insert(3, section("sh", "python -m pip install python-dotenv",
    note="Optional .env practice setup. Only demo settings are used; never paste a real token into a public file."))
days["23.5"]["parts"][2]["sections"].append(section("sh",
    "python data_converter.py scores.csv scores.json --input-format csv --output-format json\npython data_converter.py --help",
    note="Save the complete project as data_converter.py in a practice folder and prepare its declared CSV header. Run from that folder; output must use a new filename."))
days["23.5"]["parts"][-1]["sections"].append(section("p",
    "Optional official references: https://docs.python.org/3.12/library/csv.html · https://docs.python.org/3.12/library/json.html · https://docs.python.org/3.12/library/configparser.html · https://docs.python.org/3.12/library/tomllib.html · https://docs.python.org/3.12/library/xml.etree.elementtree.html · https://pyyaml.org/wiki/PyYAMLDocumentation · https://bbc2.github.io/python-dotenv/. The full teaching is already included for offline reading."))


def write():
    target = ROOT / "study-hub.html"
    original = target.read_bytes().decode("utf-8")
    start = original.index("const DAY_TEACH = {")
    end = original.index("\n};\n\nconst REST_DAY", start)
    if any(('"' + key + '":') in original[start:end] for key in days):
        raise RuntimeError("Week 23 exists; refusing to overwrite.")
    addition = "\n".join(json.dumps(k) + ": " + json.dumps(v, ensure_ascii=False, indent=2) + "," for k, v in days.items())
    prefix = original[:end].rstrip()
    if not prefix.endswith(","):
        prefix += ","
    result = prefix + "\n" + addition + original[end:]
    temporary = target.with_suffix(".html.tmp")
    temporary.write_bytes(result.encode("utf-8"))
    temporary.replace(target)
    artifact = ROOT / "docs" / "python-week23-data-converter.py"
    artifact.write_text('"""Week 23 practice CLI. Python 3.11+, standard library only.\n'
        'Small local student tables; explicit version-2 schema and UTF-8 policy.\n'
        'Use a new destination filename. Not concurrent-write coordination.\n'
        '"""\n' + PROJECT + '\nif __name__ == "__main__":\n    sys.exit(main())\n', encoding="utf-8")
    (ROOT / "docs" / "python-week23-scores.csv").write_text(
        'id,name,score\n007,"सीता & Hari",90\n008,東京,80\n', encoding="utf-8")
    parts = [p for day in days.values() for p in day["parts"]]
    quizzes = sum(len(s["lesson"]["quiz"]) for p in parts for s in p["sections"] if s["t"] == "checkpoint")
    print(f"Added Week 23: 6 days, {len(parts)} parts, {len(parts)*2} practice prompts, {quizzes} questions, {executed} verified examples.")


if __name__ == "__main__":
    write()

