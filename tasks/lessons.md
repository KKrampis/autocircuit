# Lessons Learned

<!-- Record patterns and corrections here after each session. -->
<!-- Format: ## Date - Context / What went wrong / Rule to prevent it -->

## 2026-02-12 - CLAUDE.md caused over-exploration and double planning

**What went wrong:**
1. "Plan Mode Default" in CLAUDE.md conflicted with system-level plan mode, causing double planning loops
2. "Use subagents liberally" caused agent to explore `/home/tao/jason/circuit-tracer/` (external dependency) instead of staying in autocircuit/
3. No scope boundary meant agent spent excessive time reading files outside the repo

**Rule:**
- Do not add rules to CLAUDE.md that duplicate system-level capabilities (plan mode, subagent launching)
- Always define a scope boundary in CLAUDE.md so agents stay within the repo
- Subagent instructions should describe the workflow (researcher → creates skill), not just "use liberally"

## 2026-02-12 - Refactoring demo/ into graph_analysis/ modules

**What was done:**
- Extracted shared data classes (Feature, Supernode, InterventionGraph) from `demo/graph_visualization.py` into `graph_analysis/utils/intervention_types.py`
- Extracted model loading and top-output helpers into `graph_analysis/utils/model_utils.py`
- Created 4 new CLI modules from 5 demo files:
  - `check_feature.py` (from `demo/check_feature.py`) - feature inspection
  - `run_attribution.py` (from `demo/attribution_demo.py`) - graph generation
  - `run_intervention.py` (from `demo/circuit_tracing_tutorial.py`) - supernode interventions
  - `feature_intervention.py` (from `demo/intervention_demo.py`) - feature-level interventions
- `supernode_intervention` now returns structured dict (top_outputs, node_activations, interventions_applied) instead of only SVG
- `demo/graph_visualization.py` SVG rendering left in demo/ (human-only tool)
- `demo/attribution_demo.py` `serve()` function ignored (manual frontend)

**Key pattern:**
- Demo files mix setup, execution, and visualization in one script
- For agent use: separate into argparse CLIs that return structured data (print or --json)
- Keep SVG/HTML visualization in demo/ for human use only

**Gap identified:**
- `run_intervention.py` requires pre-annotated Neuronpedia URLs (supernodes defined by human)
- No programmatic annotation capability yet (added to todo.md)