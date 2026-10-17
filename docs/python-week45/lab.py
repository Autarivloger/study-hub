"""Offline regression teaching lab using explicitly simulated independent events."""

import argparse
import json
from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    root_mean_squared_error,
)
from sklearn.model_selection import KFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

SEED = 45
FEATURES = ["guests", "hours", "forecast_c", "promotion"]


def make_data(n=360, seed=SEED):
    """A reproducible simulator, not recorded demand from real customers.

    Each row is a separate fictional event, not a time series. All inputs are
    available before that event; the target is the later observed cup count.
    """
    rng = np.random.default_rng(seed)
    X = pd.DataFrame(
        {
            "guests": rng.integers(20, 241, n),
            "hours": rng.uniform(1, 5, n),
            "forecast_c": rng.uniform(5, 32, n),
            "promotion": rng.integers(0, 2, n),
        }
    )
    expected = (
        12
        + 1.1 * X.guests
        + 8 * X.hours
        + 0.055 * X.guests * X.hours
        + 0.22 * (X.forecast_c - 18) ** 2
        + 22 * X.promotion
    )
    y = pd.Series(np.maximum(0, np.rint(expected + rng.normal(0, 14, n))), name="cups")
    return X, y


def make_splits():
    X, y = make_data()
    Xt, Xh, yt, yh = train_test_split(X, y, test_size=0.2, random_state=SEED)
    return {"X_train": Xt, "X_test": Xh, "y_train": yt, "y_test": yh}


def regression_pipeline(model, polynomial=False, scale=True):
    steps = [("fill", SimpleImputer(strategy="median"))]
    if polynomial:
        steps.append(("poly", PolynomialFeatures(degree=2, include_bias=False)))
    if scale:
        steps.append(("scale", StandardScaler()))
    steps.append(("model", model))
    return Pipeline(steps)


def make_candidates():
    """Four predeclared models plus a separately identified reference baseline."""
    return {
        "baseline": regression_pipeline(DummyRegressor(strategy="median"), scale=False),
        "linear": regression_pipeline(LinearRegression()),
        "engineered_ridge": regression_pipeline(Ridge(alpha=1.0), polynomial=True),
        "random_forest": regression_pipeline(
            RandomForestRegressor(
                n_estimators=48, max_depth=8, min_samples_leaf=3, n_jobs=1, random_state=SEED
            ),
            scale=False,
        ),
        "gradient_boosting": regression_pipeline(
            GradientBoostingRegressor(n_estimators=60, max_depth=2, random_state=SEED),
            scale=False,
        ),
    }


def make_folds(X):
    """Reuse identical positional folds on training data for every candidate."""
    return list(KFold(n_splits=5, shuffle=True, random_state=SEED).split(X))


def compare_models(X_train, y_train):
    folds = make_folds(X_train)
    comparison = {}
    for name, model in make_candidates().items():
        scores = cross_validate(
            model,
            X_train,
            y_train,
            cv=folds,
            scoring={"mae": "neg_mean_absolute_error", "rmse": "neg_root_mean_squared_error"},
            n_jobs=1,
            error_score="raise",
        )
        mae = -scores["test_mae"]
        comparison[name] = {
            "fold_mae": mae.tolist(),
            "mean_mae": float(mae.mean()),
            "sd_mae": float(mae.std(ddof=1)),
            "mean_rmse": float((-scores["test_rmse"]).mean()),
        }
    return comparison


def select_winner(comparison):
    names = [name for name in comparison if name != "baseline"]
    return min(names, key=lambda name: (comparison[name]["mean_mae"], name))


def metrics(actual, predicted):
    return {
        "mae": float(mean_absolute_error(actual, predicted)),
        "mse": float(mean_squared_error(actual, predicted)),
        "rmse": float(root_mean_squared_error(actual, predicted)),
        "r2": float(r2_score(actual, predicted)),
    }


def run_experiment():
    """Select with training-only CV, then inspect the final reserved holdout."""
    data = make_splits()
    comparison = compare_models(data["X_train"], data["y_train"])
    winner = select_winner(comparison)
    model = make_candidates()[winner].fit(data["X_train"], data["y_train"])
    baseline = make_candidates()["baseline"].fit(data["X_train"], data["y_train"])
    predicted = model.predict(data["X_test"])
    report = {
        "data": "Simulated independent events; no recorded customers or market observations",
        "target": "later cup demand; predictions are unrounded numerical estimates",
        "features": FEATURES,
        "seed": SEED,
        "selection": "lowest mean training-only 5-fold CV MAE among four predeclared models",
        "winner": winner,
        "baseline": "training median; reference for the primary MAE criterion",
        "cv": comparison,
        "train_rows": len(data["X_train"]),
        "test_rows": len(data["X_test"]),
        "train_metrics": metrics(data["y_train"], model.predict(data["X_train"])),
        "test_metrics": metrics(data["y_test"], predicted),
        "baseline_test_metrics": metrics(data["y_test"], baseline.predict(data["X_test"])),
        "versions": {name: version(name) for name in ["scikit-learn", "numpy", "pandas"]},
        "limitations": [
            "The simulator was designed by the author; results cannot establish real demand accuracy.",
            "Rows are independent fictional events; repeated venues or future-day forecasting need a different split.",
            "CV fold standard deviation is not a confidence interval or prediction interval.",
            "Predictions are associations, not causal promotion effects or guaranteed integer demand.",
            "Once inspected, this final test is seen; further changes need fresh evaluation.",
        ],
    }
    return model, data, report


def predict_checked(model, rows):
    if not isinstance(rows, pd.DataFrame) or rows.empty:
        raise ValueError("Provide a nonempty DataFrame of event inputs")
    if not rows.columns.is_unique or set(rows.columns) != set(FEATURES):
        raise ValueError("Use exactly guests, hours, forecast_c and promotion")
    ordered = rows.loc[:, FEATURES]
    if any(not pd.api.types.is_numeric_dtype(dtype) for dtype in ordered.dtypes):
        raise ValueError("Use numeric inputs in the documented units")
    values = ordered.to_numpy(dtype=float, na_value=np.nan)
    if not np.isfinite(values).all():
        raise ValueError("Provide complete finite event inputs for this prediction interface")
    if (ordered.guests < 0).any() or (ordered.guests % 1 != 0).any() or (ordered.hours <= 0).any():
        raise ValueError("Guests must be nonnegative whole counts and hours must be positive")
    if not ordered.promotion.isin([0, 1]).all():
        raise ValueError("Promotion must be 0 or 1")
    if not ordered.forecast_c.between(-50, 60).all():
        raise ValueError("Check forecast units: use Celsius within the interface's -50 to 60 range")
    return pd.Series(model.predict(ordered), index=rows.index, name="predicted_cups")


def write_report(folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    model, data, report = run_experiment()
    predicted = model.predict(data["X_test"])
    (folder / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    pd.DataFrame(
        {
            "row_id": data["X_test"].index,
            "actual_cups": data["y_test"].to_numpy(),
            "predicted_cups": predicted,
            "residual": data["y_test"].to_numpy() - predicted,
        }
    ).to_csv(folder / "test-predictions.csv", index=False)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    report = write_report(args.output)
    print("Data: simulated independent event demand, not real customer evidence")
    for name, score in report["cv"].items():
        print(f"CV {name}: MAE={score['mean_mae']:.2f} cups; fold SD={score['sd_mae']:.2f}")
    print("Selected with training-only CV:", report["winner"])
    for name in ["test_metrics", "baseline_test_metrics"]:
        print(name, {key: round(value, 3) for key, value in report[name].items()})
    print("Saved report.json and test-predictions.csv in", args.output)
    print("Final test inspected. Do not tune against this reported result.")


if __name__ == "__main__":
    main()
