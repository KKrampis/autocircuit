---
name: np-run-intervention
description: Run supernode interventions to test circuit hypotheses. Use when testing whether ablating or replacing supernodes changes model output as expected. Supports ablation (scaling down), activation (scaling up), and cross-prompt replacement (swapping supernodes between prompts). Requires an annotated Neuronpedia graph URL and GPU.
---

# Supernode Intervention

Test circuit hypotheses using `run_intervention.py`. The prompt is fetched automatically from the Neuronpedia API.

## Usage

```bash
python -m graph_analysis.run_intervention \
    --source_url <url> --intervene <name:factor> [--json]
```

## Parameters

- `--source_url`: Neuronpedia URL with annotated supernodes (required). Must contain `pinnedIds` and `supernodes` query params, or use `--api_key` to fetch them.
- `--intervene`: Interventions as `supernode_name:scaling_factor` (required, repeatable)
- `--replacement_url`: Neuronpedia URL for replacement supernodes (cross-prompt swap)
- `--activate`: Replacement supernodes to activate as `name:factor` (repeatable)
- `--api_key`: Neuronpedia API key. Required if `--source_url` lacks `pinnedIds` (fetches from subgraph list API).
- `--json`: Output structured JSON results
- `--top_k`: Number of top outputs (default: 5)

## Intervention Types

- **Ablation**: `--intervene "Texas:-2"` sets Texas features to -2x default
- **Amplification**: `--intervene "Texas:2"` doubles Texas features
- **Cross-prompt swap**: Combine `--intervene "Texas:-2"` with `--activate "California:2"` using a replacement URL

## URL Handling

- If the URL contains `pinnedIds` and `supernodes` query params, supernodes are extracted directly.
- If `pinnedIds` is missing, the URL must contain a `subgraph` query param. The script fetches saved subgraphs from the Neuronpedia API (requires `--api_key`) and matches by subgraph ID to get the correct pinnedIds/supernodes.
- If the URL has neither `pinnedIds` nor `subgraph`, the script exits with an error.

## Output

Human-readable or `--json`:
- `top_outputs`: top-k token predictions after intervention
- `node_activations`: activation fraction for each supernode relative to baseline
- `interventions_applied`: what was intervened and how

## Examples

```bash
# Ablate the Texas supernode (URL with pinnedIds)
python -m graph_analysis.run_intervention \
    --source_url "https://www.neuronpedia.org/gemma-2-2b/graph?slug=gemma-fact-dallas-austin&pinnedIds=27_22605_10%2C20_15589_10%2C...&supernodes=%5B%5B%22Texas%22%2C...%5D%5D" \
    --intervene "Texas:-2"

# Same but fetch pinnedIds from subgraph list API (requires subgraph param)
python -m graph_analysis.run_intervention \
    --source_url "https://www.neuronpedia.org/gemma-2-2b/graph?slug=gemma-fact-dallas-austin&subgraph=abc123" \
    --api_key $NEURONPEDIA_API_KEY \
    --intervene "Texas:-2"

# Cross-prompt: swap Texas -> California
python -m graph_analysis.run_intervention \
    --source_url "https://www.neuronpedia.org/gemma-2-2b/graph?slug=gemma-fact-dallas-austin&pinnedIds=...&supernodes=..." \
    --intervene "Texas:-2" \
    --replacement_url "https://www.neuronpedia.org/gemma-2-2b/graph?slug=gemma-fact-oakland-sacramento&pinnedIds=...&supernodes=..." \
    --activate "California:2" \
    --json
```
