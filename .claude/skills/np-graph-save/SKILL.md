---
name: np-graph-save
description: Save discovered subgraphs to Neuronpedia API with supernodes and pinned nodes. Use when ready to save analysis results, create named subgraphs, or upload circuit discoveries to Neuronpedia.
---

# Save Subgraph to Neuronpedia

Save discovered subgraphs using `do_subgraph_save.py`.

## Usage

```bash
python -m graph_analysis.do_subgraph_save --graph_file <path> --api_key <key> \
  -s <Label1> <node1> <node2> \
  -s <Label2> <node3> <node4> \
  --extra_pinned_ids <nodeX> <nodeY> \
  --subgraph_name <name>
```

## Parameters

- `--graph_file`: Path to graph JSON file
- `--api_key`: Neuronpedia API key (required)
- `-s` / `--supernodes`: Define supernodes. First arg is label, rest are node IDs. Repeat for multiple supernodes.
- `--extra_pinned_ids`: Additional node IDs to pin that aren't in any supernode
- `--subgraph_name`: Display name for the subgraph

## Example

```bash
python -m graph_analysis.do_subgraph_save \
  --graph_file .tmp/graphs/model=gemma-2-2b__slug=dna-stands-for-clt.json \
  --api_key $NEURONPEDIA_API_KEY \
  --subgraph_name "DNA Circuit" \
  -s "Domain Detection" 0_928_1 1_234_1 \
  -s "Output Boosting" 25_567_6 25_890_6 \
  --extra_pinned_ids 17_456_4
```

## Limitations

- Requires valid API key from Neuronpedia
- Node IDs must exist in the graph
- If API call fails, check the error message and verify node IDs are correct
