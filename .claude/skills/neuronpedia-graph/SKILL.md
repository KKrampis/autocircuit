---
name: neuronpedia-graph
description: Analyze Neuronpedia attribution graphs to discover subgraphs and computational circuits. Use when working with Graph JSON files from Neuronpedia's circuit tracer, analyzing neural network circuits, finding hub nodes, tracing information flow, creating supernodes, or saving subgraphs to Neuronpedia API. Triggers on tasks involving graph analysis, circuit discovery, node importance, layer transitions, or subgraph extraction from .json graph files.
---

# Neuronpedia Graph Analysis

This is the entry point for graph analysis. Use the focused skills below based on your task.

## Available Skills

### Graph Analysis (no GPU required)

| Skill | Use When |
|-------|----------|
| `np-graph-schema` | Understanding graph JSON structure |
| `np-graph-analyze` | Analyzing supernodes, layer transitions, context flow |
| `np-graph-hubs` | Finding important nodes by degree/weight |
| `np-graph-sample` | Sampling top-N nodes from specific positions |
| `np-check-feature` | Inspecting what a specific feature does (activation range, top logits, examples) |
| `np-graph-fetch` | Fetching graph metadata (prompt, slug) and saved subgraphs from Neuronpedia API |

### Graph Generation & Intervention (GPU required)

| Skill | Use When |
|-------|----------|
| `np-run-attribution` | Generating a new attribution graph from a prompt |
| `np-run-intervention` | Testing hypotheses by ablating/replacing supernodes |
| `np-feature-intervention` | Direct feature-level interventions (zero, scale, swap) |

### Saving Results

| Skill | Use When |
|-------|----------|
| `np-graph-save` | Saving subgraphs to Neuronpedia API |

## Typical Workflow

1. **Generate graph**: Use `np-run-attribution` to create a graph from a prompt
2. **Analyze structure**: Use `np-graph-analyze` with `print_metadata`, `analyze_supernodes`, `layer_transitions`
3. **Find important nodes**: Use `np-graph-hubs` and `np-graph-sample`
4. **Inspect features**: Use `np-check-feature` to understand what specific features do
5. **Test hypotheses**: Use `np-run-intervention` (supernode-level) or `np-feature-intervention` (feature-level)
6. **Save results**: Use `np-graph-save` to upload validated subgraphs to Neuronpedia

## When Skills Are Insufficient

If you need functionality not covered by these skills (e.g., different grouping logic, filtering by feature labels, automated annotation), stop and ask the user for guidance rather than guessing.
