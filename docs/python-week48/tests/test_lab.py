import json
import socket

import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import accuracy_score

import lab
import neural


def test_sources_need_no_network_and_splits_preserve_rows(monkeypatch):
    def unavailable(*args, **kwargs):
        raise AssertionError("No dataset download is allowed")

    monkeypatch.setattr(socket.socket, "connect", unavailable)
    data = lab.customer_split()
    assert [len(rows) for rows in data.values()] == [360, 120, 120]
    all_ids = [i for rows in data.values() for i in rows.index]
    assert len(all_ids) == len(set(all_ids)) == 600
    assert set(all_ids) == set(range(600))
    pd.testing.assert_frame_equal(lab.make_customers(), lab.make_customers())
    digits = neural.digits_split()
    ids = [int(i) for name in ["train", "validation", "test"] for i in digits[name + "_ids"]]
    assert len(ids) == len(set(ids)) == 1797


def test_segment_preparation_owns_only_training_rows():
    model, data, projection, report = lab.fit_segments()
    np.testing.assert_allclose(model.named_steps["fill"].statistics_, data["train"].median())
    np.testing.assert_allclose(model.named_steps["scale"].mean_, data["train"].mean())
    assert model.named_steps["scale"].n_samples_seen_ == len(data["train"])
    assert projection.n_samples_ == len(data["train"])
    assert sum(report["training_cluster_counts"].values()) == 360
    assert report["chosen_k"] in report["candidate_k"]


def test_audit_changes_cannot_select_k_or_change_fitted_state(monkeypatch):
    model, data, _, report = lab.fit_segments()
    altered = {name: rows.copy() for name, rows in data.items()}
    altered["audit"] += 10000
    monkeypatch.setattr(lab, "customer_split", lambda: altered)
    repeated, _, _, changed = lab.fit_segments()
    assert changed["chosen_k"] == report["chosen_k"]
    assert changed["development_silhouette"] == report["development_silhouette"]
    np.testing.assert_allclose(
        repeated.named_steps["cluster"].cluster_centers_,
        model.named_steps["cluster"].cluster_centers_,
    )
    assert changed["audit_silhouette"] is None


def test_geometry_handles_a_single_assigned_cluster():
    data = lab.customer_split()
    model = lab.make_segmenter().fit(data["train"])
    repeated = pd.concat([data["train"].iloc[:1]] * 4, ignore_index=True)
    assert lab.geometry_score(model, repeated) is None


def test_fault_cutoff_uses_calibration_and_preserves_evaluation_counts():
    model, data, scores, flags, report = lab.fit_fault_detector()
    expected = np.quantile(-model.score_samples(data["calibration"]), 0.98)
    assert report["cutoff"] == pytest.approx(expected)
    np.testing.assert_array_equal(flags, scores > expected)
    assert sum(report["evaluation"].values()) == 200
    assert report["evaluation"]["tp"] + report["evaluation"]["fn"] == 40


def test_fault_evaluation_answers_cannot_change_the_cutoff(monkeypatch):
    model, data, scores, _, report = lab.fit_fault_detector()
    altered = {name: value.copy() for name, value in data.items()}
    altered["truth"] = 1 - altered["truth"]
    monkeypatch.setattr(lab, "fault_split", lambda: altered)
    repeated, _, repeated_scores, _, changed = lab.fit_fault_detector()
    assert changed["cutoff"] == report["cutoff"]
    np.testing.assert_array_equal(scores, repeated_scores)
    np.testing.assert_array_equal(model.predict(data["train"]), repeated.predict(data["train"]))


@pytest.mark.parametrize("name", ["W1", "b1", "W2", "b2"])
def test_manual_backprop_matches_central_finite_difference(name):
    X, y = neural.xor_data()
    parameters = neural.init_tiny()
    _, grads = neural.tiny_loss_grads(X, y, parameters)
    eps = 1e-5
    for index in np.ndindex(parameters[name].shape):
        plus = {key: value.copy() for key, value in parameters.items()}
        minus = {key: value.copy() for key, value in parameters.items()}
        plus[name][index] += eps
        minus[name][index] -= eps
        numerical = (
            neural.tiny_loss_grads(X, y, plus)[0] - neural.tiny_loss_grads(X, y, minus)[0]
        ) / (2 * eps)
        assert grads[name][index] == pytest.approx(numerical, abs=1e-8)


def test_numpy_network_learns_all_four_training_xor_cases():
    X, y = neural.xor_data()
    parameters, losses = neural.train_tiny()
    assert losses[-1] < losses[0] / 5
    assert np.isfinite(losses).all()
    np.testing.assert_array_equal(neural.tiny_forward(X, parameters)[2] >= 0.5, y.astype(bool))


def test_digit_scaler_fits_only_training_rows():
    d = neural.digits_split()
    np.testing.assert_allclose(d["scaler"].mean_, d["raw_X"][d["train_ids"]].mean(axis=0))
    assert d["scaler"].n_samples_seen_ == len(d["train_ids"])
    assert d["X_train"].dtype == np.float32
    assert d["y_train"].dtype == np.int64


def test_torch_checkpoint_selection_ignores_test_labels(monkeypatch):
    import torch

    model, data, history, epoch = neural.train_digits(epochs=8)
    assert epoch == min(history, key=lambda item: item["validation_loss"])["epoch"]
    altered = {
        key: value.copy() if isinstance(value, np.ndarray) else value for key, value in data.items()
    }
    altered["y_test"] = (altered["y_test"] + 1) % 10
    monkeypatch.setattr(neural, "digits_split", lambda: altered)
    repeated, _, repeated_history, repeated_epoch = neural.train_digits(epochs=8)
    assert repeated_epoch == epoch and repeated_history == history
    for name, value in model.state_dict().items():
        torch.testing.assert_close(value, repeated.state_dict()[name], rtol=0, atol=0)


def test_report_reconstructs_counts_accuracy_and_saved_inference(tmp_path):
    import torch

    report = lab.write_report(tmp_path)
    loaded = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    assert loaded["segmentation"]["chosen_k"] == report["segmentation"]["chosen_k"]
    segment = pd.read_csv(tmp_path / "segments.csv")
    assert len(segment) == 600 and segment.row_id.is_unique
    fault = pd.read_csv(tmp_path / "fault-audit.csv")
    assert (
        int(((fault.actual_fault == 1) & fault.flag).sum()) == report["anomaly"]["evaluation"]["tp"]
    )
    digits = pd.read_csv(tmp_path / "digits-test.csv")
    assert (
        accuracy_score(digits.actual, digits.neural) == report["digits"]["test_accuracy"]["neural"]
    )
    restored = neural.new_torch_model()
    restored.load_state_dict(
        torch.load(tmp_path / "own-digits-state.pt", map_location="cpu", weights_only=True)
    )
    restored.eval()
    d = neural.digits_split()
    with np.load(tmp_path / "digits-preparation.npz", allow_pickle=False) as preparation:
        prepared = (
            (d["raw_X"][d["test_ids"]] - preparation["mean"]) / preparation["scale"]
        ).astype(np.float32)
    with torch.no_grad():
        predictions = restored(torch.from_numpy(prepared)).argmax(dim=1).numpy()
    np.testing.assert_array_equal(predictions, digits.neural)
