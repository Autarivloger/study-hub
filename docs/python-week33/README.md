# Python Week33 — Statistics for data work

Six days, **28 parts**, **56 practice prompts**, **66 explained quiz questions**,
**84 executed examples/solutions** and **28 embedded chart pictures**.
Existing Day7 Review & rest shuffles this week's practice prompts.

## Study sequence

1. Five parts: mean/median/modes; variance and SD by hand; explicit ddof;
   quartile conventions and IQR; skew, unknowns and flags; weighted rates.
2. Four parts: normal density versus interval probability; discrete and
   continuous uniform; fixed-trial binomial; Poisson rates and exposure.
3. Four parts: event rules and overlap; conditional denominators; Bayes and
   base rates; exact counting versus10000-draw Monte Carlo checks.
4. Five parts: population/frame/unit/bias; sampling distributions and CLT;
   SD versus SE; mean t intervals and simulated coverage; bootstrap units.
5. Five parts: null/alternative/p/alpha/errors/power; Welch mean difference
   and interval; paired differences; contingency counts and sparse-table
   checks; effect magnitude, multiplicity and marginal interval limits.
6. Five parts: Pearson shape checks; Spearman ranks/ties; OLS/residuals/R²;
   group composition and confounding; real-data Iris statistics capstone.

Every part uses the established objective, first-use boxes, explanation,
syntax, complete example/output, actual chart, walkthrough, common mistake,
practice, mini challenge, solutions, quiz and existing notes/navigation.
Code and storage functions are unchanged; existing saved IDs, progress,
search, learned-only reviews/practice and backup/import are preserved.

## Offline setup

    python -m pip install "numpy>=2,<3" "pandas>=3,<4" "matplotlib>=3.10,<3.11" "scipy>=1.15,<2"

Verified with Python3.12, NumPy2.3.5, pandas3.0.1, Matplotlib3.10.9 and
SciPy1.18.1. Initial installation needs internet. Every lesson, essential
explanation, output and preview is embedded in study-hub.html; local examples
and the supplied data run without network afterward. Python is run outside
the website. Snippets reuse chart.png: use a fresh practice folder.

## Real-data project

Keep statistics_report.py and iris.data together. From this folder:

    python statistics_report.py iris.data statistics-run-01
    python statistics_report.py --help

Use statistics-run-02 for the next run. The script refuses an existing
destination and retains raw source bytes. It validates input, checks group
sizes/variation and expected frequencies, stages an owned temporary bundle
and publishes seven files together:

- overview.png: distributions, species boxes, observed table and pooled fit.
- descriptive.csv: count, mean, median, sample SD, min and max by species.
- contingency.csv and expected.csv: observed and null-expected counts.
- regression_rows.csv: original row label, species, fitted values/residuals.
- analysis.json: effects, interval, raw/adjusted p, coefficients and source hash.
- interpretation.txt: the meaning and limitations of every analysis.

The original file has150 plant records with four positive measurements in
centimetres and three species,50 each. No field is imputed; invalid/unknown
values stop the run. Source limits are1MiB/10000rows. Identical measurement
rows are retained because values do not establish specimen identity.
**See SOURCE.md for attribution, CC BY4.0 terms, hash and historical errors.**

### Explicit teaching analysis choices

- Test1: independent-sample Welch, two-sided, mean setosa sepal length minus
  mean versicolor sepal length. Report n, signed cm difference, t, df, raw p
  and a **marginal95%** difference interval.
- Test2: species versus sepal width>=3cm, a fixed pedagogical threshold;
  Pearson chi-square with correction=False. All expected cells must be>=5.
  Report counts, expectations, statistic/df, p and Cramer's V.
- Exactly these two comparisons form the teaching Bonferroni family:
  min(1,2*p). Both raw and adjusted p-values are retained. Adjusted p-values
  do not make the reported marginal interval simultaneously95%.
- Pearson, Spearman, within-species coefficients, pooled OLS slope/intercept,
  residuals and in-sample R² are **descriptive exploration**, not another
  family of confirmatory significance claims. The fit mixes species.

These are reproducible exploratory choices, not a claimed preregistered study.
The historic collection is not established here as a random sample of a
specified modern population. Independence and other model assumptions remain
conditional. The report cannot prove species causes a measurement change,
predict another population reliably, or identify a causal growth effect.

## Interpretation rules practised throughout

Name units and denominators; do not replace unknown with zero; a flag is not
proof of invalidity. Set variance divisors and quantile conventions explicitly.
SD and mean SE differ. CLT concerns suitable sums/means under conditions,
not raw-data normalisation or a universal n30 rule. A95% interval describes
procedure coverage under assumptions; it is not automatically a posterior
probability or an individual prediction range. P is not P(null true), effect
magnitude or practical importance. Failure to reject does not prove equality.
Resampling reuses observed units. Correlation is not causation; R² is not
percent correct future predictions. Tiny positive p-values use scientific
notation rather than being presented as exact zero.

## Verification

84 examples/solutions are executed in isolated folders. Static checks compare
all older lessons and surrounding application/storage code with commitc6c58c0.
Browser checks cover28parts/66questions/images, notes, completion, refresh,
navigation, search, studied-only practice/review,375px themes and JS errors.
The existing actual merge/replace backup/import regression is retained.
Project checks verify source hash/counts, hand-computed descriptive values,
Welch effect/CI direction, expected-count arithmetic, test-family adjustment,
OLS residual identity, artifact contents, invalid inputs, no overwrite and
cleanup after export failure.

## Primary references

- [NumPy statistics](https://numpy.org/doc/stable/reference/routines.statistics.html)
- [SciPy statistics](https://docs.scipy.org/doc/scipy/reference/stats.html)
- [Welch test and interval](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html)
- [Paired t-test](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_rel.html)
- [Contingency test](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html)
- [Linear fit](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.linregress.html)
- [ASA p-value principles](https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf)
- [UCI Iris](https://archive.ics.uci.edu/dataset/53/iris)
