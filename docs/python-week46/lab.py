"""Offline classification lab: simulated 30-day subscription cancellation."""

import argparse
import json
from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import expit
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

SEED = 46
FEATURES = ["tenure_months", "weekly_sessions", "unresolved_tickets", "days_inactive"]
FP_COST = 1
FN_COST = 8
THRESHOLDS = np.r_[np.linspace(0, 1, 21), 1.01]


def make_data(n=1200, seed=SEED):
    """Independent fictional subscriptions, not observed customers or effects."""
    rng = np.random.default_rng(seed)
    X = pd.DataFrame(
        {
            "tenure_months": rng.uniform(1, 36, n),
            "weekly_sessions": rng.poisson(5, n),
            "unresolved_tickets": rng.poisson(1, n),
            "days_inactive": np.minimum(rng.exponential(8, n), 60),
        }
    )
    score = (
        -3.2
        - 0.025 * X.tenure_months
        - 0.18 * X.weekly_sessions
        + 0.65 * X.unresolved_tickets
        + 0.07 * X.days_inactive
    )
    y = pd.Series(rng.binomial(1, expit(score)), name="cancelled_within_30_days")
    return X, y


def make_splits():
    X, y = make_data()
    Xd, Xh, yd, yh = train_test_split(X, y, test_size=0.2, stratify=y, random_state=SEED)
    Xt, Xv, yt, yv = train_test_split(Xd, yd, test_size=0.25, stratify=yd, random_state=SEED)
    return {"X_train": Xt, "X_valid": Xv, "X_test": Xh, "y_train": yt, "y_valid": yv, "y_test": yh}


def classifier_pipeline(model, scale=True):
    steps = [("fill", SimpleImputer(strategy="median"))]
    if scale:
        steps.append(("scale", StandardScaler()))
    return Pipeline(steps + [("model", model)])


def make_candidates():
    return {
        "logistic": classifier_pipeline(LogisticRegression(C=1.0, max_iter=2000, tol=1e-7)),
        "balanced_logistic": classifier_pipeline(
            LogisticRegression(C=1.0, class_weight="balanced", max_iter=2000, tol=1e-7)
        ),
        "forest": classifier_pipeline(
            RandomForestClassifier(
                n_estimators=48, max_depth=7, min_samples_leaf=5, random_state=SEED, n_jobs=1
            ),
            scale=False,
        ),
        "boosting": classifier_pipeline(
            GradientBoostingClassifier(n_estimators=60, max_depth=2, random_state=SEED),
            scale=False,
        ),
        "xgboost": classifier_pipeline(
            XGBClassifier(
                n_estimators=60,
                max_depth=2,
                learning_rate=0.08,
                tree_method="hist",
                objective="binary:logistic",
                eval_metric="logloss",
                random_state=SEED,
                n_jobs=1,
            ),
            scale=False,
        ),
    }


def positive_scores(model, X):
    """Never assume that probability-column position implies the positive label."""
    position = list(model.classes_).index(1)
    return model.predict_proba(X)[:, position]


def binary_metrics(actual, scores, threshold=0.5):
    y, p = np.asarray(actual), np.asarray(scores, dtype=float)
    if y.ndim != 1 or p.shape != y.shape or set(np.unique(y)) != {0, 1}:
        raise ValueError("Use paired one-dimensional scores and both binary classes 0/1")
    if not np.isfinite(p).all() or ((p < 0) | (p > 1)).any():
        raise ValueError("Probability scores must be finite and within 0 to 1")
    if not np.isfinite(threshold) or not 0 <= threshold <= 1.01:
        raise ValueError("Use a finite threshold from 0 to 1.01")
    predicted = (p >= threshold).astype(int)
    tn, fp, fn, tp = map(int, confusion_matrix(y, predicted, labels=[0, 1]).ravel())
    return {
        "rows": len(y),
        "threshold": float(threshold),
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "tp": tp,
        "accuracy": float(accuracy_score(y, predicted)),
        "precision": float(precision_score(y, predicted, zero_division=0)),
        "recall": float(recall_score(y, predicted, zero_division=0)),
        "f1": float(f1_score(y, predicted, zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(y, predicted)),
        "roc_auc": float(roc_auc_score(y, p)),
        "average_precision": float(average_precision_score(y, p)),
        "brier": float(brier_score_loss(y, p)),
        "total_cost": FP_COST * fp + FN_COST * fn,
        "cost_per_row": float((FP_COST * fp + FN_COST * fn) / len(y)),
    }


def choose_threshold(actual, scores):
    rows = [binary_metrics(actual, scores, float(t)) for t in THRESHOLDS]
    # Declared tie-break: larger threshold when teaching cost is exactly tied.
    return min(rows, key=lambda row: (row["total_cost"], -row["threshold"]))


def oversample_training(X, y, seed=SEED):
    """Duplicate minority training positions only; never touch validation/test."""
    labels = np.asarray(y)
    groups = [np.flatnonzero(labels == label) for label in [0, 1]]
    if set(np.unique(labels)) != {0, 1} or len(X) != len(y):
        raise ValueError("Provide paired training rows containing both classes")
    rng = np.random.default_rng(seed)
    size = max(map(len, groups))
    positions = np.concatenate(
        [np.r_[group, rng.choice(group, size - len(group), replace=True)] for group in groups]
    )
    rng.shuffle(positions)
    return X.iloc[positions].reset_index(drop=True), y.iloc[positions].reset_index(drop=True)


def select_with_validation(data):
    fitted, comparison = {}, {}
    for name, model in make_candidates().items():
        model.fit(data["X_train"], data["y_train"])
        scores = positive_scores(model, data["X_valid"])
        comparison[name] = choose_threshold(data["y_valid"], scores)
        fitted[name] = model
    winner = min(comparison, key=lambda name: (comparison[name]["total_cost"], name))
    return fitted[winner], winner, comparison


def run_experiment():
    """Jointly select model/threshold on validation, freeze, then inspect test."""
    data = make_splits()
    model, winner, comparison = select_with_validation(data)
    threshold = comparison[winner]["threshold"]
    scores = positive_scores(model, data["X_test"])
    report = {
        "data": "Simulated independent subscriptions, not real customer churn evidence",
        "target": "1 = cancellation within 30 days; 0 = retained",
        "features": FEATURES,
        "seed": SEED,
        "split_rows": {part: len(data["X_" + part]) for part in ["train", "valid", "test"]},
        "selection": "lowest validation teaching cost; model-name tie-break; no final-test selection",
        "costs": {"false_positive": FP_COST, "false_negative": FN_COST, "unit": "illustrative"},
        "threshold_grid": THRESHOLDS.tolist(),
        "threshold_rule": "flag if positive score >= threshold; 1.01 means never flag",
        "winner": winner,
        "threshold": threshold,
        "validation_comparison": comparison,
        "test_at_selected_threshold": binary_metrics(data["y_test"], scores, threshold),
        "test_at_half": binary_metrics(data["y_test"], scores, 0.5),
        "test_never_flag_baseline": binary_metrics(data["y_test"], np.zeros(len(scores)), 0.5),
        "versions": {name: version(name) for name in ["scikit-learn", "xgboost-cpu", "numpy"]},
        "limitations": [
            "Synthetic labels and feature relationships do not establish real customer performance or causal effects.",
            "Costs are illustrative, not observed business losses or recommendations.",
            "One validation set chooses five models and thresholds; selection can overfit that development feedback.",
            "Keep the training fit after choosing the threshold; no silent train-plus-validation refit changes the scores.",
            "Weighted/resampled probability outputs need separate calibration assessment at natural prevalence.",
            "After reading the final test result, further revisions need fresh independent evaluation.",
        ],
    }
    return model, data, report


def predict_checked(model, rows, threshold):
    if not isinstance(rows, pd.DataFrame) or rows.empty:
        raise ValueError("Provide a nonempty DataFrame of subscription inputs")
    if not rows.columns.is_unique or set(rows.columns) != set(FEATURES):
        raise ValueError("Use exactly the four documented feature columns")
    ordered = rows.loc[:, FEATURES]
    if any(not pd.api.types.is_numeric_dtype(dtype) for dtype in ordered.dtypes):
        raise ValueError("Inputs must be numeric in the documented units")
    values = ordered.to_numpy(dtype=float, na_value=np.nan)
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("Inputs must be complete finite nonnegative measurements")
    if any(
        (ordered[column] % 1 != 0).any() for column in ["weekly_sessions", "unresolved_tickets"]
    ):
        raise ValueError("Session and ticket counts must be whole numbers")
    if not np.isfinite(threshold) or not 0 <= threshold <= 1.01:
        raise ValueError("Use a finite threshold from 0 to 1.01")
    p = positive_scores(model, ordered)
    return pd.DataFrame({"cancellation_score": p, "flag": p >= threshold}, index=rows.index)


def write_report(folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    model, data, report = run_experiment()
    scores = positive_scores(model, data["X_test"])
    (folder / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    pd.DataFrame(
        {
            "row_id": data["X_test"].index,
            "actual": data["y_test"].to_numpy(),
            "positive_score": scores,
            "flag": (scores >= report["threshold"]).astype(int),
        }
    ).to_csv(folder / "test-predictions.csv", index=False)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    r = write_report(args.output)
    print("Simulated subscriptions; no actual customer data")
    print("Selected with validation:", r["winner"], "threshold", r["threshold"])
    for name in ["test_never_flag_baseline", "test_at_half", "test_at_selected_threshold"]:
        row = r[name]
        print(
            name,
            {
                k: round(row[k], 3)
                for k in [
                    "accuracy",
                    "precision",
                    "recall",
                    "f1",
                    "roc_auc",
                    "average_precision",
                    "cost_per_row",
                ]
            },
        )
    print("Saved report.json and test-predictions.csv in", args.output)
    print("The final test is now inspected; later tuning needs fresh evaluation.")


if __name__ == "__main__":
    main()
