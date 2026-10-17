import json
import socket

import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import accuracy_score, confusion_matrix

from lab import (
    FEATURES,
    LABELS,
    build_model,
    load_data,
    make_splits,
    predict_checked,
    run_experiment,
    write_report,
)


def test_data_and_run_do_not_need_network(monkeypatch):
    def unavailable(*args, **kwargs):
        raise AssertionError("Network must not be used")

    monkeypatch.setattr(socket.socket, "connect", unavailable)
    X, y = load_data()
    assert X.shape == (150, 4)
    assert y.value_counts().to_dict() == {0: 50, 1: 50, 2: 50}
    assert run_experiment()[2]["scores"]["test"]["rows"] == 30


def test_split_is_disjoint_complete_stratified_and_repeatable():
    data = make_splits()
    groups = [set(data["X_" + part].index) for part in ["train", "valid", "test"]]
    assert [len(group) for group in groups] == [90, 30, 30]
    assert not (groups[0] & groups[1] or groups[0] & groups[2] or groups[1] & groups[2])
    assert set.union(*groups) == set(range(150))
    again = make_splits()
    for part, count in [("train", 30), ("valid", 10), ("test", 10)]:
        X, y = data["X_" + part], data["y_" + part]
        assert X.index.equals(y.index)
        assert y.value_counts().to_dict() == {0: count, 1: count, 2: count}
        pd.testing.assert_frame_equal(X, again["X_" + part])


def test_unseen_extremes_do_not_change_fitted_statistics():
    data = make_splits()
    model = build_model().fit(data["X_train"], data["y_train"])
    np.testing.assert_allclose(model.named_steps["impute"].statistics_, data["X_train"].median())
    np.testing.assert_allclose(model.named_steps["scale"].mean_, data["X_train"].mean())
    before = model.named_steps["scale"].mean_.copy()
    unseen = data["X_test"].copy() * 1000
    model.predict(unseen)
    np.testing.assert_array_equal(model.named_steps["scale"].mean_, before)
    assert model.named_steps["scale"].n_samples_seen_ == 90


def test_report_metrics_are_derived_from_the_named_holdout():
    model, data, report = run_experiment()
    for part in ["train", "valid", "test"]:
        actual = data["y_" + part]
        predicted = model.predict(data["X_" + part])
        assert report["scores"][part]["accuracy"] == accuracy_score(actual, predicted)
        assert report["scores"][part]["correct"] == int((predicted == actual).sum())
        assert report["scores"][part]["baseline_accuracy"] == pytest.approx(1 / 3)
    assert (
        report["test_confusion_matrix"]
        == confusion_matrix(
            data["y_test"], model.predict(data["X_test"]), labels=[0, 1, 2]
        ).tolist()
    )
    assert sum(map(sum, report["test_confusion_matrix"])) == 30
    assert len(report["limitations"]) >= 3


def test_prediction_reorders_columns_and_preserves_rows():
    model, data, _ = run_experiment()
    rows = data["X_test"].iloc[:4]
    expected = predict_checked(model, rows)
    pd.testing.assert_series_equal(expected, predict_checked(model, rows[FEATURES[::-1]]))
    assert expected.index.equals(rows.index)
    assert set(expected) <= set(LABELS)
    missing = rows.copy()
    missing.iloc[0, 0] = np.nan
    assert len(predict_checked(model, missing)) == 4


@pytest.mark.parametrize(
    "kind", ["empty", "column", "duplicate", "text", "infinite", "negative", "unmeasured"]
)
def test_invalid_predictions_fail_clearly(kind):
    model, data, _ = run_experiment()
    rows = data["X_test"].iloc[:1].copy()
    if kind == "empty":
        rows = rows.iloc[:0]
    elif kind == "column":
        rows = rows.drop(columns=FEATURES[0])
    elif kind == "duplicate":
        rows.columns = [FEATURES[0]] * 4
    elif kind == "text":
        rows[FEATURES[0]] = "5 cm"
    elif kind == "infinite":
        rows.iloc[0, 0] = np.inf
    elif kind == "negative":
        rows.iloc[0, 0] = -1
    else:
        rows.iloc[0] = np.nan
    with pytest.raises(ValueError):
        predict_checked(model, rows)


def test_exports_match_predictions_and_repeat_without_mutating_source(tmp_path):
    X, _ = load_data()
    report = write_report(tmp_path)
    assert json.loads((tmp_path / "report.json").read_text()) == report
    rows = pd.read_csv(tmp_path / "test-predictions.csv")
    assert len(rows) == 30 and rows.row_id.is_unique
    assert (rows.actual == rows.predicted).mean() == report["scores"]["test"]["accuracy"]
    assert write_report(tmp_path) == report
    pd.testing.assert_frame_equal(load_data()[0], X)
