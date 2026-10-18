"""Offline segmentation and anomaly-analysis lab with explicit information boundaries."""

import argparse
import json
from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.metrics import adjusted_rand_score, confusion_matrix, silhouette_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

SEED = 48
FEATURES = ["monthly_visits", "monthly_spend", "support_tickets", "tenure_months"]


def make_customers(n=600, seed=SEED):
    """Independent simulated profiles; latent generator groups are never returned as labels."""
    rng = np.random.default_rng(seed)
    component = rng.integers(0, 3, n)
    centers = np.array([[3, 35, 1, 5], [12, 160, 2, 18], [6, 80, 5, 10]])
    spread = np.array([1.2, 18, 0.8, 2.5])
    values = np.maximum(0, centers[component] + rng.normal(size=(n, 4)) * spread)
    return pd.DataFrame(values, columns=FEATURES).rename_axis("row_id")


def customer_split():
    X = make_customers()
    train, other = train_test_split(X, test_size=0.4, random_state=SEED)
    development, audit = train_test_split(other, test_size=0.5, random_state=SEED + 1)
    return {"train": train, "development": development, "audit": audit}


def make_segmenter(k=3, seed=SEED):
    return Pipeline(
        [
            ("fill", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("cluster", KMeans(n_clusters=k, n_init=10, random_state=seed)),
        ]
    )


def geometry_score(model, rows):
    labels = model.predict(rows)
    if not 2 <= len(np.unique(labels)) < len(rows):
        return None
    return float(silhouette_score(model[:-1].transform(rows), labels))


def fit_segments():
    data = customer_split()
    models = {k: make_segmenter(k).fit(data["train"]) for k in [2, 3, 4, 5]}
    selection = {k: geometry_score(model, data["development"]) for k, model in models.items()}
    usable = [k for k, score in selection.items() if score is not None]
    if not usable:
        raise ValueError("No candidate has defined development silhouette")
    chosen = max(usable, key=lambda k: (selection[k], -k))
    model = models[chosen]
    labels = model.predict(data["development"])
    stability = []
    for seed in [49, 50]:
        repeated = make_segmenter(chosen, seed).fit(data["train"])
        stability.append(float(adjusted_rand_score(labels, repeated.predict(data["development"]))))
    # Freeze the selected training fit; audit rows do not trigger selection or refitting.
    audit_score = geometry_score(model, data["audit"])
    raw = data["train"].assign(segment=model.predict(data["train"]))
    profiles = raw.groupby("segment")[FEATURES].mean()
    counts = raw.groupby("segment").size()
    projection = PCA(n_components=2, svd_solver="full").fit(model[:-1].transform(data["train"]))
    report = {
        "dataset": "600 simulated independent profiles; no actual customer outcomes",
        "rows": {name: len(rows) for name, rows in data.items()},
        "candidate_k": [2, 3, 4, 5],
        "development_silhouette": selection,
        "chosen_k": chosen,
        "audit_silhouette": audit_score,
        "stability_ari_against_seed48": stability,
        "training_cluster_counts": {str(k): int(v) for k, v in counts.items()},
        "training_profiles_original_units": profiles.round(4).to_dict(orient="index"),
        "pca_explained_variance_ratio": projection.explained_variance_ratio_.tolist(),
        "protocol": "fit preparation/clusters on360 training; choose k on120 development; freeze and describe120 audit; no audit-driven redesign",
        "limitations": [
            "Silhouette describes scaled Euclidean geometry, not true customer types or predictive accuracy.",
            "Cluster ids are arbitrary; stability here changes initialization only, not samples or populations.",
            "Scaling, features and k shape the result. PCA projections can hide separation or distort interpretation.",
            "Recommendations are hypotheses for human research; no causal business benefit is established.",
        ],
    }
    return model, data, projection, report


def fault_split(seed=SEED):
    """Verified-normal fitting/calibration is an idealized teaching assumption."""
    rng = np.random.default_rng(seed)

    def normal(n):
        return rng.normal([50, 2], [2, 0.2], (n, 2))

    train, calibration = normal(320), normal(100)
    evaluation = np.vstack([normal(160), rng.normal([57, 2.8], [2, 0.2], (40, 2))])
    truth = np.r_[np.zeros(160, dtype=int), np.ones(40, dtype=int)]
    order = rng.permutation(len(truth))
    columns = ["temperature_c", "vibration_mm_s"]
    return {
        "train": pd.DataFrame(train, columns=columns),
        "calibration": pd.DataFrame(calibration, columns=columns),
        "evaluation": pd.DataFrame(evaluation[order], columns=columns),
        "truth": truth[order],
    }


def fit_fault_detector():
    data = fault_split()
    model = IsolationForest(n_estimators=80, contamination="auto", random_state=SEED, n_jobs=1)
    model.fit(data["train"])
    reference = -model.score_samples(data["calibration"])
    cutoff = float(np.quantile(reference, 0.98))
    # Evaluation labels are consulted only after this fixed cutoff is chosen.
    scores = -model.score_samples(data["evaluation"])
    flags = scores > cutoff
    tn, fp, fn, tp = map(int, confusion_matrix(data["truth"], flags, labels=[0, 1]).ravel())
    report = {
        "cutoff": cutoff,
        "calibration_quantile": 0.98,
        "score_direction": "larger negative score_samples is more unusual; flag score>cutoff",
        "evaluation": {"tn": tn, "fp": fp, "fn": fn, "tp": tp},
        "limitations": "Synthetic injected faults; unusual is not confirmed fault/fraud. Normal-only calibration is assumed, not discovered. No guaranteed future false-alert rate.",
    }
    return model, data, scores, flags, report


def write_report(folder):
    from neural import compare_digits

    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    model, data, _projection, segmentation = fit_segments()
    tables = []
    for name, rows in data.items():
        table = rows.copy()
        table["split"] = name
        table["segment"] = model.predict(rows)
        tables.append(table)
    pd.concat(tables).sort_index().to_csv(folder / "segments.csv")
    centers = model.named_steps["scale"].inverse_transform(
        model.named_steps["cluster"].cluster_centers_
    )
    pd.DataFrame(centers, columns=FEATURES).to_csv(folder / "centroids.csv", index_label="segment")
    _, faults, scores, flags, anomaly = fit_fault_detector()
    faults["evaluation"].assign(actual_fault=faults["truth"], score=scores, flag=flags).to_csv(
        folder / "fault-audit.csv", index=False
    )
    _, _, digits = compare_digits(folder)
    report = {
        "segmentation": segmentation,
        "anomaly": anomaly,
        "digits": digits,
        "versions": {name: version(name) for name in ["numpy", "pandas", "scikit-learn", "torch"]},
        "recommendations": [
            "Describe observed profiles in original units before naming groups.",
            "Investigate repeated-source/time relevance and resampling stability before operational segmentation.",
            "Send unusual measurements for human inspection; do not automatically punish a customer.",
            "Keep a simple supervised baseline; validation-selected neural training is not automatically superior.",
        ],
    }
    (folder / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    report = write_report(args.output)
    print("Selected segmentation k:", report["segmentation"]["chosen_k"])
    print("Audit geometry:", round(report["segmentation"]["audit_silhouette"], 3))
    print("Fault audit counts:", report["anomaly"]["evaluation"])
    print("Digits final accuracy:", report["digits"]["test_accuracy"])
    print("Saved traceable offline reports in", args.output)
    print("Audit/test evidence has been inspected; this is not a production deployment.")


if __name__ == "__main__":
    main()
