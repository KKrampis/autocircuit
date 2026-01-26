# %%

import argparse

from graph_analysis.utils import load_graph_data, print_metadata, organize_nodes_by_layer_ctx, analyze_supernodes, print_layer_transition_stats, print_context_flow

# %%

if __name__ == "__main__":
    # Load graph data
    parser = argparse.ArgumentParser(description='Analyze Neuronpedia circuit tracer graph in a JSON file')
    parser.add_argument('--graph_file', help='Path to the graph JSON file', required=True)
    parser.add_argument('--tasks', nargs='+', help='List of analysis tasks to perform', choices=['print_metadata', 'analyze_supernodes', 'layer_transitions', 'context_flow'], required=True)
    args = parser.parse_args()

    data = load_graph_data(args.graph_file)

    if 'print_metadata' in args.tasks:
        print(f"Loaded graph from {args.graph_file} with {len(data['nodes'])} nodes and {len(data['links'])} edges.")
        print_metadata(data['metadata'])

    if 'analyze_supernodes' in args.tasks:
        # Group nodes by layer and context
        layer_ctx_groups = organize_nodes_by_layer_ctx(data['nodes'])

        # Calculate statistics for each group
        analyze_supernodes(layer_ctx_groups)

    if 'layer_transitions' in args.tasks:
        # Analyze information flow by layer transitions        
        print_layer_transition_stats(data['links'])

    if 'context_flow' in args.tasks:
        # Analyze context position flow
        print_context_flow(data['nodes'], data['links'], data['metadata']['prompt_tokens'])

# %%
