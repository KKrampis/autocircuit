---
name: np-graph-analyze
description: Analyze Neuronpedia graph structure including metadata, supernodes (grouped by layer and context position), layer transitions, and context flow. Use when needing to understand graph overview, analyze how features group by layer/position, trace layer-to-layer information flow, or understand token-level context patterns.
---

# Graph Structure Analysis

Analyze graph structure using `circuit_analysis.py`.

## Usage

```bash
python -m graph_analysis.circuit_analysis --graph_file <path> --tasks <task1> <task2> ...
```

## Tasks

### print_metadata
Print graph overview: model, prompt tokens, node count, edge count, pruning settings.

### analyze_supernodes
Group nodes by (layer, ctx_idx) and compute statistics for each group. Shows feature counts and average influence per supernode.

### layer_transitions
Analyze edge flow between layers. Shows which layer pairs have strongest connections.

### context_flow
Analyze information flow between token positions. Shows how information moves across context positions.

## Example

```bash
# Get overview
python -m graph_analysis.circuit_analysis --graph_file .tmp/graphs/model=gemma-2-2b__slug=example.json --tasks print_metadata

# Full analysis
python -m graph_analysis.circuit_analysis --graph_file .tmp/graphs/model=gemma-2-2b__slug=example.json --tasks print_metadata analyze_supernodes layer_transitions context_flow
```

## Limitations

- Supernode grouping by (layer, ctx_idx) is one approach. Other grouping strategies may be needed for different analyses.
- If you need different grouping logic, ask the user for guidance or create new analysis code.
