"""YAML-driven supernode intervention runner.

Loads experiment definitions from YAML files and runs supernode interventions
to test circuit hypotheses. Reproduces the workflow from
demo/circuit_tracing_tutorial.py in a declarative, terminal-friendly format.

Usage:
    # Run all experiments in a YAML config
    python -m graph_analysis.run_intervention \\
        --config experiments/capital_cities.yaml

    # Run a specific experiment
    python -m graph_analysis.run_intervention \\
        --config experiments/capital_cities.yaml \\
        --experiment ablate_say_capital

    # Save SVG visualizations
    python -m graph_analysis.run_intervention \\
        --config experiments/capital_cities.yaml \\
        --save_graph --graph_dir output/graphs/

    # Output as JSON
    python -m graph_analysis.run_intervention \\
        --config experiments/capital_cities.yaml --json
"""

import argparse
import copy
import json
import os
import sys
from urllib.parse import urlparse, parse_qs, urlencode, quote

from circuit_tracer.utils.demo_utils import extract_supernode_features

from graph_analysis.api.graph import fetch_graph_metadata, parse_neuronpedia_url
from graph_analysis.api.subgraph import fetch_subgraph_list
from graph_analysis.utils import (
    Feature,
    Supernode,
    InterventionGraph,
    Intervention,
    load_model,
    get_top_outputs,
    print_top_outputs,
)
from graph_analysis.utils.yaml_loader import (
    load_experiment_config,
    build_supernodes,
    resolve_graph_layout,
    resolve_interventions,
)


# ---------------------------------------------------------------------------
# URL helpers (kept from original for standalone URL-based usage)
# ---------------------------------------------------------------------------


def url_valid_graph(url: str) -> bool:
    """Check if a Neuronpedia URL contains pinnedIds and supernodes query parameters."""
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    return "pinnedIds" in query and bool(query["pinnedIds"][0]) and "supernodes" in query and bool(query["supernodes"][0])


def enrich_url_from_subgraph(url: str, api_key: str) -> str:
    """If URL lacks pinnedIds, fetch them from subgraph list API and rebuild URL.

    Uses the `subgraph` query param in the URL to match the correct subgraph.
    """
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    subgraph_id = query.get("subgraph", [None])[0]

    if not subgraph_id:
        print("Error: URL has no pinnedIds or supernodes and no subgraph param.", file=sys.stderr)
        sys.exit(1)

    model_id, slug = parse_neuronpedia_url(url)
    subgraphs = fetch_subgraph_list(model_id, slug, api_key)

    if not subgraphs:
        print(f"Error: No subgraphs found for {model_id}/{slug}.", file=sys.stderr)
        sys.exit(1)

    sg = next((s for s in subgraphs if s["id"] == subgraph_id), None)
    if sg is None:
        available = [f"  {s['id']} ({s.get('displayName', 'unnamed')})" for s in subgraphs]
        print(f"Error: Subgraph '{subgraph_id}' not found. Available:", file=sys.stderr)
        print("\n".join(available), file=sys.stderr)
        sys.exit(1)

    print(f"  Using subgraph: {sg.get('displayName', sg['id'])}")

    parsed = urlparse(url)
    query = parse_qs(parsed.query, keep_blank_values=True)
    query["pinnedIds"] = [",".join(sg["pinnedIds"])]
    query["supernodes"] = [json.dumps(sg["supernodes"])]
    if sg.get("clerps"):
        query["clerps"] = [json.dumps(sg["clerps"])]

    new_query = urlencode(query, doseq=True, quote_via=quote)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"


def build_supernodes_from_url(url: str) -> dict[str, Supernode]:
    """Extract supernodes from a Neuronpedia URL and create Supernode objects."""
    supernode_features = extract_supernode_features(url)
    return {name: Supernode(name=name, features=features) for name, features in supernode_features.items()}


def get_prompt_from_url(url: str) -> str:
    """Fetch the prompt associated with a Neuronpedia graph URL."""
    model_id, slug = parse_neuronpedia_url(url)
    metadata = fetch_graph_metadata(model_id, slug)
    prompt = metadata["prompt"]
    if prompt.startswith("<bos>"):
        prompt = prompt[len("<bos>"):]
    return prompt


def prepare_url(url: str, api_key: str | None) -> str:
    """Ensure URL has pinnedIds and supernodes, enriching from subgraph list API if needed."""
    if url_valid_graph(url):
        return url

    print("  URL missing pinnedIds or supernodes, fetching from subgraph list API...")
    if not api_key:
        print("Error: URL has no pinnedIds or supernodes and no --api_key provided.", file=sys.stderr)
        sys.exit(1)

    return enrich_url_from_subgraph(url, api_key)


# ---------------------------------------------------------------------------
# Core intervention logic
# ---------------------------------------------------------------------------


def supernode_intervention(
    model,
    intervention_graph: InterventionGraph,
    interventions: list[Intervention],
    replacements: dict[str, Supernode] | None = None,
) -> dict:
    """Perform supernode interventions and return structured results.

    Always prints a text summary describing the intervention outcome,
    including top outputs, activation fractions, and replacements.

    Args:
        model: ReplacementModel instance.
        intervention_graph: The graph containing supernodes to intervene on.
        interventions: List of Intervention(supernode, scaling_factor).
        replacements: Optional dict mapping target node name -> replacement Supernode.

    Returns:
        dict with top_outputs, node_activations, interventions_applied, replacements_applied.
    """
    intervention_values = [
        (*feature, scaling_factor * default_act)
        for intervened_supernode, scaling_factor in interventions
        for feature, default_act in zip(
            intervened_supernode.features, intervened_supernode.default_activations
        )
    ]
    new_logits, new_activations = model.feature_intervention(
        intervention_graph.prompt, intervention_values
    )
    intervention_graph.set_node_activation_fractions(new_activations)
    top_outputs = get_top_outputs(new_logits, model.tokenizer)

    for intervened_supernode, scaling_factor in interventions:
        intervened_supernode.activation = None
        intervened_supernode.intervention = f"{scaling_factor}x"

    replacements_applied = []
    if replacements is not None:
        for target, replacement in replacements.items():
            intervention_graph.nodes[target].replacement_node = replacement
            replacements_applied.append({"target": target, "replacement": replacement.name})

    results = {
        "top_outputs": top_outputs,
        "node_activations": intervention_graph.get_activation_summary(),
        "interventions_applied": [
            {"supernode": s.name, "scaling_factor": sf}
            for s, sf in interventions
        ],
        "replacements_applied": replacements_applied,
    }

    # Always print text summary
    print_intervention_results(results)

    return results


def print_intervention_results(results: dict, experiment_name: str = ""):
    """Print intervention results describing what the visualization would show.

    Prints interventions applied, top outputs after intervention,
    node activation fractions, and replacements.
    """
    if experiment_name:
        print(f"\n{'=' * 60}")
        print(f"  Experiment: {experiment_name}")
        print(f"{'=' * 60}")

    print("\n  Interventions applied:")
    for iv in results["interventions_applied"]:
        print(f"    {iv['supernode']}: {iv['scaling_factor']}x")

    print_top_outputs(results["top_outputs"], label="  Top outputs after intervention")

    intervened_names = {iv["supernode"] for iv in results["interventions_applied"]}

    print("\n  Node activations (relative to baseline):")
    for name, act in results["node_activations"].items():
        if act is None:
            if name in intervened_names:
                print(f"    {name}: [intervened]")
            else:
                print(f"    {name}: [no features]")
        else:
            pct = act * 100
            indicator = ""
            if pct <= 25:
                indicator = " (grayed out in SVG)"
            elif pct >= 150:
                indicator = " (amplified)"
            print(f"    {name}: {pct:.0f}%{indicator}")

    if results.get("replacements_applied"):
        print("\n  Replacements (visual node swaps):")
        for r in results["replacements_applied"]:
            print(f"    {r['target']} -> {r['replacement']}")
    else:
        print("\n  Replacements: none")


def save_graph_svg(
    intervention_graph: InterventionGraph,
    top_outputs: list[tuple[str, float]],
    output_path: str,
):
    """Save graph visualization as SVG file.

    Imports create_graph_visualization from demo.graph_visualization,
    which returns an IPython.display.SVG object.
    """
    from demo.graph_visualization import create_graph_visualization

    svg_obj = create_graph_visualization(intervention_graph, top_outputs)
    svg_data = svg_obj.data

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(svg_data)
    print(f"  Saved SVG: {output_path}")


# ---------------------------------------------------------------------------
# Experiment runner
# ---------------------------------------------------------------------------


def run_experiment(
    model,
    config: dict,
    experiment_name: str,
    supernodes: dict[str, Supernode],
    pos_offsets: dict[str, int],
    activations_cache: dict[str, tuple],
    save_graph: bool = False,
    graph_dir: str = ".tmp/run_intervention",
) -> dict:
    """Run a single experiment from a YAML config.

    Steps:
    1. Deep-copy supernodes for state isolation
    2. Build InterventionGraph from graph_layout
    3. Get activations for each prompt in 'initialize' (with caching)
    4. Initialize nodes from their respective prompt activations
    5. Apply pos_offset for nodes that need position shifting
    6. For each intervention: run, print results, optionally save SVG

    Returns dict with experiment results.
    """
    exp_config = config["experiments"][experiment_name]
    prompts = config["prompts"]

    print(f"\n{'=' * 60}")
    print(f"  Experiment: {experiment_name}")
    if "description" in exp_config:
        print(f"  {exp_config['description']}")
    print(f"{'=' * 60}")

    # Deep-copy supernodes to isolate state between experiments
    exp_supernodes = copy.deepcopy(supernodes)

    # Resolve graph layout
    ordered_nodes = resolve_graph_layout(config, exp_config, exp_supernodes)

    # Resolve prompt
    prompt_key = exp_config["prompt"]
    if prompt_key not in prompts:
        raise ValueError(f"Prompt '{prompt_key}' not found in prompts config")
    prompt = prompts[prompt_key]
    print(f"  Prompt: {prompt!r}")

    # Build intervention graph
    intervention_graph = InterventionGraph(ordered_nodes=ordered_nodes, prompt=prompt)

    # Initialize nodes from activations
    init_config = exp_config["initialize"]
    for init_prompt_key, node_keys in init_config.items():
        if init_prompt_key not in prompts:
            raise ValueError(f"Initialize prompt '{init_prompt_key}' not found in prompts config")
        init_prompt = prompts[init_prompt_key]

        # Cache activations per prompt
        if init_prompt_key not in activations_cache:
            print(f"  Getting activations for prompt: {init_prompt!r}")
            logits, activations = model.get_activations(init_prompt)
            activations_cache[init_prompt_key] = (logits, activations)

        _, activations = activations_cache[init_prompt_key]

        for node_key in node_keys:
            if node_key not in exp_supernodes:
                raise ValueError(f"Node '{node_key}' referenced in initialize but not defined")
            intervention_graph.initialize_node(exp_supernodes[node_key], activations)

    # Apply pos_offset AFTER initialization (matches tutorial pattern)
    for node_key, offset in pos_offsets.items():
        if node_key in exp_supernodes and exp_supernodes[node_key].features:
            exp_supernodes[node_key].features = [
                Feature(f.layer, f.pos + offset, f.feature_idx)
                for f in exp_supernodes[node_key].features
            ]

    # Set baseline activation fractions
    base_prompt_key = exp_config["prompt"]
    _, base_activations = activations_cache[base_prompt_key]
    intervention_graph.set_node_activation_fractions(base_activations)

    # Print baseline top outputs
    base_logits, _ = activations_cache[base_prompt_key]
    baseline_top = get_top_outputs(base_logits, model.tokenizer)
    print_top_outputs(baseline_top, label="  Baseline top outputs")

    # Run interventions
    all_results = []
    for i, intervention_def in enumerate(exp_config["interventions"]):
        # Reset graph state before each intervention
        intervention_graph.set_node_activation_fractions(base_activations)

        interventions, replacements = resolve_interventions(
            intervention_def, exp_supernodes
        )

        results = supernode_intervention(
            model, intervention_graph, interventions, replacements
        )
        results["baseline_top_outputs"] = baseline_top
        all_results.append(results)

        if save_graph:
            svg_name = f"{experiment_name}_{i}.svg" if len(exp_config["interventions"]) > 1 else f"{experiment_name}.svg"
            svg_path = os.path.join(graph_dir, svg_name)
            save_graph_svg(intervention_graph, results["top_outputs"], svg_path)

    return {
        "experiment": experiment_name,
        "description": exp_config.get("description", ""),
        "prompt": prompt,
        "baseline_top_outputs": baseline_top,
        "interventions": all_results,
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="YAML-driven supernode intervention runner."
    )
    parser.add_argument(
        "--config", required=True,
        help="Path to YAML experiment config file"
    )
    parser.add_argument(
        "--experiment", nargs="*",
        help="Specific experiment(s) to run. If omitted, runs all."
    )
    parser.add_argument(
        "--save_graph", action="store_true",
        help="Save SVG graph visualizations to files"
    )
    parser.add_argument(
        "--graph_dir", default=".tmp/run_intervention",
        help="Directory for SVG output files (default: .tmp/run_intervention)"
    )
    parser.add_argument(
        "--api_key",
        help="Neuronpedia API key (needed if graph URLs lack pinnedIds and supernodes query params)"
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output structured JSON results"
    )
    args = parser.parse_args()

    # 1. Load YAML config
    print(f"Loading config: {args.config}")
    config = load_experiment_config(args.config)

    # 2. Prepare graph URLs (enrich with pinnedIds if needed)
    for name, url in config.get("graphs", {}).items():
        config["graphs"][name] = prepare_url(url, args.api_key)

    # 3. Build supernodes (resolve features from URLs)
    print("Building supernodes...")
    extracted_cache = {}
    supernodes, pos_offsets = build_supernodes(config, extracted_cache)
    print(f"  Defined supernodes: {list(supernodes.keys())}")

    # 4. Load model
    model_cfg = config["model"]
    print(f"Loading model: {model_cfg['name']}")
    model = load_model(model_cfg["name"], model_cfg["transcoder"], model_cfg["backend"])

    # 5. Determine which experiments to run
    experiments_to_run = args.experiment or list(config["experiments"].keys())
    for exp_name in experiments_to_run:
        if exp_name not in config["experiments"]:
            print(f"Error: Experiment '{exp_name}' not found in config.", file=sys.stderr)
            print(f"Available: {list(config['experiments'].keys())}", file=sys.stderr)
            sys.exit(1)

    # 6. Run experiments
    activations_cache = {}
    all_results = {}

    for exp_name in experiments_to_run:
        results = run_experiment(
            model, config, exp_name, supernodes, pos_offsets,
            activations_cache,
            save_graph=args.save_graph,
            graph_dir=args.graph_dir,
        )
        all_results[exp_name] = results

    # 7. JSON output
    if args.json:
        print("\n" + json.dumps(all_results, indent=2, default=str))

    print(f"\nDone. Ran {len(all_results)} experiment(s).")


if __name__ == "__main__":
    main()