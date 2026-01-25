

def print_hypothesis_results(nodes: list, metric: str):
    """
    Print formatted hypothesis results.
    Expected node's feature_type is 'cross layer transcoder'.
    """
    print(f"Metric: {metric}\n")
    if isinstance(nodes[0], tuple):
        # Handle (node, metric) tuples
        for i, (node, metric) in enumerate(nodes, 1):
            inf = node['influence']
            layer = node['layer']
            featureId = extract_per_layer_feature_id(node)
            print(f"{i}. Feature {featureId:>10} | "
                  f"Layer: {layer:<2} | Metric: {metric:.3f} | "
                  f"Inf: {inf:.3f} | Act: {fmt_activation(node['activation'])}")
    else:
        # Handle plain nodes
        for i, node in enumerate(nodes, 1):
            inf = node['influence']
            layer = node['layer']
            featureId = extract_per_layer_feature_id(node)
            print(f"{i}. Feature {featureId:>10} | "
                  f"Layer: {layer:<2} | Inf: {inf:.3f} | Act: {fmt_activation(node['activation'])}")

def extract_per_layer_feature_id(node: dict) -> int:
    """
    Extract per-layer feature ID from node ID.

    Note: only node with feature_type 'embedding', 'cross layer transcoder', and 'logit'. node with feature_type 'mlp reconstruction error' have different node_id format.

    Expected node_id format: "<layer>_<feature_id>_<ctx_idx>"
    """
    if node['feature_type'] == 'mlp reconstruction error':
        return -1
    return int(node['node_id'].split('_')[1])

def fmt_activation(v: int | None) -> str:
    """
    N/A when node's feature_type is 'mlp reconstruction error'.
    """
    return f"{v:.2f}" if v is not None else "N/A"