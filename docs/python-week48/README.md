# Week 48 — Unsupervised learning & deep learning intro

Open **Course → Week 48**: six days, 36 parts, 72 exercises, 72 explained quiz
questions, 108 executed snippets and eight embedded charts. Take as many sessions
as needed. New terminology is explained before its first use. The original app,
earlier curriculum, notes, progress, themes, backup/import and sync are preserved.

## One-time setup

Use Python 3.12 or 3.13 on Windows or Linux x86-64. From this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe lab.py --output artifacts
```

On Linux use `.venv/bin/python` instead of `.\.venv\Scripts\python.exe`.
Installation needs internet and downloads CPU-only PyTorch, UMAP and dependencies
once. No GPU, paid account, remote dataset or service is required. Subsequent
fitting, figures and reporting run offline. The HTML lesson text, outputs and
figures remain readable without installing Python. Imports of `lab` or `neural`
refer to these supplied local files, not an unidentified package to install.

## What you learn

1. Distances, scaling, K-means, silhouette limits, initialization stability,
   hierarchical clustering, DBSCAN and original-unit cluster profiles.
2. PCA directions/variance/reconstruction, t-SNE and actual UMAP visualization;
   embedding islands, distances and axes are not automatic ground truth.
3. Robust statistical screening and Isolation Forest, separate calibration,
   planted-fault evaluation and the distinction between unusual and confirmed bad.
4. A NumPy 2 → 4 tanh → 1 logistic network, stable binary cross-entropy, manual
   backpropagation, finite-difference checks and honest XOR training evidence.
5. CPU PyTorch tensors, autograd, modules, batches, logits, cross-entropy,
   training/evaluation modes, validation-selected checkpoints and saved inference.
6. Classical baselines, data/compute judgment, reproducible reports and an
   evidence-led segmentation milestone with practical research recommendations.

## Segmentation protocol

`make_customers` simulates 600 independent profiles with four measurements.
Generator component ids are not returned as target labels. The measurements are
continuous teaching profiles; visits/tickets are not a production event schema.

- Split into 360 fitting, 120 development and 120 audit profiles with fixed seeds.
- Fit median imputation, standard scaling and K-means on fitting rows only.
- Compare declared k values 2/3/4/5 by development silhouette in that scaled
  four-dimensional space; undefined silhouette is reported as missing.
- Select the largest development silhouette, preferring smaller k on exact ties.
  Keep that training fit frozen. Do not refit using audit data or redesign from
  audit results while calling them untouched.
- Report audit geometry, training profiles in original units and initialization
  stability on the development profiles using ARI, which ignores label numbering.
- Fit the two-component PCA on training-prepared data only for visualization.

Silhouette is a geometry diagnostic, not cluster accuracy, true customer types or
evidence of causal benefit. Scaling/features/k change the question. Stability
across initial seeds is narrower than resampling, new-source or future-period
stability. IDs are arbitrary: segment 2 is not better than segment 0.

## Anomaly protocol

`fault_split` generates 320 assumed-normal fitting rows, 100 assumed-normal
calibration rows and 200 shuffled evaluation rows, including 40 injected faults.
Isolation Forest fits only the fitting rows. The 98th calibration quantile of
`-score_samples` fixes a cutoff before evaluation labels are inspected.
Larger scores are more unusual; the declared rule uses `score > cutoff`.

This is an idealized normal-reference simulation, not operational fraud evidence.
The quantile is not a guaranteed future false-alert rate. Unusual observations
need investigation; a detector score is not confirmed fault, intent or guilt.
Lessons distinguish this workflow from fitting outlier detectors to contaminated
tables and from chronological forecasting or rolling-window monitoring.

## Neural protocol

`neural.py` first implements XOR using NumPy. Tests check all 17 manual gradient
coordinates by central finite differences. Learning four XOR examples demonstrates
training mechanics, not generalization to unseen handwriting.

The actual PyTorch exercise uses sklearn's bundled 1,797 UCI optical digits.
It makes a fixed stratified train/validation/test split; scaling fits training only.
A 64 → 32 ReLU → 10-logit network trains on CPU with Adam, learning rate 0.01,
batch size 128 and 45 epochs. Validation loss selects a copied checkpoint.
Only after that choice is frozen are test accuracy and log loss reported.

A predeclared standardized logistic model (C=1) uses the same fitting rows and
final test. The comparison is a teaching split with unequal optimization budgets,
not proof that either model family always wins. Writer/source groups are not
available here; random row splitting does not establish new-writer performance.
No timing benchmark or GPU speedup claim is made. Seeds and one CPU thread aid
repeatability in the pinned environment, not bitwise equivalence across all devices.

## Inspect the output

- `report.json`: selection rules, geometry, profiles, stability, anomaly counts,
  neural/baseline comparison, versions, recommendations and evidence limits.
- `segments.csv`: all profile row ids, original measurements, split and cluster id.
- `centroids.csv`: selected centers converted back to original measurement units.
- `fault-audit.csv`: paired planted labels, unusualness scores and fixed-cutoff flags.
- `digits-test.csv`: final row ids, actual class and both model predictions.
- `own-digits-state.pt`: the locally created neural state dictionary.
- `digits-preparation.npz`: training scaler means/scales; load with allow_pickle=False.

Tests reconstruct counts/accuracy and reload the owned state with
`torch.load(..., weights_only=True, map_location="cpu")`, preserving its architecture
and preparation. Load only artifacts you trust; weights_only is not a reason to
accept arbitrary public uploads. This lab has no public model-serving endpoint.

Reading audit/test reports consumes their untouched status. Rerunning checks
reproducibility; it does not create new independent outcome evidence. The project
never reads Study Hub storage, credentials, learner notes or progress.

## Optional primary references

- [Clustering](https://scikit-learn.org/stable/modules/clustering.html)
- [Silhouette analysis](https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_silhouette_analysis.html)
- [PCA](https://scikit-learn.org/stable/modules/decomposition.html#pca)
- [Manifold learning](https://scikit-learn.org/stable/modules/manifold.html)
- [UMAP parameters](https://umap-learn.readthedocs.io/en/latest/parameters.html)
- [Outlier/novelty detection](https://scikit-learn.org/stable/modules/outlier_detection.html)
- [PyTorch basics](https://docs.pytorch.org/tutorials/beginner/basics/intro.html)
- [PyTorch reproducibility](https://docs.pytorch.org/docs/stable/notes/randomness.html)
- [Bundled digits provenance](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html)

Explanations, exercises and lesson charts are original. Optional links supplement
the embedded offline learning material.
