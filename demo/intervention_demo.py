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
    Feature(layer=20,pos=-1,feature_idx=341),
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
"""