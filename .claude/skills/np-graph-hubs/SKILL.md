---
name: np-graph-hubs
description: Find important hub nodes in Neuronpedia graphs by degree and weight metrics. Use when needing to identify high-connectivity nodes, find integration points in the circuit, or discover nodes with high incoming/outgoing influence.
---

# Hub Node Analysis

Find important nodes using `analyze_hubs.py`.

## Usage

```bash
python -m graph_analysis.analyze_hubs --graph_file <path> --tasks <task1> ...
```

## Tasks

### total_degree
Find nodes with highest total degree (in_degree + out_degree). These are highly connected nodes.

### weighted_in
Find nodes with highest weighted in-degree (sum of absolute incoming edge weights). These receive the most influence.

### weighted_out
Find nodes with highest weighted out-degree (sum of absolute outgoing edge weights). These exert the most influence.

## Example

```bash
# Find all hub types
python -m graph_analysis.analyze_hubs --graph_file .tmp/graphs/model=gemma-2-2b__slug=example.json --tasks total_degree weighted_in weighted_out
```

## Output

Shows top 20 nodes for each metric with: node_id, layer, ctx_idx, degree/weight values, and influence score.

## Limitations

- Only finds hubs by connectivity metrics. Does not consider node labels, feature descriptions, or activation patterns.
- If you need to find important nodes by other criteria (e.g., by feature semantics), ask the user for guidance.
