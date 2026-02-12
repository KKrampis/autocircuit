"""Run attribution on a prompt to produce a graph JSON file for analysis.

Usage:
    python -m graph_analysis.run_attribution --prompt "The capital of state containing Dallas is" --slug dallas-austin

    python -m graph_analysis.run_attribution \
        --prompt "The capital of state containing Dallas is" \
        --slug dallas-austin \
        --node_threshold 0.8 \
        --edge_threshold 0.98 \
        --output_dir .tmp/graph_files
"""

import argparse
import os
from pathlib import Path

from circuit_tracer import attribute
from circuit_tracer.utils import create_graph_files

from graph_analysis.utils import load_model


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run attribution on a prompt and produce graph JSON files.")
    parser.add_argument("--prompt", required=True, help="Input prompt to attribute")
    parser.add_argument("--slug", required=True, help="Name/identifier for the graph")
    parser.add_argument("--model_name", default="google/gemma-2-2b", help="HuggingFace model name")
    parser.add_argument("--transcoder_name", default="gemma", help="Transcoder config name")
    parser.add_argument("--backend", default="transformerlens", choices=["transformerlens", "nnsight"])
    parser.add_argument("--output_dir", default=".tmp/graph_files", help="Directory for output graph JSON files")
    parser.add_argument("--graph_pt_dir", default=".tmp/graphs", help="Directory for intermediate .pt graph file")
    parser.add_argument("--node_threshold", type=float, default=0.8, help="Node pruning threshold (0-1)")
    parser.add_argument("--edge_threshold", type=float, default=0.98, help="Edge pruning threshold (0-1)")
    parser.add_argument("--max_n_logits", type=int, default=10, help="Max logits to attribute from")
    parser.add_argument("--desired_logit_prob", type=float, default=0.95, help="Cumulative probability threshold for logits")
    parser.add_argument("--batch_size", type=int, default=256, help="Attribution batch size")
    parser.add_argument("--max_feature_nodes", type=int, default=8192, help="Max feature nodes (None=no limit)")
    parser.add_argument("--offload", default="cpu", choices=["cpu", "disk"], help="Offload strategy for memory")
    args = parser.parse_args()

    repo_dir = Path(__file__).resolve().parents[1]
    output_dir = repo_dir / args.output_dir
    graph_pt_dir = repo_dir / args.graph_pt_dir

    # Load model
    print(f"Loading model: {args.model_name}")
    model = load_model(args.model_name, args.transcoder_name, args.backend)

    # Run attribution
    print(f"Running attribution on: {args.prompt!r}")
    graph = attribute(
        prompt=args.prompt,
        model=model,
        max_n_logits=args.max_n_logits,
        desired_logit_prob=args.desired_logit_prob,
        batch_size=args.batch_size,
        max_feature_nodes=args.max_feature_nodes,
        offload=args.offload,
        verbose=True,
    )

    # Save .pt file
    os.makedirs(graph_pt_dir, exist_ok=True)
    graph_pt_path = graph_pt_dir / f"{args.slug}.pt"
    graph.to_pt(graph_pt_path)
    print(f"Saved graph .pt: {graph_pt_path}")

    # Create graph JSON files
    create_graph_files(
        graph_or_path=graph_pt_path,
        slug=args.slug,
        output_path=output_dir,
        node_threshold=args.node_threshold,
        edge_threshold=args.edge_threshold,
    )

    graph_json_path = output_dir / f"{args.slug}.json"
    print(f"Saved graph JSON: {graph_json_path}")
    print("\nGraph ready for analysis with:")
    print(f"  python -m graph_analysis.circuit_analysis --graph_file {graph_json_path} --tasks print_metadata analyze_supernodes")
