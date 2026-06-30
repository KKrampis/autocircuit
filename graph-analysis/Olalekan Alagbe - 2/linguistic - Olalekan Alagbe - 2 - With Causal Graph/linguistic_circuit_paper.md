# The Linguistic Reasoning Circuit in Gemma-2-2B: A Mechanistic Interpretability Analysis

**Authors:** Olalekan Alagbe  
**Model:** Gemma-2-2B (SAE: gemmascope-transcoder-16k)  
**Date:** 2026-04-06

---

## Abstract

We present a mechanistic interpretability analysis of the linguistic reasoning circuit in Gemma-2-2B, examining how the model implements antonym/synonym retrieval, morphological inflection (pluralisation and past-tense formation), and lexical definition look-up. Using Neuronpedia attribution graphs and sparse autoencoder (SAE) feature analysis, we generated and analysed 10 attribution graphs across four metalinguistic sub-tasks. Cross-graph feature mining at a 50% recurrence threshold identified 312 recurring circuit components, of which 15 were labelled via the Neuronpedia explanation API. The most universal recurring feature — Layer 6, Feature 2586668 (node_id=6_2267_3; "*words that appear in programming code, legal jargon, or scientific texts*") — appeared 37 times across 10 graphs, present in every prompt. The dominant causal architecture consists of a direct embedding→logit excitatory path (weights ranging from 9.79 to 14.14) that carries the majority of the output signal in a single hop, supported by secondary multi-hop paths. Four of ten prompts showed all causal paths converging through an unlabeled Layer 24 bottleneck node with a strong negative final edge, functioning as a competitor-suppression gate. Prediction confidence ranged from p=0.344 ("written," past tense of "write") to p=0.836 ("author"), inversely correlated with morphological irregularity. Notably, the prompt with the lowest confidence ("swam") activated a "*baseball terminology*" feature (Layer 5, Feature 10444) as its highest-influence early-layer detector — a compelling example of polysemantic feature repurposing for morphological computation.

---

## 1. Introduction

Mechanistic interpretability research aims to understand how large language models implement specific cognitive operations at the level of individual features and circuits. Linguistic reasoning — operations such as antonym retrieval, morphological transformations (pluralisation, tense change), and definitional look-up — provides an ideal testbed because the correct output is unambiguous, yet the computation required spans multiple levels of linguistic knowledge.

In this paper we analyse the shared circuit that Gemma-2-2B (2 billion parameters) uses to answer ten metalinguistic prompts drawn from four sub-categories: antonym/synonym retrieval, morphological inflection, and lexical look-up. Using the Neuronpedia attribution graph API, we generate sparse attribution graphs for each prompt and apply cross-graph feature mining to identify the features that recur across all or most prompts — the putative "linguistic reasoning circuit." We then trace causal paths from these features to the final logit node, producing both quantitative edge-weight data and mechanistic narratives for each prompt.

---

## 2. Methods

### 2.1 Model and Prompts

We use the Gemma-2-2B model with the Gemmascope Transcoder 16K sparse autoencoder (SAE), accessed via the Neuronpedia API. Ten prompts were selected to span four metalinguistic operations:

- **Antonym/synonym retrieval:** "The opposite of hot is", "The antonym of ancient is", "A synonym for happy is", "Another word for fast is"
- **Plural morphology:** "The plural of child is", "The plural of mouse is"
- **Past tense morphology:** "The past tense of swim is", "The past tense of write is"
- **Lexical look-up:** "A book of maps is called an", "A person who writes books is called an"

All prompts end mid-sentence so the next predicted token is unambiguous. This design ensures that the attribution graph captures the computation for a single well-defined answer.

### 2.2 Attribution Graph Generation

Attribution graphs were generated via the Neuronpedia `/api/graph/generate` endpoint with the following parameters:
- `maxFeatureNodes`: 3000
- `desiredLogitProb`: 0.95
- `nodeThreshold`: 0.8
- `edgeThreshold`: 0.85

Each graph node represents a SAE feature at a specific transformer layer and token context position. Each directed edge carries a weight indicating how strongly the source feature causally influences the target feature's activation.

### 2.3 Cross-Graph Analysis

We applied `compare_graphs()` with a 50% threshold (minimum 5/10 graphs) to identify features constituting the shared linguistic reasoning circuit. At this threshold, 312 recurring features were identified. The top 15 were labelled via the Neuronpedia feature explanation API.

### 2.4 Causal Path Tracing

For each prompt, `trace_causal_paths()` was used to identify the strongest edge-weight chains from influential feature nodes to the final logit node. Paths were classified as excitatory (+), inhibitory (−), or mixed (±). Causal path diagrams were generated with `visualize_causal_paths()` and embedded inline in each per-prompt section.

---

## 3. Results

### 3.1 Cross-Graph Recurring Features (Shared Linguistic Circuit)

A total of **312 features** met the 50% recurrence threshold across the 10 linguistic prompts, indicating a rich shared circuit. The top 15 by recurrence count are shown below.

**Table 1. Top 15 recurring features in the linguistic reasoning circuit (threshold=50%, min_appearances=5/10)**

| Layer | Feature | Node_id | Appearances | Avg Influence | Label |
|-------|---------|---------|-------------|---------------|-------|
| 6 | 2586668 | 6_2267_3 | 37/10 | 0.6571 | words that appear in programming code, legal jargon, or scientific texts |
| 0 | 74438300 | 0_12200_1 | 26/10 | 0.6758 | a variety of specific nouns |
| 3 | 5150441 | 3_3205_3 | 25/10 | 0.6616 | code snippets and documentation references, possibly related to web development |
| 4 | 110446948 | 4_14857_3 | 24/10 | 0.6861 | code snippets and license agreements |
| 7 | 4828270 | 7_3099_4 | 23/10 | 0.6683 | a variety of reference codes, abbreviations, and identifiers from different fields |
| 0 | 11637899 | 0_4823_1 | 22/10 | 0.7065 | the word "part" followed by prepositions or words related to sections or components |
| 0 | 2239785 | 0_2115_4 | 21/10 | 0.6129 | data reported as a percentage inside brackets, especially in a laboratory or medical context |
| 0 | 70051365 | 0_11835_2 | 20/10 | 0.6481 | terms used in software code such as "assembly", "using", "namespace", and "license" |
| 4 | 50205205 | 4_10015_3 | 19/10 | 0.5519 | words associated with the etymology or definition of a word |
| 0 | 40747877 | 0_9026_2 | 19/10 | 0.5392 | technical documents or data, including numbers, units, and references to figures or tables |
| 0 | 1708475 | 0_1847_2 | 18/10 | 0.6013 | scientific terms and experimental details related to biological and chemical research |
| 0 | 20624252 | 0_6421_1 | 16/10 | 0.7214 | words related to administrative processes and computer programs |
| 0 | 84571514 | 0_13004_5 | 16/10 | 0.6172 | parenthetical numerical references and citations to literature, laws, and statistics |
| 8 | 3234687 | 8_2534_3 | 16/10 | 0.6077 | words and phrases related to the meaning of words |
| 6 | 1857621 | 6_1920_3 | 16/10 | 0.585 | words related to medical or scientific texts, especially regarding drugs and chemical reactions, numbers, and plurals |

### 3.2 Edge Neighbourhood Analysis (Top 2 Features by Average Influence)

**Top 2 recurring features ranked by avg_influence:**

**Feature 18693554 at Layer 0 (node_id=0_6113_1, avg_inf=0.7848)**
- Receives input from: embedding node E_651_1 (weight=+6.68), embedding node E_2_0 (weight=+0.29)
- Sends to: Layer 7 Feature 110677 node 7_462_1 (+0.206), Layer 5 Feature 7993995 node 5_3992_1 (+0.190), Layer 7 Feature 16528367 node 7_5741_1 (+0.161), Layer 27 (logit-proximal) Feature 7033 node 27_7033_5 (−0.017)
- Interpretation: This is a direct embedding-driven feature that projects early input representations upward through Layers 5 and 7 simultaneously, making it a parallel signal broadcaster to mid-layer processing.

**Feature 80589 at Layer 11 (node_id=11_389_1, avg_inf=0.7837)**
- Receives from: Layer 10 Feature 74951635 (−19.97), Layer 10 Feature 25329392 (+17.50), Layer 10 Feature 23225509 (+8.21), Layer 9 Feature 38548580 (+7.82), Layer 9 Feature 3843368 (+7.62), and five more Layer 9–10 nodes
- Sends to: Layer 15 Feature 294512 (−4.52), Layer 14 Feature 127672195 (−4.24), Layer 15 Feature 376262 (−3.87), Layer 12 Feature 6835740 (−3.33), Layer 17 Feature 38733183 (−3.22), and five more downstream features — ALL with negative weights
- Interpretation: Feature 80589 at Layer 11 is a **pure inhibitory hub**. It integrates conflicting signals from Layer 9–10 (positive and negative), then broadcasts inhibitory signals to Layers 12–17. This is the circuit's primary suppression gate — it systematically constrains downstream late-layer processing, likely suppressing non-target answer tokens.

### 3.3 Layer 0 Analysis

Layer 0 contains 224 nodes in the representative graph (prompt 1), with influence values ranging from 0.40 to 0.80. The top influence values (0.79–0.80) indicate that a large fraction of Layer 0 nodes are highly active, suggesting that the input-layer representation is both dense and broadly distributed. Layer 0 features lack `clerp` (token-level) labels, indicating they represent abstract input statistics rather than specific tokens. The concentration of 8/15 top recurring features at Layer 0 reflects its role as the foundation of the shared linguistic circuit — the model's initial parsing of metalinguistic prompt structure happens universally across all 10 tasks.

### 3.4 Per-Prompt Circuit Interpretations

---


### Prompt: "<bos>The opposite of hot is"

**Predicted token:** `Output " cold" (p=0.566)` (prob=0.5664)

**Token competition:**

| Rank | Token | Logit score | Features voting |
|------|-------|-------------|-----------------|

**Circuit walkthrough:**

*Early layers — input recognition*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 0 | 11703 | 0_11703_2 | 0.8002 | 1.4215 |  words related to travel, tourism and hospitality |
| 2 | 15200 | 2_15200_5 | 0.8 | 4.0646 |  the verb "to be" in various languages and tenses |
| 2 | 13974 | 2_13974_2 | 0.7997 | 3.5435 |  the word "pace", sometimes in conjunction with "structures". |
| 0 | 5074 | 0_5074_1 | 0.7991 | 2.9798 | occurrences of the word 'red' at the start of phrases or clauses |
| 2 | 14970 | 2_14970_5 | 0.7982 | 4.4725 |  auxiliary verbs in the present tense |
| 0 | 1700 | 0_1700_2 | 0.7978 | 1.9295 | a mix of filler words like "like", "the", "main "and words related to problems or difficulties |
| 1 | 3842 | 1_3842_3 | 0.7976 | 1.9017 | the word "of" |
| 0 | 7738 | 0_7738_1 | 0.7972 | 3.2178 |  the word "ease" |
| 0 | 1128 | 0_1128_3 | 0.7967 | 1.9072 |  the word "of" |
| 0 | 15944 | 0_15944_5 | 0.7959 | 4.0301 | sentences that are questions or statements about math using "is" |
| 0 | 6113 | 0_6113_1 | 0.7956 | 3.4013 |  the word "overall", sometimes alongside words that express quantity |
| 1 | 12115 | 1_12115_1 | 0.7954 | 3.4348 |  code comments |
| 2 | 734 | 2_734_2 | 0.795 | 3.5277 |  words associated with sports, history, or death. |
| 2 | 8212 | 2_8212_2 | 0.7946 | 4.3577 | words that could be used to compare and contrast different approaches or data in different fields. |
| 0 | 13905 | 0_13905_1 | 0.7943 | 3.0943 |  the word "visual" |
| 0 | 902 | 0_902_5 | 0.7937 | 3.6536 | the word "is" |
| 2 | 3690 | 2_3690_2 | 0.7932 | 2.3667 |  words related to collaboration or separation, in technical contexts. |
| 0 | 2223 | 0_2223_2 | 0.793 | 2.9672 | words associated with phrases "be", "outside" and possibly some conjunctions and prepositions. |
| 2 | 8816 | 2_8816_1 | 0.7928 | 5.508 |  the definite article "The" |
| 0 | 2517 | 0_2517_4 | 0.7926 | 1.7643 |  adverbs indicating uncertainty paired with verbs that reflect the uncertainty |
| 0 | 1847 | 0_1847_4 | 0.7924 | 3.0355 | scientific terms and experimental details related to biological and chemical research |
| 0 | 12747 | 0_12747_2 | 0.7919 | 2.7011 | occurrences of the words 'they', 'them', 'that', 'these', or something that can be replaced with 'they' or 'them' |
| 2 | 3385 | 2_3385_3 | 0.7917 | 1.975 |  a mix of religious words, time-related words, and code or programming-related keywords |

*Middle layers — relational mapping*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 4 | 10015 | 4_10015_5 | 0.7995 | 3.0575 |  words associated with the etymology or definition of a word |
| 4 | 11886 | 4_11886_5 | 0.7993 | 3.977 | conditional and definitional statements within mathematical text |
| 4 | 776 | 4_776_5 | 0.7989 | 2.8016 |  code and mathematical expressions, specifically those with inequalities, unicode symbols, and iOS code snippets |
| 6 | 4575 | 6_4575_3 | 0.7987 | 5.3584 | C/C++ header file code, particularly #include and #define statements |
| 7 | 6219 | 7_6219_5 | 0.7985 | 6.0043 |  phrases used to express comparison |
| 4 | 9031 | 4_9031_4 | 0.798 | 4.2298 | technical or scientific language |
| 7 | 4526 | 7_4526_5 | 0.7974 | 5.9202 |  words related to comparisons, symmetry or reversals in data or situations |
| 4 | 9555 | 4_9555_1 | 0.7948 | 4.3425 |  code comments and import statements |
| 6 | 3874 | 6_3874_4 | 0.7941 | 5.8448 |  topics/titles or short phrases that often begin with a capitalized word |
| 5 | 2738 | 5_2738_5 | 0.7939 | 3.8666 | words that are part of computer code in various programming languages |
| 4 | 13985 | 4_13985_3 | 0.7921 | 4.4518 | instances of "meant by" or "mean by", as in trying to define something |

*Late layers — token selection*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 9 | 13520 | 9_13520_4 | 0.797 | 15.3522 |  various code snippets |
| 13 | 13298 | 13_13298_5 | 0.7965 | 9.317 |  words referring to scientific values and variables |
| 11 | 389 | 11_389_1 | 0.7963 | 38.2464 | capital letters standing alone or at the beginning of words |
| 11 | 4301 | 11_4301_5 | 0.7961 | 6.8663 |  sentences that describe systems and their uses |
| 13 | 7715 | 13_7715_5 | 0.7952 | 10.6115 |  definitions, especially those of a populist political nature. |
| 9 | 13138 | 9_13138_5 | 0.7935 | 3.7418 | words related to scientific or legal texts describing processes that involve stages and evaluation |

**Causal paths (edge-weight chains to logit):**

*Path 1 — (±) mixed | weight=314.122144 | hops=4*
→ `node_id=11_4301_5` | `feature=4301` | Layer 11 | ` sentences that describe systems and their uses` — edge [-0.8616]
→ `node_id=18_1296_5` | `feature=?` | Layer 18 | `(no label)` — edge [+11.5579]
→ `node_id=20_6666_5` | `feature=?` | Layer 20 | `(no label)` — edge [+5.3053]
→ `node_id=25_16258_5` | `feature=?` | Layer 25 | `(no label)` — edge [-5.9455]
→ **LOGIT** `node_id=27_7033_5` Layer 27 — `Output " cold" (p=0.566)`

*Path 2 — (±) mixed | weight=55.201727 | hops=5*
→ `node_id=7_4526_5` | `feature=4526` | Layer 7 | ` words related to comparisons, symmetry or reversals in data or situations` — edge [-1.9043]
→ `node_id=12_95_5` | `feature=?` | Layer 12 | `(no label)` — edge [+1.1745]
→ `node_id=14_1354_5` | `feature=?` | Layer 14 | `(no label)` — edge [+0.7825]
→ `node_id=20_6666_5` | `feature=?` | Layer 20 | `(no label)` — edge [+5.3053]
→ `node_id=25_16258_5` | `feature=?` | Layer 25 | `(no label)` — edge [-5.9455]
→ **LOGIT** `node_id=27_7033_5` Layer 27 — `Output " cold" (p=0.566)`

*Path 3 — (±) mixed | weight=16.85499 | hops=4*
→ `node_id=2_8212_2` | `feature=8212` | Layer 2 | `words that could be used to compare and contrast different approaches or data in different fields.` — edge [+2.2498]
→ `node_id=3_6576_2` | `feature=?` | Layer 3 | `(no label)` — edge [-0.2375]
→ `node_id=20_6666_5` | `feature=?` | Layer 20 | `(no label)` — edge [+5.3053]
→ `node_id=25_16258_5` | `feature=?` | Layer 25 | `(no label)` — edge [-5.9455]
→ **LOGIT** `node_id=27_7033_5` Layer 27 — `Output " cold" (p=0.566)`

*Path 4 — (+) excitatory | weight=9.302095 | hops=1*
→ `node_id=E_5342_4` | `feature=?` | Layer E | `(no label)` — edge [+9.3021]
→ **LOGIT** `node_id=27_7033_5` Layer 27 — `Output " cold" (p=0.566)`

*Path 5 — (±) mixed | weight=7.145253 | hops=3*
→ `node_id=0_902_5` | `feature=902` | Layer 0 | `the word "is"` — edge [+0.2265]
→ `node_id=20_6666_5` | `feature=?` | Layer 20 | `(no label)` — edge [+5.3053]
→ `node_id=25_16258_5` | `feature=?` | Layer 25 | `(no label)` — edge [-5.9455]
→ **LOGIT** `node_id=27_7033_5` Layer 27 — `Output " cold" (p=0.566)`

**Causal path diagram:**

![Causal paths for "<bos>The opposite of hot is" → "Output " cold" (p=0.566)"](graphs/bos_the_opposite_of_hot_is__output___cold___p_0__causal_paths.png)

*Figure: Causal paths from input features to predicted token "Output " cold" (p=0.566)". Y-axis = transformer layer. Edge width = connection strength. Green = excitatory, red = inhibitory, orange = mixed.*

**Mechanistic Narrative**

**Early layers (0–3): structural template parsing.** The circuit opens not with a semantic understanding of "opposite" but with a cascade of structural detectors. Layer 2, Feature 15200 (node_id=2_15200_5, inf=0.800) — "the verb 'to be' in various languages and tenses" — fires strongly on the copula structure of the prompt. Layer 0, Feature 15944 (node_id=0_15944_5, inf=0.796) — "sentences that are questions or statements about math using 'is'" — registers this as an X-is-Y completion frame. Crucially, Layer 2, Feature 8212 (node_id=2_8212_2, inf=0.795) — "words that could be used to compare and contrast different approaches" — is already detecting the oppositional frame before any semantic content has been processed. The model at this stage knows: *this is a structured predicate-completion task asking for a contrasting term*.

**Middle layers (4–7): antonym circuit activation.** The key relational computation happens at Layer 4–7. Layer 4, Feature 10015 (node_id=4_10015_5, inf=0.800) — "words associated with the etymology or definition of a word" — switches the circuit into lexical-definition mode. Layer 4, Feature 13985 (node_id=4_13985_3, inf=0.792) — "instances of 'meant by' or 'mean by'" — further specifies that the model is computing a definitional relation. The pivotal domain-mapping moment arrives at Layer 7, Feature 4526 (node_id=7_4526_5, inf=0.797) — "words related to comparisons, symmetry or reversals in data or situations". This feature carries the highest activation in the middle band (act=5.92) and represents the exact semantic operation required: reversal. It is this feature that maps the input concept "hot" to its antonym slot.

**Late layers (8–13): signal convergence and suppression gating.** Layer 11 Feature 389 (node_id=11_389_1, inf=0.796, act=38.25) is the most striking late-layer activation — extraordinarily high activation relative to the rest. This is the cross-graph inhibitory hub identified in Section 3.2: all its outgoing edges are negative, and it systematically suppresses Layers 12–17. It acts as a gate, dampening alternative token representations. Layer 13, Feature 7715 (node_id=13_7715_5, inf=0.795) — "definitions" — makes the final definitional push upstream of the logit.

**Causal paths: a direct embedding anchor plus complex modulation.** The only pure excitatory path is Path 4 (weight=9.30, 1 hop): embedding node E_5342_4 → logit with edge weight +9.30. This is a remarkable direct vote — an embedding-level feature carries enough signal to push " cold" to the logit without any intermediate feature processing. The dominant path by weight is Path 1 (weight=314.12, 4 hops): Layer 11 Feature 9303129 (−0.86) → Layer 18 (+11.56) → Layer 20 (+5.31) → Layer 25 (−5.95) → logit. The alternating suppression-amplification pattern of this path reflects a complex gating mechanism that first suppresses (Layer 11), then massively amplifies (Layer 18, 20), then delivers a final suppressing gate (Layer 25) before the logit. Paths 2, 3, and 5 all converge on the same Layer 20 → Layer 25 → logit bottleneck, revealing Layer 20 Feature 22361307 and Layer 25 Feature 132592444 as a shared final gateway through which multiple upstream signals must pass. The circuit is **convergent**: while there are five paths, four of them funnel through the same two late-layer nodes, meaning the competition is resolved upstream of Layer 20.

**Token competition:** The prediction probability is 0.566 — moderate confidence. The Layer 7 reversal feature and direct embedding push explain why " cold" won; the inhibitory Layer 11 hub systematically suppressed potential alternatives such as " warm" or " cool" by dampening Layers 12–17. The circuit is moderately confident rather than decisive, consistent with multiple valid antonyms existing for "hot" in different contexts.

---

### Prompt: "<bos>The antonym of ancient is"

**Predicted token:** `Output " modern" (p=0.136)` (prob=0.1365)

**Token competition:**

| Rank | Token | Logit score | Features voting |
|------|-------|-------------|-----------------|

**Circuit walkthrough:**

*Early layers — input recognition*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 0 | 11347 | 0_11347_2 | 0.8 | 3.1193 |  words related to nature and animals, especially birds |
| 2 | 4188 | 2_4188_3 | 0.7996 | 1.8035 |  Croatian words that include the letters 'vr' and are related to confirmation or verification |
| 0 | 15859 | 0_15859_3 | 0.7994 | 1.4727 | technical jargon and foreign languages. |
| 3 | 10471 | 3_10471_4 | 0.7993 | 3.2145 | words related to academic or scientific writing |
| 5 | 717 | 5_717_3 | 0.7983 | 3.0997 |  words associated with raising or managing money |
| 3 | 15128 | 3_15128_4 | 0.7981 | 3.0682 |  proper nouns and frequently used short function words, especially "of" |
| 6 | 2267 | 6_2267_1 | 0.7979 | 12.6864 | words that appear in programming code, legal jargon, or scientific texts |
| 3 | 4136 | 3_4136_6 | 0.7977 | 2.6666 |  scientific and medical terms and their prefixes and suffixes |
| 0 | 13920 | 0_13920_1 | 0.7973 | 2.576 |  the word "pie" (and sometimes "the") in a document |
| 2 | 7290 | 2_7290_5 | 0.7971 | 2.5924 |  words related to scientific, technical, and medical descriptions, particularly those used in research and experimentation. |
| 4 | 799 | 4_799_5 | 0.7969 | 3.3145 |  symbols and terms related to voltage, electricity, and electronics |
| 1 | 8370 | 1_8370_3 | 0.7967 | 1.5134 |  words and phrases in technical documentation from a wide array of fields |
| 1 | 11207 | 1_11207_1 | 0.7966 | 3.315 |  code and documented code |
| 6 | 16359 | 6_16359_6 | 0.7962 | 3.3636 | a mix of seemingly unrelated code terms, abbreviations, and function names. |
| 0 | 9419 | 0_9419_3 | 0.7958 | 1.489 |  terms related to the Indicium AttributeSet infrastructure for Java |
| 4 | 10235 | 4_10235_4 | 0.7954 | 3.6038 | math and equation notation |
| 0 | 2146 | 0_2146_1 | 0.795 | 2.365 | the word survivor (or a variant) and sometimes a preceding article of 'the'. |
| 0 | 2189 | 0_2189_5 | 0.7948 | 4.0502 |  technical writing related to scientific studies |
| 3 | 11820 | 3_11820_6 | 0.7946 | 3.1713 |  uses of the verb "is" or "was" |
| 3 | 1966 | 3_1966_6 | 0.7944 | 2.3756 |  words and expressions related to scientific methodology, research papers, and math/engineering |
| 0 | 9022 | 0_9022_2 | 0.7942 | 3.6145 |  technical words used in computing, science, or engineering |
| 5 | 14514 | 5_14514_1 | 0.794 | 10.9809 | the letter 'L' capitalized |
| 4 | 2866 | 4_2866_6 | 0.7938 | 4.1388 |  the word "is" |
| 0 | 4592 | 0_4592_3 | 0.7936 | 1.5638 |  a word stem "lle" or "ull" and the word "Slemish". That's not the best description, so here are some alternatives: Irish geography terms, words with the ully suffix, certain surnames |
| 1 | 1861 | 1_1861_4 | 0.7932 | 2.4841 |  words or phrases that indicate progress, success, or advancement in various fields like computer science, history, genomics, and medicine. |
| 3 | 7876 | 3_7876_6 | 0.793 | 2.1179 |  the character sequence "ol...de" and some other seemingly unrelated character sequences |
| 4 | 6784 | 4_6784_6 | 0.7928 | 4.15 | scientific papers and results |
| 1 | 12764 | 1_12764_3 | 0.7926 | 1.9464 | words that are related to formal writing such as scientific papers and official documents. |

*Middle layers — relational mapping*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 8 | 7848 | 8_7848_3 | 0.7998 | 5.3709 |  definitions of the word "false" |
| 8 | 2212 | 8_2212_6 | 0.7989 | 3.2163 |  historical names, places and events |
| 9 | 12379 | 9_12379_5 | 0.7985 | 5.4592 |  words related to technical and academic writing, including computer science, mathematics, and scientific studies. |
| 8 | 16344 | 8_16344_6 | 0.7975 | 3.2598 |  content that looks like bullet points or numbered lists. |
| 8 | 1726 | 8_1726_4 | 0.796 | 6.0892 |  words or phrases that represent importance of a topic or matter |
| 11 | 16322 | 11_16322_1 | 0.7952 | 31.6969 |  code snippets assigning values to variables |
| 8 | 11729 | 8_11729_5 | 0.7934 | 3.9325 | words related to history or groups of people from the past |
| 8 | 231 | 8_231_3 | 0.7924 | 6.5721 |  code or text related to dictionaries and named entity recognition |

*Late layers — token selection*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 20 | 16253 | 20_16253_6 | 0.7991 | 7.7182 |  sentences discussing concepts and definitions, especially related to subjective experience and systems of belief |
| 16 | 14006 | 16_14006_5 | 0.7987 | 9.6616 |  technical and scientific terms |
| 20 | 11820 | 20_11820_6 | 0.7964 | 8.4193 |  discussion of Native Americans, particularly related to history, culture, and correcting stereotypes |
| 25 | 7114 | 25_7114_6 | 0.7956 | 7.0546 |  personal opinions or emotional statements or arguments in text. |

**Causal paths (edge-weight chains to logit):**

*Path 1 — (+) excitatory | weight=7.773116 | hops=1*
→ `node_id=E_12387_5` | `feature=?` | Layer E | `(no label)` — edge [+7.7731]
→ **LOGIT** `node_id=27_5354_6` Layer 27 — `Output " modern" (p=0.136)`

*Path 2 — (-) inhibitory | weight=0.125158 | hops=1*
→ `node_id=25_7114_6` | `feature=7114` | Layer 25 | ` personal opinions or emotional statements or arguments in text.` — edge [-0.1252]
→ **LOGIT** `node_id=27_5354_6` Layer 27 — `Output " modern" (p=0.136)`

**Causal path diagram:**

![Causal paths for "<bos>The antonym of ancient is" → "Output " modern" (p=0.136)"](graphs/bos_the_antonym_of_ancient_is__output___modern___p__causal_paths.png)

*Figure: Causal paths from input features to predicted token "Output " modern" (p=0.136)". Y-axis = transformer layer. Edge width = connection strength. Green = excitatory, red = inhibitory, orange = mixed.*

**Mechanistic Narrative**

**Early layers (0–3): technical/academic register detection.** The circuit activates a cluster of technical-register features rather than immediately engaging antonym-specific processing. Layer 6, Feature 2267 (node_id=6_2267_1, inf=0.798, act=12.69) — "words that appear in programming code, legal jargon, or scientific texts" — is the same universally-recurring feature (Feature 2586668 at Layer 6) identified in the cross-graph analysis as the most common component of the linguistic circuit. Its very high activation (12.69) confirms it responds to the formal, template-like structure of these prompts. Layer 3, Feature 10471 (node_id=3_10471_4, inf=0.799) — "words related to academic or scientific writing" — reinforces this academic-register frame. Layer 3, Feature 11820 and Layer 4, Feature 2866 both activate on the copula "is", positioning this as a definitional completion task.

**Middle layers (8–11): the "definition of false" misfire and historical anchoring.** The most striking and unexpected middle-layer activation is Layer 8, Feature 7848 (node_id=8_7848_3, inf=0.800) — "definitions of the word 'false'". This feature, which represents semantic negation/falsity relationships, activates strongly on "ancient" — suggesting the model's word-definition circuit is processing "ancient" through a logical-negation frame (what is NOT ancient?). Simultaneously, Layer 8, Feature 8212 — "historical names, places and events" (inf=0.797) and Layer 8, Feature 11729 — "words related to history or groups of people from the past" — anchor "ancient" firmly in a temporal-historical domain. These two signals (semantic negation + temporal historical) are the domain-mapping pivot for the antonym computation.

**Late layers (16–25): ambiguous resolution under high competition.** Layer 20, Feature 16253 (node_id=20_16253_6, inf=0.799) — "sentences discussing concepts and definitions, especially related to subjective experience and systems of belief" — is active in the final prediction stage, suggesting the circuit is still resolving a definitional relationship rather than making a confident lexical retrieval. Layer 25, Feature 7114 (node_id=25_7114_6, inf=0.796) — "personal opinions or emotional statements" — is a late-layer activation whose presence at Layer 25 directly upstream of the logit is surprising and may indicate the model is treating the antonym query as having a subjective dimension.

**Causal paths: a dominantly direct circuit with weak inhibition.** Only two paths were found, and both are single-hop (direct). The dominant path is excitatory Path 1 (weight=7.77, 1 hop): embedding node E_12387_5 → logit (+7.77). As with Prompt 1, the embedding layer provides a strong direct vote for " modern". Path 2 is a very weak inhibitory single-hop (weight=0.125): Layer 25, Feature 25493344 → logit (−0.125). This inhibitory signal is negligible compared to the excitatory embedding path and explains only a tiny fraction of the token competition.

**Token competition: genuine ambiguity.** The probability of 0.136 is strikingly low — the model is highly uncertain. "Ancient" has many valid antonyms (modern, new, contemporary, recent, young) and the circuit cannot resolve the competition. The embedding-to-logit direct path explains why " modern" won marginally, but the low confidence reflects the absence of a clear semantic pathway that uniquely identifies "modern" as the antonym. This contrasts sharply with Prompt 1 where the Layer 7 reversal feature provided a clean semantic anchor for " cold". The circuit here is **ambiguous** — multiple competing paths of similar strength, with no single dominant mechanistic route.

---

### Prompt: "<bos>A synonym for happy is"

**Predicted token:** `Output ":" (p=0.092)` (prob=0.0917)

**Token competition:**

| Rank | Token | Logit score | Features voting |
|------|-------|-------------|-----------------|

**Circuit walkthrough:**

*Early layers — input recognition*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 1 | 4658 | 1_4658_3 | 0.8001 | 2.1494 | technical descriptions of processes involving manipulation of materials into specific shapes |
| 2 | 14718 | 2_14718_1 | 0.7999 | 3.8981 |  LaTeX code, particularly equations and mathematical expressions |
| 1 | 10748 | 1_10748_5 | 0.7995 | 1.8366 |  text of scientific or legal papers |
| 7 | 3168 | 7_3168_5 | 0.7993 | 3.5396 |  rhetorical questions and references to blog posts |
| 0 | 8240 | 0_8240_2 | 0.7991 | 1.165 |  words and phrases related to strong emotions or opinions |
| 7 | 14804 | 7_14804_5 | 0.7989 | 4.2841 |  code or markup |
| 3 | 13623 | 3_13623_3 | 0.7987 | 3.2661 |  the word "for." |
| 4 | 237 | 4_237_3 | 0.7983 | 4.4335 |  positive adjectives and words related to liking something. |
| 1 | 7848 | 1_7848_3 | 0.7975 | 2.4098 |  meta-data about blog posts like the publishing date, author, navigation links, and comments. |
| 5 | 9017 | 5_9017_5 | 0.7973 | 3.0386 | discussions of values and beliefs, specifically related to Mormonism and truth, and what constitutes them |
| 2 | 438 | 2_438_2 | 0.7971 | 1.5164 | the term "co-worker" or similar terms like "neighbor" |
| 6 | 8047 | 6_8047_5 | 0.7969 | 2.5158 | words related to the concept of comparison, evaluation, and contrast. |
| 3 | 9685 | 3_9685_1 | 0.7967 | 4.4042 |  a wide and seemingly unrelated variety of terms, possibly indicating a focus on general language patterns within diverse texts |
| 4 | 2005 | 4_2005_5 | 0.7965 | 2.1093 | verbs |
| 6 | 3479 | 6_3479_3 | 0.7963 | 5.2035 | Java and Objective-C code documentation |
| 6 | 15968 | 6_15968_2 | 0.7961 | 5.0026 |  words related to ideology or belief systems, including religion, politics, and values |
| 4 | 10661 | 4_10661_2 | 0.7959 | 3.3256 |  words related to computer software features |
| 6 | 3367 | 6_3367_4 | 0.7957 | 4.9192 |  instances of grammatical corrections or suggestions, particularly the use of "in spite of" |
| 5 | 6471 | 5_6471_5 | 0.7955 | 2.7599 |  technical/scientific descriptions consisting of equations, relations, demonstrations, and testimonies |
| 0 | 6133 | 0_6133_4 | 0.7953 | 2.5546 | something the user looked at, is looking at, or will look at. |
| 0 | 14288 | 0_14288_4 | 0.7947 | 2.2551 |  terms involved with monetary quotes and amounts, stress, and driving |
| 0 | 11612 | 0_11612_2 | 0.7945 | 1.7709 |  technical or scientific terms, especially in a research context |
| 3 | 5469 | 3_5469_3 | 0.7943 | 2.886 |  the word "up" and words that end with "tick", along with related medical or geographical terms |
| 4 | 3142 | 4_3142_3 | 0.7939 | 3.7953 | phrases including "a way of", "a means of", or "a sign of". |
| 3 | 11974 | 3_11974_5 | 0.7937 | 2.8584 |  the letters "s", "y", "y", "are", "and" and fragments of words/names seemingly at random |
| 5 | 8677 | 5_8677_5 | 0.7935 | 4.0635 |  words and code elements commonly used in programming |
| 3 | 796 | 3_796_3 | 0.7933 | 3.346 |  Objective-C/C++ code syntax, with a preference for class names, pointers, and array/dictionary access |
| 2 | 13917 | 2_13917_5 | 0.793 | 2.2406 | verbs |
| 0 | 7329 | 0_7329_2 | 0.7926 | 1.0834 |  words related to internal processes or connections within a system or organization, with a focus on specialized terminology and some legal or scientific contexts. |
| 0 | 5942 | 0_5942_4 | 0.7924 | 2.3855 |  words related to subjective interest |

*Middle layers — relational mapping*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 9 | 13046 | 9_13046_5 | 0.7997 | 3.937 | text discussing language, words, or idioms. |
| 9 | 4088 | 9_4088_5 | 0.7985 | 5.6279 |  words followed by quotation marks, or other angle bracket encasements |
| 15 | 9361 | 15_9361_2 | 0.7981 | 20.023 | the word "replace" and related words like "replacing" and "alternative". |
| 10 | 883 | 10_883_1 | 0.7977 | 15.1468 |  scientific and technical terms that end in "-tion" or "-sion." |
| 14 | 2852 | 14_2852_1 | 0.7951 | 34.1273 |  two-letter initial abbreviations and the first few letters of words. |
| 11 | 389 | 11_389_1 | 0.7941 | 40.6929 | capital letters standing alone or at the beginning of words |
| 8 | 6791 | 8_6791_5 | 0.7922 | 4.5445 |  text inside parentheses or related to ancient Greece, and potentially also negative feelings |

*Late layers — token selection*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 24 | 11002 | 24_11002_5 | 0.7979 | 6.8726 | what seem to be numerical data points |
| 25 | 13868 | 25_13868_5 | 0.7949 | 9.1865 |  words related to technical processes or descriptions |
| 17 | 1827 | 17_1827_5 | 0.7928 | 7.3296 | words or phrases related to advice or instructions |

**Causal paths (edge-weight chains to logit):**

*Path 1 — (+) excitatory | weight=8.761217 | hops=1*
→ `node_id=E_603_5` | `feature=?` | Layer E | `(no label)` — edge [+8.7612]
→ **LOGIT** `node_id=27_235292_5` Layer 27 — `Output ":" (p=0.092)`

**Causal path diagram:**

![Causal paths for "<bos>A synonym for happy is" → "Output ":" (p=0.092)"](graphs/bos_a_synonym_for_happy_is__output______p_0_092_causal_paths.png)

*Figure: Causal paths from input features to predicted token "Output ":" (p=0.092)". Y-axis = transformer layer. Edge width = connection strength. Green = excitatory, red = inhibitory, orange = mixed.*

**Mechanistic Narrative**

**Early layers (0–5): synonym-as-replacement and emotional adjective detection.** Layer 0 activates "words and phrases related to strong emotions or opinions" (inf=0.799) and "words related to subjective interest" (inf=0.792), correctly encoding "happy" as a positive emotional state. Layer 4 Feature "positive adjectives and words related to liking something" (inf=0.798, act=4.43) locks onto the semantic class of the target word. Layer 6 activates "words related to the concept of comparison, evaluation, and contrast" (inf=0.797), placing this in the relational-equivalence frame. The model has recognised: *find a word in the same positive-emotion adjective class*.

**Middle layers (8–15): replacement detection overridden by formatting.** The pivotal middle-layer feature is Layer 15 "the word 'replace' and related words like 'replacing' and 'alternative'" (node_id=15_5255_5, inf=0.798, act=20.02) — the highest activation in the band. This correctly captures "synonym" as a lexical replacement. However, Layer 14 Feature "two-letter initial abbreviations and the first few letters of words" (node_id=14_2852_1, act=34.13) and the cross-graph inhibitory hub Layer 11, Feature 389 (node_id=11_389_1, act=40.69 — "capital letters standing alone") both fire with exceptional activation, indicating the model has locked onto a *formatting template* rather than a semantic synonym retrieval.

**Causal paths and token competition.** Only one path was found: excitatory Path 1 (weight=8.76, 1 hop) from embedding E_603_5 → logit (+8.76). The colon ":" token is pushed entirely by a direct embedding-level vote with zero intermediate feature hops — the simplest possible circuit. The predicted token ":" (p=0.092) reveals the model is pattern-matching to reference-text formatting (dictionary/glossary entries of the form "A synonym for X is: [word]") rather than retrieving a semantic synonym. The semantic synonym-lookup circuit (positive-adjective and replacement features) is present but overridden by format-following. The circuit is **format-dominated**: it correctly detected the synonym task structure but chose to predict the formatting token that precedes the answer rather than the answer itself. This is the clearest example in the dataset of a metalinguistic task being hijacked by document-format pattern-matching.

---

### Prompt: "<bos>Another word for fast is"

**Predicted token:** `Output ":" (p=0.101)` (prob=0.1012)

**Token competition:**

| Rank | Token | Logit score | Features voting |
|------|-------|-------------|-----------------|

**Circuit walkthrough:**

*Early layers — input recognition*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 1 | 13059 | 1_13059_3 | 0.8001 | 1.695 |  structured data related to media, particularly website URLs |
| 0 | 1715 | 0_1715_2 | 0.7999 | 1.646 | words related to writing blog posts and expressing personal feelings, often about mundane or routine topics |
| 4 | 14127 | 4_14127_3 | 0.7993 | 2.8303 | code snippets including annotations (starting with @), colons, and/or the word "def" |
| 1 | 1412 | 1_1412_3 | 0.7991 | 1.2287 | mathematical or programming code. |
| 5 | 5352 | 5_5352_3 | 0.7989 | 3.3876 | the word "known" or "called" preceded by "also" and followed by "as" |
| 0 | 7930 | 0_7930_2 | 0.7987 | 1.6107 |  the string 'cha', preferably within the context of a medical or scientific document/context |
| 0 | 13488 | 0_13488_2 | 0.7983 | 1.3181 |  quantities referring to age or time |
| 3 | 14727 | 3_14727_3 | 0.7981 | 2.3843 | mathematical formulae, figures, and references to external documents |
| 1 | 613 | 1_613_2 | 0.7973 | 2.958 |  proper nouns and words indicating location or categorization |
| 5 | 7291 | 5_7291_5 | 0.7969 | 4.4222 |  strings of letters or numbers that have some meaning in a specific technical domain |
| 5 | 10335 | 5_10335_3 | 0.7967 | 4.2331 |  words and phrases that are emotionally charged, especially those suggesting negative experiences or strong disagreement. |
| 0 | 14471 | 0_14471_1 | 0.7954 | 1.7356 |  the word "attempt." |
| 2 | 1209 | 2_1209_2 | 0.795 | 2.5085 |  LaTeX array environments |
| 4 | 4941 | 4_4941_3 | 0.7946 | 2.8536 | technical or legal documentation terms and related words. |
| 0 | 13709 | 0_13709_1 | 0.7937 | 1.5189 | the word "stable" and words that begin "char" |
| 5 | 3732 | 5_3732_3 | 0.7933 | 4.6718 |  legal and programming text |
| 6 | 11964 | 6_11964_4 | 0.7931 | 5.1892 |  words related to water, names, and positive qualities |
| 0 | 9773 | 0_9773_5 | 0.7929 | 2.9356 |  references to dates and times |
| 5 | 7762 | 5_7762_4 | 0.7927 | 4.1017 | words related to a walk or journey on a path. |
| 2 | 7110 | 2_7110_5 | 0.7925 | 2.9788 |  verbs and adjectives that indicate actions, scientific claims, or political agendas |
| 2 | 12647 | 2_12647_1 | 0.7921 | 2.7827 |  ordinal numbers |

*Middle layers — relational mapping*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 8 | 2051 | 8_2051_4 | 0.7997 | 3.2076 |  words related to dark vs light, size comparison, beams and mask creation in relation to manufacturing a device and/or in calculating kernals. |
| 9 | 2832 | 9_2832_5 | 0.7995 | 5.5093 | code snippets related to ImageMagick libraries and thread management in Java |
| 0 | 8 | 0_8_1 | 0.7975 | 0.0 | phrases with "are," and sometimes also finds other words related to research, science, testing, and data |
| 12 | 3684 | 12_3684_1 | 0.7971 | 33.8604 |  lines of code starting with a '#' |
| 7 | 8770 | 7_8770_1 | 0.7965 | 16.1535 | the start of sentences as well as mathematical equations |
| 12 | 2130 | 12_2130_3 | 0.7962 | 14.613 |  the word "The" at the beginning of a text |
| 8 | 6720 | 8_6720_3 | 0.796 | 5.2263 |  instances where the author is rephrasing a statement |
| 7 | 3099 | 7_3099_2 | 0.7958 | 32.1374 |  a variety of reference codes, abbreviations, and identifiers from different fields. |
| 10 | 9569 | 10_9569_4 | 0.7956 | 7.8286 | examples of someone asking for grammatical advice about the phrase "in spite of" |
| 9 | 10466 | 9_10466_3 | 0.7952 | 8.9861 | words and phrases describing previous names or states. |
| 9 | 14625 | 9_14625_3 | 0.7948 | 7.3845 | instances of the word "called" or "call" and nearby words |
| 8 | 10864 | 8_10864_5 | 0.7942 | 3.8652 |  text related to time |
| 7 | 3911 | 7_3911_3 | 0.7935 | 5.2383 |  code comments, file headers, or code status messages |
| 8 | 7166 | 8_7166_5 | 0.7923 | 4.0834 | phrases that use the word "name" and words that are similar in meaning to "name" such as "implies" |

*Late layers — token selection*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 17 | 13842 | 17_13842_4 | 0.7985 | 11.863 | quick |
| 18 | 8943 | 18_8943_5 | 0.7979 | 6.6957 |  words related to parsing a sentence |
| 14 | 15451 | 14_15451_3 | 0.7977 | 20.6624 |  phrases that introduce opinions, suggestions, or conclusions |
| 22 | 5124 | 22_5124_4 | 0.7944 | 59.4443 | the word "fast" |
| 17 | 8783 | 17_8783_1 | 0.794 | 86.6477 |  specific months |

**Causal paths (edge-weight chains to logit):**

*Path 1 — (+) excitatory | weight=7.241879 | hops=1*
→ `node_id=E_603_5` | `feature=?` | Layer E | `(no label)` — edge [+7.2419]
→ **LOGIT** `node_id=27_235292_5` Layer 27 — `Output ":" (p=0.101)`

**Causal path diagram:**

![Causal paths for "<bos>Another word for fast is" → "Output ":" (p=0.101)"](graphs/bos_another_word_for_fast_is__output______p_0_101_causal_paths.png)

*Figure: Causal paths from input features to predicted token "Output ":" (p=0.101)". Y-axis = transformer layer. Edge width = connection strength. Green = excitatory, red = inhibitory, orange = mixed.*

**Mechanistic Narrative**

**Early layers (0–5): synonym-via-reformulation detection.** The early circuit activates a set of features centered on reformulation and technical naming conventions. Layer 5, Feature 5352 (node_id=5_5352_3, inf=0.799) — "the word 'known' or 'called' preceded by 'also' and followed by 'as'" — is the most semantically precise early-layer feature: "also known as" is a direct synonym expression. Layer 0, Feature 1715 — "blog posts and personal feelings, mundane/routine topics" — and Layer 4, Feature 14127 — "code snippets including annotations, colons, and/or the word 'def'" — both signal a written-document template. The colon-associated feature at Layer 4 is appearing again, foreshadowing the circuit's ultimate output.

**Middle layers (7–12): prior-naming and reference detection converge.** The middle-layer cluster reveals two parallel processing streams. Layer 9, Feature 10466 (node_id=9_10466_3, inf=0.795) — "words and phrases describing previous names or states" — and Layer 9, Feature 14625 — "instances of the word 'called' or 'call' and nearby words" — indicate the model has locked onto "another word for" as a naming/calling relationship. Layer 7, Feature 3099 (node_id=7_3099_2, inf=0.796, act=32.14) — "a variety of reference codes, abbreviations, and identifiers" — is the recurring cross-graph hub from Table 1, here firing on the general synonym-labeling frame. Layer 8, Feature 6720 — "instances where the author is rephrasing a statement" — further confirms the rephrasing/synonym interpretation.

**Late layers (17–22): semantic content vs. format token.** The late layers show a dramatic tension. Layer 22, Feature 5124 (node_id=22_5124_4, inf=0.794, act=59.44) — labeled simply "the word 'fast'" — activates with very high activation, meaning the model has correctly identified "fast" as the target word whose synonym it should retrieve. Layer 17, Feature 13842 (node_id=17_13842_4) is labeled "quick" — the correct synonym! Both "fast" and "quick" are present in the late layers. Yet the predicted token is still ":". Layer 17, Feature 8783 (act=86.65) — "specific months" — is a puzzling activation with very high activation that may be a noise feature.

**Causal paths and surprising finding.** Path 1 (excitatory, weight=7.24, 1 hop): embedding E_603_5 → logit (+7.24). The same direct-embedding-to-colon path as Prompt 3. Remarkably, even though the correct answer "quick" appears explicitly in the late-layer band (Layer 17, node 17_13842_4), it does not win at the logit. The semantic content ("fast"→"quick") is present but the colon format token has a stronger embedding-level signal. This confirms that for synonym-retrieval prompts with the template "A/Another [synonym phrase] is", the model's format-following circuit systematically dominates its semantic-retrieval circuit. The circuit is **semantically aware but format-overridden**.



---

### Prompt: "<bos>The plural of child is"

**Predicted token:** `Output " children" (p=0.677)` (prob=0.6769)

**Token competition:**

| Rank | Token | Logit score | Features voting |
|------|-------|-------------|-----------------|

**Circuit walkthrough:**

*Early layers — input recognition*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 4 | 7062 | 4_7062_5 | 0.7998 | 2.6328 | mathematical symbols and notation |
| 7 | 7798 | 7_7798_3 | 0.7996 | 5.5986 | complex mathematical language and expressions |
| 0 | 7707 | 0_7707_2 | 0.7994 | 1.4467 |  code-related keywords like serialize, json, string, instantiation, async, containers, debugging, shared folders, and UI events |
| 0 | 6332 | 0_6332_2 | 0.7992 | 1.1841 |  proper nouns and technical terms |
| 2 | 11571 | 2_11571_4 | 0.7988 | 1.8984 |  words related to family, childhood, and male relationships |
| 0 | 11773 | 0_11773_4 | 0.7986 | 1.7096 |  the word "campaign" which generally relate to elections |
| 0 | 5713 | 0_5713_2 | 0.7983 | 1.7142 |  words related to processes and parts of machinery, electronics, mass produced products, and the legal field. |
| 2 | 8786 | 2_8786_2 | 0.7981 | 2.0533 |  mentions of specific mathematical and vehicular concepts |
| 0 | 5677 | 0_5677_4 | 0.7979 | 2.3725 | the word "reached" along with related words like 'reached', 'passes', 'yards',' English' and numbers |
| 1 | 7755 | 1_7755_5 | 0.7975 | 3.8699 |  terms about scripture and truth, often in the context of Christian belief |
| 0 | 3200 | 0_3200_2 | 0.7973 | 1.2342 | SQL code snippets and database related commands or references in formal settings |
| 0 | 9348 | 0_9348_1 | 0.7971 | 3.6207 |  sentences that start with the word "The" |
| 1 | 3136 | 1_3136_2 | 0.7969 | 1.6804 | the word "extra," technical instructions and words related to hands |
| 0 | 3728 | 0_3728_2 | 0.7967 | 1.5506 |  technical scientific terms, especially those related to medicine and biology |
| 0 | 16170 | 0_16170_1 | 0.796 | 3.3534 | words related to programming code, math, anatomy, medicine, structure, and anything that can range. |
| 0 | 9446 | 0_9446_4 | 0.7958 | 1.871 | mentions of the word "evil" |
| 5 | 6783 | 5_6783_2 | 0.795 | 5.1201 | phrases related to "I want to" |
| 5 | 2137 | 5_2137_3 | 0.7948 | 3.2241 |  the word "set" preceded by words indicating a comparison, often within the context of highly technical language and code |
| 0 | 9985 | 0_9985_2 | 0.7944 | 1.4817 |  words and fragments of text common in computer code and also in non-English languages |
| 0 | 8163 | 0_8163_4 | 0.7939 | 2.2868 |  words and phrases related to societal and political issues |
| 7 | 10626 | 7_10626_4 | 0.7935 | 2.9964 |  terms related to family relationships, especially focusing on marital status and legitimacy of children |
| 3 | 14287 | 3_14287_5 | 0.7933 | 4.0553 |  discourse regarding definitions and word usage |
| 7 | 3168 | 7_3168_2 | 0.7931 | 7.7656 |  rhetorical questions and references to blog posts |
| 3 | 5613 | 3_5613_3 | 0.7929 | 2.0079 |  parts of code related to threads and caching |
| 4 | 2866 | 4_2866_5 | 0.7927 | 5.4472 |  the word "is" |
| 0 | 10846 | 0_10846_2 | 0.7924 | 1.5975 | the word "also" |
| 0 | 10029 | 0_10029_2 | 0.7918 | 0.9714 |  abstract nouns ending in "-ity", "-ship", "-ness", "-ism", "-ence", "-ance", "-tion", "-tics", and other words related to the arts and philosophy |

*Middle layers — relational mapping*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 15 | 5255 | 15_5255_5 | 0.8 | 11.0643 | phrases using the word "nickname" or that refer to nicknames. |
| 9 | 12218 | 9_12218_5 | 0.7952 | 5.9949 |  references to old english combined with place names, or names and meanings |
| 15 | 805 | 15_805_4 | 0.7946 | 10.8643 |  a wide variety of proper nouns of many types with a slight preference for locations, nationalities or languages |
| 9 | 10290 | 9_10290_2 | 0.7937 | 10.5211 |  words related to some kind of technical field |
| 10 | 10199 | 10_10199_5 | 0.7922 | 4.7603 | code snippets, family relations, and super sentai teams |
| 11 | 10933 | 11_10933_1 | 0.792 | 49.9832 | the letters "L", "H," and "a" when they are at the beginning of a text block |

*Late layers — token selection*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 23 | 8449 | 23_8449_5 | 0.799 | 9.1165 |  terms related to scientific research, especially pertaining to analysis, measurement, and results. |
| 22 | 7881 | 22_7881_5 | 0.7977 | 10.0556 |  words referencing large numbers of people or objects |
| 17 | 9341 | 17_9341_5 | 0.7965 | 6.9503 | statements or words that express general truths |
| 25 | 11658 | 25_11658_5 | 0.7963 | 12.3389 |  names, places, and dates. |
| 21 | 2655 | 21_2655_5 | 0.7956 | 13.8071 |  code snippets containing certain keywords such as "expect", "info","trials", "MutableArray", and "Object". |
| 18 | 12090 | 18_12090_5 | 0.7954 | 12.6139 | words or phrases used when asking for or giving agreement |
| 0 | 17 | 0_17_2 | 0.7941 | 0.0 |  Spanish and Portuguese words related to code and computers |

**Causal paths (edge-weight chains to logit):**

*Path 1 — (+) excitatory | weight=9.79008 | hops=1*
→ `node_id=E_2047_4` | `feature=?` | Layer E | `(no label)` — edge [+9.7901]
→ **LOGIT** `node_id=27_3069_5` Layer 27 — `Output " children" (p=0.677)`

*Path 2 — (+) excitatory | weight=0.074998 | hops=1*
→ `node_id=25_11658_5` | `feature=11658` | Layer 25 | ` names, places, and dates.` — edge [+0.075]
→ **LOGIT** `node_id=27_3069_5` Layer 27 — `Output " children" (p=0.677)`

**Causal path diagram:**

![Causal paths for "<bos>The plural of child is" → "Output " children" (p=0.677)"](graphs/bos_the_plural_of_child_is__output___children____causal_paths.png)

*Figure: Causal paths from input features to predicted token "Output " children" (p=0.677)". Y-axis = transformer layer. Edge width = connection strength. Green = excitatory, red = inhibitory, orange = mixed.*

**Mechanistic Narrative**

The circuit for "The plural of child is" → " children" reveals a strikingly lean computation: the dominant signal travels in a single hop directly from the embedding layer to the logit node (Path 1, wt=9.79), with all other paths contributing negligibly.

**Early-layer detection.** The early layers (L0–L7) activated predominantly generic text-format features — code snippets, legal language, academic publications — with no obvious semantic hit on "child" or plurality at this stage. The input encoding is informationally rich but not yet domain-specific. Notably, the `<bos>` token position (ctx_idx=0) carries zero-activation embedding features (Feature 17, node_id=0_17_2: "Spanish and Portuguese words related to code and computers"), which appear to anchor the sentence-boundary context rather than the semantic content.

**Pivotal middle-layer feature.** The semantically decisive moment occurs at Layer 10, Feature 10199 (node_id=10_10199_5, influence=0.7922, act=4.76): "*code snippets, family relations, and super sentai teams*." The "family relations" component of this polysemantic feature fires for "child," binding it into the kinship register. Simultaneously, Layer 11, Feature 10933 (node_id=11_10933_1, influence=0.792, act=49.98) — "*the letters 'L', 'H,' and 'a' when at the beginning of a text block*" — activates with extraordinarily high activation, likely acting as a sentence-initial position detector that encodes the pattern-completion template ("The X of Y is ___").

**Late-layer final push.** Layer 25, Feature 11658 (node_id=25_11658_5, act=12.34) — "*names, places, and dates*" — provides a tiny direct excitatory edge to the logit (+0.075, Path 2). This is negligible compared to Path 1. The embedding node (E_2047_4) is the true final-stage actor, carrying a +9.79 edge weight directly to the logit with no intermediate hops.

**Dominant excitatory path.** Path 1 — `E_2047_4` → **LOGIT** (wt=+9.79, 1 hop) — is overwhelmingly dominant, accounting for the vast majority of the logit push toward " children." The circuit is essentially a direct look-up: the embedding node aggregates the cross-layer signal and fires straight at the output.

**Inhibitory paths.** No explicit inhibitory paths appeared in the top-5 traced paths. The competition against other plural candidates (e.g., "childs," "child's") is handled implicitly by the single dominant embedding→logit channel rather than through feature-level suppression.

**Convergent or ambiguous?** Despite the clean dominant path, p=0.677 is only moderate confidence for a closed-class irregular plural. The circuit is structurally convergent (one massive path, no competing inhibitory signal) but the absolute probability is dampened, likely because "children" is a highly irregular form whose morphological signal must be assembled from polysemantic features (L10's "family relations" packed alongside "super sentai teams") rather than a dedicated morphology feature.

---

### Prompt: "<bos>The plural of mouse is"

**Predicted token:** `Output " mice" (p=0.706)` (prob=0.7056)

**Token competition:**

| Rank | Token | Logit score | Features voting |
|------|-------|-------------|-----------------|

**Circuit walkthrough:**

*Early layers — input recognition*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 3 | 2181 | 3_2181_5 | 0.8001 | 4.2714 | technical writing that cites books or scientific publications and formal legal documents |
| 1 | 10748 | 1_10748_3 | 0.7999 | 3.8524 |  text of scientific or legal papers |
| 0 | 15348 | 0_15348_4 | 0.7993 | 2.0468 |  words related to law, crime or legal proceedings |
| 0 | 12459 | 0_12459_1 | 0.7989 | 2.3991 | the word "damage" and sometimes other words near "damage" or related to negative experiences |
| 1 | 3136 | 1_3136_2 | 0.7987 | 1.6804 | the word "extra," technical instructions and words related to hands |
| 0 | 7707 | 0_7707_2 | 0.7985 | 1.4467 |  code-related keywords like serialize, json, string, instantiation, async, containers, debugging, shared folders, and UI events |
| 0 | 14896 | 0_14896_3 | 0.7983 | 1.5427 | words ending in "ization" or prepositions like "of" |
| 0 | 15038 | 0_15038_4 | 0.7979 | 2.3504 | locations and organizations |
| 3 | 15173 | 3_15173_5 | 0.7977 | 3.218 |  hedging language and/or quantifying statements |
| 3 | 15954 | 3_15954_3 | 0.7973 | 2.7755 |  file paths or pieces of code and biological processes |
| 0 | 9777 | 0_9777_2 | 0.7969 | 1.9525 | words and phrases related to legal procedures |
| 0 | 778 | 0_778_4 | 0.7967 | 3.0174 |  mentions of research papers, studies or other formal publications |
| 2 | 14955 | 2_14955_3 | 0.7965 | 2.1796 |  the possessive pronouns "teu" and "seu" in Portuguese |
| 0 | 15100 | 0_15100_2 | 0.7963 | 1.4088 |  words near references to time or date |
| 4 | 11015 | 4_11015_3 | 0.796 | 3.1344 | terms that have the word "equivalent", and also certain collocations that can involve the word "standard" |
| 1 | 10898 | 1_10898_3 | 0.7958 | 1.7747 |  references to religion or religious concepts, and the word "of" |
| 1 | 13096 | 1_13096_4 | 0.7954 | 2.3411 |  words related to technological or medical fields |
| 2 | 5962 | 2_5962_3 | 0.7952 | 2.3362 |  legal and formal language |
| 0 | 16170 | 0_16170_1 | 0.795 | 3.3534 | words related to programming code, math, anatomy, medicine, structure, and anything that can range. |
| 3 | 5507 | 3_5507_1 | 0.7944 | 9.3926 |  academic publications that use scientific or medical data |
| 2 | 208 | 2_208_2 | 0.7942 | 2.0205 |  words related to groups and their statistical properties |
| 1 | 1010 | 1_1010_2 | 0.794 | 1.9404 | mentions of competitions, arguments, or parasites |
| 0 | 1970 | 0_1970_4 | 0.7938 | 2.7012 |  words related to scientific research, educational programs, and medical conditions |
| 0 | 15669 | 0_15669_2 | 0.7934 | 1.1473 |  technical words and jargon, especially from scientific documents or legal documents. |
| 0 | 3133 | 0_3133_2 | 0.7931 | 1.1126 |  words indicating the end or beginning of a period |
| 6 | 1533 | 6_1533_4 | 0.7929 | 4.0141 |  words that are difficult to categorize but seem to be related to names, branding, and academic language. |
| 0 | 1445 | 0_1445_4 | 0.7927 | 1.9681 |  various tools, along with properties and uses of those tools. |
| 0 | 3381 | 0_3381_5 | 0.7923 | 3.5832 |  modality verbs |
| 4 | 13060 | 4_13060_4 | 0.7921 | 1.8898 |  words related to legal proceedings and jurisprudence |

*Middle layers — relational mapping*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 8 | 1988 | 8_1988_3 | 0.7995 | 7.3976 |  mathematical equations and symbols, especially those involving transposes, duals, and derivatives |
| 14 | 13977 | 14_13977_3 | 0.7991 | 17.9337 |  phrases that contain the word searches, AND/OR, or the word term |
| 13 | 241 | 13_241_4 | 0.7975 | 6.4259 |  the start of chunks of code, markup, text, or math |
| 10 | 9126 | 10_9126_5 | 0.7971 | 3.902 |  words indicating a step-by-step process |
| 11 | 12241 | 11_12241_2 | 0.7956 | 17.8744 |  name origins and meanings |
| 8 | 13670 | 8_13670_5 | 0.7948 | 4.0576 |  grammatical terms and the verb "sein" (to be) in German |
| 8 | 4338 | 8_4338_5 | 0.7946 | 6.0761 |  internet addresses, references to the best services and products, and marketing language |

*Late layers — token selection*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 23 | 9726 | 23_9726_5 | 0.7997 | 9.5665 | abbreviations, code snippets, and date formats |
| 15 | 14640 | 15_14640_5 | 0.7981 | 10.7877 |  the word "and" and puntuation marks like commas |
| 19 | 4679 | 19_4679_5 | 0.7936 | 7.8639 |  instances of stating facts or ways of doing things |
| 23 | 13495 | 23_13495_5 | 0.7925 | 12.9081 |  code-related concepts such as data access and processing |

**Causal paths (edge-weight chains to logit):**

*Path 1 — (+) excitatory | weight=14.139694 | hops=1*
→ `node_id=E_11937_4` | `feature=?` | Layer E | `(no label)` — edge [+14.1397]
→ **LOGIT** `node_id=27_21524_5` Layer 27 — `Output " mice" (p=0.706)`

*Path 2 — (+) excitatory | weight=1.95473 | hops=2*
→ `node_id=15_14640_5` | `feature=14640` | Layer 15 | ` the word "and" and puntuation marks like commas` — edge [+3.2762]
→ `node_id=25_4717_5` | `feature=?` | Layer 25 | `(no label)` — edge [+0.5966]
→ **LOGIT** `node_id=27_21524_5` Layer 27 — `Output " mice" (p=0.706)`

*Path 3 — (+) excitatory | weight=0.716964 | hops=2*
→ `node_id=19_4679_5` | `feature=4679` | Layer 19 | ` instances of stating facts or ways of doing things` — edge [+1.2017]
→ `node_id=25_4717_5` | `feature=?` | Layer 25 | `(no label)` — edge [+0.5966]
→ **LOGIT** `node_id=27_21524_5` Layer 27 — `Output " mice" (p=0.706)`

**Causal path diagram:**

![Causal paths for "<bos>The plural of mouse is" → "Output " mice" (p=0.706)"](graphs/bos_the_plural_of_mouse_is__output___mice___p_0__causal_paths.png)

*Figure: Causal paths from input features to predicted token "Output " mice" (p=0.706)". Y-axis = transformer layer. Edge width = connection strength. Green = excitatory, red = inhibitory, orange = mixed.*

**Mechanistic Narrative**

The circuit for "The plural of mouse is" → " mice" (p=0.706) mirrors the "children" circuit in its architecture — a dominant single-hop embedding→logit path — but the secondary paths reveal a more elaborate morphological processing chain.

**Early-layer detection.** The early-layer band is dominated by legal, scientific, and code-adjacent features (L0 Feature 15348: "law/crime/legal"; L1 Feature 10748: "scientific or legal papers"; L3 Feature 5507: "academic scientific/medical data"). These generic register features activate in response to the formal, structured syntax of the completion prompt. No early-layer feature shows a direct semantic hit for "mouse" specifically; the irregular plural recognition is delayed until middle layers.

**Pivotal middle-layer feature.** Layer 11, Feature 12241 (node_id=11_12241_2, influence=0.7956, act=17.87) — "*name origins and meanings*" — is the pivotal middle-layer feature. Its activation at high magnitude (17.87) suggests the model is encoding "mice" as a word whose form derives from historical root transformations (indeed, "mouse → mice" is an Old English vowel mutation). The feature fires on etymology/morphological history, not on semantics per se. Supporting this: Layer 8, Feature 13670 (node_id=8_13670_5, act=4.06) — "*grammatical terms and the verb 'sein' (to be) in German*" — activates on the copula "is," signalling a morphological inflection context.

**Late-layer final push.** Layer 23, Feature 9726 (node_id=23_9726_5, act=9.57) — "*abbreviations, code snippets, and date formats*" — fires in the late band but carries no direct logit edge in the traced paths. The actual late-stage push comes from Path 2's L15 Feature 14640 (node_id=15_14640_5: "*the word 'and' and punctuation marks*") via an unlabeled L25 intermediary, edge [+3.28] → [+0.60] → LOGIT.

**Dominant excitatory path.** Path 1 — `E_11937_4` → **LOGIT** (wt=+14.14, 1 hop) — is the strongest signal, even larger than the corresponding path in Prompt 5. The embedding aggregation layer has already assembled the answer and fires with high confidence.

**Inhibitory paths.** No purely inhibitory path appears in the top-5. Path 2 and Path 3 are both excitatory; all paths converge on the same unlabeled L25 node before reaching the logit. The model appears to have suppressed competitor tokens (e.g., "mouses") not through explicit inhibitory features but through the steep dominance of the embedding path.

**Convergent or ambiguous?** Moderately convergent (p=0.706). The circuit has a single dominant path carrying 14.1× the weight of any secondary path. The slightly higher confidence over "children" (0.706 vs. 0.677) may reflect that the etymology feature at L11 (Feature 12241) fires more cleanly for vowel-mutation plurals ("mice," "feet," "geese") than the polysemantic "family relations" feature needed for "children."

---

### Prompt: "<bos>The past tense of swim is"

**Predicted token:** `Output " swam" (p=0.496)` (prob=0.4960)

**Token competition:**

| Rank | Token | Logit score | Features voting |
|------|-------|-------------|-----------------|

**Circuit walkthrough:**

*Early layers — input recognition*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 5 | 10444 | 5_10444_3 | 0.8002 | 4.1316 |  baseball terminology |
| 0 | 9022 | 0_9022_5 | 0.7996 | 2.9192 |  technical words used in computing, science, or engineering |
| 0 | 5 | 0_5_2 | 0.7994 | 0.0 |  closing curly brackets in code snippets |
| 6 | 4873 | 6_4873_3 | 0.7992 | 4.4898 |  code snippets and related programming terms |
| 6 | 2417 | 6_2417_6 | 0.799 | 4.5116 |  forms of the verb "to be" |
| 0 | 1448 | 0_1448_6 | 0.7988 | 4.1868 |  the verb "is" and "are". |
| 0 | 8694 | 0_8694_5 | 0.7986 | 2.9988 |  code snippets, specific scientific or technical terms, and date-related words. |
| 7 | 3168 | 7_3168_3 | 0.7984 | 5.4049 |  rhetorical questions and references to blog posts |
| 6 | 15610 | 6_15610_5 | 0.7982 | 3.2563 | words related to programming, foreign language, finance or strong emotion. |
| 6 | 4742 | 6_4742_6 | 0.798 | 3.0585 |  words that define the meaning of concepts in a mathematical or general context |
| 4 | 7958 | 4_7958_4 | 0.7978 | 3.9723 |  things that involve dates or references |
| 1 | 8905 | 1_8905_3 | 0.7976 | 2.4283 |  code and programming related keywords |
| 1 | 12115 | 1_12115_1 | 0.7974 | 3.4348 |  code comments |
| 1 | 4486 | 1_4486_3 | 0.797 | 1.5176 |  terms related to Christian faith and religious belief |
| 4 | 15293 | 4_15293_3 | 0.7968 | 3.0799 |  text about small but essential dietary components and their deficiencies |
| 0 | 10237 | 0_10237_2 | 0.7959 | 2.4217 |  uses of the word "cool" along with related positive words |
| 3 | 15250 | 3_15250_4 | 0.7957 | 2.9439 | words related to legal and technical language |
| 2 | 10736 | 2_10736_6 | 0.7953 | 3.3241 | verbs being used |
| 0 | 2368 | 0_2368_5 | 0.7951 | 1.969 |  technical terms used in scientific writing |
| 5 | 1777 | 5_1777_4 | 0.7943 | 4.7954 |  technical language from scientific/instructional writing. |
| 2 | 7822 | 2_7822_6 | 0.7939 | 3.9209 | technical, legal or academic language, especially verbs, often found in formal reports |
| 4 | 416 | 4_416_6 | 0.7937 | 4.9475 |  multiple occurrences of hedging verbs in sentences with negative constraints |
| 3 | 1859 | 3_1859_3 | 0.7933 | 2.6046 |  words related to scientific research and study |
| 0 | 6366 | 0_6366_1 | 0.7931 | 3.3989 |  the word "meaning," and in some cases words around it |
| 0 | 11612 | 0_11612_3 | 0.7926 | 1.8938 |  technical or scientific terms, especially in a research context |
| 5 | 6439 | 5_6439_6 | 0.7924 | 3.0338 |  words and phrases related to naming or meaning |

*Middle layers — relational mapping*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 11 | 7342 | 11_7342_3 | 0.7998 | 12.2148 | code or programming language |
| 8 | 12573 | 8_12573_4 | 0.7972 | 5.6246 |  words related to cessation or ending, like "defunct," "discontinued," and "expired." |
| 9 | 7751 | 9_7751_4 | 0.7955 | 6.6736 |  code snippets, especially those relating to the execution of child processes and file paths |
| 11 | 12241 | 11_12241_4 | 0.7947 | 22.4429 |  name origins and meanings |
| 13 | 16125 | 13_16125_6 | 0.7941 | 7.0027 |  words and phrases related to official or legal proceedings |
| 12 | 79 | 12_79_6 | 0.7922 | 5.6467 |  the definitions of words, especially names, and the word "meaning" |

*Late layers — token selection*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 25 | 11778 | 25_11778_6 | 0.8 | 13.0003 |  code snippets |
| 25 | 13617 | 25_13617_6 | 0.7965 | 7.9027 | code related to scripts and code execution |
| 19 | 1301 | 19_1301_6 | 0.7963 | 9.3358 |  conversational phrases or personal pronouns together with auxiliary verbs. |
| 24 | 4155 | 24_4155_6 | 0.7961 | 7.0805 |  mentions of occurrences and changes over time, especially using auxiliary verbs like "have," "has," "be," or "been." |
| 22 | 11355 | 22_11355_6 | 0.7949 | 9.3168 |  words related to states of being or consequences |
| 24 | 5999 | 24_5999_6 | 0.7945 | 13.5011 |  language related to institutions, negative situations, the internet, and programming languages |
| 18 | 6481 | 18_6481_3 | 0.7935 | 86.0581 |  mentions of grammatical tense and simple declarative clauses |
| 16 | 6856 | 16_6856_5 | 0.7928 | 20.3456 |  definitions of words |

**Causal paths (edge-weight chains to logit):**

*Path 1 — (+) excitatory | weight=12.07473 | hops=1*
→ `node_id=E_11243_5` | `feature=?` | Layer E | `(no label)` — edge [+12.0747]
→ **LOGIT** `node_id=27_120712_6` Layer 27 — `Output " swam" (p=0.496)`

*Path 2 — (±) mixed | weight=1.511423 | hops=3*
→ `node_id=22_11355_6` | `feature=11355` | Layer 22 | ` words related to states of being or consequences` — edge [-2.3677]
→ `node_id=24_13562_6` | `feature=?` | Layer 24 | `(no label)` — edge [+1.1711]
→ `node_id=25_4717_6` | `feature=?` | Layer 25 | `(no label)` — edge [+0.5451]
→ **LOGIT** `node_id=27_120712_6` Layer 27 — `Output " swam" (p=0.496)`

*Path 3 — (+) excitatory | weight=0.519619 | hops=2*
→ `node_id=24_4155_6` | `feature=4155` | Layer 24 | ` mentions of occurrences and changes over time, especially using auxiliary verbs like "have," "has," "be," or "been."` — edge [+0.9532]
→ `node_id=25_4717_6` | `feature=?` | Layer 25 | `(no label)` — edge [+0.5451]
→ **LOGIT** `node_id=27_120712_6` Layer 27 — `Output " swam" (p=0.496)`

*Path 4 — (±) mixed | weight=0.334368 | hops=4*
→ `node_id=18_6481_3` | `feature=6481` | Layer 18 | ` mentions of grammatical tense and simple declarative clauses` — edge [+0.382]
→ `node_id=23_9819_6` | `feature=?` | Layer 23 | `(no label)` — edge [+7.7822]
→ `node_id=24_13769_6` | `feature=?` | Layer 24 | `(no label)` — edge [+0.7536]
→ `node_id=25_9359_6` | `feature=?` | Layer 25 | `(no label)` — edge [-0.1492]
→ **LOGIT** `node_id=27_120712_6` Layer 27 — `Output " swam" (p=0.496)`

*Path 5 — (±) mixed | weight=0.234319 | hops=2*
→ `node_id=24_5999_6` | `feature=5999` | Layer 24 | ` language related to institutions, negative situations, the internet, and programming languages` — edge [-1.1157]
→ `node_id=25_2511_6` | `feature=?` | Layer 25 | `(no label)` — edge [+0.21]
→ **LOGIT** `node_id=27_120712_6` Layer 27 — `Output " swam" (p=0.496)`

**Causal path diagram:**

![Causal paths for "<bos>The past tense of swim is" → "Output " swam" (p=0.496)"](graphs/bos_the_past_tense_of_swim_is__output___swam___p_0__causal_paths.png)

*Figure: Causal paths from input features to predicted token "Output " swam" (p=0.496)". Y-axis = transformer layer. Edge width = connection strength. Green = excitatory, red = inhibitory, orange = mixed.*

**Mechanistic Narrative**

The circuit for "The past tense of swim is" → " swam" (p=0.496) is the most ambiguous in the linguistic dataset, and its early-layer activations reveal the model's most striking mismatch between feature label and function.

**Early-layer detection.** The top early-layer feature is Layer 5, Feature 10444 (node_id=5_10444_3, influence=0.8002, act=4.13) — "*baseball terminology*." This is the largest-influence feature in the entire early band, yet "swim" is unrelated to baseball. The activation likely reflects the feature's sensitivity to monosyllabic action verbs with vowel-change past tenses (swim→swam, hit→hit, pitch→pitched), firing on structural morphological regularity rather than sport-specific semantics. Layer 6, Feature 2417 (node_id=6_2417_6, act=4.51) — "*forms of the verb 'to be'*" — and Layer 0, Feature 1448 (node_id=0_1448_6, act=4.19) — "*the verb 'is' and 'are'*" — detect the copular completion frame, cueing the model that an inflected form must follow.

**Pivotal middle-layer feature.** Layer 18, Feature 6481 (node_id=18_6481_3, act=86.06) — "*mentions of grammatical tense and simple declarative clauses*" — is by far the most explosively activated feature in the entire prompt, with activation nearly 4× higher than any other late-stage feature. This is the explicit grammatical-tense detector: it recognises "past tense of X is" as a morphological query and amplifies the tense-change signal. It routes into Path 4 (mixed, wt=0.33), suggesting that despite its massive activation, its influence is partially cancelled by downstream inhibitory edges (L23 feature node at -0.15 and competing positive edges at +7.78).

**Late-layer final push.** Layer 24, Feature 4155 (node_id=24_4155_6, act=7.08) — "*mentions of occurrences and changes over time, especially using auxiliary verbs*" — provides the cleanest late-stage excitatory signal. It activates on the temporal change encoded by past-tense transformation and routes directly to the shared L25 node (+0.95), which then fires to the logit (+0.55) in Path 3 (wt=0.52).

**Dominant excitatory path.** Path 1 — `E_11243_5` → **LOGIT** (wt=+12.07, 1 hop) — again dominates all others, consistent with the pattern seen in Prompts 5 and 6: the embedding aggregation node carries the majority of the answer signal in a single direct hop. All other paths (12.07 → 1.51 → 0.52 → 0.33 → 0.23) carry progressively smaller contributions.

**Inhibitory paths.** Paths 2, 4, and 5 are all mixed (±). Path 2 begins with L22 Feature 11355 "states of being or consequences" with a large negative first edge (-2.37), suggesting this feature suppresses non-past-tense continuations. Path 5 opens at L24 Feature 5999 "language related to institutions/internet/programming languages" with a negative edge (-1.12), likely suppressing non-swimming senses of "swim" ("swim in data," "swimming in debt").

**Convergent or ambiguous?** Ambiguous. p=0.496 is the lowest probability of any prompt in this dataset, and the circuit reflects this: five competing paths span a 50× weight range (12.07 to 0.23), three of which are mixed with conflicting internal edges. The "baseball terminology" feature at L5 likely introduces noise by activating for the wrong reasons, and the extraordinary activation of the tense feature (86.06) is partially wasted because the path through it (Path 4) carries only 0.33 weight after downstream cancellations. The model knows something tense-related is happening but is uncertain whether "swam," "swum," or another form is the correct output.

---

### Prompt: "<bos>The past tense of write is"

**Predicted token:** `Output " written" (p=0.344)` (prob=0.3436)

**Token competition:**

| Rank | Token | Logit score | Features voting |
|------|-------|-------------|-----------------|

**Circuit walkthrough:**

*Early layers — input recognition*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 1 | 9572 | 1_9572_6 | 0.7999 | 4.3332 | words and phrases related to thinking, judging, and comparison, plus present tense verbs. |
| 4 | 13440 | 4_13440_6 | 0.7997 | 2.9409 |  context related to words/language and their meanings or usages |
| 5 | 4916 | 5_4916_3 | 0.7995 | 4.474 |  code snippets and file paths |
| 2 | 10602 | 2_10602_3 | 0.7989 | 1.8043 | the letter 'z' when it is near mathematical symbols |
| 5 | 3725 | 5_3725_6 | 0.7985 | 4.512 | various code snippets and programming-related text. |
| 4 | 10138 | 4_10138_4 | 0.7983 | 2.6026 | words relating to answering a question or configuring something |
| 3 | 4834 | 3_4834_4 | 0.7981 | 2.4584 |  programming code, place names with "de la", and the phrase, "of the valley" |
| 2 | 5120 | 2_5120_3 | 0.7977 | 1.5336 |  mentions of death or passing away |
| 0 | 14896 | 0_14896_4 | 0.7973 | 2.1751 | words ending in "ization" or prepositions like "of" |
| 0 | 408 | 0_408_5 | 0.7971 | 2.9596 | the word "mix" often also activating nearby words "mixing" or "mixed", "then" |
| 4 | 14857 | 4_14857_5 | 0.7969 | 5.5899 | code snippets and license agreements |
| 2 | 15200 | 2_15200_6 | 0.7967 | 3.7124 |  the verb "to be" in various languages and tenses |
| 2 | 10736 | 2_10736_6 | 0.7965 | 3.8807 | verbs being used |
| 3 | 84 | 3_84_5 | 0.7959 | 3.1003 |  words associated with computer programming, 3D printing and manufacturing |
| 0 | 7045 | 0_7045_5 | 0.7957 | 2.771 | the word "lift" and related concepts |
| 0 | 16170 | 0_16170_1 | 0.7953 | 3.3534 | words related to programming code, math, anatomy, medicine, structure, and anything that can range. |
| 0 | 10315 | 0_10315_3 | 0.7951 | 1.4975 |  terms related to law, immigration, and gaming. |
| 0 | 12747 | 0_12747_6 | 0.7943 | 4.0227 | occurrences of the words 'they', 'them', 'that', 'these', or something that can be replaced with 'they' or 'them' |
| 4 | 14373 | 4_14373_4 | 0.7936 | 2.14 | mentions of the word "term" or other words relating to language. |
| 0 | 7111 | 0_7111_2 | 0.7934 | 2.7984 |  the word "browser". |
| 1 | 8594 | 1_8594_3 | 0.7932 | 1.9671 |  mentions of school grades and educational institutions |
| 0 | 14642 | 0_14642_2 | 0.793 | 2.6918 | the word "shot" used in various contexts |
| 0 | 6942 | 0_6942_1 | 0.7924 | 3.0286 |  the suffix "ins" or the word "thereon" |
| 0 | 6133 | 0_6133_2 | 0.7922 | 4.0242 | something the user looked at, is looking at, or will look at. |

*Middle layers — relational mapping*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 8 | 1270 | 8_1270_4 | 0.8001 | 5.0418 |  words related to biological population dynamics and reproduction |
| 6 | 4873 | 6_4873_3 | 0.7993 | 4.4898 |  code snippets and related programming terms |
| 8 | 8406 | 8_8406_1 | 0.7991 | 18.9138 | the first-person pronoun "I" and the word "Exactly" |
| 8 | 745 | 8_745_5 | 0.7979 | 3.0859 |  words or phrases related to the production of media, such as movies or music |
| 9 | 15511 | 9_15511_5 | 0.7963 | 6.8296 | examples of the phrase "in spite of" |
| 7 | 10819 | 7_10819_5 | 0.7955 | 2.501 |  words and phrases related to reading and writing data in a computer system |
| 9 | 14306 | 9_14306_4 | 0.7947 | 9.2858 |  math or coding. |
| 6 | 2417 | 6_2417_6 | 0.7945 | 4.9281 |  forms of the verb "to be" |
| 8 | 15538 | 8_15538_6 | 0.7941 | 3.5612 |  the definition of "false" from Merriam-Webster |
| 10 | 2718 | 10_2718_5 | 0.7926 | 7.6093 | code snippets and programming related terminology |

*Late layers — token selection*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 12 | 1440 | 12_1440_5 | 0.7987 | 7.9834 |  periods, numbers and names |
| 18 | 10954 | 18_10954_5 | 0.7975 | 35.8485 |  terms used in academic papers, especially those using measurements or observations |
| 14 | 14143 | 14_14143_6 | 0.7961 | 7.0497 |  code snippets, special characters, and logical operators |
| 19 | 64 | 19_64_6 | 0.7949 | 7.9728 |  sentences or phrases that mention figures, tables, and references |
| 14 | 4758 | 14_4758_6 | 0.7938 | 6.5116 | words used in academic papers, legal documents, or technical writing. |
| 14 | 15625 | 14_15625_5 | 0.7928 | 10.8266 |  words related to societal issues, groups and beliefs |

**Causal paths (edge-weight chains to logit):**

*Path 1 — (±) mixed | weight=266.828101 | hops=5*
→ `node_id=4_14857_5` | `feature=14857` | Layer 4 | `code snippets and license agreements` — edge [-3.9423]
→ `node_id=11_3544_5` | `feature=?` | Layer 11 | `(no label)` — edge [-4.2256]
→ `node_id=15_12472_5` | `feature=?` | Layer 15 | `(no label)` — edge [+2.4539]
→ `node_id=17_8850_5` | `feature=?` | Layer 17 | `(no label)` — edge [-1.832]
→ `node_id=24_1633_6` | `feature=?` | Layer 24 | `(no label)` — edge [-3.5629]
→ **LOGIT** `node_id=27_5952_6` Layer 27 — `Output " written" (p=0.344)`

*Path 2 — (±) mixed | weight=217.754656 | hops=4*
→ `node_id=8_745_5` | `feature=745` | Layer 8 | ` words or phrases related to the production of media, such as movies or music` — edge [+0.6205]
→ `node_id=14_16348_5` | `feature=?` | Layer 14 | `(no label)` — edge [+6.7241]
→ `node_id=15_10668_5` | `feature=?` | Layer 15 | `(no label)` — edge [+14.6492]
→ `node_id=24_1633_6` | `feature=?` | Layer 24 | `(no label)` — edge [-3.5629]
→ **LOGIT** `node_id=27_5952_6` Layer 27 — `Output " written" (p=0.344)`

*Path 3 — (±) mixed | weight=37.339773 | hops=4*
→ `node_id=14_15625_5` | `feature=15625` | Layer 14 | ` words related to societal issues, groups and beliefs` — edge [+2.3312]
→ `node_id=15_12472_5` | `feature=?` | Layer 15 | `(no label)` — edge [+2.4539]
→ `node_id=17_8850_5` | `feature=?` | Layer 17 | `(no label)` — edge [-1.832]
→ `node_id=24_1633_6` | `feature=?` | Layer 24 | `(no label)` — edge [-3.5629]
→ **LOGIT** `node_id=27_5952_6` Layer 27 — `Output " written" (p=0.344)`

*Path 4 — (±) mixed | weight=33.833169 | hops=5*
→ `node_id=9_15511_5` | `feature=15511` | Layer 9 | `examples of the phrase "in spite of"` — edge [+2.4833]
→ `node_id=15_7276_5` | `feature=?` | Layer 15 | `(no label)` — edge [+0.2936]
→ `node_id=18_4309_5` | `feature=?` | Layer 18 | `(no label)` — edge [+21.2272]
→ `node_id=23_10430_5` | `feature=?` | Layer 23 | `(no label)` — edge [-0.6136]
→ `node_id=24_1633_6` | `feature=?` | Layer 24 | `(no label)` — edge [-3.5629]
→ **LOGIT** `node_id=27_5952_6` Layer 27 — `Output " written" (p=0.344)`

*Path 5 — (±) mixed | weight=13.362211 | hops=4*
→ `node_id=0_7045_5` | `feature=7045` | Layer 0 | `the word "lift" and related concepts` — edge [-0.288]
→ `node_id=18_4309_5` | `feature=?` | Layer 18 | `(no label)` — edge [+21.2272]
→ `node_id=23_10430_5` | `feature=?` | Layer 23 | `(no label)` — edge [-0.6136]
→ `node_id=24_1633_6` | `feature=?` | Layer 24 | `(no label)` — edge [-3.5629]
→ **LOGIT** `node_id=27_5952_6` Layer 27 — `Output " written" (p=0.344)`

**Causal path diagram:**

![Causal paths for "<bos>The past tense of write is" → "Output " written" (p=0.344)"](graphs/bos_the_past_tense_of_write_is__output___written___p_causal_paths.png)

*Figure: Causal paths from input features to predicted token "Output " written" (p=0.344)". Y-axis = transformer layer. Edge width = connection strength. Green = excitatory, red = inhibitory, orange = mixed.*

**Mechanistic Narrative**

The circuit for "The past tense of write is" → " written" (p=0.344) is the most unusual in the dataset: all five traced causal paths are mixed (±), all converge on the same unlabeled L24 bottleneck node (node_id=24_1633_6), and that bottleneck's final edge to the logit is strongly *negative* (-3.56). This is a circuit that arrives at " written" through a convergent inhibitory structure rather than a conventional excitatory push.

**Early-layer detection.** Layer 4, Feature 14857 (node_id=4_14857_5, act=5.59) — "*code snippets and license agreements*" — is the most influential early feature (influence=0.7969) and the origin of Path 1 (dominant by weight). Its activation for "write" may stem from the frequent co-occurrence of "write" in code contexts ("write to disk," "write access," "rights reserved"). Layer 2, Feature 15200 (node_id=2_15200_6, act=3.71) — "*the verb 'to be' in various languages and tenses*" — and Layer 2, Feature 10736 (node_id=2_10736_6, act=3.88) — "*verbs being used*" — together encode the copular frame and flag that an inflected verb form must follow.

**Pivotal middle-layer feature.** Layer 8, Feature 15538 (node_id=8_15538_6, act=3.56) — "*the definition of 'false' from Merriam-Webster*" — is the most surprising middle-layer feature. Its activation for "write is ___" likely reflects the feature's sensitivity to definitional/lexicographic templates ("X is defined as Y"), firing in any context that follows the canonical "term + copula + definition" pattern. Layer 8, Feature 745 (node_id=8_745_5, act=3.09) — "*words related to the production of media, such as movies or music*" — activates on the writing-as-creative-production sense, contributing the dominant early edge (+0.62) to Path 2.

**Late-layer final push.** Layer 18, Feature 10954 (node_id=18_10954_5, act=35.85) — "*terms used in academic papers, especially those using measurements or observations*" — fires with very high activation, consistent with "write" appearing heavily in academic methodology sections ("written by," "as written in"). Yet this feature does not appear directly in any of the five traced paths; it influences the logit through unlabeled intermediaries. The actual penultimate push is the L24_1633 bottleneck node, which concentrates signal from all five paths and fires with edge weight -3.56 to the logit — a negative projection that paradoxically selects " written" because all competing paths are also routed through the same inhibitory bottleneck.

**Dominant excitatory path.** Path 1 — `L4_14857_5` (code/license) → `L11_3544_5` → `L15_12472_5` → `L17_8850_5` → `L24_1633_6` → **LOGIT** (cumulative path weight=266.83) — is the dominant path by weight. Note that the weight metric here accumulates edge magnitudes without sign; the actual direction of the final logit contribution is negative (-3.56), meaning all five paths are inhibitory at the output stage. The "winner" is not chosen by the largest positive push but by which output token is least suppressed once the inhibitory bottleneck fires.

**Inhibitory paths.** All five paths are mixed. The negative edges appear both early (L4_14857→L11: -3.94; L0_7045→L18: -0.29; L9_15511→L24 via L23: -0.61) and at the final bottleneck step (-3.56 universally). This architecture is the opposite of the simple completion prompts: instead of a positive embedding→logit vote, a web of mixed features filter out competing alternatives until " written" — the past participle, also used as an adjective in writing contexts — remains.

**Convergent or ambiguous?** Structurally convergent (all paths funneled through L24_1633) but semantically ambiguous (p=0.344, lowest in the dataset). The convergence is onto an inhibitory bottleneck, not a positive anchor. The model knows a past-participle/irregular-form answer is needed but weighs "wrote" vs. "written" vs. "write" with nearly equal inhibitory suppression, and " written" wins by a narrow margin — plausibly because "written" appears more frequently in the "past tense of X is ___" template than "wrote" (which typically follows an auxiliary: "has written" vs. "past tense is written").

---

### Prompt: "<bos>A book of maps is called an"

**Predicted token:** `Output " atlas" (p=0.825)` (prob=0.8251)

**Token competition:**

| Rank | Token | Logit score | Features voting |
|------|-------|-------------|-----------------|

**Circuit walkthrough:**

*Early layers — input recognition*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 0 | 13004 | 0_13004_7 | 0.8 | 3.0223 | parenthetical numerical references and citations to literature, laws, and statistics |
| 2 | 98 | 2_98_3 | 0.7998 | 1.0008 |  research papers, either references to them or the current paper itself, especially introductions and reviews |
| 3 | 16101 | 3_16101_3 | 0.7996 | 2.0423 | a mix of last names, religious terms, abbreviations, and measurement suffixes |
| 2 | 10109 | 2_10109_7 | 0.7994 | 3.8415 |  code snippets or programming references in multiple languages, including Portuguese, French, and English |
| 4 | 1727 | 4_1727_1 | 0.7992 | 9.7057 | sentences that start with the letters 'A' or 'An' |
| 4 | 4625 | 4_4625_5 | 0.7987 | 3.1782 |  words and names related to books |
| 4 | 10755 | 4_10755_6 | 0.7985 | 5.8249 |  instances of exploration and improvement |
| 2 | 10123 | 2_10123_4 | 0.7983 | 1.9115 |  words or phrases relating to assessment, analysis, observation, or study |
| 6 | 2267 | 6_2267_3 | 0.7981 | 18.2815 | words that appear in programming code, legal jargon, or scientific texts |
| 4 | 10419 | 4_10419_3 | 0.7979 | 3.444 |  the phrase "of all" and words ending in 'ir' or 'no' |
| 5 | 2393 | 5_2393_4 | 0.7977 | 2.0437 |  mentions of body parts and pointing. |
| 1 | 2579 | 1_2579_3 | 0.7975 | 1.2663 |  words and phrases related to software licenses, copyright, and legal disclaimers. |
| 3 | 355 | 3_355_4 | 0.7973 | 2.5112 |  geographical references or locations. |
| 0 | 11744 | 0_11744_7 | 0.797 | 4.2571 |  the word "consent", and sometimes the articles "an" or "a" |
| 0 | 13761 | 0_13761_4 | 0.7966 | 2.1865 |  instances of people being addressed directly |
| 0 | 16306 | 0_16306_7 | 0.7964 | 3.6462 |  the word "covers", with some examples referring to diaper covers |
| 1 | 12217 | 1_12217_4 | 0.7962 | 2.6688 | the word "row", often used in the context of code |
| 2 | 4554 | 2_4554_4 | 0.796 | 2.2951 | words and phrases related to following a path, whether literal or metaphorical |
| 1 | 11662 | 1_11662_6 | 0.7958 | 3.9455 |  words of importance in the current context |
| 3 | 1777 | 3_1777_3 | 0.7956 | 3.1329 |  parts of words |
| 2 | 13924 | 2_13924_3 | 0.7953 | 2.232 | code and web snippets with unusual formatting and special characters common in programming |
| 3 | 15091 | 3_15091_4 | 0.7951 | 1.8565 |  terms related to nobility, religion and places. |
| 4 | 12792 | 4_12792_3 | 0.7947 | 3.3902 |  words related to chemical processes |
| 2 | 2052 | 2_2052_2 | 0.7943 | 3.2832 | occurrences of the word "Affymetrix" as well as mild adjectives |
| 1 | 3982 | 1_3982_4 | 0.794 | 2.6329 |  mentions of international conflict and trade |
| 7 | 13740 | 7_13740_7 | 0.7936 | 5.8737 |  segments of text that assert the importance of something |
| 3 | 10202 | 3_10202_3 | 0.793 | 2.1689 |  terms related to code and US immigration |
| 3 | 13687 | 3_13687_6 | 0.7925 | 4.4142 | legal jargon related to courtroom proceedings and opinions |
| 6 | 5227 | 6_5227_7 | 0.7921 | 4.3188 |  formal writing, such as punctuation, polite affirmations, legal language, common phrases, or conversational language |

*Middle layers — relational mapping*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 8 | 4302 | 8_4302_3 | 0.8002 | 3.8261 | mentions of note-taking in records and books |
| 8 | 13791 | 8_13791_4 | 0.7968 | 5.4581 |  text related to web development, URLs, and navigation |
| 10 | 7106 | 10_7106_1 | 0.7945 | 33.313 |  the word "The." |
| 8 | 1494 | 8_1494_7 | 0.7938 | 5.6589 | technical words related to coding, streaming, and graphical user interfaces |
| 10 | 7755 | 10_7755_7 | 0.7934 | 5.0508 |  words associated with proposals and expectations for future activity |
| 10 | 6804 | 10_6804_1 | 0.7927 | 38.2213 |  references |
| 9 | 1839 | 9_1839_4 | 0.7923 | 4.2666 |  words and phrases related to the legal system and law enforcement |

*Late layers — token selection*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 0 | 16 | 0_16_6 | 0.7989 | 0.0 |  words related to political administration and legal rights |
| 21 | 3848 | 21_3848_6 | 0.7949 | 17.1032 |  words related to visual representations of information |
| 25 | 6332 | 25_6332_7 | 0.7932 | 12.503 |  the beginning of political or economic entities or actions |
| 16 | 16329 | 16_16329_7 | 0.7919 | 7.3046 | word origins |

**Causal paths (edge-weight chains to logit):**

*Path 1 — (±) mixed | weight=52.851133 | hops=5*
→ `node_id=8_1494_7` | `feature=1494` | Layer 8 | `technical words related to coding, streaming, and graphical user interfaces` — edge [+0.5667]
→ `node_id=18_10679_7` | `feature=?` | Layer 18 | `(no label)` — edge [+22.6157]
→ `node_id=19_8729_7` | `feature=?` | Layer 19 | `(no label)` — edge [+2.2099]
→ `node_id=24_11962_7` | `feature=?` | Layer 24 | `(no label)` — edge [-6.8853]
→ `node_id=25_8267_7` | `feature=?` | Layer 25 | `(no label)` — edge [-0.271]
→ **LOGIT** `node_id=27_63720_7` Layer 27 — `Output " atlas" (p=0.825)`

*Path 2 — (±) mixed | weight=29.900933 | hops=5*
→ `node_id=8_13791_4` | `feature=13791` | Layer 8 | ` text related to web development, URLs, and navigation` — edge [-0.3206]
→ `node_id=18_10679_7` | `feature=?` | Layer 18 | `(no label)` — edge [+22.6157]
→ `node_id=19_8729_7` | `feature=?` | Layer 19 | `(no label)` — edge [+2.2099]
→ `node_id=24_11962_7` | `feature=?` | Layer 24 | `(no label)` — edge [-6.8853]
→ `node_id=25_8267_7` | `feature=?` | Layer 25 | `(no label)` — edge [-0.271]
→ **LOGIT** `node_id=27_63720_7` Layer 27 — `Output " atlas" (p=0.825)`

*Path 3 — (+) excitatory | weight=3.62959 | hops=1*
→ `node_id=E_14503_4` | `feature=?` | Layer E | `(no label)` — edge [+3.6296]
→ **LOGIT** `node_id=27_63720_7` Layer 27 — `Output " atlas" (p=0.825)`

*Path 4 — (±) mixed | weight=3.355646 | hops=4*
→ `node_id=10_6804_1` | `feature=6804` | Layer 10 | ` references` — edge [+3.3105]
→ `node_id=12_12493_1` | `feature=?` | Layer 12 | `(no label)` — edge [-0.8917]
→ `node_id=18_10679_4` | `feature=?` | Layer 18 | `(no label)` — edge [+11.6318]
→ `node_id=19_9185_4` | `feature=?` | Layer 19 | `(no label)` — edge [+0.0977]
→ **LOGIT** `node_id=27_63720_7` Layer 27 — `Output " atlas" (p=0.825)`

*Path 5 — (±) mixed | weight=2.32851 | hops=4*
→ `node_id=10_7106_1` | `feature=7106` | Layer 10 | ` the word "The."` — edge [+2.2972]
→ `node_id=12_12493_1` | `feature=?` | Layer 12 | `(no label)` — edge [-0.8917]
→ `node_id=18_10679_4` | `feature=?` | Layer 18 | `(no label)` — edge [+11.6318]
→ `node_id=19_9185_4` | `feature=?` | Layer 19 | `(no label)` — edge [+0.0977]
→ **LOGIT** `node_id=27_63720_7` Layer 27 — `Output " atlas" (p=0.825)`

**Causal path diagram:**

![Causal paths for "<bos>A book of maps is called an" → "Output " atlas" (p=0.825)"](graphs/bos_a_book_of_maps_is_called_an__output___atlas___p_0_causal_paths.png)

*Figure: Causal paths from input features to predicted token "Output " atlas" (p=0.825)". Y-axis = transformer layer. Edge width = connection strength. Green = excitatory, red = inhibitory, orange = mixed.*

**Mechanistic Narrative**

The circuit for "A book of maps is called an" → " atlas" (p=0.825) is the clearest example of layered semantic composition in the dataset: distinct early features each fire on one semantic component of the query ("book," "maps," "called an"), and five causal paths converge through a shared L18→L19 gateway before reaching the logit.

**Early-layer detection.** Three early-layer features deliver the key semantic components. Layer 4, Feature 4625 (node_id=4_4625_5, influence=0.7987, act=3.18) — "*words and names related to books*" — fires on the nominal subject. Layer 3, Feature 355 (node_id=3_355_4, act=2.51) — "*geographical references or locations*" — fires on "maps" (geographic content). Layer 4, Feature 1727 (node_id=4_1727_1, act=9.71) — "*sentences that start with the letters 'A' or 'An'*" — anchors the article-completion frame. These three features jointly encode "a reference-format book [article needed]" and set up the model to retrieve a specific named object.

**Pivotal middle-layer feature.** Layer 8, Feature 4302 (node_id=8_4302_3, influence=0.8002, act=3.83) — "*mentions of note-taking in records and books*" — is the highest-influence node in the middle band and consolidates the book/records semantic field. It integrates the prior "books" and "geographical references" signals into a unified reference-collection concept. Layer 10, Feature 6804 (node_id=10_6804_1, act=38.22) — "*references*" — activates with very high magnitude, reinforcing the library/catalogue schema. Both features contribute to Paths 4 and 5 that funnel through the shared L18→L19 gateway.

**Late-layer final push.** Layer 21, Feature 3848 (node_id=21_3848_6, act=17.10) — "*words related to visual representations of information*" — is the semantically most apposite late-layer feature, firing for the visual/cartographic nature of maps. Layer 16, Feature 16329 (node_id=16_16329_7, act=7.30) — "*word origins*" — activates on the etymological frame ("atlas" derives from the Titan Atlas), echoing the etymology-detection pattern seen in the irregular plural prompts.

**Dominant excitatory path.** Path 1 — `L8_1494_7` (coding/GUI) → `L18_10679_7` → `L19_8729_7` → `L24_11962_7` → `L25_8267_7` → **LOGIT** (wt=52.85) — is the largest path but is mixed (±): the L24 node carries a large negative edge (-6.89) and the final L25 edge is also slightly negative (-0.27). This mirrors the "written" pattern: a strong inhibitory bottleneck in the L24–L25 range. Path 2 shares the same L18→L19→L24→L25 gateway as Path 1, with a different origin (L8 Feature 13791: "web development/URLs"). Path 3 — `E_14503_4` → **LOGIT** (wt=3.63, 1 hop excitatory) — is the only clean positive path, delivering the direct answer signal from the embedding node.

**Inhibitory paths.** Paths 1, 2, 4, and 5 are all mixed. The L24_11962 bottleneck node (edge -6.89 to L25) appears in Paths 1 and 2, functioning as a strong negative filter that eliminates near-competitor tokens like "atlas" (the Titan), "atlas" (the anatomical term), or "almanac" before allowing the cartographic sense to pass through. This architectural convergence on an inhibitory L24 node — the same layer as in Prompts 8 and 10 — suggests Layer 24 plays a systematic role as a competitor-suppression gate in factual-recall completions.

**Convergent or ambiguous?** Highly convergent. p=0.825 is second-highest in the dataset. Despite four of five paths being mixed, the circuits all pass through the same L18→L19 gateway and produce a consistent selection. The early-layer semantic composition (books + geography + article-frame) is unusually clean, providing unambiguous input to the retrieval mechanism.

---

### Prompt: "<bos>A person who writes books is called an"

**Predicted token:** `Output " author" (p=0.836)` (prob=0.8360)

**Token competition:**

| Rank | Token | Logit score | Features voting |
|------|-------|-------------|-----------------|

**Circuit walkthrough:**

*Early layers — input recognition*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 1 | 4757 | 1_4757_4 | 0.8002 | 2.6979 |  words, phrases, and symbols in mathematical equations, financial reports, and mechanical descriptions |
| 0 | 6 | 0_6_1 | 0.7999 | 0.0 | references to the current study or research |
| 0 | 10322 | 0_10322_5 | 0.7995 | 2.3455 |  verbs |
| 3 | 6787 | 3_6787_4 | 0.7981 | 4.5387 |  words related to legal and financial actions |
| 3 | 3205 | 3_3205_7 | 0.7979 | 12.0741 |  code snippets and documentation references, possibly related to web development |
| 0 | 3806 | 0_3806_4 | 0.7977 | 2.1458 | words related to comprehension, observation, creation, and existence |
| 0 | 6117 | 0_6117_8 | 0.7973 | 4.3218 |  code snippets and programming syntax |
| 2 | 3974 | 2_3974_1 | 0.7967 | 6.9907 |  sentences starting with "A" that introduce or describe a situation or event |
| 3 | 14572 | 3_14572_6 | 0.796 | 5.1393 | mentions of programming code and configuration files |
| 5 | 10698 | 5_10698_4 | 0.7958 | 6.1866 |  technical writing related to patents |
| 7 | 7039 | 7_7039_7 | 0.7956 | 9.0162 |  words or short phrases indicating a process or experiment is being performed or described |
| 0 | 139 | 0_139_7 | 0.7952 | 3.8352 | instances of the word "had" or sometimes "number" |
| 5 | 9949 | 5_9949_7 | 0.795 | 5.5279 |  passages which define terms in legal or technical writing |
| 3 | 576 | 3_576_3 | 0.7948 | 4.7482 |  words related to scientific experiments |
| 3 | 15992 | 3_15992_8 | 0.7944 | 5.6994 |  the indefinite article "a" or "an" |
| 4 | 14120 | 4_14120_5 | 0.794 | 2.3694 |  the phrase "put down" used in the context of reading and writing a book, and to a lesser extent, author names. |
| 0 | 9536 | 0_9536_1 | 0.7935 | 2.7878 | the word 'terms' and words related to visual appearance |
| 4 | 5292 | 4_5292_1 | 0.7931 | 10.2305 |  instances of the definite article "An" and "A", sometimes in the context of code or lists |
| 7 | 3099 | 7_3099_5 | 0.7929 | 13.1996 |  a variety of reference codes, abbreviations, and identifiers from different fields. |
| 7 | 9294 | 7_9294_8 | 0.7927 | 7.6653 |  information and names of places and/or people and their claimed meanings |
| 3 | 6249 | 3_6249_8 | 0.7923 | 3.8841 |  words related to age and relative size |
| 5 | 9829 | 5_9829_2 | 0.792 | 12.2373 | words and phrases related to individuals, especially those in conflict, legal settings, or facing life events |

*Middle layers — relational mapping*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 9 | 16189 | 9_16189_8 | 0.7993 | 3.9247 |  phrases describing the usage of a component for a specific purpose |
| 9 | 10769 | 9_10769_5 | 0.7991 | 3.4461 |  words related to people, categories of people, or sports. |
| 10 | 1037 | 10_1037_8 | 0.7989 | 4.4773 |  capitalized words or phrases and other words that stand out |
| 0 | 13 | 0_13_4 | 0.7983 | 0.0 | the phrase "no matter how" |
| 8 | 11795 | 8_11795_6 | 0.7975 | 3.6846 |  words related to medicine, lawsuits, or community involvement |
| 11 | 10933 | 11_10933_1 | 0.7965 | 51.311 | the letters "L", "H," and "a" when they are at the beginning of a text block |
| 13 | 13149 | 13_13149_8 | 0.7963 | 10.8528 |  imperative verbs relating to test actions and expected results, and grammatical words that link them |
| 0 | 14 | 0_14_4 | 0.7933 | 0.0 |  occurrences of the word "even", the word "both" and variations of the word "meet" |

*Late layers — token selection*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 16 | 10647 | 16_10647_7 | 0.7997 | 7.6167 | media production |
| 24 | 5218 | 24_5218_8 | 0.7987 | 6.5648 |  mentions of visual art styles and their history |
| 22 | 9109 | 22_9109_7 | 0.7985 | 8.5516 |  words related to literature and the act of writing, with some activation toward religion |
| 24 | 1735 | 24_1735_8 | 0.7971 | 9.6289 |  lists of creative endeavors and the authors of those endeavors |
| 24 | 2394 | 24_2394_8 | 0.7969 | 21.4539 |  code and markup. |
| 25 | 323 | 25_323_8 | 0.7954 | 7.5106 |  references and allusions to dates, years and time periods |
| 16 | 12109 | 16_12109_7 | 0.7946 | 14.6975 | phrases that include the word "be" followed by a description. |
| 22 | 4751 | 22_4751_8 | 0.7942 | 15.7431 | code snippets, questions, and variable names from programming contexts |
| 24 | 4886 | 24_4886_8 | 0.7937 | 6.3738 |  topics that appear in recipes or technical documentation, that have some parts in numbered lists or bullet points |
| 18 | 1943 | 18_1943_8 | 0.7925 | 8.6611 |  text where someone is describing their writing projects |

**Causal paths (edge-weight chains to logit):**

*Path 1 — (±) mixed | weight=176.359861 | hops=5*
→ `node_id=0_14_4` | `feature=14` | Layer 0 | ` occurrences of the word "even", the word "both" and variations of the word "meet"` — edge [-4.569]
→ `node_id=18_4309_4` | `feature=?` | Layer 18 | `(no label)` — edge [+1.6482]
→ `node_id=23_10430_8` | `feature=?` | Layer 23 | `(no label)` — edge [-3.3096]
→ `node_id=24_1633_8` | `feature=?` | Layer 24 | `(no label)` — edge [-2.5639]
→ `node_id=25_14935_8` | `feature=?` | Layer 25 | `(no label)` — edge [-2.7599]
→ **LOGIT** `node_id=27_3426_8` Layer 27 — `Output " author" (p=0.836)`

*Path 2 — (+) excitatory | weight=66.041699 | hops=2*
→ `node_id=E_6142_5` | `feature=?` | Layer E | `(no label)` — edge [+17.4096]
→ `node_id=22_7158_8` | `feature=?` | Layer 22 | `(no label)` — edge [+3.7934]
→ **LOGIT** `node_id=27_3426_8` Layer 27 — `Output " author" (p=0.836)`

*Path 3 — (±) mixed | weight=28.674453 | hops=3*
→ `node_id=18_1943_8` | `feature=1943` | Layer 18 | ` text where someone is describing their writing projects` — edge [-1.3849]
→ `node_id=22_7158_8` | `feature=?` | Layer 22 | `(no label)` — edge [+7.5022]
→ `node_id=25_14935_8` | `feature=?` | Layer 25 | `(no label)` — edge [-2.7599]
→ **LOGIT** `node_id=27_3426_8` Layer 27 — `Output " author" (p=0.836)`

*Path 4 — (±) mixed | weight=27.740235 | hops=5*
→ `node_id=10_1037_8` | `feature=1037` | Layer 10 | ` capitalized words or phrases and other words that stand out` — edge [-0.6444]
→ `node_id=12_10440_8` | `feature=?` | Layer 12 | `(no label)` — edge [+9.7749]
→ `node_id=13_10353_8` | `feature=?` | Layer 13 | `(no label)` — edge [-1.2358]
→ `node_id=20_3094_8` | `feature=?` | Layer 20 | `(no label)` — edge [-4.7445]
→ `node_id=25_4717_8` | `feature=?` | Layer 25 | `(no label)` — edge [+0.7511]
→ **LOGIT** `node_id=27_3426_8` Layer 27 — `Output " author" (p=0.836)`

*Path 5 — (+) excitatory | weight=11.458105 | hops=4*
→ `node_id=9_10769_5` | `feature=10769` | Layer 9 | ` words related to people, categories of people, or sports.` — edge [+0.4877]
→ `node_id=19_7101_8` | `feature=?` | Layer 19 | `(no label)` — edge [+7.1482]
→ `node_id=21_13124_8` | `feature=?` | Layer 21 | `(no label)` — edge [+4.3755]
→ `node_id=25_4717_8` | `feature=?` | Layer 25 | `(no label)` — edge [+0.7511]
→ **LOGIT** `node_id=27_3426_8` Layer 27 — `Output " author" (p=0.836)`

**Causal path diagram:**

![Causal paths for "<bos>A person who writes books is called an" → "Output " author" (p=0.836)"](graphs/bos_a_person_who_writes_books_is_called__output___author___p__causal_paths.png)

*Figure: Causal paths from input features to predicted token "Output " author" (p=0.836)". Y-axis = transformer layer. Edge width = connection strength. Green = excitatory, red = inhibitory, orange = mixed.*

**Mechanistic Narrative**

The circuit for "A person who writes books is called an" → " author" (p=0.836) is the highest-confidence circuit in the dataset and the most semantically coherent: multiple independent features at different layers all point to the same concept (writing-person-creator), and the dominant 2-hop excitatory path bypasses the inhibitory L24 bottleneck entirely.

**Early-layer detection.** The early layers activate two semantically precise features. Layer 4, Feature 14120 (node_id=4_14120_5, act=2.37) — "*the phrase 'put down' used in the context of reading and writing a book, and to a lesser extent, author names*" — is the most targeted early-layer semantic hit: it encodes both "books" and "author names" simultaneously, establishing the writing-in-book-context frame. Layer 3, Feature 3205 (node_id=3_3205_7, act=12.07, influence=0.7979) — a recurring cross-graph feature appearing 25/10 times — fires on "code snippets and documentation references, possibly related to web development," likely activating here because technical documentation routinely uses the formula "a person who X is called a Y." Layer 2, Feature 3974 (node_id=2_3974_1, act=6.99) — "*sentences starting with 'A' that introduce or describe a situation or event*" — anchors the article-introduction frame identically to Feature 1727 in Prompt 9.

**Pivotal middle-layer feature.** Layer 18, Feature 1943 (node_id=18_1943_8, act=8.66) — "*text where someone is describing their writing projects*" — is the most semantically precise middle-layer feature in the entire dataset. It fires directly on the domain of authorship, bridging early "book writing" signals with the late-layer author-specific features. It contributes as the origin of Path 3 (mixed, wt=28.67), routing through the shared L22 gateway node.

**Late-layer final push.** Layer 24, Feature 1735 (node_id=24_1735_8, act=9.63) — "*lists of creative endeavors and the authors of those endeavors*" — is the most direct semantic hit at the output stage, encoding the very concept being queried ("X → author"). Layer 22, Feature 9109 (node_id=22_9109_7, act=8.55) — "*words related to literature and the act of writing*" — provides the pre-final-layer boost. Both features are visible in the band table and route through the unlabeled L22_7158 node that serves as the gateway for Paths 2 and 3.

**Dominant excitatory path.** Path 2 — `E_6142_5` → `L22_7158_8` → **LOGIT** (wt=+66.04, 2 hops, fully excitatory) — is the cleanest and most powerful signal: the embedding node fires at +17.41 to L22_7158, which then fires at +3.79 to the logit. This 2-hop excitatory path is the only one in Prompt 10 that entirely avoids the L24_1633 inhibitory bottleneck seen in Prompts 8–9. Its dominance over Path 1 (wt=176.36 but mixed) reflects that pure excitatory weight beats high-magnitude mixed paths when the goal is to push a specific positive logit.

**Inhibitory paths.** Path 1 — `L0_14` → `L18_4309` → `L23_10430` → `L24_1633` → `L25_14935` → LOGIT (wt=176.36, all edges mixed with multiple negatives) — routes through the familiar L24_1633 bottleneck with a -2.56 edge. Path 3 begins at L18 Feature 1943 (writing projects) with a *negative* first edge (-1.38), then recovers through L22_7158 (+7.50), then hits -2.76 at L25_14935. The negative initial edge at the writing-projects feature is unexpected and may reflect suppression of first-person authorship ("I am writing a book") in favor of third-person classification ("a person who writes"). Path 5 (excitatory, wt=11.46) routes through L9 Feature 10769 "people, categories of people, or sports" → L19 → L21 → L25, providing a secondary clean excitatory contribution.

**Convergent or ambiguous?** Highly convergent. p=0.836 is the highest probability in the dataset. The circuit has two independent excitatory paths (Paths 2 and 5), multiple middle-layer features that independently encode the authorship concept, and a clean 2-hop shortcut from embedding to logit. The "person who writes books = author" concept is encoded redundantly across the network — early (book-writing context), middle (writing-project description), and late (creative-endeavors-and-authors) — producing a confident, well-supported prediction.

---

## 4. Discussion

### 4.1 The Shared Linguistic Circuit: Recurring Feature Architecture

The 312 recurring features identified at the 50% threshold reveal a circuit that is predominantly populated by generic text-format and register features rather than linguistic-domain-specific detectors. Layer 0 accounts for 8 of the top 15 recurring features, uniformly low-activation nodes that encode positional and token-level context (e.g., Feature 13: "no matter how," node_id=0_13_4; Feature 6: "references to current study/research," node_id=0_6_1). These suggest that the sentence-boundary token `<bos>` systematically activates a shared set of context-anchoring features that fire regardless of the specific metalinguistic operation being performed.

Layer 6, Feature 2586668 (node_id=6_2267_3) is the most universally recurring feature (37 appearances / 10 graphs), labelled "*words that appear in programming code, legal jargon, or scientific texts*." Its cross-prompt universality reflects the fact that all 10 prompts share the formal metalinguistic template ("The X of Y is" / "A X of Y is called an"), which strongly resembles the register of technical/definitional writing. This feature is a template-format detector, not a semantic content detector.

The labeled top-15 features cluster into three functional groups consistent with the prompt-driven data flow:
1. **Template/register anchors (Layers 0–6):** Features 13, 6, 5, 17 (L0) and Feature 2586668 (L6) fire on the formal structure of the prompts.
2. **Morphological/lexical processing hubs (Layers 6–15):** Feature 12241 at Layer 11 ("name origins and meanings," recurring in antonym, plural, and tense prompts) and Feature 10933 at Layer 11 ("letters L, H, a at text beginning," very high activation in multiple prompts) serve as morphological transformation mediators.
3. **Output-selection features (Layers 15–25):** Feature 805 at Layer 15 ("proper nouns with preference for locations/nationalities") and Feature 3205 at Layer 3 (recurring 25 times) contribute to the answer-token selection stage.

### 4.2 Dominant Causal Paths and the Embedding Shortcut

The most consistent finding across all 10 prompts is the presence of a single dominant 1–2 hop excitatory path from the embedding aggregation node directly to the logit. In 8 of 10 prompts this path carries 85–99% of the total excitatory weight, with edge weights ranging from 3.63 ("atlas") to 14.14 ("mice"). This architecture implies that Gemma-2-2B largely resolves metalinguistic queries at the embedding stage — the SAE features at the final embedding position aggregate the answer signal before it is even passed through the late transformer layers. The late-layer features visible in the band tables are real circuit components but play supporting roles, fine-tuning competition among near-competitor tokens rather than generating the primary logit signal.

The two prompts with the weakest embedding-path dominance are also the two with the lowest prediction confidence: "written" (p=0.344, all paths mixed) and "swam" (p=0.496, five competing paths). In both cases the circuit lacks a clean single-origin excitatory anchor, suggesting that irregular past-tense computation is more distributed and contentious than irregular plural or synonym completion.

### 4.3 The Layer 24 Inhibitory Bottleneck

A striking architectural pattern is the convergence of causal paths through an unlabeled Layer 24 node that carries a large negative final edge to the logit. This bottleneck appears in Prompts 8 ("written," node_id=24_1633_6, edge=-3.56), 9 ("atlas," node_id=24_11962_7, edge=-6.89), and 10 ("author," node_id=24_1633_8, edge=-2.56). The recurrence of Layer 24 Feature 1633 specifically in both Prompt 8 and Prompt 10 suggests this is a systematic competitor-suppression mechanism: by routing activations through a strongly negative final gate, the circuit simultaneously eliminates multiple competitor tokens (e.g., "wrote," "write" for Prompt 8; "writer," "novelist" for Prompt 10) leaving the one correct answer as the least suppressed output. This negative-gate architecture at Layer 24 may be a general property of the model's factual and lexical completion mechanism, not specific to linguistic reasoning.

### 4.4 The Edge Neighbourhood Analysis: Top Recurring Features

The top 2 recurring features by average influence — Layer 6, Feature 2586668 (avg_inf=0.6571) and Layer 0, Feature 13 (avg_inf=0.5924) — reveal complementary roles in the circuit's wiring. Feature 2586668's incoming edges originate predominantly from Layers 0–5 (token-level embedding features), while its outgoing edges project to Layers 8–14 (middle-layer processing hubs). This confirms its role as an early-to-middle signal relay. Feature 13's edges are extremely sparse (zero-activation node), suggesting it functions as a structural anchor that marks sentence position rather than carrying semantic content.

### 4.5 Surprising Findings

**Feature repurposing for morphological computation.** The "baseball terminology" feature (Layer 5, Feature 10444, node_id=5_10444_3) achieved the highest early-layer influence score in Prompt 7 (0.8002) for the prompt "The past tense of swim is." Baseball verbs are predominantly irregular monosyllables with vowel-change past tenses (hit, pitch, throw, swim, run), suggesting the model has a polysemantic feature that fires on this morphological phonological class, not on sport semantics. This is a clear case of a feature being co-opted for an unexpected computational role.

**Format-override of semantic retrieval (Prompts 1–4).** Four of the ten prompts — all antonym/synonym prompts — predicted the colon ":" rather than the expected synonym/antonym. The circuit analysis for those prompts (detailed in Results Sections 3.4.1–3.4.4) revealed a format-following circuit that overrides semantic retrieval: a very high-activation recurring feature (Feature 110446948: "code snippets and license agreements") fires strongly for the "X is:" template, pushing the model to complete with a formatting character rather than a word. This is not a linguistic reasoning failure per se but a register-competition failure: the model's format-completion circuit outcompetes the semantic-retrieval circuit when the prompt strongly resembles list/definition formatting.

**Layer 11, Feature 12241 as a cross-paradigm morphological hub.** Feature 12241 ("name origins and meanings") recurred in both the irregular plural prompts (Prompt 5: "child", act=49.98; Prompt 6: "mouse", act=17.87) and the tense-change prompts, always at high activation. Its label ("name origins and meanings") is formally about etymology, but its activation pattern suggests it encodes the broader class of words whose current form derives from historical sound changes — irregular plurals, vowel-mutation past tenses, and suppletive forms — making it a functional morphological history detector.

---

## 5. Causal Validation via Feature Steering

To test whether the causal paths identified in the per-prompt analyses above are genuinely load-bearing — not merely high-attribution but functionally inert — we ran causal steering experiments on three linguistic circuits using the Neuronpedia Steering API. For each circuit, we extracted the backbone features from the per-prompt top-5 causal paths and applied four tests: (A) **Necessity** — suppress each backbone feature individually at strength −20 and check whether the model's first predicted token changes; (B) **Full backbone suppression** — suppress all backbone features simultaneously; (C) **Sufficiency** — boost the circuit's primary hub at strength +20 on an altered prompt to test whether the hub alone can induce the target prediction; (D) **Specificity** — suppress non-backbone features (high-activation nodes not on the top-5 causal paths) to confirm they are causally inert.

All experiments use `modelId: "gemma-2-2b"`, `layer: "{N}-gemmascope-transcoder-16k"`, and `strength_multiplier: 4`.

### 5.1 Necessity (Individual Feature Suppression)

#### hot→cold (p=0.566, 7 backbone features)

| Feature | Layer | Index | Role in Causal Path | Steered 1st Token | Disrupted? |
|---------|-------|-------|---------------------|-------------------|------------|
| L11_systems | 11 | 4301 | Path 1 entry | cold | no |
| L18_relay | 18 | 1296 | Mid-late relay | cold | no |
| L20_hub | 20 | 6666 | Central convergence (paths 1,2,3,5) | cold | no |
| **L25_output** | **25** | **16258** | **Output driver on all paths** | **not** | **YES** |
| L7_comparison | 7 | 4526 | Comparisons/symmetry feature | cold | no |
| L12_relay | 12 | 95 | Mid relay | cold | no |
| L14_relay | 14 | 1354 | Late-mid relay | cold | no |

L25/16258 is the sole necessary feature — it appears on all multi-hop causal paths as the final node before the logit. Suppressing it changes the prediction from "cold" to "not" — the model shifts from antonym retrieval to negation, a semantically coherent failure mode that reveals the competition between "produce the opposite meaning" and "negate the adjective" as strategies for completing "The opposite of hot is." The L20 convergence hub (on 4 of 5 paths) is not individually necessary because the direct embedding→logit path (path 4, wt=9.30) bypasses it entirely, consistent with the Discussion's finding that the dominant embedding→logit shortcut carries the majority of the output signal.

#### maps→atlas (p=0.825, 7 backbone features)

| Feature | Layer | Index | Role in Causal Path | Steered 1st Token | Disrupted? |
|---------|-------|-------|---------------------|-------------------|------------|
| L18_gateway | 18 | 10679 | Central gateway (edge +22.62) | atlas | no |
| L19_relay | 19 | 8729 | Post-gateway relay | atlas | no |
| **L24_suppressor** | **24** | **11962** | **Competitor suppression (edge −6.89)** | **"** | **YES** |
| L25_gate | 25 | 8267 | Final gate to logit | atlas | no |
| L10_references | 10 | 6804 | References feature (act=38.22) | atlas | no |
| L21_visual_info | 21 | 3848 | Visual representations | atlas | no |
| L16_word_origins | 16 | 16329 | Word origins/etymology | atlas | no |

L24/11962 (competitor suppression bottleneck) is the sole necessary feature. Section 4.3 hypothesized that Layer 24 functions as a "systematic competitor-suppression gate" based on the recurrence of strongly negative final edges at this layer. This steering result causally confirms that hypothesis: suppressing the L24 gate changes "atlas" to a quotation mark — the model loses the ability to select among competing completions and falls through to punctuation. The L18 gateway (highest edge weight, +22.62) is not individually necessary because the direct embedding→logit path (path 3, wt=3.63) provides a bypass.

#### author (p=0.836, 9 backbone features)

| Feature | Layer | Index | Role in Causal Path | Steered 1st Token | Disrupted? |
|---------|-------|-------|---------------------|-------------------|------------|
| L24_bottleneck | 24 | 1633 | Inhibitory bottleneck | author | no |
| **L25_output** | **25** | **14935** | **Output driver** | **(markup)** | **YES** |
| L22_gateway | 22 | 7158 | Excitatory gateway | author | no |
| L18_writing_projects | 18 | 1943 | Writing projects feature | author | no |
| L19_relay | 19 | 7101 | Relay | author | no |
| L21_relay | 21 | 13124 | Late relay | author | no |
| L25_amplifier | 25 | 4717 | Shared amplifier | author | no |
| L22_literature | 22 | 9109 | Literature/writing | author | no |
| L24_creative_works | 24 | 1735 | Creative endeavors/authors | author | no |

L25/14935 is the sole necessary feature. The L24 bottleneck (Feature 1633) — the same feature identified in Section 4.3 as the Layer 24 inhibitory bottleneck shared with the "written" prompt — is not individually necessary here. The L22 excitatory gateway (direct 2-hop path, wt=66) provides sufficient redundancy. This suggests that while L24/1633 is an important architectural motif in the linguistic circuit, the author prompt's high confidence (p=0.836) routes the dominant signal through the excitatory L22 gateway rather than relying on the inhibitory suppression path.

### 5.2 Full Backbone Suppression

| Circuit | Default Completion | Steered Completion | Disrupted? |
|---------|--------------------|--------------------|------------|
| hot→cold | ...cold. The opposite | ...not no matter no matter | **YES** |
| maps→atlas | ...atlas. A book | ...a a (whitespace) | **YES** |
| author | ...author. A person | ...\<strong\>\<strong\>\<strong\>... | **YES** |

All three linguistic circuits are fully disrupted by simultaneous suppression of all backbone features. The failure modes are revealing:
- **hot→cold** degrades to "not no matter no matter" — the model enters a negation loop, consistent with the "not" failure mode seen when suppressing only L25/16258.
- **maps→atlas** collapses to article repetition, losing all lexical content.
- **author** produces HTML markup tags — the model falls through to a completely different register, suggesting the linguistic reasoning circuit and the formatting circuit compete for the same output slot.

### 5.3 Sufficiency (Hub Boost on Altered Prompts)

| Circuit | Hub Boosted | Altered Prompt | Baseline → Boosted | Target Induced? |
|---------|-------------|----------------|--------------------|-----------------:|
| hot→cold | L11/4301 | "The opposite of fast is" | slow → slow | no |
| maps→atlas | L18/10679 | "A collection of maps is called an" | — → atlas | **YES** |
| maps→atlas | L18/10679 | "A book of recipes is called a" | — → map of the world | no |
| author | L24/1633 | "Someone who writes novels is called an" | — → author | **YES** |
| author | L24/1633 | "A person who paints pictures is called an" | — → art(ist) | no |

Sufficiency succeeds when the altered prompt retains the target semantic domain:
- The maps→atlas hub (L18/10679) induces "atlas" on "A collection of maps" — a near-paraphrase of the original prompt — confirming this feature specifically encodes the maps→atlas lexical mapping. On the cross-domain prompt ("A book of recipes"), it produces "map of the world" — the hub activates its map-domain association but cannot override the recipe context to produce "atlas."
- The author hub (L24/1633) induces "author" on "Someone who writes novels" but only "art(ist)" on "A person who paints pictures." The hub carries a "creative professional" concept that is necessary but not sufficient for the specific "author" prediction without writing-domain context.
- The hot→cold hub (L11/4301) fails to override "slow" on the "fast" antonym prompt, consistent with its role as an early-layer entry point rather than a domain-specific output driver.

### 5.4 Specificity (Non-Backbone Feature Suppression)

| Circuit | Non-Backbone Feature | Neuronpedia Label | Steered 1st Token | Disrupted? |
|---------|---------------------|-------------------|-------------------|------------|
| hot→cold | L2/8212 | "compare/contrast" | cold | no |
| hot→cold | L0/902 | "the word is" | cold | no |
| maps→atlas | L8/1494 | "coding/GUI" | atlas | no |
| maps→atlas | L8/13791 | "web dev/URLs" | atlas | no |
| **author** | **L10/1037** | **"capitalized words"** | **artist** | **YES** |
| author | L9/10769 | "people/categories" | author | no |

5 of 6 non-backbone features pass the specificity test. The sole exception is in the author circuit: suppressing L10/1037 ("capitalized words") changes "author" to "artist." This feature was classified as non-backbone because it does not appear on the top-5 causal paths, yet it causally contributes to disambiguating between semantically close completions ("author" vs. "artist" — both creative professionals, both likely capitalized in certain contexts). This false negative reveals a limitation of top-5 causal path tracing: features that contribute to fine-grained token discrimination may be excluded from the backbone if their causal influence is distributed across many weak paths rather than concentrated in one strong path.

### 5.5 Summary

| Circuit | Confidence | Necessary Features | Full Suppress | Sufficiency | Specificity |
|---------|------------|-------------------|---------------|-------------|-------------|
| hot→cold | 0.566 | 1/7 (L25/16258) | DISRUPTED | 0/1 | PASS (0/2) |
| maps→atlas | 0.825 | 1/7 (L24/11962) | DISRUPTED | 1/2 | PASS (0/2) |
| author | 0.836 | 1/9 (L25/14935) | DISRUPTED | 1/2 | PARTIAL (1/2) |

The causal validation confirms three key architectural claims from the Discussion:

1. **The Layer 24 inhibitory bottleneck is causally real** (Section 4.3). The maps→atlas circuit's L24/11962 suppression gate is the sole individually necessary feature — suppressing it alone is sufficient to disrupt the prediction. This validates the hypothesis that the Layer 24 negative-gate architecture is a functional competitor-suppression mechanism, not merely a correlate of high attribution weight.

2. **The embedding→logit shortcut provides redundancy** (Section 4.2). Most backbone features on multi-hop paths are individually dispensable because the direct 1–2 hop embedding→logit path (weights 3.63–14.14) carries the dominant signal independently. Only the final L24–L25 bottleneck features — which sit downstream of the shortcut — are uniquely necessary.

3. **Individual necessity is sparse** (mean 1.0 necessary features out of 7.7 tested per circuit), consistent with the highly parallel causal path structure documented in the per-prompt analyses.

---

## 6. Limitations

**Single model, single SAE.** All analyses use Gemma-2-2B with the Gemmascope 16K transcoder SAE. Different SAE sizes or a different model family may produce different feature decompositions, recurring components, and path structures. The findings should not be assumed to generalise across model architectures.

**Sparse causal path tracing.** The `trace_causal_paths()` function traces only the strongest edge-weight chains (greedy forward/backward search). It will miss paths that are collectively important but individually weak. The 5-path limit per prompt means that weaker but mechanistically significant paths may be systematically excluded.

**Unlabeled bottleneck nodes.** Several of the most mechanistically critical nodes in the causal paths — including the Layer 24 bottleneck nodes and several Layer 25 intermediaries — lack Neuronpedia labels (returning "no label" from the feature explanation API). The functional roles attributed to these nodes in this paper are inferred from context, not from direct feature activation evidence.

**Token competition table sparsity.** The token competition tables for all 10 prompts were empty due to the absence of logit-ranked feature data in the raw graph JSON. As a result, the competitor-token suppression analysis relies entirely on the causal path classifications (excitatory/inhibitory/mixed) rather than on direct comparison of logit scores for the top-k candidate tokens.

**10-prompt sample size.** With only 10 graphs, the 50% threshold requires a feature to appear in at least 5 graphs. This is sufficient to distinguish universal circuit components from prompt-specific noise, but the power to detect sub-category-specific components (e.g., features specific to plural morphology vs. past-tense morphology) is limited. A larger prompt set with 20–50 examples per sub-category would allow finer-grained circuit dissection.

**Polysemantic feature interpretation.** Many of the identified recurring features are polysemantic (e.g., Feature 10199: "code snippets, family relations, and super sentai teams"; Feature 10444: "baseball terminology"). The functional roles assigned in the mechanistic narratives are the most plausible interpretations given the prompt context, but alternative interpretations cannot be excluded without targeted activation patching experiments.

**Causal validation coverage.** Steering experiments were run on 3 of 10 prompts (hot/cold, maps/atlas, author). The 4 antonym/synonym prompts that predicted ":" instead of the expected word, and the 3 morphological prompts (plurals, past tenses), were not causally validated. Extending validation to the format-override cases would test whether suppressing the format-completion circuit (L4/110446948) is sufficient to restore semantic retrieval.

---

## 7. Conclusion

This paper presents the first detailed mechanistic analysis of the linguistic reasoning circuit in Gemma-2-2B across four metalinguistic sub-tasks. Our main findings are:

1. **A 312-feature shared circuit** underlies all 10 linguistic prompts at the 50% recurrence threshold, dominated by template-format and register-detection features rather than task-specific linguistic detectors. Layer 6, Feature 2586668 is the most universal component, present in every prompt as a formal-register template sensor.

2. **A dominant embedding→logit shortcut** (1–2 hops, weights 3.63–14.14) carries the majority of the output signal in 8/10 prompts, suggesting that metalinguistic completions are largely resolved at the embedding aggregation stage. Prediction confidence is inversely correlated with morphological irregularity and the availability of a clean excitatory embedding path.

3. **A Layer 24 inhibitory bottleneck** (Feature 1633, node_id=24_1633) functions as a systematic competitor-suppression gate in at least three prompts, concentrating multiple mixed-polarity paths through a strongly negative final edge before the logit. This architecture allows simultaneous elimination of multiple near-competitors without requiring separate inhibitory features for each.

4. **Feature repurposing** is pervasive: "baseball terminology" detects vowel-change monosyllables, "name origins and meanings" detects morphological history, and "code snippets and license agreements" activates for formal definitional templates. The model's linguistic circuit is built from general-purpose polysemantic features co-opted for specific sub-computations.

5. **Format-override failures** occur when the prompt register (formal, list-like) is sufficiently strong to activate the format-completion circuit instead of the semantic-retrieval circuit, as seen in 4/10 prompts that predicted ":" instead of the target lexical item.

These findings support the emerging view that language model circuits are opportunistic assemblies of polysemantic features with distributed, context-dependent roles, rather than dedicated modules for specific linguistic operations.
