# Python Week34 — Exploratory Data Analysis end to end

Six days, **28 parts**, **56 practice prompts**, **66 explained quiz questions**,
**84 executed examples/solutions** and **28 embedded chart pictures**.
The existing Day7 Review & rest shuffles this week's practice prompts.

## Study sequence

1. Four parts: question/unit/denominator; data dictionary and units; five
   question-to-evidence plans; frozen raw source and reproducible runs.
2. Four parts: preserved raw tokens and schema; every-field profile;
   missingness patterns and scope; exploratory hypotheses and identity limits.
3. Five parts: dataset-specific audited pipeline; category rules; numeric
   conversion/rejection; retained IQR/equal-value flags; inclusion sensitivity.
4. Five parts: all numeric fields; category counts with unknowns; complete
   coordinate pairs; group means/medians/spreads/counts; support/row shares.
5. Five parts: strata and comparison overlap; correlations/pair counts;
   explicit equal-known-sex weighting; cross-sectional year composition;
   robustness under disclosed centre/inclusion choices.
6. Five parts: claim/evidence/limit/next check; complementary report panels;
   complete audited preparation; generated executive summary; full milestone.

Every part uses the existing objective, first-use boxes, syntax, example and
actual output/picture, walkthrough, mistake/fix, practice, mini challenge,
solutions, quiz, notes, completion and navigation. No application/renderer
function or storage structure changes. Other courses and saved IDs remain.

## Offline environment

    python -m pip install "numpy>=2,<3" "pandas>=3,<4" "matplotlib>=3.10,<3.11"

Verified with Python3.12, NumPy2.3.5, pandas3.0.1 and Matplotlib3.10.9.
Initial installation needs internet. Lessons and their pictures are embedded
in study-hub.html; examples and the supplied project then run locally without
network. Python is executed outside the website. Snippets reuse chart.png,
so run them in a fresh practice folder.

Early inline examples use a labelled12-row real excerpt, first4rows from each
species. It is not a random sample and its summaries/support must not be
substituted for the full file. Deliberately dirty or hypothetical examples
are labelled fictional. See **SOURCE.md** for pinned data, credits and CC0.

## Run the full milestone

Keep eda_report.py and penguins.csv together. From this folder:

    python eda_report.py penguins.csv eda-run-01
    python eda_report.py --help

Choose eda-run-02 for another run. The CLI uses **all344source rows**, not the
excerpt. It refuses an existing destination, preserves raw bytes and stages
its own temporary bundle before publishing. Failed exports leave no partial
bundle. Analysis scope and environment remain part of the evidence.

### Dataset-specific contract

- UTF-8/UTF-8-BOM CSV, eight exact ordered unique headers,1–10000records,
  <=1MiB and no ragged/blank rows.
- Species Adelie/Chinstrap/Gentoo; island Biscoe/Dream/Torgersen; collection
  years2007–2009. Required category/year values must be known.
- Documented NA is retained for the four measurements and recorded sex.
  Other malformed values, infinity, nonpositive known physical measurements
  or values>1000000 in their source units stop for review. These broad bounds
  are a teaching input contract, not a biological-accuracy guarantee.
- Surrounding whitespace and known sex case are normalised with an old/new
  token ledger. No imputation, automatic source-row removal or identity-based
  deduplication is performed. Equal-value candidates and IQR flags remain.
- The report requires at least3variable complete flipper/mass pairs; this is
  an analysis requirement, not evidence that other valid rows are bad.
- Missing values are selected per question; unknown sex does not invalidate
  known mass. Source positions are references, not independently verified IDs.

### Seventeen artifacts

cleaned.csv, audit_changes.csv, decisions.json, profile.csv,
category_counts.csv, species_mass.csv, species_sex_mass.csv,
support_species_island.csv, year_species_mass.csv, correlation.csv,
pair_counts.csv, sensitivity.csv, standardised_mass.csv, review_flags.csv,
overview.png, summary.json and report.md.

The8-panel figure has distribution, species boxes, paired scatter, unknown
counts, recorded-sex means, species/island support, year summaries and a
correlation matrix. Exact values/counts and caveats live in the CSVs/report.

### What the full source supports

344rows:152Adelie,68Chinstrap,124Gentoo. Mass is known for342; recorded sex is
unknown for11; known sex+mass has333records. Known-mass counts/means are:

| Species | Known mass n | Mean g | Median g |
| --- | ---: | ---: | ---: |
| Adelie | 151 | 3700.7 | 3700 |
| Chinstrap | 68 | 3733.1 | 3700 |
| Gentoo | 123 | 5076.0 | 5000 |

These are genuine descriptive differences in the recorded sample. They do
not imply every Gentoo exceeds every other bird, establish population means,
or identify a cause. Gentoo is observed only on Biscoe and Chinstrap only on
Dream; absent comparison support cannot be repaired by a colourful model.
Collection-year means do not establish matched-bird growth or climate effects.

Standardised means explicitly use equal female/male weights among known
outcomes; unavailable subgroup support remains missing. Sensitivity compares
known-mass versus known-sex/mass inclusion plus mean/median, with counts.
No automatic p-value search or unverified confirmatory inference is claimed.

## Verification

All84 authored snippets execute with fresh globals and temporary folders;
plotting defaults/random state reset and figures close between examples.
Imports are reused by the authoring verifier for speed; it is not a sandbox
for untrusted code and is never executed by the deployed website.28 actual
PNG previews are embedded. Static checks compare older lessons and all
surrounding application/storage code against commit285e395. Browser checks
cover28parts/66quizzes, pictures, notes/progress, navigation, search,
studied-only practice/review, refresh,375px themes and console errors. Existing
backup/import merge and replace regression is also checked. Project tests
verify source bytes/counts, summaries, support, missingness, token audit,
retained rows, sensitivity, artifacts and publication failure handling.

## Primary references

- [Palmer Penguins source and credits](https://allisonhorst.github.io/palmerpenguins/)
- [Original research](https://doi.org/10.1371/journal.pone.0090081)
- [NIST: what is EDA?](https://www.itl.nist.gov/div898/handbook/eda/section1/eda11.htm)
- [pandas missing data](https://pandas.pydata.org/docs/user_guide/missing_data.html)
- [pandas joining](https://pandas.pydata.org/docs/user_guide/merging.html)
