# Project Tasks

## Open Questions

- [ ] Do we automatically or manually identify subgraph patterns across prompts?
  - Theory of change mentions manual confirmation based on graph structure metrics
- [ ] What is the project output focus?
  - Option A: Identify dangerous capabilities (features that always activate for specific tasks)
  - Option B: Understand how models represent goals/values (explain multi-hop computation)
  - Option C: Automated alerts for deviations from baseline patterns
  - Option D: Cross-model comparison for universal safety-relevant patterns

## Phase 1: Graph Collection & Analysis

- [x] Run attribution on prompts to generate graphs (`np-run-attribution` skill)
- [x] Analyze graph structure: supernodes, hubs, layer transitions (`np-graph-analyze`, `np-graph-hubs`)
- [x] Inspect individual features (`np-check-feature` skill)
- [x] Run supernode interventions to test hypotheses (`np-run-intervention` skill)
- [x] Run direct feature interventions (`np-feature-intervention` skill)
- [x] Save subgraphs to Neuronpedia API (`np-graph-save` skill)
- [ ] Automatically collect graphs across prompts using Neuronpedia's API
- [ ] Programmatically upload pruned graphs using Neuronpedia's API
- [ ] Extract subgraphs by filtering noise
  - [ ] Define methods to extract a subgraph (research required)

### Gaps

- [ ] **Automated graph annotation**: `run_intervention.py` requires an already-annotated Neuronpedia URL (with supernodes defined by a human). There is no programmatic way to annotate a new graph (group nodes into supernodes) without the manual frontend (`serve()`). Possible approaches:
  - Use `np-graph-analyze` + `np-graph-hubs` to identify candidate groupings, then `np-graph-save` to save them
  - Build an LLM-based annotation step that reads feature descriptions and proposes supernode groupings
- [ ] **Cross-prompt supernode matching**: No tool to find the "same" supernode across different prompts (e.g., find the "Texas" equivalent in an "Oakland" graph)

## Phase 2: Subgraph Discovery

- [ ] Identify recurring subgraph patterns across prompts
- [ ] Define methods to generate circuit hypotheses (research required)
- [ ] Validate identified subgraphs (research required)

## Phase 3: Validation

- [ ] Validate subgraph patterns using targeted interventions
- [ ] Define validation methods for cross-prompt patterns

## Research Questions

### Feature Annotation
- Features are auto-annotated but descriptions may be too specific, underspecified, or incorrect
- When should an agent re-annotate features?
- Does providing activation values improve LLM-generated descriptions?

### Hypothesis Generation
- Should we generate hypotheses from prompts, or generate prompts from hypotheses?

## Project Output

- [ ] Library of interpretable reasoning circuits with causal evidence
- [ ] Define which reasoning circuits to discover:
  - Dangerous capability identification
  - Goal/value representation
  - Language-specific features
  - Content-related circuits