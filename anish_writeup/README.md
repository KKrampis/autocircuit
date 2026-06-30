# anish_writeup

Agent-driven circuit discovery on neural network attribution graphs. An LLM agent explores a precomputed attribution graph through hypothesis-driven search — inspecting nodes, tracing paths, forming and testing hypotheses — rather than exhaustive algorithmic pruning.

## Files

### `circuit_analysis_tools.py`

A CLI toolkit providing 18 tools for an LLM agent to explore Neuronpedia-format attribution graphs. The agent calls these tools iteratively to navigate the graph, building up an understanding of the circuit.

**Implemented tools** (graph-only, no GPU):
- `get_node_info` / `get_top_nodes` / `search_nodes` — find and inspect nodes
- `get_neighbors` — trace upstream/downstream connections from a node
- `find_paths` — find highest-attribution paths between two nodes (priority-queue BFS, max 4 hops)
- `get_subgraph` — extract local neighborhoods via BFS
- `note` / `get_notes` / `get_progress` — persistent agent notebook for recording findings

**Stubbed tools** (require TransformerLens/nnsight + GPU):
- `patch_node` / `patch_edge` / `ablate_nodes` — causal intervention tools
- `run_model` / `test_circuit_faithfulness` — model execution
- `get_attention_pattern` / `logit_lens` / `get_max_activating_examples` / `get_node_activation` — component inspection

#### Usage

```bash
# Single query
python circuit_analysis_tools.py --graph graph_data.json get_top_nodes --top_k 10

# Interactive REPL (for agent use)
echo 'get_top_nodes --top_k 5' | python circuit_analysis_tools.py --graph graph_data.json repl
```

### `agent_state.json`

Output from a run on **Gemma 2 2B** predicting "acid" after `<bos>DNA stands for deoxyribonucleic` (p=0.989). The graph has 1,191 nodes and 35,075 edges across 26 layers.

The agent inspected 227 of 1,191 nodes (~19%) over 54 tool calls. Here's the reasoning trajectory it followed:

#### Step 1: Identify the output and its direct contributors
The agent started at the output node (`27_6898_6`, the logit for "acid") and found 1,192 upstream edges. The top direct contributors were all at position 6 (the "bonucleic" token): features at L16 (w=1.72), L22 (w=1.31), L19 (w=1.14), L21 (w=1.02), L23 (w=0.93). This immediately told the agent the circuit lives almost entirely at one token position.

#### Step 2: Discover the hub
Tracing upstream from the strongest output contributor, the agent found `16_11463_6` (layer 16, position 6) is the critical hub. It has the strongest single edge to the output (1.72) and also feeds the L19 and L22 nodes with massive weights (24.4 and 9.1). Its dominant input is the "bonucleic" embedding (w=24.7).

#### Step 3: Form a hypothesis
The agent hypothesized that `16_11463_6` integrates the "bonucleic" embedding with residual stream information from layers 7–15, then broadcasts downstream through L19 and L22. It noticed negative weights from `<bos>` (w=-3.2) and "DNA" (w=-2.4) feeding into the hub — suggesting the hub actively suppresses signal in non-chemistry contexts.

#### Step 4: Verify paths
Path analysis confirmed that all high-attribution paths from the "bonucleic" embedding to the output pass through `16_11463_6` as a bottleneck. The hub also receives weak cross-position signals: "deoxy" at position 4 (w=2.4) and "stands" at position 2 (w=2.7).

#### Step 5: Find early-layer gating
The agent found `0_9026_6`, a layer-0 feature that reads all 7 token embeddings (bonucleic dominant at +22.2) and sends mostly negative weights to late-layer features (L22–L25). This acts as a broad context detector / suppressor gate.

#### Step 6: Map the cascade
The full backbone emerged: `bonucleic embedding → L16 hub → L19 → L21/L22 → L23 → output`. Each backbone node feeds the next AND connects directly to the output. The cascade structure was confirmed by in-degree rankings.

#### Step 7: Assess cross-position flow
The agent checked how much information flows between token positions. Answer: very little. The circuit is 90%+ position-6 processing. "DNA", "stands", "for", "deoxy" embeddings mostly stay at their own positions. The few cross-position paths all converge on the L16 hub.

#### Final interpretation
The model predicts "acid" primarily through a deep cascade at the "bonucleic" token position. The word "bonucleic" alone is a strong enough cue — the model barely needs the earlier context ("DNA stands for deoxy..."). The negative weights from non-target tokens at the hub suggest contextual suppression rather than contextual boosting.
