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

- [ ] Automatically collect graphs across prompts using Neuronpedia's API
- [ ] Programmatically upload pruned graphs using Neuronpedia's API
- [ ] Extract subgraphs by filtering noise
  - [ ] Define methods to extract a subgraph (research required)

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