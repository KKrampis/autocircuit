from graph_analysis.utils import calculate_nodes_stats

def subgraph_supernodes_by_layer_ctx(grouped_nodes: dict[tuple[str, int], list[dict]],
                                     prompt_tokens: list[str]) -> list[list[str]]:
    """
    Create supernode definitions from grouped nodes.

    Expected grouped_nodes keys are (layer: str, context_position: int).

    Returns:
        List of list of node_ids for each supernode

    A supernode is a list of node IDs where the first element is the label
    """
    supernodes = []

    # Sort by layer then context position
    for (layer, ctx_idx), nodes in sorted(grouped_nodes.items()):
        # Get token name
        token = prompt_tokens[ctx_idx]
        token = token.strip()  # Clean whitespace

        # Extract node IDs
        node_ids = [n['node_id'] for n in nodes]

        # Calculate statistics
        avg_influence, avg_activation = calculate_nodes_stats(nodes)

        label = f"L{layer}_C{ctx_idx}: {token} | {len(node_ids)} nodes | AvgInf: {avg_influence:.3f}, AvgAct: {avg_activation:.2f}"

        supernodes.append([label] + node_ids)

    return supernodes