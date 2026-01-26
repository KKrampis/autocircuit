# Graph Analysis Tools

This directory contains tools for analyzing neural network circuits from Neuronpedia graph data.

## Overview

These scripts help analyze computational circuits by:
- Identifying information flow pathways
- Grouping features into functional supernodes
- Finding hub nodes and bottlenecks
- Generating hypotheses about feature semantics
- Preparing features for validation

## Scripts

### `circuit_analysis.py`

Comprehensive circuit analysis script that:
- Groups features into supernodes by (layer, context_position)
- Analyzes layer-to-layer information flows
- Identifies token-level flow patterns
- Generates statistics about circuit structure

**Usage:**
```bash
python circuit_analysis.py
```

**Requirements:**
- Graph data saved as `/tmp/neuronpedia_graph_data.json`

**Output:**
- Supernode structure with feature counts and influence scores
- Top 30 layer-to-layer flows by total edge weight
- Token-to-token flow patterns with edge counts

---

### `analyze_hubs.py`

Identifies hub nodes (high-degree nodes) in the circuit.

**Usage:**
```bash
python analyze_hubs.py
```

**Requirements:**
- Graph data saved as `/tmp/neuronpedia_graph_data.json`

**Output:**
- Top 20 nodes by total degree (in + out)
- Top 20 nodes by weighted in-degree
- Top 20 nodes by weighted out-degree
- Layer and context position information

---

### `validate_hypotheses.py`

Samples key features from different computational phases for hypothesis validation.

**Usage:**
```bash
python validate_hypotheses.py <path_to_graph_data.json>
```

**Example:**
```bash
python validate_hypotheses.py example1/graph_data.json
```

**Output:**
- Sampled features for each hypothesis category:
  1. Domain/Topic features (early layers)
  2. Syntactic/Structural features (definitional patterns)
  3. Morphological/Prefix features (morpheme processing)
  4. Integration Hub features (evidence combination)
  5. Token-Specific features (output boosting)
- Feature IDs ready for Neuronpedia lookup

---

## Example Analyses

### Example 1: "DNA stands for deoxyribonucleic"

**Location:** `example1/`

**Task:** Predict completion of scientific definition

**Key Findings:**
- Hierarchical target-focused circuit with 6 phases
- Strong skip connections from L0 to L22-L25
- Dense decision module in layers 22-25
- Progressive concentration toward target token

**Files:**
- `graph_info.txt` - Graph metadata and API information
- `circuit_description.md` - Detailed flow analysis
- `feature_hypotheses.md` - Predicted feature semantics
- `hypothesis_features_summary.txt` - Key features to validate
- `CIRCUIT_ANALYSIS_COMPLETE.md` - Executive summary

---

## Workflow

### 1. Download Graph Data

```bash
# Get graph metadata
curl -X GET "https://www.neuronpedia.org/api/graph/{MODEL}/{SLUG}"

# Download full graph data
curl -s -X GET "{url}" -o ./tmp/graphs/model={model_Id}__slug={slug}.json
```

### 2. Run Circuit Analysis

```bash
# Analyze overall circuit structure
python -m graph_analysis.circuit_analysis --graph_file {graph_file}

# Identify hub nodes
python -m graph_analysis.analyze_hubs --graph_file {graph_file}

# Sample features for validation

# Hypothesis Name: Domain/Topic Features
# Description: Scientific/biology domain context detectors
# Location: L0-L2, Context position 1
# Metric: Influence
python -m graph_analysis.top_n_nodes --graph_file {graph_file} --layer_ctx 0,1 1,1 2,1 -top_n 5 --metric influence

# Hypothesis Name: Syntatic/Structural Features
# Description: Definitional structure detectors ('X stands for Y')
# Location: L1-L3, Context position 2-3
# Metric: Influence
python -m graph_analysis.top_n_nodes --graph_file {graph_file} --layer_ctx 1,2 2,2 -top_n 3 --metric influence
python -m graph_analysis.top_n_nodes --graph_file {graph_file} --layer_ctx 2,3 3,3 -top_n 3 --metric influence

# Hypothesis Name: Morphological Features
# Description: Chemical prefix detectors ('deoxy-')
# Location: L6-L10, Context position 4
# Metric: Influence
python -m graph_analysis.top_n_nodes --graph_file {graph_file} --layer_ctx 6,4 7,4 8,4 9,4 10,4 -top_n 5 --metric influence

# Hypothesis Name: Integration Hub Features
# Description: High in-degree nodes combining multiple evidence sources
# Location: L23, Context position 6
# Metric: In-Degree
python -m graph_analysis.top_n_nodes --graph_file {graph_file} --layer_ctx 23,6 -top_n 5 --metric in_degree

# Hypothesis Name: Token-Specific Boosting Features
# Description: Features specifically boosting output token
# Location: L25, Context position 6
# Metric: Weight
python -m graph_analysis.top_n_nodes --graph_file {graph_file} --layer_ctx 25,6 -top_n 5 --metric weight

python -m graph_analysis.do_subgraph_save --graph_file {graph_file} --subgraph_name {subgraph_name} --send --api_key {api_key} -s {supernode1} -s {supernode2} --extra_pinned_ids {extra_pinned_ids}
```

`graph_analysis.do_subgraph_save` Note:
- `-s` or `--supernode` Define one supernode per -s. First item is the supernode LABEL, followed by node IDs (space-separated). Can be repeated to add multiple supernodes. Example: -s 'LabelA' node1 node2 -s 'LabelB' node3
- `--extra_pinned_ids` List of node IDs to pin that DO NOT belong to any supernode (space-separated). These are additional standalone pinned nodes. Example: --extra_pinned_ids nodeX nodeY

### 3. Validate Hypotheses

For each sampled feature:
1. Look up on Neuronpedia: `https://neuronpedia.org/{MODEL}/{SOURCE}/{FEATURE_ID}`
2. Check if activation patterns match predictions
3. Document semantic interpretation
4. Calculate confirmation rate

To Do: Look up on Neuronpedia is broken: (1) what is the source value?, (2) should use a python file and only retrieve the relevant information.

---

## Analysis Methodology

### Supernode Grouping

Features are grouped by **(Layer, Context Position)** to create interpretable supernodes:

```python
supernode_id = (layer, context_position)
# Example: (0, 1) = Layer 0, Token position 1
```

**Why this works:**
- Layer indicates computational depth
- Context position shows which token is being processed
- Creates natural functional groups

### Information Flow Analysis

Layer-to-layer transitions are analyzed by:
1. Counting edges between layer pairs
2. Summing absolute edge weights
3. Identifying highest-flow pathways
4. Tracking cross-token connections

### Hub Node Identification

Hub nodes are identified by:
- **In-degree:** Number of incoming edges
- **Out-degree:** Number of outgoing edges
- **Weighted degree:** Sum of absolute edge weights
- High-degree nodes often serve as integration points

### Feature Hypothesis Generation

Based on circuit structure and task, we predict:
1. **Domain features** (early layers) - topic/context detection
2. **Structural features** (early layers) - syntactic patterns
3. **Morphological features** (middle layers) - prefix/suffix processing
4. **Routing features** (middle layers) - cross-position information flow
5. **Integration features** (late layers) - evidence combination
6. **Token features** (final layers) - specific token boosting

---

## Citation

If using these tools, please cite:

```
Circuit Analysis Tools for Neuronpedia Graphs
Repository: https://github.com/KKrampis/autocircuit
```

---

## Dependencies

- Python 3.7+
- Standard library only (json, collections, statistics)

---

## Contributing

To add new analysis scripts:
1. Follow the existing script structure
2. Document usage and output format
3. Add example to this README
4. Create new example directory if needed

---

## Future Work

- Automated feature interpretation lookup
- Visualization tools (circuit diagrams)
- Comparative analysis across prompts
- Batch processing for multiple graphs
- Integration with existing circuit analysis tools
