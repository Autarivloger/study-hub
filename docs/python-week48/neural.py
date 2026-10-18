"""A two-layer NumPy network and a CPU PyTorch comparison on bundled digits."""

import copy
from pathlib import Path

import numpy as np
from scipy.special import expit
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def xor_data():
    return np.array([[-1, -1], [-1, 1], [1, -1], [1, 1]], dtype=float), np.array(
        [[0], [1], [1], [0]], dtype=float
    )


def init_tiny(seed=48):
    rng = np.random.default_rng(seed)
    return {
        "W1": rng.normal(0, 0.5, (2, 4)),
        "b1": np.zeros(4),
        "W2": rng.normal(0, 0.5, (4, 1)),
        "b2": np.zeros(1),
    }


def tiny_forward(X, parameters):
    hidden = np.tanh(X @ parameters["W1"] + parameters["b1"])
    logits = hidden @ parameters["W2"] + parameters["b2"]
    return hidden, logits, expit(logits)


def tiny_loss_grads(X, y, parameters):
    hidden, logits, probability = tiny_forward(X, parameters)
    loss = float(np.mean(np.logaddexp(0, logits) - y * logits))
    dz = (probability - y) / len(X)
    dh = (dz @ parameters["W2"].T) * (1 - hidden**2)
    gradients = {"W2": hidden.T @ dz, "b2": dz.sum(axis=0), "W1": X.T @ dh, "b1": dh.sum(axis=0)}
    return loss, gradients


def train_tiny(steps=1600, rate=0.2):
    X, y = xor_data()
    parameters = init_tiny()
    losses = []
    for _ in range(steps):
        loss, gradients = tiny_loss_grads(X, y, parameters)
        losses.append(loss)
        for name in parameters:
            parameters[name] -= rate * gradients[name]
    return parameters, np.array(losses)


def digits_split():
    X, y = load_digits(return_X_y=True)
    ids = np.arange(len(y))
    train, other = train_test_split(ids, test_size=0.4, stratify=y, random_state=48)
    validation, test = train_test_split(other, test_size=0.5, stratify=y[other], random_state=49)
    scaler = StandardScaler().fit(X[train])
    data = {"raw_X": X, "raw_y": y, "scaler": scaler}
    for name, positions in [("train", train), ("validation", validation), ("test", test)]:
        data[name + "_ids"] = positions
        data["X_" + name] = scaler.transform(X[positions]).astype(np.float32)
        data["y_" + name] = y[positions].astype(np.int64)
    return data


def new_torch_model():
    import torch
    from torch import nn

    torch.manual_seed(48)
    return nn.Sequential(nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, 10))


def train_digits(epochs=45):
    import torch
    from torch import nn
    from torch.utils.data import DataLoader, TensorDataset

    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    data = digits_split()
    model = new_torch_model()
    train_X, train_y = torch.from_numpy(data["X_train"]), torch.from_numpy(data["y_train"])
    valid_X, valid_y = (
        torch.from_numpy(data["X_validation"]),
        torch.from_numpy(data["y_validation"]),
    )
    loader = DataLoader(
        TensorDataset(train_X, train_y),
        batch_size=128,
        shuffle=True,
        generator=torch.Generator().manual_seed(48),
        num_workers=0,
    )
    loss_fn, optimizer = nn.CrossEntropyLoss(), torch.optim.Adam(model.parameters(), lr=0.01)
    best_loss, best_epoch, best_state = float("inf"), 0, None
    history = []
    for epoch in range(epochs):
        model.train()
        total = 0.0
        for batch_X, batch_y in loader:
            optimizer.zero_grad()
            loss = loss_fn(model(batch_X), batch_y)
            loss.backward()
            optimizer.step()
            total += float(loss.detach()) * len(batch_X)
        model.eval()
        with torch.no_grad():
            valid_loss = float(loss_fn(model(valid_X), valid_y))
        history.append(
            {"epoch": epoch + 1, "train_loss": total / len(train_y), "validation_loss": valid_loss}
        )
        if valid_loss < best_loss:
            best_loss, best_epoch = valid_loss, epoch + 1
            best_state = copy.deepcopy(model.state_dict())
    model.load_state_dict(best_state)
    model.eval()
    return model, data, history, best_epoch


def compare_digits(folder=None):
    import pandas as pd
    import torch

    model, data, _history, epoch = train_digits()
    baseline = make_pipeline(StandardScaler(), LogisticRegression(C=1, max_iter=2000))
    baseline.fit(data["raw_X"][data["train_ids"]], data["y_train"])
    with torch.no_grad():
        logits = model(torch.from_numpy(data["X_test"]))
        scores = logits.softmax(dim=1).numpy()
    neural_prediction = scores.argmax(axis=1)
    baseline_prediction = baseline.predict(data["raw_X"][data["test_ids"]])
    report = {
        "dataset": "sklearn bundled UCI optical digits; 1797 independent-row teaching assumption, not handwriting-source validation",
        "rows": {name: len(data["y_" + name]) for name in ["train", "validation", "test"]},
        "architecture": "64 -> 32 ReLU -> 10 logits; CPU; Adam lr0.01;45 epochs; validation selects checkpoint",
        "selected_epoch": epoch,
        "test_accuracy": {
            "logistic": float(accuracy_score(data["y_test"], baseline_prediction)),
            "neural": float(accuracy_score(data["y_test"], neural_prediction)),
        },
        "test_neural_log_loss": float(log_loss(data["y_test"], scores, labels=list(range(10)))),
        "trainable_parameters": sum(parameter.numel() for parameter in model.parameters()),
        "limitations": "Fixed teaching split, no writer/source ids. Validation selects checkpoint; test inspected once after freeze. No timing benchmark or guaranteed neural advantage.",
    }
    if folder is not None:
        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)
        torch.save(model.state_dict(), folder / "own-digits-state.pt")
        np.savez(
            folder / "digits-preparation.npz",
            mean=data["scaler"].mean_,
            scale=data["scaler"].scale_,
        )
        pd.DataFrame(
            {
                "row_id": data["test_ids"],
                "actual": data["y_test"],
                "logistic": baseline_prediction,
                "neural": neural_prediction,
            }
        ).to_csv(folder / "digits-test.csv", index=False)
    return model, data, report
