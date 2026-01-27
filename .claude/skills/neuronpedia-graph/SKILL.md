---
name: neuronpedia-graph
description: Analyze Neuronpedia attribution graphs to discover subgraphs and computational circuits. Use when working with Graph JSON files from Neuronpedia's circuit tracer, analyzing neural network circuits, finding hub nodes, tracing information flow, creating supernodes, or saving subgraphs to Neuronpedia API. Triggers on tasks involving graph analysis, circuit discovery, node importance, layer transitions, or subgraph extraction from .json graph files.
---

# Neuronpedia Graph Analysis

Analyze attribution graphs from Neuronpedia to discover computational circuits in LLMs.

## Graph JSON Schema

Graph files contain three main keys:

| Key | Type | Description |
|-----|------|-------------|
| `nodes` | array | Features with `node_id`, `layer`, `ctx_idx`, `influence`, `feature_type` |
| `links` | array | Edges with `source`, `target`, `weight` |
| `metadata` | object | Model info, prompt tokens, pruning settings |

**Node fields**: `node_id`, `layer` (int), `ctx_idx` (int), `influence` (float, null for logits), `feature_type` ("latent"/"logit"/"mlp reconstruction error")

**Link fields**: `source` (node_id), `target` (node_id), `weight` (float)

## Available Tools

All tools are in `graph_analysis/` and run as Python modules from repo root.

### 1. Circuit Analysis

Analyze graph structure, supernodes, layer transitions, and context flow.

```bash
python -m graph_analysis.circuit_analysis --graph_file <path> --tasks <task1> <task2> ...
```

**Tasks**: `print_metadata`, `analyze_supernodes`, `layer_transitions`, `context_flow`

### 2. Hub Analysis

Find important nodes by degree and weight.

```bash
python -m graph_analysis.analyze_hubs --graph_file <path> --tasks <task1> ...
```

**Tasks**: `total_degree`, `weighted_in`, `weighted_out`

### 3. Top-N Nodes

Get top nodes from specific layer+context positions by metric.

```bash
python -m graph_analysis.top_n_nodes --graph_file <path> --layer_ctx <L,C> ... --top_n <N> --metric <metric>
```

**Metrics**: `influence`, `in_degree`, `weight`

Example: `--layer_ctx 0,1 1,1 2,1 --top_n 5 --metric influence`

### 4. Save Subgraph

Save discovered subgraph to Neuronpedia API.

```bash
python -m graph_analysis.do_subgraph_save --graph_file <path> --api_key <key> \
  -s <Label1> <node1> <node2> \
  -s <Label2> <node3> <node4> \
  --extra_pinned_ids <nodeX> <nodeY> \
  --subgraph_name <name>
```

## Workflow: Subgraph Discovery

1. **Understand the graph**: Run `print_metadata` to see prompt, model, and size
2. **Analyze structure**: Run `analyze_supernodes` and `layer_transitions`
3. **Find hubs**: Run hub analysis to identify important nodes
4. **Sample candidates**: Use `top_n_nodes` for specific layer/context positions
5. **Group into supernodes**: Decide which nodes to group and label
6. **Save to API**: Use `do_subgraph_save` with supernodes and pinned IDs

## Reference

For detailed API contracts and advanced patterns, see [references/workflow.md](references/workflow.md).
