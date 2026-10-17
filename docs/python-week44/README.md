# Week 44 — Machine learning foundations

Read **Course → Week 44** in Study Hub. Six days each contain six teaching parts,
with explanations, syntax, worked output, mistakes, exercises, mini challenges
and explained quizzes. Take as long as needed; the part boundaries are study
checkpoints, not deadlines. Weeks 25–35 provide the NumPy, pandas and plotting
background. Week 45 develops regression and Week 46 develops classification.

## Run the independent practice lab

Use Python 3.12 or 3.13 in a fresh virtual environment. From this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe lab.py --output artifacts
```

The initial installation needs internet. After installation, the examples and
lab run offline: `load_iris` uses data bundled with scikit-learn. No account,
downloaded dataset, GPU or paid service is required. The Study Hub lesson text,
executed outputs and charts are embedded in the HTML and readable offline without
installing Python. The lab never reads browser progress or other project data.

## What the project actually does

Predict one of three Iris flower classes from four measurements in centimetres.
The small historical dataset has 150 rows. `make_splits` fixes stratified
90/30/30 training/validation/test partitions with seed 44 before any learned
preprocessing. `build_model` fixes a median imputer, standard scaler and
five-nearest-neighbours classifier. The majority-class baseline uses the same
training labels and evaluation rows. No model search or hidden remote service runs.

`lab.py` exports `artifacts/report.json` and `artifacts/test-predictions.csv`.
The report includes counts, accuracies, the baseline, a labelled confusion matrix,
versions, split rules and limitations. Rows of the matrix are actual classes;
columns are predicted classes, in the report's `classes` order. No executable
serialized model is loaded or exported.

**Test discipline:** the CLI is a final reporting run that inspects the test set.
During development, fit on training rows and make choices using validation only.
If you revise the model after reading the final test result, that test is now seen;
obtain a new independent evaluation rather than describing repeated tuning as an
untouched test. A rerun reproduces this demonstration; it is not new evidence.

## Study route

1. **What ML is and isn't:** examples versus rules, task types, features/targets,
   baselines, generalisation and ten problem-framing exercises.
2. **The workflow:** prediction-time contract, provenance, split boundaries,
   a prewritten evaluation plan and reproducibility.
3. **scikit-learn:** environment, `fit`, `predict`, `transform`, a nearest-neighbour
   classifier, a complete short example and a fair baseline.
4. **Train/test splits:** paired indices, stratification, train/validation/test,
   memorisation, data leakage, group/time splits and bias/variance intuition.
5. **Preparation:** missing values, scaling, categorical encodings,
   `ColumnTransformer`, `Pipeline` and checks on unseen input.
6. **Project:** data audit, frozen pipeline, evaluation, error analysis, checked
   prediction input and an inspectable report with honest limitations.

The tiny mixed-type tables in Day 5 are explicitly fictional transformation
drills. They are not evidence that a useful real prediction model has been built.
Iris scores likewise do not establish safe field identification, causal effects,
performance on other species or robustness to measurement changes.

## Optional primary references

- [scikit-learn getting started](https://scikit-learn.org/stable/getting_started.html)
- [Iris dataset and provenance](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_iris.html)
- [Splitting data](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html)
- [Leakage and common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html)
- [Pipeline and ColumnTransformer](https://scikit-learn.org/stable/modules/compose.html)
- [OneHotEncoder](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OneHotEncoder.html)

Explanations and practice tasks are original. Library interfaces were checked
against the primary documentation; lesson outputs are executed, not invented.
