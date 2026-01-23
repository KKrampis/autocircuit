# %%

import json
from collections import defaultdict, Counter
import statistics
import argparse

# %%

# Load graph data
parser = argparse.ArgumentParser(description='Analyze Neuronpedia circuit tracer graph in a JSON file')
parser.add_argument('graph_file', help='Path to the graph JSON file')
args = parser.parse_args()

with open(args.graph_file, 'r') as f:
    data = json.load(f)
print(f"Loaded graph from {args.graph_file} with {len(data['nodes'])} nodes and {len(data['links'])} edges.")

metadata = data['metadata']
print(f"Model: {metadata['scan']}")
print(f"Prompt Tokens: {metadata['prompt_tokens']}")
print(f"Prompt: {metadata['prompt']}")

print(f"Max number of logits nodes to attribute from: {metadata['generation_settings']['max_n_logits']}")
print(f"Cumulative probability threshold for top logits: {metadata['generation_settings']['desired_logit_prob']}")
print(f"Batch size for backward passes: {metadata['generation_settings']['batch_size']}")
print(f"Maximum number of feature nodes: {metadata['generation_settings']['max_feature_nodes']}")

print(f"Keeps minimum nodes with cumulative influence >= threshold: {metadata['pruning_settings']['node_threshold']}")
print(f"Keeps minimum edges with cumulative influence >= threshold: {metadata['pruning_settings']['edge_threshold']}")
print(f"The set of transcoders to use for attribution: {metadata['info']['transcoder_set']}")

# %%

ft_counts = Counter([n['feature_type'] for n in data['nodes']])
print(f"Feature Types Counts: {ft_counts.items()}")

# Group nodes by layer and context
layer_ctx_groups = defaultdict(list)
for node in data['nodes']:
    if node['feature_type'] not in ['embedding', 'logit']: 
        """
        To Do: why exclude 'embedding' and 'logit' nodes? why not exclude 'mlp reconstruction error' nodes?

        Findings:
        - 'embedding' nodes does not have 'activation' field.
        - 'logit' nodes do not have 'influence' or 'activation' fields.
        """
        key = (node['layer'], node['ctx_idx'])
        layer_ctx_groups[key].append(node)

# %%

# Calculate statistics for each group
print("\n1. GROUPING FEATURES INTO SUPERNODES")
print("=" * 100)
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
        print(f"\n--- Layer {current_layer} ---")
    
    print(f"  Supernode L{int(sn['layer']):02d}_C{sn['ctx_idx']:02d}: "
          f"{sn['count']:3d} nodes, "
          f"AvgInf={sn['avg_influence']:.3f}, "
          f"MaxInf={sn['max_influence']:.3f}, "
          f"AvgAct={sn['avg_activation']:.3f}")

# %%

# Analyze information flow by layer transitions
print("\n\n2. MAIN INFORMATION FLOWS (Input → Output)")
print("=" * 100)

s_counts = Counter([e['source'] for e in data['links']])
t_counts = Counter([e['target'] for e in data['links']])
print(f"Format: layer_featureIndex_contextIndex")
print(f"Top 5 Source Nodes: {s_counts.most_common(5)}")
print(f"Top 5 Target Nodes: {t_counts.most_common(5)}")

# Track connections between layer groups
layer_transitions = defaultdict(lambda: {'count': 0, 'total_weight': 0, 'max_weight': 0})

for link in data['links']:
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
      "TotalWeight = sum of weights of all edges between the layer pair\n")
print("\nTop 30 Layer-to-Layer Information Flows (by total edge weight):\n")
for (src, tgt), stats in sorted_transitions:
    avg_weight = stats['total_weight'] / stats['count']
    print(f"  Layer {src:>2} → Layer {tgt:>2}: "
          f"{stats['count']:4d} edges, "
          f"TotalWeight={stats['total_weight']:8.1f}, "
          f"AvgWeight={avg_weight:6.2f}, "
          f"MaxWeight={stats['max_weight']:7.2f}")

# Analyze context position flow
print("\n\n3. CONTEXT POSITION FLOW (Token-level processing)")
print("=" * 100)

ctx_flow = defaultdict(lambda: {'count': 0, 'total_weight': 0})
nodes_dict = {n['node_id']: n for n in data['nodes']}

for link in data['links']:
    source_node = nodes_dict[link['source']]
    target_node = nodes_dict[link['target']]
    
    src_ctx = source_node['ctx_idx']
    tgt_ctx = target_node['ctx_idx']
    key = (src_ctx, tgt_ctx)
    ctx_flow[key]['count'] += 1
    ctx_flow[key]['total_weight'] += abs(link['weight'])

print("\nToken-to-Token Flow (by edge count):\n")
for (src, tgt), stats in sorted(ctx_flow.items(), key=lambda x: x[1]['count'], reverse=True)[:20]:
    tokens = data['metadata']['prompt_tokens']
    src_token = tokens[src] if src < len(tokens) else f"ctx{src}"
    tgt_token = tokens[tgt] if tgt < len(tokens) else f"ctx{tgt}"
    print(f"  C{src} ({src_token:>12}) → C{tgt} ({tgt_token:>12}): "
          f"{stats['count']:5d} edges, TotalWeight={stats['total_weight']:8.1f}")
