import json
import socket

import numpy as np
import pandas as pd
import pytest

import lab


@pytest.fixture(scope="module")
def experiment():
    return lab.run_experiment()


def test_generation_and_experiment_need_no_network(monkeypatch):
    def unavailable(*args, **kwargs):
        raise AssertionError("No network is allowed")

    monkeypatch.setattr(socket.socket, "connect", unavailable)
    X, y = lab.make_data()
    again, labels = lab.make_data()
    pd.testing.assert_frame_equal(X, again)
    pd.testing.assert_series_equal(y, labels)
    assert X.shape == (1200, 4)
    assert 0 < y.mean() < 0.25
    assert lab.run_experiment()[2]["split_rows"] == {"train": 720, "valid": 240, "test": 240}


def test_split_membership_pairing_and_prevalence():
    d = lab.make_splits()
    groups = [set(d["X_" + part].index) for part in ["train", "valid", "test"]]
    assert not (groups[0] & groups[1] or groups[0] & groups[2] or groups[1] & groups[2])
    assert set.union(*groups) == set(range(1200))
    for part in ["train", "valid", "test"]:
        assert d["X_" + part].index.equals(d["y_" + part].index)
        assert set(d["y_" + part]) == {0, 1}
        assert abs(d["y_" + part].mean() - lab.make_data()[1].mean()) < 0.01


def test_hand_computed_confusion_metrics_and_score_ranking():
    row = lab.binary_metrics([0, 0, 1, 1], [0.1, 0.7, 0.8, 0.4], 0.5)
    assert [row[k] for k in ["tn", "fp", "fn", "tp"]] == [1, 1, 1, 1]
    assert row["accuracy"] == row["precision"] == row["recall"] == row["f1"] == 0.5
    assert row["total_cost"] == lab.FP_COST + lab.FN_COST
    assert row["roc_auc"] == pytest.approx(0.75)
    changed = lab.binary_metrics([0, 0, 1, 1], [0.1, 0.7, 0.8, 0.4], 0.3)
    assert changed["recall"] == 1
    assert changed["roc_auc"] == row["roc_auc"]


def test_threshold_selection_and_declared_tie_break():
    y, scores = [0, 0, 1, 1], [0.1, 0.7, 0.8, 0.4]
    selected = lab.choose_threshold(y, scores)
    rows = [lab.binary_metrics(y, scores, float(t)) for t in lab.THRESHOLDS]
    assert selected == min(rows, key=lambda row: (row["total_cost"], -row["threshold"]))
    assert lab.binary_metrics(y, scores, 1.01)["tp"] == 0
    assert lab.binary_metrics(y, scores, 0)["tn"] == 0


def test_final_labels_cannot_change_model_or_threshold(monkeypatch, experiment):
    _, d, r = experiment
    altered = {key: value.copy() for key, value in d.items()}
    altered["y_test"] = 1 - altered["y_test"]
    monkeypatch.setattr(lab, "make_splits", lambda: altered)
    _, _, changed = lab.run_experiment()
    assert changed["winner"] == r["winner"]
    assert changed["threshold"] == r["threshold"]
    assert changed["validation_comparison"] == r["validation_comparison"]


def test_oversampling_only_duplicates_training_sources():
    d = lab.make_splits()
    X, y = lab.oversample_training(d["X_train"], d["y_train"])
    assert y.value_counts()[0] == y.value_counts()[1]
    original_pairs = set(map(tuple, d["X_train"].assign(label=d["y_train"]).to_numpy()))
    for row in X.assign(label=y).itertuples(index=False, name=None):
        assert row in original_pairs
    assert len(d["X_valid"]) == len(d["X_test"]) == 240


def test_report_uses_frozen_training_state_and_final_prediction_pairs(experiment):
    model, d, r = experiment
    assert len(r["validation_comparison"]) == 5
    expected = min(
        r["validation_comparison"], key=lambda n: (r["validation_comparison"][n]["total_cost"], n)
    )
    assert expected == r["winner"]
    np.testing.assert_allclose(model.named_steps["fill"].statistics_, d["X_train"].median())
    p = lab.positive_scores(model, d["X_test"])
    assert r["test_at_selected_threshold"] == lab.binary_metrics(d["y_test"], p, r["threshold"])
    assert r["test_at_half"]["roc_auc"] == r["test_at_selected_threshold"]["roc_auc"]
    baseline = r["test_never_flag_baseline"]
    assert baseline["tp"] == baseline["fp"] == 0
    assert baseline["recall"] == 0


def test_checked_input_reorders_columns_and_preserves_rows(experiment):
    model, d, r = experiment
    rows = d["X_valid"].iloc[:3]
    a = lab.predict_checked(model, rows, r["threshold"])
    b = lab.predict_checked(model, rows[lab.FEATURES[::-1]], r["threshold"])
    pd.testing.assert_frame_equal(a, b)
    assert a.index.equals(rows.index)
    assert np.array_equal(a.flag, a.cancellation_score >= r["threshold"])


@pytest.mark.parametrize(
    "kind", ["empty", "column", "text", "missing", "infinite", "negative", "fraction", "threshold"]
)
def test_invalid_input_is_rejected(experiment, kind):
    model, d, r = experiment
    row, threshold = d["X_valid"].iloc[:1].copy(), r["threshold"]
    if kind == "empty":
        row = row.iloc[:0]
    elif kind == "column":
        row = row.drop(columns="days_inactive")
    elif kind == "text":
        row["weekly_sessions"] = "five"
    elif kind == "missing":
        row["days_inactive"] = np.nan
    elif kind == "infinite":
        row["days_inactive"] = np.inf
    elif kind == "negative":
        row["days_inactive"] = -1
    elif kind == "fraction":
        row["weekly_sessions"] = 1.5
    else:
        threshold = np.nan
    with pytest.raises(ValueError):
        lab.predict_checked(model, row, threshold)


def test_saved_csv_reconstructs_final_confusion_counts(tmp_path):
    r = lab.write_report(tmp_path)
    assert json.loads((tmp_path / "report.json").read_text(encoding="utf-8")) == r
    rows = pd.read_csv(tmp_path / "test-predictions.csv")
    assert len(rows) == 240 and rows.row_id.is_unique
    rebuilt = lab.binary_metrics(rows.actual, rows.positive_score, r["threshold"])
    for key in ["tn", "fp", "fn", "tp", "total_cost"]:
        assert rebuilt[key] == r["test_at_selected_threshold"][key]
    assert np.array_equal(rows.flag, (rows.positive_score >= r["threshold"]).astype(int))
