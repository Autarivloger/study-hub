# Python Week 30 — Aggregation, joins and time series

Six study days, 25 parts. Day6 has five parts so time series and the complete
project are taught separately. Each part contains first-use concept explanations,
syntax, executed example/output, a worked exercise, mini challenge, mistakes,
retrieval and quiz questions. Reuse the existing course notes, completion,
navigation, review and Python Practice controls.

## Study order

1. Grouping: observation grain, split/apply/combine, size versus count/nunique,
   missing-key policies, all-missing totals, multiple keys, categorical groups
   and eight practical questions with explicit units/denominators.
2. Aggregation: named multi-metric reports, transform and aligned shares,
   zero-denominator handling, whole-group filter versus row filter, weighted
   rates, rankings and ties.
3. Joins: fact/dimension grain, explicit keys and left/inner/right/outer,
   cardinality validation, indicators, unmatched-key reporting, suffixes,
   many-to-many expansion, null keys, indexed join and reconciled totals.
4. Concatenation: rows/columns, label alignment, schemas, source provenance,
   expected twelve-month manifests, ID types and cross-export overlap checks.
5. Dates: exact parsing, coercion audit, local clocks versus aware instants,
   year/month/weekdays/quarter/period, elapsed gaps, source timezone policies,
   repeated daylight-saving clocks and half-open reporting boundaries.
6. Time series: daily/monthly bins, complete versus unknown coverage, seven
   observations versus seven days, trailing windows, calendar-aligned shift,
   undefined growth, observed purchase cohorts, censoring and sales project.

## Run the fictional project

Python3.11+ and pandas3.x. Outputs were executed with pandas3.0.1. Initial
package installation requires internet; after installation these lessons,
scripts and fictional CSVs work locally without network requests.

    python -m pip install "pandas>=3,<4"

From this folder:

    python sales_report.py sale_lines.csv products.csv customers.csv run-01 --start 2025-01-01 --end 2025-04-01 --complete-feed
    python sales_report.py --help

Use run-02 for the next run. The supplied CSVs are fictional; retain real
personal data outside public repositories. The lesson examples generate their
own fictional fixture files: execute them in a fresh practice folder.

## Project contract and interpretation

- Three local UTF-8/UTF-8-BOM comma-separated CSVs; unique exact header sets,
  no ragged rows, at most5MiB and10000 observations per input.
- IDs remain text; sale-line IDs and dimension IDs are known/unique, foreign
  keys must match. Product names and customer regions are known.
- One fact row is one sale line. Historical price belongs to the transaction,
  not the current catalog. Many lines may reference a unique lookup record.
- Date-only YYYY-MM-DD calendar labels, not timezone-aware instants. A naive
  midnight month-start window uses start inclusive/end exclusive, up to24months.
- Positive integer units/prices up to1000000; prices/revenue in integer minor
  units of one fictional currency. Refunds, discounts, taxes, exchange rates,
  historical region changes and profitability are outside this small project.
- --complete-feed is the caller's assertion that all events in every supplied
  calendar month are represented. It cannot prove absence of unsupplied data.
  Only this contract permits absent daily events to mean zero.
- Missing/invalid records stop the run; this program does not automatically
  repair, quarantine or deduplicate inputs. Week29 explains deliberate cleaning.
- Joins preserve sale IDs, line count and recorded revenue. Monthly totals
  reconcile with the enriched fact table.
- Daily rolling7 means need seven daily observations; the first six remain
  missing. Month-over-month growth is percent; first and zero-base comparisons
  remain missing. Do not apply full-month comparison to an incomplete month.
- Product rankings are within region; equal revenue uses product_id ascending
  as a display tie-breaker. The report retains every product, not just winners.
- Cohorts are first observed purchases within the report window, not proven
  acquisition. Distinct monthly customers form the numerator; age0 cohort size
  stays the denominator. Elapsed covered ages can be0; future ages stay missing.
  This is monthly purchase retention, not churn or continuous usage retention.
- Six CSV reports and a summary JSON publish to a fresh output directory via
  one owned temporary directory. Existing bundles and raw inputs are retained.
  Blank growth/rolling/retention CSV cells mean undefined or not yet observable.

## Verification

75 examples/solutions execute before insertion. Static checks compare all older
lessons and all application/storage code against commit fe13425. Project tests
check actual revenue110000, monthly30000/25000/55000, joins, historical prices,
zero-base growth, daily rolling, distinct-customer cohorts, future cells,
input immutability, invalid-source boundaries, CLI coverage declaration and
new-bundle preservation. Browser checks use fictional progress in an isolated
profile for lesson rendering, navigation, quizzes, notes, completion, practice,
reviews, refresh, search, backup/import, mobile themes and JavaScript errors.

## Primary references

- [GroupBy](https://pandas.pydata.org/docs/user_guide/groupby.html)
- [Merge, join and concat](https://pandas.pydata.org/docs/user_guide/merging.html)
- [Dates and time series](https://pandas.pydata.org/docs/user_guide/timeseries.html)
- [Windows](https://pandas.pydata.org/docs/user_guide/window.html)

Explanations, fictional fixtures and exercises are original; essential learning
material is included in the offline HTML rather than depending on these links.
