# Meeting script

## Slide 1 — Reassessing analogy circuits

We reproduced the original five analogy attribution graphs and asked two
questions: which features genuinely recur across prompts, and whether their
layer-wise organization supports a three-phase description.

## Slide 2 — Same graphs, corrected experimental unit

The regenerated graphs use the published model, prompts, and pruning
parameters, and their node and edge counts match the published summaries.
The correction happens downstream. We count how many distinct graphs contain
each SAE feature. Repeated activations at several token positions within one
graph remain multiple contexts, but they contribute only one vote toward
cross-prompt recurrence.

## Slide 3 — The shared core is smaller but remains substantial

The all-five core falls from 180 to 119 features, a 33.9 percent reduction.
The at-least-four-of-five result falls from 277 to 210. Importantly, all five
headline manuscript features genuinely survive in all five graphs. This
preserves the interesting shared signal while giving it a more accurate size.

## Slide 4 — BIC selects three phases

BIC is the Bayesian Information Criterion. It rewards a model for fitting the
data and penalizes it for adding unnecessary complexity; lower is better.
Among the one- through five-phase models, three phases have the lowest BIC,
-74.4. Four and five phases improve some fit measures, but not enough to
justify their extra boundaries and parameters.

## Slide 5 — The three numeric regimes

The data-selected phases begin at layers 7 and 15. Phase 1, layers 0 through 6,
has many broadly recurring features and lower activation. Phase 2, layers 7
through 14, is sparser and has the highest average influence. Phase 3, layers
15 through 25, is sparse and has the highest median activation. We can use
broad representation, selective transformation, and output consolidation as
working descriptions, but the semantic names remain provisional.

## Slide 6 — Bootstrap support and boundary uncertainty

Across 1,000 prompt-bootstrap reruns, the first boundary lies at L7 in 782
runs and L8 in 218. The second boundary is most often L15, with uncertainty
from L14 to L18. The result supports a three-part summary, while also showing
that the later transition is less precisely located.

## Slide 7 — What the evidence supports now

We reproduced the original graphs, corrected the recurrence calculation, and
retained a substantial shared circuit. BIC selects a three-phase organization:
an early broad feature regime, a middle high-influence regime, and a late
high-activation regime. The next step is to validate the boundaries on more
prompts, blind the semantic annotation, and test each phase with matched causal
controls.

## Short answers for questions

**Does BIC prove three phases exist?**
No. It says three phases are the best balance of fit and complexity among the
tested segmented models. More prompts and causal validation are still needed.

**Did the correction eliminate the core features?**
No. It reduced the size of the all-five core from 180 to 119, but all five
headline features remain.

**Why are the boundaries different from the original L5 and L10 split?**
The new boundaries were selected from objective layer-wise graph metrics rather
than fixed in advance.

**What do the phases mean?**
The statistics support different numeric regimes. The functional names are
working interpretations until blinded annotation and causal tests confirm them.
