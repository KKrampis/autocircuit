#!/usr/bin/env python3
"""Export meeting-ready figures from the corrected analogy audit outputs."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


BASE = Path(__file__).parent / "audit_outputs" / "corrected_20260712"
FIGURES = BASE / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

BLUE = "#2563EB"
GREEN = "#0F9D7A"
ORANGE = "#E68A2E"
GRAY = "#8A93A3"
GRID = "#D8DDE6"
TEXT = "#172033"
RED = "#C94B4B"


def finish(fig: plt.Figure, filename: str) -> None:
    fig.savefig(FIGURES / filename, dpi=190, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def overlap_figure() -> None:
    summary = json.loads((BASE / "summary.json").read_text(encoding="utf-8"))
    original = summary["original_occurrence_threshold_counts_on_fresh_graphs"]
    corrected = summary["corrected_distinct_graph_counts_on_fresh_graphs"]
    labels = ["At least 3/5", "At least 4/5", "All 5/5"]
    old_values = [original[str(value)] for value in (3, 4, 5)]
    new_values = [corrected[str(value)] for value in (3, 4, 5)]

    fig, ax = plt.subplots(figsize=(10.2, 4.8))
    y = np.arange(len(labels))
    height = 0.31
    old_bars = ax.barh(y - height / 2, old_values, height, color=GRAY, label="Published method")
    new_bars = ax.barh(y + height / 2, new_values, height, color=BLUE, label="Corrected distinct-graph count")
    ax.bar_label(old_bars, padding=5, color=TEXT, fontsize=10)
    ax.bar_label(new_bars, padding=5, color=TEXT, fontsize=10, fontweight="bold")
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(0, 555)
    ax.set_xlabel("Number of recurring SAE features")
    fig.suptitle(
        "Correcting repeated token-position activations reduces graph overlap",
        x=0.08,
        y=0.98,
        ha="left",
        fontweight="bold",
        color=TEXT,
    )
    fig.text(0.08, 0.91, "The all-five core falls from 180 to 119 features (−33.9%).", color="#526079")
    fig.subplots_adjust(top=0.82)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="lower right")
    for spine in ax.spines.values():
        spine.set_visible(False)
    finish(fig, "01-corrected-feature-overlap.png")


def model_comparison_figure() -> None:
    result = json.loads((BASE / "numeric_phase_detection.json").read_text(encoding="utf-8"))
    piecewise = result["candidate_piecewise_models"]
    smooth = next(row for row in result["smooth_polynomial_controls"] if row["degree"] == 3)
    labels = [f"{row['n_phases']} phase" + ("s" if row["n_phases"] != 1 else "") for row in piecewise]
    labels.append("Smooth cubic")
    values = [row["leave_one_prompt_out_loss"] for row in piecewise]
    values.append(smooth["leave_one_prompt_out_loss"])
    colors = [BLUE] * len(piecewise) + [GREEN]

    fig, ax = plt.subplots(figsize=(10.2, 5.0))
    bars = ax.bar(np.arange(len(labels)), values, color=colors, width=0.68)
    ax.bar_label(bars, labels=[f"{value:.3f}" for value in values], padding=4, color=TEXT, fontsize=10)
    ax.set_xticks(np.arange(len(labels)), labels)
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Leave-one-prompt-out prediction loss")
    fig.suptitle(
        "A smooth depth trend predicts held-out prompts better than discrete phases",
        x=0.08,
        y=0.98,
        ha="left",
        fontweight="bold",
        color=TEXT,
    )
    fig.text(0.08, 0.91, "Lower is better. BIC selects three phases, but the smooth model has the best held-out fit.", color="#526079")
    fig.subplots_adjust(top=0.82)
    ax.annotate(
        "BIC choice",
        xy=(2, values[2]),
        xytext=(2, values[2] + 0.20),
        ha="center",
        color=TEXT,
        arrowprops={"arrowstyle": "-|>", "color": GRAY, "lw": 1.1},
    )
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    finish(fig, "02-phase-model-comparison.png")


def boundary_stability_figure() -> None:
    result = json.loads((BASE / "numeric_phase_detection.json").read_text(encoding="utf-8"))
    pairs = result["bootstrap"]["fixed_bic_model_boundary_frequency_top_10"]
    boundary_one = {}
    boundary_two = {}
    for row in pairs:
        first, second = row["boundaries"]
        boundary_one[first] = boundary_one.get(first, 0) + row["count"]
        boundary_two[second] = boundary_two.get(second, 0) + row["count"]

    fig, ax = plt.subplots(figsize=(10.2, 4.8))
    layers = np.arange(26)
    width = 0.38
    first_counts = [boundary_one.get(int(layer), 0) for layer in layers]
    second_counts = [boundary_two.get(int(layer), 0) for layer in layers]
    ax.bar(layers - width / 2, first_counts, width, color=BLUE, label="First boundary")
    ax.bar(layers + width / 2, second_counts, width, color=ORANGE, label="Second boundary")
    for layer, count in boundary_one.items():
        ax.text(layer - width / 2, count + 18, str(count), ha="center", color=TEXT, fontsize=9)
    for layer, count in boundary_two.items():
        ax.text(layer + width / 2, count + 18, str(count), ha="center", color=TEXT, fontsize=9)
    ax.axvline(5, color=RED, linestyle="--", linewidth=1.3, label="Published boundaries")
    ax.axvline(10, color=RED, linestyle="--", linewidth=1.3)
    ax.text(5, 900, "Published L5", rotation=90, va="top", ha="right", color=RED, fontsize=9)
    ax.text(10, 900, "Published L10", rotation=90, va="top", ha="right", color=RED, fontsize=9)
    ax.set_xlim(-0.8, 25.8)
    ax.set_ylim(0, 950)
    ax.set_xticks(np.arange(0, 26, 2))
    ax.set_xlabel("Layer where the new segment begins")
    ax.set_ylabel("Bootstrap selections out of 1,000")
    fig.suptitle(
        "Bootstrap boundaries cluster near L7–8 and L14–18—not L5 and L10",
        x=0.08,
        y=0.98,
        ha="left",
        fontweight="bold",
        color=TEXT,
    )
    fig.text(0.08, 0.91, "Fixed three-segment model across 1,000 prompt-bootstrap reruns.", color="#526079")
    fig.subplots_adjust(top=0.82)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, ncol=3, loc="upper right")
    for spine in ax.spines.values():
        spine.set_visible(False)
    finish(fig, "03-bootstrap-boundary-stability.png")


def main() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10.5,
            "axes.labelcolor": TEXT,
            "xtick.color": "#526079",
            "ytick.color": "#526079",
        }
    )
    overlap_figure()
    model_comparison_figure()
    boundary_stability_figure()
    for path in sorted(FIGURES.glob("*.png")):
        print(path.resolve())


if __name__ == "__main__":
    main()
