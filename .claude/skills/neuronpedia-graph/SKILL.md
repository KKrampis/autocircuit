---
name: neuronpedia-graph
description: Analyze Neuronpedia attribution graphs to discover subgraphs and computational circuits. Use when working with Graph JSON files from Neuronpedia's circuit tracer, analyzing neural network circuits, finding hub nodes, tracing information flow, creating supernodes, or saving subgraphs to Neuronpedia API. Triggers on tasks involving graph analysis, circuit discovery, node importance, layer transitions, or subgraph extraction from .json graph files.
---

# Neuronpedia Graph Analysis

This is the entry point for graph analysis. Use the focused skills below based on your task.

## Available Skills

| Skill | Use When |
|-------|----------|
| `np-graph-schema` | Understanding graph JSON structure |
| `np-graph-analyze` | Analyzing supernodes, layer transitions, context flow |
| `np-graph-hubs` | Finding important nodes by degree/weight |
| `np-graph-sample` | Sampling top-N nodes from specific positions |
| `np-graph-save` | Saving subgraphs to Neuronpedia API |

## Typical Workflow

1. Use `np-graph-analyze` with `print_metadata` to understand the graph
2. Use `np-graph-analyze` with `analyze_supernodes`, `layer_transitions` to see structure
3. Use `np-graph-hubs` to find important nodes
4. Use `np-graph-sample` to get candidates from specific positions
5. Decide which nodes to group into supernodes
6. Use `np-graph-save` to upload to Neuronpedia

## When Skills Are Insufficient

If you need functionality not covered by these skills (e.g., different grouping logic, filtering by feature labels, etc.), stop and ask the user for guidance rather than guessing.
