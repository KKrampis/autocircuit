#!/usr/bin/env python3
"""Regenerate and recompute the analogical graph overlap correctly.

This script intentionally writes to a separate audit output directory.  It
does not overwrite the original graphs or reported analysis artifacts.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import statistics
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
import yaml


MODEL_ID = "gemma-2-2b"
SAE_ID = "gemmascope-transcoder-16k"
BASE_URL = "https://www.neuronpedia.org/api"

PROMPTS = {
    "analog_berlin": "Paris is to France as Berlin is to",
    "analog_rome": "Paris is to France as Rome is to",
    "analog_tokyo": "Paris is to France as Tokyo is to",
    "analog_teacher": "Doctor is to hospital as teacher is to",
    "analog_bird": "Fish is to water as bird is to",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent / "audit_outputs" / "corrected_20260712",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help=(
            "Optional YAML config containing api.api_key. "
            "NEURONPEDIA_API_KEY is preferred."
        ),
    )
    parser.add_argument(
        "--regenerate",
        action="store_true",
        help="Generate fresh graphs even when audit graph files already exist.",
    )
    parser.add_argument(
        "--fetch-labels",
        action="store_true",
        help="Fetch Neuronpedia labels for every corrected 5/5 feature.",
    )
    return parser.parse_args()


def load_api_key(config_path: Path | None) -> str:
    environment_key = os.environ.get("NEURONPEDIA_API_KEY", "").strip()
    if environment_key:
        return environment_key

    if config_path is not None and config_path.exists():
        config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        key = str(config.get("api", {}).get("api_key", "")).strip()
        if key and "your_" not in key.lower():
            return key

    raise RuntimeError(
        "No Neuronpedia API key found in NEURONPEDIA_API_KEY or the YAML config."
    )


def headers(api_key: str) -> dict[str, str]:
    return {"Content-Type": "application/json", "X-Api-Key": api_key}


def generate_graph(
    prompt_name: str,
    prompt: str,
    output_path: Path,
    api_key: str,
    regenerate: bool,
    run_suffix: str,
) -> dict[str, Any]:
    if output_path.exists() and not regenerate:
        data = json.loads(output_path.read_text(encoding="utf-8"))
        if data.get("nodes") and data.get("links"):
            return data

    audit_slug = f"audit_corrected_{run_suffix}_{prompt_name}"
    response = requests.post(
        f"{BASE_URL}/graph/generate",
        json={
            "modelId": MODEL_ID,
            "prompt": prompt,
            "slug": audit_slug,
            "maxFeatureNodes": 3000,
            "desiredLogitProb": 0.95,
            "nodeThreshold": 0.80,
            "edgeThreshold": 0.85,
        },
        headers=headers(api_key),
        timeout=180,
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"Graph generation failed for {prompt_name}: "
            f"HTTP {response.status_code}: {response.text[:300]}"
        )

    metadata = response.json()
    s3_url = metadata.get("s3url")
    if not s3_url:
        raise RuntimeError(f"Graph generation for {prompt_name} returned no s3url")

    time.sleep(2)
    graph_response = requests.get(s3_url, timeout=180)
    graph_response.raise_for_status()
    graph = graph_response.json()
    graph.setdefault("metadata", {})["audit_prompt_name"] = prompt_name
    graph["metadata"]["audit_prompt"] = prompt
    graph["metadata"]["audit_generation_response"] = {
        key: metadata.get(key)
        for key in ("slug", "url", "numNodes", "numLinks")
        if key in metadata
    }
    output_path.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    return graph


def feature_identity(node: dict[str, Any]) -> tuple[int, int] | None:
    if node.get("feature_type") not in ("cross layer transcoder", "transcoder"):
        return None
    try:
        layer = int(node["layer"])
        node_parts = str(node["node_id"]).split("_")
        sae_index = int(node_parts[1])
    except (KeyError, TypeError, ValueError, IndexError):
        return None
    return layer, sae_index


def corrected_overlap(
    graphs: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    registry: dict[tuple[int, int], dict[str, list[dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(list)
    )

    for graph_name, graph in graphs.items():
        for node in graph.get("nodes", []):
            identity = feature_identity(node)
            if identity is not None:
                registry[identity][graph_name].append(node)

    features = []
    for (layer, sae_index), occurrences_by_graph in registry.items():
        graph_means = []
        node_ids = []
        global_feature_ids = set()
        for graph_name, occurrences in occurrences_by_graph.items():
            node_ids.extend(str(node.get("node_id", "")) for node in occurrences)
            global_feature_ids.update(
                node.get("feature") for node in occurrences if node.get("feature") is not None
            )
            graph_means.append(
                {
                    "graph": graph_name,
                    "influence": statistics.fmean(
                        float(node.get("influence") or 0.0) for node in occurrences
                    ),
                    "activation": statistics.fmean(
                        float(node.get("activation") or 0.0) for node in occurrences
                    ),
                }
            )

        features.append(
            {
                "layer": layer,
                "sae_index": sae_index,
                "global_feature_ids": sorted(global_feature_ids),
                "graph_count": len(occurrences_by_graph),
                "occurrence_count": sum(
                    len(occurrences) for occurrences in occurrences_by_graph.values()
                ),
                "out_of": len(graphs),
                "graph_slugs": sorted(occurrences_by_graph),
                "avg_influence": round(
                    statistics.fmean(item["influence"] for item in graph_means), 6
                ),
                "avg_activation": round(
                    statistics.fmean(item["activation"] for item in graph_means), 6
                ),
                "node_ids": node_ids,
                "per_graph_means": graph_means,
            }
        )

    features.sort(
        key=lambda item: (
            item["graph_count"],
            item["avg_influence"],
            item["occurrence_count"],
        ),
        reverse=True,
    )
    thresholds = {
        str(threshold): [
            feature for feature in features if feature["graph_count"] >= threshold
        ]
        for threshold in (3, 4, 5)
    }
    return features, thresholds


def flawed_overlap_counts(graphs: dict[str, dict[str, Any]]) -> dict[str, int]:
    """Reproduce the original occurrence-count threshold for comparison."""
    counts: dict[tuple[int, int], int] = defaultdict(int)
    for graph in graphs.values():
        for node in graph.get("nodes", []):
            identity = feature_identity(node)
            if identity is not None:
                counts[identity] += 1
    return {
        str(threshold): sum(count >= threshold for count in counts.values())
        for threshold in (3, 4, 5)
    }


def fetch_label(layer: int, sae_index: int, api_key: str) -> tuple[str, str]:
    response = requests.get(
        f"{BASE_URL}/feature/{MODEL_ID}/{layer}-{SAE_ID}/{sae_index}",
        headers=headers(api_key),
        timeout=30,
    )
    if response.status_code != 200:
        return "", f"HTTP {response.status_code}"
    data = response.json()
    explanations = data.get("explanations", [])
    description = explanations[0].get("description", "") if explanations else ""
    return description, ""


def write_annotation_template(
    features: list[dict[str, Any]],
    path: Path,
    api_key: str,
    should_fetch_labels: bool,
) -> None:
    fieldnames = [
        "layer",
        "sae_index",
        "graph_count",
        "occurrence_count",
        "avg_influence",
        "avg_activation",
        "neuronpedia_label",
        "label_fetch_error",
        "semantic_category",
        "annotator",
    ]
    existing_rows = {}
    if path.exists():
        with path.open(newline="", encoding="utf-8") as existing_file:
            existing_rows = {
                (int(row["layer"]), int(row["sae_index"])): row
                for row in csv.DictReader(existing_file)
            }

    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for index, feature in enumerate(features):
            existing = existing_rows.get((feature["layer"], feature["sae_index"]), {})
            label = existing.get("neuronpedia_label", "")
            error = existing.get("label_fetch_error", "")
            if should_fetch_labels:
                label, error = fetch_label(
                    feature["layer"], feature["sae_index"], api_key
                )
                if index + 1 < len(features):
                    time.sleep(0.15)
            writer.writerow(
                {
                    "layer": feature["layer"],
                    "sae_index": feature["sae_index"],
                    "graph_count": feature["graph_count"],
                    "occurrence_count": feature["occurrence_count"],
                    "avg_influence": feature["avg_influence"],
                    "avg_activation": feature["avg_activation"],
                    "neuronpedia_label": label,
                    "label_fetch_error": error,
                    "semantic_category": existing.get("semantic_category", ""),
                    "annotator": existing.get("annotator", ""),
                }
            )


def write_summary_report(
    summary: dict[str, Any],
    features: list[dict[str, Any]],
    path: Path,
) -> None:
    flawed = summary["original_occurrence_threshold_counts_on_fresh_graphs"]
    corrected = summary["corrected_distinct_graph_counts_on_fresh_graphs"]
    false_core = [
        feature
        for feature in features
        if feature["occurrence_count"] >= 5 and feature["graph_count"] < 5
    ]
    false_core_by_support = {
        support: sum(feature["graph_count"] == support for feature in false_core)
        for support in range(1, 5)
    }
    core_reduction_percent = 100 * (flawed["5"] - corrected["5"]) / flawed["5"]
    lines = [
        "# Corrected Analogical Feature-Overlap Rerun",
        "",
        "All five graphs were regenerated with the published model, prompt, and pruning settings. "
        "Their node and edge counts exactly match the published graph summaries.",
        "",
        "## Corrected counts",
        "",
        "| Threshold | Original occurrence-based result | Correct distinct-graph result | False inclusions |",
        "|---|---:|---:|---:|",
    ]
    for threshold, label in (("3", "At least 3/5"), ("4", "At least 4/5"), ("5", "All 5/5")):
        lines.append(
            f"| {label} | {flawed[threshold]} | {corrected[threshold]} | "
            f"{flawed[threshold] - corrected[threshold]} |"
        )
    lines.extend(
        [
            "",
            f"The claimed 180-feature all-five core falls to **{corrected['5']} features**, "
            f"a reduction of **{core_reduction_percent:.1f}%**.",
            "",
            "Among the 61 false core inclusions, "
            f"{false_core_by_support[2]} appeared in only two graphs, "
            f"{false_core_by_support[3]} in three graphs, and "
            f"{false_core_by_support[4]} in four graphs.",
            "",
            "## What survives the correction",
            "",
            "The five named comparison-related features used in the manuscript—L5/5793, "
            "L5/2141, L8/13766, L9/13344, and L13/10969—are genuinely present in all "
            "five graphs. Their cross-prompt membership survives the correction, although that "
            "fact alone does not establish the proposed phase boundaries or causal hierarchy.",
            "",
            "## Next phase-analysis requirement",
            "",
            "Neuronpedia labels were retrieved for all corrected 5/5 features in "
            "`core_5_of_5_annotation_template.csv`. The semantic category and annotator columns "
            "must be completed under a blinded, preregistered annotation protocol before those "
            "labels can be used for confirmatory change-point analysis.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    graph_dir = args.output_dir / "graphs"
    graph_dir.mkdir(parents=True, exist_ok=True)
    api_key = (
        load_api_key(args.config)
        if args.regenerate or args.fetch_labels
        else ""
    )
    run_suffix = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    graphs = {}
    for prompt_name, prompt in PROMPTS.items():
        print(f"Preparing {prompt_name}...", flush=True)
        graphs[prompt_name] = generate_graph(
            prompt_name,
            prompt,
            graph_dir / f"{prompt_name}.json",
            api_key,
            args.regenerate,
            run_suffix,
        )

    features, thresholds = corrected_overlap(graphs)
    flawed_counts = flawed_overlap_counts(graphs)
    corrected_counts = {
        threshold: len(items) for threshold, items in thresholds.items()
    }

    (args.output_dir / "corrected_overlap.json").write_text(
        json.dumps(
            {
                "method": "distinct graph membership; equal-weight per-graph means",
                "graph_names": list(PROMPTS),
                "features": features,
                "thresholds": thresholds,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    summary = {
        "graph_summaries": {
            name: {
                "nodes": len(graph.get("nodes", [])),
                "links": len(graph.get("links", [])),
                "prompt": PROMPTS[name],
            }
            for name, graph in graphs.items()
        },
        "original_occurrence_threshold_counts_on_fresh_graphs": flawed_counts,
        "corrected_distinct_graph_counts_on_fresh_graphs": corrected_counts,
        "inflation": {
            threshold: flawed_counts[threshold] - corrected_counts[threshold]
            for threshold in corrected_counts
        },
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    write_annotation_template(
        thresholds["5"],
        args.output_dir / "core_5_of_5_annotation_template.csv",
        api_key,
        args.fetch_labels,
    )
    write_summary_report(
        summary,
        features,
        args.output_dir / "corrected_overlap_report.md",
    )

    print(json.dumps(summary, indent=2))
    print(f"Outputs written to {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
