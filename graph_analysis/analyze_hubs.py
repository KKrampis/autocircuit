# %%

import argparse

from graph_analysis.utils import load_graph_data, summarize_nodes

# %%

def fmt_influence(v: int | None) -> str:
    return f"{v:.3f}" if v is not None else "N/A"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze Neuronpdia circuit tracer graph in a JSON file')
    parser.add_argument('--graph_file', help='Path to the graph JSON file', required=True)
    parser.add_argument('--tasks', nargs='+', help='List of analysis tasks to perform', choices=['total_degree', 'weighted_in', 'weighted_out'], required=True)
    args = parser.parse_args()

    # Load graph data
    data = load_graph_data(args.graph_file)

    node_degrees = summarize_nodes(data['links'], data['nodes'])

    print("Note: Influence N/A when node's feature_type is 'logit'")

    if 'total_degree' in args.tasks:
        print("Top 20 Hub Nodes (by total degree):")
        print("="*80)
        for i, node in enumerate(node_degrees[:20], 1):
            print(f"{i:2d}. NodeId:{node['node_id']:<15} Layer:{node['layer']:<3} Ctx:{node['ctx_idx']:<3} "
                f"In:{node['in_degree']:<4} Out:{node['out_degree']:<4} "
                f"Total:{node['total_degree']:<4} Influence:{fmt_influence(node['influence'])}")

    if 'weighted_in' in args.tasks:
        print("Note: a node with feature_type 'mlp reconstruction error' will have 0 in_degree")

        print("\n\nTop 20 Nodes by Weighted In-degree:")
        print("="*80)
        node_degrees.sort(key=lambda x: x['weighted_in'], reverse=True)
        for i, node in enumerate(node_degrees[:20], 1):
            print(f"{i:2d}. NodeId:{node['node_id']:<20} Layer:{node['layer']:<3} Ctx:{node['ctx_idx']:<3} "
                f"WeightedIn:{node['weighted_in']:<7.2f} Influence:{fmt_influence(node['influence'])}")

    if 'weighted_out' in args.tasks:
        print("\n\nTop 20 Nodes by Weighted Out-degree:")
        print("="*80)
        node_degrees.sort(key=lambda x: x['weighted_out'], reverse=True)
        for i, node in enumerate(node_degrees[:20], 1):
            print(f"{i:3d}. NodeId:{node['node_id']:<20} Layer:{node['layer']:<3} Ctx:{node['ctx_idx']:<3} "
                f"WeightedOut:{node['weighted_out']:<7.2f} Influence:{fmt_influence(node['influence'])}")
