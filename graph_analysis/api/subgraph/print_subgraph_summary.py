def print_subgraph_summary(payload: dict):
    """Print summary of subgraph configuration."""
    print("\n" + "="*80)
    print("SUBGRAPH CONFIGURATION SUMMARY")
    print("="*80)

    print(f"\nModel: {payload['modelId']}")
    print(f"Graph Slug: {payload['slug']}")
    print(f"Total Supernodes: {len(payload['supernodes'])}")
    print(f"Pinned Nodes: {len(payload['pinnedIds'])}")
    print(f"Pruning Threshold: {payload['pruningThreshold']}")
    print(f"Density Threshold: {payload['densityThreshold']}")

    # Show largest supernodes
    print("\nLargest Supernodes by Node Count (Top 10):")
    sorted_sn = sorted(payload['supernodes'],
                       key=lambda s: len(s),
                       reverse=True)
    print("No | Supernode Label")
    for i, sn in enumerate(sorted_sn[:10], 1):
        print(f"  {i:02d}. {sn[0]}")