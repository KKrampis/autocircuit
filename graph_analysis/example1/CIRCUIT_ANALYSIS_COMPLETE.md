# Complete Circuit Analysis: "DNA stands for deoxyribonucleic"

## Executive Summary

We analyzed the Neuronpedia graph for gemma-2-2b processing the prompt "DNA stands for deoxyribonucleic" and discovered a **hierarchical target-focused circuit** with clear computational stages and testable feature hypotheses.

**Circuit Statistics:**
- 1,193 nodes (features), 35,075 edges (connections)
- 27 layers + embeddings
- 7 context positions (tokens 0-6)

---

## Three Key Questions Answered

### Q1: How to Group Features into Supernodes?

**Answer:** Group by **(Layer, Context Position)** pairs

**Supernode Structure (88 total):**

| Layer Range | Feature Distribution | Computational Role |
|-------------|---------------------|-------------------|
| **L0-L5** | 335+ features, spread across all tokens | Parallel token analysis |
| **L6-L15** | 20-60 features, shifting toward C6 | Target-focused routing |
| **L16-L21** | 7-19 features, exclusively C6 | High-confidence bottleneck |
| **L22-L25** | 15-30 features per layer, C6 only | Dense decision module |
| **L27** | 1 output node | Final logit prediction |

**Key Pattern:** Progressive concentration toward target position (C6 - "bonucleic")

---

### Q2: What are the Main Information Flows?

**Answer:** Five major pathways with distinct functions

#### **Flow 1: Embeddings → Layer 0** (2,755 total weight)
- Target embedding (bonucleic) has HIGHEST output: 2,766
- DNA embedding: 2,043
- All tokens feed into early processing

#### **Flow 2: Layer 0 → Early Layers** (Parallel processing)
- L0 → L1: 1,907 edges
- L0 → L2: 735 edges
- Distributed token-level feature extraction

#### **Flow 3: Skip Connections: L0 → L22-L25** (2,700+ weight)
- L0 → L23: 1,148 edges (985 weight)
- L0 → L22/L24/L25: Similar patterns
- Preserve early features for final decision

#### **Flow 4: Late Layer Cascade** (HIGHEST weights)
- **L23 → L25: 1,897** (strongest flow!)
- **L23 → L24: 1,623**
- **L24 → L25: 1,420**
- Dense 4-layer decision network

#### **Flow 5: All → Output Logit 27_6898_6**
- 1,192 incoming edges from entire circuit
- Weighted integration of all evidence

**Token-Level Flow Pattern:**
```
C6 → C6: 17,028 edges (heavy self-processing)
C1 (DNA) → C6: 2,565 edges (subject to target)
C3 (for) → C6: 2,241 edges (preposition to target)
C4 (deoxy) → C6: 1,602 edges (prefix to target)
```

---

### Q3: What High-Level Circuit Does the Model Use?

**Answer:** **6-Phase Hierarchical Target-Focused Circuit**

```
┌─────────────────────────────────────────────────┐
│ Phase 1: Distributed Token Analysis (L0-L1)    │
│ - Process each token independently              │
│ - Extract: DNA (scientific) + "stands for"     │
│   (definition) + "deoxy" (prefix)               │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│ Phase 2: Context Integration (L2-L5)           │
│ - Build: "DNA stands for" = definitional frame │
│ - Recognize: "deoxy + ri" = chemical pattern   │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│ Phase 3: Target-Focused Routing (L6-L15)       │
│ - 80% features shift to C6 (target position)   │
│ - Route: DNA → target, "for" → target,         │
│   "deoxy" → target                              │
│ - Skip connections: L0 → L22-L25               │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│ Phase 4: Decision Bottleneck (L16-L21)         │
│ - Only 7-19 features (highly selective)        │
│ - High influence: 0.43-0.78                    │
│ - Crystallize: "bonucleic" prediction          │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│ Phase 5: Dense Output Module (L22-L25)         │
│ - Tightly connected 4-layer network            │
│ - Combine: "DNA" + "definition" + "deoxy-"     │
│ - Transform to token logit                     │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│ Phase 6: Final Prediction (L27)                │
│ - Output: Logit 6898 = "bonucleic"             │
└─────────────────────────────────────────────────┘
```

**Key Computational Principles:**
1. **Hierarchical Processing:** Early=distributed, Late=integrated
2. **Skip Connections:** L0 directly feeds L22-L25
3. **Target-Focused Funnel:** Progressive routing to position C6
4. **Dense Decision Module:** L22-L25 highest inter-layer weights
5. **Multi-Evidence Integration:** DNA + definition + prefix → output

---

## Feature Hypotheses

Based on the circuit structure and task, we predict **6 categories of features**:

### 1. **Domain/Topic Features** (L0-L10, C1-C6)
**Expected semantics:** Scientific, biology, chemistry domain detectors

**Key features to validate:**
- Feature 122500377 (L0_C1): Inf 0.796
- Feature 63545 (L0_C1): Inf 0.796
- Feature 130969019 (L0_C1): Inf 0.788

**Prediction:** Should activate on DNA, RNA, ATP, enzyme names

---

### 2. **Syntactic/Structural Features** (L1-L5, C2-C3)
**Expected semantics:** Definitional structure detectors ("X stands for Y")

**Key features to validate:**
- Feature 38084626 (L1_C2): Inf 0.789
- Feature 59759775 (L2_C3): Inf 0.797
- Feature 1745643 (L2_C3): Inf 0.783

**Prediction:** Should activate on "means", "refers to", "is called"

---

### 3. **Morphological/Prefix Features** (L6-L10, C4)
**Expected semantics:** Chemical prefix detectors ("deoxy-")

**Key features to validate:**
- Feature 114587083 (L7_C4): Inf 0.793, Act 6.27
- Feature 93413938 (L7_C4): Inf 0.776, Act 7.42
- Feature 2946370 (L7_C4): Inf 0.742, Act 12.13

**Prediction:** Should activate on "deoxyribose", "deoxygenated", chemical prefixes

---

### 4. **Token Prediction Features** (L20-L27, C6)
**Expected semantics:** Specific token boosters ("bonucleic")

**Key features to validate:**
- Feature 11250370 (L25_C6): Edge weight 0.865 to output, Act 272.29

**Prediction:** Should activate specifically on "bonucleic", "ribonucleic acid"

---

### 5. **Information Routing Features** (L5-L20, Cross-position)
**Expected semantics:** Cross-token information movers

**Flow patterns:**
- C1 (DNA) → C6: 2,565 edges
- C4 (deoxy) → C6: 1,602 edges

**Prediction:** Should act as "memory" carrying context to target position

---

### 6. **Integration/Decision Features** (L22-L25, C6)
**Expected semantics:** Multi-evidence combiners

**Key hub features:**
- Feature 22194429 (L23_C6): In-degree 610, Inf 0.271
- Feature 16753342 (L23_C6): In-degree 475, Inf 0.303
- Feature 17650687 (L23_C6): In-degree 380, Inf 0.319

**Prediction:** Should combine DNA + definition + prefix contexts

---

## Validation Strategy

### Step 1: Sample Key Features (DONE)
✅ Identified 26 key features across all hypotheses
✅ Grouped by computational role and circuit position

### Step 2: Feature Lookup (TODO)
For each feature, visit:
```
https://neuronpedia.org/gemma-2-2b/gemmascope-transcoder-16k/{FEATURE_ID}
```

Check:
- Top activating examples match hypothesis?
- Activation distribution (narrow vs. broad)?
- Semantic interpretation aligns with predicted role?

### Step 3: Calculate Validation Metrics
```
Hypothesis Confirmation Rate = Confirmed Features / Total Sampled
Surprise Discovery Rate = Unexpected Features / Total Sampled
Polysemanticity Rate = Multi-Role Features / Total Sampled
```

---

## Expected vs. Counter-Expected Findings

### SHOULD Find ✓
- Scientific domain features in L0-L5
- Definitional structure features at C2-C3
- Chemical prefix features in L6-L10 at C4
- Integration hubs in L23-L25 with high in-degree
- Token-specific features in L25 with strong output connections

### SHOULD NOT Find ✗
- Generic word frequency features in late layers
- Grammatical features (verb/noun) in L22-L25
- Unrelated domain features (sports, politics)
- Random or noise activation patterns

---

## Files Generated

| File | Description |
|------|-------------|
| `/tmp/neuronpedia_graph_data.json` | Full graph data (3.0 MB) |
| `/tmp/circuit_analysis.py` | Supernode analysis script |
| `/tmp/analyze_hubs.py` | Hub node identification |
| `/tmp/circuit_description.md` | Detailed circuit description |
| `/tmp/feature_hypotheses.md` | Complete hypothesis document |
| `/tmp/hypothesis_features_summary.txt` | Key features to validate |

---

## Next Steps

1. **Manual Feature Validation:** Look up sampled features on Neuronpedia
2. **Automated Validation:** Create script to batch-fetch feature descriptions
3. **Hypothesis Testing:** Calculate confirmation rates for each category
4. **Discovery Analysis:** Document unexpected findings
5. **Circuit Visualization:** Create flow diagrams for paper/presentation
6. **Integration:** Add this analysis methodology to autocircuit project

---

## Key Insights

1. **Skip Connections Matter:** L0 → L22-L25 bypass middle layers, preserving early features

2. **Target Embedding is Critical:** The target position embedding (bonucleic) has the HIGHEST weighted output (2,766), suggesting positional context is crucial

3. **Funnel Architecture:** Progressive concentration from distributed (L0) to focused (L25)

4. **Dense Decision Module:** L22-L25 form tightly coupled network with highest weights

5. **Multi-Evidence Integration:** Circuit combines domain, structure, morphology cues

6. **Hierarchical Computation:** Clear phase transitions visible in feature distributions

---

## Conclusion

The model uses a sophisticated **hierarchical target-focused circuit** that:
- Analyzes tokens in parallel (early layers)
- Routes information to target position (middle layers)
- Selects high-confidence features (bottleneck)
- Integrates multiple evidence sources (late layers)
- Predicts specific token (output)

This circuit structure supports the hypothesis that LLMs build compositional representations through staged processing, with clear functional specialization across layers and positions.

**Testable prediction:** Feature semantics should align with computational phases, validatable through Neuronpedia lookup.
