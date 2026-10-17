# Week 47 — Model evaluation, tuning & pipelines

Open **Course → Week 47**. Six days with six teaching parts each cover the complete
selection procedure, interpretation, diagnostics and a local inference release.
Every part has explanations, first-use terms, syntax, executed examples, mistakes,
exercises, a mini challenge and explained quizzes. Take as long as needed.

## Install once, then practise offline

Use Python 3.12 or 3.13 in this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe lab.py --output artifacts
.\.venv\Scripts\python.exe api.py --bundle artifacts/model.json --port 8047
```

Open `http://127.0.0.1:8047/docs` to send a local prediction. Installation needs
internet once. Data generation, model fitting, explanation, export and local
serving then work offline. No account, GPU or remote dataset is required.
Starlette is pinned with FastAPI to retain the verified HTTPX TestClient contract;
a fresh install must not silently switch to a newer incompatible test-client API.
Study Hub's text, outputs and six charts are embedded and readable without Python.
The project never reads your browser progress or other app instances.

## Declared experiment

The lab uses a new fixed seed 47 simulation of 1200 independent subscriptions.
It does not retune Week 46's inspected test or claim fresh actual customer evidence.
Inputs are tenure months, recent weekly sessions, unresolved ticket count and
days inactive, recorded before a 30-day cancellation label. Label 1 is cancellation.
The same illustrative cost convention is retained: FP 1, FN 8, correct decisions 0.

1. Reserve a stratified 240-row final holdout; all selection uses the remaining 960.
2. A pipeline owns median imputation, standard scaling and logistic regression.
3. `TunedThresholdClassifierCV` selects a threshold using 3 internal folds, then
   refits that pipeline on its allowed fitting portion. Its declared threshold
   grid is 0, 0.1, ..., 1 plus 1.01 for never flagging.
4. `GridSearchCV` uses 3 further inner folds to choose C from 0.1/1/10 and class
   weight from None/balanced. It evaluates the entire threshold-fitting/refit
   procedure, rather than optimising a threshold on the evaluation labels.
5. Three outer folds evaluate that complete search. Each outer fit owns all
   preparation, parameter selection and threshold development. Outer scores
   describe the procedure; do not use them to redesign it and still call them
   untouched estimates. Negative scorer values are converted back to positive cost.
6. Run the declared search on all 960 training rows, then evaluate its frozen
   refitted model/threshold on the reserved 240. Compare with a never-flag reference.

The extra threshold-selection level is intentional. Parameter-selection folds
must not score decisions whose threshold was optimised using those same validation
answers. This is a bounded teaching search, not a competition for the best score.
All fitting runs on one CPU worker; no nested parallel oversubscription occurs.

`run_experiment` and `write_report` inspect the final test. After reading that
result, treat it as seen. Rerunning the simulation checks reproducibility, not
new independent real-world evidence. Fold spread is not a confidence interval,
and rare positive counts limit conclusions. The simulator and cost assumptions
do not establish causal intervention effects or actual customer performance.

## Explanations and diagnostics

`explain_rows` uses the fitted preprocessing and a declared 64-row training
background with `shap.maskers.Independent` and `shap.LinearExplainer`.
Base value plus contributions reconstructs **log-odds**, not probability.
Applying the sigmoid reconstructs the probability score. The background and
independent-feature explanation convention affect attributions; they are not
causal effects or automatic calibration evidence. The report explains one
training example so the final test does not become a feature-design worksheet.

Lessons also execute permutation importance, partial dependence, learning curves,
group/time splits and a nested Optuna TPE exercise. These are explicitly scoped
development drills. The main release uses the predeclared grid above; it does not
quietly choose among search methods based on final results.

## Inspectable numeric release

The CLI writes:

- `artifacts/report.json`: nested costs, selected settings, final counts, versions,
  evidence limits, a training-example SHAP explanation and the numeric-file hash.
- `artifacts/test-predictions.csv`: all final row ids, actual labels, scores and flags.
- `artifacts/model.json`: a validated four-input numeric logistic representation:
  imputation medians, scaler mean/scale, coefficients/intercept, threshold, feature
  order, format version and training metadata.

`bundle.py` validates dimensions, finite values, positive scales and the exact
feature-order/format contract. Its numeric prediction is tested against the full
fitted sklearn pipeline, including missing-input transformation. It does not
deserialize executable Python objects. This format supports only this reviewed
binary linear pipeline, not arbitrary estimators or an automatic model converter.
The stored hash detects file changes when compared with a trusted report; a hash
is not by itself proof of origin. Training-version metadata is recorded, while
numeric inference is verified under the pinned environment.

The separate joblib lesson loads only a file it just created in its owned practice
folder. Pickle/joblib can execute code when loading and require trusted provenance
and compatible environments. The API has no model-upload or training endpoint.

## API contract and boundaries

`api.py` binds to 127.0.0.1. It loads one validated numeric bundle before startup;
`GET /health` returns readiness/version and `POST /predict` accepts 1–50 snapshots.
The four inputs are required, finite and nonnegative, with whole session/ticket
counts. Extra fields, booleans in count fields, missing values and oversized
batches are rejected. Broad structural limits are not a guarantee of training
support or real-world validity. The API requests complete snapshots even though
the underlying numeric representation preserves the training imputation policy.

Example request:

```json
{"rows":[{"tenure_months":12.0,"weekly_sessions":3,"unresolved_tickets":1,"days_inactive":8.0}]}
```

The response names the model version, positive label and threshold, then gives
one score and flag per row. Flags use score>=threshold. They are model decisions,
not observed cancellations. `lesson_support.running_api` owns a temporary numeric
file and a real loopback server for executable examples, then stops it and cleans
its own folder. The tests also exercise actual HTTP startup and prediction.

This is a **local release lab**, not a public production deployment. GitHub Pages
publishes the learning material; it cannot run this Python API. A public service
needs a separate host and reviewed authentication, transport, limits, monitoring,
version/rollback and data-handling configuration. Weeks 42–43 provide that background.

## Study route

1. Match K-fold, stratified, grouped and chronological evaluation to the task.
2. Compare grid, random and TPE search with proper nesting and fixed budgets.
3. Tune the whole pipeline, including fitted preparation and threshold selection.
4. Interpret importance, PDP and local SHAP contributions within their limits.
5. Diagnose learning curves, errors, labels and distribution changes.
6. Export, verify, version and call a local inference release.

## Optional primary references

- [Nested evaluation](https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html)
- [Parameter search](https://scikit-learn.org/stable/modules/grid_search.html)
- [Threshold tuning](https://scikit-learn.org/stable/modules/classification_threshold.html)
- [Pipeline composition](https://scikit-learn.org/stable/modules/compose.html)
- [SHAP LinearExplainer](https://shap.readthedocs.io/en/stable/generated/shap.LinearExplainer.html)
- [Optuna TPE](https://optuna.readthedocs.io/en/stable/reference/samplers/generated/optuna.samplers.TPESampler.html)
- [Model persistence](https://scikit-learn.org/stable/model_persistence.html)
- [FastAPI request bodies](https://fastapi.tiangolo.com/tutorial/body/)

Explanations and exercises are original. Outputs come from executing the supplied
code. These links are optional; the authored lesson remains readable offline.
