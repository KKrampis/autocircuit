# Example 1: "DNA stands for deoxyribonucleic"

## Overview

This directory contains a complete circuit analysis for the prompt:
**"<bos>DNA stands for deoxyribonucleic"**

**Model:** gemma-2-2b
**Circuit Size:** 1,193 nodes, 35,075 edges
**Task:** Predict completion token "bonucleic" at position 6

---

## Files

### Graph Information
- **`graph_info.txt`** - Complete metadata about the graph including:
  - API endpoints and download commands
  - Prompt and token information
  - Generation settings and thresholds
  - Creator and tool information

### Analysis Documents
1. **`CIRCUIT_ANALYSIS_COMPLETE.md`** - **START HERE**
   - Executive summary of all findings
   - Answers to three key questions about the circuit
   - Feature hypotheses and validation strategy
   - Recommended as entry point for understanding the analysis

2. **`circuit_description.md`** - Detailed technical analysis
   - Complete circuit flow breakdown
   - Information flow pathways with weights
   - Token-level routing patterns
   - Phase-by-phase computational strategy

3. **`feature_hypotheses.md`** - Comprehensive hypothesis document
   - 6 categories of predicted feature types
   - Expected activation patterns
   - Testable predictions for each category
   - Counter-hypotheses (what we shouldn't find)
   - Validation methodology

4. **`hypothesis_features_summary.txt`** - Quick reference guide
   - Key features sampled for each hypothesis
   - Feature IDs with influence and activation scores
   - Neuronpedia lookup URLs
   - Expected vs. unexpected findings

---

## Key Findings

### Circuit Architecture
The model uses a **hierarchical target-focused circuit** with 6 computational phases:

1. **Distributed Token Analysis** (L0-L1)
   - Process each token independently
   - Extract domain (scientific), structure (definition), morphology (prefix)

2. **Context Integration** (L2-L5)
   - Build "DNA stands for" definitional frame
   - Recognize "deoxy + ri" chemical pattern

3. **Target-Focused Routing** (L6-L15)
   - 80% of features shift to target position C6
   - Route information: DNA → target, "for" → target, "deoxy" → target

4. **Decision Bottleneck** (L16-L21)
   - Only 7-19 features per layer (highly selective)
   - High influence scores (0.43-0.78)
   - Crystallize "bonucleic" prediction

5. **Dense Output Module** (L22-L25)
   - Tightly connected 4-layer network
   - Highest inter-layer weights in entire circuit
   - Combines: "DNA" + "definition" + "deoxy-" prefix

6. **Final Prediction** (L27)
   - Output logit 6898 = "bonucleic"
   - 1,192 incoming edges from entire circuit

### Information Flow Patterns

**Top 5 Flows by Total Weight:**
1. Embeddings → L0: 2,755 weight
2. L23 → L25: 1,897 weight (highest layer-to-layer!)
3. L23 → L24: 1,623 weight
4. L24 → L25: 1,420 weight
5. L0 → L23: 985 weight (skip connection)

**Token-Level Routing:**
- C6 → C6: 17,028 edges (self-processing)
- C1 (DNA) → C6: 2,565 edges
- C3 (for) → C6: 2,241 edges
- C4 (deoxy) → C6: 1,602 edges

### Critical Insight: Skip Connections

Layer 0 directly connects to layers 22-25, bypassing middle layers:
- L0 → L23: 1,148 edges
- L0 → L22: 891 edges
- L0 → L25: 658 edges

This preserves early token-level features for final decision-making.

---

## Feature Hypotheses

We predict **6 categories of features** active in this circuit:

### 1. Domain/Topic Features (L0-L10)
**Predicted:** Scientific/biology domain detectors
**Sample Features:** 122500377, 63545, 130969019
**Expected activations:** DNA, RNA, ATP, enzyme names

### 2. Syntactic/Structural Features (L1-L5)
**Predicted:** Definitional structure detectors
**Sample Features:** 38084626, 59759775, 1745643
**Expected activations:** "stands for", "means", "refers to"

### 3. Morphological/Prefix Features (L6-L10)
**Predicted:** Chemical prefix processors
**Sample Features:** 114587083, 93413938, 2946370
**Expected activations:** "deoxy-", "deoxyribose", "deoxygenated"

### 4. Token Prediction Features (L20-L27)
**Predicted:** Specific token boosters
**Sample Features:** 11250370 (activation: 272.29!)
**Expected activations:** "bonucleic", "ribonucleic acid"

### 5. Information Routing Features (L5-L20)
**Predicted:** Cross-position information movers
**Observable:** 2,565 edges C1→C6, 1,602 edges C4→C6
**Expected:** Act as "memory" carrying context to target

### 6. Integration/Decision Features (L22-L25)
**Predicted:** Multi-evidence combiners
**Sample Features:** 22194429 (in-degree: 610!), 16753342 (475), 17650687 (380)
**Expected:** Combine DNA + definition + prefix contexts

---

## Validation Strategy

### Step 1: Feature Lookup ✅
Identify key features from each category (26 total features sampled)

### Step 2: Semantic Verification ⏳
For each feature, check on Neuronpedia:
```
https://neuronpedia.org/gemma-2-2b/gemmascope-transcoder-16k/{FEATURE_ID}
```

Verify:
- Do activation examples match predictions?
- Is the feature semantically interpretable?
- Does it serve the hypothesized role?

### Step 3: Calculate Confirmation Rate ⏳
```
Hypothesis Validation Score = Confirmed Features / Total Sampled
```

### Step 4: Document Findings ⏳
- Confirmed hypotheses
- Surprising discoveries
- Polysemantic features (serving multiple roles)

---

## How to Reproduce

### 1. Download Graph Data

```bash
# Get metadata
curl -X GET "https://www.neuronpedia.org/api/graph/gemma-2-2b/dnastandsfordeox-1767880345293" \
  -H "x-api-key: sk-np-xM8SydJfvJjlyFg7hZPEPpqWB3Bcqpx8O0mIM4P5BmQ0"

# Download full graph
curl -s -X GET "https://neuronpedia-attrib.s3.us-east-1.amazonaws.com/user-graphs/cm7zchuzj0000k39abdgecnhp/dnastandsfordeox-1767880345293.json" \
  -o graph_data.json
```

### 2. Run Analysis Scripts

```bash
# From autocircuit/graph-analysis/ directory:

# Basic circuit analysis
python circuit_analysis.py

# Hub node identification
python analyze_hubs.py

# Feature sampling for validation
python validate_hypotheses.py example1/graph_data.json
```

### 3. Explore Results

Start with `CIRCUIT_ANALYSIS_COMPLETE.md` for the executive summary, then dive into specific documents based on your interests:
- Circuit flow details → `circuit_description.md`
- Feature predictions → `feature_hypotheses.md`
- Quick reference → `hypothesis_features_summary.txt`

---

## Research Questions

This example helps address:

1. **How do language models decompose complex tasks?**
   - Answer: Hierarchical processing with distinct computational phases

2. **What role do skip connections play?**
   - Answer: Preserve early features for late-stage integration

3. **How does information route across token positions?**
   - Answer: Progressive concentration toward target ("funnel architecture")

4. **What features are active at different depths?**
   - Answer: Early=domain/syntax, Middle=routing/morphology, Late=integration/prediction

5. **How predictable are feature semantics from circuit structure?**
   - Answer: Testable through Neuronpedia validation (in progress)

---

## Next Steps

- [ ] Validate sampled features on Neuronpedia
- [ ] Calculate hypothesis confirmation rates
- [ ] Document unexpected findings
- [ ] Compare with other scientific prompts
- [ ] Visualize circuit flow diagrams
- [ ] Write up findings for publication

---

## Acknowledgments

- **Graph Generator:** circuit-tracer by Hanna & Piotrowski
- **Platform:** Neuronpedia (neuronpedia.org)
- **Model:** gemma-2-2b by Google DeepMind
- **Features:** GemmaScope transcoders (16k features)

---

## Questions or Issues?

For questions about this analysis, please open an issue in the repository:
https://github.com/KKrampis/autocircuit/issues
