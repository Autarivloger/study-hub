import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from scipy.special import expit
from sklearn.model_selection import StratifiedKFold

import lab
from api import create_app
from bundle import FEATURES, NumericBundle, export_bundle, load_bundle, predict_frame, save_bundle


@pytest.fixture(scope="module")
def fitted():
    data = lab.make_splits()
    model = lab.make_tuned().fit(data["X_train"], data["y_train"])
    bundle = export_bundle(model, len(data["X_train"]), {"scikit-learn": "test fixture"})
    return model, data, bundle


def test_source_and_final_split_are_repeatable_and_offline(monkeypatch):
    def unavailable(*args, **kwargs):
        raise AssertionError("Training data must not require the network")

    monkeypatch.setattr(socket.socket, "connect", unavailable)
    a, b = lab.make_splits(), lab.make_splits()
    assert len(a["X_train"]) == 960 and len(a["X_test"]) == 240
    assert not set(a["X_train"].index) & set(a["X_test"].index)
    assert set(a["X_train"].index) | set(a["X_test"].index) == set(range(1200))
    pd.testing.assert_frame_equal(a["X_train"], b["X_train"])
    assert a["X_train"].index.equals(a["y_train"].index)


def test_nested_outer_fits_own_their_preprocessing():
    data = lab.make_splits()
    result = lab.nested_evaluate(data["X_train"], data["y_train"])
    folds = StratifiedKFold(n_splits=3, shuffle=True, random_state=lab.SEED + 3)
    for (fit, valid), search, score in zip(
        folds.split(data["X_train"], data["y_train"]),
        result["estimator"],
        result["test_cost"],
        strict=True,
    ):
        pipeline = search.best_estimator_.estimator_
        Xfit = data["X_train"].iloc[fit]
        np.testing.assert_allclose(pipeline.named_steps["fill"].statistics_, Xfit.median())
        assert pipeline.named_steps["scale"].n_samples_seen_ == len(fit)
        assert not set(fit) & set(valid)
        prediction = search.predict(data["X_train"].iloc[valid])
        assert score == pytest.approx(-lab.decision_cost(data["y_train"].iloc[valid], prediction))


def test_final_answers_never_change_training_selection(monkeypatch):
    d = lab.make_splits()
    original_model, _, original_report, original_bundle = lab.run_experiment()
    altered = {key: value.copy() for key, value in d.items()}
    altered["y_test"] = 1 - altered["y_test"]
    monkeypatch.setattr(lab, "make_splits", lambda: altered)
    repeated_model, _, repeated_report, repeated_bundle = lab.run_experiment()
    assert (
        repeated_report["full_training_selected_parameters"]
        == original_report["full_training_selected_parameters"]
    )
    assert repeated_report["outer_cost_per_row"] == original_report["outer_cost_per_row"]
    assert repeated_model.best_threshold_ == original_model.best_threshold_
    assert repeated_bundle == original_bundle
    assert repeated_report["final"]["tp"] + repeated_report["final"]["fn"] != (
        original_report["final"]["tp"] + original_report["final"]["fn"]
    )


def test_export_rejects_a_different_training_feature_order():
    d = lab.make_splits()
    model = lab.make_tuned().fit(d["X_train"][FEATURES[::-1]], d["y_train"])
    with pytest.raises(ValueError, match="feature names and order"):
        export_bundle(model, len(d["X_train"]), {})


def test_cost_sign_and_threshold_fit_boundary(fitted):
    model, d, _ = fitted
    assert lab.decision_cost([0, 1], [1, 0]) == 4.5
    assert lab.COST_SCORER(model, d["X_test"], d["y_test"]) <= 0
    assert model.estimator_.named_steps["scale"].n_samples_seen_ == 960


def test_numeric_round_trip_matches_full_fitted_pipeline(tmp_path, fitted):
    model, d, bundle = fitted
    path = tmp_path / "model.json"
    save_bundle(bundle, path)
    loaded = load_bundle(path)
    rows = d["X_test"].copy()
    rows.iloc[0, 0] = np.nan
    predicted = predict_frame(loaded, rows)
    np.testing.assert_allclose(
        predicted.positive_score, model.predict_proba(rows)[:, 1], atol=1e-12
    )
    np.testing.assert_array_equal(predicted.flag, model.predict(rows).astype(bool))
    pd.testing.assert_frame_equal(predicted, predict_frame(loaded, rows[FEATURES[::-1]]))
    assert predicted.index.equals(rows.index)


@pytest.mark.parametrize("kind", ["format", "order", "scale", "infinite", "extra"])
def test_numeric_bundle_rejects_invalid_contracts(kind, fitted):
    _, _, bundle = fitted
    values = bundle.model_dump()
    if kind == "format":
        values["artifact_format"] = "unknown"
    elif kind == "order":
        values["features"] = tuple(FEATURES[::-1])
    elif kind == "scale":
        values["scales"] = (0.0,) * 4
    elif kind == "infinite":
        values["intercept"] = float("inf")
    else:
        values["executable_object"] = "not permitted"
    with pytest.raises(ValidationError):
        NumericBundle.model_validate(values)


def test_shap_reconstructs_log_odds_not_probability(fitted):
    model, d, _ = fitted
    rows = d["X_train"].iloc[:3]
    explanation = lab.explain_rows(model, d["X_train"].sample(64, random_state=47), rows)
    log_odds = explanation.base_values + explanation.values.sum(axis=1)
    np.testing.assert_allclose(log_odds, model.estimator_.decision_function(rows), atol=1e-9)
    np.testing.assert_allclose(expit(log_odds), model.predict_proba(rows)[:, 1], atol=1e-9)


def test_api_prediction_matches_numeric_model_and_rejects_bad_batches(fitted):
    _, d, bundle = fitted
    client = TestClient(create_app(bundle))
    row = {
        "tenure_months": 12.0,
        "weekly_sessions": 3,
        "unresolved_tickets": 1,
        "days_inactive": 8.0,
    }
    response = client.post("/predict", json={"rows": [row]})
    assert response.status_code == 200
    expected = predict_frame(bundle, pd.DataFrame([row])).iloc[0]
    actual = response.json()["predictions"][0]
    assert actual["positive_score"] == pytest.approx(expected.positive_score)
    assert actual["flag"] == bool(expected.flag)
    assert client.get("/health").json()["model_version"] == "w47-v1"
    assert client.post("/predict", json={"rows": []}).status_code == 422
    assert client.post("/predict", json={"rows": [row] * 51}).status_code == 422
    for bad in [
        dict(row, weekly_sessions=2.5),
        dict(row, weekly_sessions=True),
        dict(row, secret="extra"),
        dict(row, days_inactive=None),
        dict(row, days_inactive=-1.0),
    ]:
        assert client.post("/predict", json={"rows": [bad]}).status_code == 422
    assert client.post("/train", json={}).status_code == 404
    assert len(d["X_test"]) == 240


def test_real_loopback_server_accepts_the_exported_bundle(tmp_path, fitted):
    _, _, bundle = fitted
    path = tmp_path / "model.json"
    save_bundle(bundle, path)
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    root = Path(__file__).resolve().parents[1]
    log_path = tmp_path / "server.log"
    with log_path.open("w", encoding="utf-8") as output:
        process = subprocess.Popen(
            [sys.executable, "api.py", "--bundle", str(path), "--port", str(port)],
            cwd=root,
            stdout=output,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        try:
            with httpx.Client(
                base_url=f"http://127.0.0.1:{port}", timeout=1, trust_env=False
            ) as client:
                deadline = time.monotonic() + 30
                while time.monotonic() < deadline:
                    try:
                        if client.get("/health").status_code == 200:
                            break
                    except httpx.TransportError:
                        pass
                    if process.poll() is not None:
                        pytest.fail(log_path.read_text(encoding="utf-8"))
                    time.sleep(0.1)
                else:
                    pytest.fail("Local inference server did not become ready")
                row = {
                    "tenure_months": 12.0,
                    "weekly_sessions": 3,
                    "unresolved_tickets": 1,
                    "days_inactive": 8.0,
                }
                response = client.post("/predict", json={"rows": [row]})
                assert response.status_code == 200
                assert response.json()["model_version"] == "w47-v1"
                assert len(response.json()["predictions"]) == 1
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def test_complete_exports_reconstruct_final_cost(tmp_path):
    report = lab.write_report(tmp_path)
    assert json.loads((tmp_path / "report.json").read_text(encoding="utf-8")) == report
    rows = pd.read_csv(tmp_path / "test-predictions.csv")
    assert len(rows) == 240 and rows.row_id.is_unique
    assert lab.decision_cost(rows.actual, rows.flag) == pytest.approx(
        report["final"]["cost_per_row"]
    )
    model = load_bundle(tmp_path / "model.json")
    assert model.training_rows == 960
    assert len(report["outer_cost_per_row"]) == 3
