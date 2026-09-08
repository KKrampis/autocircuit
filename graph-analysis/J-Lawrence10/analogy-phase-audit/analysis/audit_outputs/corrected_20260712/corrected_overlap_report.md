# Corrected Analogical Feature-Overlap Rerun

All five graphs were regenerated with the published model, prompt, and pruning settings. Their node and edge counts exactly match the published graph summaries.

## Corrected counts

| Threshold | Original occurrence-based result | Correct distinct-graph result | False inclusions |
|---|---:|---:|---:|
| At least 3/5 | 510 | 490 | 20 |
| At least 4/5 | 277 | 210 | 67 |
| All 5/5 | 180 | 119 | 61 |

The claimed 180-feature all-five core falls to **119 features**, a reduction of **33.9%**.

Among the 61 false core inclusions, 3 appeared in only two graphs, 42 in three graphs, and 16 in four graphs.

## What survives the correction

The five named comparison-related features used in the manuscript—L5/5793, L5/2141, L8/13766, L9/13344, and L13/10969—are genuinely present in all five graphs. Their cross-prompt membership survives the correction, although that fact alone does not establish the proposed phase boundaries or causal hierarchy.

## Next phase-analysis requirement

Neuronpedia labels were retrieved for all corrected 5/5 features in `core_5_of_5_annotation_template.csv`. The semantic category and annotator columns must be completed under a blinded, preregistered annotation protocol before those labels can be used for confirmatory change-point analysis.
