# Analogy Feature-Overlap and Phase Audit

This folder is an isolated, reproducible audit package. It does not replace or
move any files in the original analysis directories.

## Main findings

- All five attribution graphs were regenerated with the published prompts,
  model, and pruning parameters. Their node and edge counts match the published
  graph summaries.
- Recurrence is counted by **distinct graph membership**, so repeated
  token-position activations within one graph do not count as independent
  cross-prompt appearances.
- The corrected all-five feature core contains 119 features rather than 180, a
  reduction of 33.9%.
- The five named manuscript features remain present in all five graphs.
- Among one- through five-segment models, BIC selects three segments beginning
  at L7 and L15: L0-6, L7-14, and L15-25.
- These are objective numeric regimes. Their functional labels remain
  provisional pending blinded semantic annotation and causal validation.

## Folder layout

```text
METHODS.md
analysis/
  DATA_MANIFEST.md
  rerun_corrected_analysis.py
  detect_numeric_phase_boundaries.py
  plot_corrected_audit_figures.py
  tests/
  audit_outputs/corrected_20260712/
    graphs/                         # five raw regenerated graphs
    figures/                        # meeting-ready figures
    summary.json
    corrected_overlap.json
    numeric_phase_detection.json
    phase_model_metrics.csv
    core_5_of_5_annotation_template.csv
presentation/
  analogy_phase_audit_meeting.pptx
  meeting_script.md
requirements.txt
requirements-lock.txt
```

## Reproduce from the included graphs

From this folder:

```powershell
python -m pip install -r requirements.txt
python analysis/rerun_corrected_analysis.py
python analysis/detect_numeric_phase_boundaries.py
python analysis/plot_corrected_audit_figures.py
python -m pytest analysis/tests
```

The first command reuses the included graph JSON files and does not require an
API key.

The package was verified with Python 3.13.3. Use `requirements-lock.txt` when
an exact recreation of the tested environment is preferred.

## Regenerate graphs from Neuronpedia

Set the key in the environment and request fresh graphs:

```powershell
$env:NEURONPEDIA_API_KEY = "<your key>"
python analysis/rerun_corrected_analysis.py --regenerate --fetch-labels
```

No API credential is stored in this package.

## Statistical procedure

A step-by-step explanation without assumed statistical background is available
in [How the analysis works](METHODS.md).

For each prompt and layer, the phase analysis calculates:

1. log unique-feature count;
2. median feature influence;
3. log median feature activation; and
4. mean token contexts per feature.

The metrics are standardized within prompt. Exact dynamic programming finds
the minimum-error segmentation for one through five phases, with a minimum
segment size of three layers. BIC penalizes additional boundaries and segment
parameters. Boundary stability is evaluated with 1,000 prompt-bootstrap
reruns.

Lower BIC is better. The three-phase model has BIC -74.378, compared with
-70.377 for four phases and -68.310 for five phases.

## Interpretation limits

The three phases are the best discrete summary among the tested segmented
models. BIC does not prove that the boundaries are mechanistically sharp.
Semantic phase names require blinded annotation, and a causal hierarchy
requires matched interventions, mediation measurements, and rescue tests.
