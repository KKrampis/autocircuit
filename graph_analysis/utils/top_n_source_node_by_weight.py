def top_n_source_node_by_weight(nodes: list[dict], edges: list[dict],
                                output_node_id: str, layer_ctx: list[tuple[str, int]],
                                n: int = 5) -> list[tuple[dict, float]]:
    """
    Sample features with strongest connections to output logit.

    Expected node's feature_type is 'cross layer transcoder'.
    """
    output_edges = []
    for layer, ctx_pos in layer_ctx:
        for edge in edges:
            if edge['target'] != output_node_id:
                continue
            src = [node for node in nodes if node['node_id'] == edge['source']][0]
            if src['layer'] != layer or src['ctx_idx'] != ctx_pos:
                continue
            output_edges.append((src, abs(edge['weight'])))

    output_edges.sort(key=lambda x: x[1], reverse=True)
    return output_edges[:n]