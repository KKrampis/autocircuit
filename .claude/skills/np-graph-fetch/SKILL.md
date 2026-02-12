---
name: np-graph-fetch
description: Fetch graph metadata and subgraph data from Neuronpedia API. Use when needing to get the prompt for a graph, list saved subgraphs, or retrieve pinnedIds and supernodes from Neuronpedia. Works with graph URLs or model_id + slug pairs.
---

# Fetch Graph Data from Neuronpedia

## Graph Metadata

Fetch prompt and metadata for a graph.

```bash
# From a URL
python -m graph_analysis.api.graph.graph_get --url "https://www.neuronpedia.org/gemma-2-2b/graph?slug=gemma-fact-dallas-austin"

# From model_id + slug
python -m graph_analysis.api.graph.graph_get --model_id gemma-2-2b --slug gemma-fact-dallas-austin
```

Returns JSON with: `id`, `modelId`, `slug`, `prompt`, `promptTokens`, `url` (S3 link to full graph JSON).

## Subgraph List

Fetch saved subgraphs (with pinnedIds and supernodes) for a graph.

```bash
python -m graph_analysis.api.subgraph.subgraph_list --model_id gemma-2-2b --slug gemma-fact-dallas-austin --api_key $NEURONPEDIA_API_KEY
```

Requires `--api_key`. Returns subgraphs with: `id`, `displayName`, `pinnedIds`, `supernodes`, `clerps`.

## Programmatic Use

```python
from graph_analysis.api.graph import fetch_graph_metadata, parse_neuronpedia_url
from graph_analysis.api.subgraph import fetch_subgraph_list

model_id, slug = parse_neuronpedia_url(url)
metadata = fetch_graph_metadata(model_id, slug)
subgraphs = fetch_subgraph_list(model_id, slug, api_key)
```
