---
name: np-check-feature
description: Inspect individual transcoder features from HuggingFace. Use when needing to understand what a specific feature does, check its activation range, see top/bottom logits, or view example activations. Triggers on tasks like "what does feature 1454 at layer 20 do?" or "inspect this feature".
---

# Feature Inspection

Inspect transcoder features using `check_feature.py`.

## Usage

```bash
python -m graph_analysis.check_feature --layer <L> --feature_idx <IDX>
python -m graph_analysis.check_feature --layer <L> --feature_idx <IDX> --hf_repo <repo>
```

## Parameters

- `--layer`: Transformer layer (int)
- `--feature_idx`: Feature index (int)
- `--hf_repo`: HuggingFace repo ID (default: `mwhanna/gemma-scope-transcoders`)

## Output

- Activation range (act_min, act_max)
- Top 10 logits the feature promotes
- Bottom 10 logits the feature suppresses
- Example activations from different quantiles with highlighted tokens

## Example

```bash
# What does feature 1454 at layer 20 do?
python -m graph_analysis.check_feature --layer 20 --feature_idx 1454
```
