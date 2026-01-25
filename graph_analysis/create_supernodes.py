#!/usr/bin/env python3
"""
Generate and save supernode configuration for Neuronpedia API.

This script analyzes a Neuronpedia graph and creates supernodes by grouping
features according to (layer, context_position) pairs, then optionally sends
the configuration to the Neuronpedia API to create a subgraph view.

Usage:
    python create_supernodes.py <graph_data.json> [--send]

Arguments:
    graph_data.json    Path to downloaded Neuronpedia graph JSON
    --send            Optional: Send configuration to API (requires valid key)
"""

import json
import sys
import requests
from collections import defaultdict
from typing import Dict, List, Tuple, Any


def load_graph_data(filepath: str) -> dict:
    """Load graph data from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def calculate_supernode_stats(nodes: List[dict]) -> Tuple[float, float]:
    """Calculate average influence and activation for a group of nodes."""
    influences = [n.get('influence') for n in nodes if n.get('influence') is not None]
    activations = [n.get('activation') for n in nodes if n.get('activation') is not None]

    avg_influence = sum(influences) / len(influences) if influences else 0
    avg_activation = sum(activations) / len(activations) if activations else 0

    return avg_influence, avg_activation


def group_nodes_by_layer_context(graph_data: dict) -> Dict[Tuple[str, int], List[dict]]:
    """
    Group nodes by (layer, context_position) pairs.

    Returns:
        Dictionary mapping (layer, ctx_idx) -> list of nodes
    """
    grouped = defaultdict(list)

    for node in graph_data['nodes']:
        # Only group transcoder features (not embeddings or logits)
        if node.get('feature_type') == 'cross layer transcoder':
            key = (str(node['layer']), node['ctx_idx'])
            grouped[key].append(node)

    return grouped


def create_supernode_definitions(grouped_nodes: Dict[Tuple[str, int], List[dict]],
                                 metadata: dict) -> List[Dict[str, Any]]:
    """
    Create supernode definitions from grouped nodes.

    Returns:
        List of supernode configuration dictionaries
    """
    supernodes = []

    # Token names from prompt
    prompt_tokens = metadata.get('prompt_tokens', [])
    token_names = {i: tok for i, tok in enumerate(prompt_tokens)}

    # Sort by layer then context position
    for (layer, ctx_idx), nodes in sorted(grouped_nodes.items()):
        # Get token name
        token = token_names.get(ctx_idx, f"C{ctx_idx}")
        token = token.strip()  # Clean whitespace

        # Extract node IDs
        node_ids = [n['node_id'] for n in nodes]

        # Calculate statistics
        avg_influence, avg_activation = calculate_supernode_stats(nodes)

        # Determine phase/role based on layer
        layer_num = int(layer) if layer.isdigit() else 0
        if layer_num <= 5:
            phase = "Early Processing"
        elif layer_num <= 15:
            phase = "Middle Routing"
        elif layer_num <= 21:
            phase = "Bottleneck"
        else:
            phase = "Output Module"

        # Create supernode definition
        supernode = {
            "id": f"L{layer}_C{ctx_idx}",
            "label": f"L{layer}_C{ctx_idx}: {token} ({len(node_ids)} feat)",
            "description": (
                f"Layer {layer}, Context {ctx_idx} ({token}) | "
                f"{phase} | "
                f"AvgInf: {avg_influence:.3f}, AvgAct: {avg_activation:.2f}"
            ),
            "nodeIds": node_ids
        }

        supernodes.append(supernode)

    return supernodes


def identify_key_nodes(graph_data: dict) -> Dict[str, List[str]]:
    """
    Identify key nodes to pin in the visualization.

    Returns:
        Dictionary with 'pinned' list of node IDs
    """
    nodes = graph_data['nodes']

    # Calculate in-degree
    in_degree = defaultdict(int)
    for link in graph_data['links']:
        in_degree[link['target']] += 1

    pinned_ids = []

    # 1. Highest in-degree hub (integration point)
    hub_nodes = [(n['node_id'], in_degree[n['node_id']])
                 for n in nodes if n.get('feature_type') == 'cross layer transcoder']
    if hub_nodes:
        top_hub = max(hub_nodes, key=lambda x: x[1])
        pinned_ids.append(top_hub[0])

    # 2. Highest influence in early layer (important feature)
    early_nodes = [n for n in nodes
                   if n.get('feature_type') == 'cross layer transcoder'
                   and n.get('layer') in ['0', '1', '2']
                   and n.get('influence') is not None]
    if early_nodes:
        top_influence = max(early_nodes, key=lambda n: n['influence'])
        pinned_ids.append(top_influence['node_id'])

    # 3. Output logit (target)
    output_nodes = [n for n in nodes if n.get('feature_type') == 'logit']
    if output_nodes:
        pinned_ids.append(output_nodes[0]['node_id'])

    return {"pinned": pinned_ids}


def create_subgraph_payload(graph_data: dict, metadata: dict) -> dict:
    """
    Create complete payload for /api/graph/subgraph/save endpoint.

    Returns:
        Dictionary ready to send as JSON to API
    """
    # Extract model and slug from metadata
    model_id = metadata.get('scan', 'unknown')
    slug = metadata.get('slug', 'unknown')

    # Group nodes and create supernodes
    grouped = group_nodes_by_layer_context(graph_data)
    supernodes = create_supernode_definitions(grouped, metadata)

    # Identify key nodes
    key_nodes = identify_key_nodes(graph_data)

    # Get thresholds from metadata
    pruning_settings = metadata.get('pruning_settings', {})

    # Build payload
    payload = {
        "modelId": model_id,
        "slug": slug,
        "supernodes": supernodes,
        "pinnedIds": key_nodes['pinned'],
        "pruningThreshold": pruning_settings.get('node_threshold', 0.8),
        "densityThreshold": pruning_settings.get('edge_threshold', 0.85)
    }

    return payload


def send_to_api(payload: dict, api_key: str) -> dict:
    """
    Send supernode configuration to Neuronpedia API.

    Returns:
        API response as dictionary
    """
    url = "https://www.neuronpedia.org/api/graph/subgraph/save"

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    return response.json()


def print_summary(payload: dict, grouped_nodes: Dict):
    """Print summary of supernode configuration."""
    print("\n" + "="*80)
    print("SUPERNODE CONFIGURATION SUMMARY")
    print("="*80)

    print(f"\nModel: {payload['modelId']}")
    print(f"Graph Slug: {payload['slug']}")
    print(f"Total Supernodes: {len(payload['supernodes'])}")
    print(f"Pinned Nodes: {len(payload['pinnedIds'])}")
    print(f"Pruning Threshold: {payload['pruningThreshold']}")
    print(f"Density Threshold: {payload['densityThreshold']}")

    # Count nodes by phase
    phases = defaultdict(int)
    for sn in payload['supernodes']:
        layer = int(sn['id'].split('_')[0][1:])
        if layer <= 5:
            phases['Early (L0-L5)'] += 1
        elif layer <= 15:
            phases['Middle (L6-L15)'] += 1
        elif layer <= 21:
            phases['Bottleneck (L16-L21)'] += 1
        else:
            phases['Output (L22+)'] += 1

    print("\nSupernodes by Phase:")
    for phase, count in sorted(phases.items()):
        print(f"  {phase}: {count} supernodes")

    # Show largest supernodes
    print("\nLargest Supernodes (Top 10):")
    sorted_sn = sorted(payload['supernodes'],
                       key=lambda s: len(s['nodeIds']),
                       reverse=True)
    for i, sn in enumerate(sorted_sn[:10], 1):
        print(f"  {i}. {sn['label']}")

    print("\nPinned Nodes:")
    for node_id in payload['pinnedIds']:
        print(f"  - {node_id}")

    print("\n" + "="*80)


def main():
    """Main execution function."""
    if len(sys.argv) < 2:
        print("Usage: python create_supernodes.py <graph_data.json> [--send] [--api-key KEY]")
        print("\nOptions:")
        print("  --send              Send configuration to Neuronpedia API")
        print("  --api-key KEY       API key for authentication (required if --send)")
        sys.exit(1)

    graph_path = sys.argv[1]
    send_flag = '--send' in sys.argv

    # Get API key if sending
    api_key = None
    if send_flag:
        if '--api-key' in sys.argv:
            idx = sys.argv.index('--api-key')
            if idx + 1 < len(sys.argv):
                api_key = sys.argv[idx + 1]

        if not api_key:
            print("Error: --api-key required when using --send")
            sys.exit(1)

    print(f"Loading graph data from: {graph_path}")
    graph_data = load_graph_data(graph_path)

    metadata = graph_data.get('metadata', {})
    print(f"Prompt: {metadata.get('prompt', 'unknown')}")

    # Group nodes
    grouped = group_nodes_by_layer_context(graph_data)
    print(f"Found {len(grouped)} unique (layer, context) groups")

    # Create configuration
    payload = create_subgraph_payload(graph_data, metadata)

    # Save to file
    output_file = 'supernode_config.json'
    with open(output_file, 'w') as f:
        json.dump(payload, f, indent=2)

    print(f"\nConfiguration saved to: {output_file}")

    # Print summary
    print_summary(payload, grouped)

    # Send to API if requested
    if send_flag:
        print("\nSending to Neuronpedia API...")
        try:
            response = send_to_api(payload, api_key)
            print("\n✓ Success!")
            print(f"Subgraph ID: {response.get('subgraphId', 'unknown')}")
            if 'url' in response:
                print(f"View at: {response['url']}")
        except Exception as e:
            print(f"\n✗ Error: {e}")
            sys.exit(1)
    else:
        print("\nTo send to API, run with: --send --api-key YOUR_KEY")


if __name__ == "__main__":
    main()
