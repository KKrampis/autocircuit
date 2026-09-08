#!/usr/bin/env python3
"""Exploratory change-point analysis of objective layer-wise graph metrics.

This does not assign semantic phase names.  It tests whether the ordered layer
metrics are better described by discrete piecewise-constant regimes.  Semantic
phase claims require the separately generated blinded annotation dataset.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np


METRIC_NAMES = (
    "log_unique_feature_count",
    "median_influence",
    "log_median_activation",
    "mean_contexts_per_feature",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--graph-dir",
        type=Path,
        default=Path(__file__).parent
        / "audit_outputs"
        / "corrected_20260712"
        / "graphs",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent
        / "audit_outputs"
        / "corrected_20260712",
    )
    parser.add_argument("--min-segment-size", type=int, default=3)
    parser.add_argument("--max-boundaries", type=int, default=4)
    parser.add_argument("--bootstrap-samples", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=20260712)
    return parser.parse_args()


def feature_identity(node: dict[str, Any]) -> tuple[int, int] | None:
    if node.get("feature_type") not in ("cross layer transcoder", "transcoder"):
        return None
    try:
        return int(node["layer"]), int(str(node["node_id"]).split("_")[1])
    except (KeyError, TypeError, ValueError, IndexError):
        return None


def graph_layer_metrics(graph: dict[str, Any], n_layers: int = 26) -> np.ndarray:
    by_layer_feature: dict[int, dict[int, list[dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for node in graph.get("nodes", []):
        identity = feature_identity(node)
        if identity is not None:
            layer, sae_index = identity
            by_layer_feature[layer][sae_index].append(node)

    result = np.zeros((n_layers, len(METRIC_NAMES)), dtype=float)
    for layer in range(n_layers):
        features = by_layer_feature.get(layer, {})
        if not features:
            continue
        feature_influences = []
        feature_activations = []
        context_counts = []
        for occurrences in features.values():
            feature_influences.append(
                np.mean([float(node.get("influence") or 0.0) for node in occurrences])
            )
            feature_activations.append(
                np.mean([float(node.get("activation") or 0.0) for node in occurrences])
            )
            context_counts.append(len(occurrences))
        result[layer] = (
            math.log1p(len(features)),
            float(np.median(feature_influences)),
            math.log1p(max(0.0, float(np.median(feature_activations)))),
            float(np.mean(context_counts)),
        )
    return result


def standardize_within_prompt(values: np.ndarray) -> np.ndarray:
    means = values.mean(axis=0, keepdims=True)
    standard_deviations = values.std(axis=0, keepdims=True)
    standard_deviations[standard_deviations == 0] = 1.0
    return (values - means) / standard_deviations


def segment_cost(prefix: np.ndarray, prefix_sq: np.ndarray, start: int, end: int) -> float:
    count = end - start
    totals = prefix[end] - prefix[start]
    squared_totals = prefix_sq[end] - prefix_sq[start]
    return float(np.sum(squared_totals - (totals * totals) / count))


def exact_segmentation(
    values: np.ndarray,
    n_boundaries: int,
    min_segment_size: int,
) -> tuple[list[int], float]:
    """Return boundary layer indexes and the globally minimal within-segment SSE."""
    n_layers = len(values)
    n_segments = n_boundaries + 1
    if n_segments * min_segment_size > n_layers:
        raise ValueError("Too many boundaries for the requested minimum segment size")

    prefix = np.vstack([np.zeros(values.shape[1]), np.cumsum(values, axis=0)])
    prefix_sq = np.vstack(
        [np.zeros(values.shape[1]), np.cumsum(values * values, axis=0)]
    )
    infinity = float("inf")
    costs = np.full((n_segments + 1, n_layers + 1), infinity)
    previous = np.full((n_segments + 1, n_layers + 1), -1, dtype=int)
    costs[0, 0] = 0.0

    for segments_used in range(1, n_segments + 1):
        earliest_end = segments_used * min_segment_size
        for end in range(earliest_end, n_layers + 1):
            earliest_start = (segments_used - 1) * min_segment_size
            latest_start = end - min_segment_size
            for start in range(earliest_start, latest_start + 1):
                candidate = costs[segments_used - 1, start]
                if not math.isfinite(candidate):
                    continue
                candidate += segment_cost(prefix, prefix_sq, start, end)
                if candidate < costs[segments_used, end]:
                    costs[segments_used, end] = candidate
                    previous[segments_used, end] = start

    boundaries = []
    end = n_layers
    for segments_used in range(n_segments, 1, -1):
        start = int(previous[segments_used, end])
        boundaries.append(start)
        end = start
    boundaries.reverse()
    return boundaries, float(costs[n_segments, n_layers])


def segment_means(values: np.ndarray, boundaries: list[int]) -> np.ndarray:
    predictions = np.zeros_like(values)
    starts = [0, *boundaries]
    ends = [*boundaries, len(values)]
    for start, end in zip(starts, ends):
        predictions[start:end] = values[start:end].mean(axis=0)
    return predictions


def piecewise_cv_loss(prompt_values: np.ndarray, n_boundaries: int, min_size: int) -> float:
    losses = []
    for held_out in range(len(prompt_values)):
        training = np.delete(prompt_values, held_out, axis=0)
        training_mean = training.mean(axis=0)
        boundaries, _ = exact_segmentation(training_mean, n_boundaries, min_size)
        training_segment_means = segment_means(training_mean, boundaries)
        losses.append(float(np.mean((prompt_values[held_out] - training_segment_means) ** 2)))
    return float(np.mean(losses))


def polynomial_cv_loss(prompt_values: np.ndarray, degree: int) -> float:
    layers = np.arange(prompt_values.shape[1], dtype=float)
    losses = []
    for held_out in range(len(prompt_values)):
        training_mean = np.delete(prompt_values, held_out, axis=0).mean(axis=0)
        prediction = np.zeros_like(training_mean)
        for metric_index in range(training_mean.shape[1]):
            coefficients = np.polyfit(layers, training_mean[:, metric_index], degree)
            prediction[:, metric_index] = np.polyval(coefficients, layers)
        losses.append(float(np.mean((prompt_values[held_out] - prediction) ** 2)))
    return float(np.mean(losses))


def polynomial_fit_stats(values: np.ndarray, degree: int) -> tuple[float, int]:
    layers = np.arange(values.shape[0], dtype=float)
    prediction = np.zeros_like(values)
    for metric_index in range(values.shape[1]):
        coefficients = np.polyfit(layers, values[:, metric_index], degree)
        prediction[:, metric_index] = np.polyval(coefficients, layers)
    rss = float(np.sum((values - prediction) ** 2))
    n_parameters = (degree + 1) * values.shape[1]
    return rss, n_parameters


def bic_score(rss: float, n_observations: int, n_parameters: int) -> float:
    adjusted_rss = max(rss, np.finfo(float).tiny)
    return n_observations * math.log(adjusted_rss / n_observations) + n_parameters * math.log(
        n_observations
    )


def run_analysis(args: argparse.Namespace) -> dict[str, Any]:
    graph_paths = sorted(args.graph_dir.glob("analog_*.json"))
    if len(graph_paths) != 5:
        raise RuntimeError(f"Expected five graph files in {args.graph_dir}, found {len(graph_paths)}")

    prompt_names = [path.stem for path in graph_paths]
    prompt_values = np.stack(
        [
            standardize_within_prompt(
                graph_layer_metrics(json.loads(path.read_text(encoding="utf-8")))
            )
            for path in graph_paths
        ]
    )
    aggregate = prompt_values.mean(axis=0)
    model_rows = []
    n_observations = aggregate.size
    n_metrics = aggregate.shape[1]

    for n_boundaries in range(args.max_boundaries + 1):
        boundaries, rss = exact_segmentation(
            aggregate, n_boundaries, args.min_segment_size
        )
        n_parameters = (n_boundaries + 1) * n_metrics + n_boundaries
        model_rows.append(
            {
                "n_boundaries": n_boundaries,
                "n_phases": n_boundaries + 1,
                "boundaries": boundaries,
                "segments": [
                    [start, end - 1]
                    for start, end in zip(
                        [0, *boundaries], [*boundaries, len(aggregate)]
                    )
                ],
                "rss": rss,
                "bic": bic_score(rss, n_observations, n_parameters),
                "leave_one_prompt_out_loss": piecewise_cv_loss(
                    prompt_values, n_boundaries, args.min_segment_size
                ),
            }
        )

    selected = min(model_rows, key=lambda row: row["bic"])
    cv_selected = min(model_rows, key=lambda row: row["leave_one_prompt_out_loss"])
    polynomial_models = []
    for degree in (1, 2, 3):
        rss, n_parameters = polynomial_fit_stats(aggregate, degree)
        polynomial_models.append(
            {
                "degree": degree,
                "rss": rss,
                "bic": bic_score(rss, n_observations, n_parameters),
                "n_parameters": n_parameters,
                "leave_one_prompt_out_loss": polynomial_cv_loss(prompt_values, degree),
            }
        )
    overall_bic_candidates = [
        {
            "family": "piecewise",
            "name": f"{row['n_phases']}-phase",
            "bic": row["bic"],
        }
        for row in model_rows
    ] + [
        {
            "family": "smooth_polynomial",
            "name": f"degree-{row['degree']}",
            "bic": row["bic"],
        }
        for row in polynomial_models
    ]

    rng = np.random.default_rng(args.seed)
    selected_k_counts = Counter()
    boundary_counts = Counter()
    fixed_k = selected["n_boundaries"]
    for _ in range(args.bootstrap_samples):
        indexes = rng.integers(0, len(prompt_values), size=len(prompt_values))
        bootstrap_aggregate = prompt_values[indexes].mean(axis=0)
        bootstrap_models = []
        for n_boundaries in range(args.max_boundaries + 1):
            boundaries, rss = exact_segmentation(
                bootstrap_aggregate, n_boundaries, args.min_segment_size
            )
            parameters = (n_boundaries + 1) * n_metrics + n_boundaries
            bootstrap_models.append(
                (
                    bic_score(rss, n_observations, parameters),
                    n_boundaries,
                    boundaries,
                )
            )
        _, selected_k, _ = min(bootstrap_models)
        selected_k_counts[selected_k] += 1
        fixed_boundaries, _ = exact_segmentation(
            bootstrap_aggregate, fixed_k, args.min_segment_size
        )
        boundary_counts[tuple(fixed_boundaries)] += 1

    return {
        "scope": "objective graph metrics only; no semantic phase labels",
        "prompt_names": prompt_names,
        "metric_names": list(METRIC_NAMES),
        "normalization": "within-prompt z-score for each metric",
        "minimum_segment_size": args.min_segment_size,
        "candidate_piecewise_models": model_rows,
        "bic_selected_model": selected,
        "cross_validation_selected_model": cv_selected,
        "smooth_polynomial_controls": polynomial_models,
        "overall_bic_selected_model": min(overall_bic_candidates, key=lambda row: row["bic"]),
        "bootstrap": {
            "samples": args.bootstrap_samples,
            "bic_selected_boundary_count_frequency": {
                str(key): value for key, value in sorted(selected_k_counts.items())
            },
            "fixed_bic_model_boundary_frequency_top_10": [
                {"boundaries": list(boundaries), "count": count}
                for boundaries, count in boundary_counts.most_common(10)
            ],
        },
    }


def write_report(result: dict[str, Any], output_path: Path) -> None:
    selected = result["bic_selected_model"]
    cv_selected = result["cross_validation_selected_model"]
    lines = [
        "# Objective Layer Segmentation Audit",
        "",
        "This analysis uses graph statistics only. It does not establish semantic phase roles.",
        "",
        "## Candidate piecewise models",
        "",
        "| Phases | Boundaries | BIC | Leave-one-prompt-out loss |",
        "|---:|---|---:|---:|",
    ]
    for row in result["candidate_piecewise_models"]:
        lines.append(
            f"| {row['n_phases']} | {row['boundaries']} | {row['bic']:.3f} | "
            f"{row['leave_one_prompt_out_loss']:.6f} |"
        )
    lines.extend(
        [
            "",
            f"BIC selected **{selected['n_phases']} phase(s)** with boundaries "
            f"{selected['boundaries']}.",
            "",
            f"Leave-one-prompt-out prediction selected **{cv_selected['n_phases']} phase(s)** "
            f"with full-data boundaries {cv_selected['boundaries']}.",
            "",
            "## Smooth controls",
            "",
            "| Polynomial degree | BIC | Leave-one-prompt-out loss |",
            "|---:|---:|---:|",
        ]
    )
    for row in result["smooth_polynomial_controls"]:
        lines.append(
            f"| {row['degree']} | {row['bic']:.3f} | "
            f"{row['leave_one_prompt_out_loss']:.6f} |"
        )
    lines.extend(
        [
            "",
            f"Across both model families, BIC selected **{result['overall_bic_selected_model']['name']}** "
            f"({result['overall_bic_selected_model']['family']}).",
            "",
            "A publishable semantic phase claim additionally requires blinded feature annotations, "
            "held-out prompts, stable boundaries, and independent causal validation.",
        ]
    )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result = run_analysis(args)
    json_path = args.output_dir / "numeric_phase_detection.json"
    report_path = args.output_dir / "numeric_phase_detection.md"
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_report(result, report_path)
    print(json.dumps(result, indent=2))
    print(f"Report written to {report_path.resolve()}")


if __name__ == "__main__":
    main()
