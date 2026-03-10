"""Render review reports from transaction data and an existing score export.

No model fitting or classification is performed here. The top 2% is an
illustrative, rank-based review budget, not a decision-function threshold.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter

BLUE = "#2368a0"
ORANGE = "#db7b32"
INK = "#17324a"


def prepare_review(transactions: pd.DataFrame, scores: pd.DataFrame) -> pd.DataFrame:
    """Require complete, unique matching IDs; select exactly ceil(2% * n) rows."""
    if transactions.empty or scores.empty:
        raise ValueError("Transactions and scores must be nonempty.")
    if transactions.tx_id.duplicated().any() or scores.tx_id.duplicated().any():
        raise ValueError("Transaction IDs must be unique in both inputs.")
    if set(transactions.tx_id) != set(scores.tx_id):
        raise ValueError("Transaction and score IDs must match exactly.")
    if not np.isfinite(scores.anomaly_score).all():
        raise ValueError("Scores must be finite.")
    frame = transactions.merge(
        scores[["tx_id", "anomaly_score"]], on="tx_id", validate="one_to_one"
    )
    frame["date"] = pd.to_datetime(frame["date"], errors="raise")
    frame = frame.sort_values(["anomaly_score", "tx_id"], ascending=[False, True]).reset_index(
        drop=True
    )
    frame["review"] = np.arange(len(frame)) < int(np.ceil(len(frame) * 0.02))
    return frame


def canvas(title: str, subtitle: str) -> tuple[plt.Figure, np.ndarray]:
    fig, axes = plt.subplots(1, 2, figsize=(16, 7), facecolor="#f5f8fb")
    fig.suptitle(title, x=0.07, ha="left", y=0.96, fontsize=24, fontweight="bold", color=INK)
    fig.text(0.07, 0.865, subtitle, fontsize=11, color=INK)
    fig.text(
        0.07,
        0.045,
        "Unsupervised ranking • Top 2% is an illustrative review budget"
        " • No confirmed fraud labels",
        fontsize=10,
        color=INK,
    )
    fig.subplots_adjust(left=0.075, right=0.96, bottom=0.20, top=0.76, wspace=0.32)
    for ax in axes:
        ax.set_facecolor("white")
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color="#e4ebf1", linewidth=0.6)
        ax.set_axisbelow(True)
    return fig, axes


def save(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path, dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)


def render_reports(frame: pd.DataFrame, destination: Path) -> None:
    """Write three PNGs using all rows and the same global review cohort."""
    destination.mkdir(parents=True, exist_ok=True)
    selected = frame.loc[frame.review]
    period = f"{frame.date.min():%d %b %Y} – {frame.date.max():%d %b %Y}"
    subtitle = (
        f"{period}  |  {len(frame):,} transactions  |  {frame.user_id.nunique():,} users"
        f"  |  {len(selected):,} selected for review"
    )
    with plt.rc_context({"font.family": "DejaVu Sans", "font.size": 11}):
        fig, axes = canvas("Anomaly ranking & transaction amounts", subtitle)
        baseline = frame.loc[~frame.review]
        axes[0].scatter(
            baseline.amount, baseline.anomaly_score, s=5, color=BLUE, alpha=0.12, rasterized=True
        )
        axes[0].scatter(
            selected.amount,
            selected.anomaly_score,
            s=10,
            color=ORANGE,
            alpha=0.55,
            label="Top 2% review cohort",
            rasterized=True,
        )
        axes[0].set(
            xlabel="Transaction amount (dataset units)",
            ylabel="Anomaly score",
            title="Amount alone does not define the ranking",
        )
        axes[0].legend(loc="lower right", fontsize=9)
        axes[1].plot(
            np.arange(1, len(frame) + 1) / len(frame) * 100,
            frame.anomaly_score,
            color=BLUE,
            linewidth=2,
        )
        axes[1].axvline(
            len(selected) / len(frame) * 100,
            color=ORANGE,
            linestyle="--",
            label="Review budget boundary",
        )
        axes[1].set(
            xlabel="Ranked transactions (% of dataset)",
            ylabel="Anomaly score",
            title="Score declines through the ranked queue",
            xlim=(0, 100),
        )
        axes[1].legend(fontsize=9)
        save(fig, destination / "anomaly_review.png")

        users = (
            selected.groupby("user_id")
            .agg(
                selected_transactions=("tx_id", "size"),
                selected_amount=("amount", "sum"),
                max_score=("anomaly_score", "max"),
            )
            .sort_values(["max_score", "selected_amount"], ascending=False)
            .head(12)
        )
        users = users.iloc[::-1]
        fig, axes = canvas("User review priorities", subtitle)
        axes[0].barh(users.index, users.max_score, color=BLUE)
        axes[0].set(xlabel="Highest transaction anomaly score", title="Top users by highest score")
        axes[1].barh(users.index, users.selected_amount, color=ORANGE)
        axes[1].set(
            xlabel="Selected transaction amount (dataset units)",
            title="Amounts within the same review cohort",
        )
        axes[1].xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:,.0f}"))
        save(fig, destination / "user_review.png")

        daily = frame.groupby("date").agg(
            transactions=("tx_id", "size"), selected_transactions=("review", "sum")
        )
        fig, axes = canvas("Transaction activity & review workload", subtitle)
        axes[0].plot(daily.index, daily.transactions, color=BLUE, linewidth=1.8)
        axes[0].set(ylabel="Transactions per day", title="Daily transaction volume", ylim=(0, None))
        axes[1].bar(daily.index, daily.selected_transactions, color=ORANGE, width=0.8)
        axes[1].set(
            ylabel="Selected transactions per day",
            title="Daily workload from the global top 2%",
            ylim=(0, None),
        )
        for ax in axes:
            ax.tick_params(axis="x", rotation=30, labelsize=9)
        save(fig, destination / "transaction_activity.png")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transactions", type=Path, default=Path("data/transactions.csv"))
    parser.add_argument("--scores", type=Path, default=Path("outputs/fraud_scores.csv"))
    parser.add_argument("--outdir", type=Path, default=Path("screenshots"))
    args = parser.parse_args()
    frame = prepare_review(pd.read_csv(args.transactions), pd.read_csv(args.scores))
    render_reports(frame, args.outdir)


if __name__ == "__main__":
    main()
