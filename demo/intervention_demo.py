# %%

from collections import namedtuple
from functools import partial
import torch
from circuit_tracer import ReplacementModel

# display functions
from circuit_tracer.utils.demo_utils import display_topk_token_predictions, display_generations_comparison

# %%

backend = 'transformerlens'  # change to 'nnsight' for the nnsight backend!
model = ReplacementModel.from_pretrained("google/gemma-2-2b", "gemma", dtype=torch.bfloat16, backend=backend)

# %%

Feature = namedtuple('Feature', ['layer', 'pos', 'feature_idx'])

# a display function that needs the model's tokenizer
display_topk_token_predictions = partial(display_topk_token_predictions, tokenizer=model.tokenizer)

# %% Example: Changing languages with zero ablations

"""
Imagine that yu have the following [annotated attribution graph](https://www.neuronpedia.org/gemma-2-2b/graph?slug=gemma-michael-jordan-es&clerps=%5B%5B%222308855%22%2C%22sports%22%5D%2C%5B%222502222%22%2C%22Spanish+articles%22%5D%2C%5B%222513416%22%2C%22Spanish%22%5D%2C%5B%222509334%22%2C%22Spanish%22%5D%2C%5B%222413490%22%2C%22Spanish%22%5D%2C%5B%222403018%22%2C%22Spanish%22%5D%2C%5B%222407980%22%2C%22Spanish+articles%22%5D%2C%5B%222511463%22%2C%22Spanish%22%5D%2C%5B%222104818%22%2C%22basketball%22%5D%2C%5B%222109324%22%2C%22sports%22%5D%2C%5B%222009090%22%2C%22basketball%22%5D%2C%5B%221712431%22%2C%22sports%22%5D%2C%5B%221515208%22%2C%22play%22%5D%2C%5B%22401305%22%2C%22game%22%5D%2C%5B%22109339%22%2C%22a%2Fal+in+Spanish%22%5D%2C%5B%2213978%22%2C%22romance+languages%22%5D%2C%5B%2215822%22%2C%22romance+languages%22%5D%2C%5B%221404939%22%2C%22play%22%5D%2C%5B%221915763%22%2C%22sports%22%5D%2C%5B%221812672%22%2C%22basketball%22%5D%2C%5B%221414510%22%2C%22sports%22%5D%2C%5B%22401742%22%2C%22basketball%22%5D%2C%5B%22101173%22%2C%22basketball%22%5D%2C%5B%22411%22%2C%22famous+people+%2F+named+entities%22%5D%2C%5B%222000341%22%2C%22Spanish%22%5D%2C%5B%222303604%22%2C%22sports+%2F+table+tennis+%2F+pool+%22%5D%2C%5B%222413277%22%2C%22%28incomprehensible%29%22%5D%5D&pinnedIds=27_143831_6%2C25_13416_6%2C24_3018_6%2C25_9334_6%2C24_13490_6%2C25_2222_6%2C24_7980_6%2C25_11463_6%2C21_9324_6%2C21_4818_6%2C23_8855_6%2C20_9090_6%2C17_12431_6%2C15_15208_6%2C14_4939_6%2C4_1305_6%2C1_9339_6%2CE_113501_5%2C0_13978_5%2C0_15822_5%2CE_717_6%2C19_15763_6%2C18_12672_6%2C4_1742_4%2C14_14510_4%2C1_1173_4%2CE_18853_4%2CE_7939_3%2C0_411_4%2C20_341_6&supernodes=%5B%5B%22basketball%22%2C%2220_9090_6%22%2C%2218_12672_6%22%2C%2221_4818_6%22%2C%2223_8855_6%22%5D%2C%5B%22sports%22%2C%2217_12431_6%22%2C%2219_15763_6%22%2C%2221_9324_6%22%5D%2C%5B%22play%22%2C%224_1305_6%22%2C%2214_4939_6%22%2C%2215_15208_6%22%5D%2C%5B%22basketball%22%2C%224_1742_4%22%2C%221_1173_4%22%5D%2C%5B%22romance+language%22%2C%221_9339_6%22%2C%220_15822_5%22%2C%220_13978_5%22%5D%2C%5B%22Spanish%22%2C%2225_9334_6%22%2C%2225_13416_6%22%2C%2224_13490_6%22%2C%2224_7980_6%22%2C%2224_3018_6%22%2C%2225_2222_6%22%2C%2225_11463_6%22%2C%2220_341_6%22%5D%5D&clickedId=20_341_6) showing the circuit for the Spanish sentence `Hecho: Michael Jordan juega al` or in English, `Fact: Michael Jordan plays`. The correct answer, which the model correctly predicts, is `baloncesto`, or `basketball`. We observe a supernode of features that correspond to the Spanish language. Can we intervene on these features to change the model's output?

First, we can try to do this by identifying these supernode features, which we store below. For each, we store their layer, position (here, always -1, as all of these features are active at the final position), and feature ID. For the sake of convenience, we'll only add one supernode feature.
"""

supernode_features = [
    Feature(layer=20,pos=-1,feature_idx=341), # spanish supernode feature
]

# %%

"""
Next, we need to turn our supernode features into a list of intervention tuples. These tuples are formatted as (layer, pos, feature_idx, new_feature_value). For now, let's try just zeroing out these features as the last position.
"""

intervention_tuples = [(*supernode_feature, 0.0) for supernode_feature in supernode_features]

# %%

"""
Finally, we can run the intervention and view its effects on the model's output!
"""

s = "Hecho: Michael Jordan juega al"

with torch.inference_mode():
    original_logits, _  = model.feature_intervention(s, [])
    new_logits, _ = model.feature_intervention(s, intervention_tuples)

# %%

"""
That's wasn't very effective! We do see that the probability of `basketball` has risen, bringing it into the top 5. But intervening on just one feature isn't enough to change the model's behavior dramatically, the rest of the distribution remains or less the same. This is because many Spanish features contribute to our model's output language, while we changed only one. Try changing more!
"""

display_topk_token_predictions(s, original_logits, new_logits)

# %% Example: Swapping languages by turning features on

"""
In the last example, we only turned Spanish features off, yielding text in English, which seems to be the model's default. But what if we wanted to swap to another language? Then we'd have to turn language features from that language on. Let's try this with another language, French. Here is the attribution graph for the analogous French sentence, `Fait: Michael Jordan joue au` -> `basket`.

The answer to the French query is "basket". can we change that to Spanish? We start by taking one relatively low-level French feature, that feeds into all of the others.
"""

french_supernode_features = [Feature(layer=20,pos=-1,feature_idx=1454)]

# %%

"""
But what should we set the values of the French supernode feature to be? Ideally, we set them to some in-distribution values. To do this, we can get the activations of these nodes on the French input sentence. We'll get these as a sparse tensor, to save on memory.

Sparse tensor, a tensor where most values are zero. Instead of storing all values, it only stores the non-zero positions and their values. For example:

Dense: [0, 0, 5.2, 0, 0, 0, 3.1, 0, ...] # stores every element
Sparse: {2: 5.2, 6: 3.1} # stores only non-zeros

This matters here because each transcoder layer has ~16k features, but only a handful fire on any given token (that's what "sparse" means in SAE/transcoder research, most features are inactive)
"""

s_spanish = "Hecho: Michael Jordan juega al"
_, activations = model.get_activations(s_spanish, sparse=True)

# %%

print("activations shape:", activations.indices()) # shape: [3, nnz] (3 dims: layer, seq, feat)
print("activations nonzero values:", activations.values()) # shape: [nnz]

indices = activations.indices() # shape: [3, nnz] (3 dims: layer, seq, feat)
layer_idx = indices[0] # which layer each non-zero is in
seq_idx = indices[1] # which token position
feat_idx = indices[2] # which feature

# To see active features at a specific layer/position, convert that slice to dense:
layer, pos = 20, -1
dense_slice = activations[layer, pos].to_dense() # shape: [n_features]
nonzero_feats = dense_slice.nonzero().squeeze(-1) # feature indices that fired
print(f"nonzero feature indices at layer {20}, pos {pos}:", nonzero_feats)
print("their values:", dense_slice[nonzero_feats]) # their values

# %%

"""
Now, we construct and perform the intervention! Each supernode_feature contaisn precisely the information needed to index into activations
"""
spanish_supernode_features = supernode_features  # from before
fr_es_intervention_tuples = [(*supernode_feature, 0.0) for supernode_feature in french_supernode_features] 
fr_es_intervention_tuples += [(*supernode_feature, 10*activations[supernode_feature]) for (supernode_feature) in spanish_supernode_features]

# %%

s_french = "Fait: Michael Jordan joue au"

with torch.inference_mode():
    original_logits, _ = model.feature_intervention(s_french, [])
    new_logits, _ = model.feature_intervention(s_french, fr_es_intervention_tuples)

display_topk_token_predictions(s_french, original_logits, new_logits)

# %% Example: Interventions + Sampling

"""
We've now intervened twice on the last token of the sentence; interventions on other positions work analogously. But what if we want to intervene in an open-ended fashion, allowing our model to generate tokens with that intervention still active? We can do this as follows, by setting the position of our intervention to an open-ended slice: `slice(pos, None None)`. We set `pos` to be the last token of the original input, but you can also set it to an earlier position.
"""
sequence_length = len(model.tokenizer(s_spanish).input_ids)
original_feature_pos = sequence_length - 1
open_ended_slice = slice(original_feature_pos, None, None)
open_ended_es_fr_intervention_tuples = [(layer, open_ended_slice, feature_idx, 0.0) for (layer, _, feature_idx) in french_supernode_features] 
open_ended_es_fr_intervention_tuples += [(layer, open_ended_slice, feature_idx, 10*activations[layer, orig_pos, feature_idx]) for (layer, orig_pos, feature_idx) in spanish_supernode_features]

# %%

"""
Now, we generate by  calling `feature_intervention_generate`! `do_sample` is off here for consistency, but you can turn it on.

Without KV cache - every generation step reruns the full forward pass over all tokens:
Step 1: ["F", "ait", ":", " Michael", " Jordan", " joue", " au"] -> predicts " basket"
Step 2: ["F", "ait", ":", " Michael", " Jordan", " joue", " au", " basket"] -> predicts " avec"]

At every step, your intervention hook fires on the full sequence. If you said "zero out feature 1454 at position 6", it applies cleanly at position 6 every time.

With KV cache - the attention keys/values from previous tokens are cached. Only the newest token is passed through the model on each step:
Step 1: ["F", "ait", ":", " Michael", " Jordan", " joue", " au"] -> predicts " basket" -> full pass, KVs cached
Step 2: ["basket"] -> predicts " avec" -> only 1 token, use cached KVs

The problem: at step 2, the input is just ["basket"], it has only 1 position. If your intervention says "modify position 5", there is no position 6 anymore. The hook has nothing to grab onto.

That's why open-ended interventions use `slice(pos, None)` and the code converts them to `position=0` during generation in `circuit_tracer.replacement_model.replacement_model_transformerlens.py`

```
if isinstance(pos, slice) and pos.stop is None:
    converted.append((layer, 0, feat_idx, value))
```

So with KV cache enabled, the intervention is re-applied at position 0 (the current new token) on every generation step, which is actually what you want for open-ended generation.
"""

pre_intervention_generation = [model.feature_intervention_generate(s_french, [], do_sample=False, verbose=False)[0]]
post_intervention_generation = [model.feature_intervention_generate(s_french, open_ended_es_fr_intervention_tuples, do_sample=False, verbose=False)[0]]

display_generations_comparison(s_french, pre_intervention_generation, post_intervention_generation)

# %%