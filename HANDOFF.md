# Session Handoff — AutoCircuit Paper

## What This Project Is

An LLM agent explores pre-computed Neuronpedia attribution graphs (from Anthropic's circuit tracing) to discover circuits in Gemma 2 2B. The agent uses graph query tools (not model access) to find hubs, cascades, gating mechanisms, etc. through hypothesis-driven search. We're writing a detailed writeup for NeurIPS 2026.

## Project Location

`/Users/anish/Desktop/aisc_project/`

## Key Files

- `PAPER_DRAFT.md` — Current writeup. Has detailed analysis for DNA→acid + summaries for the other 9. **Needs expansion** (see below).
- `EXPERIMENT_PLAN.md` — Original plan for 5 experiments.
- `.env` — Neuronpedia API key (NEURONPEDIA_API_KEY)
- `initial_testrun/circuit_analysis_tools.py` — Agent toolkit (18 tools, 9 implemented: get_node_info, get_neighbors, find_paths, get_subgraph, get_top_nodes, search_nodes, note, get_notes, get_progress)

## What's Done

### All 10 Circuit Analyses (Experiment 4)
Each has a detailed `*_analysis.md` in `experiments/exp4_scale/circuits/`:
- `factual_geography_analysis.md` — Japan→Tokyo (hourglass, dual-stream)
- `factual_chemistry_analysis.md` — H2→O (hourglass cascade)
- `IOI_analysis.md` — Mary/John IOI (multi-position routing, 54% cross-position)
- `greater_than_analysis.md` — 1517→18+ (deep cascade + inhibition)
- `analogy_analysis.md` — Berlin→Germany (dual-entity convergence)
- `antonym_analysis.md` — hot→cold (hub-and-spoke)
- `factual_causal_analysis.md` — Newton→gravity (multi-cue convergence)
- `factual_science_analysis.md` — Jupiter (single bottleneck)
- Plus the original two: `initial_testrun/circuit_writeup.md` (DNA→acid), `/Users/anish/graphexample/` (Seattle→Washington)

### Baselines (all 8 new circuits)
- `experiments/exp4_scale/baseline_results.json` — Agent beats all baselines on every circuit
- `experiments/exp3_baselines/raw_results.json` — Original DNA→acid baselines

### Feature Lookups (all 8 new circuits)
- `experiments/exp4_scale/feature_lookup_results.json` — 79/92 features labeled, ~82% confirmation
- `experiments/exp1_feature_lookup/raw_results.json` — Original DNA→acid lookups

### Steering / Causal Validation
- `experiments/exp2_steering/full_results.json` — **DETAILED** DNA→acid steering (individual suppression with logprobs, strength sweep, sufficiency, specificity)
- `experiments/exp4_scale/steering_results.json` — Steering on 3 new circuits (geography, analogy, antonym) but **ONLY SUMMARY LEVEL**, not as detailed as exp2

## What's Done (Session 2 — 2026-04-03)

### Paper Expansion — DONE
`PAPER_DRAFT.md` expanded from 333 → 1,195 lines. All 10 circuits now have detailed sections with backbone tables, ASCII diagrams, feature validation, baselines, and steering results with logprobs.

### Steering on All 10 Circuits — DONE
All 8 new circuits have steering results in `steering_results.json` (zero errors remaining).
- `run_steering.py` has all 8 circuit configs with backbone features
- Key findings already written into each circuit's section in the paper

### Number Verification — DONE
Checked coverage/coherence against `baseline_results.json`. Fixed backbone sizes in overview table (were stale from original handoff; now match JSON: e.g. antonym=29 not 4, IOI=46 not 19).

## What's Done (Session 3 — 2026-04-03)

### Experiment 5: Reproducibility — DONE
- 3 independent runs on DNA→acid graph with different exploration strategies (top-down, embedding-forward, degree-centrality)
- Results in `experiments/exp5_reproducibility/` (run1/, run2/, run3/, results.json, compute_jaccard.py)
- **Average Jaccard = 0.766** (all pairwise > 0.7 target)
- 12-node core backbone found by all 3 runs; all structural features (hub, cascade, gate, amplifier, inhibitory) agree 3/3
- 3 peripheral nodes varied by strategy
- Written up as new "Experiment 5: Reproducibility" section in PAPER_DRAFT.md before Limitations
- Updated Limitations: "Reproducibility untested" → "Cross-LLM reproducibility untested"

### Final Polish — DONE
- **Steering logprobs**: Spot-checked 4 circuits (geography, chemistry, IOI, greater-than) — all values match JSON after rounding
- **Baseline tables fixed**: All 8 per-circuit baseline tables had stale node counts from original backbone sizes. Updated to match `baseline_results.json` (e.g. geography 14→32, chemistry 21→38, IOI 19→46, etc.). Max-weight path node counts also corrected.
- **Aggregate baseline table fixed**: Top-k in-degree mean coverage was 0.195 (stale), corrected to 0.243. Random coherence 0.130→0.155. Max-weight coverage 0.227→0.224.
- **Overview stats**: SD for mean coverage corrected from 0.07 to 0.08
- **Cross-circuit comparison**: Verified all claims match corrected backbone sizes

## What Might Still Be Worth Doing

- Cross-LLM reproducibility (run agent with GPT-4 backbone)
- Sensitivity to graph thresholds (regenerate graph at different pruning levels)
- More detailed sufficiency/specificity steering tests on newer circuits

## API Details

- Neuronpedia API base: https://www.neuronpedia.org/api
- Key endpoints: /feature/{modelId}/{layer}/{index}, /steer, /graph/generate
- Layer format for transcoders: "{layer}-gemmascope-transcoder-16k"
- Steering: strength_multiplier field (use 4), features array with modelId/layer/index/strength
- Feature lookup: GET /api/feature/gemma-2-2b/{layer}-gemmascope-transcoder-16k/{feature_index}

## The Agent Toolkit

`initial_testrun/circuit_analysis_tools.py` — 18 tools, 9 implemented:
- Graph queries: get_node_info, get_neighbors, find_paths, get_subgraph, get_top_nodes, search_nodes
- State: note, get_notes, get_progress
- Stubbed (not used): patch_node, patch_edge, ablate_nodes, run_model, test_circuit_faithfulness, get_attention_pattern, logit_lens, get_max_activating_examples, get_node_activation

Usage: `python circuit_analysis_tools.py --graph <path.json> <tool_name> [--args]`
