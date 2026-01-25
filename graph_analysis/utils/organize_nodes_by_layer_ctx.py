from collections import defaultdict

def organize_nodes_by_layer_ctx(nodes: list[dict]) -> dict[tuple[str, int], list[dict]]:
    """
    Organize nodes by (layer, context_position) pairs.
    Node with feature_type 'embedding', 'mlp reconstruction error', or 'logit' are excluded.

    To Do: if we ignore some node types here, what about other functions e.g. calculate_in_degree? doesn't that function count inputs from all node types?
    """
    organized = defaultdict(list)
    for node in nodes:
        if node['feature_type'] == 'cross layer transcoder':
            key = (str(node['layer']), node['ctx_idx'])
            organized[key].append(node)
    return organized