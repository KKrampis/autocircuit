# Feature Hypotheses for "DNA stands for deoxyribonucleic" Circuit

## Overview
Given the prompt structure and task, we can form testable hypotheses about what semantic features should be active in this circuit.

---

## Feature Categories We Expect to Find

### 1. **DOMAIN/TOPIC FEATURES** (Early-to-Middle Layers, Multiple Positions)

#### Hypothesis 1.1: Biology/Science Domain Features
**Expected to activate on:** C1 (DNA), C2 (stands), C6 (target)
**Expected layers:** L0-L10
**Feature behavior:**
- Should activate strongly on "DNA" token
- May activate on scientific prefixes like "deoxy"
- Help prime the model for scientific vocabulary in output

**Testable predictions:**
- Features should show activation on other scientific acronyms (RNA, ATP, etc.)
- Should have high influence scores (important for domain selection)
- May connect strongly to late-layer decision nodes

#### Hypothesis 1.2: Chemistry/Biochemistry Features
**Expected to activate on:** C4 (deoxy), C5 (ri), C6 (target)
**Expected layers:** L0-L8
**Feature behavior:**
- Recognize "deoxy" as chemical prefix (meaning "without oxygen")
- Activate on chemical compound names
- Support prediction of "-ribonucleic" completion

**Testable predictions:**
- Should activate on other chemical prefixes (hydroxy-, methyl-, etc.)
- May show connections to features detecting "-ic acid" suffixes
- Higher activation in later tokens (C4-C6) than earlier ones

---

### 2. **SYNTACTIC/STRUCTURAL FEATURES** (Early Layers, Specific Positions)

#### Hypothesis 2.1: Definitional Structure Features
**Expected to activate on:** C2 (stands), C3 (for)
**Expected layers:** L0-L5
**Feature behavior:**
- Detect "X stands for Y" pattern
- Recognize definitional/explanatory context
- Signal that what follows is an expansion/explanation

**Testable predictions:**
- Should activate on similar phrases: "means", "refers to", "represents"
- Strong connections from C2-C3 → C6 (routing definition to target)
- May suppress alternative interpretations (not action "stands", but definition)

#### Hypothesis 2.2: Acronym Expansion Features
**Expected to activate on:** C1 (DNA), C2-C3 (stands for), C6 (target)
**Expected layers:** L1-L10
**Feature behavior:**
- Recognize that DNA is an acronym (all caps, 3 letters)
- Expect expansion after "stands for"
- Prime for multi-word technical phrase

**Testable predictions:**
- Should activate on other acronyms (FBI, NASA, RNA)
- May check that following tokens form expansion (D→deoxy, N→nucleic, A→acid)
- Connects early layers (C1) to late layers (C6) via skip connections

---

### 3. **MORPHOLOGICAL/PREFIX FEATURES** (Middle Layers, Target Position)

#### Hypothesis 3.1: "deoxy-" Prefix Features
**Expected to activate on:** C4 (deoxy), C6 (target)
**Expected layers:** L4-L12
**Feature behavior:**
- Recognize "deoxy" as incomplete prefix
- Predict that continuation involves "-ribonucleic"
- May detect that "deoxy-" modifies a base term

**Testable predictions:**
- Should activate on other "deoxy-" compounds (deoxygenated, deoxythymidine)
- Strong flow from C4 → C6 (prefix routing to completion)
- May interact with features detecting "-nucleic" or "-acid" suffixes

#### Hypothesis 3.2: "-ribonucleic" Completion Features
**Expected to activate on:** C5 (ri), C6 (target)
**Expected layers:** L8-L25
**Feature behavior:**
- Recognize "ri" as start of "ribonucleic"
- Complete the chemical compound name
- Strongly boost "bonucleic" token in output

**Testable predictions:**
- Should have very high influence scores (critical for final prediction)
- Concentrated in late layers (L22-L25)
- May show activation on related terms: "ribose", "nucleic acid", "RNA"

---

### 4. **TOKEN PREDICTION FEATURES** (Late Layers, Target Position)

#### Hypothesis 4.1: "bonucleic" Token Boosting Features
**Expected to activate on:** C6 (target)
**Expected layers:** L20-L27
**Feature behavior:**
- Specifically encode/boost logit for "bonucleic" token
- Integrate all previous evidence
- Suppress alternative completions

**Testable predictions:**
- Should have highest influence scores in circuit
- Feed directly into output logit 27_6898_6
- May be very specific features (narrow activation distribution)

#### Hypothesis 4.2: Continuation/Completion Features
**Expected to activate on:** C5-C6
**Expected layers:** L15-L25
**Feature behavior:**
- Recognize partial word "ri" needs completion
- Detect that sentence/phrase is incomplete
- Signal expectation of specific technical term

**Testable predictions:**
- May activate on other incomplete scientific terms
- Should have connections to both C5 and C6 positions
- Higher activation when term is partially complete vs. at start

---

### 5. **INFORMATION ROUTING FEATURES** (All Layers, Variable Positions)

#### Hypothesis 5.1: Subject-to-Target Routing Features
**Expected flow:** C1 (DNA) → C6 (target)
**Expected layers:** L5-L20
**Feature behavior:**
- Move information about "DNA" to target position
- Maintain "what we're defining" context
- Enable integration: DNA = deoxy + ribonucleic + acid

**Testable predictions:**
- Should see 2,500+ edges from C1 → C6 (as observed)
- Middle-to-late layer features (L8-L18)
- May act as "memory" carrying subject through sentence

#### Hypothesis 5.2: Prefix-to-Target Routing Features
**Expected flow:** C4 (deoxy) → C6 (target)
**Expected layers:** L6-L18
**Feature behavior:**
- Route "deoxy" prefix to completion position
- Maintain incomplete morpheme information
- Combine with "ribonucleic" to form complete word

**Testable predictions:**
- Should see 1,600+ edges from C4 → C6 (as observed)
- May show activation on any incomplete prefix + completion task
- Stronger in middle layers (L8-L15) than early layers

---

### 6. **INTEGRATION/DECISION FEATURES** (Late Layers, Target Position)

#### Hypothesis 6.1: Multi-Evidence Integration Features
**Expected to activate on:** C6 (target)
**Expected layers:** L22-L25
**Feature behavior:**
- Combine multiple pieces of evidence:
  * Domain: scientific/chemical
  * Structure: definitional
  * Subject: DNA
  * Prefix: deoxy-
- Make final prediction: "bonucleic"

**Testable predictions:**
- Should be hub nodes with very high in-degree
- Located in L23-L25 supernodes (as observed)
- May activate on any complex multi-constraint prediction task
- Should have weights from diverse sources (all earlier positions)

#### Hypothesis 6.2: Confidence/Decision Features
**Expected to activate on:** C6 (target)
**Expected layers:** L16-L21 (bottleneck)
**Feature behavior:**
- High-confidence feature selection
- Suppress alternative interpretations
- Lock in "bonucleic" as the answer

**Testable predictions:**
- Very high influence scores (0.7+)
- Low feature count (7-19 per layer, as observed)
- May be suppressive (negative weights to alternative tokens)

---

## Expected Feature Distributions by Circuit Phase

### **Phase 1: Early Layers (L0-L5)**
```
Expected Feature Mix:
- 30% Domain/Topic features (science, chemistry, biology)
- 25% Syntactic/Structural features (definitional, acronym)
- 20% Token-level features (word identity, POS)
- 15% Morphological features (prefixes, roots)
- 10% Routing/Attention features (position tracking)
```

**Key Hypothesis:** Early layers should show diverse feature types with
broad semantic categories (domain, syntax) dominating.

### **Phase 2: Middle Layers (L6-L15)**
```
Expected Feature Mix:
- 35% Routing features (C1→C6, C4→C6, etc.)
- 25% Morphological features ("deoxy-" prefix processing)
- 20% Integration features (combining DNA + deoxy context)
- 15% Domain features (maintaining scientific context)
- 5% Syntactic features (less important in middle layers)
```

**Key Hypothesis:** Middle layers should emphasize information routing
and morphological processing (prefix handling).

### **Phase 3: Late Layers (L16-L25)**
```
Expected Feature Mix:
- 40% Token prediction features ("bonucleic" specific)
- 30% Integration features (multi-evidence combination)
- 20% Decision/Confidence features (suppression, selection)
- 10% Routing features (final connections to target)
```

**Key Hypothesis:** Late layers should be dominated by specific token
prediction and evidence integration features.

---

## Specific Testable Predictions

### Prediction 1: Scientific Domain Feature in Early Layers
**Feature profile:**
- Activates on: DNA, RNA, ATP, RNA, enzyme names
- Layer: L0-L2
- Position: C1 (subject tokens)
- High influence: 0.7+

**How to test:** Look up features in L0_C1 supernode, check activation patterns

### Prediction 2: Definitional Structure Feature
**Feature profile:**
- Activates on: "stands for", "means", "refers to", "is called"
- Layer: L1-L4
- Position: C2-C3
- Connections: Strong edges to C6 target position

**How to test:** Search L1-L4 features at C2-C3, check if they route to C6

### Prediction 3: "Deoxy-" Prefix Feature
**Feature profile:**
- Activates on: "deoxy", "deoxyribose", "deoxygenated"
- Layer: L6-L10
- Position: C4, C6
- Behavior: Predicts continuation with "-ribonucleic" type terms

**How to test:** Check L6-L10 features at C4, look for routing to C6

### Prediction 4: Late-Layer Integration Hub
**Feature profile:**
- Multiple high-weight incoming connections (100+ edges)
- Layer: L23
- Position: C6
- Influence: 0.5-0.7
- Behavior: Combines DNA + deoxy + definition context

**How to test:** Examine L23_C6 features with highest in-degree (already found: L23_10894_6, etc.)

### Prediction 5: "Bonucleic" Token-Specific Feature
**Feature profile:**
- Very specific: only activates on "bonucleic" or "ribonucleic"
- Layer: L25
- Position: C6
- Influence: 0.6+
- Direct connection to output logit

**How to test:** Check L25_C6 features with strongest edge weights to output logit

---

## Counter-Hypotheses (What We SHOULDN'T Find)

### Counter-Hypothesis 1: No Common Word Features in Late Layers
**Expectation:** Late layers (L20+) should NOT contain generic features
like "frequent word", "short word", "common token"

**Rationale:** Task requires specific scientific knowledge, not general statistics

### Counter-Hypothesis 2: No Grammatical Features in Decision Module
**Expectation:** L22-L25 should NOT contain features for grammar/syntax
like "verb", "noun", "past tense"

**Rationale:** By this phase, grammatical structure is resolved; only semantic
content and specific token prediction matter

### Counter-Hypothesis 3: No Unrelated Domain Features
**Expectation:** Should NOT find features for unrelated domains like
"sports", "politics", "food" with high activation

**Rationale:** Circuit should be specialized for scientific/chemical domain

---

## Validation Strategy

### Step 1: Sample High-Influence Features from Each Supernode
```
Sample features from:
- L0_C1 (expect: domain features)
- L1-L4_C2-C3 (expect: definitional features)
- L6-L10_C4 (expect: prefix features)
- L23-L25_C6 (expect: integration + token features)
```

### Step 2: Look Up Feature Interpretations via API
```bash
# For each sampled feature:
curl -X GET "https://www.neuronpedia.org/api/feature/gemma-2-2b/gemmascope-transcoder-16k/{FEATURE_ID}" \
  -H "x-api-key: sk-np-xM8SydJfvJjlyFg7hZPEPpqWB3Bcqpx8O0mIM4P5BmQ0"
```

### Step 3: Check Activation Patterns
- Do features activate on hypothesized token classes?
- Are they in expected layers?
- Do they have expected connection patterns?

### Step 4: Quantify Hypothesis Confirmation Rate
```
Confirmed hypotheses / Total hypotheses = Validation score
```

---

## Expected Findings Summary

**If our hypotheses are correct, we should find:**

1. ✓ Scientific domain features in early layers (L0-L5) at C1
2. ✓ Definitional structure features at C2-C3 with strong C6 connections
3. ✓ "Deoxy-" prefix features in middle layers (L6-L10) at C4
4. ✓ Integration hub features in L23-L25 at C6 with high in-degree
5. ✓ Token-specific "bonucleic" features in L25 with strong output connections

**This would support the circuit description:**
- Early: Domain + structure recognition
- Middle: Prefix routing + integration
- Late: Evidence combination + token prediction

**If hypotheses are NOT confirmed:**
- May reveal novel computational strategies
- Could indicate features are more abstract than expected
- Might suggest polysemantic features serving multiple roles
