"""Validated numeric logistic inference; no executable model deserialization."""

from pathlib import Path
from typing import Annotated, Literal

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, model_validator
from scipy.special import expit

FEATURES = ["tenure_months", "weekly_sessions", "unresolved_tickets", "days_inactive"]
Number = Annotated[float, Field(strict=True, allow_inf_nan=False)]
Vector = Annotated[tuple[Number, ...], Field(min_length=4, max_length=4)]


class NumericBundle(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    artifact_format: Literal["week47.numeric-logistic.v1"]
    model_version: Literal["w47-v1"]
    features: tuple[str, ...]
    medians: Vector
    means: Vector
    scales: Vector
    coefficients: Vector
    intercept: Number
    threshold: Annotated[Number, Field(ge=0, le=1.01)]
    training_rows: Annotated[int, Field(strict=True, gt=0)]
    training_versions: dict[str, str]

    @model_validator(mode="after")
    def reviewed_contract(self):
        if list(self.features) != FEATURES:
            raise ValueError("Feature order must match the reviewed four-column contract")
        if any(scale <= 0 for scale in self.scales):
            raise ValueError("Scales must be strictly positive")
        return self


def export_bundle(tuned, training_rows, versions):
    pipeline = tuned.estimator_
    if list(pipeline.feature_names_in_) != FEATURES:
        raise ValueError("Export requires the reviewed raw feature names and order")
    classifier = pipeline.named_steps["model"]
    if list(classifier.classes_) != [0, 1] or classifier.coef_.shape != (1, 4):
        raise ValueError("Export supports only the reviewed binary four-input logistic model")
    return NumericBundle(
        artifact_format="week47.numeric-logistic.v1",
        model_version="w47-v1",
        features=tuple(FEATURES),
        medians=tuple(pipeline.named_steps["fill"].statistics_),
        means=tuple(pipeline.named_steps["scale"].mean_),
        scales=tuple(pipeline.named_steps["scale"].scale_),
        coefficients=tuple(classifier.coef_[0]),
        intercept=float(classifier.intercept_[0]),
        threshold=float(tuned.best_threshold_),
        training_rows=training_rows,
        training_versions=versions,
    )


def save_bundle(bundle, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(bundle.model_dump_json(indent=2) + "\n", encoding="utf-8")


def load_bundle(path):
    path = Path(path)
    if path.stat().st_size > 65536:
        raise ValueError("Numeric bundle exceeds the documented size limit")
    return NumericBundle.model_validate_json(path.read_text(encoding="utf-8"))


def predict_frame(bundle, frame):
    if not isinstance(frame, pd.DataFrame) or frame.empty:
        raise ValueError("Provide a nonempty named DataFrame")
    if not frame.columns.is_unique or set(frame.columns) != set(FEATURES):
        raise ValueError("Provide exactly the four reviewed feature columns")
    ordered = frame.loc[:, FEATURES]
    if any(not pd.api.types.is_numeric_dtype(dtype) for dtype in ordered.dtypes):
        raise ValueError("Numeric inference needs numeric measurements")
    values = ordered.to_numpy(dtype=float, na_value=np.nan)
    if np.isinf(values).any():
        raise ValueError("Infinite measurements are invalid")
    filled = np.where(np.isnan(values), np.asarray(bundle.medians), values)
    prepared = (filled - np.asarray(bundle.means)) / np.asarray(bundle.scales)
    score = expit(prepared @ np.asarray(bundle.coefficients) + bundle.intercept)
    return pd.DataFrame(
        {"positive_score": score, "flag": score >= bundle.threshold}, index=frame.index
    )
