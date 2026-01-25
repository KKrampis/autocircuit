def top_n_nodes_by_in_degree(nodes_by_layer_ctx: dict, in_degree: dict,
                             layer_ctx: list[tuple[str, int]], n: int = 5) -> list[tuple[dict, int]]:
    """
    Sample hub nodes with highest in-degree.
    Expected node's feature_type is not 'logit'.
    """
    nodes_with_in_degree = []
    for layer, ctx_pos in layer_ctx:
        nodes = nodes_by_layer_ctx[(layer, ctx_pos)]
        for node in nodes:
            if node['feature_type'] == 'logit': # node with feature_type 'logit' do not have influence
                continue
            degree = in_degree[node['node_id']]
            nodes_with_in_degree.append((node, degree))

    nodes_with_in_degree.sort(key=lambda x: x[1], reverse=True)
    return nodes_with_in_degree[:n]