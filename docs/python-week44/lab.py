"""Offline Iris classification lab. No network, accounts or model deserialization."""

import argparse
import json
from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

SEED = 44
FEATURES = list(load_iris().feature_names)
LABELS = list(load_iris().target_names)


def load_data():
    """The dataset ships inside scikit-learn; no fetch_* or HTTP request."""
    dataset = load_iris(as_frame=True)
    return dataset.data.copy(), dataset.target.copy()


def make_splits():
    """Fix a 60/20/20 stratified split before learning any statistics."""
    X, y = load_data()
    X_develop, X_test, y_develop, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=SEED
    )
    X_train, X_valid, y_train, y_valid = train_test_split(
        X_develop, y_develop, test_size=0.25, stratify=y_develop, random_state=SEED
    )
    return {
        "X_train": X_train,
        "X_valid": X_valid,
        "X_test": X_test,
        "y_train": y_train,
        "y_valid": y_valid,
        "y_test": y_test,
    }


def build_model():
    """Predeclared educational model; not a test-score-driven search."""
    return Pipeline(
        [
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("classify", KNeighborsClassifier(n_neighbors=5)),
        ]
    )


def run_experiment():
    """Train once; expose separate development and final holdout evidence."""
    data = make_splits()
    model = build_model().fit(data["X_train"], data["y_train"])
    baseline = DummyClassifier(strategy="most_frequent").fit(data["X_train"], data["y_train"])
    report = {
        "dataset": "scikit-learn bundled Iris; four flower measurements in cm",
        "seed": SEED,
        "model": "median imputer -> standard scaler -> 5-nearest neighbours",
        "selection": "fixed before final test inspection; no tuning in this run",
        "classes": LABELS,
        "features": FEATURES,
        "versions": {name: version(name) for name in ["scikit-learn", "numpy", "pandas"]},
        "scores": {},
        "limitations": [
            "Small historical three-class teaching dataset; not field identification.",
            "One fixed split is not an uncertainty estimate or deployment guarantee.",
            "Similarity predicts labels, not causal effects or botanical explanations.",
            "After inspecting the test, treat it as seen; use fresh data for new claims.",
        ],
    }
    for name in ["train", "valid", "test"]:
        X, y = data["X_" + name], data["y_" + name]
        predicted = model.predict(X)
        report["scores"][name] = {
            "rows": len(y),
            "correct": int((predicted == y.to_numpy()).sum()),
            "accuracy": float(accuracy_score(y, predicted)),
            "baseline_accuracy": float(accuracy_score(y, baseline.predict(X))),
        }
    test_predicted = model.predict(data["X_test"])
    report["test_confusion_matrix"] = confusion_matrix(
        data["y_test"], test_predicted, labels=[0, 1, 2]
    ).tolist()
    return model, data, report


def predict_checked(model, rows):
    """Validate the measurement contract and preserve caller row order."""
    if not isinstance(rows, pd.DataFrame) or rows.empty:
        raise ValueError("Provide a nonempty pandas DataFrame")
    if not rows.columns.is_unique or set(rows.columns) != set(FEATURES):
        raise ValueError("Use exactly the four named Iris measurement columns")
    ordered = rows.loc[:, FEATURES]
    if any(not pd.api.types.is_numeric_dtype(dtype) for dtype in ordered.dtypes):
        raise ValueError("Measurements must be numeric centimetres, not text")
    values = ordered.to_numpy(dtype=float, na_value=np.nan)
    if np.isinf(values).any() or (values <= 0).any():
        raise ValueError("Known measurements must be finite and positive")
    if np.isnan(values).all(axis=1).any():
        raise ValueError("A completely unmeasured flower cannot be classified")
    predicted = model.predict(ordered)
    return pd.Series([LABELS[int(label)] for label in predicted], index=rows.index)


def write_report(folder):
    """Export inspectable results; deliberately do not save executable pickles."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    model, data, report = run_experiment()
    (folder / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    predictions = pd.DataFrame(
        {
            "row_id": data["X_test"].index,
            "actual": [LABELS[int(n)] for n in data["y_test"]],
            "predicted": [LABELS[int(n)] for n in model.predict(data["X_test"])],
        }
    )
    predictions.to_csv(folder / "test-predictions.csv", index=False)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    report = write_report(args.output)
    for name, score in report["scores"].items():
        print(f"{name}: {score['correct']}/{score['rows']} = {score['accuracy']:.3f}")
    print("Saved report.json and test-predictions.csv in", args.output)
    print("This run inspected the test set. Do not tune against this result.")


if __name__ == "__main__":
    main()
