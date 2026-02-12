# %%

from circuit_tracer import ReplacementModel
from circuit_tracer.utils.demo_utils import extract_supernode_features
from graph_visualization import create_graph_visualization, Supernode, InterventionGraph, Feature

import torch

from collections import namedtuple

# %%

# do export HF_TOKEN=...
# gemma-2-2b is a gated model.
backend = 'transformerlens' # 'transformerlens' or 'nnsight'
model = ReplacementModel.from_pretrained("google/gemma-2-2b", "gemma", dtype=torch.bfloat16, backend=backend)

# %%

dallas_austin_url = "https://www.neuronpedia.org/gemma-2-2b/graph?slug=gemma-fact-dallas-austin&clerps=%5B%5D&pruningThreshold=0.53&pinnedIds=27_22605_10%2C20_15589_10%2CE_26865_9%2C21_5943_10%2C23_12237_10%2C20_15589_9%2C16_25_9%2C14_2268_9%2C18_8959_10%2C4_13154_9%2C7_6861_9%2C19_1445_10%2CE_2329_7%2CE_6037_4%2C0_13727_7%2C6_4012_7%2C17_7178_10%2C15_4494_4%2C6_4662_4%2C4_7671_4%2C3_13984_4%2C1_1000_4%2C19_7477_9%2C18_6101_10%2C16_4298_10%2C7_691_10&supernodes=%5B%5B%22capital%22%2C%2215_4494_4%22%2C%226_4662_4%22%2C%224_7671_4%22%2C%223_13984_4%22%2C%221_1000_4%22%5D%2C%5B%22state%22%2C%226_4012_7%22%2C%220_13727_7%22%5D%2C%5B%22Texas%22%2C%2220_15589_9%22%2C%2219_7477_9%22%2C%2216_25_9%22%2C%224_13154_9%22%2C%2214_2268_9%22%2C%227_6861_9%22%5D%2C%5B%22preposition+followed+by+place+name%22%2C%2219_1445_10%22%2C%2218_6101_10%22%5D%2C%5B%22capital+cities+%2F+say+a+capital+city%22%2C%2221_5943_10%22%2C%2217_7178_10%22%2C%227_691_10%22%2C%2216_4298_10%22%5D%5D"
supernode_features = extract_supernode_features(dallas_austin_url)

print(supernode_features)

# %%

# Supernodes that upweight certain outputs. Note that e.g. the Say Austin node is not the only node promoting Austin, but that is its primary role
say_austin_node = Supernode(
    name="Say Austin", features=[Feature(layer=23, pos=10, feature_idx=12237)]
)
# Say a capital -> say Austin
say_capital_node = Supernode(
    name="Say a capital",
    features=supernode_features["capital cities / say a capital city"],
    children=[say_austin_node],
)

print(say_austin_node)
print(say_capital_node)

# %%

# Intermediate nodes
# Texas -> say Austin
texas_node = Supernode(
    name="Texas", features=supernode_features["Texas"], children=[say_austin_node]
)
# state -> "say a capital", "Texas"
state_node = Supernode(
    name="state", features=supernode_features["state"], children=[say_capital_node, texas_node]
)
# capital -> "say a capital"
capital_node = Supernode(
    name="capital", features=supernode_features["capital"], children=[say_capital_node]
)

print(texas_node)
print(state_node)
print(capital_node)

# %%

# Embedding nodes
# Emb: Dallas -> Texas
dallas_node = Supernode(name="Emb: Dallas", features=None, children=[texas_node])
# Emb: state -> Texas
state_emb_node = Supernode(name="Emb: state", features=None, children=[state_node])
# Emb: capital -> capital
capital_emb_node = Supernode(name="Emb: capital", features=None, children=[capital_node])

print(dallas_node)
print(state_emb_node)
print(capital_emb_node)

# %%

prompt = "Fact: the capital of the state containing Dallas is"
ordered_nodes = [
    [capital_emb_node, state_emb_node],
    [capital_node, state_node, dallas_node],
    [say_capital_node, texas_node],
    [say_austin_node],
]
# ordered_nodes is used purely for visualization layout. It controls how nodes are positioned in the SVG graph rendering
dallas_austin_graph = InterventionGraph(ordered_nodes=ordered_nodes, prompt=prompt)

# %%

logits, dallas_activations = model.get_activations(prompt)

# %%

print(f"logits.shape: {logits.shape}") # shape: [batch, sequence, vocab_size]
print(f"dallas_activations.shape: {dallas_activations.shape}") # shape: [n_layers, n_pos, d_transcoder]

# %%

print(capital_node.features[0])
print(dallas_activations[capital_node.features[0]])
print(dallas_activations[15,4,4494])

# %%

# initialize each node, adding it to the intervention graph and recording its default activation
for node in [capital_node, state_node, dallas_node, say_capital_node, texas_node, say_austin_node]:
    dallas_austin_graph.initialize_node(node, dallas_activations)
    """
    dallas_austion_graph.initialize_node does the following:
    ```python
    self.nodes[node.name] = node
    node.default_activations = torch.tensor(
        [dallas_activations[feature] for feature in node.features]
    )
    ```
    This becomes the baseline - the activation the model naturally produces on this prompt
    """

# set each node's current activation to a percent of its default activation (here 100%)
dallas_austin_graph.set_node_activation_fractions(dallas_activations)
"""
dallas_austin_graph.set_node_activation_fractions does the following:
for node in self.nodes.values():
  current = torch.tensor([dallas_activations[f] for f in node.features])
  node.activation = (current / node.default_activations).mean().item()
  node.intervention = None
  node.replacement_node = None

It divides current activations by default activations element-wise, then takes the mean. Right now, since `current_activations` is the same `dallas_activations` used to initialize, every node gets `activation = 1.0` (100% of default)

This becomes useful later when you run an intervention, you'd pass the post-intervention activations to set_node_activation_fractions, and nodes would show values like `0.0` (knocked out), `0.5` (half strength), `2.0` (doubled), etc. The visualization uses this to gray out low-activation nodes (those with activation <= 0.25)
"""

# %%

def get_top_outputs(logits: torch.Tensor, k: int = 5):
    top_probs, top_token_ids = logits.squeeze(0)[-1].softmax(-1).topk(k)
    top_tokens = [model.tokenizer.decode(token_id) for token_id in top_token_ids]
    top_outputs = list(zip(top_tokens, top_probs.tolist()))
    return top_outputs


top_outputs = get_top_outputs(logits)

# %%

print("Top model outputs:")
for token, prob in top_outputs:
    print(f"{token}: {prob:.4f}")

# %%

# return SVG graph visualization showing the intervention graph and top model outputs
create_graph_visualization(dallas_austin_graph, top_outputs)

# %%

# An Intervention says "set the activation of supernode to intervention_value * its activation in the given activations tensor"
Intervention = namedtuple("Intervention", ["supernode", "scaling_factor"])

def supernode_intervention(
    intervention_graph: InterventionGraph,
    interventions: list[Intervention],
    replacements: dict[str, Supernode] = None,
):
    """Performs interventions on a set of supernodes, records the outputs, and draws the corresponding graph

    Args:
        interventions (list[Intervention]): List of interventions to perform
        replacements (dict[str, Supernode], optional): Replacement supernodes to add, if we're adding supernodes
            from another prompt. Defaults to None.

    Returns:
        HTML: An IPython.display.HTML object showing the graph corresponding to these interventions
    """
    intervention_values = [
        (*feature, scaling_factor * default_act)
        for intervened_supernode, scaling_factor in interventions
        for feature, default_act in zip(
            intervened_supernode.features, intervened_supernode.default_activations
        )
    ]
    new_logits, new_activations = model.feature_intervention(
        intervention_graph.prompt, intervention_values
    )
    intervention_graph.set_node_activation_fractions(new_activations)
    top_outputs = get_top_outputs(new_logits)

    for intervened_supernode, scaling_factor in interventions:
        intervened_supernode.activation = None
        """
        for an intervened node, the "activation fraction" metric is meaningless. The node's activation wasn't naturally computed by the model, it was forcibly overridden. Showing a percentage would be misleading.
        Setting it to `None` tells the visualization to skip the activation label for that node
        So in the SVG, you'd see:
        - Intervened nodes: show an orange "-2x" badge (no activation percentage)
        - Other nodes: show their activation percentage relative to baseline (e.g. "18%" if they dropped due to the intervention propagating)
        """
        intervened_supernode.intervention = f"{scaling_factor}x"

    if replacements is not None:
        """
        `replacements` is for swapping in features from a different prompt's activations into the visualization. It visually shows that a node has been replaced by an alternative.
        For example, imagine you want to test: "what if the model thought about California instead of Texas?"
        You'd:
        1. Run a different prompt (e.g. about Sacramento/California) to get its activations
        2. Create a new supernode from those activations (e.g. `california_node`)
        3. Pass `replacements={"Texas": california_node}`
        """
        for target, replacement in replacements.items():
            intervention_graph.nodes[target].replacement_node = replacement

    return create_graph_visualization(intervention_graph, top_outputs)

# %%

# set every feature in "Say a capital" to -2x its default value.
#
# In the original paper, turning off the "Say a capital" feature caused the "Say Austin" supernode to shut off, and the model's top logit to change to Texas. What happens if we do the same?
#
# We observe precisely the same behavior! Strongly shutting off the "Say a capital" supernode turned off the "Say Austin" node, and changed the top logit to Texas.
supernode_intervention(dallas_austin_graph, [Intervention(say_capital_node, -2)])

# %% What if we turn off the "capital" supernode?

# set every feature in "capital" to -2x its default value.
#
# This yields similar behavior to before. We turn off the "Say a capital" supernode, though not as strongly in as in the prior intervention. This also partially turns off the "Say Austin" node.
supernode_intervention(dallas_austin_graph, [Intervention(capital_node, -2)])

# %% What if we turn off the Texas supernode?

# set every feature in "Texas" to -2x its default value.
#
# Turning off the Texas supernode off also disabled the "Say Austin" node, yielding the capitals of other states.
supernode_intervention(dallas_austin_graph, [Intervention(texas_node, -2)])

# %%
# What if we turn off the "state" supernode?

# set every feature in "state" to -2x its default value.
#
# Turning off the state supernode was largely ineffective: It caused little change to any of the other supernode activations, and little change to the model logits.
supernode_intervention(dallas_austin_graph, [Intervention(state_node, -2)])

# %%
# We've validated the behavior of nodes by ablating them. Could we inject entirely different nodes and validate that they have the expected effect? Take the circuit from the prompt `Fact: The capital of the state containing Oakland is` -> `Sacramento`). We'll add two supernodes from this graph-"California" and "Say Sacramento" to our InterventionGraph.

oakland_prompt = "Fact: the capital of the state containing Oakland is"
_, oakland_activations = model.get_activations(oakland_prompt)

oakland_url = "https://www.neuronpedia.org/gemma-2-2b/graph?slug=gemma-fact-oakland-sacramento&clerps=%5B%5D&pruningThreshold=0.5&pinnedIds=27_43939_10%2CE_49024_9%2C21_5943_10%2C19_9209_10%2C18_8959_10%2C14_12562_9%2C7_14530_9%2C8_14641_9%2C4_8625_9%2C19_9209_9%2C17_7178_10%2CE_6037_4%2C15_4494_4%2CE_2329_7%2C16_4298_10%2C7_691_10%2C6_4662_4%2C4_7671_4%2C2_8734_4%2C0_1961_4%2C6_13909_9%2C22_4367_10%2C21_2464_10&supernodes=%5B%5B%22capital%22%2C%226_4662_4%22%2C%2215_4494_4%22%2C%224_7671_4%22%2C%222_8734_4%22%2C%220_1961_4%22%5D%2C%5B%22capital%22%2C%2221_5943_10%22%2C%2216_4298_10%22%2C%2217_7178_10%22%2C%227_691_10%22%5D%2C%5B%22California%22%2C%2222_4367_10%22%2C%2221_2464_10%22%5D%2C%5B%22Bay+Area+%28say+California%29%22%2C%227_14530_9%22%2C%224_8625_9%22%5D%2C%5B%22California%22%2C%226_13909_9%22%2C%228_14641_9%22%2C%2214_12562_9%22%5D%5D&clickedId=27_43939_10"
oakland_supernodes = extract_supernode_features(oakland_url)

say_sacramento_node = Supernode(
    "Say Sacramento", features=[Feature(layer=19, pos=10, feature_idx=9209)]
)
california_node = Supernode(
    "California",
    features=oakland_supernodes["California"] + oakland_supernodes["California (2)"],
    children=[say_sacramento_node],
)

for node in [say_sacramento_node, california_node]:
    dallas_austin_graph.initialize_node(node, oakland_activations)

"""
Why we do not call dallas_austin_graph.set_node_activation_fractions here:
- Because `set_node_activation_fractions` is called inside `supernode_intervention` function
The two new nodes were already registered via `initialize_node`, which adds them to `dallas_austin_graph.nodes`. So when `supernode_intervention` function runs and calls `set_node_activation_fractions(new_activations)`, it iterates over all nodes in self.nodes, including `say_sacramento_node` and `california_node`.
The earlier call to `set_node_activation_fractions` was just to set the initial 100% baseline for the visualization before any interventions. For the Oakland nodes, that initial display isn't needed since they go straight into an intervention.
"""

# %%

"""
Doing this caused the "Say Austin" node to shut off entirely, while the "Say Sacramento" node began to activate! Our model's top output is now Sacramento, as well.
"""
oakland_interventions = [Intervention(texas_node, -2), Intervention(california_node, 2)]
supernode_intervention(
    dallas_austin_graph,
    oakland_interventions,
    {texas_node.name: california_node, say_austin_node.name: say_sacramento_node},
)

# %%

"""
We can also do this replacing states with countries. Take the circuit for `Fact: The capital of the coutnry containing Shanghai is` -> `Beijing`. Well do precisely what we did before, disabling Texas and activating the China supernode. This time, there is no "Say Beijing" node, but the effect of this intervention should be visible in the logits.
"""

shanghai_prompt = "Fact: the capital of the country containing Shanghai is"
_, shanghai_activations = model.get_activations(shanghai_prompt)

shanghai_url = "https://www.neuronpedia.org/gemma-2-2b/graph?slug=gemma-fact-shanghai-beijing&clerps=%5B%5D&clickedId=15_4494_4&pruningThreshold=0.45&pinnedIds=27_33395_10%2CE_38628_9%2C21_5943_10%2C19_12274_10%2C19_12274_9%2C14_12274_9%2C18_6101_10%2C17_7178_10%2C6_6811_9%2C4_4257_9%2C4_11570_9%2CE_6037_4%2C0_8885_4%2C18_7639_10%2C19_2695_10%2C16_4298_10%2C15_4494_4%2C6_4662_4&supernodes=%5B%5B%22China%22%2C%2219_12274_9%22%2C%2214_12274_9%22%2C%226_6811_9%22%2C%224_11570_9%22%2C%224_4257_9%22%5D%2C%5B%22China%22%2C%2219_12274_10%22%2C%2218_7639_10%22%5D%2C%5B%22capital%22%2C%2216_4298_10%22%2C%2217_7178_10%22%2C%2218_6101_10%22%2C%2219_2695_10%22%2C%2221_5943_10%22%5D%2C%5B%22capital+cities+%28say+city%29%22%2C%226_4662_4%22%2C%2215_4494_4%22%2C%220_8885_4%22%5D%5D"
shanghai_supernodes = extract_supernode_features(shanghai_url)

china_node = Supernode(
    "China", features=shanghai_supernodes["China"] + shanghai_supernodes["China (2)"]
)

for node in [china_node]:
    dallas_austin_graph.initialize_node(node, shanghai_activations)
# %%

"""
This works as well! Beijing is now the models' most likely output.
"""
china_interventions = [Intervention(texas_node, -2), Intervention(china_node, 2)]
supernode_intervention(dallas_austin_graph, china_interventions, {texas_node.name: china_node})

# %%

"""
Does this always work? Let's try with the circuit for `Fact: the capital of the territory containing Vancouver is` -> `Victoria`
"""
vancouver_prompt = "Fact: the capital of the territory containing Vancouver is"
_, vancouver_activations = model.get_activations(vancouver_prompt)

vancouver_url = "https://www.neuronpedia.org/gemma-2-2b/graph?slug=gemma-fact-vancouver-victoria&clerps=%5B%5D&clickedId=4_11742_9&pruningThreshold=0.45&pinnedIds=27_18221_10%2CE_32936_9%2C21_2236_10%2C19_15123_10%2C18_1025_10%2C14_12562_9%2C14_5600_9%2C6_11873_9%2C4_8439_9%2CE_6037_4%2CE_19412_7%2C4_11742_9%2C0_16137_7&supernodes=%5B%5B%22Canada%22%2C%2214_5600_9%22%2C%226_11873_9%22%2C%224_8439_9%22%5D%5D"
vancouver_supernodes = extract_supernode_features(vancouver_url)

say_victoria_node = Supernode(
    "Say Victoria", features=[Feature(layer=21, pos=10, feature_idx=2236)]
)
bc_node = Supernode(
    "British Columbia",
    features=[Feature(layer=18, pos=10, feature_idx=1025)],
    children=[say_victoria_node],
)

for node in [say_victoria_node, bc_node]:
    dallas_austin_graph.initialize_node(node, vancouver_activations)

# %%

"""
In this case, the intervention was not very effective. The model's output looks like it did when just ablating Texas, which indicates that the addition of British Columbia did little. A motivated reader might want to try activating the British Columbia node more strongly - what happens?
"""
bc_interventions = [Intervention(texas_node, -2), Intervention(bc_node, 2)]
supernode_intervention(
    dallas_austin_graph,
    bc_interventions,
    {texas_node.name: bc_node, say_austin_node.name: say_victoria_node},
)

# %% Multilingual Circuits

"""
In this section, we'll look at multilingual circuits, as studied in the [original paper](https://transformer-circuits.pub/2025/attribution-graphs/biology.html#dives-multilingual). Specifically, we'll look at three circuits, for the same sentence in 3 languages:
- English: `The opposite of "small" is ` -> `big`
- French: `Le contraire de "petit" est ` -> `grand`
- Chinese: `“小”的反义词是` -> `大`

Work on Haiku showed one shared multilingual circuit

Our circuits indicate the same behavior. In fact, unlike the Haiku circuits, the Gemma 2 (2B) circuits are essentially entirely multilingual. There are no individual "Say big" or "Say grand" supernodes that cause the model to output a specific language. Instead, all circuits use "Ssay big" features, combined with a "French" or "Chinese" feature if the answer is non-English.

Let's study these circuits by performing interventions on them. First, we'll create Supernode objects, as before:
"""

url_fr = "https://www.neuronpedia.org/gemma-2-2b/graph?slug=gemma-small-big-fr&clerps=%5B%5D&pruningThreshold=0.65&pinnedIds=27_21996_8%2CE_64986_5%2C24_16045_8%2C19_5058_8%2C21_10062_8%2C23_2592_8%2C20_1454_8%2CE_63265_2%2C23_8683_8%2C23_8488_8%2C20_11434_8%2C19_5802_8%2CE_1455_7%2C15_5617_5%2C18_9402_8%2C6_4362_5%2C14_11360_5%2C3_2908_5%2C2_5452_5%2C3_6627_5%2C6_16184_2%2C4_95_2%2C22_10566_8%2C21_1144_8%2CE_2025_1%2CE_581_3%2C5_982_2%2C6_651_2%2C5_8646_2%2C6_2743_2%2C8_1988_2%2C4_7409_2%2C4_15846_2%2C3_11241_2%2C2_321_2%2C2_4657_2&supernodes=%5B%5B%22say+big+%2F+large%22%2C%2223_8683_8%22%2C%2223_8488_8%22%2C%2221_10062_8%22%5D%2C%5B%22too%22%2C%2219_5058_8%22%2C%2224_16045_8%22%2C%2220_11434_8%22%5D%2C%5B%22small%22%2C%2215_5617_5%22%2C%2214_11360_5%22%2C%223_6627_5%22%2C%223_2908_5%22%2C%222_5452_5%22%5D%2C%5B%22size%22%2C%2218_9402_8%22%2C%226_4362_5%22%5D%2C%5B%22French%22%2C%2221_1144_8%22%2C%2222_10566_8%22%2C%2220_1454_8%22%2C%2223_2592_8%22%2C%2219_5802_8%22%5D%2C%5B%22opposite%22%2C%226_16184_2%22%2C%224_95_2%22%2C%225_8646_2%22%2C%226_2743_2%22%2C%228_1988_2%22%2C%226_651_2%22%2C%225_982_2%22%2C%222_321_2%22%2C%223_11241_2%22%2C%222_4657_2%22%2C%224_7409_2%22%2C%224_15846_2%22%5D%5D&clickedId=3_11241_2"
supernodes_fr = extract_supernode_features(url_fr)
french_node = Supernode("French", features=supernodes_fr["French"], children=[])
say_big_node = Supernode("Say big", features=supernodes_fr["say big / large"])
small_node = Supernode("small", features=supernodes_fr["small"], children=[say_big_node])
opposite_node = Supernode("opposite", features=supernodes_fr["opposite"], children=[say_big_node])

url_en = "https://www.neuronpedia.org/gemma-2-2b/graph?slug=gemma-small-big-en&clerps=%5B%5D&pruningThreshold=0.65&pinnedIds=27_13210_8%2CE_10498_5%2C23_8683_8%2C21_10062_8%2C17_12530_5%2C18_9402_8%2C6_4362_5%2C15_5617_5%2C15_5756_5%2C19_5058_8%2C14_11360_5%2CE_13388_2%2C15_7209_2%2C4_95_2%2C3_6576_2%2C27_7773_8%2C7_10545_5&supernodes=%5B%5B%22Output+%5C%22big%5C%22+or+%5C%22large%5C%22%22%2C%2227_7773_8%22%2C%2227_13210_8%22%5D%2C%5B%22say+big+%2F+huge+%2F+large%22%2C%2221_10062_8%22%2C%2223_8683_8%22%5D%2C%5B%22opposite%22%2C%224_95_2%22%2C%2215_7209_2%22%2C%223_6576_2%22%5D%2C%5B%22small%22%2C%2214_11360_5%22%2C%2217_12530_5%22%2C%2215_5617_5%22%5D%2C%5B%22large+%2F+size%22%2C%226_4362_5%22%2C%227_10545_5%22%2C%2215_5756_5%22%5D%5D&clickedId=6_4362_5"
supernodes_en = extract_supernode_features(url_en)


url_zh = "https://www.neuronpedia.org/gemma-2-2b/graph?slug=gemma-small-big-zh&clerps=%5B%5D&pruningThreshold=0.65&pinnedIds=27_235469_8%2CE_235585_2%2C23_8488_8%2C23_8683_8%2C21_10062_8%2C19_5058_8%2C22_11933_8%2C21_9377_8%2C18_9402_8%2C15_5617_2%2C14_11360_2%2C14_13476_2%2C2_2169_2%2C1_10169_2%2C8_1988_6%2C4_15846_6%2C4_7409_6%2CE_208659_4%2CE_237379_6%2CE_236711_5%2C24_2394_8%2C23_13630_8%2C21_13505_8%2C20_12983_8&supernodes=%5B%5B%22reverse%22%2C%224_7409_6%22%2C%228_1988_6%22%2C%224_15846_6%22%5D%2C%5B%22small%22%2C%2215_5617_2%22%2C%2214_11360_2%22%5D%2C%5B%22say+big+%2F+large%22%2C%2223_8683_8%22%2C%2221_10062_8%22%2C%2223_8488_8%22%5D%2C%5B%22Chinese%22%2C%2224_2394_8%22%2C%2222_11933_8%22%2C%2220_12983_8%22%2C%2221_13505_8%22%2C%2223_13630_8%22%5D%2C%5B%22Chinese-related+English+text%22%2C%221_10169_2%22%2C%2214_13476_2%22%5D%2C%5B%22size%22%2C%2218_9402_8%22%2C%222_2169_2%22%5D%5D&clickedId=27_235469_8"
supernodes_zh = extract_supernode_features(url_zh)
chinese_node = Supernode(
    "Chinese",
    features=supernodes_zh["Chinese"] + supernodes_zh["Chinese-related English text"],
    children=[],
)

ordered_nodes_fr = [[french_node, opposite_node, small_node], [say_big_node]]

prompt_en = 'The opposite of "small" is "'
prompt_fr = 'Le contraire de "petit" est "'
prompt_zh = '"小"的反义词是"'

small_big_graph = InterventionGraph(ordered_nodes=ordered_nodes_fr, prompt=prompt_fr)

# %%

"""
Then, we get the activations for these nodes, initialize them, and create a visualization
"""

logits_fr, activations_fr = model.get_activations(prompt_fr)

for node in [say_big_node, small_node, french_node, opposite_node]:
    small_big_graph.initialize_node(
        node, activations_fr
    )  # initialize each node, adding it to the graph and recording its default activation

logits_zh, activations_zh = model.get_activations(prompt_zh)
small_big_graph.initialize_node(chinese_node, activations_zh)

small_big_graph.set_node_activation_fractions(
    activations_fr
)  # set each node's current activation to a percent of its default activation (here always 100%)
create_graph_visualization(small_big_graph, get_top_outputs(logits_fr))

# %%

"""
We'll turn off the French supernode.

Turning off the French supernode resulted in English output! Notably, it had only minor effects on the "Say big" supernode; their effects seem to be independent.
"""
french_to_english_interventions = [Intervention(french_node, -2)]
supernode_intervention(small_big_graph, french_to_english_interventions)

# %%

"""
Now, let's try to change the language to another: we'll turn off the French supernode, and turn on the Chinese supernode.

As expected, the model'ss output post-intervention is identical to its original output on the Chinese example.
"""
french_to_chinese_interventions = [Intervention(french_node, -2), Intervention(chinese_node, 2)]
supernode_intervention(
    small_big_graph, french_to_chinese_interventions, replacements={french_node.name: chinese_node}
)

# %% What if we replace the "small" feature with a "big" feature?

url_fr_big_small = "https://www.neuronpedia.org/gemma-2-2b/graph?slug=gemma-big-small-fr&clerps=%5B%5D&pruningThreshold=0.65&clickedId=21_9082_8&pinnedIds=27_64986_8%2CE_21996_5%2C21_9082_8%2C15_5756_5%2C6_4362_5%2C3_2873_5%2C2_4298_5&supernodes=%5B%5B%22large+%2F+huge%22%2C%2215_5756_5%22%2C%226_4362_5%22%2C%223_2873_5%22%2C%222_4298_5%22%5D%5D"
supernodes_fr_big_small = extract_supernode_features(url_fr_big_small)
say_small_node = Supernode("Say small", features=[Feature(layer=21, pos=8, feature_idx=9082)])
big_node = Supernode(
    "big", features=supernodes_fr_big_small["large / huge"], children=[say_small_node]
)

prompt_fr_rev = 'Le contraire de "grand" est "'
logits_fr_rev, activations_fr_rev = model.get_activations(prompt_fr_rev)

for node in [say_small_node, big_node]:
    small_big_graph.initialize_node(
        node, activations_fr_rev
    )  # initialize each node, adding it to the graph and recording its default activation

# %%

"""
Replacing the "small" supernode with a "big" supernode causes the "Say big" supernode to shutoff, and a new "Say small" supernode to turn on! The model's output changes to "petit", or "small", in French.
"""

big_to_small_interventions = [Intervention(small_node, -2), Intervention(big_node, 2)]
supernode_intervention(
    small_big_graph,
    big_to_small_interventions,
    replacements={small_node.name: big_node, say_big_node.name: say_small_node},
)

# %%

url_fr_syn = "https://www.neuronpedia.org/gemma-2-2b/graph?slug=gemma-small-min-fr&clerps=%5B%5D&pruningThreshold=0.8&pinnedIds=27_64986_9%2C27_69658_9%2CE_64986_6%2C8_11850_3%2CE_14904_2%2C4_13762_3%2C6_10175_3%2C3_15891_3&supernodes=%5B%5B%22synonymy%22%2C%223_15891_3%22%2C%228_11850_3%22%2C%224_13762_3%22%2C%226_10175_3%22%5D%5D&clickedId=5_13985_3"
supernodes_fr_syn = extract_supernode_features(url_fr_syn)
say_small_node2 = Supernode("say small", features=[Feature(layer=21, pos=8, feature_idx=9082)])
synonym_node = Supernode(
    "synonym", features=supernodes_fr_syn["synonymy"], children=[say_small_node2]
)

prompt_fr_syn = 'Un synonyme de "petit" est "'
logits_fr_syn, activations_fr_syn = model.get_activations(prompt_fr_syn)
print('Top outputs for Un synonyme de "petit" est ": ', get_top_outputs(logits_fr_syn))

small_big_graph.initialize_node(
    synonym_node, activations_fr_syn
)  # initialize each node, adding it to the graph and recording its default activation
synonym_node.features = [
    Feature(layer=f.layer, pos=f.pos - 1, feature_idx=f.feature_idx) for f in synonym_node.features
]

# %%

"""
Why `Feature(pos=f.pos - 1, ...)`
It's a token position alignment fix. The synonym features were extracted from the prompt: 

`'Un synonyme de "petit" est "'`

But the intervention run on the `small_big_graph`, which uses:

`'Le contraire de "petit" est "'`

These two prompts tokenize to different lengths. The synonym prompt has one extra token before the position where the "synonymy" features fire (likely because "synonyme" tokenizes into more subword tokens than "contraire"). So the synonym features from the URL have pos=3, but in the French prompt the equivalent position is pos=2.

The `f.pos - 1` shifts the position to align with the French prompt's tokenization, so the intervention targets the correct token position when running on `'Le contraire de "petit" est "'`.
"""

tokens = model.tokenizer.tokenize(prompt_fr_syn)
print("Tokenized prompt_fr_syn: ", tokens)
print(model.tokenizer.convert_tokens_to_ids(tokens))

tokens = model.tokenizer.tokenize(small_big_graph.prompt)
print("Tokenized small_big_graph.prompt: ", tokens)
print(model.tokenizer.convert_tokens_to_ids(tokens))

# %%

"""
We'll try one last intervention - can we replace the "opposite" supernode with a "synonym" supernode, to obtain a synonymous output? Our model is not very good at synonymy; given "Un synonyme de "petit" est ", it repeats "petit", rather than another synonym. But we can still see if this intervention reproduces that behavior.

Unfortunately, this intervention doesn't work! Though the "Say small" supernode turns on, the "Say big" supernode stays on too, and the model's outputs don't change. This is not very surprising - if we look at the original [circuit](https://www.neuronpedia.org/gemma-2-2b/graph?slug=gemma-small-big-fr&clerps=%5B%5D&pruningThreshold=0.65&pinnedIds=27_21996_8%2CE_64986_5%2C24_16045_8%2C19_5058_8%2C21_10062_8%2C23_2592_8%2C20_1454_8%2CE_63265_2%2C23_8683_8%2C23_8488_8%2C20_11434_8%2C19_5802_8%2CE_1455_7%2C15_5617_5%2C18_9402_8%2C6_4362_5%2C14_11360_5%2C3_2908_5%2C2_5452_5%2C3_6627_5%2C6_16184_2%2C4_95_2%2C22_10566_8%2C21_1144_8%2CE_2025_1%2CE_581_3&supernodes=%5B%5B%22opposite%22%2C%226_16184_2%22%2C%224_95_2%22%5D%2C%5B%22say+big+%2F+large%22%2C%2223_8683_8%22%2C%2223_8488_8%22%2C%2221_10062_8%22%5D%2C%5B%22too%22%2C%2219_5058_8%22%2C%2224_16045_8%22%2C%2220_11434_8%22%5D%2C%5B%22small%22%2C%2215_5617_5%22%2C%2214_11360_5%22%2C%223_6627_5%22%2C%223_2908_5%22%2C%222_5452_5%22%5D%2C%5B%22size%22%2C%2218_9402_8%22%2C%226_4362_5%22%5D%2C%5B%22French%22%2C%2221_1144_8%22%2C%2222_10566_8%22%2C%2220_1454_8%22%2C%2223_2592_8%22%2C%2219_5802_8%22%5D%5D&clickedId=22_10566_8) for the task, we see that the "opposite" supernode has only weak connections to the output. As a result, its causal effect is rather low, even though it would make sense for it to play a role.
"""
antonym_to_synonym_interventions = [Intervention(opposite_node, -2), Intervention(synonym_node, 2)]
supernode_intervention(
    small_big_graph,
    antonym_to_synonym_interventions,
    replacements={opposite_node.name: synonym_node, say_big_node.name: say_small_node},
)

# %%