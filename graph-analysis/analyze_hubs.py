# %%

import json
from collections import defaultdict
import argparse

# %%

# Load graph data
parser = argparse.ArgumentParser(description='Analyze Neuronpdia circuit tracer graph in a JSON file')
parser.add_argument('--graph_file', help='Path to the graph JSON file')
args = parser.parse_args()

with open(args.graph_file, 'r') as f:
    data = json.load(f)
print(f"Loaded graph from {args.graph_file} with {len(data['nodes'])} nodes and {len(data['links'])} edges.")

# %%

# Calculate node degrees
in_degree = defaultdict(int)
out_degree = defaultdict(int)
weighted_in = defaultdict(float)
weighted_out = defaultdict(float)

for link in data['links']:
    source = link['source']
    target = link['target']
    weight = abs(link['weight'])
    
    out_degree[source] += 1
    in_degree[target] += 1
    weighted_out[source] += weight
    weighted_in[target] += weight

# Create node lookup
nodes_dict = {n['node_id']: n for n in data['nodes']}

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

def fmt_influence(v: int | None) -> str:
    return f"{v:.3f}" if v is not None else "N/A"

print("Top 20 Hub Nodes (by total degree):")
print("="*80)
for i, node in enumerate(node_degrees[:20], 1):
    print(f"{i:3d}. NodeId:{node['node_id']:<20} Layer:{node['layer']:<3} Ctx:{node['ctx_idx']:<3} "
          f"In:{node['in_degree']:<4} Out:{node['out_degree']:<4} "
          f"Total:{node['total_degree']:<4} Influence:{fmt_influence(node['influence'])}")

print("a node with feature_type 'mlp reconstruction error' will have 0 in_degree")

print("\n\nTop 20 Nodes by Weighted In-degree:")
print("="*80)
node_degrees.sort(key=lambda x: x['weighted_in'], reverse=True)
for i, node in enumerate(node_degrees[:20], 1):
    print(f"{i:3d}. NodeId:{node['node_id']:<20} Layer:{node['layer']:<3} Ctx:{node['ctx_idx']:<3} "
          f"WeightedIn:{node['weighted_in']:<7.2f} Influence:{fmt_influence(node['influence'])}")

print("\n\nTop 20 Nodes by Weighted Out-degree:")
print("="*80)
node_degrees.sort(key=lambda x: x['weighted_out'], reverse=True)
for i, node in enumerate(node_degrees[:20], 1):
    print(f"{i:3d}. NodeId:{node['node_id']:<20} Layer:{node['layer']:<3} Ctx:{node['ctx_idx']:<3} "
          f"WeightedOut:{node['weighted_out']:<7.2f} Influence:{fmt_influence(node['influence'])}")
    
breakpoint()
