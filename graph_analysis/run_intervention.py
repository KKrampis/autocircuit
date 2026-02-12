"""Run supernode interventions to test circuit hypotheses.

Todo:
- --activate "California:2" "California (2):2" is a separate node
  - the print_intervention function currently prints both nodes: "California" and "California (2)"
  - How to specify it as a supernode called "California"?
  - How to specify that "California" supernode have children "Ssay Sacramento" supernode?
    - Can we write it in a .yaml file to be able to mimic what demo/circuit_tracing_tutorial.py?
  - replacement doesn't work as intended "replace node with another node"
  
Performs ablation or replacement interventions on supernodes extracted from
Neuronpedia-annotated graphs, then reports structured results (top outputs,
activation fractions) suitable for agent consumption.

The prompt is fetched automatically from the Neuronpedia API using the URL's
model_id and slug. The URL must contain pinnedIds and supernodes query params
(from an annotated Neuronpedia graph). If pinnedIds are missing, the URL must
contain a subgraph query param so the script can fetch the correct subgraph
from the Neuronpedia API (requires --api_key).

Usage:
    # Ablate a supernode (set to -2x its default activation)
    python -m graph_analysis.run_intervention \
        --source_url "https://www.neuronpedia.org/gemma-2-2b/graph?slug=...&pinnedIds=...&supernodes=..." \
        --intervene "Texas:-2"

    # Ablate one supernode and activate another from a different prompt
    python -m graph_analysis.run_intervention \
        --source_url "https://www.neuronpedia.org/gemma-2-2b/graph?slug=...&pinnedIds=...&supernodes=..." \
        --intervene "Texas:-2" \
        --replacement_url "https://www.neuronpedia.org/gemma-2-2b/graph?slug=...&pinnedIds=...&supernodes=..." \
        --activate "California:2"
"""

import argparse
import json
import sys
from urllib.parse import urlparse, parse_qs, urlencode, quote

from circuit_tracer.utils.demo_utils import extract_supernode_features

from graph_analysis.api.graph import fetch_graph_metadata, parse_neuronpedia_url
from graph_analysis.api.subgraph import fetch_subgraph_list
from graph_analysis.utils import (
    Supernode,
    InterventionGraph,
    Intervention,
    load_model,
    get_top_outputs,
    print_top_outputs,
)


def url_has_pinned_ids(url: str) -> bool:
    """Check if a Neuronpedia URL contains pinnedIds query parameter."""
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    return "pinnedIds" in query and bool(query["pinnedIds"][0])


def enrich_url_from_subgraph(url: str, api_key: str) -> str:
    """If URL lacks pinnedIds, fetch them from subgraph list API and rebuild URL.

    Uses the `subgraph` query param in the URL to match the correct subgraph.
    If the URL has no `subgraph` param, exits with an error.

    Args:
        url: Neuronpedia graph URL with `subgraph` param but missing pinnedIds.
        api_key: Neuronpedia API key.

    Returns:
        URL with pinnedIds and supernodes added from the matched subgraph.
    """
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    subgraph_id = query.get("subgraph", [None])[0]

    if not subgraph_id:
        print("Error: URL has no pinnedIds and no subgraph param.", file=sys.stderr)
        print("Cannot determine which subgraph to use.", file=sys.stderr)
        print("Provide a URL with either pinnedIds+supernodes or a subgraph param.", file=sys.stderr)
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

    # Rebuild URL with pinnedIds and supernodes from the subgraph
    parsed = urlparse(url)
    query = parse_qs(parsed.query, keep_blank_values=True)
    query["pinnedIds"] = [",".join(sg["pinnedIds"])]
    query["supernodes"] = [json.dumps(sg["supernodes"])]
    if sg.get("clerps"):
        query["clerps"] = [json.dumps(sg["clerps"])]

    new_query = urlencode(query, doseq=True, quote_via=quote)
    enriched_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"
    return enriched_url


def build_supernodes_from_url(url: str) -> dict[str, Supernode]:
    """Extract supernodes from a Neuronpedia URL and create Supernode objects.

    Returns dict mapping supernode name -> Supernode.
    """
    supernode_features = extract_supernode_features(url)
    supernodes = {}
    for name, features in supernode_features.items():
        supernodes[name] = Supernode(name=name, features=features)
    return supernodes


def get_prompt_from_url(url: str) -> str:
    """Fetch the prompt associated with a Neuronpedia graph URL."""
    model_id, slug = parse_neuronpedia_url(url)
    metadata = fetch_graph_metadata(model_id, slug)
    prompt = metadata["prompt"]
    # strip <bos> tags if present?
    if prompt.startswith("<bos>"):
        prompt = prompt[len("<bos>") :]
    return prompt


def supernode_intervention(
    model,
    intervention_graph: InterventionGraph,
    interventions: list[Intervention],
    replacements: dict[str, Supernode] | None = None,
) -> dict:
    """Perform supernode interventions and return structured results.

    Args:
        model: ReplacementModel instance.
        intervention_graph: The graph containing supernodes to intervene on.
        interventions: List of Intervention(supernode, scaling_factor).
        replacements: Optional dict mapping target node name -> replacement Supernode.

    Returns:
        dict with:
            - top_outputs: list of (token, probability)
            - node_activations: dict of node_name -> activation_fraction (or None)
            - interventions_applied: list of dicts describing each intervention
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

    if replacements is not None:
        for target, replacement in replacements.items():
            intervention_graph.nodes[target].replacement_node = replacement

    return {
        "top_outputs": top_outputs,
        "node_activations": intervention_graph.get_activation_summary(),
        "interventions_applied": [
            {"supernode": s.name, "scaling_factor": sf}
            for s, sf in interventions
        ],
    }


def print_intervention_results(results: dict):
    """Print intervention results in a readable format."""
    print("\n=== Intervention Results ===")

    print("\nInterventions applied:")
    for iv in results["interventions_applied"]:
        print(f"  {iv['supernode']}: {iv['scaling_factor']}x")

    print_top_outputs(results["top_outputs"], label="Top outputs after intervention")

    print("\nNode activation fractions (relative to baseline):")
    for name, act in results["node_activations"].items():
        if act is None:
            print(f"  {name}: intervened (no activation fraction)")
        else:
            print(f"  {name}: {act:.2%}")


def parse_intervention_spec(spec: str) -> tuple[str, float]:
    """Parse 'supernode_name:scaling_factor' string."""
    name, factor = spec.rsplit(":", 1)
    return name, float(factor)


def prepare_url(url: str, api_key: str | None) -> str:
    """Ensure URL has pinnedIds, enriching from subgraph list API if needed."""
    if url_has_pinned_ids(url):
        return url

    print("  URL missing pinnedIds, fetching from subgraph list API...")
    if not api_key:
        print("Error: URL has no pinnedIds and no --api_key provided.", file=sys.stderr)
        print("Either provide a full URL with pinnedIds and supernodes,", file=sys.stderr)
        print("or provide a URL with a subgraph param and --api_key.", file=sys.stderr)
        sys.exit(1)

    return enrich_url_from_subgraph(url, api_key)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run supernode interventions to test circuit hypotheses."
    )
    parser.add_argument("--source_url", required=True, help="Neuronpedia URL with annotated supernodes")
    parser.add_argument(
        "--intervene", nargs="+", required=True,
        help="Interventions as 'supernode_name:scaling_factor' (e.g., 'Texas:-2')"
    )
    parser.add_argument("--replacement_url", help="Neuronpedia URL for replacement supernodes (cross-prompt swap)")
    parser.add_argument(
        "--activate", nargs="*", default=[],
        help="Replacement supernodes to activate as 'supernode_name:scaling_factor' (e.g., 'California:2')"
    )
    parser.add_argument("--api_key", help="Neuronpedia API key (needed if URL lacks pinnedIds)")
    parser.add_argument("--model_name", default="google/gemma-2-2b")
    parser.add_argument("--transcoder_name", default="gemma")
    parser.add_argument("--backend", default="transformerlens", choices=["transformerlens", "nnsight"])
    parser.add_argument("--top_k", type=int, default=5, help="Number of top outputs to show")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    # Prepare source URL (enrich with pinnedIds if needed)
    print("Preparing source URL...")
    source_url = prepare_url(args.source_url, args.api_key)

    # Fetch prompt from Neuronpedia API
    print("Fetching prompt from Neuronpedia API...")
    source_prompt = get_prompt_from_url(source_url)
    print(f"  Prompt: {source_prompt!r}")

    # Load model
    print(f"Loading model: {args.model_name}")
    model = load_model(args.model_name, args.transcoder_name, args.backend)

    # Build supernodes from source URL
    print("Extracting supernodes from source URL...")
    source_supernodes = build_supernodes_from_url(source_url)
    print(f"  Found supernodes: {list(source_supernodes.keys())}")

    # Get baseline activations
    print("Getting baseline activations...")
    logits, activations = model.get_activations(source_prompt)

    # Create intervention graph
    intervention_graph = InterventionGraph(
        ordered_nodes=[[sn for sn in source_supernodes.values()]],
        prompt=source_prompt,
    )

    # Initialize source supernodes
    for sn in source_supernodes.values():
        intervention_graph.initialize_node(sn, activations)
    intervention_graph.set_node_activation_fractions(activations)

    # Print baseline
    baseline_top = get_top_outputs(logits, model.tokenizer, k=args.top_k)
    print_top_outputs(baseline_top, label="Baseline top outputs")

    # Parse interventions
    intervention_specs = [parse_intervention_spec(s) for s in args.intervene]
    interventions = []
    for name, factor in intervention_specs:
        if name not in source_supernodes:
            parser.error(f"Supernode '{name}' not found in source URL. Available: {list(source_supernodes.keys())}")
        interventions.append(Intervention(source_supernodes[name], factor))

    # Handle replacement supernodes from a different prompt
    replacements = None
    if args.replacement_url and args.activate:
        print("Preparing replacement URL...")
        replacement_url = prepare_url(args.replacement_url, args.api_key)

        print("Fetching replacement prompt from Neuronpedia API...")
        replacement_prompt = get_prompt_from_url(replacement_url)
        print(f"  Replacement prompt: {replacement_prompt!r}")

        print("Extracting replacement supernodes...")
        replacement_supernodes = build_supernodes_from_url(replacement_url)
        print(f"  Found supernodes: {list(replacement_supernodes.keys())}")

        _, replacement_activations = model.get_activations(replacement_prompt)

        for sn in replacement_supernodes.values():
            intervention_graph.initialize_node(sn, replacement_activations)

        activate_specs = [parse_intervention_spec(s) for s in args.activate]
        for name, factor in activate_specs:
            if name not in replacement_supernodes:
                parser.error(f"Supernode '{name}' not found in replacement URL. Available: {list(replacement_supernodes.keys())}")
            interventions.append(Intervention(replacement_supernodes[name], factor))

    # Run intervention
    results = supernode_intervention(model, intervention_graph, interventions, replacements)

    if args.json:
        json_results = {
            "prompt": source_prompt,
            "baseline_top_outputs": [(t, p) for t, p in baseline_top],
            "intervention_top_outputs": results["top_outputs"],
            "node_activations": results["node_activations"],
            "interventions_applied": results["interventions_applied"],
        }
        print(json.dumps(json_results, indent=2, default=str))
    else:
        print_intervention_results(results)
