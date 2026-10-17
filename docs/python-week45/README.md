# Week 45 — Regression & prediction

Open **Course → Week 45** in Study Hub. Six days, each with six teaching parts,
develop numerical prediction from an interpretable line through metrics,
polynomials, regularisation, feature design, trees and model comparison. Every
part includes original explanations, new-term boxes, worked output, mistakes,
practice, a mini challenge and explained quizzes. Take as many sessions as needed.

## Run the separate offline lab

Use Python 3.12 or 3.13. In this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe lab.py --output artifacts
```

Only installation needs internet. The dataset is generated locally; there is no
account, GPU, remote dataset or paid service. The website's lesson text, outputs
and six charts are embedded for offline reading without installing Python.
The lab does not read browser progress, notes or other project instances.

## Data and intended use

Each row is an **independent fictional event**, with registered guest count,
planned duration in hours, a Celsius temperature forecast available before the
event, and a planned promotion flag. The target is later demand in cups. These
records are simulated by `make_data`, including an interaction, a curved term
and random noise. They are not observed customer records or market research.

The deliberately known simulator helps verify learning mechanics. If a real
pricing/demand rule were exactly known, use the rule rather than approximate it
with ML. Scores here establish only behaviour on this simulation. They cannot
justify real inventory decisions or a causal claim about promotions.

## Evaluation contract

- Fix seed 45 and reserve72 of 360 rows before development. Keep the288 training
  rows for model comparison. An ordinary row split is appropriate only for the
  simulator's independent-event assumption; grouped venues and future-day series
  need a matching group/time design instead.
- Compare four predeclared pipelines: linear regression, degree-two engineered
  Ridge, random forest and gradient boosting. Include a training-median dummy
  baseline as a separate reference. **Primary selection criterion: mean CV MAE.**
- Reuse the same five training-only folds. Imputation, polynomial representation
  and scaling are fitted inside each fold's pipeline. Report fold MAE and its
  sample standard deviation; that deviation is not a confidence interval.
- Select with CV only, refit the chosen pipeline on all 288 training rows and
  evaluate once on the final 72. Report MAE, MSE, RMSE and R-squared for both the
  chosen model and the baseline. Predictions remain unrounded for scoring.
- `run_experiment` and the CLI are final reporting operations: they inspect the
  test set. Reading their output means the test is now seen. Later revisions
  require fresh independent evaluation for new performance claims.

`artifacts/report.json` records data status, split counts, settings, versions,
CV scores, selected method, final metrics and limitations.
`artifacts/test-predictions.csv` contains row ids, actual/predicted cups and
residuals defined as **actual minus predicted**. No executable model pickle is
loaded or exported. Rerunning the setup checks repeatability, not new evidence.

## Study route

1. **Linear regression:** slope, intercept, least squares, multiple coefficients,
   residuals, assumptions and extrapolation.
2. **Metrics:** MAE, MSE, RMSE, R-squared, training baselines, error distributions
   and cost-aware interpretation.
3. **Polynomial & regularisation:** curved representations, complexity,
   scaling, Ridge, Lasso and development-only parameter choices.
4. **Feature engineering:** prediction-time availability, interactions, curved
   terms, categories, transformations and a same-fold feature ablation.
5. **Trees:** threshold-based prediction, depth, forests, sequential boosting,
   feature importance limits and fair validation comparisons.
6. **Project:** frozen split/folds, four-model comparison, selection, final
   evaluation, checked inference and an inspectable written report.

## Optional primary references

- [Linear models](https://scikit-learn.org/stable/modules/linear_model.html)
- [Regression metrics](https://scikit-learn.org/stable/modules/model_evaluation.html#regression-metrics)
- [Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html)
- [Pipeline composition](https://scikit-learn.org/stable/modules/compose.html)
- [Tree regression](https://scikit-learn.org/stable/modules/tree.html#regression)
- [Feature importance limitations](https://scikit-learn.org/stable/auto_examples/inspection/plot_permutation_importance.html)

Read Week 44 first for X/y, fit/predict/transform, leakage and split boundaries.
Week 46 develops classification; Week 47 develops evaluation and tuning further.
