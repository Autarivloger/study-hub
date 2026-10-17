import json
import socket

import numpy as np
import pandas as pd
import pytest
from sklearn.base import clone
from sklearn.metrics import mean_absolute_error

import lab


@pytest.fixture(scope="module")
def experiment():
    return lab.run_experiment()


def test_simulation_is_repeatable_and_offline(monkeypatch):
    def unavailable(*args, **kwargs):
        raise AssertionError("Network must not be used")

    monkeypatch.setattr(socket.socket, "connect", unavailable)
    X, y = lab.make_data()
    again, labels = lab.make_data()
    assert X.shape == (360, 4) and y.shape == (360,)
    assert list(X.columns) == lab.FEATURES and (y >= 0).all()
    pd.testing.assert_frame_equal(X, again)
    pd.testing.assert_series_equal(y, labels)


def test_final_holdout_and_cv_membership_are_disjoint():
    d = lab.make_splits()
    train_ids, test_ids = set(d["X_train"].index), set(d["X_test"].index)
    assert len(train_ids) == 288 and len(test_ids) == 72
    assert not train_ids & test_ids and train_ids | test_ids == set(range(360))
    assert d["X_train"].index.equals(d["y_train"].index)
    seen = []
    for fit, valid in lab.make_folds(d["X_train"]):
        assert not set(fit) & set(valid)
        ids = set(d["X_train"].iloc[valid].index)
        assert not ids & test_ids
        seen.extend(ids)
    assert len(seen) == len(set(seen)) == 288


def test_cv_scores_match_manual_fold_refits(experiment):
    _, d, report = experiment
    candidate = lab.make_candidates()["engineered_ridge"]
    manual = []
    for fit, valid in lab.make_folds(d["X_train"]):
        model = clone(candidate).fit(d["X_train"].iloc[fit], d["y_train"].iloc[fit])
        np.testing.assert_allclose(
            model.named_steps["fill"].statistics_, d["X_train"].iloc[fit].median()
        )
        prediction = model.predict(d["X_train"].iloc[valid])
        manual.append(mean_absolute_error(d["y_train"].iloc[valid], prediction))
    np.testing.assert_allclose(manual, report["cv"]["engineered_ridge"]["fold_mae"])
    assert report["cv"]["engineered_ridge"]["mean_mae"] == pytest.approx(np.mean(manual))


def test_selection_depends_only_on_training_cv_not_holdout(monkeypatch, experiment):
    _, data, report = experiment
    altered = {key: value.copy() for key, value in data.items()}
    altered["y_test"] += 10000
    monkeypatch.setattr(lab, "make_splits", lambda: altered)
    _, _, changed = lab.run_experiment()
    assert changed["winner"] == report["winner"]
    assert changed["cv"] == report["cv"]
    assert changed["test_metrics"]["mae"] > 9000


def test_report_metrics_and_baseline_use_the_actual_holdout(experiment):
    model, d, r = experiment
    assert r["winner"] == lab.select_winner(r["cv"])
    assert len(r["cv"]) == 5  # four competing models plus a reference baseline
    predicted = model.predict(d["X_test"])
    assert r["test_metrics"] == lab.metrics(d["y_test"], predicted)
    median_prediction = np.full(len(d["y_test"]), d["y_train"].median())
    assert r["baseline_test_metrics"] == lab.metrics(d["y_test"], median_prediction)
    assert r["test_metrics"]["rmse"] ** 2 == pytest.approx(r["test_metrics"]["mse"])


def test_inference_preserves_state_and_reorders_named_inputs(experiment):
    model, d, _ = experiment
    rows = d["X_test"].iloc[:4]
    before = model.named_steps["fill"].statistics_.copy()
    expected = lab.predict_checked(model, rows)
    pd.testing.assert_series_equal(expected, lab.predict_checked(model, rows[lab.FEATURES[::-1]]))
    assert expected.index.equals(rows.index)
    np.testing.assert_array_equal(model.named_steps["fill"].statistics_, before)


@pytest.mark.parametrize(
    "kind",
    ["empty", "column", "text", "missing", "infinite", "fraction", "hours", "promo", "units"],
)
def test_invalid_event_inputs_fail_clearly(experiment, kind):
    model, d, _ = experiment
    rows = d["X_test"].iloc[:1].copy()
    if kind == "empty":
        rows = rows.iloc[:0]
    elif kind == "column":
        rows = rows.drop(columns="guests")
    elif kind == "text":
        rows["guests"] = "twenty"
    elif kind == "missing":
        rows["hours"] = np.nan
    elif kind == "infinite":
        rows["hours"] = np.inf
    elif kind == "fraction":
        rows["guests"] = 3.5
    elif kind == "hours":
        rows["hours"] = 0
    elif kind == "promo":
        rows["promotion"] = 2
    else:
        rows["forecast_c"] = 100
    with pytest.raises(ValueError):
        lab.predict_checked(model, rows)


def test_saved_predictions_reproduce_the_report(tmp_path):
    r = lab.write_report(tmp_path)
    saved = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    assert saved == r
    rows = pd.read_csv(tmp_path / "test-predictions.csv")
    assert len(rows) == 72 and rows.row_id.is_unique
    np.testing.assert_allclose(rows.residual, rows.actual_cups - rows.predicted_cups)
    assert rows.residual.abs().mean() == pytest.approx(r["test_metrics"]["mae"])
    assert len(r["limitations"]) >= 4
