# %%

from pathlib import Path
import torch

from circuit_tracer import ReplacementModel, attribute
from circuit_tracer.utils import create_graph_files
from circuit_tracer.frontend.local_server import serve
from circuit_tracer.graph import prune_graph

import os

from IPython import get_ipython
if get_ipython() is not None:
    from IPython.display import display, IFrame

# %%

repo_dir = Path(__file__).resolve().parents[1]

# %%

"""
First, load your model and transcoders by name. `model_name` is a normal HuggingFace / TransformerLens model name; we'll use `google/gemma-2-2b`. We set the `transcoder_name` to `gemma`, which is shorthand for the [Gemma Scope](https://arxiv.org/abs/2408.05147) transcoders; we take the transcoders with lowest L0 (mean # of acive features) for each layer.

We additionally support model_name = "meta-llama/Llama-3.2-1B", with "llama" transcoders; these are ReLU skip-transcoders that we trained, available [here](https://huggingface.co/mntss/skip-transcoder-Llama-3.2-1B-131k-nobos/tree/new-training)

If you want to use other models, you'll have to provide your own transcoders. To do this, set `transcoder_name` to point to your own configuration file, specifying the list of transcoders that you want to use. You can see `circuit_tracer/configs` for example configs.
"""

model_name = "google/gemma-2-2b"
transcoder_name = "gemma"
backend = 'transformerlens'  # change to 'nnsight' for the nnsight backend!
model = ReplacementModel.from_pretrained(
    model_name, transcoder_name, dtype=torch.bfloat16, backend=backend
)

# %%

"""
Next, set your attribution arguments.
"""
prompt = "The capital of state containing Dallas is"  # What you want to get the graph for
max_n_logits = 10  # How many logits to attribute from, max. We attribute to min(max_n_logits, n_logits_to_reach_desired_log_prob); see below for the latter
desired_logit_prob = 0.95  # Attribution will attribute from the minimum number of logits needed to reach this probability mass (or max_n_logits, whichever is lower)
max_feature_nodes = 8192  # Only attribute from this number of feature nodes, max. Lower is faster, but you will lose more of the graph. None means no limit.
batch_size = 256  # Batch size when attributing
offload = "cpu"  # Offload various parts of the model during attribution to save memory. Can be 'disk', 'cpu', or None (keep on GPU)
verbose = True  # Whether to display a tqdm progress bar and timing report

# %%

"""
Then, just run attribution
"""
graph = attribute(
    prompt=prompt,
    model=model,
    max_n_logits=max_n_logits,
    desired_logit_prob=desired_logit_prob,
    batch_size=batch_size,
    max_feature_nodes=max_feature_nodes,
    offload=offload,
    verbose=verbose,
)

# %%

"""
We now have a graph object! We can save it as a .pt file, but be warned that it's large (~167MB).
"""
graph_dir = repo_dir / ".tmp" / "graphs"
os.makedirs(graph_dir, exist_ok=True)
graph_name = "example_graph.pt"
graph_dir = Path(graph_dir)
graph_dir.mkdir(exist_ok=True)
graph_path = graph_dir / graph_name

graph.to_pt(graph_path)

# %%

"""
Given this object, we can create the graph files that we need to visualize the graph. Give it a slug (name), and set the node / edge thresholds for pruning. Pruning removes unimportant nodes and edges from your graph; lower thresholds (i.e., more aggresive pruning) results in smaller graphs. These may be easier to interpret, but explain less of the model's behavior.
"""

slug = "dallas-austin"  # this is the name that you assign to the graph
graph_file_dir = repo_dir / ".tmp" / "graph_files"  # where to write the graph files. no need to make this one; create_graph_files does that for you
node_threshold = 0.8  # keep only the minimum # of nodes whose cumulative influence is >= 0.8
edge_threshold = 0.98  # keep only the minimum # of edges whose cumulative influence is >= 0.98

create_graph_files(
    graph_or_path=graph_path,  # the graph to create files for
    slug=slug,
    output_path=graph_file_dir,
    node_threshold=node_threshold,
    edge_threshold=edge_threshold,
)

# %%

"""
Now, you can visualize the graph using the following commands! This will spin up a local server to act as the frontend.

If you're running this notebook on a remote server, make sure that you set up port forwarding, so that the chosen port is accessible on your local machine too.

You can select nodes by clicking on them. Ctrl/Cmd+Click on nodes to pin and unpin them to your subgraph. G+Click on nodes in the subgraph to group them together into a supernode; G+Click on the X next to a supernode to dissolve it. Click on the edit button to edit node descriptions, and click on supernode description to edit that.
"""

port = 8888
server = serve(data_dir=graph_file_dir, port=port)

# %%

print(f"Use the IFrame below, or open your graph here: http://localhost:{port}/index.html")
if get_ipython() is not None:
    display(IFrame(src=f'http://localhost:{port}/index.html', width='100%', height='800px'))

# %%

"""
Once you're done, you can stop the server with the following command.
"""

# server.stop()

# %% Graph

"""
Earlier, you created a graph object. Its adjacency matrix / edge weights are stored in `graph.adjacency_matrix` in a dense format, rows are target nodes and columns are source nodes. The first `len(graph.real_features)` entries of the matrix represent features; the `i`th entry corresponds to the `i`th feature in `graph.real_features`, given in `(layer, position, feature_idx)` format. The next `graph.cfg.n_layers * graph.n_pos` entries are error_nodes. The next `graph.n_pos` entries are token nodes. The final `len(graph.logit_tokens)` entries are logit nodes.

The value of the cell `graph.adjacency_matrix[target, source]` is the direct effect of the source on the target node. That is, it tells you how much the target node's value would change if the source node were set to 0, while holding the attention patterns, layernorm denominators, and other feature activations constant. Thus, if the target node is a feature, this tells you how much the target feature would change; if the target node is a logit, this tells you how much the (de-meaned) value of the logit would change.

Note that `gemma-2-2b` is a model (family) that uses logit softcapping. This means that a softcap function, `softcap(x) = t * tanh(x/t)` is used to constrain the logits to fall within (-t, t); `gemma-2-2b` uses `t=30`. For such models, we preidct the change in logits pre-softcap, as the nonlinearity introduced by softcapping would cause our attribution to yield incorrect / approximate direct effect values.
"""

# %% Pruning

"""
Given a graph, you might want to prune it, as it will otherwise contain many low-impact nodes and edges that clutter the circuit diagram while adding little information. We enable you to prune nodes by absolute influence, i.e. the total impact that the nodes have on the logits, direct, and indirect. The default threshold is 0.8: this means we will keep the minimum number of nodes required to capture 80% of all logit effects. Similarly, the `edge_threshold`, by default 0.98, means that we will keep the minimum number of edges required to capture 98% of all logits effects.
"""

prune_graph(graph, node_threshold=0.8, edge_threshold=0.98)

# %%