---
name: np-graph-schema
description: Understand Neuronpedia Graph JSON file structure. Use when needing to understand the schema of graph JSON files from Neuronpedia's circuit tracer, including node fields, link fields, metadata structure, and possible values for each field.
---

# Graph JSON Schema

Graph files from Neuronpedia contain three main keys: `nodes`, `links`, `metadata`.

## Node Object

| Field | Type | Description |
|-------|------|-------------|
| `node_id` | string | Unique identifier |
| `layer` | string | Transformer layer (e.g., "0", "17", "E" for embedding) |
| `ctx_idx` | int | Token context position (0-based index into prompt_tokens) |
| `influence` | float/null | Node influence score (null for logit nodes) |
| `feature_type` | string | See possible values below |
| `activation` | float/null | Feature activation strength |

**feature_type values**: `"embedding"`, `"cross layer transcoder"`, `"logit"`, `"mlp reconstruction error"`

**node_id format**:
- embedding, cross layer transcoder, logit: `{layer}_{featureId}_{ctxIdx}`
- mlp reconstruction error: `0_{layer}_{ctxIdx}`

## Link Object

| Field | Type | Description |
|-------|------|-------------|
| `source` | string | Source node_id |
| `target` | string | Target node_id |
| `weight` | float | Edge weight (can be negative) |

## Metadata Object

| Field | Type | Description |
|-------|------|-------------|
| `model_id` | string | Model identifier |
| `slug` | string | Graph slug for API |
| `scan` | string | Model scan identifier |
| `prompt` | string | Input prompt |
| `prompt_tokens` | array | Tokenized prompt |
| `pruning_settings` | object | Contains `node_threshold`, `edge_threshold` |

## Limitations

This schema is based on gemma-2-2b graphs. Other models may have different field values or additional fields. If you encounter unexpected structure, verify by loading the JSON and inspecting it.
