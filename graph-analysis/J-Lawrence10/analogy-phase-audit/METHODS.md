# How the analysis works

This document explains what the scripts do in plain language. It separates the
steps performed by the code from the conclusions we might draw from them.

## Part 1: Count features across graphs

Each attribution graph can contain the same feature at several token positions.
Those are several uses of one feature inside one graph. They are not several
independent graphs.

The code identifies a feature by two values:

- the model layer;
- the feature number in that layer.

For each feature, the code keeps a set of graph names in which the feature
appears. Its cross-graph count is the size of that set.

```text
for each graph:
    for each feature occurrence in that graph:
        feature = (layer, feature number)
        add the graph name to that feature's set

cross-graph count = number of graph names in the set
```

A feature occurring five times in the Berlin graph and nowhere else therefore
has a cross-graph count of one, not five.

The code also records the total number of occurrences, but does not use that
number as evidence that the feature appears in more graphs.

When averaging influence or activation, the code first averages all occurrences
inside each graph. It then averages those graph-level values. This gives each
prompt equal weight even when a feature appears at more token positions in one
prompt than another.

## Part 2: Summarize every layer

The model has 26 layers, numbered 0 through 25. For every prompt and layer, the
code calculates four measurements:

1. the number of different features in the layer;
2. the middle influence value across those features;
3. the middle activation value across those features;
4. the average number of token positions at which each feature appears.

Before calculating the influence and activation summaries, repeated occurrences
of the same feature in one layer are averaged together.

The feature count and activation measurements can contain a few values much
larger than the rest. The code uses `log(1 + value)` for those two measurements
so that a small number of large values do not control the result.

## Part 3: Put the measurements on the same scale

The four measurements use different units. Feature count might be in the
hundreds, while influence may be below one. Comparing the raw numbers would give
the largest-numbered measurement too much weight.

For each prompt and each measurement, the code:

1. subtracts that prompt's average across layers;
2. divides by that prompt's spread across layers.

After this step, zero means typical for that prompt. Positive values are above
its average, and negative values are below its average. The code then averages
the five prompt profiles.

## Part 4: Try possible layer splits

The code tests models with one through five sections. A section is a continuous
run of layers, and every section must contain at least three layers.

For any proposed section, the code finds its average four-measurement profile.
It then measures how far each layer is from that section average. Smaller total
error means the layers grouped into a section are more alike.

The code checks all valid split locations using dynamic programming. In this
case, that means it stores the best earlier result and reuses it instead of
recalculating every complete combination. It still returns the split locations
with the lowest total error; it is not a greedy search that accepts the first
improvement.

## Part 5: Choose how many sections to keep

Adding more sections almost always lowers the fitting error. That alone would
favor as many sections as the code allows. The Bayesian Information Criterion,
or BIC, adds a penalty for every extra section and boundary.

The exact score used by the code is:

```text
BIC = N × log(error / N) + K × log(N)
```

Here:

- `N` is the number of layer measurements being fitted;
- `error` is the total squared distance from the section averages;
- `K` is the number of fitted section values plus the number of boundaries.

Lower BIC is better. Among the tested section-based models, the lowest BIC came
from three sections beginning at layers 7 and 15. This gives L0–L6, L7–L14, and
L15–L25.

This result means that three sections are the best balance of fit and simplicity
among the tested section-based models. It does not prove that the model contains
three sharply separated mechanisms.

## Part 6: Check whether a result carries to an omitted prompt

The code also leaves out one prompt at a time:

1. find the splits using the other four prompts;
2. use those section averages to predict the omitted prompt;
3. measure the prediction error;
4. repeat until every prompt has been omitted once.

The reported value is the average error across the five rounds. This checks
whether a model describes prompts that were not used to choose its boundaries.

## Part 7: Compare sections with a gradual change

The code also fits simple smooth curves across layer depth. This checks whether
the measurements require clear breaks or can be described as a gradual change.

The current data give lower BIC and lower omitted-prompt error to a smooth cubic
curve, which can change direction up to twice. The three-section result should
therefore be read as the best simple section summary, not as proof of sharp
boundaries.

## Part 8: Check how stable the result is

The code repeats the analysis 1,000 times. On each repeat, it draws five prompts
from the original five, allowing the same prompt to be drawn more than once.

It records two things:

- how often BIC chooses each number of sections;
- when three sections are held fixed, where the two boundaries appear.

The first boundary usually appears at L7 or L8. The second is less precise and
appears from L14 through L18, most often at L15.

## What the algorithm does not determine

The algorithm finds patterns in graph measurements. It does not determine what
the sections mean. Names such as representation, transformation, or output
consolidation are working descriptions that require separate evidence.

Claims about function require blinded feature annotation. Claims that one stage
causes another require controlled interventions, downstream measurements, and
tests showing that restoring the downstream activity restores performance.
