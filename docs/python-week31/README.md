# Python Week 31 — Visualisation with Matplotlib

Six teaching days, **24 parts**, **48 practice prompts**, **58 explained quiz
questions**, **72 executed examples/solutions**, and **24 actual chart pictures**.
The existing seventh day collects the week's shuffled review exercises.

## Learning sequence

1. Figure/Axes/Axis, explicit and implicit interfaces, paired coordinates,
   ordering, missing-value gaps and a chart-reading contract.
2. Line, vertical/horizontal/grouped bar, scatter, histogram, box and pie;
   choose by the question, observation grain and meaningful denominator.
3. Titles, labels, legends, ticks, limits, log scales, annotations, dates and
   percentage formatting without changing the data meaning.
4. Axes arrays, shared scales, GridSpec and complementary report panels.
5. Scoped styles, accessible cues, colormaps, numeric colourbars and helpers
   that draw on their caller's Axes instead of opening unexpected figures.
6. Physical size/DPI, PNG/SVG/PDF, backgrounds/cropping, figure lifecycle and
   the Week30 sales visual report with supported interpretation.

Every part has a learning objective, first-use explanations, syntax, runnable
example and output, embedded chart, walkthrough, mistake/fix, practice,
mini challenge, revealable solutions and a saved quiz checkpoint. Existing
completion, part navigation, notes, search, studied-only practice and reviews
are reused. The only renderer addition is an escaped, PNG-data-only figure
section; no storage schema or root key changes.

## Offline use

All essential teaching and pictures are embedded in study-hub.html. Reading
them does not request external image files. Python executes locally outside
the website. Initial package installation needs internet; these examples and
the fictional project work offline once dependencies are installed.

Python3.11+, Matplotlib3.10.x and pandas3.x. Verified with Matplotlib3.10.9,
pandas3.0.1, NumPy2.3.5 and the bundled Python3.12 environment.

    python -m pip install "matplotlib>=3.10,<3.11" "pandas>=3,<4"

Example snippets write chart.png in the current practice directory. Use a
fresh folder when experimenting; each snippet is self-contained. File-only
testing uses the Agg backend. A desktop GUI may also use show after saving.

## Standalone capstone

Keep the neighbouring **python-week30** folder: its strict preparation code
and three original fictional CSVs are reused, rather than copied or weakened.
From this folder:

    python visual_report.py ../python-week30/sale_lines.csv ../python-week30/products.csv ../python-week30/customers.csv visual-run-01 --start 2025-01-01 --end 2025-04-01 --complete-feed
    python visual_report.py --help

Use visual-run-02 for the next run. The complete-feed switch is the caller's
assertion of complete coverage, not something the program can independently
prove. The Week30 bounds, ID/lookup uniqueness, join coverage, date parsing,
positive integer amounts and historical transaction-price contract still
apply. Invalid source data stops before publication.

Eight files are published together to a new directory: report.png (300DPI,
3000-by2100pixels), report.svg, report.pdf, monthly_plot.csv, region_plot.csv,
product_plot.csv, sale_line_plot.csv and interpretation.txt. Plot-data CSVs
retain exact integer minor units; displayed charts divide by100. Raw inputs
and older output bundles are not overwritten. Temporary output cleanup is
owned by the project's TemporaryDirectory.

### What the sample supports

- Eight sale lines;110000 minor units =1100 fictional currency units.
- Monthly revenue: January300, February250, March550.
- Region revenue: NP600, JP500. Product revenue: Book700, Pen400.
- Sample sale-line histogram:100-unit intervals, counts1,5,1,1; final interval includes
  its right edge. Larger source amounts use coarser intervals to keep the
  project within20 bins. Monthly totals are not the histogram's observations.
- Revenue is not profit. No experiment, causal attribution, forecast or
  general business-performance claim is supported by this fictional sample.

The report uses4panels, a labelled time series, a first-maximum annotation,
category summaries, a distribution, consistent units, zero baselines for
ordinary positive bars and a white export background. View its files at
their intended reading size; additional DPI cannot repair tiny text.

## Verification

Authoring executes all72 snippets and embeds24 real PNG outputs. Static
checks compare every older lesson and all other application/storage code
with commit29e3eeb, permitting only the single figure-renderer branch.
Project checks inspect actual totals, source preservation, exported pixels,
PNG/SVG/PDF signatures, exact plot data, figure cleanup, validation failures
and refusal to overwrite an earlier bundle. Browser tests use fictional data
in an isolated profile to exercise all24parts and58questions, offline images,
navigation, exact-part search, notes, completion, studied-only practice,
reviews, refresh, mobile themes and console errors. Existing backup/import
regressions are also checked.

## Primary references

- [Matplotlib quick start](https://matplotlib.org/stable/users/explain/quick_start.html)
- [Constrained layout](https://matplotlib.org/stable/users/explain/axes/constrainedlayout_guide.html)
- [Colour maps](https://matplotlib.org/stable/users/explain/colors/colormaps.html)
- [Box plots](https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.boxplot.html)
- [Saving figures](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.savefig.html)

Explanations, fictional exercises and pictures are original. External links
are optional references; the offline course contains the essential material.
