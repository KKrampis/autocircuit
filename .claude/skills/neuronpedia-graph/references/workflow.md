# Detailed Workflow Reference

## Table of Contents

1. [Graph JSON Schema Details](#graph-json-schema-details)
2. [Analysis Workflow Patterns](#analysis-workflow-patterns)
3. [Subgraph Save API Contract](#subgraph-save-api-contract)
4. [Example Analysis Session](#example-analysis-session)

---

## Graph JSON Schema Details

### Node Object

```json
{
  "node_id": "0_928_1",
  "layer": "17",
  "ctx_idx": 5,
  "influence": 0.0234,
  "feature_type": "logit",
  "jsNodeId": "0_928-0",
  "activation": 3.45,
  "clerp": ""
}
```

| Field | Type | Description |
|-------|------|-------------|
| `node_id` | string | Unique identifier (format: `{layer}_{feature_id}_{ctx_idx}`) |
| `layer` | string | Transformer layer (0-25 for gemma-2-2b) |
| `ctx_idx` | int | Token context position (0-based index into prompt_tokens) |
| `influence` | float/null | Node influence score (null for logit nodes) |
| `feature_type` | string | "embedding", "cross layer transcoder", "logit", or "mlp reconstruction error" |
| `activation` | float/null | Feature activation strength |

### Link Object

```json
{
  "source": "E_23807_1",
  "target": "0_928_1",
  "weight": 0.156
}
```

### Metadata Object

```json
{
  "model_id": "gemma-2-2b",
  "slug": "dna-stands-for-clt",
  "scan": "gemma-2-2b",
  "prompt": "<bos>DNA stands for deoxyribonucleic",
  "prompt_tokens": ["<bos>", "DNA", " stands", " for", " deoxy", "ri", "bonucleic"],
  "pruning_settings": {
    "node_threshold": 0.01,
    "edge_threshold": 0.001
  }
}
```

---

## Analysis Workflow Patterns

### Pattern 1: Understanding Graph Structure

```bash
# Step 1: Get overview
python -m graph_analysis.circuit_analysis --graph_file <path> --tasks print_metadata

# Step 2: Analyze layer-by-layer structure
python -m graph_analysis.circuit_analysis --graph_file <path> --tasks analyze_supernodes layer_transitions

# Step 3: Understand token-level flow
python -m graph_analysis.circuit_analysis --graph_file <path> --tasks context_flow
```

### Pattern 2: Finding Important Nodes

```bash
# Hub nodes (high connectivity)
python -m graph_analysis.analyze_hubs --graph_file <path> --tasks total_degree weighted_in weighted_out

# Targeted search by layer/position
python -m graph_analysis.top_n_nodes --graph_file <path> \
  --layer_ctx 0,1 1,1 2,1 \
  --top_n 5 \
  --metric influence
```

### Pattern 3: Hypothesis-Driven Analysis

For "DNA stands for deoxyribonucleic" example:

```bash
# Domain features (early layers, position 1 = "DNA")
python -m graph_analysis.top_n_nodes --graph_file <path> --layer_ctx 0,1 1,1 2,1 --top_n 5 --metric influence

# Structural features (positions 2-3 = "stands for")
python -m graph_analysis.top_n_nodes --graph_file <path> --layer_ctx 1,2 2,2 2,3 3,3 --top_n 3 --metric influence

# Morphological features (position 4 = "deoxy")
python -m graph_analysis.top_n_nodes --graph_file <path> --layer_ctx 6,4 7,4 8,4 --top_n 5 --metric influence

# Integration hubs (late layers)
python -m graph_analysis.top_n_nodes --graph_file <path> --layer_ctx 23,6 --top_n 5 --metric in_degree

# Output boosters
python -m graph_analysis.top_n_nodes --graph_file <path> --layer_ctx 25,6 --top_n 5 --metric weight
```

---

## Subgraph Save API Contract

### Endpoint

`POST https://www.neuronpedia.org/api/graph/subgraph/save`

### Headers

```
x-api-key: <your-api-key>
Content-Type: application/json
```

### Request Body

```json
{
  "modelId": "gemma-2-2b",
  "slug": "dna-stands-for-clt",
  "displayName": "DNA Circuit Analysis",
  "pinnedIds": ["node_id_1", "node_id_2", "node_id_3"],
  "supernodes": [
    ["Label for Group A", "node_id_1", "node_id_2"],
    ["Label for Group B", "node_id_3", "node_id_4"]
  ],
  "clerps": [],
  "pruningThreshold": 0.01,
  "densityThreshold": 0.001
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `modelId` | Yes | Model identifier from metadata.scan |
| `slug` | Yes | Graph slug from metadata.slug |
| `displayName` | No | Human-readable name for subgraph |
| `pinnedIds` | Yes | All node IDs to include (union of all supernode members + extras) |
| `supernodes` | Yes | Array of [label, ...node_ids] arrays |
| `clerps` | Yes | Empty array (custom labels, not used) |
| `pruningThreshold` | Yes | From metadata.pruning_settings.node_threshold |
| `densityThreshold` | Yes | From metadata.pruning_settings.edge_threshold |

### Response

```json
{
  "success": true,
  "subgraphId": "abc123xyz"
}
```

---

## Example Analysis Session

### Task: Discover computational circuit for "DNA stands for deoxyribonucleic"

```bash
# 1. Load and understand
python -m graph_analysis.circuit_analysis \
  --graph_file .tmp/graphs/model=gemma-2-2b__slug=dna-stands-for-clt.json \
  --tasks print_metadata

# Output shows: 257 nodes, 1456 edges, 7 tokens

# 2. Find structural patterns
python -m graph_analysis.circuit_analysis \
  --graph_file .tmp/graphs/model=gemma-2-2b__slug=dna-stands-for-clt.json \
  --tasks analyze_supernodes layer_transitions

# 3. Identify hub nodes
python -m graph_analysis.analyze_hubs \
  --graph_file .tmp/graphs/model=gemma-2-2b__slug=dna-stands-for-clt.json \
  --tasks total_degree weighted_in

# 4. Sample hypothesis-specific nodes
# (See Pattern 3 above)

# 5. Save discovered subgraph
python -m graph_analysis.do_subgraph_save \
  --graph_file .tmp/graphs/model=gemma-2-2b__slug=dna-stands-for-clt.json \
  --api_key $NEURONPEDIA_API_KEY \
  --subgraph_name "DNA Acronym Circuit" \
  -s "Domain Detection" node1 node2 node3 \
  -s "Structure Recognition" node4 node5 \
  -s "Output Boosting" node6 node7 \
  --extra_pinned_ids hub_node_1 hub_node_2
```

---

## Code Location Reference

All Python tools are in `graph_analysis/`:

| File | Purpose |
|------|---------|
| `circuit_analysis.py` | Main analysis entry point |
| `analyze_hubs.py` | Hub node detection |
| `top_n_nodes.py` | Top-N node sampling by metric |
| `do_subgraph_save.py` | Save subgraph to API |
| `utils/` | Shared utilities |
| `api/subgraph/` | API interaction code |