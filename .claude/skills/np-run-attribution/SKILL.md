---
name: np-run-attribution
description: Run circuit attribution on a prompt to produce graph JSON files for analysis. Use when needing to generate a new attribution graph from a prompt, create graph files for visualization, or prepare a graph for analysis with other np-graph skills. Requires GPU.
---

# Run Attribution

Generate attribution graphs using `run_attribution.py`.

## Usage

```bash
python -m graph_analysis.run_attribution --prompt <text> --slug <name>
```

## Parameters

- `--prompt`: Input prompt to attribute (required)
- `--slug`: Name/identifier for the graph (required)
- `--model_name`: HuggingFace model (default: `google/gemma-2-2b`)
- `--transcoder_name`: Transcoder config (default: `gemma`)
- `--backend`: `transformerlens` or `nnsight` (default: `transformerlens`)
- `--output_dir`: Directory for graph JSON (default: `.tmp/graph_files`)
- `--node_threshold`: Node pruning threshold 0-1 (default: 0.8)
- `--edge_threshold`: Edge pruning threshold 0-1 (default: 0.98)
- `--max_n_logits`: Max logits to attribute from (default: 10)
- `--batch_size`: Attribution batch size (default: 256)
- `--max_feature_nodes`: Max feature nodes (default: 8192)
- `--offload`: Memory strategy `cpu` or `disk` (default: `cpu`)

## Output

- `.pt` graph file in `--graph_pt_dir`
- Pruned JSON graph file in `--output_dir` ready for analysis

## Example

```bash
python -m graph_analysis.run_attribution \
    --prompt "The capital of state containing Dallas is" \
    --slug dallas-austin
```

Then analyze with:
```bash
python -m graph_analysis.circuit_analysis --graph_file .tmp/graph_files/dallas-austin.json --tasks print_metadata analyze_supernodes
```
