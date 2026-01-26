import statistics

def analyze_supernodes(layer_ctx_groups: dict):
    print("\Supernode (grouped by Layer-Token Index):\n")

    supernode_summary = []
    for (layer, ctx_idx), nodes in sorted(layer_ctx_groups.items()):
        influences = [n['influence'] for n in nodes if n.get('influence') is not None]
        activations = [n['activation'] for n in nodes if n.get('activation') is not None]
        
        if influences and activations:
            """
            To Do:
            - why not summarize a supernode when either influences or activations is empty?
            - what does average influence, maximum influence and average activation tells us?
            """
            avg_influence = statistics.mean(influences)
            avg_activation = statistics.mean(activations)
            max_influence = max(influences)
            
            supernode_summary.append({
                'layer': layer,
                'ctx_idx': ctx_idx,
                'count': len(nodes),
                'avg_influence': avg_influence,
                'max_influence': max_influence,
                'avg_activation': avg_activation
            })

    print("Influence = how much that node contributed to logits\n"
          "AvgInf = Average Influence of nodes in the supernode\n"
          "MaxInf = Maximum Influence of nodes in the supernode\n"
          "AvgAct = Average Activation of nodes in the supernode")

    # Print supernodes by layer
    current_layer = None
    for sn in sorted(supernode_summary, key=lambda x: (int(x['layer']), x['ctx_idx'])):
        if sn['layer'] != current_layer:
            current_layer = sn['layer']
            print(f"\nLayer {current_layer}")
        
        print(f"Supernode L{int(sn['layer']):02d}_C{sn['ctx_idx']:02d}: "
            f"{sn['count']:3d} nodes, "
            f"AvgInf={sn['avg_influence']:.3f}, "
            f"MaxInf={sn['max_influence']:.3f}, "
            f"AvgAct={sn['avg_activation']:.3f}")