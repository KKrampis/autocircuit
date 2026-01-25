def top_n_nodes_by_influence(nodes_by_layer_ctx: dict, layer_ctx: list[tuple[str, int]], 
                             n: int = 5) -> list[dict]:
    """
    Get top-n nodes based on the node's influence from specific layers at specific context position.
    
    The expected node's feature_type is 'cross layer transcoder'.
    """
    nodes = []
    for layer, ctx_pos in layer_ctx:
        nodes.extend(nodes_by_layer_ctx[(layer, ctx_pos)])

    nodes = [node for node in nodes]
    nodes.sort(key=lambda x: x['influence'], reverse=True)
    return nodes[:n]