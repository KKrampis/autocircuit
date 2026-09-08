# Objective Layer Segmentation Audit

This analysis uses graph statistics only. It does not establish semantic phase roles.

## Candidate piecewise models

| Phases | Boundaries | BIC | Leave-one-prompt-out loss |
|---:|---|---:|---:|
| 1 | [] | -1.932 | 1.000000 |
| 2 | [10] | -53.799 | 0.582066 |
| 3 | [7, 15] | -74.378 | 0.476662 |
| 4 | [3, 7, 15] | -70.377 | 0.451973 |
| 5 | [7, 14, 18, 22] | -68.310 | 0.421420 |

BIC selected **3 phase(s)** with boundaries [7, 15].

Leave-one-prompt-out prediction selected **5 phase(s)** with full-data boundaries [7, 14, 18, 22].

## Smooth controls

| Polynomial degree | BIC | Leave-one-prompt-out loss |
|---:|---:|---:|
| 1 | -61.223 | 0.571702 |
| 2 | -95.981 | 0.421724 |
| 3 | -97.897 | 0.385894 |

Across both model families, BIC selected **degree-3** (smooth_polynomial).

A publishable semantic phase claim additionally requires blinded feature annotations, held-out prompts, stable boundaries, and independent causal validation.
