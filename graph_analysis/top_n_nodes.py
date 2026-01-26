import argparse
from .utils import (
    load_graph_data,
    organize_nodes_by_layer_ctx,
    calculate_in_degree,
    print_hypothesis_results,
    top_n_nodes_by_in_degree,
    top_n_nodes_by_influence,
    top_n_source_node_by_weight
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get top-n nodes based on the node's metric from specific layers at specific context position.")
    parser.add_argument('--graph_file', help='Path to the graph JSON file', required=True)
    parser.add_argument('--layer_ctx', nargs='+', help='List of layer and context index pairs in the format layer,ctx_idx (e.g., 4,2 5,3)', required=True)
    parser.add_argument('--top_n', type=int, default=5, help='Number of top nodes to retrieve', required=True)
    parser.add_argument('--metric', choices=['influence', 'in_degree', 'weight'], required=True)
    args = parser.parse_args()
    layer_ctx = []
    for pair in args.layer_ctx:
        layer, ctx_idx = pair.split(',')
        layer_ctx.append((layer, int(ctx_idx)))

    data = load_graph_data(args.graph_file)
    nodes_by_layer_ctx = organize_nodes_by_layer_ctx(data['nodes'])

    match args.metric:
        case 'influence':
            top_nodes = top_n_nodes_by_influence(nodes_by_layer_ctx, layer_ctx, n=args.top_n)
            print_hypothesis_results(top_nodes, metric="influence")
        case 'in_degree':
            in_degree = calculate_in_degree(data['links'])
            top_nodes = top_n_nodes_by_in_degree(nodes_by_layer_ctx, in_degree, layer_ctx, n=args.top_n)
            print_hypothesis_results(top_nodes, metric="influence")
        case 'weight':
            output_node_id = [node['node_id'] for node in data['nodes'] if node['feature_type'] == 'logit'][0]
            top_nodes = top_n_source_node_by_weight(data['nodes'], data['links'], output_node_id, layer_ctx, n=args.top_n)
            print_hypothesis_results(top_nodes, metric="weight")