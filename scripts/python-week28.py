"""Author Week 28 additively; execute each output in an isolated practice folder."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap

ROOT = Path(__file__).resolve().parent.parent
DAYS = {f"28.{d}": {"parts": []} for d in range(6)}
EXECUTED = 0


def clean(code):
    return textwrap.dedent(code).strip() + "\n"


def output(code):
    global EXECUTED
    with tempfile.TemporaryDirectory(prefix="studyhub-w28-") as folder:
        run = subprocess.run([sys.executable, "-c", clean(code)], cwd=folder,
                             capture_output=True, encoding="utf-8", timeout=35,
                             env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    if run.returncode:
        raise RuntimeError(run.stderr + "\n" + code)
    EXECUTED += 1
    return run.stdout.replace("\r\n", "\n").rstrip()


def s(t, v=None, **extra):
    return {"t": t, **({"v": v} if v is not None else {}), **extra}


def add(day, title, goal, concepts, explanation, syntax, code, walk, mistake,
        task, solution, challenge, challenge_code, key, quizzes):
    parts = DAYS[f"28.{day}"]["parts"]
    index = len(parts)
    questions = []
    for n, (q, answer, wrong1, wrong2, why) in enumerate(quizzes):
        rotation = (index + n) % 3
        options = [answer, wrong1, wrong2]
        for _ in range(rotation):
            options.insert(0, options.pop())
        questions.append({"q": q, "options": options, "correct": rotation, "why": why})
    parts.append({"title": title, "sections": [
        s("h", title), s("key", "Learning objective: " + goal),
        *[s("new", name, note=note) for name, note in concepts],
        s("p", explanation), s("syn", syntax, note="Pattern first; run the complete example below."),
        s("code", clean(code)), s("out", output(code)), s("p", walk),
        s("mis", wrong=mistake[0], right=mistake[1], why=mistake[2]),
        s("ex", task, practiceId=f"28.{day}.{index}.build"),
        s("sol", code=clean(solution), out=output(solution), why="Build check: " + key),
        s("ex", "Mini challenge: " + challenge, practiceId=f"28.{day}.{index}.challenge"),
        s("sol", code=clean(challenge_code), out=output(challenge_code), why="Challenge check: " + key),
        s("try", q=quizzes[0][0], code="# Predict and explain before revealing.",
          a=quizzes[0][1], why=quizzes[0][4]),
        s("checkpoint", lesson={"id": f"course:28.{day}.{index}", "quiz": questions}), s("key", key),
    ]})


def lesson(day, title, goal, concepts, explanation, syntax, example, walk,
           wrong, right, reason, task, solution, challenge, challenge_code,
           takeaway, questions):
    """Keep the existing section renderer and durable practice/quiz identifiers."""
    add(day, title, goal, concepts, explanation, syntax, example, walk,
        (wrong, right, reason), task, solution, challenge, challenge_code,
        takeaway, questions)


lesson(0, "1. Series: values with labels",
    "Build a Series, read its labels and predict label-aligned arithmetic.",
    [("pandas; import pandas as pd", "pandas is a separately installed library for labeled tables. pd is its conventional alias. Use Python 3.11+ and pandas 3.x for this week's verified examples."),
     ("Series; index; name", "A Series is a one-dimensional labeled collection. index holds row labels; name describes the collection. Labels can be strings or numbers and need not be unique."),
     ("loc; to_dict; isna", "loc selects by label, not by position. Series.to_dict converts label/value pairs to a dictionary (duplicate labels would be lost). isna marks missing values; Day4 expands selection.")],
    "NumPy taught arrays and positions. pandas adds labels that carry meaning: a student's name or an order ID can identify a value. "
    "A Series contains both values and an index; its name is separate metadata. Arithmetic between two Series aligns matching labels, even when their order differs. "
    "A label present on only one side creates a missing result rather than guessing a partner. Labels are not guaranteed to be unique, so use dictionary output only in these unique-label examples. "
    "Install the practice libraries once with internet; the lessons and local examples then remain usable offline. The website displays examples; run Python in your own practice environment.",
    'pd.Series(values, index=labels, name="description")\nseries.loc["label"]\nseries.isna()',
    '''
    import pandas as pd
    hours = pd.Series([2, 3], index=["Asha", "Bina"], name="hours")
    extra = pd.Series([10, 20], index=["Bina", "Asha"])
    print(hours.to_dict())
    print("Asha:", hours.loc["Asha"])
    print("Aligned total:", (hours + extra).to_dict())
    ''',
    "Asha को 2 मा Asha कै 20 जोडियो। पहिलो position को 10 होइन। pandas मा labels ले matching गर्छन्; values को order मात्र हेरेर हिसाब नगर्नु।",
    "Assume Series addition always pairs positions", "Check indexes; arithmetic matches labels",
    "The left and right positions may refer to different people.",
    "Store Monday/Tuesday study minutes 30/45 in a named Series; add 5 minutes and print the result.",
    '''
    import pandas as pd
    minutes = pd.Series([30, 45], index=["Monday", "Tuesday"], name="minutes")
    print((minutes + 5).to_dict())
    print(minutes.name)
    ''',
    "Add Series whose labels only partly overlap. Print which result labels are missing, without inventing a value.",
    '''
    import pandas as pd
    a = pd.Series([1, 2], index=["A", "B"])
    b = pd.Series([10, 20], index=["B", "C"])
    print((a + b).isna().to_dict())
    print("B:", (a + b).loc["B"])
    ''',
    "Series arithmetic aligns labels. A missing partner is missing data, not automatically zero.",
    [("Series arithmetic normally matches what?", "Index labels", "Only positions", "Variable names", "Indexes determine alignment."),
     ("What is pd?", "An import alias", "A Python keyword", "A row label", "The alias is chosen in the import statement.")])

lesson(0, "2. DataFrames: three construction patterns",
    "Construct equivalent tables from columns, records and rows, then inspect their shape.",
    [("DataFrame", "A DataFrame is a two-dimensional labeled table. Each column is a Series and may have a different dtype; its rows share one index."),
     ("shape; columns; to_dict(orient='records')", "shape gives (row_count, column_count); columns holds column labels. records output creates one dictionary per row, without including the index."),
     ("equals", "equals compares shape, labels, corresponding values and dtypes. It is useful here for checking independently constructed small tables.")],
    "Choose the construction pattern that fits the source. A dictionary of equally long lists naturally represents columns. "
    "A list of dictionaries naturally represents records and can represent omitted fields as missing. A list of rows needs an explicit column list so that the numbers are understandable. "
    "A dictionary of lists is not itself a DataFrame: pandas supplies selection, alignment, per-column types and table operations. "
    "The default row labels are 0,1,..., but those labels are not permanent business identities. All three examples use the same column order and complete records, so equals is True.",
    'pd.DataFrame({"name": [...], "score": [...]})\npd.DataFrame([{"name": ..., "score": ...}])\npd.DataFrame(rows, columns=["name", "score"])',
    '''
    import pandas as pd
    a = pd.DataFrame({"name": ["Asha", "Bina"], "score": [80, 90]})
    b = pd.DataFrame([{"name": "Asha", "score": 80}, {"name": "Bina", "score": 90}])
    c = pd.DataFrame([["Asha", 80], ["Bina", 90]], columns=["name", "score"])
    print(a.shape, a.columns.tolist())
    print(a.to_dict(orient="records"))
    print(a.equals(b), a.equals(c))
    ''',
    "shape (2,2) को अर्थ दुई records र दुई columns हुन्। records output मा row index आउँदैन। नाम र score एउटै column मा मिसाउनु पर्दैन।",
    'pd.DataFrame({"name": ["Asha", "Bina"], "score": [80]})',
    'pd.DataFrame({"name": ["Asha", "Bina"], "score": [80, 90]})',
    "Ordinary column lists must have equal lengths; pandas cannot guess the missing student's score.",
    "Build the same two-book title/pages table with all three construction patterns and verify equality.",
    '''
    import pandas as pd
    a = pd.DataFrame({"title": ["Python", "Data"], "pages": [100, 150]})
    b = pd.DataFrame([{"title": "Python", "pages": 100}, {"title": "Data", "pages": 150}])
    c = pd.DataFrame([["Python", 100], ["Data", 150]], columns=["title", "pages"])
    print(a.equals(b) and b.equals(c))
    print(c.shape)
    ''',
    "Create records where one record has no score. Locate that missing field using isna, without filling it.",
    '''
    import pandas as pd
    df = pd.DataFrame([{"name": "Asha", "score": 80}, {"name": "Bina"}])
    print(df["score"].isna().tolist())
    print(df.shape)
    ''',
    "Choose columns, records or explicit rows according to the source; inspect shape before using the table.",
    [("What does shape (3,2) mean?", "3 rows and 2 columns", "2 rows and 3 columns", "6 columns", "The first dimension counts rows."),
     ("Does records output include the DataFrame index?", "No", "Always", "Only numeric indexes", "It outputs dictionaries of column/value pairs.")])

lesson(0, "3. Column types and honest missing values",
    "Keep IDs as text and represent missing integer values without calling them zero.",
    [("dtype; dtypes", "dtype is one Series' storage type; dtypes lists the type of every DataFrame column. A DataFrame does not require one common numerical dtype."),
     ("string; Int64; pd.NA", "Explicit string is pandas' nullable text dtype. Capital-I Int64 is a nullable integer dtype that accepts pd.NA; lowercase int64 cannot represent a missing integer in the same way."),
     ("notna; sum; count", "notna marks present values. Summing a Boolean mask counts True entries; count counts nonmissing observations. sum normally skips missing values, which is not a data-completeness guarantee.")],
    "A code such as 001 is an identifier, not the number one. Preserve it as text before numerical inference loses its leading zeros. "
    "A missing age means unknown; assigning zero would claim a known age of zero. Use nullable integer storage when integer values may be missing. "
    "pandas 3 changed default string inference, so these lessons explicitly request string where its missing-value behavior matters. "
    "Missing markers can differ across dtypes; use isna/notna rather than equality with None, NaN or pd.NA. When summarizing, report the number of observed values too. Week29 teaches repair decisions; this week observes them.",
    'pd.Series(["001", "002"], dtype="string")\npd.Series([20, pd.NA], dtype="Int64")\nseries.isna().sum()\nseries.count()',
    '''
    import pandas as pd
    df = pd.DataFrame({"id": pd.Series(["001", "002"], dtype="string"),
                       "age": pd.Series([20, pd.NA], dtype="Int64")})
    print(df["id"].tolist())
    print(str(df["id"].dtype), str(df["age"].dtype))
    print("Missing:", df["age"].isna().sum())
    print("Known:", df["age"].count())
    ''',
    "001 जस्ताको तस्तै बच्यो। दोस्रो age थाहा छैन, त्यसैले pd.NA हो। Missing र known count छुट्टै देखाउँदा report ले वास्तविक अवस्था बताउँछ।",
    'Store every missing age as 0', 'Use nullable Int64 and report missing counts',
    "Unknown is not zero. A false value changes means and filters.",
    "Create three text IDs and nullable integer scores [90, missing, 70]. Print missing flags and known-count.",
    '''
    import pandas as pd
    df = pd.DataFrame({"id": pd.Series(["007", "008", "009"], dtype="string"),
                       "score": pd.Series([90, pd.NA, 70], dtype="Int64")})
    print(df["id"].tolist())
    print(df["score"].isna().tolist())
    print(df["score"].count())
    ''',
    "Compare an all-missing integer Series' default sum with its observed count. Explain why that sum alone is misleading.",
    '''
    import pandas as pd
    scores = pd.Series([pd.NA, pd.NA], dtype="Int64")
    print("Default sum:", scores.sum())
    print("Observed:", scores.count())
    print("Require one observation:", scores.sum(min_count=1))
    ''',
    "Preserve identifiers as text. Choose nullable dtypes deliberately and report missingness alongside totals.",
    [("Which dtype accepts missing whole numbers explicitly?", "Int64", "int64 with no missing policy", "All IDs as float", "Capital-I Int64 is pandas' nullable integer type."),
     ("Does a default sum of zero prove observations exist?", "No", "Yes", "Only with text IDs", "Check count or require min_count=1.")])

lesson(0, "4. Labels, aliases and Copy-on-Write",
    "Distinguish two names for one table from a separate pandas object.",
    [("DataFrame.index; copy", "index stores row labels independently of row positions. copy() creates a separate DataFrame object; nested mutable Python objects inside object columns need extra care beyond this numeric example."),
     ("Copy-on-Write in pandas 3", "Derived Series/DataFrames behave independently when updated. A selected Series edit does not update its parent DataFrame. Two Python names bound to the same object still share every edit."),
     ("iloc; single-step loc assignment", "iloc selects zero-based positions. df.loc[row_label, column_label] = value updates that DataFrame directly. These appear now for the ownership experiment and are developed fully on Day4.")],
    "Do not transfer NumPy slice assumptions directly to pandas. In pandas 3, Copy-on-Write prevents changing a separately derived Series from silently changing its parent table. "
    "However, alias = df creates no separate object: both names still refer to the same DataFrame. df.copy() creates an independent table for the ordinary numeric values shown here. "
    "Labels such as 10 and 20 are not positions 10 and 20; iloc[0] means the first row while loc[10] means the row labeled 10. "
    "Keep transformations explicit and update the intended DataFrame in one loc operation. Avoid legacy chained-assignment tutorials when using pandas 3.",
    'alias = df\nindependent = df.copy()\nselected = df["score"]\nselected.iloc[0] = 99\ndf.loc[10, "score"] = 85',
    '''
    import pandas as pd
    df = pd.DataFrame({"score": [80, 90]}, index=[10, 20])
    selected = df["score"]
    selected.iloc[0] = 99
    print("Parent:", df["score"].tolist())
    print("Selected:", selected.tolist())
    alias = df
    alias.loc[10, "score"] = 85
    print("Same object:", alias is df)
    print("After direct edit:", df["score"].tolist())
    ''',
    "selected छुट्टै pandas object हो, उसको edit parent मा सरेन। alias भने उही object को अर्को नाम हो, त्यसैले alias बाट गरेको edit df मा देखियो।",
    'df["score"][0] = 99', 'df.loc[10, "score"] = 99',
    "Chained assignment does not update the parent under pandas 3 Copy-on-Write; 0 is also the wrong row label here.",
    "Copy a table, edit only its copy, then prove that the original numbers are unchanged.",
    '''
    import pandas as pd
    original = pd.DataFrame({"score": [50, 60]}, index=["A", "B"])
    changed = original.copy()
    changed.loc["A", "score"] = 100
    print(original["score"].tolist())
    print(changed["score"].tolist())
    ''',
    "For index [20,10], read the first score by position and the score with label 10 separately.",
    '''
    import pandas as pd
    df = pd.DataFrame({"score": [50, 90]}, index=[20, 10])
    print("First row:", df.iloc[0]["score"])
    print("Label 10:", df.loc[10, "score"])
    ''',
    "Use pandas 3 Copy-on-Write rules, but remember that Python aliases still identify the same object.",
    [("Does alias = df make an independent table?", "No", "Yes", "Only if indexes are integers", "It binds another name to the same object."),
     ("Does changing a selected Series update its parent in pandas 3?", "No", "Always", "Only with iloc", "Update the intended parent directly.")])

lesson(1, "1. CSV loading with a declared schema",
    "Load a local CSV while preserving IDs and controlling which tokens mean missing.",
    [("read_csv; StringIO", "read_csv reads delimited text into a DataFrame. StringIO presents our supplied text as an in-memory file, so this example needs no download."),
     ("dtype; keep_default_na; na_values", "dtype declares column types. keep_default_na=False disables pandas' default missing-word list. na_values=[''] marks empty fields missing while preserving literal text such as NA."),
     ("sep; usecols; encoding", "sep sets the delimiter, usecols chooses columns and encoding decodes a real text file. Use UTF-8 or UTF-8-SIG for supplied UTF-8/BOM files; a wrong encoding is not fixed by ignoring errors.")],
    "CSV stores text and separators, not an authoritative type schema. If you let pandas infer an ID like 001, it may become the number 1. "
    "Declare the ID type before reading. Also decide what missing means: the text NA could be a region code or a legitimate answer rather than a missing value. "
    "Here empty fields are missing, while NA is kept as text. Inspect shape, types and null counts immediately after loading. "
    "Quoted commas belong inside a field; do not replace read_csv with a naive split(','). All datasets in this week are fictional, small and included locally.",
    'pd.read_csv("students.csv", dtype={"id":"string","score":"Int64"},\n            keep_default_na=False, na_values=[""], encoding="utf-8-sig")',
    '''
    from io import StringIO
    import pandas as pd
    text = 'id,name,score,region\\n001,"Asha, Rai",80,NA\\n002,Bina,,NP\\n'
    df = pd.read_csv(StringIO(text), dtype={"id": "string", "score": "Int64", "region": "string"},
                     keep_default_na=False, na_values=[""])
    print(df["id"].tolist())
    print(df["name"].tolist())
    print(df["region"].tolist())
    print(df.shape, df["score"].isna().tolist())
    ''',
    "Quoted नाममा comma भए पनि एउटै field रह्यो। NA region हराएन। Score को खाली ठाउँ मात्रै missing भयो। Read गर्दा नै policy राख्नु, पछि lost zeros फर्काउन सकिँदैन।",
    'df = pd.read_csv(path)  # assume IDs and NA tokens are always inferred correctly',
    'Declare dtype and missing-token policy when reading',
    "Inference guesses types; it cannot know the meaning of your IDs or region codes.",
    "Load a semicolon-separated table with IDs 007/008. Select only id and minutes while preserving zeros.",
    '''
    from io import StringIO
    import pandas as pd
    df = pd.read_csv(StringIO("id;minutes;note\\n007;30;ok\\n008;45;ok\\n"),
                     sep=";", usecols=["id", "minutes"], dtype={"id": "string"})
    print(df.to_dict(orient="records"))
    ''',
    "Keep literal NULL as a text label but mark an empty label missing.",
    '''
    from io import StringIO
    import pandas as pd
    df = pd.read_csv(StringIO("label\\nNULL\\n\\\"\\\"\\n"), dtype={"label": "string"},
                     keep_default_na=False, na_values=[""])
    print(df["label"].isna().tolist())
    print(df.loc[0, "label"])
    ''',
    "Declare types and missing tokens before loading. Parsing successfully is not the same as interpreting the data correctly.",
    [("How do you preserve 001 as an ID?", "Read it as string", "Infer it as an integer", "Multiply by 100", "Numeric inference discards leading zeros."),
     ("Must the literal NA always mean missing?", "No; choose a policy", "Yes", "Only in CSV headers", "Some domains use NA as ordinary text.")])

lesson(1, "2. Excel workbooks and deliberate sheet selection",
    "Round-trip a small workbook and inspect one named sheet explicitly.",
    [("to_excel; read_excel; openpyxl", "to_excel writes a workbook; read_excel loads it. openpyxl is an additional engine used here for .xlsx files. Excel installation itself is not needed."),
     ("sheet_name; index=False", "sheet_name selects the intended worksheet. index=False prevents writing the pandas row index as an extra column."),
     ("TemporaryDirectory; Path", "These standard-library tools create an owned temporary folder and portable file paths. Only fictional workbook data is written; the folder is removed at the end.")],
    "An Excel workbook can contain many sheets, titles, formulas and formatted cells. A successful load of the first sheet does not prove it is the intended table. "
    "Choose sheet_name explicitly, check headers and verify shape. Preserve text IDs in both the source workbook and the read schema: if Excel already stored 001 as numeric 1, a text dtype cannot restore the lost zeros. "
    "Our fixture has one clean table with no formulas. Formula values may depend on a workbook's saved calculation cache, so do not treat pandas as an Excel calculation engine. "
    "This example creates its own workbook safely, then loads it using openpyxl.",
    'df.to_excel(path, sheet_name="Students", index=False, engine="openpyxl")\npd.read_excel(path, sheet_name="Students", dtype={"id":"string"}, engine="openpyxl")',
    '''
    import tempfile
    from pathlib import Path
    import pandas as pd
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "students.xlsx"
        source = pd.DataFrame({"id": ["001", "002"], "score": [80, 90]})
        source.to_excel(path, sheet_name="Students", index=False, engine="openpyxl")
        loaded = pd.read_excel(path, sheet_name="Students", dtype={"id": "string"}, engine="openpyxl")
        print(loaded.to_dict(orient="records"))
        print(loaded.shape)
    ''',
    "index=False ले अनावश्यक index column हटायो। Students sheet नै पढिएको छ। वास्तविक file मा sheet को नाम र header row पहिले जाँच्नु।",
    'pd.read_excel(path)  # assume first sheet is always the data',
    'pd.read_excel(path, sheet_name="Students", engine="openpyxl")',
    "A workbook may place instructions before the actual data sheet.",
    "Write a local Books sheet with two title/page records; read it and verify its column names and page total.",
    '''
    import tempfile
    from pathlib import Path
    import pandas as pd
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "books.xlsx"
        pd.DataFrame({"title": ["Python", "Data"], "pages": [100, 150]}).to_excel(
            path, sheet_name="Books", index=False, engine="openpyxl")
        df = pd.read_excel(path, sheet_name="Books", engine="openpyxl")
        print(df.columns.tolist(), int(df["pages"].sum()))
    ''',
    "Load a specific column from a named sheet and prove no pandas index column was written.",
    '''
    import tempfile
    from pathlib import Path
    import pandas as pd
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "table.xlsx"
        pd.DataFrame({"name": ["Asha"], "score": [80]}).to_excel(
            path, sheet_name="Scores", index=False, engine="openpyxl")
        df = pd.read_excel(path, sheet_name="Scores", usecols=["score"], engine="openpyxl")
        print(df.columns.tolist(), df["score"].tolist())
    ''',
    "Choose the sheet and schema explicitly. pandas reads workbook data; it does not recalculate Excel formulas.",
    [("Does openpyxl require the Excel desktop app?", "No", "Yes", "Only for small tables", "It is a Python workbook engine."),
     ("What does index=False do when exporting?", "Omits the pandas index column", "Deletes all workbook rows", "Disables sheet names", "Row labels are not exported as a data column.")])

lesson(1, "3. JSON orientation and local round trips",
    "Load record-oriented JSON without confusing its structure with a column-oriented document.",
    [("read_json; to_json; orient", "orient specifies the JSON layout. records represents a list of row dictionaries; columns represents column mappings. Agree on orientation before loading."),
     ("JSON null versus empty text", "JSON null expresses a missing value; an empty string remains text unless you deliberately convert it. File formats can encode missingness differently.")],
    "JSON is a container format, not one fixed table layout. A list of records maps naturally to rows, but a nested API response may wrap those records under another key. "
    "Do not pass an arbitrary nested response to read_json and assume it becomes the intended table. For a wrapper, parse JSON first and construct the DataFrame from the chosen record list. "
    "Use StringIO for literal JSON text and declare orient='records'. Explicit ID dtype protects text identifiers. "
    "A records export omits row labels; if those labels contain important identity, preserve identity as a regular column or choose another supported orientation.",
    'pd.read_json(StringIO(text), orient="records", dtype={"id":"string"})\ndf.to_json(orient="records")',
    '''
    from io import StringIO
    import pandas as pd
    text = '[{"id":"001","score":80},{"id":"002","score":null}]'
    df = pd.read_json(StringIO(text), orient="records", dtype={"id": "string"})
    print(df["id"].tolist())
    print(df["score"].isna().tolist())
    print(df.to_json(orient="records"))
    ''',
    "JSON null missing भयो, तर id text रह्यो। records मा table को index हुँदैन। Metadata पनि चाहियो भने format को contract छुट्टै बनाउनु।",
    'Assume every JSON document is already a flat list of rows',
    'Inspect the JSON structure and select the intended record list',
    "Nested wrappers and records have different shapes.",
    "Extract the items list from a wrapped JSON response and build a two-row DataFrame.",
    '''
    import json
    import pandas as pd
    payload = json.loads('{"items":[{"name":"Asha"},{"name":"Bina"}],"count":2}')
    df = pd.DataFrame(payload["items"])
    print(df["name"].tolist(), df.shape)
    ''',
    "Compare null and empty string in a JSON label column using explicit string dtype.",
    '''
    from io import StringIO
    import pandas as pd
    df = pd.read_json(StringIO('[{"label":null},{"label":""}]'),
                      orient="records", dtype={"label": "string"})
    print(df["label"].isna().tolist())
    print(df.loc[1, "label"] == "")
    ''',
    "Agree on JSON orientation and missing-value meaning; a nested document is not automatically a flat table.",
    [("What does records orientation represent?", "A list of row dictionaries", "Only row indexes", "An Excel sheet", "Each dictionary describes one row."),
     ("Is empty JSON text automatically null?", "No", "Always", "Only with IDs", "An empty string and null are different values.")])

lesson(1, "4. SQL results as DataFrames",
    "Load a bounded SQLite query with parameters and a deliberate order.",
    [("sqlite3.connect; in-memory database", "sqlite3 is Python's local database module. :memory: creates a temporary database for this example; no server or credentials are involved."),
     ("read_sql_query; read_sql", "read_sql_query loads query results into a DataFrame. read_sql is a convenience interface; for this SQLite SELECT example, read_sql_query makes the purpose explicit."),
     ("SQL params; ORDER BY; LIMIT", "params binds values instead of concatenating them into SQL text. ORDER BY defines result ordering; LIMIT bounds the number of returned rows.")],
    "SQL performs the query; pandas receives a table-shaped result. Filter and choose needed columns in the query when that avoids loading unnecessary rows. "
    "Without ORDER BY, a database result has no guaranteed business order. Give tied rows a secondary key when you need a reproducible report. "
    "Pass values through params rather than building SQL with user text. Values can be bound; table/column identifiers need a separate trusted allow-list if they ever become configurable. "
    "The fixture creates three fictional students in memory, queries two of them, and closes the connection in finally. SQL connection management belongs to the database layer, not DataFrame storage.",
    'pd.read_sql_query("SELECT id,score FROM students WHERE score >= ? ORDER BY score DESC,id LIMIT 10",\n                  connection, params=(70,), dtype={"id":"string"})',
    '''
    import sqlite3
    import pandas as pd
    con = sqlite3.connect(":memory:")
    try:
        con.execute("CREATE TABLE students (id TEXT, score INTEGER)")
        con.executemany("INSERT INTO students VALUES (?,?)", [("001", 80), ("002", 60), ("003", 90)])
        df = pd.read_sql_query("SELECT id,score FROM students WHERE score >= ? ORDER BY score DESC,id",
                               con, params=(70,), dtype={"id": "string"})
        print(df.to_dict(orient="records"))
    finally:
        con.close()
    ''',
    "70 SQL text मा जोडिएको होइन, bound parameter हो। ORDER BY ले report को क्रम स्पष्ट बनायो। SQLite connection अन्त्यमा बन्द गरियो।",
    'sql = "SELECT * FROM students WHERE name = \'" + user_name + "\'"',
    'Use WHERE name = ? with params=(user_name,)',
    "Concatenated text can change SQL meaning and breaks on quoted names.",
    "Query books costing at most 500, sorted by price then title, using a bound maximum.",
    '''
    import sqlite3
    import pandas as pd
    con = sqlite3.connect(":memory:")
    try:
        con.execute("CREATE TABLE books (title TEXT, price INTEGER)")
        con.executemany("INSERT INTO books VALUES (?,?)", [("Data", 600), ("Python", 400), ("Basics", 300)])
        df = pd.read_sql_query("SELECT title,price FROM books WHERE price <= ? ORDER BY price,title",
                               con, params=(500,))
        print(df.to_dict(orient="records"))
    finally:
        con.close()
    ''',
    "Safely query a name containing an apostrophe and confirm the correct row.",
    '''
    import sqlite3
    import pandas as pd
    con = sqlite3.connect(":memory:")
    try:
        con.execute("CREATE TABLE people (name TEXT)")
        con.execute("INSERT INTO people VALUES (?)", ("O'Neil",))
        df = pd.read_sql_query("SELECT name FROM people WHERE name = ?", con, params=("O'Neil",))
        print(df["name"].tolist())
    finally:
        con.close()
    ''',
    "Bind SQL values and define result order. Loading a query does not turn pandas into a database server.",
    [("Which keeps values separate from SQL syntax?", "Bound params", "String concatenation", "Renaming pd", "The database driver handles parameter values."),
     ("Does SELECT without ORDER BY promise a report order?", "No", "Always", "Only for ID columns", "Specify ordering whenever the report requires it.")])

lesson(2, "1. First inspection: shape, head, tail and info",
    "Identify table dimensions, column names and observed counts before analysis.",
    [("head; tail", "head(n) returns the first n rows; tail(n) returns the last n. They show samples of the current order, not a random or representative sample."),
     ("info; buf; memory_usage", "info prints a structural summary and normally returns None. buf redirects its text to a file-like object; memory_usage=False omits a version-dependent memory estimate.")],
    "Your first question is whether the loaded table matches the source you intended. Count rows and columns, inspect headers, and look at both ends. "
    "A neat first five rows does not prove every later row is valid. info exposes dtypes and non-null counts; inspect it directly instead of doing print(df.info()), which also prints its None return. "
    "Column labels can contain unexpected spaces or duplicates. An index might be a default row counter rather than an ID. "
    "Treat these checks as discovery, not cleaning. Keep a repeatable first-look routine so each new dataset gets the same basic questions.",
    'df.shape\ndf.columns.tolist()\ndf.head(2)\ndf.tail(2)\ndf.info(show_counts=True)',
    '''
    from io import StringIO
    import pandas as pd
    df = pd.DataFrame({"id": pd.Series(["001", "002", "003"], dtype="string"),
                       "score": pd.Series([80, pd.NA, 90], dtype="Int64")})
    print("Shape:", df.shape)
    print("First:", df.head(1)["id"].tolist())
    print("Last:", df.tail(1)["id"].tolist())
    buf = StringIO()
    df.info(buf=buf, show_counts=True, memory_usage=False)
    print("Info has non-null counts:", "non-null" in buf.getvalue())
    print("Observed:", df.count().to_dict())
    ''',
    "First र last ले अहिलेको order का ends देखाउँछन्, random sample होइनन्। info structural check हो; missing score भएर score count दुई मात्रै आयो।",
    'print(df.info())  # expect a reusable DataFrame',
    'df.info(); use df.shape, df.dtypes and df.count() for structured results',
    "info prints a summary and returns None, not a new table.",
    "Inspect a three-row inventory's shape, headers, first item and last item.",
    '''
    import pandas as pd
    df = pd.DataFrame({"item": ["pen", "book", "bag"], "stock": [10, 5, 2]})
    print(df.shape, df.columns.tolist())
    print(df.head(1)["item"].tolist(), df.tail(1)["item"].tolist())
    ''',
    "Demonstrate that head(5) on a two-row table does not create extra records.",
    '''
    import pandas as pd
    df = pd.DataFrame({"score": [80, 90]})
    print(df.head(5).shape)
    print(df.tail(1)["score"].tolist())
    ''',
    "Inspect dimensions, headers, dtypes and observed counts. Head/tail are order-based previews, not validation.",
    [("Is head a representative random sample?", "No", "Always", "Only when n=5", "It takes the first rows in current order."),
     ("What does info normally return?", "None", "A new DataFrame", "The row count", "Its main job is printing structural information.")])

lesson(2, "2. Numeric describe and missingness denominators",
    "Interpret count, mean and spread without forgetting missing or absent observations.",
    [("describe", "For numerical columns, describe reports nonmissing count, mean, sample standard deviation, min, quartiles and max. Text summaries use different fields."),
     ("isna().sum; missing percentage", "isna().sum() counts missing cells per column. Divide by total row count for column missing percentage; an empty table has no meaningful denominator."),
     ("std: sample versus population", "pandas' usual std/describe std uses ddof=1. Week27 NumPy std defaulted to ddof=0. One observation has no defined sample standard deviation.")],
    "Descriptive statistics are a summary of observed values, not a certificate of data quality. A mean of 85 might describe two scores while a third score is missing. "
    "Report total rows and observed counts together. A column's missing percentage uses all rows as its denominator; using only present rows answers a different question. "
    "An empty table needs an explicit no-data result instead of division by zero or a misleading zero-percent claim. "
    "Remember the default standard-deviation difference from NumPy. Numeric IDs can accidentally appear in describe; numerical storage does not prove a field is meaningful to average.",
    'df[["score"]].describe()\nmissing = df.isna().sum()\npercentage = missing / len(df) * 100  # only when rows > 0',
    '''
    import pandas as pd
    df = pd.DataFrame({"score": pd.Series([80, 90, pd.NA], dtype="Int64")})
    summary = df["score"].describe()
    print("Rows:", len(df), "Observed:", int(summary["count"]))
    print("Mean:", float(summary["mean"]))
    print("Missing %:", round(float(df["score"].isna().sum()) / len(df) * 100, 2))
    print("Sample std:", round(float(summary["std"]), 2))
    ''',
    "Mean दुई known scores बाट आयो। Missing percentage भने तीनै rows को आधारमा 33.33% भयो। NumPy र pandas का std defaults एउटै सम्झिनु हुँदैन।",
    'missing / nonmissing * 100  # claim percentage of all rows',
    'missing / total_rows * 100, with an explicit empty-table policy',
    "The denominator defines the meaning of a percentage.",
    "For four scores [10,20,missing,missing], report row count, observed mean and missing percentage.",
    '''
    import pandas as pd
    scores = pd.Series([10, 20, pd.NA, pd.NA], dtype="Int64")
    print(len(scores), scores.count(), float(scores.mean()))
    print(float(scores.isna().sum()) / len(scores) * 100)
    ''',
    "Profile missingness for an empty table without claiming a measurable missing percentage.",
    '''
    import pandas as pd
    df = pd.DataFrame({"score": pd.Series([], dtype="Int64")})
    rows = len(df)
    missing_percent = None if rows == 0 else float(df["score"].isna().sum()) / rows * 100
    print("Rows:", rows, "Missing percentage:", missing_percent)
    ''',
    "Every statistic needs its observed count, denominator and convention; empty data is not a measured zero.",
    [("What denominator gives missing percentage of rows?", "Total row count", "Only present rows", "Number of columns", "Each row is a possible observation."),
     ("Which ddof does pandas std normally use?", "1", "0", "The column count", "Its default is sample standard deviation.")])

lesson(2, "3. Categories: counts, unique values and missing labels",
    "Count category frequencies and distinguish missing observations from unused labels.",
    [("value_counts; normalize; dropna", "value_counts counts category occurrences. dropna=False includes missing values. normalize=True reports proportions under the chosen missing policy."),
     ("unique; nunique", "unique returns distinct observed values in appearance order. nunique counts distinct values and normally excludes missing values; dropna=False includes them."),
     ("duplicated", "duplicated marks repeated rows (after their first occurrence by default). Repeated categories alone are not necessarily duplicate records.")],
    "A frequency table answers how often a category occurs. Decide whether missing observations belong in its denominator before comparing proportions. "
    "By default value_counts excludes missing values, so a two-thirds proportion among known regions may differ from a one-half proportion among all records. "
    "unique preserves appearance order; it does not sort categories. nunique counts distinct values under a missing policy. "
    "A category repeated many times is often expected. Duplicated rows are a different question, and even identical rows may represent valid repeated events unless a business key says otherwise.",
    'series.value_counts(dropna=False)\nseries.value_counts(normalize=True, dropna=False)\nseries.nunique(dropna=False)\ndf.duplicated().sum()',
    '''
    import pandas as pd
    regions = pd.Series(["NP", "JP", "NP", pd.NA], dtype="string")
    print("Known counts:", regions.value_counts().to_dict())
    print("NP among known:", round(float(regions.value_counts(normalize=True)["NP"]), 3))
    print("NP among all:", float(regions.value_counts(normalize=True, dropna=False)["NP"]))
    print("Distinct known:", regions.nunique(), "Including missing:", regions.nunique(dropna=False))
    ''',
    "Known regions मात्रै गन्दा NP को share 2/3 भयो। Missing समेत चार rows गन्दा 2/4 भयो। कुन population को proportion हो, report मा खुलाउनु।",
    'Treat repeated region values as duplicated people',
    'Check full rows or a declared business key separately from category frequencies',
    "Several people can legitimately share the same region.",
    "Count pen/book/pen/bag frequencies and print their appearance-order unique values.",
    '''
    import pandas as pd
    items = pd.Series(["pen", "book", "pen", "bag"], dtype="string")
    print(items.value_counts().to_dict())
    print(items.unique().tolist())
    ''',
    "Find repeated complete records while keeping two people with the same region as distinct.",
    '''
    import pandas as pd
    df = pd.DataFrame({"id": ["001", "002", "001"], "region": ["NP", "NP", "NP"]})
    print(df.duplicated().tolist())
    print("Repeated after first:", int(df.duplicated().sum()))
    ''',
    "State whether missing categories count. Repeated categories and duplicated records are different checks.",
    [("Does value_counts include missing values by default?", "No", "Always", "Only for string", "Use dropna=False when that is the desired policy."),
     ("Does unique sort its result alphabetically?", "No", "Always", "Only for regions", "It returns values in order of appearance.")])

lesson(2, "4. A reusable first-look function",
    "Combine structural checks in one nonmutating function with an explicit empty policy.",
    [("Profiling contract", "A profiler observes and reports the table; it does not silently fill, delete or reinterpret records. State its missing and duplicate policies."),
     ("dtype-to-text conversion", "str(dtype) provides a readable type name. JSON reports need ordinary Python int/float/None values rather than every pandas or NumPy scalar.")],
    "Turn the repeated checks into a function you can call on each newly loaded table. The function should return structured results rather than only printing a decorative summary. "
    "This first version reports shape, per-column types, missing counts and percentages, and duplicated full rows after the first. It does not edit the source. "
    "Empty input returns None for percentages, because no rows exist to estimate them. Column names must be unique for a dictionary-based report; otherwise two columns could overwrite one key. "
    "Day6 extends this core into a bounded CSV command-line tool. Keep interpretation separate from repair: a suspicious column deserves inspection, not an automatic destructive fix.",
    'def first_look(df):\n    # require unique columns\n    # return shape, dtypes, missing counts/percentages and duplicate count',
    '''
    import pandas as pd
    def first_look(df):
        if not df.columns.is_unique:
            raise ValueError("Require unique column labels")
        rows = len(df)
        return {"shape": list(df.shape),
                "dtypes": {str(c): str(df[c].dtype) for c in df.columns},
                "missing": {str(c): int(df[c].isna().sum()) for c in df.columns},
                "missing_percent": {str(c): None if rows == 0 else round(float(df[c].isna().sum()) / rows * 100, 2) for c in df.columns},
                "duplicate_rows_after_first": int(df.duplicated().sum())}
    df = pd.DataFrame({"score": pd.Series([80, pd.NA, 80], dtype="Int64")})
    before = df.copy()
    report = first_look(df)
    print(report)
    print("Unchanged:", df.equals(before))
    ''',
    "Function ले report फर्कायो; source बदलिएको छैन। Percent र duplicate count को policy पनि स्पष्ट छ। पछि cleaning गर्दा यही raw report सँग तुलना गर्न सकिन्छ।",
    'Fill missing values inside first_look without asking what they mean',
    'Report missingness first; keep repair in a separate, deliberate operation',
    "Profiling must not secretly change the data being diagnosed.",
    "Write a small function returning rows, columns and total missing cells for any DataFrame.",
    '''
    import pandas as pd
    def dimensions_and_missing(df):
        return {"rows": len(df), "columns": len(df.columns),
                "missing_cells": int(df.isna().sum().sum())}
    df = pd.DataFrame({"a": [1, None], "b": [None, 2]})
    print(dimensions_and_missing(df))
    ''',
    "Reject duplicate column labels before creating a dictionary-based report.",
    '''
    import pandas as pd
    df = pd.DataFrame([[1, 2]], columns=["score", "score"])
    try:
        if not df.columns.is_unique:
            raise ValueError("Require unique column labels")
    except ValueError as error:
        print(error)
    ''',
    "A useful first-look function has explicit policies, structured output and no source mutation.",
    [("Should a profiler silently repair its source?", "No", "Always", "Only missing values", "Observation and repair need separate decisions."),
     ("Why reject duplicate labels before dictionary reporting?", "Keys could overwrite each other", "They always crash Python", "They mean missing rows", "A mapping cannot keep two identical keys separately.")])

lesson(3, "1. One column, several columns and result shape",
    "Choose Series or DataFrame output deliberately and avoid ambiguous duplicate labels.",
    [("df['column'] versus df[['column']]", "For a unique column label, one label returns a Series; a list of labels returns a DataFrame even when the list contains one label."),
     ("Column order; KeyError", "A list specifies the order of selected columns. An unknown column label raises KeyError; inspect columns rather than quietly substituting the wrong field.")],
    "Before selecting rows, be precise about columns. df['score'] normally gives one Series with shape (rows,). df[['score']] keeps a table with shape (rows,1). "
    "That difference matters when a downstream function expects two dimensions or named columns. A list such as ['score','name'] also specifies the resulting order. "
    "The usual one-label rule assumes the column label is unique; duplicate column labels can make selection return a DataFrame unexpectedly. "
    "Inspect df.columns and require uniqueness for predictable beginner workflows. Selection asks for actual labels, including their capitalization and spaces.",
    'series = df["score"]\ntable = df[["score"]]\nordered = df[["score", "name"]]',
    '''
    import pandas as pd
    df = pd.DataFrame({"name": ["Asha", "Bina"], "score": [80, 90]})
    a, b = df["score"], df[["score"]]
    print(type(a).__name__, a.shape)
    print(type(b).__name__, b.shape)
    print(df[["score", "name"]].columns.tolist())
    ''',
    "एक bracket मा column name दिँदा Series आयो। List दिएपछि एक column भए पनि DataFrame रह्यो। Shape बुझ्दा पछिका operations सजिला हुन्छन्।",
    'Assume df["score"] and df[["score"]] always have identical shape',
    'Choose a Series or one-column DataFrame to fit the operation',
    "One-dimensional and two-dimensional results have different contracts.",
    "Select name and minutes in that order from a table whose original columns are minutes/name/id.",
    '''
    import pandas as pd
    df = pd.DataFrame({"minutes": [30, 45], "name": ["Asha", "Bina"], "id": ["001", "002"]})
    selected = df[["name", "minutes"]]
    print(selected.columns.tolist(), selected.shape)
    ''',
    "Catch an unknown-column request and print the available columns rather than guessing a substitute.",
    '''
    import pandas as pd
    df = pd.DataFrame({"score": [80]})
    try:
        print(df["scores"])
    except KeyError:
        print("Available:", df.columns.tolist())
    ''',
    "Selection has a shape contract. Unique labels make Series-versus-DataFrame behavior predictable.",
    [("With unique columns, what is df[['score']]?", "A DataFrame", "Always a scalar", "A Series", "A label list preserves table shape."),
     ("Which determines selected-column order?", "The supplied label list", "The values' size", "Alphabetical sorting automatically", "pandas uses the requested order.")])

lesson(3, "2. loc labels versus iloc positions",
    "Predict scalar, row and table selections and the two slice endpoint rules.",
    [("loc[row_selector, column_selector]", "loc selects row and column labels. A matching scalar pair usually returns a scalar; lists preserve a table. Label slices include both endpoints when present."),
     ("iloc[row_positions, column_positions]", "iloc selects zero-based integer positions. Its slices exclude the stop, like ordinary Python slicing. Integer row labels do not change this rule.")],
    "The most common selection error is treating an integer label as a position. In a table indexed [10,20,30], loc[20] asks for label20 while iloc[1] asks for the second row. "
    "They happen to identify the same row here, but an order change would change the positional result. Use lists on both axes when you need a DataFrame. "
    "A label slice loc[10:20] includes both labels on this ordered unique index; iloc[0:2] contains positions0 and1 and excludes2. "
    "For unsorted or duplicate indexes, label slicing can be ambiguous or fail; prefer explicit label lists until you understand those cases. Do not treat temporary row positions as stable student IDs.",
    'df.loc[20, "score"]\ndf.loc[[10,20], ["name","score"]]\ndf.loc[10:20, ["score"]]\ndf.iloc[0:2, [1]]',
    '''
    import pandas as pd
    df = pd.DataFrame({"name": ["Asha", "Bina", "Chandra"], "score": [80, 90, 70]}, index=[10, 20, 30])
    print("Label:", df.loc[20, "score"])
    print("Position:", df.iloc[1, 1])
    print("loc rows:", df.loc[10:20, ["score"]].index.tolist())
    print("iloc rows:", df.iloc[0:2, [1]].index.tolist())
    ''',
    "loc[20] मा 20 label हो। iloc[1] मा 1 दोस्रो row को position हो। यो उदाहरणमा दुवैले एउटै row पाए, तर नियम फरक हुन्।",
    'df.loc[0]  # assume first row when labels are 10,20,30',
    'df.iloc[0] for first position; df.loc[10] for label 10',
    "loc does not interpret an integer as an offset.",
    "With labels [30,10,20], select label10 and the last row's score separately.",
    '''
    import pandas as pd
    df = pd.DataFrame({"score": [70, 80, 90]}, index=[30, 10, 20])
    print("Label10:", df.loc[10, "score"])
    print("Last position:", df.iloc[-1, 0])
    ''',
    "Preserve table shape while selecting just label20 and column score.",
    '''
    import pandas as pd
    df = pd.DataFrame({"score": [80, 90]}, index=[10, 20])
    selected = df.loc[[20], ["score"]]
    print(type(selected).__name__, selected.shape)
    print(selected.to_dict(orient="records"))
    ''',
    "loc names labels and includes slice endpoints; iloc names positions and excludes the stop.",
    [("What does loc[10] mean?", "Label 10", "Always the eleventh row", "First ten rows", "Integer labels are still labels."),
     ("Does iloc[0:2] include position2?", "No", "Yes", "Only with string labels", "Positional slices follow Python's exclusive stop.")])

lesson(3, "3. Boolean filters and missing decisions",
    "Combine conditions with parenthesized operators and choose how unknown values affect selection.",
    [("&; |; ~ on masks", "& combines element-wise AND, | combines OR and ~ negates Boolean masks. Parenthesize comparisons; Python and/or do not combine whole pandas Series element-wise."),
     ("isin; between; fillna on a mask", "isin tests membership; between checks a numeric interval (both endpoints by default). fillna(False) explicitly excludes unknown decisions without replacing missing source values."),
     ("Mask alignment", "A Boolean Series aligns by index when used with loc. Build the mask from the same DataFrame to avoid selecting the wrong rows or an unalignable mask error.")],
    "A filter is a Boolean decision per row. First write each comparison separately, then combine the decisions. For nullable columns, a comparison against a missing value may itself be unknown. "
    "This lesson excludes unknown scores explicitly using mask.fillna(False); it does not pretend the score equals zero. Missing comparisons therefore remain visible in the source table. "
    "isin is clearer than many repeated equality comparisons. between states a range directly, but you still need a missing policy. "
    "Use masks with the same row labels as the table. A bare Python list of True/False is positional, while a Boolean Series can align labels.",
    'mask = (df["score"] >= 80) & df["region"].isin(["NP","JP"])\nselected = df.loc[mask.fillna(False), ["id","score"]]',
    '''
    import pandas as pd
    df = pd.DataFrame({"id": ["001", "002", "003", "004"], "region": ["NP", "US", "JP", "NP"],
                       "score": pd.Series([80, 95, pd.NA, 90], dtype="Int64")})
    mask = (df["score"] >= 80) & df["region"].isin(["NP", "JP"])
    print("Unknown decisions:", mask.isna().tolist())
    print(df.loc[mask.fillna(False), "id"].tolist())
    print("Source still missing:", df["score"].isna().tolist())
    ''',
    "Missing score को decision unknown थियो। filter मा exclude गरियो, source score बदलिएको छैन। Practice मा conditions छुट्टाछुट्टै लेखेर result जाँच्नु।",
    '(df["score"] >= 80) and (df["region"] == "NP")',
    '(df["score"] >= 80) & (df["region"] == "NP")',
    "Python and asks for one truth value; a Series contains many row decisions.",
    "Select score80 through90 inclusive, excluding missing scores explicitly.",
    '''
    import pandas as pd
    df = pd.DataFrame({"id": ["A", "B", "C", "D"],
                       "score": pd.Series([79, 80, 90, pd.NA], dtype="Int64")})
    mask = df["score"].between(80, 90).fillna(False)
    print(df.loc[mask, "id"].tolist())
    ''',
    "Select NP students OR students scoring at least90, then separately show missing-score IDs.",
    '''
    import pandas as pd
    df = pd.DataFrame({"id": ["A", "B", "C"], "region": ["NP", "US", "JP"],
                       "score": pd.Series([60, 95, pd.NA], dtype="Int64")})
    mask = ((df["region"] == "NP") | (df["score"] >= 90)).fillna(False)
    print(df.loc[mask, "id"].tolist())
    print("Missing:", df.loc[df["score"].isna(), "id"].tolist())
    ''',
    "Filter with parenthesized element-wise conditions, aligned masks and an explicit unknown-value policy.",
    [("Which operator combines row-wise AND?", "&", "and", "+", "Use & and parentheses around comparisons."),
     ("Does fillna(False) on a separate mask replace missing source scores?", "No", "Always", "Only for integers", "It changes the decision mask, not the score column.")])

lesson(3, "4. Ten selection questions and trusted query expressions",
    "Answer ten concrete table questions and use query only with a trusted expression.",
    [("query; @variable; engine", "query evaluates a trusted expression string against columns. @name refers to a supplied local variable. engine='python' avoids needing numexpr for these small examples."),
     ("Query expression trust", "query can evaluate code; never feed it arbitrary user-provided expressions. For configurable beginner filters, validate values and use direct Boolean comparisons.")],
    "Practice selection until you can translate a question into labels, positions or a mask without guessing. Our ten questions ask for: "
    "(1) IDs; (2) names/scores; (3) first row; (4) labelb; (5) scores>=80; (6) NP rows; "
    "(7) NP and score>=80; (8) NP or score>=90; (9) names at positions1:3; (10) score80..90 inclusive. "
    "The example uses a complete nonmissing numeric table so query is easy to read. Boolean masks remain the clearer choice when you need explicit nullable policies. "
    "query is an optional expression interface, not a security boundary or a way to execute any text typed into the website.",
    'threshold = 80\ndf.query("score >= @threshold and region == \'NP\'", engine="python")\n# expression is written by us, not obtained from user input',
    '''
    import pandas as pd
    df = pd.DataFrame({"id": ["001", "002", "003"], "name": ["Asha", "Bina", "Chandra"],
                       "score": [80, 90, 70], "region": ["NP", "JP", "NP"]}, index=["a", "b", "c"])
    threshold = 80
    result = df.query("score >= @threshold and region == 'NP'", engine="python")
    print(result["id"].tolist())
    print("Row b:", df.loc["b", "name"])
    ''',
    "Expression हामीले लेखेको trusted string हो। Threshold value मात्र बदलिएको छ। मनपरी input string लाई query मा नपठाउनु।",
    'df.query(input("Enter any expression: "))',
    'Use a trusted fixed expression or validated values in Boolean comparisons',
    "query expressions can evaluate code; arbitrary user expressions are not safe data.",
    "Answer all ten listed selection questions on the supplied table. Predict each result before looking at the solution.",
    '''
    import pandas as pd
    df = pd.DataFrame({"id": ["001", "002", "003"], "name": ["Asha", "Bina", "Chandra"],
                       "score": [80, 90, 70], "region": ["NP", "JP", "NP"]}, index=["a", "b", "c"])
    print("1:", df["id"].tolist())
    print("2:", df[["name", "score"]].to_dict(orient="records"))
    print("3:", df.iloc[0]["name"])
    print("4:", df.loc["b", "name"])
    print("5:", df.loc[df["score"] >= 80, "id"].tolist())
    print("6:", df.loc[df["region"] == "NP", "id"].tolist())
    print("7:", df.loc[(df["region"] == "NP") & (df["score"] >= 80), "id"].tolist())
    print("8:", df.loc[(df["region"] == "NP") | (df["score"] >= 90), "id"].tolist())
    print("9:", df.iloc[1:3]["name"].tolist())
    print("10:", df.loc[df["score"].between(80, 90), "id"].tolist())
    ''',
    "Use a fixed query with threshold85 and compare its IDs with a direct Boolean filter.",
    '''
    import pandas as pd
    df = pd.DataFrame({"id": ["A", "B", "C"], "score": [80, 90, 70]})
    threshold = 85
    a = df.query("score >= @threshold", engine="python")["id"].tolist()
    b = df.loc[df["score"] >= threshold, "id"].tolist()
    print(a, a == b)
    ''',
    "Translate the question first. Use query only for trusted expressions; handle missing decisions explicitly with masks.",
    [("What does @threshold mean inside query?", "A local variable value", "A column always named threshold", "A row index", "The @ prefix refers to the Python variable."),
     ("Should arbitrary user expressions go into query?", "No", "Always", "Only with engine='python'", "Changing engine does not make untrusted expressions safe.")])

lesson(4, "1. Five derived columns using vectorized operations",
    "Derive useful columns while preserving raw observations and naming each operation.",
    [("Vectorized Series arithmetic; round", "Arithmetic combines entire columns, aligned by index. round(n) controls displayed/computed decimal rounding; floating arithmetic is not an exact-money accounting engine."),
     ("astype; str.upper", "astype converts to a chosen dtype. The str accessor provides element-wise text operations such as upper; nullable string operations retain missing values."),
     ("Derived column", "A derived column records a calculation from source columns. Keep raw inputs alongside it so assumptions and mistakes can be traced.")],
    "Prefer built-in column operations for ordinary arithmetic and text transformations. You do not need a loop or a Python callback to multiply each row's price by its quantity. "
    "We derive subtotal, tax, total, an expensive flag and an uppercase category. The fictional tax rate is a teaching parameter, not real tax advice. "
    "Use whole currency units here; for real accounting choose a deliberate exact representation and rounding policy. Vectorized floating arithmetic alone does not solve money precision. "
    "A new column should have an understandable name and definition. Leave price and quantity unchanged so every derived value can be explained and checked.",
    'df["subtotal"] = df["price"] * df["quantity"]\ndf["tax"] = (df["subtotal"] * rate).round(2)\ndf["total"] = df["subtotal"] + df["tax"]',
    '''
    import pandas as pd
    df = pd.DataFrame({"price": [100, 200], "quantity": [2, 3], "category": ["book", "pen"]})
    df["subtotal"] = df["price"] * df["quantity"]
    df["tax"] = (df["subtotal"] * 0.10).round(2)
    df["total"] = df["subtotal"] + df["tax"]
    df["expensive"] = df["total"] > 500
    df["category_upper"] = df["category"].astype("string").str.upper()
    print(df[["subtotal", "tax", "total", "expensive", "category_upper"]].to_dict(orient="records"))
    print("Raw prices:", df["price"].tolist())
    ''',
    "प्रत्येक row को price र quantity multiply भयो। Raw price बचेकाले calculation फेरि जाँच्न सकिन्छ। Simple arithmetic मा apply चाहिँदैन।",
    'Overwrite price with total and forget the source',
    'Keep price/quantity and add named derived columns',
    "Losing raw inputs makes errors and policy changes harder to trace.",
    "Add study hours and target-met columns from minutes [30,90,120], using a60-minute target.",
    '''
    import pandas as pd
    df = pd.DataFrame({"minutes": [30, 90, 120]})
    df["hours"] = df["minutes"] / 60
    df["target_met"] = df["minutes"] >= 60
    print(df.to_dict(orient="records"))
    ''',
    "Create uppercase nullable names and prove a missing name stays missing.",
    '''
    import pandas as pd
    df = pd.DataFrame({"name": pd.Series(["Asha", pd.NA], dtype="string")})
    df["upper"] = df["name"].str.upper()
    print(df.loc[0, "upper"])
    print(df["upper"].isna().tolist())
    ''',
    "Prefer built-in column operations, name derived values clearly and preserve the raw data.",
    [("What pairs rows in Series arithmetic?", "Index labels", "Only the first values", "Column text length", "Column Series align on their row indexes."),
     ("Must simple column multiplication use apply?", "No", "Always", "Only with quantities", "Built-in multiplication is already element-wise.")])

lesson(4, "2. Assignment alignment: labels are not decoration",
    "Predict assignment from a Series versus a list and handle unmatched labels deliberately.",
    [("Series assignment alignment", "Assigning a Series to a DataFrame column matches row labels, not source positions. An unmatched target row becomes missing."),
     ("List assignment", "A plain list has no index labels; assignment is positional and its length must match the target rows. Use this only when positional matching is genuinely intended."),
     ("reindex", "reindex conforms a Series to a requested index, introducing missing values for absent labels. It makes intended alignment visible but does not validate business identity.")],
    "Alignment affects assignment as well as arithmetic. A shuffled Series of bonuses can still match people correctly if its labels are correct. "
    "Converting it to a list too early discards those labels and may attach bonuses to the wrong people. Conversely, a default-indexed Series assigned to a table indexed by names has no matching names and produces missing values. "
    "Decide whether matching should be by identity or position before assignment. reindex makes the requested label order explicit and exposes absent entries. "
    "For a real dataset, validate uniqueness and expected identity coverage; matching labels alone cannot detect a mislabeled source.",
    'df["bonus"] = bonus_series  # label matching\ndf["positional"] = values_list  # position matching\naligned = bonus_series.reindex(df.index)',
    '''
    import pandas as pd
    df = pd.DataFrame({"score": [80, 90]}, index=["A", "B"])
    bonus = pd.Series([20, 10], index=["B", "A"])
    df["bonus"] = bonus
    df["positional"] = [20, 10]
    print(df.to_dict(orient="index"))
    print("Aligned bonus:", bonus.reindex(df.index).tolist())
    ''',
    "Bonus मा B पहिले भए पनि A ले A कै 10 पायो। List मा labels नभएकाले पहिलो row ले पहिलो value पायो। कुन matching चाहिएको हो पहिले तय गर्नु।",
    'df["bonus"] = pd.Series([10,20])  # assume named rows match positions',
    'Give the Series matching labels, or use a deliberate length-checked list',
    "The default 0/1 labels do not match named rows A/B.",
    "Assign scores with source labels B/A to a target indexed A/B and print the correctly aligned scores.",
    '''
    import pandas as pd
    df = pd.DataFrame(index=["A", "B"])
    scores = pd.Series([90, 80], index=["B", "A"])
    df["score"] = scores
    print(df["score"].tolist())
    ''',
    "Assign a Series containing only labelA to rowsA/B. Identify the unmatched row without filling it.",
    '''
    import pandas as pd
    df = pd.DataFrame(index=["A", "B"])
    df["bonus"] = pd.Series([10], index=["A"], dtype="Int64")
    print(df["bonus"].isna().to_dict())
    ''',
    "Series assignment matches labels; list assignment matches positions. Preserve identity until matching is complete.",
    [("What does assigning a Series match?", "Row labels", "Only source order", "Dictionary size", "The Series index aligns to the DataFrame index."),
     ("What happens to an unmatched target label?", "Its new value is missing", "It is silently deleted", "It receives the last value", "No source value exists for that label.")])

lesson(4, "3. map and apply: choose the right level",
    "Distinguish mapping individual values from row/column callbacks and simpler vectorized operations.",
    [("Series.map", "map replaces each value using a dictionary or callable. With a dictionary, an unmapped key becomes missing; report that instead of claiming every code was recognized."),
     ("DataFrame.apply; axis=1 versus axis=0", "apply passes each row Series when axis=1, or each column Series when axis=0, to a callback. This is different from NumPy reduction-axis examples and can be slower than built-in operations."),
     ("Series.apply; pure callback", "Series.apply commonly calls a function on individual values. Keep callbacks free of mutations to the objects passed to them; prefer built-in arithmetic for simple formulas.")],
    "Use map when each code needs one replacement label. Use apply when a custom function genuinely needs a row or a column that cannot be expressed clearly through built-in operations. "
    "For price times quantity, direct vectorized multiplication is simpler and usually faster than apply(axis=1). "
    "With DataFrame.apply, axis describes which objects the callback receives: axis=1 means one row at a time, while axis=0 means one column at a time. "
    "This is not the same wording as 'which axis disappears' in NumPy reductions. Inspect unknown mapping codes and missing values explicitly. A row callback is not permission to edit the row or parent while pandas is iterating.",
    'df["label"] = df["code"].map({"NP":"Nepal","JP":"Japan"})\ndf.apply(function_receiving_row, axis=1)\ndf.apply(function_receiving_column, axis=0)',
    '''
    import pandas as pd
    df = pd.DataFrame({"code": ["NP", "JP", "XX"], "price": [100, 200, 50], "quantity": [2, 3, 4]})
    df["label"] = df["code"].map({"NP": "Nepal", "JP": "Japan"})
    def row_total(row):
        return row["price"] * row["quantity"]
    callback = df.apply(row_total, axis=1)
    vectorized = df["price"] * df["quantity"]
    print(df["label"].isna().tolist())
    print(callback.tolist(), callback.equals(vectorized))
    ''',
    "XX mapping मा थिएन, त्यसैले missing label आयो। Apply ले row पायो, तर यो multiplication built-in operation बाट झन् सजिलो भयो।",
    'Use apply(axis=1) for every ordinary column formula',
    'Use vectorized arithmetic first; reserve apply for a justified callback',
    "A Python row callback adds work and hides an otherwise simple formula.",
    "Map level codes B/I to Beginner/Intermediate and separately flag an unknown code X.",
    '''
    import pandas as pd
    codes = pd.Series(["B", "I", "X"], dtype="string")
    labels = codes.map({"B": "Beginner", "I": "Intermediate"})
    print(labels.isna().tolist())
    print("Unknown:", codes.loc[labels.isna()].tolist())
    ''',
    "Use apply(axis=0) to receive each numeric column, then compare with the built-in column sum.",
    '''
    import pandas as pd
    df = pd.DataFrame({"a": [1, 2], "b": [10, 20]})
    def column_sum(column):
        return column.sum()
    print(df.apply(column_sum, axis=0).to_dict())
    print(df.sum().to_dict())
    ''',
    "map transforms values; apply supplies rows or columns to callbacks. Prefer clear built-in operations when available.",
    [("What does apply(axis=1) normally pass to the callback?", "One row Series", "One whole database", "One column Series", "axis=1 invokes the callback across each row."),
     ("What does dictionary map do to an unknown key?", "Produces missing", "Always keeps the original code", "Deletes the record", "Inspect unmapped keys explicitly.")])

lesson(4, "4. Safe edits with one loc operation",
    "Update intended rows directly, preserve the source when needed and avoid chained assignment.",
    [("Conditional loc assignment", "df.loc[mask, column] = value modifies the intended DataFrame in one indexing operation. A separate working copy preserves the raw table."),
     ("assign", "assign returns a DataFrame with supplied new/replaced columns. A callable receives the evolving DataFrame; later assignments can refer to columns added earlier in that assign call.")],
    "Changing a table should be an explicit decision. Copy the raw table when you need an editable working version, build a clear Boolean mask and perform one loc assignment. "
    "Do not select a column, select rows from that result and expect the parent to update. Under pandas3 Copy-on-Write, chained assignment cannot implement that intention. "
    "assign is useful for a transformation that returns a new table. Callable expressions allow later derived columns to use an earlier column from the same call. "
    "Keep edits easy to audit: identify the row labels, explain the policy and check both changed and unchanged records. A missing score is not automatically a failed score.",
    'working = raw.copy()\nworking.loc[working["score"] < 60, "status"] = "review"\nresult = raw.assign(total=lambda table: table["price"] * table["quantity"])',
    '''
    import pandas as pd
    raw = pd.DataFrame({"score": [50, 80, 90]}, index=["A", "B", "C"])
    working = raw.copy()
    working["status"] = "ready"
    working.loc[working["score"] < 60, "status"] = "review"
    print(working["status"].to_dict())
    print("Raw columns:", raw.columns.tolist())
    ''',
    "Working copy मा A मात्रै review भयो। Raw table को columns समेत उस्तै छन्। किसलाई किन बदलियो भन्ने कुरा code बाटै देखिनुपर्छ।",
    'df["status"][mask] = "review"',
    'df.loc[mask, "status"] = "review"',
    "Update the parent in one operation; do not depend on a separately derived selection.",
    "Assign subtotal and a doubled total in one assign call without adding columns to raw.",
    '''
    import pandas as pd
    raw = pd.DataFrame({"price": [10, 20], "quantity": [2, 3]})
    result = raw.assign(subtotal=lambda x: x["price"] * x["quantity"],
                        doubled=lambda x: x["subtotal"] * 2)
    print(result[["subtotal", "doubled"]].to_dict(orient="records"))
    print(raw.columns.tolist())
    ''',
    "Update a nullable score column only where a known score is below60; keep unknown scores missing.",
    '''
    import pandas as pd
    df = pd.DataFrame({"score": pd.Series([50, pd.NA, 80], dtype="Int64")})
    mask = (df["score"] < 60).fillna(False)
    df.loc[mask, "score"] = 60
    print(df["score"].isna().tolist())
    print(df.loc[df["score"].notna(), "score"].tolist())
    ''',
    "Edit the intended table directly through loc. Preserve raw data when policy changes create a working version.",
    [("Which directly updates a DataFrame?", "df.loc[mask, 'status'] = value", "df['status'][mask] = value", "Only print(df)", "One loc operation identifies the target object."),
     ("Does assign normally add columns to the original object?", "No; it returns a result", "Always", "Only with lambdas", "Save the returned DataFrame.")])

PROJECT = clean(r'''
import argparse
import csv
from io import StringIO
import json
import os
from pathlib import Path
import sys
import tempfile
import numpy as np
import pandas as pd

MAX_BYTES = 5 * 1024 * 1024
MAX_ROWS = 10_000
MAX_COLUMNS = 100

def load_csv(path):
    """Read one bounded UTF-8 comma-separated snapshot; preserve text identifiers."""
    with Path(path).open("rb") as handle:
        raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("CSV exceeds 5 MiB; use a separately designed chunked profiler")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError("Expected UTF-8 CSV") from error
    try:
        reader = csv.reader(StringIO(text, newline=""), strict=True)
        header = next(reader, None)
        if not header or any(not name.strip() for name in header):
            raise ValueError("Require a nonempty header with named columns")
        if len(header) > MAX_COLUMNS:
            raise ValueError("Too many columns")
        if len(header) != len(set(header)):
            raise ValueError("Duplicate headers would make column reports ambiguous")
        rows = 0
        for record in reader:
            if not record:  # physically empty lines are not observations
                continue
            if len(record) != len(header):
                raise ValueError("Ragged CSV record")
            rows += 1
            if rows > MAX_ROWS:
                raise ValueError("Too many rows")
    except csv.Error as error:
        raise ValueError("Malformed CSV") from error
    df = pd.read_csv(StringIO(text), dtype="string", keep_default_na=False,
                     na_values=[""], skip_blank_lines=True)
    if df.shape != (rows, len(header)) or df.columns.tolist() != header:
        raise ValueError("Parser shape/header mismatch")
    return df

def profile(df):
    """Observe text fields; numeric-looking candidates are not verified business types."""
    if not df.columns.is_unique or not all(isinstance(name, str) for name in df.columns):
        raise ValueError("Require unique text column names")
    if len(df) > MAX_ROWS or len(df.columns) > MAX_COLUMNS:
        raise ValueError("Table exceeds profiling limits")
    if not all(isinstance(dtype, pd.StringDtype) for dtype in df.dtypes):
        raise ValueError("Expected explicitly loaded string columns")
    rows = len(df)
    columns = {}
    for name in df.columns:
        series = df[name]
        missing = int(series.isna().sum())
        known = int(series.count())
        unique = int(series.nunique())
        counts = series.value_counts(dropna=True).head(5)
        numeric = pd.to_numeric(series, errors="coerce")
        array = numeric.to_numpy(dtype=float, na_value=np.nan)
        finite_mask = np.isfinite(array)
        finite = array[finite_mask]
        parsed = int(numeric.notna().sum())
        nonfinite = int((numeric.notna().to_numpy(dtype=bool) & ~finite_mask).sum())
        failed = known - parsed
        mean = None
        if finite.size:
            # Scaling before summing avoids overflow from a large finite total.
            mean = float(np.sum(finite / finite.size))
            if not np.isfinite(mean):
                mean = None
        flags = []
        if missing:
            flags.append("missing_values")
        if known == 0:
            flags.append("all_missing_or_no_rows")
        elif unique == 1:
            flags.append("constant_observed_value")
        if bool((series.str.strip() != series).fillna(False).any()):
            flags.append("surrounding_whitespace")
        if bool(series.str.match(r"^[+-]?0\d").fillna(False).any()):
            flags.append("leading_zero_numeric_text")
        if parsed and failed:
            flags.append("mixed_numeric_and_other_text")
        if nonfinite:
            flags.append("nonfinite_numeric_text")
        if name.strip() != name:
            flags.append("header_surrounding_whitespace")
        columns[name] = {
            "storage_dtype": str(series.dtype),
            "observed": known, "missing": missing,
            "missing_percent": None if rows == 0 else round(missing / rows * 100, 2),
            "unique_nonmissing": unique,
            "top_nonmissing": [{"value": str(value), "count": int(count)} for value, count in counts.items()],
            "numeric_candidate": {
                "parsed_nonmissing": parsed, "failed_nonmissing": failed,
                "finite": int(finite.size), "nonfinite": nonfinite,
                "min": None if not finite.size else float(finite.min()),
                "max": None if not finite.size else float(finite.max()),
                "mean": mean,
            },
            "inspect_flags": flags,
        }
    return {
        "shape": [rows, len(df.columns)],
        "duplicate_rows_after_first": int(df.duplicated().sum()),
        "policy": {"missing": "empty fields only; literal NA/NULL preserved",
                   "input": "UTF-8 comma CSV; unique headers; blank physical lines skipped",
                   "numeric": "approximate float candidates only; never change source types",
                   "flags": "inspection signals, not instructions to delete",
                   "limits": {"bytes": MAX_BYTES, "rows": MAX_ROWS, "columns": MAX_COLUMNS}},
        "columns": columns,
    }

def write_report(report, destination):
    """Serialize first; replace only after writing an owned temporary file."""
    destination = Path(destination)
    payload = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         dir=destination.parent, prefix=destination.name + ".",
                                         suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(payload)
        os.replace(temporary, destination)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()

def main(argv=None):
    parser = argparse.ArgumentParser(description="Profile a bounded local CSV without cleaning it")
    parser.add_argument("csv_path")
    parser.add_argument("report_path")
    args = parser.parse_args(argv)
    source, destination = Path(args.csv_path), Path(args.report_path)
    try:
        if source.resolve() == destination.resolve():
            raise ValueError("Choose an output path different from the source")
        if destination.suffix.lower() != ".json":
            raise ValueError("Choose a .json report output")
        report = profile(load_csv(source))
        report["input_name"] = source.name
        write_report(report, destination)
    except (OSError, ValueError, pd.errors.ParserError) as error:
        print("No new report:", error, file=sys.stderr)
        return 1
    print("Report saved; input unchanged")
    return 0
''')

lesson(5, "1. Sorting with explicit ties and missing placement",
    "Sort rows by values or labels while preserving the original table and defining ties.",
    [("sort_values; ascending; na_position", "sort_values orders rows using column values. ascending can be one flag or one flag per sort key. na_position='last' puts missing sort values last."),
     ("kind='stable'; secondary sort key", "For a single-column sort, stable preserves original order among equal values. For a multi-column sort, explicit secondary keys define ties; kind is only applied for a single key."),
     ("sort_index", "sort_index orders row labels, not a chosen metric. Sorting normally returns a result rather than editing the original DataFrame.")],
    "A ranked report needs a deterministic order. If two scores are equal, decide whether source order, ID or another business rule breaks the tie. "
    "A stable single-column sort retains source order among ties. A multi-key sort can instead order by score descending and ID ascending. "
    "Missing values need an explicit placement policy and should not become zero merely to make sorting easier. Sorting by index answers a different question from sorting by score. "
    "Keep the sorted report as a separate object and verify that the raw row order is unchanged. The example uses unique text IDs to make the tie policy understandable.",
    'df.sort_values(["score","id"], ascending=[False,True], na_position="last")\ndf.sort_values("score", ascending=False, kind="stable")\ndf.sort_index()',
    '''
    import pandas as pd
    df = pd.DataFrame({"id": ["B", "A", "C", "D"],
                       "score": pd.Series([90, 90, 70, pd.NA], dtype="Int64")})
    stable = df.sort_values("score", ascending=False, kind="stable", na_position="last")
    by_id = df.sort_values(["score", "id"], ascending=[False, True], na_position="last")
    print("Source-tie order:", stable["id"].tolist())
    print("ID-tie order:", by_id["id"].tolist())
    print("Raw:", df["id"].tolist())
    ''',
    "Equal scores को order policy अनुसार फरक भयो। Missing D अन्तिममा रह्यो। Raw table sorted भएको छैन; report मात्रै अलग order मा आयो।",
    'Sort by score and assume tied IDs are always alphabetical',
    'Add id as a secondary key when alphabetical ID order is required',
    "The metric alone does not encode an ID tie-break rule.",
    "Sort scores descending, break ties by ID ascending and keep missing scores last.",
    '''
    import pandas as pd
    df = pd.DataFrame({"id": ["C", "B", "A"], "score": [70, 90, 90]})
    print(df.sort_values(["score", "id"], ascending=[False, True])["id"].tolist())
    ''',
    "Show that index sorting and score sorting can yield different row orders.",
    '''
    import pandas as pd
    df = pd.DataFrame({"score": [90, 60, 80]}, index=["C", "A", "B"])
    print("Labels:", df.sort_index().index.tolist())
    print("Scores:", df.sort_values("score", ascending=False).index.tolist())
    ''',
    "State metric direction, tie-break and missing placement. sort_index sorts labels, not the metric.",
    [("Which sorts row labels?", "sort_index", "value_counts", "describe", "The index is separate from data columns."),
     ("What does a stable single-key sort preserve among ties?", "Source order", "Always alphabetical IDs", "No rows", "Equal values retain their earlier relative order.")])

lesson(5, "2. Top, bottom and ranking are different reports",
    "Create top/bottom reports and choose a meaningful tie policy for ranks.",
    [("nlargest; nsmallest; keep", "These select largest/smallest values of numeric/orderable columns. keep='first' resolves boundary ties by source order; keep='all' can return more than n rows. Text columns are not supported for numerical top-N selection."),
     ("rank; method; ascending", "rank assigns rank numbers without reordering rows. method='average' gives tied observations their average rank; dense uses consecutive tied groups. ascending=False makes larger values rank first."),
     ("Top-N availability policy", "A request for ten rows cannot create ten genuine observations if fewer are eligible. Filter missing scores explicitly and report how many rows were available.")],
    "Sorting changes report order; ranking adds a position-like measure to each original row. With scores90,90,80, descending average ranks are1.5,1.5,3, while dense ranks are1,1,2. "
    "Neither convention is universally correct; state which one answers your question. Missing values normally remain unranked. "
    "For a top10 report, first identify eligible known scores. If only three exist, return three and say so. keep='all' can exceed the requested size when the boundary is tied. "
    "For deterministic ID tie-breaking, a multi-key sort followed by head(10) is often clearer than relying on source order.",
    'known.nlargest(10,"score",keep="first")\nknown.nsmallest(10,"score")\ndf["rank"] = df["score"].rank(method="dense",ascending=False)',
    '''
    import pandas as pd
    df = pd.DataFrame({"id": ["A", "B", "C", "D"],
                       "score": pd.Series([90, 90, 80, pd.NA], dtype="Int64")})
    known = df.loc[df["score"].notna()]
    print("Top1 first:", known.nlargest(1, "score", keep="first")["id"].tolist())
    print("Top1 all ties:", known.nlargest(1, "score", keep="all")["id"].tolist())
    print("Average ranks:", df["score"].rank(method="average", ascending=False).isna().tolist())
    print("Dense known:", known["score"].rank(method="dense", ascending=False).tolist())
    ''',
    "Top1 मा keep='all' ले दुई tied rows दियो। Dense rank मा gap हुँदैन। Missing score को rank बनाउनका लागि बनावटी zero नराख्नु।",
    'Assume keep="all" always returns exactly n records',
    'Check result size; boundary ties may increase it',
    "Including all tied observations can make the result larger than the requested n.",
    "Make top10 and bottom10 lists from12 known scores with IDs and print the available counts.",
    '''
    import pandas as pd
    df = pd.DataFrame({"id": [f"S{i:02}" for i in range(1, 13)], "score": list(range(10, 130, 10))})
    top, bottom = df.nlargest(10, "score"), df.nsmallest(10, "score")
    print("Top:", top["id"].tolist())
    print("Bottom:", bottom["id"].tolist())
    print("Counts:", len(top), len(bottom))
    ''',
    "Compare average/dense ranks for90,90,80 without changing the source row order.",
    '''
    import pandas as pd
    df = pd.DataFrame({"id": ["A", "B", "C"], "score": [90, 90, 80]})
    df["average_rank"] = df["score"].rank(method="average", ascending=False)
    df["dense_rank"] = df["score"].rank(method="dense", ascending=False)
    print(df.to_dict(orient="records"))
    ''',
    "Top/bottom selection, sorting and ranking answer different questions. Always state tie and missing policies.",
    [("Does rank reorder the rows?", "No", "Always", "Only dense ranks", "It assigns rank values to the existing rows."),
     ("Can keep='all' return more than n rows?", "Yes", "No", "Only when n=0", "All boundary ties are included.")])

lesson(5, "3. Dataset profiler: complete local CSV project",
    "Build a reusable read-only CSV report with limits, explicit inference and atomic output.",
    [("CSV profiling contract", "This local tool accepts UTF-8 comma-separated CSV up to5MiB,10000 rows and100 columns, with unique nonempty headers. It rejects malformed/ragged records and reports header-only input as zero rows."),
     ("csv.reader(strict=True); bounded snapshot", "csv.reader validates quoted record structure and row widths. Reading at most MAX_BYTES+1 makes one bounded snapshot so validation and pandas see the same input."),
     ("to_numeric(errors='coerce'); numeric candidates", "to_numeric attempts numerical interpretation; failures become missing in a separate result. The source stays string. Numeric-looking IDs and large integers may lose precision in float summaries, so candidates are inspection aids, not verified types."),
     ("np.isfinite; finite subset", "isfinite excludes NaN and infinities from descriptive numerical summaries. Nonfinite and unparsed text are counted separately instead of silently disappearing."),
     ("argparse; NamedTemporaryFile; os.replace", "argparse reads CLI paths. NamedTemporaryFile creates an owned unique temporary output beside the destination. os.replace installs the completed report; cleanup removes only that owned temporary file."),
     ("JSON allow_nan=False; scalar conversion", "JSON serialization rejects NaN/infinity with allow_nan=False. Convert counts to int, stats to finite float and unavailable results to None (JSON null).")],
    "The final project extends Day3's first-look idea to a reusable command-line program. It preserves every input field as nullable text, treating only empty fields as missing. "
    "It reports dimensions, types, missing counts/percentages, full-row duplicates, top observed categories, numeric-looking candidates and inspection flags. "
    "Literal NA/NULL remains text. Numeric conversion happens in a separate exploratory Series; it never rewrites IDs or drops source rows. "
    "Read the contract before interpreting the report: category output is limited to five values, numeric statistics are approximate, and a flag is a reason to inspect, not delete. "
    "Reports can contain values from your file, so keep reports of personal data private. All supplied examples use fictional data. Larger, different-encoding or semicolon files need an explicitly adapted loader, not silent guessing.",
    'python dataset_profiler.py students.csv report.json\n# separate output; input stays unchanged\nreport = profile(load_csv(source))\nwrite_report(report, destination)',
    PROJECT + '''
from pathlib import Path
Path("students.csv").write_text("id,score,region\\n001,80,NP\\n002,,NA\\n003,90,JP\\n", encoding="utf-8")
report = profile(load_csv("students.csv"))
print("Shape:", report["shape"])
print("Missing score:", report["columns"]["score"]["missing"])
print("ID flags:", report["columns"]["id"]["inspect_flags"])
print("Region known:", report["columns"]["region"]["observed"])
''',
    "Report मा ID string नै छ; leading zeros inspect flag मात्र हो। NA region missing बनेन। Score का numeric candidates छुट्टै छन्, raw file बदलिएको छैन।",
    'Infer every numeric-looking column as a verified quantity and delete every flagged row',
    'Keep raw text, label candidate statistics clearly and inspect flags using domain knowledge',
    "IDs can look numeric; duplicate rows, constants and missing values may all be legitimate.",
    "Run the complete profiler on a four-row CSV with a duplicate, one missing score and mixed region labels. Inspect its dimensions and counts.",
    PROJECT + '''
Path("sample.csv").write_text("id,score,region\\n001,80,NP\\n002,,NA\\n003,90,JP\\n001,80,NP\\n", encoding="utf-8")
report = profile(load_csv("sample.csv"))
print(report["shape"], report["duplicate_rows_after_first"])
print(report["columns"]["score"]["missing_percent"])
print(report["columns"]["score"]["numeric_candidate"]["mean"])
print(report["columns"]["region"]["top_nonmissing"])
''',
    "Save a JSON report through the CLI function; prove the CSV bytes stayed unchanged.",
    PROJECT + '''
source, destination = Path("students.csv"), Path("report.json")
source.write_text("id,score\\n001,80\\n002,90\\n", encoding="utf-8")
before = source.read_bytes()
status = main([str(source), str(destination)])
stored = json.loads(destination.read_text(encoding="utf-8"))
print("Status:", status, "Shape:", stored["shape"])
print("Unchanged:", source.read_bytes() == before)
''',
    "Profile before cleaning: preserve input, declare format/limits, separate candidate inference, and replace reports only after successful validation.",
    [("Does this profiler change ID columns into numbers?", "No", "Always", "Only with leading zeros", "Its source DataFrame is explicitly nullable text."),
     ("Are inspection flags automatic deletion instructions?", "No", "Always", "Only for duplicate rows", "Domain knowledge decides whether a flagged observation is valid.")])

lesson(5, "4. Whole-week retrieval and failure tests",
    "Verify table semantics and failure boundaries, then explain the week without copying.",
    [("Failure preservation", "Invalid input must fail before replacing a prior report. This protects useful output when a later dataset is malformed."),
     ("Owned-file cleanup", "Remove only the temporary file created by this run. Do not clean up by deleting every matching .tmp file in the folder."),
     ("Schema versus inference", "A declared schema communicates business meaning; inferred numeric candidates only suggest possible interpretations. This difference remains important during Week29 cleaning.")],
    "Finish by predicting results, not just recognizing method names. Explain label alignment, the Series/table shape difference, loc versus iloc and why chained assignment fails in pandas3. "
    "Write filters with explicit missing policies and derive columns without overwriting raw data. Build top/bottom reports with stated tie rules. "
    "Then test a boundary case for each profiler promise: duplicate headers, ragged rows, header-only input, literal NA, leading-zero IDs, nonfinite numeric text and a failed output path. "
    "A good result is both numerically understandable and safe to rerun. The project tests verify input preservation, old-report preservation and owned temporary-file cleanup. "
    "Week29 will teach cleaning decisions; knowing what you observed first makes those decisions explainable.",
    'assert source_bytes_unchanged\nassert valid_report_shape_and_missing_policy\nassert invalid_input_does_not_replace_old_report\nassert unrelated_temporary_files_remain',
    PROJECT + '''
Path("bad.csv").write_text("id,score\\n001,80,extra\\n", encoding="utf-8")
Path("report.json").write_text("previous report", encoding="utf-8")
try:
    report = profile(load_csv("bad.csv"))
    write_report(report, "report.json")
except ValueError:
    print("Rejected ragged input")
print(Path("report.json").read_text(encoding="utf-8"))
''',
    "Invalid CSV हुँदा नयाँ report बनेन। पहिलेको report सुरक्षित रह्यो। Success case मात्रै होइन, failure हुँदा के बच्यो भनेर पनि जाँच्नु।",
    'Open the final report for writing before validating the CSV',
    'Load, validate and serialize first; replace through an owned temporary file',
    "Opening the old report early could truncate it before a later error.",
    "Profile a header-only CSV and confirm zero rows with undefined missing percentages.",
    PROJECT + '''
Path("empty.csv").write_text("id,score\\n", encoding="utf-8")
report = profile(load_csv("empty.csv"))
print(report["shape"])
print(report["columns"]["score"]["missing_percent"])
print(report["columns"]["score"]["inspect_flags"])
''',
    "Count nonfinite numeric text and mixed text without changing the original string values.",
    PROJECT + '''
Path("mixed.csv").write_text("value\\n10\\ninf\\nunknown\\n", encoding="utf-8")
df = load_csv("mixed.csv")
report = profile(df)
print(df["value"].tolist())
print(report["columns"]["value"]["numeric_candidate"])
print(report["columns"]["value"]["inspect_flags"])
''',
    "Week28 mastery: labeled tables, deliberate file schemas, honest inspection, predictable selection, safe derivation and reproducible read-only reports.",
    [
        ("What matches Series arithmetic?", "Index labels", "Only positions", "Variable names", "Labels align the observations."),
        ("Is a DataFrame restricted to one dtype?", "No", "Always", "Only numerical tables", "Different columns can have different dtypes."),
        ("How should ID001 be preserved?", "As text before inference", "As integer1", "As floating1.0", "Once leading zeros are lost, dtype conversion cannot restore them."),
        ("What does info normally return?", "None", "A copied table", "The first row", "It prints a structural summary."),
        ("Does value_counts include missing values by default?", "No", "Always", "Only with NA text", "Specify dropna=False if the policy includes them."),
        ("Does loc[10] select by position?", "No; it selects label10", "Always the eleventh row", "Only for named indexes", "Integer labels are labels."),
        ("Does iloc[0:2] include position2?", "No", "Always", "Only in NumPy", "Its stop is exclusive."),
        ("Which combines row-wise AND?", "& with parentheses", "Python and", "A comma", "Use element-wise Boolean logic."),
        ("Does assigning a Series match labels?", "Yes", "No; only positions", "Only when sorted", "Missing partners produce missing values."),
        ("Does chained assignment update the parent under pandas3 CoW?", "No", "Always", "Only numeric columns", "Use one direct loc operation."),
        ("Can top1 keep='all' return two tied rows?", "Yes", "Never", "Only if both IDs match", "All boundary ties may be returned."),
        ("Does a numeric candidate prove a meaningful quantity?", "No", "Always", "Only for IDs", "Storage and business meaning require an explicit schema."),
    ])

DAYS["28.0"]["parts"][0]["sections"].insert(3, s("sh",
    'python -m pip install "pandas>=3,<4" openpyxl',
    note="One-time setup in your own Python practice environment; internet is needed for installation only. Verified with pandas3.0.6/openpyxl3.1.5. The course website stays offline."))
DAYS["28.0"]["parts"][2]["sections"].insert(3, s("new", "sum(min_count=1)",
    note="min_count requires at least that many nonmissing observations for a valid sum. With no observed numbers, min_count=1 gives a missing result instead of the default zero."))
DAYS["28.4"]["parts"][1]["sections"].insert(3, s("new", "to_dict(orient='index')",
    note="This orientation produces one row dictionary per index label. Require unique index labels; records orientation does not use index labels as dictionary keys."))
DAYS["28.5"]["parts"][2]["sections"].append(s("sh",
    "python dataset_profiler.py students.csv report.json\npython dataset_profiler.py --help",
    note="The complete code above is also supplied in docs/python-week28. Use a separate report filename and keep private-data reports off public GitHub."))
DAYS["28.5"]["parts"][3]["sections"].append(s("p",
    "Primary references: https://pandas.pydata.org/docs/getting_started/intro_tutorials/index.html · "
    "https://pandas.pydata.org/docs/user_guide/indexing.html · https://pandas.pydata.org/docs/user_guide/copy_on_write.html · "
    "https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html · https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.query.html · "
    "https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rank.html. These original explanations, local fixtures, outputs and solutions are included for offline study."))


def write():
    target = ROOT / "study-hub.html"
    original = target.read_bytes().decode("utf-8")
    start = original.index("const DAY_TEACH = {")
    end = original.index("\n};\n\nconst REST_DAY", start)
    if any(('"' + key + '":') in original[start:end] for key in DAYS):
        raise RuntimeError("Week28 exists; refusing to overwrite.")
    addition = "\n".join(json.dumps(k) + ": " + json.dumps(v, ensure_ascii=False, indent=2) + "," for k, v in DAYS.items())
    addition = addition.replace("</", "<\\/")
    prefix = original[:end].rstrip()
    if not prefix.endswith(","):
        prefix += ","
    temporary = target.with_suffix(".html.tmp")
    temporary.write_bytes((prefix + "\n" + addition + original[end:]).encode("utf-8"))
    temporary.replace(target)
    project_root = ROOT / "docs" / "python-week28"
    project_root.mkdir(exist_ok=True)
    (project_root / "dataset_profiler.py").write_text(
        '"""Week28 read-only CSV profiler. Python3.11+, pandas3.x, NumPy."""\n'
        + PROJECT + '\nif __name__ == "__main__":\n    sys.exit(main())\n', encoding="utf-8")
    (project_root / "students.csv").write_text(
        "id,name,score,region\n001,Asha,80,NP\n002,Bina,,NA\n003,Chandra,90,JP\n001,Asha,80,NP\n",
        encoding="utf-8")
    parts = [part for day in DAYS.values() for part in day["parts"]]
    quizzes = sum(len(section["lesson"]["quiz"]) for part in parts for section in part["sections"] if section["t"] == "checkpoint")
    print(f"Added Week28: 6 days, {len(parts)} parts, {len(parts)*2} practice prompts, {quizzes} questions, {EXECUTED} verified outputs.")


if __name__ == "__main__":
    write()
