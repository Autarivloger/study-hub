"""Nested evaluation of an entire fitted pipeline and decision-threshold procedure."""

import argparse
import hashlib
import json
from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import expit
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, confusion_matrix, make_scorer, roc_auc_score
from sklearn.model_selection import (
    GridSearchCV,
    StratifiedKFold,
    TunedThresholdClassifierCV,
    cross_validate,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from bundle import FEATURES, export_bundle, predict_frame, save_bundle

SEED = 47
FP_COST, FN_COST = 1, 8


def make_data(n=1200, seed=SEED):
    """A new fixed simulation, not fresh evidence about actual customers."""
    rng = np.random.default_rng(seed)
    X = pd.DataFrame(
        {
            "tenure_months": rng.uniform(1, 36, n),
            "weekly_sessions": rng.poisson(5, n),
            "unresolved_tickets": rng.poisson(1, n),
            "days_inactive": np.minimum(rng.exponential(8, n), 60),
        }
    )
    log_odds = -3.2 - 0.025 * X.tenure_months - 0.18 * X.weekly_sessions
    log_odds += 0.65 * X.unresolved_tickets + 0.07 * X.days_inactive
    y = pd.Series(rng.binomial(1, expit(log_odds)), name="cancelled_within_30_days")
    return X, y


def make_splits():
    X, y = make_data()
    Xt, Xh, yt, yh = train_test_split(X, y, test_size=0.2, stratify=y, random_state=SEED)
    return {"X_train": Xt, "X_test": Xh, "y_train": yt, "y_test": yh}


def decision_cost(actual, predicted):
    y, p = np.asarray(actual), np.asarray(predicted)
    return float(np.mean(FP_COST * ((y == 0) & (p == 1)) + FN_COST * ((y == 1) & (p == 0))))


COST_SCORER = make_scorer(decision_cost, greater_is_better=False)


def make_pipeline(C=1.0, class_weight=None):
    return Pipeline(
        [
            ("fill", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("model", LogisticRegression(C=C, class_weight=class_weight, max_iter=2000, tol=1e-7)),
        ]
    )


def make_tuned(C=1.0, class_weight=None):
    return TunedThresholdClassifierCV(
        make_pipeline(C, class_weight),
        scoring=COST_SCORER,
        thresholds=np.r_[np.linspace(0, 1, 11), 1.01],
        cv=StratifiedKFold(n_splits=3, shuffle=True, random_state=SEED + 1),
        refit=True,
        n_jobs=1,
    )


def make_search():
    return GridSearchCV(
        make_tuned(),
        {
            "estimator__model__C": [0.1, 1.0, 10.0],
            "estimator__model__class_weight": [None, "balanced"],
        },
        cv=StratifiedKFold(n_splits=3, shuffle=True, random_state=SEED + 2),
        scoring=COST_SCORER,
        refit=True,
        n_jobs=1,
        error_score="raise",
    )


def nested_evaluate(X, y):
    """Outer folds evaluate the declared search, including threshold fitting/refit."""
    return cross_validate(
        make_search(),
        X,
        y,
        cv=StratifiedKFold(n_splits=3, shuffle=True, random_state=SEED + 3),
        scoring={"cost": COST_SCORER, "ap": "average_precision"},
        return_estimator=True,
        n_jobs=1,
        error_score="raise",
    )


def final_metrics(y, scores, decisions):
    c = confusion_matrix(y, decisions, labels=[0, 1])
    tn, fp, fn, tp = map(int, c.ravel())
    return {
        "rows": len(y),
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "tp": tp,
        "cost_per_row": decision_cost(y, decisions),
        "total_cost": FP_COST * fp + FN_COST * fn,
        "roc_auc": float(roc_auc_score(y, scores)),
        "average_precision": float(average_precision_score(y, scores)),
        "precision": float(tp / (tp + fp)) if tp + fp else 0.0,
        "recall": float(tp / (tp + fn)) if tp + fn else 0.0,
    }


def run_experiment():
    data = make_splits()
    nested = nested_evaluate(data["X_train"], data["y_train"])
    search = make_search().fit(data["X_train"], data["y_train"])
    tuned = search.best_estimator_
    p = tuned.predict_proba(data["X_test"])[:, list(tuned.classes_).index(1)]
    versions = {name: version(name) for name in ["scikit-learn", "numpy", "pandas"]}
    bundle = export_bundle(tuned, len(data["X_train"]), versions)
    numeric = predict_frame(bundle, data["X_test"])
    if not np.allclose(numeric.positive_score, p, atol=1e-12):
        raise AssertionError("Numeric release differs from fitted pipeline probabilities")
    if not np.array_equal(numeric.flag, tuned.predict(data["X_test"]).astype(bool)):
        raise AssertionError("Numeric release differs from fitted decision rule")
    report = {
        "data": "Simulated independent subscriptions; no actual customer evidence",
        "seed": SEED,
        "target": "1=cancellation within30days; 0=retained",
        "features": FEATURES,
        "train_rows": len(data["X_train"]),
        "test_rows": len(data["X_test"]),
        "protocol": "outer3 -> parameter-selection3 -> threshold-selection3; every fit owns preprocessing",
        "objective": {"fp_cost": FP_COST, "fn_cost": FN_COST, "unit": "illustrative"},
        "outer_cost_per_row": (-nested["test_cost"]).tolist(),
        "outer_average_precision": nested["test_ap"].tolist(),
        "outer_selected_parameters": [model.best_params_ for model in nested["estimator"]],
        "full_training_selected_parameters": search.best_params_,
        "full_training_inner_cost": float(-search.best_score_),
        "selected_threshold": float(tuned.best_threshold_),
        "final": final_metrics(data["y_test"], p, numeric.flag.to_numpy().astype(int)),
        "never_flag": final_metrics(data["y_test"], np.zeros(len(p)), np.zeros(len(p), dtype=int)),
        "versions": versions,
        "limitations": [
            "The simulation and illustrative costs do not establish real customer performance or causal effects.",
            "Outer fold scores estimate this predeclared selection procedure; do not redesign it from outer results and call them untouched.",
            "The final test is inspected only after full-training selection; later revisions need fresh evaluation.",
            "Fold spread is not a confidence interval; few positive events limit conclusions.",
            "SHAP explanations are relative to a declared training background, in log-odds, not causal effects or automatic probability calibration.",
            "The loopback API is a local inference lab, not a public production deployment.",
        ],
    }
    return tuned, data, report, bundle


def explain_rows(tuned, background, rows):
    import shap

    pipeline = tuned.estimator_
    base = pipeline[:-1].transform(background)
    values = pipeline[:-1].transform(rows)
    masker = shap.maskers.Independent(base, max_samples=len(base))
    explanation = shap.LinearExplainer(pipeline.named_steps["model"], masker)(values)
    reconstructed = explanation.base_values + explanation.values.sum(axis=1)
    if not np.allclose(reconstructed, pipeline.decision_function(rows), atol=1e-9):
        raise AssertionError("SHAP does not reconstruct the fitted log-odds")
    return explanation


def write_report(folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    tuned, data, report, bundle = run_experiment()
    save_bundle(bundle, folder / "model.json")
    predicted = predict_frame(bundle, data["X_test"])
    pd.DataFrame(
        {
            "row_id": data["X_test"].index,
            "actual": data["y_test"].to_numpy(),
            "positive_score": predicted.positive_score.to_numpy(),
            "flag": predicted.flag.astype(int).to_numpy(),
        }
    ).to_csv(folder / "test-predictions.csv", index=False)
    report["numeric_bundle_sha256"] = hashlib.sha256(
        (folder / "model.json").read_bytes()
    ).hexdigest()
    explanation = explain_rows(
        tuned, data["X_train"].sample(n=64, random_state=SEED), data["X_train"].iloc[:1]
    )
    report["training_example_shap"] = {
        "space": "log-odds; independent training background of64rows",
        "base_value": float(explanation.base_values[0]),
        "contributions": dict(zip(FEATURES, map(float, explanation.values[0]), strict=True)),
    }
    (folder / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    r = write_report(args.output)
    print("Outer fold costs:", [round(v, 3) for v in r["outer_cost_per_row"]])
    print("Full-training choice:", r["full_training_selected_parameters"])
    print("Threshold:", round(r["selected_threshold"], 3))
    print("Final cost / baseline:", r["final"]["total_cost"], r["never_flag"]["total_cost"])
    print("Saved numeric model, report and paired predictions in", args.output)
    print("Final test inspected; no public model service was deployed.")


if __name__ == "__main__":
    main()
