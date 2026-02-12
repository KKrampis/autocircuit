---
name: np-feature-intervention
description: Direct feature-level interventions on individual features (layer, pos, feature_idx). Use when needing to zero, scale, or swap specific features rather than named supernodes. Supports language swapping, open-ended generation with interventions, and comparing pre/post outputs. Requires GPU.
---

# Feature Intervention

Direct feature-level interventions using `feature_intervention.py`.

## Usage

```bash
python -m graph_analysis.feature_intervention \
    --target_prompt <text> --zero <layer,pos,feat_idx> [--json_output]
```

## Parameters

- `--target_prompt`: Prompt to run intervention on (required)
- `--zero`: Features to zero as `layer,pos,feature_idx` (repeatable)
- `--source_prompt`: Prompt to get activation values from (needed with `--activate`)
- `--activate`: Features to activate from source as `layer,pos,feature_idx` (repeatable)
- `--scale`: Scale factor for activated features (default: 1.0)
- `--generate`: Run open-ended generation instead of single-step
- `--json_output`: Output structured JSON
- `--top_k`: Number of top outputs (default: 5)

## Examples

```bash
# Zero a Spanish feature to shift output to English
python -m graph_analysis.feature_intervention \
    --target_prompt "Hecho: Michael Jordan juega al" \
    --zero 20,-1,341

# Swap French -> Spanish: zero French, activate Spanish from source
python -m graph_analysis.feature_intervention \
    --target_prompt "Fait: Michael Jordan joue au" \
    --zero 20,-1,1454 \
    --source_prompt "Hecho: Michael Jordan juega al" \
    --activate 20,-1,341 \
    --scale 10

# Open-ended generation with language swap
python -m graph_analysis.feature_intervention \
    --target_prompt "Fait: Michael Jordan joue au" \
    --zero 20,-1,1454 \
    --source_prompt "Hecho: Michael Jordan juega al" \
    --activate 20,-1,341 \
    --scale 10 \
    --generate
```

## Output

Human-readable or `--json_output`:
- Pre/post intervention top-k predictions (single-step)
- Pre/post intervention generated text (`--generate` mode)
