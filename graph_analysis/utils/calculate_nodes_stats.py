def calculate_nodes_stats(nodes: list[dict]) -> tuple[float, float]:
    """
    Calculate average influence and activation for a group of nodes.

    a node with feature_type 'logit' have no 'influence' or 'activation' field.
    a node with feature_type 'mlp reconstruction error' have no 'activation' field.
    a node with feature_type 'embedding' have no 'activation' field.
    """
    influences = [n['influence'] for n in nodes if n['influence'] is not None]
    activations = [n['activation'] for n in nodes if n['activation'] is not None]

    avg_influence = sum(influences) / len(influences)
    avg_activation = sum(activations) / len(activations)

    return avg_influence, avg_activation