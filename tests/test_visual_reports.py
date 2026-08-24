"""Report cohort validation and image output checks."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from PIL import Image

from scripts.generate_visual_reports import prepare_review, render_reports


def inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    transactions = pd.DataFrame(
        {
            "tx_id": range(51),
            "user_id": [f"U{i % 5}" for i in range(51)],
            "date": pd.date_range("2025-01-01", periods=51),
            "amount": np.arange(51) + 1,
        }
    )
    scores = pd.DataFrame({"tx_id": range(51), "anomaly_score": np.ones(51)})
    return transactions, scores


def test_review_budget_and_tie_order() -> None:
    transactions, scores = inputs()
    frame = prepare_review(transactions.sample(frac=1, random_state=3), scores)
    assert frame.loc[frame.review, "tx_id"].tolist() == [0, 1]
    assert frame.loc[frame.review, "amount"].sum() == 3
    assert len(frame) == 51


@pytest.mark.parametrize("problem", ["empty", "duplicate", "missing", "nonfinite"])
def test_invalid_inputs(problem: str) -> None:
    transactions, scores = inputs()
    if problem == "empty":
        scores = scores.iloc[:0]
    elif problem == "duplicate":
        scores.loc[1, "tx_id"] = 0
    elif problem == "missing":
        scores = scores.iloc[1:]
    else:
        scores.loc[0, "anomaly_score"] = np.nan
    with pytest.raises(ValueError):
        prepare_review(transactions, scores)


def test_report_images(tmp_path: Path) -> None:
    render_reports(prepare_review(*inputs()), tmp_path)
    assert {p.name for p in tmp_path.glob("*.png")} == {
        "anomaly_review.png",
        "user_review.png",
        "transaction_activity.png",
    }
    for path in tmp_path.glob("*.png"):
        with Image.open(path) as image:
            assert image.size == (2880, 1260)
            assert image.format == "PNG"
