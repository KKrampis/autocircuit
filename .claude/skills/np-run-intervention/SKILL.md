---
name: np-run-intervention
description: Run supernode interventions to test circuit hypotheses. Use when testing whether ablating or replacing supernodes changes model output as expected. Supports ablation (scaling down), activation (scaling up), and cross-prompt replacement (swapping supernodes between prompts). Driven by YAML experiment configs. Requires GPU.
---

# Supernode Intervention (YAML-Driven)

Test circuit hypotheses using YAML experiment configs and `run_intervention.py`.

## Usage

```bash
python -m graph_analysis.run_intervention \
    --config <yaml_path> [--experiment <name>] [--save_graph] [--graph_dir <dir>] [--json]
```

## Parameters

- `--config`: Path to YAML experiment config file (required)
- `--experiment`: Specific experiment(s) to run (repeatable). If omitted, runs all experiments in the config.
- `--save_graph`: Save SVG graph visualizations to files
- `--graph_dir`: Directory for SVG output files (default: `.tmp/run_intervention`)
- `--api_key`: Neuronpedia API key (needed if graph URLs lack pinnedIds)
- `--json`: Output structured JSON results

## YAML Config Structure

```yaml
model:
  name: google/gemma-2-2b
  transcoder: gemma
  backend: transformerlens

graphs:                              # Neuronpedia graph URLs (keyed by name)
  dallas_austin: "https://www.neuronpedia.org/gemma-2-2b/graph?slug=...&pinnedIds=...&supernodes=..."

prompts:                             # Prompts keyed by name
  dallas: "Fact: the capital of the state containing Dallas is"

supernodes:                          # Supernode definitions
  say_austin:
    features:                        # Manual features list
      - {layer: 23, pos: 10, feature_idx: 12237}
  texas:
    features_from:                   # Extract from graph URL
      graph: dallas_austin
      groups: ["Texas"]              # Can merge multiple groups
    children: [say_austin]           # Circuit DAG children
  emb_dallas:
    features: null                   # Embedding node (no features)
    children: [texas]
  synonym:
    features_from:
      graph: fr_synonym
      groups: ["synonymy"]
    pos_offset: -1                   # Shift feature positions after init

graph_layout:                        # Default visualization layout (rows of node keys)
  - [capital, state, emb_dallas]
  - [say_capital, texas]
  - [say_austin]

experiments:
  ablate_texas:
    description: "Disabling Texas disables Say Austin"
    prompt: dallas                   # Prompt key
    initialize:                      # prompt_key -> [node_keys]
      dallas: [capital, state, texas, say_austin]
    interventions:
      - actions:
          - {node: texas, scale: -2}

  swap_texas_california:
    prompt: dallas
    initialize:
      dallas: [capital, state, texas, say_austin]
      oakland: [california, say_sacramento]
    interventions:
      - actions:
          - {node: texas, scale: -2}
          - {node: california, scale: 2}
        replacements:                # Visual node swaps
          texas: california
          say_austin: say_sacramento
```

## Supernode Feature Sources

Three ways to define features:
1. **Manual**: `features: [{layer, pos, feature_idx}, ...]`
2. **From graph URL**: `features_from: {graph: <key>, groups: [<names>]}` — merges multiple groups by concatenation
3. **Embedding**: `features: null` — structural nodes with no features

## Intervention Types

- **Ablation**: `{node: texas, scale: -2}` sets features to -2x default
- **Amplification**: `{node: texas, scale: 2}` doubles features
- **Cross-prompt swap**: Ablate one node + activate another from a different prompt, with visual `replacements`

## Output

Always prints text summary regardless of SVG:
- Interventions applied (node name + scaling factor)
- Top outputs after intervention (token + probability)
- Node activations relative to baseline (percentage, with visual indicators)
- Replacements applied (visual node swaps)

With `--save_graph`: saves SVG files to `--graph_dir`.
With `--json`: outputs structured JSON with all results.

## Experiment YAML Files

Pre-built experiments in `experiments/run_intervention/`:
- `capital_cities.yaml` — ablation experiments on Dallas/Austin capital circuit
- `capital_cities_cross_prompt.yaml` — cross-prompt swaps (Oakland, Shanghai, Vancouver)
- `multilingual_small_big.yaml` — French/Chinese language switching
- `multilingual_antonym_synonym.yaml` — big/small and synonym replacement

## Examples

```bash
# Run all capital city experiments
python -m graph_analysis.run_intervention --config experiments/run_intervention/capital_cities.yaml

# Run one specific experiment
python -m graph_analysis.run_intervention --config experiments/run_intervention/capital_cities.yaml --experiment ablate_texas

# Save SVG visualizations
python -m graph_analysis.run_intervention --config experiments/run_intervention/capital_cities.yaml --save_graph --graph_dir output/graphs/

# Cross-prompt experiments with JSON output
python -m graph_analysis.run_intervention --config experiments/run_intervention/capital_cities_cross_prompt.yaml --json
```