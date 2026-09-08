# Data manifest

The five graph JSON files were regenerated from Neuronpedia using the prompts,
model, and pruning parameters encoded in `rerun_corrected_analysis.py`.

| Graph | Prompt | Nodes | Edges |
|---|---|---:|---:|
| analog_berlin | Paris is to France as Berlin is to | 930 | 25,915 |
| analog_rome | Paris is to France as Rome is to | 963 | 27,608 |
| analog_tokyo | Paris is to France as Tokyo is to | 905 | 22,414 |
| analog_teacher | Doctor is to hospital as teacher is to | 1,040 | 35,481 |
| analog_bird | Fish is to water as bird is to | 1,071 | 38,741 |

## Derived files

- `summary.json`: graph sizes and original-versus-corrected overlap counts.
- `corrected_overlap.json`: feature-level graph membership, occurrences, and
  per-graph summaries.
- `core_5_of_5_annotation_template.csv`: corrected all-five feature set and
  Neuronpedia labels, with empty blinded-annotation fields.
- `numeric_phase_detection.json`: segmented models, smooth controls, selected
  boundaries, and bootstrap output.
- `phase_model_metrics.csv`: compact one- through five-phase comparison.
- `figures/`: presentation-ready plots generated from the JSON outputs.

The raw graphs and derived files contain no API credential.
