from collections import defaultdict

def summarize_nodes(edges: dict, nodes: dict):
    # Calculate node degrees
    in_degree = defaultdict(int)
    out_degree = defaultdict(int)
    weighted_in = defaultdict(float)
    weighted_out = defaultdict(float)

    for edge in edges:
        source = edge['source']
        target = edge['target']
        weight = abs(edge['weight'])
        
        out_degree[source] += 1
        in_degree[target] += 1
        weighted_out[source] += weight
        weighted_in[target] += weight

    # Create node lookup
    nodes_dict = {n['node_id']: n for n in nodes}

    # Find hub nodes (high degree)
    all_nodes = set(list(in_degree.keys()) + list(out_degree.keys()))
    node_degrees = []
    for node_id in all_nodes:
        total_degree = in_degree[node_id] + out_degree[node_id]
        node_info = nodes_dict[node_id]
        node_degrees.append({
            'node_id': node_id,
            'in_degree': in_degree[node_id],
            'out_degree': out_degree[node_id],
            'total_degree': total_degree,
            'weighted_in': weighted_in[node_id],
            'weighted_out': weighted_out[node_id],
            'layer': node_info['layer'],
            'ctx_idx': node_info['ctx_idx'],
            'influence': node_info.get('influence')
            # node_info.get('influence') may be None when node_info['feature_type'] is 'logit'
        })

    # Sort by total degree
    node_degrees.sort(key=lambda x: x['total_degree'], reverse=True)

    return node_degrees