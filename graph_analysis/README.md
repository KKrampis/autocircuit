# Graph Analysis Tools

Tools for analyzing neural network circuits from Neuronpedia graph data.

## Scripts

| Script | Purpose |
|--------|---------|
| `circuit_analysis.py` | Analyze supernodes, layer transitions, context flow |
| `analyze_hubs.py` | Find hub nodes by degree and weight |
| `top_n_nodes.py` | Sample top-N nodes by metric from specific layers |
| `do_subgraph_save.py` | Save discovered subgraphs to Neuronpedia API |

## Usage

All scripts run as Python modules from the repo root:

```bash
python -m graph_analysis.<script_name> --graph_file <path> [options]
```

For detailed usage and workflow, see the `neuronpedia-graph` skill in `.claude/skills/`.

## Directory Structure

```
graph_analysis/
├── circuit_analysis.py    # Main analysis entry point
├── analyze_hubs.py        # Hub node detection
├── top_n_nodes.py         # Top-N node sampling
├── do_subgraph_save.py    # API subgraph saving
├── utils/                 # Shared utilities
│   ├── load_graph_data.py
│   ├── summarize_nodes.py
│   ├── analyze_supernodes.py
│   └── ...
└── api/                   # API interaction
    └── subgraph/
        ├── subgraph_save_post.py
        └── subgraph_supernodes.py
```

## Dependencies

- Python 3.10+
- `requests` (for API calls)
