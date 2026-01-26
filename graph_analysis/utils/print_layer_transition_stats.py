from collections import Counter, defaultdict

def print_layer_transition_stats(edges: dict):
    print("\n\nMAIN INFORMATION FLOWS (Input → Output)")

    s_counts = Counter([e['source'] for e in edges])
    t_counts = Counter([e['target'] for e in edges])
    print(f"Format: layer_featureIndex_contextIndex")
    print(f"Top 5 Source Nodes: {s_counts.most_common(5)}")
    print(f"Top 5 Target Nodes: {t_counts.most_common(5)}")

    # Track connections between layer groups
    layer_transitions = defaultdict(lambda: {'count': 0, 'total_weight': 0, 'max_weight': 0})

    for link in edges:
        source = link['source']
        target = link['target']
        weight = abs(link['weight'])
        
        # Get layer info
        src_layer = source.split('_')[0]
        tgt_layer = target.split('_')[0]
        
        key = (src_layer, tgt_layer)
        layer_transitions[key]['count'] += 1 # count of edges
        layer_transitions[key]['total_weight'] += weight
        layer_transitions[key]['max_weight'] = max(layer_transitions[key]['max_weight'], weight)

    # Sort by total weight
    sorted_transitions = sorted(layer_transitions.items(), 
                                key=lambda x: x[1]['total_weight'], 
                                reverse=True)[:30]

    print("Weight = how much the source node contributes (absolute value) to the target node in the tracer's attribution\n" \
          "TotalWeight = sum of weights of all edges between the layer pair")
    print("\nTop 30 Layer-to-Layer Information Flows (by total edge weight):\n")
    for i, ((src, tgt), stats) in enumerate(sorted_transitions, 1):
        avg_weight = stats['total_weight'] / stats['count']
        print(f"{i:02d}. Layer {src:>2} → Layer {tgt:>2}: "
            f"{stats['count']:4d} edges, "
            f"TotalWeight={stats['total_weight']:8.1f}, "
            f"AvgWeight={avg_weight:6.2f}, "
            f"MaxWeight={stats['max_weight']:7.2f}")