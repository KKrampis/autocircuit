---
name: np-graph-sample
description: Sample top-N nodes from specific layer+context positions by metric (influence, in_degree, weight). Use when testing hypotheses about which nodes matter at specific positions, or when selecting candidate nodes for a subgraph from targeted locations.
---

# Node Sampling by Position

Sample top nodes from specific positions using `top_n_nodes.py`.

## Usage

```bash
python -m graph_analysis.top_n_nodes --graph_file <path> --layer_ctx <L,C> ... --top_n <N> --metric <metric>
```

## Parameters

- `--layer_ctx`: One or more layer,ctx_idx pairs (e.g., `0,1 1,1 2,1`)
- `--top_n`: Number of top nodes to return
- `--metric`: Ranking metric - `influence`, `in_degree`, or `weight`

## Metrics

- **influence**: Node's influence score (from graph data)
- **in_degree**: Number of incoming edges
- **weight**: Edge weight to output logit node

## Example

```bash
# Get top 5 nodes by influence from early layers at position 1
python -m graph_analysis.top_n_nodes --graph_file .tmp/graphs/model=gemma-2-2b__slug=example.json \
  --layer_ctx 0,1 1,1 2,1 \
  --top_n 5 \
  --metric influence

# Get top 3 nodes by in_degree from late layer at final position
python -m graph_analysis.top_n_nodes --graph_file .tmp/graphs/model=gemma-2-2b__slug=example.json \
  --layer_ctx 23,6 \
  --top_n 3 \
  --metric in_degree
```

## Limitations

- Requires specifying layer+context positions. Cannot search across all positions.
- Cannot filter by feature_type, node labels, or activation patterns.
- If you need sampling by other criteria, ask the user for guidance or create new sampling code.
