"""Local-only numeric-model inference. Train/export with lab.py first."""

import argparse
from typing import Annotated

import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

from bundle import FEATURES, NumericBundle, load_bundle, predict_frame

Measurement = Annotated[float, Field(strict=True, ge=0, le=36500, allow_inf_nan=False)]
Count = Annotated[int, Field(strict=True, ge=0, le=10000)]


class Snapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenure_months: Measurement
    weekly_sessions: Count
    unresolved_tickets: Count
    days_inactive: Measurement


class Batch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rows: Annotated[list[Snapshot], Field(min_length=1, max_length=50)]


def create_app(bundle: NumericBundle):
    app = FastAPI(title="Week47 local numeric inference", version=bundle.model_version)

    @app.get("/health")
    def health():
        return {"status": "ready", "model_version": bundle.model_version}

    @app.post("/predict")
    def predict(batch: Batch):
        frame = pd.DataFrame([row.model_dump() for row in batch.rows], columns=FEATURES)
        result = predict_frame(bundle, frame)
        return {
            "model_version": bundle.model_version,
            "positive_label": "cancellation within30days",
            "threshold": bundle.threshold,
            "predictions": [
                {"positive_score": float(p), "flag": bool(flag)}
                for p, flag in zip(result.positive_score, result.flag, strict=True)
            ],
        }

    return app


def main():
    import uvicorn

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", default="artifacts/model.json")
    parser.add_argument("--port", type=int, default=8047)
    args = parser.parse_args()
    uvicorn.run(create_app(load_bundle(args.bundle)), host="127.0.0.1", port=args.port)


if __name__ == "__main__":
    main()
