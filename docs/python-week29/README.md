# Python Week 29 — Data cleaning and preparation

Six days, four parts per day. Every part contains a learning objective,
first-use explanations, syntax, executed examples and outputs, common mistakes,
practice, a mini challenge, solutions, retrieval prompts and quizzes.

## Study order

1. Missing data: missing versus blank/zero/invalid, drop rules and retention,
   constant/median fills with provenance, interpolation and strategy comparison.
2. Duplicates: exact rows versus entity keys, newest valid updates and tie rules,
   category aliases, unknowns, cell-change audits and repeatability.
3. Types: numeric parse failures, finite/domain checks, explicit dates/timezones,
   nullable integers, ordered categoricals and staged schema validation.
4. Text: field-specific whitespace/case/Unicode rules, literal versus regex
   replacements, contains/fullmatch/extract, and structured splitting.
5. Outliers: domain errors versus rare events, IQR fences, z-score conventions,
   degenerate spread, documented decisions and final validation.
6. Reshaping: tidy observation units, melt, pivot versus aggregating pivot_table,
   named MultiIndex stack/unstack, and the complete audited cleaning pipeline.

## Run the project

Use Python 3.11+ and pandas 3.x (verified with pandas 3.0.6). Reuse the Week 28
practice environment, or install once with internet:

    python -m pip install "pandas>=3,<4"

From this folder:

    python cleaning_pipeline.py messy_students.csv run-01
    python cleaning_pipeline.py --help

The sample is fictional. The program makes no network requests. It creates
run-01/clean.csv and run-01/report.json while retaining the source CSV.
Choose a new destination such as run-02 for another run; existing bundles are
refused. Keep actual personal data and its audit reports private.

## Project contract

This is a schema-specific learning pipeline, not an automatic cleaner for
arbitrary datasets.

- Local UTF-8/UTF-8-BOM comma-separated CSV, up to 5 MiB and 10,000 observations.
- Exactly these unique headers: id,name,region,score,updated (input order may vary).
- All raw columns load as nullable text, retaining ID zeros and literal NA/NULL.
- IDs must be exactly three ASCII digits; names are required. Name whitespace
  and NFC-equivalent text are normalized; IDs remain text.
- Region aliases np/nepal and jp/japan map to NP/JP. Unknowns are quarantined.
- Updated is a valid YYYY-MM-DD calendar date, with exact zero-padded shape.
  It does not represent an instant or within-day event ordering.
- Known scores must parse, be finite and fall within 0..100. Invalid known
  tokens are quarantined, not imputed.
- The newest valid date per ID wins; equal dates choose the later parsed input
  record. Invalid newer updates are quarantined before winner selection.
- Only genuine empty/whitespace-only retained scores are median-filled using
  known retained scores. If a required estimate has no observations, the run stops.
- Source references are one-based parsed observation positions, not physical
  CSV line numbers; quoted fields may span lines.
- The report includes quarantine reasons, superseded records, estimated records,
  fill parameter and all source-to-final-staged cell differences, including
  attempted normalization/conversion for records not retained.
- IQR thresholds use final scores, including disclosed estimates. These are
  inspection signals only. Zero IQR produces no automatic outlier decision.
- Final validation and row accounting are checked before export.
- Canonical clean CSV values are repeatable after reload. A second audit has
  new source references; it cannot recover original missingness from filled CSV.
  Keep the original report for provenance.
- Publication writes both files to one owned temporary directory and renames
  it to a new destination. The parent directory must exist. A failed run does
  not overwrite previous bundles or remove unrelated temporary folders.

## Verification

All 72 examples/solutions execute before lesson insertion. Project tests check
actual values and decisions, failure isolation, audit provenance, repeatability,
input preservation and new-bundle publication boundaries. Static checks compare
every older lesson and all application/storage code against the Week 28 baseline.
Isolated-browser checks cover all lesson parts, navigation, search, quizzes,
saved notes/progress, mobile layouts, themes and JavaScript errors. Existing
backup/import regression uses fictional data in a separate browser profile.

## Primary references

- [Missing data](https://pandas.pydata.org/docs/user_guide/missing_data.html)
- [Text operations](https://pandas.pydata.org/docs/user_guide/text.html)
- [Datetime conversion](https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html)
- [Reshaping](https://pandas.pydata.org/docs/user_guide/reshaping.html)
- [pandas 3 stack interface](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.stack.html)
