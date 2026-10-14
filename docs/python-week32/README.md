# Week 32 — Seaborn and statistical graphics

Six days, **26 parts**, **52 practice prompts**, **62 explained quiz questions**,
**78 executed examples/solutions** and **26 embedded chart pictures**.
Existing Day7 Review & rest reuses the week's shuffled practice questions.

## Study order

1. Four parts: tidy observations, semantic column mappings, Axes versus
   Figure-level ownership, melt and a scoped theme with inspected summaries.
2. Five parts: grouped histogram bins, density/area and denominators, KDE
   bandwidth/support, threshold ECDFs, rugs/discrete values and missing pairs.
3. Five parts: count versus unique learners, means/medians, spread versus
   uncertainty, raw-point overlays, violin/swarm limits and category choices.
4. Four parts: hue/size/style, default line aggregation, repeated learner
   trajectories and relational facets with stable mappings.
5. Four parts: FacetGrid, PairGrid, pairplot inclusion policies and correlation
   heatmaps with fixed colour limits, undefined values and pair counts.
6. Four parts: Plotly Express, hover/legend/ordering, standalone offline HTML,
   and an eight-chart exploratory capstone with an evidence ledger.

Every part includes first-use explanations, objective, syntax, self-contained
code, actual output, actual chart preview, walkthrough, mistake/fix, practice,
mini challenge, revealed solutions and a saved quiz. All older lessons,
application functions and storage code remain unchanged. Existing notes,
completion, search, learned-only practice/review and backups are reused.

## Local environment and offline boundaries

    python -m pip install "seaborn>=0.13.2,<0.14" "matplotlib>=3.10,<3.11" "pandas>=3,<4" "plotly>=6,<7"

Verified with Seaborn0.13.2, Matplotlib3.10.9, pandas3.0.1, Plotly6.9.0 and
Python3.12. Installation initially needs internet; the supplied data and
normal lesson/project runs do not. No sns.load_dataset downloads are used.

All essential teaching, code, solutions and static pictures are embedded in
study-hub.html. Python runs locally outside the website. Example snippets
reuse chart.png/chart.html, so run them in a fresh practice folder.

Plotly lesson previews use write_image, whose **optional** image-export stack
requires Kaleido and a compatible Chrome installation:

    python -m pip install "kaleido>=1,<2"

Omit write_image when generating only interactive HTML. The standalone EDA
project needs Plotly but not Kaleido. Its static charts use Matplotlib.

### Open the actual interactive demo

[Open the self-contained demo](interactive-demo.html), save that HTML file to
your device, and open the saved file offline. Hover displays exact fictional
details; legend clicks toggle categories; zoom/pan and reset change the view.
The library is bundled inline using include_plotlyjs=True. No CDN is needed.

A static picture has no hover. Merely visiting the hosted StudyHub page does
not guarantee that this separate demo/project folder was cached for offline
use. Save the HTML or download the project files. Any embedded data remains
readable to a recipient even if its trace is hidden by a legend control.

## Run the new fictional capstone

From this folder:

    python exploration_report.py practice_sessions.csv exploration-run-01
    python exploration_report.py --help

Choose exploration-run-02 for another run. Existing destinations are refused;
source bytes are retained. New output is staged in an owned temporary folder
and published as one bundle. Failed exports do not publish a partial bundle.

The CSV contains **24 sessions from12 fictional learners**, two sessions per
learner,8sessions per track, and1unknown score (23known outcomes). The first
session is Solo and the second Guided: mode and day coincide. The report
cannot isolate a mode effect, treat repeated rows as independent people or
establish any real teaching-quality, causal or population-inference claim.

The input contract checks exact headers/width, <=1MiB/10000records, nonblank
IDs/categories, unique session IDs and learner/day pairs, known category
labels, finite bounded numbers, integer days/tasks and at least3known scores.
Blank score is the only numeric missing token; invalid values are refused.
Days are1–31, minutes1–240, tasks0–100 and scores0–100; this particular report
additionally requires minutes<=60 to retain its fixed displayed histogram
coverage. Unknown scores stay unknown and are counted explicitly.

### The thirteen output files

- Eight individual chart PNGs: duration histogram, score ECDF, score/track
  boxes, track row counts, descriptive mode means, complete-pair scatter,
  descriptive day means and a Pearson correlation heatmap.
- overview.png combines the eight questions into a single report.
- interactive.html is a self-contained hover/zoom/legend chart.
- prepared_sessions.csv retains the data and unknown outcome.
- summary.json records row/unit/known counts, means and exact pair counts.
- interpretation.txt explains every view and its limitations.

Counts refer to sessions, not unique learners. Score views use known
outcomes; scatter omits one incomplete pair. Correlation uses pairwise known
rows; unknown/undefined is not converted to zero. Day2 has one fewer known
contributor. Mean bars deliberately use no inferential interval. SD spread,
bootstrap uncertainty and causal identification are different concepts.

## Verification

Authoring executes78 snippets in isolated folders and embeds26 real images,
including genuine Plotly static exports. Static checks compare old lessons
and every byte of surrounding application/storage code to commit779f9d5.
Browser checks cover every part/question/picture, navigation, notes/progress,
refresh, exact-part search, studied-only practice/review,375px themes and
console errors. Existing merge/replace backup/import regression is retained.
Project checks inspect actual chart data and denominators, invalid input,
source preservation, export failure and overwrite refusal. A separate browser
check loads the demo offline and exercises hover, legend and zoom/reset.

## Primary references

- [Plot function families](https://seaborn.pydata.org/tutorial/function_overview.html)
- [Distribution plots](https://seaborn.pydata.org/tutorial/distributions.html)
- [Categorical plots](https://seaborn.pydata.org/tutorial/categorical.html)
- [Error bars](https://seaborn.pydata.org/tutorial/error_bars.html)
- [Grid layouts](https://seaborn.pydata.org/tutorial/axis_grids.html)
- [Standalone HTML](https://plotly.com/python/interactive-html-export/)
- [Optional static export](https://plotly.com/python/static-image-export/)

Original explanations, fictional fixtures and exercises are included locally;
external sources are optional references rather than required lesson assets.
