# Python Week 28 — pandas fundamentals

Original teaching material for the existing offline Study Hub. Six study days,
four parts per day. Every part includes an objective, first-use explanations,
syntax, executed example/output, a wrong/right comparison, a build exercise,
a mini challenge, solutions, retrieval prompt and quiz.

## Study order

1. Series and DataFrames: labels, three construction patterns, nullable dtypes,
   identifiers and pandas 3 Copy-on-Write.
2. Loading: explicit CSV schemas, named Excel sheets, JSON records and local
   SQLite queries with bound parameters.
3. Inspection: previews, info, numeric describe, missingness denominators,
   category counts and a reusable nonmutating first-look function.
4. Selection: Series/table shapes, loc/iloc, inclusive/exclusive slices,
   nullable Boolean filters and ten selection questions.
5. Columns: five vectorized derivations, assignment alignment, map/apply
   differences and direct loc updates.
6. Reports: deterministic sorting, top/bottom 10, ranking, the complete CSV
   profiler and whole-week retrieval/failure tests.

## Run the project

Use Python 3.11+ in your own practice environment. Install pandas 3.x and
openpyxl once (installation needs internet):

    python -m pip install "pandas>=3,<4" openpyxl

From this folder:

    python dataset_profiler.py students.csv report.json
    python dataset_profiler.py --help

The supplied data is fictional. The CLI reads local files, makes no network
requests and leaves the CSV unchanged. The report contains category values:
keep reports made from your personal data private.

## Profiler contract

- UTF-8/UTF-8-BOM, comma-separated CSV; unique nonempty column headers.
- At most 5 MiB, 10,000 observations and 100 columns. Larger files require a
  separately designed chunked profiler.
- Header-only input is allowed; percentages are null when there are no rows.
- Empty fields are missing; literal NA/NULL remains text. Blank physical lines
  are skipped. Ragged/malformed records are rejected before reporting.
- All source columns are nullable strings, preserving leading-zero IDs.
- Numerical summaries are approximate candidates from a separate conversion;
  they do not establish business types. Large numeric identifiers may lose
  precision in candidate float summaries; their original text stays intact.
- Nonfinite parsed values and failed conversions are counted separately;
  finite values alone contribute to candidate min/max/mean.
- Up to five nonmissing category frequencies are included per column.
- Duplicate count means complete duplicated rows after the first occurrence.
  Missing, constant, whitespace and other flags request inspection, not deletion.
- Output must be a separate .json path. Validation and serialization precede
  replacement; unique temporary-file cleanup touches only the file this run owns.
- This is a beginner local-file tool, not a streaming or hostile-file parser.

## Verification

Verified with Python 3.12, pandas 3.0.6 and openpyxl 3.1.5.
The generator executes all 72 examples/solutions before adding content.
Project tests exercise interpretation and file-preservation boundaries.
Static checks compare every prior lesson and all application/storage code
with the Week 27 baseline. Isolated-browser checks cover rendering, navigation,
quizzes, saved progress/notes, search, mobile layouts, themes and JavaScript
errors. The existing backup/import regression runs with fictional data.

## Primary references

- [pandas introductory tutorials](https://pandas.pydata.org/docs/getting_started/intro_tutorials/index.html)
- [Indexing and selection](https://pandas.pydata.org/docs/user_guide/indexing.html)
- [Copy-on-Write](https://pandas.pydata.org/docs/user_guide/copy_on_write.html)
- [CSV loading](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
- [Query expressions](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.query.html)
- [Ranking](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rank.html)
