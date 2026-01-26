#!/usr/bin/env python3
import json
import sys
import argparse

from .utils import load_graph_data
from .api import create_subgraph_save_body, do_subgraph_save_post, print_subgraph_summary


if __name__ == "__main__":
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Create supernode configuration from Neuronpedia graph data.")
    parser.add_argument("--graph_file", required=True, help="Path to the graph JSON file")
    parser.add_argument("--subgraph_name", help="Name for the subgraph")
    parser.add_argument("-s", "--supernodes", type=str, nargs="+", action="append", required=True,
                        help="Define one supernode per -s. First item is the supernode LABEL, followed by node IDs (space-separated). "
                             "Can be repeated to add multiple supernodes. Example: -s LabelA node1 node2 -s LabelB node3")
    parser.add_argument("--extra_pinned_ids", nargs="+", 
                        help="List of node IDs to pin that DO NOT belong to any supernode (space-separated). "
                             "These are additional standalone pinned nodes. Example: --extra_pinned_ids nodeX nodeY")
    parser.add_argument("--output_file", help="Output file for supernode configuration")
    parser.add_argument("--api_key", required=True, help="API key for authentication")
    args = parser.parse_args()

    # Get API key if sending
    if args.send and args.api_key is None:
        print("Error: --api-key required when using --send")
        sys.exit(1)

    print(f"Loading graph data from: {args.graph_file}")
    graph_data = load_graph_data(args.graph_file)

    metadata = graph_data['metadata']
    pruning_settings = metadata['pruning_settings']
    print(f"Prompt: {metadata['prompt']}")

    pinnedIds = []
    for sn in args.supernodes:
        pinnedIds.extend(sn[1:])  # Exclude label at sn[0]
    if args.extra_pinned_ids is not None:
        pinnedIds.extend(args.extra_pinned_ids)

    breakpoint()

    # Create configuration
    payload = create_subgraph_save_body(metadata['scan'], metadata['slug'], args.subgraph_name, pruning_settings['node_threshold'], pruning_settings['edge_threshold'], pinnedIds, args.supernodes)

    # Print summary
    print_subgraph_summary(payload)

    # Save to file
    if args.output_file is not None:
        with open(args.output_file, 'w') as f:
            json.dump(payload, f, indent=2)

        print(f"\nConfiguration saved to: {args.output_file}")

    # Send to API
    print("\nSending to Neuronpedia API...")
    try:
        response = do_subgraph_save_post(payload, args.api_key)
        if response['success']:
            print("\nSuccess!")
            print(f"Subgraph ID: {response['subgraphId']}")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
