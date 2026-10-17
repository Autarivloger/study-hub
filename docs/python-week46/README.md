# Week 46 — Classification

Open **Course → Week 46** in Study Hub. Six days, each with six teaching parts,
cover category prediction, logistic regression, confusion counts, precision,
recall, F1, ROC/PR curves, thresholds, imbalance and tree ensembles. Each part
has original explanations, new-term boxes, syntax, executed output, mistakes,
practice, a mini challenge and explained quizzes. Take as many sessions as needed.

## Run the separate offline lab

Use Python 3.12 or 3.13. From this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe lab.py --output artifacts
```

The first installation needs internet. Afterwards, this lab generates its data
locally. No account, remote dataset or GPU is required. `xgboost-cpu` installs the
CPU-only distribution, imported as `xgboost`; install it in this fresh environment
rather than alongside a different XGBoost distribution. The Study Hub text,
executed outputs and six charts are embedded for offline reading without Python.
The lab never reads browser progress, notes, accounts or other project instances.

## Data and question

Predict **cancellation within the next 30 days** for independent fictional
subscriptions. Label 1 means cancellation; label 0 means retention. The four
numeric inputs are tenure in months, recent weekly sessions, unresolved ticket
count and days inactive, all recorded before the prediction boundary. A known
simulator generates stochastic labels; these are not real customer observations.
Day 2 also uses the packaged Iris measurements for an actual-data logistic
regression exercise, with a separately stated botanical label mapping.

The simulator is educational. Its scores establish no real customer performance,
causal retention intervention, revenue forecast or suitable production policy.
Repeated snapshots of actual accounts would need grouped/time-aware evaluation,
and labels would need the complete follow-up period to avoid treating pending
outcomes as retained accounts.

## Selection and final evaluation

- Reserve stratified **720/240/240** training/validation/final-test rows with seed 46.
  Fit imputation, scaling and models on training only. Keep validation/test at
  the original simulated prevalence.
- Compare five predeclared candidates: ordinary logistic, class-weighted logistic,
  random forest, gradient boosting and CPU XGBoost. Select each threshold using
  validation labels only, then select the model by that validation cost.
- Illustrative cost: **false positive1 unit; false negative8 units**. This is a
  teaching objective, not measured business loss. The threshold grid is declared
  in `THRESHOLDS`; flag when positive score **>=** threshold. Threshold 1.01 is
  the explicit never-flag sentinel. An exact threshold-cost tie prefers the
  larger threshold; an exact model-cost tie prefers the alphabetically first name.
- Freeze both the selected training fit and its threshold. There is **no silent
  training-plus-validation refit**, which could change score behaviour after
  threshold selection. The final 240 rows are reported only after selection.
- Report the same model at threshold 0.5 and its selected threshold, plus a
  never-flag reference. Include TN/FP/FN/TP, accuracy, precision, recall, F1,
  balanced accuracy, ROC AUC, average precision, Brier score and illustrative cost.
- One validation set chooses several models and thresholds, so selection can
  overfit development feedback. The final holdout is essential; more demanding
  evaluation and tuning designs follow in Week 47.

`run_experiment`, `write_report` and the CLI inspect the final test. After reading
those results, consider the test seen; subsequent changes require fresh relevant
evaluation for new claims. Rerunning the same simulation checks reproducibility,
not independent real-world evidence. A flag is a model decision, not verified truth.

### Observed result of this fixed teaching run

Validation selects balanced logistic at threshold 0.7. On the final 240 cases its
illustrative cost is 98 units, compared with 96 for never flagging. The same fit at 0.5
costs 87, but choosing that rule now because of the final result would use test
feedback. The selected procedure **did not improve the predeclared final cost**.
Its ROC AUC is about 0.802 at both thresholds; ranking improvement and useful
decisions are different questions. The lesson preserves this result rather than
changing the seed or objective to manufacture success. Further work needs a new
development plan and independent evaluation, with more relevant observed events.

## Training-only resampling

`oversample_training` duplicates minority training positions. It never resamples
validation or final test rows. If adapting this to cross-validation, resample
inside each fitting fold; resampling before splitting can put copies of the same
source in fitting and evaluation. Duplicates add weight, not new evidence.
Class weights and resampling can change score calibration. Evaluate on natural
prevalence and do not describe weighted `predict_proba` values as automatically
calibrated population probabilities.

## Inspect the artifacts

`artifacts/report.json` records selection, costs, threshold rule, candidate scores,
versions, final metrics and limitations. `artifacts/test-predictions.csv` records
every final source id, actual label, positive score and selected flag. Confusion
counts and cost can be recalculated from these pairs. No executable pickle is
loaded or exported.

## Study route

1. **Fundamentals:** binary/multiclass/multilabel tasks, positive labels,
   probabilities, decision boundaries, baseline and prediction-time availability.
2. **Logistic regression:** sigmoid, odds/log-odds, packaged real-data fit,
   coefficient interpretation, regularisation, log loss and calibration.
3. **Metrics:** accuracy traps, all four confusion cells, precision/recall,
   F1, zero-denominator conventions and multiclass averaging.
4. **Curves and thresholds:** rank scores, ROC AUC, precision-recall/AP,
   threshold tradeoffs, validation-only cost selection and reporting limits.
5. **Imbalance:** prevalence, class weights, training-only duplication,
   undersampling, leakage and a common natural-prevalence comparison.
6. **Ensembles and project:** forests, boosting, CPU XGBoost, validation-only
   model/threshold selection, feature importance limits and final artifacts.

## Optional primary references

- [LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html)
- [Classification metrics](https://scikit-learn.org/stable/modules/model_evaluation.html#classification-metrics)
- [Threshold tuning](https://scikit-learn.org/stable/modules/classification_threshold.html)
- [Probability calibration](https://scikit-learn.org/stable/modules/calibration.html)
- [Average precision](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html)
- [XGBoost estimator interface](https://xgboost.readthedocs.io/en/stable/python/sklearn_estimator.html)

Read Week 44 for estimator interfaces and leakage, and Week 45 for model-comparison
discipline. Explanations and exercises are original; outputs are executed rather
than guessed. Library documentation links are optional further reading.
