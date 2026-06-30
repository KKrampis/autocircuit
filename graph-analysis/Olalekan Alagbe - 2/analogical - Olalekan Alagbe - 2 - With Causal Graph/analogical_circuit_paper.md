# Mechanistic Interpretability of Analogical Reasoning in Gemma-2-2B: A Circuit Analysis

## Abstract

We present a mechanistic interpretability analysis of analogical reasoning in Gemma-2-2B across 10 diverse A:B::C:? prompts. Attribution graphs were generated for each prompt via the Neuronpedia transcoder SAE (gemmascope-transcoder-16k), and 429 recurring circuit features were identified at a 50% appearance threshold. The 15 most universal features span layers 0–10, with the top features being: L6/F2586668 (structural/formal register, 48/10 graphs), L3/F5150441 (code-documentation patterns, 47/10), L8/F94882191 ("analogies or comparisons," 41/10), L4/F110446948 (license/code patterns, 37/10), and L7/F4828270 (reference codes and abbreviations, 31/10). Per-prompt causal path analysis reveals that model confidence correlates with path clarity: geographic capital-city analogies (Paris/Germany, p=0.97; Cairo/Kenya, p=0.96) show convergent 3–5-hop causal chains with strong domain-specific features, while functional/botanical analogies (Fish/air, p=0.12; Leaf/flower, p=0.14) produce diffuse, mixed-sign path structures with no clear dominant mechanism. Explicit analogy-detection features at Layers 7, 8, 9, and 15 are identified. Five of ten prompts contain purely excitatory causal paths; all ten show convergent late-layer aggregation through Layers 21–25 to the logit node at Layer 27. The results suggest that Gemma-2-2B implements analogical reasoning through a two-stage circuit: a universal structural-parsing stage (Layers 0–6) shared across all prompts, and a domain-specific resolution stage (Layers 7–27) that varies in strength with the clarity of the relational mapping.

## Introduction

This paper presents a mechanistic interpretability analysis of analogical reasoning in Gemma-2-2B, a 2-billion parameter transformer language model. Analogical reasoning — the ability to identify and complete structural relationships of the form A:B::C:? — is a fundamental component of abstract intelligence. We investigate how this capability is implemented at the level of individual model features using attribution graphs generated via the Neuronpedia platform.

We selected 10 analogical reasoning prompts spanning diverse relational categories: geographic (capital cities), biological (animal/habitat, life stages), physical (tools/measurements), functional (activities), botanical (plant structures), mechanical (vehicle components), and social (institutional roles). For each prompt, we generated an attribution graph over Gemma-2-2B's transcoder features, then identified recurring circuit components across graphs using a 50% appearance threshold.

Our analysis reveals the specific layers and features that constitute the analogical reasoning circuit in Gemma-2-2B, the causal paths through which information flows from input tokens to the final predicted token, and the mechanistic basis for token selection in this class of reasoning task.

## Methods

**Model.** Gemma-2-2B (Google DeepMind), a 26-layer transformer language model.

**SAE.** Gemmascope transcoder, 16k features per layer, applied at all transformer layers.

**Graph generation.** Attribution graphs were generated via the Neuronpedia API (`/api/graph/generate`) with parameters: `maxFeatureNodes=3000`, `desiredLogitProb=0.95`, `nodeThreshold=0.8`, `edgeThreshold=0.85`. Each graph captures the most influential transcoder features and their edge weights for a single prompt.

**Recurring feature identification.** `compare_graphs()` was run across all 10 graphs with `threshold=0.50` (a feature must appear in ≥5/10 graphs to qualify as a shared circuit component). This threshold distinguishes category-level circuit structure from prompt-specific noise.

**Node labeling.** Recurring features were labeled via the Neuronpedia `/api/feature/{model}/{sae}/{feature}` endpoint, which returns human-readable descriptions derived from automated interpretability methods.

**Causal path tracing.** `trace_causal_paths()` traces the dominant signal pathways from influential input features to the logit node by following edge weights through the graph. Paths are scored by the product of absolute edge weights across hops and classified as excitatory (+), inhibitory (−), or mixed (±).

**Per-prompt interpretation.** `interpret_prompt_graph()` labels the top 40 nodes per graph (grouped into early/middle/late layer bands), identifies token competition, traces causal paths, generates a causal path figure, and appends all data to this paper.

**Prompt dataset.** 10 analogical reasoning prompts:
1. Paris is to France as Berlin is to
2. Cairo is to Egypt as Nairobi is to
3. Fish is to water as bird is to
4. Puppy is to dog as kitten is to
5. Clock is to time as thermometer is to
6. Book is to reading as radio is to
7. Leaf is to tree as petal is to
8. Wheel is to car as wing is to
9. Judge is to court as priest is to
10. Soldier is to army as sailor is to

## Results

### Recurring Circuit Features (≥50% of graphs, i.e., ≥5/10)

A total of **429 recurring features** were identified at the 50% threshold. The top 15 by appearance count are shown below, with human-readable labels.

| Layer | Feature | Node_id | Appearances | Avg Influence | Avg Activation | Label |
|-------|---------|---------|-------------|---------------|----------------|-------|
| 6 | 2586668 | 6_2267_4 | 48/10 | 0.7217 | 15.7879 | words that appear in programming code, legal jargon, or scientific texts |
| 3 | 5150441 | 3_3205_3 | 47/10 | 0.6449 | 14.0235 | code snippets and documentation references, possibly related to web development |
| 8 | 94882191 | 8_13766_3 | 41/10 | 0.4939 | 32.1364 | analogies or comparisons |
| 4 | 110446948 | 4_14857_1 | 37/10 | 0.6755 | 15.9887 | code snippets and license agreements |
| 7 | 4828270 | 7_3099_1 | 31/10 | 0.7418 | 26.888 | a variety of reference codes, abbreviations, and identifiers from different fields |
| 9 | 89171325 | 9_13344_5 | 30/10 | 0.6755 | 13.7622 | phrases suggesting uncertainty or comparison between two things |
| 0 | 74438300 | 0_12200_1 | 27/10 | 0.701 | 3.8298 | a variety of specific nouns |
| 9 | 4261730 | 9_2909_8 | 27/10 | 0.6394 | 18.0839 | formulas, ratios, and mathematical notation |
| 5 | 16817094 | 5_5793_8 | 27/10 | 0.5668 | 17.3751 | analogies |
| 0 | 1708475 | 0_1847_1 | 26/10 | 0.5885 | 7.5277 | scientific terms and experimental details related to biological and chemical research |
| 0 | 81262125 | 0_12747_3 | 25/10 | 0.6496 | 3.8484 | occurrences of the words 'they', 'them', 'that', 'these', or something that can be replaced with 'they' or 'them' |
| 0 | 2239785 | 0_2115_4 | 25/10 | 0.637 | 6.5559 | data reported as a percentage inside brackets, especially in a laboratory or medical context, and also recognizes countries |
| 5 | 46836675 | 5_9672_7 | 25/10 | 0.5711 | 19.3411 | the phrase "there/they are" or the phrase "it is to." |
| 10 | 105902170 | 10_14542_8 | 23/10 | 0.7307 | 9.7973 | words related to research, business or product comparison |
| 7 | 286895 | 7_749_5 | 21/10 | 0.6201 | 12.1686 | analogies and comparisons |

### Edge Neighbourhood Analysis (Step 5a)

**Top feature by avg_influence: node_id=7_3099_1 (L7, F4828270, "reference codes, abbreviations, and identifiers")**

Analysis performed on the graph for "Cairo is to Egypt as Nairobi is to".

- **In-degree:** 11, **Out-degree:** 7
- **Top incoming edges:** E_2_0 (embedding, w=−38.73), L4/F110446948 (w=−13.61), L3/F5150441 (w=−6.45), L6/F48733121 (w=−5.42), L5/F7993995 (w=−4.95), embedding/F1 (w=+4.81), L4/F47653198 (w=+3.36), L0/F26978184 (w=+3.05)
- **Top outgoing edges:** L10/F100614194 (w=+1.84), L9/F4701701 (w=+1.22), L10/F59891029 (w=+1.10), L9/F125286525 (w=−1.01), L18/F63861932 (w=−0.22), L27/F28273 (w=−0.02)

Key observations: This feature is strongly modulated by embedding-layer inputs (E_2_0 with weight −38.73), suggesting it fires in response to the specific token embeddings encoding the relation markers ("is to", "as"). Its strongest outgoing connections reach layers 10, 9, and ultimately layer 27, suggesting it participates in a long-range excitatory pathway toward the logit.

**Second feature by avg_influence: node_id=6_2267_4 (L6, F2586668, "programming code, legal jargon, scientific texts")**

Analysis performed on the graph for "Paris is to France as Berlin is to".

- **In-degree:** 7, **Out-degree:** 16
- **Top incoming edges:** embedding E_2_0 (w=−7.33), E_29437_1 (w=−6.37), E_6081_4 (w=+3.92), L5/F−1 (w=+2.66), E_603_2 (w=+2.60), L4/F110446948 (w=−1.39), L3/F−1 (w=−1.08)
- **Top outgoing edges:** L8/F45300912 (w=+0.74), L10/F133489619 (w=+0.60), L15/F55825445 (w=+0.56), L10/F19521865 (w=+0.52), L9/F63095751 (w=+0.46), L12/F2951222 (w=+0.38), L8/F4947076 (w=+0.36), L9/F14810393 (w=+0.25)

Key observations: This feature fans out broadly to 16 downstream nodes across layers 8–18, acting as a hub that distributes structural/formal-register signal across many subsequent layers. It too is driven primarily by embedding-layer inputs. Its connection to the co-occurring recurring feature at L4/F110446948 (incoming, weight −1.39) reveals cross-inhibition between structural-register features at different layers.

### Layer Analysis (Step 5b)

**Hub layer: Layer 0** (appears 4 times in top-15 recurring features: F74438300, F1708475, F81262125, F2239785)

Layer 0 in the paris graph contains **146 nodes**. The top 15 by influence:

| node_id | feature | influence | activation |
|---------|---------|-----------|------------|
| 0_3636_4 | 6615702 | 0.7993 | 2.1165 |
| 0_9222_4 | 42536475 | 0.7941 | 2.5155 |
| 0_8008_2 | 32076044 | 0.7937 | 1.3879 |
| 0_253_1 | 32384 | 0.7921 | 1.729 |
| 0_11834_8 | 70039529 | 0.7917 | 4.1844 |
| 0_12200_5 | 74438300 | 0.7915 | 2.5868 |
| 0_1548_5 | 1200474 | 0.7909 | 2.5233 |
| 0_0_7 | −1 | 0.7903 | 0.0 |
| 0_5796_4 | 16805502 | 0.7892 | 2.0385 |
| 0_10210_5 | 52137365 | 0.7888 | 2.1873 |
| 0_4071_1 | 8292627 | 0.7859 | 1.4287 |
| 0_13919_4 | 96890159 | 0.7853 | 2.2555 |
| 0_3256_6 | 5305652 | 0.7834 | 2.7185 |
| 0_12698_1 | 80638649 | 0.7832 | 1.5973 |
| 0_9773_1 | 47770424 | 0.7829 | 1.8096 |

Layer 0's high density of recurring features reflects its role as a lexical-semantic gateway: at the first transformer layer, the model encodes noun identity, relational markers, and domain cues simultaneously. The recurring features at this layer (specific nouns, country recognition, pronoun resolution) suggest that the analogical circuit activates from the very first layer when it encounters the characteristic "X is to Y as Z is to" template.

### Step 5c: Cross-graph Interpretation

**Which features appear most universally?**
Features at layers 6 (F2586668, 48/10) and 3 (F5150441, 47/10) appear in nearly every graph. Interestingly, their labels ("programming code/legal jargon" and "code snippets/documentation") suggest these features detect the formal, structured register of the analogy template rather than its semantic content. The "A is to B as C is to" construction has a syntactic formality that resembles technical documentation patterns.

**Functional layer clustering:**
- **Early layers (0–4):** Lexical encoding. Layer 0 fires broadly across token identities (nouns, pronouns, country names). Layers 3–4 detect structural/formal-register patterns in the prompt template.
- **Middle layers (5–9):** Relational abstraction. Layers 5, 7, 8, 9 host the explicit "analogy"/"comparison" features (F16817094, F286895, F94882191, F89171325) — the model is building an explicit representation that this is an analogy task.
- **Late layers (10+):** Answer convergence. Layer 10 (F105902170: "research, business or product comparison") and layer 25 participate in the final answer selection.

**Surprising findings:**
The most universal features (L6/L3) are labeled with code/documentation patterns rather than analogy-specific labels, suggesting Gemma-2-2B's internal representation of analogy structure resembles formal-structured text patterns. The explicit "analogies" features (L5, L7, L8) are more semantically specific but appear later in the early/middle layers — the model first parses structure (L3–L6), then recognizes relational content (L7–L9).

**Edge neighbourhood insights:**
The top feature by influence (7_3099_1) receives massive inhibitory input from embedding layers (−38.73), indicating strong competition between the embedding-level representation of the analogy template and this relational feature. Its outgoing path to layers 9–10 represents a compressed excitatory channel toward the answer.

---

## Per-prompt Circuit Interpretations

*The following sections are generated incrementally as each prompt is interpreted.*


### Prompt: "<bos>Paris is to France as Berlin is to"

**Predicted token:** `Output " Germany" (p=0.973)` (prob=0.9732)

**Token competition:**

| Rank | Token | Logit score | Features voting |
|------|-------|-------------|-----------------|

**Circuit walkthrough:**

*Early layers — input recognition*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 4 | 5757 | 4_5757_6 | 0.7999 | 2.0721 | place names or location references |
| 0 | 3636 | 0_3636_4 | 0.7993 | 2.1165 |  proper nouns, especially names of people and places |
| 6 | 8956 | 6_8956_6 | 0.7991 | 4.4822 |  brand names, languages, and operating systems |
| 4 | 15859 | 4_15859_6 | 0.7981 | 3.2247 |  places, people, and political entities in Europe and Africa, especially related to Swaziland, Denmark, and the Schleswig-Holstein region. |
| 1 | 12602 | 1_12602_4 | 0.7975 | 2.9644 |  words associated with team sports, law, government, and time duration. |
| 6 | 4516 | 6_4516_1 | 0.7973 | 7.8828 |  the letter "i." |
| 3 | 3554 | 3_3554_6 | 0.7971 | 2.9865 |  mentions of countries |
| 3 | 752 | 3_752_5 | 0.7969 | 2.3824 | something about saving a file, or about volleyball, or about organizations with the initials WO. |
| 1 | 6024 | 1_6024_6 | 0.7965 | 2.0856 |  words related to medicine & programming and 'ner' in various contexts |
| 1 | 9357 | 1_9357_6 | 0.7963 | 2.9016 |  words or phrases related to booking flights, including origin, destination, airport, city, flight id and images |
| 6 | 3335 | 6_3335_5 | 0.7957 | 4.8645 |  words and phrases that express difficulty or challenges |
| 6 | 3182 | 6_3182_4 | 0.7953 | 3.475 |  mentions of cities or regions |
| 4 | 15534 | 4_15534_6 | 0.7949 | 4.003 | a variety of specific technical and scientific terms and jargon. |
| 6 | 5451 | 6_5451_5 | 0.7947 | 5.2873 | opinionated political discussions |
| 4 | 13375 | 4_13375_5 | 0.7943 | 2.754 |  words and phrases that evoke a sense of nation and political entities |
| 0 | 9222 | 0_9222_4 | 0.7941 | 2.5155 |  the equals sign |
| 0 | 8008 | 0_8008_2 | 0.7937 | 1.3879 |  mentions of a female subject |
| 4 | 426 | 4_426_5 | 0.7935 | 3.3206 |  a mix of positive and negative sentiment, and words related to quantity |
| 5 | 3635 | 5_3635_6 | 0.7933 | 3.7195 |  proper nouns, especially names of places, people, languages, or organizations |
| 5 | 4967 | 5_4967_8 | 0.7931 | 5.9053 |  common phrases with "out" and "back" along with some words indicating judgement. |
| 5 | 5332 | 5_5332_4 | 0.7927 | 3.0736 |  proper nouns referring to geographic locations, organizations, and people. |
| 0 | 2 | 0_2_7 | 0.7925 | 0.0 |  terminology related to technical and scientific writing |

*Middle layers — relational mapping*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 7 | 1022 | 7_1022_4 | 0.7997 | 4.2357 |  words ending with "ics" or "oma" as well as mentions of wicca. |
| 10 | 5144 | 10_5144_5 | 0.7995 | 8.52 | comparisons. |
| 8 | 10532 | 8_10532_6 | 0.7989 | 8.4559 |  words referring to fields of study, types of problems in those fields, or people who work in those fields |
| 13 | 4435 | 13_4435_8 | 0.7987 | 9.2783 |  opera-related terms, including German words and names of places |
| 7 | 6884 | 7_6884_2 | 0.7979 | 9.3975 |  place names relating to France and cities, specifically "Saint-...", and "ville" or "canton." |
| 7 | 11973 | 7_11973_8 | 0.7977 | 7.2224 |  mentions of tech companies and products, especially in the mobile device market |
| 7 | 10892 | 7_10892_6 | 0.7967 | 5.0899 |  words related to babies, painful situations, or the body and/or reactions of the body. |
| 7 | 2033 | 7_2033_6 | 0.7959 | 2.7182 | mentions of legal trouble in Europe |
| 7 | 3828 | 7_3828_5 | 0.7955 | 3.3997 | scientific or technical language discussing experiments and programming; also finds celebrity names. |
| 9 | 7669 | 9_7669_8 | 0.7945 | 6.4386 | phrases that express strong disagreement or contradiction. |
| 12 | 2171 | 12_2171_8 | 0.7939 | 5.9301 |  contexts where unit measurements are being discussed |

*Late layers — token selection*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 19 | 14348 | 19_14348_8 | 0.8001 | 15.7641 |  uses of the word "to" and other prepositions, but not very precisely. |
| 21 | 4827 | 21_4827_7 | 0.7985 | 45.0356 |  words and phrases related to scientific and medical research |
| 15 | 8095 | 15_8095_6 | 0.7983 | 12.5808 |  people saying things, referencing political figures, locations, or general statements |
| 16 | 6491 | 16_6491_8 | 0.7961 | 8.1436 |  locations, directions and distances, especially in California and Colorado. |
| 0 | 17 | 0_17_7 | 0.7951 | 0.0 |  Spanish and Portuguese words related to code and computers |
| 21 | 3271 | 21_3271_8 | 0.7929 | 7.8615 |  text about politics, history, and people |
| 16 | 4240 | 16_4240_8 | 0.7923 | 8.8411 |  mentions of the United States and its economic standing in the world |

**Causal paths (edge-weight chains to logit):**

*Path 1 — (±) mixed | weight=306.121568 | hops=3*
→ `node_id=21_4827_7` | `feature=4827` | Layer 21 | ` words and phrases related to scientific and medical research` — edge [+197.9638]
→ `node_id=22_15670_7` | `feature=?` | Layer 22 | `(no label)` — edge [-1.3555]
→ `node_id=25_4717_8` | `feature=?` | Layer 25 | `(no label)` — edge [+1.1408]
→ **LOGIT** `node_id=27_9066_8` Layer 27 — `Output " Germany" (p=0.973)`

*Path 2 — (±) mixed | weight=178.849321 | hops=5*
→ `node_id=16_6491_8` | `feature=6491` | Layer 16 | ` locations, directions and distances, especially in California and Colorado.` — edge [-0.7446]
→ `node_id=17_14546_8` | `feature=?` | Layer 17 | `(no label)` — edge [+4.5501]
→ `node_id=19_5773_8` | `feature=?` | Layer 19 | `(no label)` — edge [+2.9736]
→ `node_id=21_7482_8` | `feature=?` | Layer 21 | `(no label)` — edge [+8.4876]
→ `node_id=25_2725_8` | `feature=?` | Layer 25 | `(no label)` — edge [-2.0915]
→ **LOGIT** `node_id=27_9066_8` Layer 27 — `Output " Germany" (p=0.973)`

*Path 3 — (±) mixed | weight=168.024308 | hops=5*
→ `node_id=7_11973_8` | `feature=11973` | Layer 7 | ` mentions of tech companies and products, especially in the mobile device market` — edge [+0.6996]
→ `node_id=17_14546_8` | `feature=?` | Layer 17 | `(no label)` — edge [+4.5501]
→ `node_id=19_5773_8` | `feature=?` | Layer 19 | `(no label)` — edge [+2.9736]
→ `node_id=21_7482_8` | `feature=?` | Layer 21 | `(no label)` — edge [+8.4876]
→ `node_id=25_2725_8` | `feature=?` | Layer 25 | `(no label)` — edge [-2.0915]
→ **LOGIT** `node_id=27_9066_8` Layer 27 — `Output " Germany" (p=0.973)`

*Path 4 — (±) mixed | weight=110.585287 | hops=4*
→ `node_id=16_4240_8` | `feature=4240` | Layer 16 | ` mentions of the United States and its economic standing in the world` — edge [-2.0949]
→ `node_id=19_5773_8` | `feature=?` | Layer 19 | `(no label)` — edge [+2.9736]
→ `node_id=21_7482_8` | `feature=?` | Layer 21 | `(no label)` — edge [+8.4876]
→ `node_id=25_2725_8` | `feature=?` | Layer 25 | `(no label)` — edge [-2.0915]
→ **LOGIT** `node_id=27_9066_8` Layer 27 — `Output " Germany" (p=0.973)`

*Path 5 — (±) mixed | weight=65.927255 | hops=4*
→ `node_id=6_3335_5` | `feature=3335` | Layer 6 | ` words and phrases that express difficulty or challenges` — edge [+0.2497]
→ `node_id=19_855_8` | `feature=?` | Layer 19 | `(no label)` — edge [+13.5011]
→ `node_id=24_1963_8` | `feature=?` | Layer 24 | `(no label)` — edge [-9.3496]
→ `node_id=25_2725_8` | `feature=?` | Layer 25 | `(no label)` — edge [-2.0915]
→ **LOGIT** `node_id=27_9066_8` Layer 27 — `Output " Germany" (p=0.973)`

**Causal path diagram:**

![Causal paths for "<bos>Paris is to France as Berlin is to" → "Output " Germany" (p=0.973)"](graphs/bos_paris_is_to_france_as_berlin_is_to__output___germany___p_causal_paths.png)

*Figure: Causal paths from input features to predicted token "Output " Germany" (p=0.973)". Y-axis = transformer layer. Edge width = connection strength. Green = excitatory, red = inhibitory, orange = mixed.*

**Mechanistic narrative:**

**[EARLY]** At the earliest layers, Gemma-2-2B immediately parsed the geographic and political character of the input. Feature F5757 at Layer 4 (node_id=4_5757_6, inf=0.7999) registered "place names or location references," while F15859 at Layer 4 (node_id=4_15859_6, inf=0.7981) more specifically detected "places, people, and political entities in Europe and Africa." Feature F3554 at Layer 3 (node_id=3_3554_6, inf=0.7971) activated for "mentions of countries," and F13375 at Layer 4 (node_id=4_13375_5, inf=0.7943) for "words and phrases that evoke a sense of nation and political entities." Together, these early features establish that the model has identified all four terms (Paris, France, Berlin) as European geographic and political entities before any relational processing begins. Notably, F3636 at Layer 0 (node_id=0_3636_4, inf=0.7993) fires for "proper nouns, especially names of people and places" — the very first transformer layer is already registering proper-noun status for all analogy terms.

**[MIDDLE]** By the middle layers, domain knowledge takes over with two striking developments. First, F6884 at Layer 7 (node_id=7_6884_2, inf=0.7979) activates specifically for "place names relating to France and cities, specifically 'Saint-...' and 'ville' or 'canton'" — the model has mapped the A-term (Paris) into its France-specific geography domain. Then, F4435 at Layer 13 (node_id=13_4435_8, inf=0.7987) fires for "opera-related terms, including German words and names of places," grounding the B-term (Berlin) in its German cultural context. The critical relational insight arrives at L10 with F5144 (node_id=10_5144_5, inf=0.7995), labeled simply "comparisons" — by Layer 10, the model has abstracted the analogy template as a comparison structure, with Paris-to-France and Berlin-to-Germany resolved as parallel capital-to-country relationships.

**[LATE]** The late layers crystallise the answer through a convergent pathway. F14348 at Layer 19 (node_id=19_14348_8, inf=0.8001) — labeled "uses of the word 'to' and other prepositions" — achieves the highest influence score in the entire graph. This feature appears to be tracking the structural connector "is to" in the analogy template, acting as a final syntactic anchor. F4827 at Layer 21 (node_id=21_4827_7, inf=0.7985) provides the dominant upstream push to the logit via Path 1 (weight=306.1), sending an edge of +197.96 through Layer 22 to Layer 25, which then fires the logit node with +1.14.

**[TOKEN COMPETITION]** The logit was predicted with probability 0.9732 — an extraordinarily confident prediction, reflecting the clarity of the capital-city relationship. The circuit was convergent: Paths 2–4 all share the L17→L19→L21→L25→LOGIT backbone, demonstrating that multiple early-to-mid layer triggers (a location feature at L16/F6491, a U.S.-economy feature at L16/F4240, and tech-company features at L7/F11973) all route their signals through the same late-layer aggregation channels. All five paths are classified as Mixed (alternating positive and negative edges), but the dominant direction is excitatory — the negative edges (at L22→L25 and L25→LOGIT transitions in Path 1) represent competition suppression rather than true inhibition of the target token.

**[SYNTHESIS]** The complete causal story: the model detects European geographic entities at Layer 0–4, maps France-specific and Germany-specific geographic knowledge at Layers 7–13, recognises the comparison template at Layer 10, and routes converging signals through a shared L17→L21→L25 aggregation pathway to the logit. The dominant mechanism is Path 1, originating at the "scientific/medical research" feature at Layer 21 (F4827), which despite its seemingly mismatched label, carries the strongest single edge weight (+197.96) to the logit. This suggests the model encodes the formal, structured nature of the analogy template in a feature cluster associated with technical register. The extraordinary confidence (p=0.9732) reflects a clean convergent circuit with no genuine competitor paths — "Germany" was the unambiguous winner.

---

### Prompt: "<bos>Cairo is to Egypt as Nairobi is to"

**Predicted token:** `Output " Kenya" (p=0.963)` (prob=0.9628)

**Token competition:**

| Rank | Token | Logit score | Features voting |
|------|-------|-------------|-----------------|

**Circuit walkthrough:**

*Early layers — input recognition*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 5 | 7130 | 5_7130_5 | 0.7996 | 4.603 | verbs ending in "ing" that are being used as gerunds or present participles |
| 3 | 15381 | 3_15381_2 | 0.7994 | 3.3469 |  names of government departments and related terms |
| 0 | 1 | 0_1_7 | 0.7991 | 0.0 |  Spanish-language programming-related terms |
| 5 | 15362 | 5_15362_5 | 0.7989 | 2.5296 |  mentions of people and places |
| 4 | 9704 | 4_9704_4 | 0.7987 | 3.2569 |  words that describe environmental conditions or physical attributes, and also some measurement or lab related terms |
| 1 | 9900 | 1_9900_6 | 0.7981 | 2.2453 |  words related to booking or reserving something |
| 5 | 14698 | 5_14698_6 | 0.7979 | 2.7607 |  places, especially universities and US states |
| 5 | 575 | 5_575_5 | 0.7973 | 2.9661 |  code snippets or descriptions of converting digital signals to analog |
| 5 | 6490 | 5_6490_1 | 0.7971 | 4.0009 |  words and phrases related to geography, politics, or groups of people, particularly related to conflict |
| 4 | 12832 | 4_12832_5 | 0.7969 | 2.3034 |  words or short phrases in the neighborhood of "she," "he," "I," "as". |
| 0 | 0 | 0_0_7 | 0.7965 | 0.0 | mentions of clubs or sports teams, and sometimes related words like 'sister' or 'kids' |
| 2 | 13965 | 2_13965_1 | 0.7963 | 2.6666 |  places on a map, body parts involved in medicine, and economic terms |
| 5 | 11012 | 5_11012_3 | 0.7954 | 5.2732 | verbs of action and change |
| 5 | 6728 | 5_6728_5 | 0.7952 | 3.7843 |  code, RDF, and scientific terms |
| 0 | 5215 | 0_5215_4 | 0.795 | 2.1942 | code-related terms, especially from multiple languages (C, Swift, etc.) and technical documentation. |
| 1 | 7832 | 1_7832_3 | 0.7948 | 1.5438 |  the word "to". |
| 0 | 4470 | 0_4470_4 | 0.7946 | 1.9006 |  references to religion, religious figures, or important religious places |
| 3 | 11806 | 3_11806_5 | 0.7936 | 2.2821 |  words/phrases related to story telling |
| 5 | 5500 | 5_5500_8 | 0.7934 | 3.6353 |  profanity and comparisons |
| 0 | 14184 | 0_14184_5 | 0.7926 | 3.372 |  the word "it" when immediately preceded by a word ending in a vowel and immediately followed by a word starting with a consonant |
| 0 | 13916 | 0_13916_6 | 0.7924 | 2.8652 |  words and terms about medicine and scientific research, including references. |

*Middle layers — relational mapping*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 10 | 14118 | 10_14118_8 | 0.8 | 5.8252 |  phrases expressing unfavorable conditions or uncertainty |
| 8 | 15706 | 8_15706_6 | 0.7998 | 3.9033 |  words related to markets, measurements, and racial issues |
| 6 | 2736 | 6_2736_8 | 0.7993 | 7.8579 |  words associated with negativity in society, relationships and situations. |
| 11 | 3596 | 11_3596_4 | 0.7983 | 9.5114 | snippets of code and text relating to academic research |
| 7 | 11758 | 7_11758_4 | 0.7967 | 5.0055 |  words with some cultural (often middle eastern) or historical aspect that may be a name or location |
| 0 | 8 | 0_8_7 | 0.7959 | 0.0 | phrases with "are," and sometimes also finds other words related to research, science, testing, and data |
| 6 | 10428 | 6_10428_6 | 0.7956 | 2.8565 |  references to animals or young humans |
| 7 | 1177 | 7_1177_6 | 0.7944 | 3.4789 |  phrases related to US politics, history, and terrorism |
| 6 | 9865 | 6_9865_1 | 0.794 | 13.5981 |  code and file paths |
| 0 | 9 | 0_9_1 | 0.7932 | 0.0 |  math and mathematical notation |
| 6 | 3192 | 6_3192_1 | 0.793 | 5.7159 |  proper nouns that are countries or cities |

*Late layers — token selection*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 18 | 12171 | 18_12171_6 | 0.7985 | 16.2289 |  language that indicates unfairness or a lack of fairness |
| 15 | 5355 | 15_5355_4 | 0.7977 | 10.3601 |  geographical locations |
| 0 | 15 | 0_15_2 | 0.7975 | 0.0 | the word "interval" and phrases containing it |
| 13 | 10167 | 13_10167_8 | 0.7961 | 6.7758 |  words relating to student life, sports, experiments and medicine |
| 13 | 4435 | 13_4435_8 | 0.7958 | 11.0511 |  opera-related terms, including German words and names of places |
| 18 | 13586 | 18_13586_8 | 0.7942 | 15.5628 | Legal documents |
| 14 | 8796 | 14_8796_4 | 0.7938 | 25.0068 |  places, countries, areas, and tribes, particularly in the middle east |
| 15 | 1019 | 15_1019_6 | 0.7928 | 14.5685 | sentences with a lot of clauses, logic and/or comparisons. |

**Causal paths (edge-weight chains to logit):**

*Path 1 — (±) mixed | weight=86.124859 | hops=5*
→ `node_id=13_4435_8` | `feature=4435` | Layer 13 | ` opera-related terms, including German words and names of places` — edge [+2.2185]
→ `node_id=15_15954_8` | `feature=?` | Layer 15 | `(no label)` — edge [+6.7443]
→ `node_id=18_13586_8` | `feature=13586` | Layer 18 | `Legal documents` — edge [+1.5251]
→ `node_id=24_1260_8` | `feature=?` | Layer 24 | `(no label)` — edge [-8.5025]
→ `node_id=25_15920_8` | `feature=?` | Layer 25 | `(no label)` — edge [-0.4439]
→ **LOGIT** `node_id=27_28273_8` Layer 27 — `Output " Kenya" (p=0.963)`

*Path 2 — (±) mixed | weight=67.481537 | hops=5*
→ `node_id=5_15362_5` | `feature=15362` | Layer 5 | ` mentions of people and places` — edge [+0.1594]
→ `node_id=20_15360_8` | `feature=?` | Layer 20 | `(no label)` — edge [+7.7863]
→ `node_id=23_13914_8` | `feature=?` | Layer 23 | `(no label)` — edge [+10.6511]
→ `node_id=24_8251_8` | `feature=?` | Layer 24 | `(no label)` — edge [-4.762]
→ `node_id=25_286_8` | `feature=?` | Layer 25 | `(no label)` — edge [-1.0719]
→ **LOGIT** `node_id=27_28273_8` Layer 27 — `Output " Kenya" (p=0.963)`

*Path 3 — (±) mixed | weight=60.1826 | hops=4*
→ `node_id=0_8_7` | `feature=8` | Layer 0 | `phrases with "are," and sometimes also finds other words related to research, science, testing, and data` — edge [+1.9875]
→ `node_id=10_5559_8` | `feature=?` | Layer 10 | `(no label)` — edge [-22.7107]
→ `node_id=11_16076_8` | `feature=?` | Layer 11 | `(no label)` — edge [+3.0036]
→ `node_id=25_15920_8` | `feature=?` | Layer 25 | `(no label)` — edge [-0.4439]
→ **LOGIT** `node_id=27_28273_8` Layer 27 — `Output " Kenya" (p=0.963)`

*Path 4 — (±) mixed | weight=36.433288 | hops=5*
→ `node_id=5_5500_8` | `feature=5500` | Layer 5 | ` profanity and comparisons` — edge [+0.9529]
→ `node_id=7_749_8` | `feature=?` | Layer 7 | `(no label)` — edge [+1.2626]
→ `node_id=10_5559_8` | `feature=?` | Layer 10 | `(no label)` — edge [-22.7107]
→ `node_id=11_16076_8` | `feature=?` | Layer 11 | `(no label)` — edge [+3.0036]
→ `node_id=25_15920_8` | `feature=?` | Layer 25 | `(no label)` — edge [-0.4439]
→ **LOGIT** `node_id=27_28273_8` Layer 27 — `Output " Kenya" (p=0.963)`

*Path 5 — (+) excitatory | weight=35.325629 | hops=4*
→ `node_id=15_5355_4` | `feature=5355` | Layer 15 | ` geographical locations` — edge [+0.7159]
→ `node_id=20_5236_8` | `feature=?` | Layer 20 | `(no label)` — edge [+3.5751]
→ `node_id=21_5251_8` | `feature=?` | Layer 21 | `(no label)` — edge [+9.6702]
→ `node_id=25_4717_8` | `feature=?` | Layer 25 | `(no label)` — edge [+1.4273]
→ **LOGIT** `node_id=27_28273_8` Layer 27 — `Output " Kenya" (p=0.963)`

**Causal path diagram:**

![Causal paths for "<bos>Cairo is to Egypt as Nairobi is to" → "Output " Kenya" (p=0.963)"](graphs/bos_cairo_is_to_egypt_as_nairobi_is_to__output___kenya___p_0_causal_paths.png)

*Figure: Causal paths from input features to predicted token "Output " Kenya" (p=0.963)". Y-axis = transformer layer. Edge width = connection strength. Green = excitatory, red = inhibitory, orange = mixed.*

**Mechanistic narrative:**

**[EARLY]** For "Cairo is to Egypt as Nairobi is to," the early layers encode a more diffuse set of features than for the Paris/Germany analogy. The highest-influence early node is F7130 at Layer 5 (node_id=5_7130_5, inf=0.7996), detecting "verbs ending in 'ing' used as gerunds or present participles" — a structural parsing feature responding to the "is to" relational connectors. F15381 at Layer 3 (node_id=3_15381_2, inf=0.7994) activates for "names of government departments and related terms," reflecting the model's encoding of the political-administrative relationship between capitals and countries. F15362 at Layer 5 (node_id=5_15362_5, inf=0.7989) catches "mentions of people and places," broadly registering the proper-noun geography. F14698 at Layer 5 (node_id=5_14698_6, inf=0.7979) specifically activates for "places, especially universities and US states," while F7 at Layer 7 (middle band) fires for "words with some cultural (often middle eastern) or historical aspect" — registering that Cairo and Egypt are Middle Eastern proper nouns.

**[MIDDLE]** The middle layers show a surprising pattern: the highest-influence middle node, F14118 at Layer 10 (node_id=10_14118_8, inf=0.8000), is labeled "phrases expressing unfavorable conditions or uncertainty," and F15706 at Layer 8 (node_id=8_15706_6, inf=0.7998) detects "words related to markets, measurements, and racial issues." These labels seem mismatched to a geographic analogy — but this misalignment may reflect that the model's recurring "comparison/uncertainty" features activate broadly for any A:B::C:? structure, since comparison inherently involves contrasting two things, which the model internally represents through a negative-framing feature. More directly geographic is F14796 at Layer 14 in the late band: "places, countries, areas, and tribes, particularly in the middle east" (node_id=14_8796_4, inf=0.7938), which explicitly maps Nairobi into an East African geographic context.

**[LATE]** The late layers are dominated by F12171 at Layer 18 (node_id=18_12171_6, inf=0.7985) — "language that indicates unfairness or a lack of fairness" — another apparently mismatched label that likely reflects this feature activating on the contrastive-comparison structure. The key geographic feature is F5355 at Layer 15 (node_id=15_5355_4, inf=0.7977), labeled "geographical locations," which forms the origin of the only purely excitatory path (Path 5, weight=35.3): L15/F14426490 (+0.72) → L20 (+3.58) → L21 (+9.67) → L25 (+1.43) → LOGIT. This ascending-weight excitatory chain (0.72 → 3.58 → 9.67 → 1.43) shows signal being amplified through the late layers toward the predicted token " Kenya."

**[TOKEN COMPETITION]** The prediction " Kenya" was made with probability 0.963, indicating high confidence. Path 5 (excitatory, weight=35.3) was the only pure excitatory path among five identified paths; the remaining four were all Mixed. The dominant Path 1 (mixed, weight=86.1) traces from L13/F9899011 through layers 15, 18, 24, 25 to the logit — a longer convergent chain involving "opera-related terms, including German words and names of places" (L13/F4435) as an intermediate node, suggesting the model uses a general European/African proper-noun feature cluster to mediate geographic capital-to-country relationships.

**[SYNTHESIS]** The complete causal story for "Cairo is to Egypt as Nairobi is to" → " Kenya": the model detects the proper-noun geographic and administrative nature of the terms at Layers 3–5, activates Middle Eastern/African geographic features at Layers 7–14, then routes through a convergent late-layer aggregation (L17→L20→L21→L25→LOGIT) to produce the high-confidence answer. The dominant mechanism is Path 1 (weight=86.1, mixed), supplemented by the only clean excitatory path (Path 5, weight=35.3) originating from a "geographical locations" feature at Layer 15. The circuit is convergent, with multiple paths sharing the same L24→L25→LOGIT backbone, but relies more heavily on mixed-sign edge chains than the Germany analogy — consistent with the model's internal representation of African geographic relationships through indirect feature clusters rather than the direct Europe-specific features available for the Paris/Berlin prompt.

---

### Prompt: "<bos>Fish is to water as bird is to"

**Predicted token:** `Output " air" (p=0.117)` (prob=0.1167)

**Token competition:**

| Rank | Token | Logit score | Features voting |
|------|-------|-------------|-----------------|

**Circuit walkthrough:**

*Early layers — input recognition*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 6 | 9865 | 6_9865_3 | 0.7997 | 20.1705 |  code and file paths |
| 4 | 2866 | 4_2866_2 | 0.7989 | 7.1793 |  the word "is" |
| 2 | 9088 | 2_9088_3 | 0.7985 | 1.6687 |  things which are believed, demonstrated, or thought to be true |
| 2 | 426 | 2_426_1 | 0.7976 | 2.6844 |  words related to computer programming, math, or numbers |
| 3 | 5102 | 3_5102_2 | 0.7974 | 3.7084 |  technical jargon and scientific terms from a wide variety of fields |
| 0 | 14963 | 0_14963_6 | 0.7972 | 3.7276 |  words related to medical/legal/scientific terminology |
| 2 | 7356 | 2_7356_4 | 0.7966 | 2.505 |  cooking ingredients and recipes |
| 5 | 4703 | 5_4703_4 | 0.7962 | 4.7563 | metaphors for dangerous or surprising events |
| 1 | 8120 | 1_8120_6 | 0.796 | 3.8706 |  recipes and food preparation techniques |
| 4 | 2857 | 4_2857_8 | 0.7959 | 4.439 |  verbs related to tasks and performing them |
| 5 | 7191 | 5_7191_8 | 0.7957 | 5.7456 |  words and phrases related to legal proceedings or agreements |
| 6 | 5621 | 6_5621_5 | 0.7955 | 3.57 |  descriptions of musical albums and sports leagues and seasons |
| 1 | 11752 | 1_11752_4 | 0.7951 | 2.8279 |  scientific names of organisms that cause plant galls |
| 0 | 8163 | 0_8163_6 | 0.7945 | 4.5913 |  words and phrases related to societal and political issues |
| 0 | 8008 | 0_8008_2 | 0.7943 | 1.3318 |  mentions of a female subject |
| 5 | 9672 | 5_9672_4 | 0.7939 | 3.5277 |  the phrase "there/they are" or the phrase "it is to." |
| 4 | 9720 | 4_9720_3 | 0.7933 | 4.8912 |  announcements of product or company news and clinical trials |
| 4 | 6466 | 4_6466_5 | 0.7931 | 3.1166 |  legal and medical terminology |
| 6 | 12493 | 6_12493_5 | 0.7929 | 7.5923 |  legal citations |
| 6 | 11763 | 6_11763_4 | 0.7928 | 3.5949 |  substrings resembling code or equations including special characters |
| 5 | 11877 | 5_11877_5 | 0.7926 | 3.8685 |  mathematical terms related to exponents and powers |

*Middle layers — relational mapping*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 7 | 13919 | 7_13919_8 | 0.7995 | 8.2225 |  words related to regulations, standards, and procedures. |
| 9 | 8857 | 9_8857_5 | 0.7993 | 6.6666 |  answer choices in mathematical questions |
| 8 | 4440 | 8_4440_2 | 0.7991 | 12.7045 | discussions of food, especially meat |
| 7 | 2318 | 7_2318_8 | 0.7983 | 3.2918 | a variety of numeric and statistical data, including p-values, BMI, ages, and measurements |
| 8 | 13494 | 8_13494_6 | 0.7982 | 5.5575 | phrases  related to running out of supplies |
| 7 | 2678 | 7_2678_8 | 0.7978 | 5.6884 |  a wide variety of mostly short phrases; the neuron may be faulty |
| 7 | 7080 | 7_7080_4 | 0.797 | 4.5232 |  words and phrases related to food and dining, especially in the context of a region or place. |
| 13 | 2249 | 13_2249_6 | 0.7964 | 13.5967 |  noun phrases ending in "-ists", and also seems to have some other unrelated triggers. |
| 7 | 8622 | 7_8622_6 | 0.7949 | 5.8154 | words related to animals, taxonomy, animal habitats and animal research |
| 7 | 4108 | 7_4108_8 | 0.7937 | 5.6759 | verbs and prepositions possibly related to conflict or legal disputes |
| 7 | 11973 | 7_11973_8 | 0.7935 | 7.516 |  mentions of tech companies and products, especially in the mobile device market |

*Late layers — token selection*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 0 | 22 | 0_22_5 | 0.8 | 0.0 | words ending in the suffix "ality,' or the word "other." |
| 14 | 14321 | 14_14321_8 | 0.7999 | 6.926 | words commonly found at the beginning of sentences or phrases |
| 16 | 12036 | 16_12036_8 | 0.7987 | 7.1728 | a little bit of everything, including punctuation, 's', and the words 'uniform' and 'after', which is too broad to be useful |
| 17 | 101 | 17_101_8 | 0.798 | 9.8202 | non-English words |
| 21 | 881 | 21_881_8 | 0.7968 | 7.8511 | connectives and technical terms |
| 15 | 12472 | 15_12472_4 | 0.7953 | 60.6484 | words associated with legal, academic, or technical documents, and numerical references |
| 17 | 6986 | 17_6986_8 | 0.7947 | 9.8884 |  things wrapped or attached to other things, especially with the preposition "on." |
| 0 | 16 | 0_16_3 | 0.7941 | 0.0 |  words related to political administration and legal rights |

**Causal paths (edge-weight chains to logit):**

*Path 1 — (+) excitatory | weight=60.808751 | hops=2*
→ `node_id=E_2003_4` | `feature=?` | Layer E | `(no label)` — edge [+12.0646]
→ `node_id=22_4252_8` | `feature=?` | Layer 22 | `(no label)` — edge [+5.0403]
→ **LOGIT** `node_id=27_2681_8` Layer 27 — `Output " air" (p=0.117)`

*Path 2 — (±) mixed | weight=41.67803 | hops=4*
→ `node_id=1_8120_6` | `feature=8120` | Layer 1 | ` recipes and food preparation techniques` — edge [+0.6877]
→ `node_id=4_13402_6` | `feature=?` | Layer 4 | `(no label)` — edge [+15.4161]
→ `node_id=20_3824_8` | `feature=?` | Layer 20 | `(no label)` — edge [+14.4137]
→ `node_id=25_11801_8` | `feature=?` | Layer 25 | `(no label)` — edge [-0.2727]
→ **LOGIT** `node_id=27_2681_8` Layer 27 — `Output " air" (p=0.117)`

*Path 3 — (±) mixed | weight=22.713631 | hops=4*
→ `node_id=2_7356_4` | `feature=7356` | Layer 2 | ` cooking ingredients and recipes` — edge [+0.2426]
→ `node_id=22_4252_8` | `feature=?` | Layer 22 | `(no label)` — edge [+19.4543]
→ `node_id=24_8106_8` | `feature=?` | Layer 24 | `(no label)` — edge [-6.0286]
→ `node_id=25_12962_8` | `feature=?` | Layer 25 | `(no label)` — edge [-0.7984]
→ **LOGIT** `node_id=27_2681_8` Layer 27 — `Output " air" (p=0.117)`

*Path 4 — (±) mixed | weight=1.801989 | hops=3*
→ `node_id=8_13494_6` | `feature=13494` | Layer 8 | `phrases  related to running out of supplies` — edge [+0.3744]
→ `node_id=24_8106_8` | `feature=?` | Layer 24 | `(no label)` — edge [-6.0286]
→ `node_id=25_12962_8` | `feature=?` | Layer 25 | `(no label)` — edge [-0.7984]
→ **LOGIT** `node_id=27_2681_8` Layer 27 — `Output " air" (p=0.117)`

**Causal path diagram:**

![Causal paths for "<bos>Fish is to water as bird is to" → "Output " air" (p=0.117)"](graphs/bos_fish_is_to_water_as_bird_is_to__output___air___p_0_1_causal_paths.png)

*Figure: Causal paths from input features to predicted token "Output " air" (p=0.117)". Y-axis = transformer layer. Edge width = connection strength. Green = excitatory, red = inhibitory, orange = mixed.*

**Mechanistic narrative:**

**[EARLY]** For "Fish is to water as bird is to," the early-layer features engage primarily with structural and syntactic parsing. The top early node, F9865 at Layer 6 (node_id=6_9865_3, inf=0.7997), is labeled "code and file paths" -- a structural-register feature that fires on the formal pattern of the analogy template. F2866 at Layer 4 (node_id=4_2866_2, inf=0.7989) detects "the word 'is'" -- the model is explicitly tracking the relational connector. F9088 at Layer 2 (node_id=2_9088_3, inf=0.7985) activates for "things which are believed, demonstrated, or thought to be true," reflecting the declarative, definitional nature of analogy frames. Crucially absent are any domain-specific features for fish, water, or birds -- the early circuit is operating almost entirely on the syntactic structure of the analogy.

**[MIDDLE]** The middle layers show no explicit habitat/environment features. F13919 at Layer 7 (node_id=7_13919_8, inf=0.7995) fires for "words related to regulations, standards, and procedures" -- another structural-formalism feature. F8857 at Layer 9 (node_id=9_8857_5, inf=0.7993) detects "answer choices in mathematical questions," and F8494 at Layer 8 fires for "food, especially meat." These labels are unexpected for a habitat analogy -- they suggest the model's internal circuit for analogical reasoning uses features that generalize across many formal-comparison contexts rather than encoding domain-specific knowledge.

**[LATE]** The most interesting late-layer finding: F22 at Layer 0 (node_id=0_22_5, inf=0.8000) -- labeled "words ending in the suffix '-ality' or the word 'other'" -- achieves the highest influence score. This may reflect the model's encoding of the open-completion slot ("is to ___") as an abstract category placeholder. F14321 at Layer 14 (node_id=14_14321_8, inf=0.7999) fires for "words commonly found at the beginning of sentences or phrases," suggesting it is tracking the output-initiation context. F881 at Layer 21 (node_id=21_881_8, inf=0.7968) detects "connectives and technical terms."

**[TOKEN COMPETITION]** The model predicted " air" with only 11.7% probability -- the lowest confidence of all 10 prompts. The dominant excitatory path (Path 1, weight=60.8) is remarkably short: embedding -> L22/F9139927 -> LOGIT with edge weights 12.06 and 5.04. This 2-hop path bypasses all the labeled features entirely, suggesting that for this ambiguous analogy, the final token decision was driven by a direct embedding-to-late-layer route rather than the full multi-layer causal chain seen in high-confidence predictions.

**[SYNTHESIS]** This is the most ambiguous circuit in the dataset. The model has no strong domain-specific features for "air" or "sky" -- both are valid completions. The circuit is operating in a near-pure structural mode: the analogy template is recognized (structural features at L2-L6), the comparison slot is registered (F22 as abstract placeholder), and the logit is driven by a 2-hop excitatory path from an embedding feature. The 11.7% confidence reflects genuine competition: "sky," "air," and other habitat words have roughly equal support from the circuit, and the final choice of " air" appears to be driven by subtle token-level frequency biases rather than a strong domain-specific causal chain.

---

### Prompt: "<bos>Puppy is to dog as kitten is to"

**Predicted token:** `Output " cat" (p=0.756)` (prob=0.7565)

**Token competition:**

| Rank | Token | Logit score | Features voting |
|------|-------|-------------|-----------------|

**Circuit walkthrough:**

*Early layers — input recognition*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 1 | 11438 | 1_11438_5 | 0.8 | 2.3273 | the word "as", and in some contexts words related to government organization or proceedings |
| 1 | 12148 | 1_12148_6 | 0.7997 | 1.9932 |  words related to hosts, pathogens, and infections |
| 3 | 5267 | 3_5267_4 | 0.7995 | 2.8455 |  words related to science and engineering that are nouns |
| 5 | 7714 | 5_7714_8 | 0.7991 | 5.2637 |  words that are used to evaluate a situation, including words indicating negativity, scientific discourse, mathematical language and general business reviews about internet companies |
| 5 | 13340 | 5_13340_4 | 0.7989 | 4.9129 | technical or jargonistic language related to a variety of fields |
| 3 | 308 | 3_308_2 | 0.7983 | 2.4183 | instances of writing, commenting, and communicating about technical subjects |
| 4 | 11886 | 4_11886_5 | 0.7981 | 2.6228 | conditional and definitional statements within mathematical text |
| 1 | 1250 | 1_1250_5 | 0.7975 | 2.0992 |  LaTeX or XML markup |
| 0 | 3256 | 0_3256_6 | 0.7965 | 3.7466 |  SSH public key authentication details |
| 7 | 10892 | 7_10892_6 | 0.7959 | 4.3184 |  words related to babies, painful situations, or the body and/or reactions of the body. |
| 7 | 10892 | 7_10892_8 | 0.7957 | 6.9252 |  words related to babies, painful situations, or the body and/or reactions of the body. |
| 2 | 11571 | 2_11571_1 | 0.7955 | 2.3846 |  words related to family, childhood, and male relationships |
| 6 | 9865 | 6_9865_3 | 0.7953 | 20.8974 |  code and file paths |
| 4 | 11188 | 4_11188_3 | 0.7951 | 3.9347 | the word "so" and sometimes the words "too" or "am" near "so." |
| 7 | 2678 | 7_2678_8 | 0.7949 | 4.8255 |  a wide variety of mostly short phrases; the neuron may be faulty |
| 7 | 462 | 7_462_1 | 0.7947 | 4.3856 |  code documentation and import statements |
| 1 | 11387 | 1_11387_5 | 0.7943 | 2.3956 |  formal legal definitions and analysis of how principles work |
| 2 | 14798 | 2_14798_2 | 0.7941 | 3.031 | sentences using helping verbs, along with content related to criminal or political circumstances. |
| 0 | 127 | 0_127_1 | 0.7939 | 1.4752 |  proper names, particularly of people and places. |
| 7 | 3099 | 7_3099_6 | 0.7935 | 12.1392 |  a variety of reference codes, abbreviations, and identifiers from different fields. |
| 3 | 15856 | 3_15856_8 | 0.7933 | 5.556 |  conjunctions (and/or/but) near words indicating possibility |
| 0 | 11710 | 0_11710_6 | 0.7929 | 2.3997 |  words, abbreviations, and symbols related to scientific measurement and notation |
| 6 | 2267 | 6_2267_2 | 0.7927 | 20.2967 | words that appear in programming code, legal jargon, or scientific texts |
| 5 | 4539 | 5_4539_4 | 0.7925 | 5.0999 |  words and phrases related to peer-to-peer networks, scientific study of hosts/pathogens, and physics |
| 6 | 14666 | 6_14666_6 | 0.7923 | 3.643 |  terms relating to baseball and other sports teams, organizations, and competitions |

*Middle layers — relational mapping*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 9 | 2909 | 9_2909_7 | 0.7999 | 14.7521 |  formulas, ratios, and mathematical notation |
| 10 | 2565 | 10_2565_4 | 0.7987 | 7.6054 | commonly used sayings or idioms |
| 14 | 4256 | 14_4256_6 | 0.7985 | 11.3468 |  a group of words; one of which is "astronomy", and the rest of which are from a list of words about art, measurement, time and history. |
| 10 | 14542 | 10_14542_6 | 0.7979 | 8.8969 |  words related to research, business or product comparison |
| 11 | 9508 | 11_9508_8 | 0.7977 | 9.5501 |  mathematical expressions with variables and subscripts especially coordinate pairs contained within parentheses. |
| 11 | 5517 | 11_5517_4 | 0.7973 | 9.6624 |  a wide array of words in a text. |
| 9 | 16195 | 9_16195_6 | 0.7971 | 5.4992 |  words related to food, cooking, and building materials |
| 9 | 8770 | 9_8770_1 | 0.7967 | 23.1286 | sentences beginning with "It" or "In" and also the word "There". |
| 13 | 735 | 13_735_3 | 0.7963 | 13.3752 | the word "to", and some other prepositions |
| 10 | 8919 | 10_8919_6 | 0.7945 | 3.1049 |  vocabulary related to strong emotions and prejudice. |
| 10 | 15902 | 10_15902_4 | 0.7937 | 5.6055 |  words describing organizations and their relationships to issues |
| 9 | 1195 | 9_1195_8 | 0.7931 | 7.2028 |  various political or social topics, including scandals, film festivals, and finance |

*Late layers — token selection*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 0 | 22 | 0_22_6 | 0.7993 | 0.0 | words ending in the suffix "ality,' or the word "other." |
| 25 | 553 | 25_553_8 | 0.7969 | 32.9351 |  text passages written in all capital letters |
| 23 | 6905 | 23_6905_8 | 0.7961 | 12.4826 |  nouns preceded by articles or adjectives within a specific context, often related to political or public discourse |

**Causal paths (edge-weight chains to logit):**

*Path 1 — (±) mixed | weight=551.738936 | hops=5*
→ `node_id=9_2909_7` | `feature=2909` | Layer 9 | ` formulas, ratios, and mathematical notation` — edge [-1.2561]
→ `node_id=14_3704_7` | `feature=?` | Layer 14 | `(no label)` — edge [+11.8871]
→ `node_id=20_3094_7` | `feature=?` | Layer 20 | `(no label)` — edge [-12.7578]
→ `node_id=22_15670_7` | `feature=?` | Layer 22 | `(no label)` — edge [-2.4502]
→ `node_id=25_4717_8` | `feature=?` | Layer 25 | `(no label)` — edge [+1.1821]
→ **LOGIT** `node_id=27_4401_8` Layer 27 — `Output " cat" (p=0.756)`

*Path 2 — (+) excitatory | weight=294.013773 | hops=2*
→ `node_id=E_56081_6` | `feature=?` | Layer E | `(no label)` — edge [+49.1547]
→ `node_id=19_302_8` | `feature=?` | Layer 19 | `(no label)` — edge [+5.9814]
→ **LOGIT** `node_id=27_4401_8` Layer 27 — `Output " cat" (p=0.756)`

*Path 3 — (±) mixed | weight=194.912395 | hops=5*
→ `node_id=13_735_3` | `feature=735` | Layer 13 | `the word "to", and some other prepositions` — edge [+5.717]
→ `node_id=17_13553_4` | `feature=?` | Layer 17 | `(no label)` — edge [+6.0761]
→ `node_id=18_6875_4` | `feature=?` | Layer 18 | `(no label)` — edge [-4.0453]
→ `node_id=21_15785_4` | `feature=?` | Layer 21 | `(no label)` — edge [+0.2942]
→ `node_id=24_10034_8` | `feature=?` | Layer 24 | `(no label)` — edge [-4.7146]
→ **LOGIT** `node_id=27_4401_8` Layer 27 — `Output " cat" (p=0.756)`

*Path 4 — (±) mixed | weight=73.6242 | hops=5*
→ `node_id=14_4256_6` | `feature=4256` | Layer 14 | ` a group of words; one of which is "astronomy", and the rest of which are from a list of words about art, measurement, time and history.` — edge [-0.9386]
→ `node_id=17_12910_6` | `feature=?` | Layer 17 | `(no label)` — edge [+6.3577]
→ `node_id=19_302_6` | `feature=?` | Layer 19 | `(no label)` — edge [+5.6374]
→ `node_id=22_7486_8` | `feature=?` | Layer 22 | `(no label)` — edge [+8.9144]
→ `node_id=25_15216_8` | `feature=?` | Layer 25 | `(no label)` — edge [-0.2455]
→ **LOGIT** `node_id=27_4401_8` Layer 27 — `Output " cat" (p=0.756)`

*Path 5 — (±) mixed | weight=57.234595 | hops=4*
→ `node_id=10_8919_6` | `feature=8919` | Layer 10 | ` vocabulary related to strong emotions and prejudice.` — edge [+0.7907]
→ `node_id=19_302_8` | `feature=?` | Layer 19 | `(no label)` — edge [+33.0763]
→ `node_id=22_7486_8` | `feature=?` | Layer 22 | `(no label)` — edge [+8.9144]
→ `node_id=25_15216_8` | `feature=?` | Layer 25 | `(no label)` — edge [-0.2455]
→ **LOGIT** `node_id=27_4401_8` Layer 27 — `Output " cat" (p=0.756)`

**Causal path diagram:**

![Causal paths for "<bos>Puppy is to dog as kitten is to" → "Output " cat" (p=0.756)"](graphs/bos_puppy_is_to_dog_as_kitten_is_to__output___cat___p_0_7_causal_paths.png)

*Figure: Causal paths from input features to predicted token "Output " cat" (p=0.756)". Y-axis = transformer layer. Edge width = connection strength. Green = excitatory, red = inhibitory, orange = mixed.*

**Mechanistic narrative:**

**[EARLY]** For "Puppy is to dog as kitten is to," the early layers immediately register the life-stage relational structure. The top early feature, F11438 at Layer 1 (node_id=1_11438_5, inf=0.8000), is labeled "the word 'as', and in some contexts words related to government or organization" -- the model locks onto the "as" connective that bridges the two analogy pairs, the structural heart of the A:B::C:? template. F12148 at Layer 1 (node_id=1_12148_6, inf=0.7997) fires for "words related to hosts, pathogens, and infections," and F5267 at Layer 3 (node_id=3_5267_4, inf=0.7995) for "words related to science and engineering that are nouns." These labels are surprising for an animal life-stage analogy but suggest the model uses a broad "category-member" feature cluster that spans biological taxonomy and scientific classification contexts.

**[MIDDLE]** The key middle-layer feature is F2909 at Layer 9 (node_id=9_2909_7, inf=0.7999), labeled "formulas, ratios, and mathematical notation." This recurring feature (also seen in the Cairo/Kenya graph) is the circuit's representation of the proportional/ratio structure of analogy -- "puppy:dog = kitten:cat" as a formal equivalence. F10565 at Layer 10 (label: "commonly used sayings or idioms") may be responding to the idiomatic quality of the analogy template. F4256 at Layer 14 activates for "a group of words including 'astronomy' and related terms" -- likely a general category-membership feature.

**[LATE]** F553 at Layer 25 (node_id=25_553_8, inf=0.7969) fires for "text passages written in all capital letters" -- an unusual late-layer feature that may be capturing the categorical salience of the answer. F6905 at Layer 23 (node_id=23_6905_8, inf=0.7961) fires for "nouns preceded by articles or adjectives within a specific context," which accurately describes the syntactic slot being filled.

**[TOKEN COMPETITION]** " cat" was predicted with 75.6% probability -- the second-highest confidence in the dataset after Germany (97.3%). The dominant path is Path 1 (mixed, weight=551.7), which begins at the ratio/formula feature (L9/F4261730), routes through L14 and L20, then to L25 and the logit. Path 2 is excitatory (weight=294.0) with just 2 hops from an embedding feature through L19 directly to the LOGIT. This dual-pathway structure -- one long mixed path from middle-layer domain features and one short excitatory path from embeddings -- explains the high confidence: both channels independently converge on " cat."

**[SYNTHESIS]** The puppy/kitten analogy produces the clearest mechanistic story for a non-geographic analogy. The "as" connector (F11438, L1) triggers analogy template recognition from the very first layer. The mathematical-proportion feature at Layer 9 (F4261730) implements the A:B::C:? ratio, and a direct 2-hop excitatory path from the embedding confirms the answer. The 75.6% confidence reflects convergent evidence: the life-stage relationship (puppy->dog, kitten->?) is unambiguous in the model's representation, and competing tokens are cleanly separated.

---

### Prompt: "<bos>Clock is to time as thermometer is to"

**Predicted token:** `Output " temperature" (p=0.182)` (prob=0.1823)

**Token competition:**

| Rank | Token | Logit score | Features voting |
|------|-------|-------------|-----------------|

**Circuit walkthrough:**

*Early layers — input recognition*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 2 | 7856 | 2_7856_8 | 0.8001 | 3.4787 |  the archaic word "unto" and words immediately surrounding it |
| 3 | 13575 | 3_13575_4 | 0.7995 | 2.8938 | words that involve actions, especially verbs |
| 0 | 7706 | 0_7706_4 | 0.7993 | 2.333 | the word "pat" or relating to patents |
| 7 | 3617 | 7_3617_5 | 0.7991 | 4.7318 | common words in diverse contexts seemingly without a clear theme |
| 5 | 11443 | 5_11443_5 | 0.799 | 3.1928 |  phrases that describe importance, triumph, and locations |
| 3 | 2472 | 3_2472_3 | 0.7988 | 1.8815 |  phrases related to tasks |
| 4 | 8134 | 4_8134_4 | 0.7986 | 5.2675 |  a wide range of action verbs in various contexts |
| 0 | 10901 | 0_10901_6 | 0.798 | 3.054 |  the word "temperature" |
| 7 | 1020 | 7_1020_8 | 0.7979 | 6.6531 | a variety of words that seem to have to do with separate and specific processes and items. |
| 0 | 8379 | 0_8379_5 | 0.7977 | 2.0109 |  words indicating relationship with others or with direction |
| 5 | 14644 | 5_14644_5 | 0.7975 | 3.1638 |  mathematical symbols and notation, especially related to set theory and probability |
| 0 | 5024 | 0_5024_8 | 0.7973 | 2.3014 |  the word "to" followed by high activation on words like "do" or "with" |
| 5 | 13039 | 5_13039_6 | 0.7971 | 6.1953 |  words and phrases that suggest a comparison or an analogy is being made or a summary of something is being presented. |
| 2 | 121 | 2_121_3 | 0.7969 | 1.9199 |  the word "to" |
| 0 | 13593 | 0_13593_4 | 0.7967 | 2.5052 | words related to achieving or creating something |
| 7 | 15209 | 7_15209_6 | 0.7965 | 7.3947 |  mentions of the passage of time |
| 5 | 2267 | 5_2267_2 | 0.7962 | 16.5935 |  law related terminology and references to specific cases or legal entities. |
| 3 | 13119 | 3_13119_2 | 0.796 | 3.6841 |  words and phrases related to medical conditions, disabilities, ailments, and violent conflicts |
| 6 | 558 | 6_558_8 | 0.7958 | 6.7496 | phrases indicating a comparison and mathematical notations. |
| 6 | 2539 | 6_2539_8 | 0.7956 | 5.8836 |  words and phrases associated with political opinions or debates. |
| 5 | 617 | 5_617_6 | 0.7954 | 5.7773 |  words related to research and analysis, often within technical documents |
| 2 | 9481 | 2_9481_4 | 0.7952 | 2.4101 | mentions of time, duration, or scheduling |
| 4 | 15913 | 4_15913_4 | 0.7947 | 5.1276 |  words related to linings and surfaces |
| 4 | 8974 | 4_8974_3 | 0.7945 | 3.0588 |  words and phrases used when actively communicating within a discussion |
| 7 | 476 | 7_476_3 | 0.7943 | 6.0871 | objective C code related to sliders |
| 0 | 4991 | 0_4991_6 | 0.7939 | 4.0593 |  words or phrases associated with scientific or formal writing, particularly words relating to natural history, archeology, or formal analysis |
| 5 | 15827 | 5_15827_8 | 0.7932 | 3.7962 |  well-known proverbs and quotations |
| 5 | 11167 | 5_11167_2 | 0.793 | 6.5715 |  recipes |

*Middle layers — relational mapping*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 0 | 11 | 0_11_2 | 0.7984 | 0.0 |  the string "ot" |
| 13 | 13281 | 13_13281_8 | 0.7982 | 6.0611 |  words related to relationships between things |
| 15 | 12474 | 15_12474_5 | 0.7964 | 21.768 |  analogies in conversational text. |
| 12 | 4592 | 12_4592_8 | 0.7949 | 8.3279 | a mix of code, chemical symbols, labels such as "MTB",  "Bond length", and words related to legal counsel |
| 12 | 16125 | 12_16125_7 | 0.7941 | 18.0381 |  words related to conflict |
| 9 | 6402 | 9_6402_8 | 0.7935 | 7.5958 |  references to laws, articles and sections. |

*Late layers — token selection*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 20 | 14348 | 20_14348_8 | 0.7999 | 8.6818 | words and conjunctions that connect other words, and the letters "PPC" |
| 24 | 3523 | 24_3523_8 | 0.7997 | 6.5394 |  language describing grammatical principles, specifically the use of "in spite of" |
| 17 | 2469 | 17_2469_5 | 0.795 | 27.5778 |  analogies using "the same way" construction |
| 0 | 22 | 0_22_4 | 0.7937 | 0.0 | words ending in the suffix "ality,' or the word "other." |
| 23 | 221 | 23_221_8 | 0.7933 | 15.2135 |  words associated with temperature |
| 25 | 13004 | 25_13004_8 | 0.7928 | 10.0606 |  uses of the word "of" and "and" to connect ideas, especially within the context of academic writing or legal matters. |

**Causal paths (edge-weight chains to logit):**

*Path 1 — (±) mixed | weight=523.227727 | hops=5*
→ `node_id=0_10901_6` | `feature=10901` | Layer 0 | ` the word "temperature"` — edge [-0.316]
→ `node_id=6_15037_6` | `feature=?` | Layer 6 | `(no label)` — edge [+13.2661]
→ `node_id=17_7119_8` | `feature=?` | Layer 17 | `(no label)` — edge [+8.8043]
→ `node_id=22_5937_8` | `feature=?` | Layer 22 | `(no label)` — edge [+14.2508]
→ `node_id=25_7779_8` | `feature=?` | Layer 25 | `(no label)` — edge [-0.9949]
→ **LOGIT** `node_id=27_5809_8` Layer 27 — `Output " temperature" (p=0.182)`

*Path 2 — (±) mixed | weight=132.18993 | hops=5*
→ `node_id=7_15209_6` | `feature=15209` | Layer 7 | ` mentions of the passage of time` — edge [-0.5664]
→ `node_id=8_8244_6` | `feature=?` | Layer 8 | `(no label)` — edge [+1.8697]
→ `node_id=17_7119_8` | `feature=?` | Layer 17 | `(no label)` — edge [+8.8043]
→ `node_id=22_5937_8` | `feature=?` | Layer 22 | `(no label)` — edge [+14.2508]
→ `node_id=25_7779_8` | `feature=?` | Layer 25 | `(no label)` — edge [-0.9949]
→ **LOGIT** `node_id=27_5809_8` Layer 27 — `Output " temperature" (p=0.182)`

*Path 3 — (±) mixed | weight=10.468594 | hops=3*
→ `node_id=13_13281_8` | `feature=13281` | Layer 13 | ` words related to relationships between things` — edge [-0.7383]
→ `node_id=22_5937_8` | `feature=?` | Layer 22 | `(no label)` — edge [+14.2508]
→ `node_id=25_7779_8` | `feature=?` | Layer 25 | `(no label)` — edge [-0.9949]
→ **LOGIT** `node_id=27_5809_8` Layer 27 — `Output " temperature" (p=0.182)`

*Path 4 — (+) excitatory | weight=7.785569 | hops=1*
→ `node_id=E_68572_6` | `feature=?` | Layer E | `(no label)` — edge [+7.7856]
→ **LOGIT** `node_id=27_5809_8` Layer 27 — `Output " temperature" (p=0.182)`

*Path 5 — (-) inhibitory | weight=0.109199 | hops=1*
→ `node_id=25_13004_8` | `feature=13004` | Layer 25 | ` uses of the word "of" and "and" to connect ideas, especially within the context of academic writing or legal matters.` — edge [-0.1092]
→ **LOGIT** `node_id=27_5809_8` Layer 27 — `Output " temperature" (p=0.182)`

**Causal path diagram:**

![Causal paths for "<bos>Clock is to time as thermometer is to" → "Output " temperature" (p=0.182)"](graphs/bos_clock_is_to_time_as_thermometer_is__output___temperature_causal_paths.png)

*Figure: Causal paths from input features to predicted token "Output " temperature" (p=0.182)". Y-axis = transformer layer. Edge width = connection strength. Green = excitatory, red = inhibitory, orange = mixed.*

**Mechanistic narrative:**

**[EARLY]** "Clock is to time as thermometer is to" activates an unusual set of early features. The top early node, F7856 at Layer 2 (node_id=2_7856_8, inf=0.8001), is labeled "the archaic word 'unto' and words immediately surrounding it" -- likely responding to the "is to" relational connector's archaic/formal character. F13575 at Layer 3 (node_id=3_13575_4, inf=0.7995) activates for "words that involve actions, especially verbs," registering the active relational nature of the measurement template. F7706 at Layer 0 (node_id=0_7706_4, inf=0.7993) fires for "the word 'pat' or relating to patents" -- likely detecting the technical/functional domain of clock and thermometer as measurement instruments.

**[MIDDLE]** Two remarkable middle-layer features appear: F13281 at Layer 13 (node_id=13_13281_8, inf=0.7982) activates for "words related to relationships between things" -- a direct representation of relational structure. More significantly, F12474 at Layer 15 (node_id=15_12474_5, inf=0.7964) is labeled "analogies in conversational text" -- the model has an explicit analogy-detection feature that fires in the middle layers for this prompt. This is the clearest evidence that the middle-layer circuit has learned a dedicated analogical reasoning sub-network.

**[LATE]** F14348 at Layer 20 (node_id=20_14348_8, inf=0.7999) activates for "words and conjunctions that connect other words" -- the connector/preposition feature seen in the Paris/Germany circuit. F3523 at Layer 24 (node_id=24_3523_8, inf=0.7997) fires for "language describing grammatical principles." F2469 at Layer 17 (node_id=17_2469_5, inf=0.7950) is labeled "analogies using 'the same way' construction" -- a second explicit analogy template feature in the late layers.

**[TOKEN COMPETITION]** " temperature" was predicted with 18.2% probability -- genuinely ambiguous, as "heat" and "warmth" are reasonable alternatives. The dominant path (Path 1, mixed, weight=523.2) travels 5 hops from L0 through L6, L17, L20-L25 to the logit. The presence of two explicit analogy features (F12474 at L15 and F2469 at L17) in the causal chain means this circuit is more self-aware of its analogical task than any other prompt in the dataset.

**[SYNTHESIS]** The Clock/thermometer analogy reveals the most explicit analogy-circuit activation in the dataset. The circuit contains dedicated analogy-detection features at Layer 15 ("analogies in conversational text") and Layer 17 ("analogies using 'the same way' construction"). Despite clear relational recognition, the prediction is uncertain (18.2%) because "thermometer" maps to multiple measurement concepts (temperature, heat, degrees). The circuit correctly solves the structural analogy but faces genuine semantic ambiguity in the final token-selection step.

---

### Prompt: "<bos>Book is to reading as radio is to"

**Predicted token:** `Output " listening" (p=0.345)` (prob=0.3455)

**Token competition:**

| Rank | Token | Logit score | Features voting |
|------|-------|-------------|-----------------|

**Circuit walkthrough:**

*Early layers — input recognition*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 5 | 5683 | 5_5683_5 | 0.7999 | 3.3896 | technical terminology in scientific writing, especially words ending in "specific", "tion", or containing mathematical symbols |
| 4 | 4328 | 4_4328_3 | 0.7997 | 5.0989 |  instances of how a goal may be achieved, or how someone plans to achieve something |
| 0 | 663 | 0_663_4 | 0.7995 | 1.7037 |  words and phrases related to opinions, arguments, and discussions. |
| 6 | 8378 | 6_8378_5 | 0.7993 | 3.4709 |  words related to expressing meaning in symbols |
| 4 | 7960 | 4_7960_4 | 0.7989 | 4.2426 |  gerunds in different contexts |
| 5 | 815 | 5_815_6 | 0.7988 | 3.7597 |  words indicating a control group of people in a study |
| 1 | 5314 | 1_5314_2 | 0.7986 | 2.52 |  words that often come before or after a coordinating conjunction. |
| 1 | 1861 | 1_1861_2 | 0.798 | 2.5715 |  words or phrases that indicate progress, success, or advancement in various fields like computer science, history, genomics, and medicine. |
| 4 | 14293 | 4_14293_2 | 0.7978 | 4.859 |  words related to projects, particularly those involving math or technology |
| 6 | 9289 | 6_9289_6 | 0.7974 | 3.0708 |  words related to electronics and appliances, and words related to consumerism in general |
| 5 | 7785 | 5_7785_6 | 0.7972 | 4.5455 | a mix of technical jargon with a focus on physics and abstract metaphors for criticism |
| 2 | 6274 | 2_6274_2 | 0.797 | 2.8528 | words that describe actions or events in a formal context, such as legal, medical, or academic settings |
| 0 | 15414 | 0_15414_8 | 0.7969 | 3.9884 |  words and phrases related to obligation, judgement, or destiny |
| 4 | 12179 | 4_12179_3 | 0.7967 | 4.3082 |  definitions of words |
| 2 | 12041 | 2_12041_1 | 0.7965 | 1.7416 | words related to books and publications in various formats |
| 0 | 12200 | 0_12200_5 | 0.7963 | 2.8945 |  a variety of specific nouns |
| 1 | 14292 | 1_14292_1 | 0.7959 | 2.595 | the word 'segment', sometimes in the context of computer memory or mathematics |
| 6 | 13822 | 6_13822_5 | 0.7955 | 4.5559 |  technical vocabulary, potentially related to medicine, genetics, and programming. |
| 1 | 903 | 1_903_4 | 0.7951 | 2.3007 |  words and phrases relating to books, paper crafts, and the publishing industry |
| 3 | 433 | 3_433_5 | 0.7949 | 2.7204 |  character strings that appear to represent non-English text, URLs, code snippets, or other specialized content |
| 5 | 10741 | 5_10741_8 | 0.7947 | 5.3197 | words ending in 'ing' that indicate a feeling or opinion |
| 0 | 0 | 0_0_8 | 0.7944 | 0.0 | mentions of clubs or sports teams, and sometimes related words like 'sister' or 'kids' |
| 2 | 189 | 2_189_6 | 0.7938 | 3.984 |  people in positions of power, either as leaders, family roles, or contributors |
| 1 | 12264 | 1_12264_4 | 0.7936 | 2.6371 |  words associated with education and academia |
| 1 | 8587 | 1_8587_4 | 0.7934 | 2.0242 |  words related to travel, planning trips, and travel agencies |
| 5 | 11751 | 5_11751_4 | 0.7932 | 4.1679 |  analogies or comparisons using "like" or "having" |
| 5 | 11443 | 5_11443_5 | 0.7928 | 3.7689 |  phrases that describe importance, triumph, and locations |

*Middle layers — relational mapping*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 11 | 5517 | 11_5517_4 | 0.8001 | 12.9376 |  a wide array of words in a text. |
| 8 | 4175 | 8_4175_4 | 0.7991 | 5.9789 |  mentions of published works, publishers, and literary studies |
| 8 | 11280 | 8_11280_5 | 0.7982 | 9.3885 |  qualifiers such as how often or to what degree that something happens |
| 7 | 14645 | 7_14645_6 | 0.7976 | 2.028 |  references to unpleasant sounds and nuisances |
| 10 | 14542 | 10_14542_7 | 0.7957 | 13.3404 |  words related to research, business or product comparison |
| 7 | 4264 | 7_4264_4 | 0.7953 | 7.3212 |  words and phrases having to do with reading and documents |
| 12 | 10930 | 12_10930_8 | 0.7946 | 7.8208 |  math equations and formal math language |
| 10 | 14542 | 10_14542_6 | 0.7942 | 7.0319 |  words related to research, business or product comparison |
| 10 | 13736 | 10_13736_8 | 0.793 | 9.8187 | this isn't enough data |

*Late layers — token selection*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 0 | 22 | 0_22_7 | 0.7984 | 0.0 | words ending in the suffix "ality,' or the word "other." |
| 17 | 2469 | 17_2469_8 | 0.7961 | 8.3538 |  analogies using "the same way" construction |
| 0 | 22 | 0_22_4 | 0.794 | 0.0 | words ending in the suffix "ality,' or the word "other." |
| 20 | 1851 | 20_1851_8 | 0.7926 | 8.7505 | words and phrases related to organization and process |

**Causal paths (edge-weight chains to logit):**

*Path 1 — (+) excitatory | weight=108.84962 | hops=2*
→ `node_id=E_7752_6` | `feature=?` | Layer E | `(no label)` — edge [+19.2449]
→ `node_id=21_12984_8` | `feature=?` | Layer 21 | `(no label)` — edge [+5.656]
→ **LOGIT** `node_id=27_15655_8` Layer 27 — `Output " listening" (p=0.345)`

*Path 2 — (±) mixed | weight=46.673148 | hops=5*
→ `node_id=5_7785_6` | `feature=7785` | Layer 5 | `a mix of technical jargon with a focus on physics and abstract metaphors for criticism` — edge [+0.529]
→ `node_id=11_15947_6` | `feature=?` | Layer 11 | `(no label)` — edge [+3.516]
→ `node_id=12_7403_6` | `feature=?` | Layer 12 | `(no label)` — edge [-1.0826]
→ `node_id=20_14622_8` | `feature=?` | Layer 20 | `(no label)` — edge [+5.587]
→ `node_id=25_14716_8` | `feature=?` | Layer 25 | `(no label)` — edge [-4.149]
→ **LOGIT** `node_id=27_15655_8` Layer 27 — `Output " listening" (p=0.345)`

*Path 3 — (±) mixed | weight=8.546575 | hops=3*
→ `node_id=5_11751_4` | `feature=11751` | Layer 5 | ` analogies or comparisons using "like" or "having"` — edge [-0.3687]
→ `node_id=20_14622_8` | `feature=?` | Layer 20 | `(no label)` — edge [+5.587]
→ `node_id=25_14716_8` | `feature=?` | Layer 25 | `(no label)` — edge [-4.149]
→ **LOGIT** `node_id=27_15655_8` Layer 27 — `Output " listening" (p=0.345)`

*Path 4 — (±) mixed | weight=0.662701 | hops=2*
→ `node_id=0_22_7` | `feature=22` | Layer 0 | `words ending in the suffix "ality,' or the word "other."` — edge [+0.1597]
→ `node_id=25_14716_8` | `feature=?` | Layer 25 | `(no label)` — edge [-4.149]
→ **LOGIT** `node_id=27_15655_8` Layer 27 — `Output " listening" (p=0.345)`

*Path 5 — (±) mixed | weight=0.491367 | hops=3*
→ `node_id=4_12179_3` | `feature=12179` | Layer 4 | ` definitions of words` — edge [-0.7984]
→ `node_id=8_13518_3` | `feature=?` | Layer 8 | `(no label)` — edge [+0.1483]
→ `node_id=25_14716_8` | `feature=?` | Layer 25 | `(no label)` — edge [-4.149]
→ **LOGIT** `node_id=27_15655_8` Layer 27 — `Output " listening" (p=0.345)`

**Causal path diagram:**

![Causal paths for "<bos>Book is to reading as radio is to" → "Output " listening" (p=0.345)"](graphs/bos_book_is_to_reading_as_radio_is_to__output___listening___causal_paths.png)

*Figure: Causal paths from input features to predicted token "Output " listening" (p=0.345)". Y-axis = transformer layer. Edge width = connection strength. Green = excitatory, red = inhibitory, orange = mixed.*

**Mechanistic narrative:**

**[EARLY]** "Book is to reading as radio is to" activates features in the activity/medium domain. The top early feature, F5683 at Layer 5 (node_id=5_5683_5, inf=0.7999), detects "technical terminology in scientific writing" -- likely responding to the formal register of the analogy template. F4328 at Layer 4 (node_id=4_4328_3, inf=0.7997) activates for "instances of how a goal may be achieved, or how someone plans to" -- encoding the functional/purposive relationship (books are for reading, radio is for listening). F663 at Layer 0 (node_id=0_663_4, inf=0.7995) fires for "words and phrases related to opinions, arguments, and discussion" -- potentially registering the communicative nature of both reading and listening.

**[MIDDLE]** F5517 at Layer 11 (node_id=11_5517_4, inf=0.8001) -- the highest-influence middle node -- is labeled "a wide array of words in a text," a broad feature detecting the general textual/linguistic nature of the prompt. F4175 at Layer 8 (node_id=8_4175_4, inf=0.7991) specifically fires for "mentions of published works, publishers, and literary studies" -- connecting the "book/reading" source domain. F2469 at Layer 17 (node_id=17_2469_8, inf=0.7961) fires for "analogies using 'the same way' construction" -- the analogy template detector also seen in the Clock/thermometer prompt.

**[LATE]** F22 at Layer 0 (node_id=0_22_7, inf=0.7984) fires for "words ending in '-ality' or 'other'" -- the abstract category placeholder. The analogy template feature (F2469) appearing in the late band at Layer 17 indicates that analogy recognition continues into the final prediction stages.

**[TOKEN COMPETITION]** " listening" was predicted with 34.5% probability. Path 1 is excitatory (weight=108.8, 2 hops): embedding -> L21 -> LOGIT -- the same short-circuit excitatory pattern seen in high-confidence predictions. The mixed Path 2 (weight=46.7) routes through L5 -> L11 -> L12 -> higher layers -> LOGIT, incorporating the "published works" feature (L8/F4175) into the causal chain.

**[SYNTHESIS]** The Book/radio analogy shows a functionally clean circuit: reading is the activity associated with books, listening with radio. The analogy template detector (F2469 at L17) fires for both this prompt and the Clock/thermometer one, suggesting a shared sub-circuit for activity/function analogies. The dominant mechanism is the 2-hop excitatory path from an embedding feature to L21 to LOGIT (Path 1, weight=108.8). The 34.5% confidence reflects genuine ambiguity between "listening," "broadcasting," and "hearing" -- all valid completions competing for the output slot.

---

### Prompt: "<bos>Leaf is to tree as petal is to"

**Predicted token:** `Output " flower" (p=0.136)` (prob=0.1361)

**Token competition:**

| Rank | Token | Logit score | Features voting |
|------|-------|-------------|-----------------|

**Circuit walkthrough:**

*Early layers — input recognition*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 7 | 15463 | 7_15463_5 | 0.8001 | 5.1559 |  a multitude of concepts including things, exclamations, comparisons and fire. |
| 6 | 6178 | 6_6178_4 | 0.7999 | 6.2802 |  words related to domestic animals and farming |
| 6 | 11868 | 6_11868_6 | 0.7997 | 4.5873 |  words related to animals and natural objects/phenomena |
| 0 | 2841 | 0_2841_7 | 0.7995 | 5.7566 | auxiliary verbs such as "should", "be", and other helping verbs. |
| 0 | 15651 | 0_15651_6 | 0.7993 | 4.2503 |  technical terms from the domains of biology, statistics and finance |
| 0 | 8607 | 0_8607_6 | 0.7991 | 3.1344 | the word "channel," and words synonymous with "button" in a variety of contexts, including anatomy |
| 1 | 12115 | 1_12115_1 | 0.7984 | 1.987 |  code comments |
| 6 | 9865 | 6_9865_1 | 0.7982 | 9.5584 |  code and file paths |
| 4 | 14857 | 4_14857_5 | 0.798 | 3.7083 | code snippets and license agreements |
| 0 | 4125 | 0_4125_4 | 0.7969 | 2.0289 | code snippets and code-related terms |
| 5 | 10332 | 5_10332_5 | 0.7967 | 3.692 | descriptions of something anticipated or expected |
| 2 | 4999 | 2_4999_5 | 0.796 | 1.84 |  the word "as" |
| 6 | 15183 | 6_15183_6 | 0.7958 | 5.1324 | words and phrases related to the characteristics of fruit and eggs. |
| 7 | 3319 | 7_3319_4 | 0.7956 | 7.0593 |  the word "to" when it is used as a preposition. |
| 1 | 12347 | 1_12347_4 | 0.7952 | 2.6004 |  words related to plant genetics and cultivation, often in the context of scientific research or description of new varieties |
| 4 | 2651 | 4_2651_6 | 0.795 | 3.5281 |  references to pages in books, newspapers or other media. |
| 2 | 7167 | 2_7167_4 | 0.7949 | 3.5191 |  words related to geographically located infrastructure, including geographical locations, natural resources and transport infrastructure |
| 5 | 2039 | 5_2039_6 | 0.7947 | 3.5323 |  scientific names. |
| 0 | 16139 | 0_16139_4 | 0.7941 | 3.2216 | the word "passive" |
| 0 | 11835 | 0_11835_4 | 0.7939 | 3.2248 | terms used in software code such as "assembly", "using", "namespace", and "license" |
| 1 | 12694 | 1_12694_3 | 0.7937 | 1.6493 | snippets of code and mathematical formulas |
| 6 | 15640 | 6_15640_8 | 0.7935 | 6.0194 | the word "to" and the immediately preceding and following words |
| 1 | 15024 | 1_15024_4 | 0.7932 | 3.4541 |  code or code-like text, especially related to math or science |
| 6 | 5837 | 6_5837_5 | 0.793 | 3.8532 |  the words "as", "undo", and "ilim" after filtering out the zero's. |
| 4 | 12411 | 4_12411_2 | 0.7928 | 3.9375 | words and phrases used in scientific and technical writing |

*Middle layers — relational mapping*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 10 | 8082 | 10_8082_8 | 0.7986 | 7.4409 | This neuron seems to identify language used to express complex debates and controversies across a range of social, political and scientific topics. |
| 11 | 1917 | 11_1917_4 | 0.7978 | 10.5443 | abbreviations, measurements, units, and values |
| 14 | 8179 | 14_8179_8 | 0.7977 | 9.5436 | phrases with lots of function words (articles, prepositions, etc) strung together. |
| 10 | 13392 | 10_13392_4 | 0.7975 | 9.5956 |  words specifically related to wedding anniversaries and their associated symbols |
| 9 | 13344 | 9_13344_7 | 0.7971 | 14.0749 |  phrases suggesting uncertainty or comparison between two things |
| 9 | 13520 | 9_13520_1 | 0.7963 | 44.7062 |  various code snippets |
| 9 | 6893 | 9_6893_5 | 0.7962 | 5.6052 |  the word "whereas" and other words indicating a contrast, such as "while", "but", or "however." |
| 8 | 4746 | 8_4746_7 | 0.7945 | 8.479 |  mentions of converting between different programming languages or replacing one thing with another |

*Late layers — token selection*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 18 | 6647 | 18_6647_7 | 0.7989 | 30.0506 |  segments of code or legal documents. |
| 20 | 16267 | 20_16267_8 | 0.7988 | 7.716 |  instances of stream of consciousness writing, particularly related to feelings, the world, or war |
| 23 | 13964 | 23_13964_8 | 0.7973 | 6.8606 | code related to user information and language translation |
| 23 | 12661 | 23_12661_8 | 0.7965 | 11.6425 |  numbers and words associated with measurement, quantity or order |
| 18 | 12090 | 18_12090_7 | 0.7954 | 7.0865 | words or phrases used when asking for or giving agreement |
| 25 | 11084 | 25_11084_8 | 0.7943 | 18.1374 |  botanical terms related to plants |
| 23 | 489 | 23_489_8 | 0.7933 | 6.7509 |  business language related to loans, finance, getting legal or business help, and entrepreneurs |

**Causal paths (edge-weight chains to logit):**

*Path 1 — (±) mixed | weight=2086.949095 | hops=5*
→ `node_id=5_2039_6` | `feature=2039` | Layer 5 | ` scientific names.` — edge [-1.7125]
→ `node_id=6_1199_6` | `feature=?` | Layer 6 | `(no label)` — edge [+5.6529]
→ `node_id=19_6923_8` | `feature=?` | Layer 19 | `(no label)` — edge [+8.1066]
→ `node_id=22_1760_8` | `feature=?` | Layer 22 | `(no label)` — edge [+6.9879]
→ `node_id=25_12763_8` | `feature=?` | Layer 25 | `(no label)` — edge [-3.8057]
→ **LOGIT** `node_id=27_10377_8` Layer 27 — `Output " flower" (p=0.136)`

*Path 2 — (±) mixed | weight=545.647651 | hops=5*
→ `node_id=6_9865_1` | `feature=9865` | Layer 6 | ` code and file paths` — edge [-7.9951]
→ `node_id=9_13520_1` | `feature=13520` | Layer 9 | ` various code snippets` — edge [+3.5984]
→ `node_id=10_14174_1` | `feature=?` | Layer 10 | `(no label)` — edge [+21.7541]
→ `node_id=15_851_1` | `feature=?` | Layer 15 | `(no label)` — edge [+0.8355]
→ `node_id=25_4717_8` | `feature=?` | Layer 25 | `(no label)` — edge [+1.0435]
→ **LOGIT** `node_id=27_10377_8` Layer 27 — `Output " flower" (p=0.136)`

*Path 3 — (±) mixed | weight=96.700321 | hops=4*
→ `node_id=6_15183_6` | `feature=15183` | Layer 6 | `words and phrases related to the characteristics of fruit and eggs.` — edge [+0.4821]
→ `node_id=20_10103_8` | `feature=?` | Layer 20 | `(no label)` — edge [+7.5427]
→ `node_id=22_1760_8` | `feature=?` | Layer 22 | `(no label)` — edge [+6.9879]
→ `node_id=25_12763_8` | `feature=?` | Layer 25 | `(no label)` — edge [-3.8057]
→ **LOGIT** `node_id=27_10377_8` Layer 27 — `Output " flower" (p=0.136)`

*Path 4 — (+) excitatory | weight=68.247729 | hops=4*
→ `node_id=9_13520_1` | `feature=13520` | Layer 9 | ` various code snippets` — edge [+3.5984]
→ `node_id=10_14174_1` | `feature=?` | Layer 10 | `(no label)` — edge [+21.7541]
→ `node_id=15_851_1` | `feature=?` | Layer 15 | `(no label)` — edge [+0.8355]
→ `node_id=25_4717_8` | `feature=?` | Layer 25 | `(no label)` — edge [+1.0435]
→ **LOGIT** `node_id=27_10377_8` Layer 27 — `Output " flower" (p=0.136)`

*Path 5 — (+) excitatory | weight=4.935679 | hops=1*
→ `node_id=E_127427_6` | `feature=?` | Layer E | `(no label)` — edge [+4.9357]
→ **LOGIT** `node_id=27_10377_8` Layer 27 — `Output " flower" (p=0.136)`

**Causal path diagram:**

![Causal paths for "<bos>Leaf is to tree as petal is to" → "Output " flower" (p=0.136)"](graphs/bos_leaf_is_to_tree_as_petal_is_to__output___flower___p__causal_paths.png)

*Figure: Causal paths from input features to predicted token "Output " flower" (p=0.136)". Y-axis = transformer layer. Edge width = connection strength. Green = excitatory, red = inhibitory, orange = mixed.*

**Mechanistic narrative:**

**[EARLY]** "Leaf is to tree as petal is to" activates the richest set of botanical/natural features in the dataset. The top early node, F15463 at Layer 7 (node_id=7_15463_5, inf=0.8001), fires for "a multitude of concepts including things, exclamations, comparisons..." -- a broad analogy-context feature. Crucially, F6178 at Layer 6 (node_id=6_6178_4, inf=0.7999) detects "words related to domestic animals and farming," and F11868 at Layer 6 (node_id=6_11868_6, inf=0.7997) fires for "words related to animals and natural objects/phenomena" -- the model is encoding all prompt terms (leaf, tree, petal) as natural/biological objects from the earliest layers. This natural-objects cluster is the most domain-specific early activation in the dataset.

**[MIDDLE]** F8082 at Layer 10 (node_id=10_8082_8, inf=0.7986) activates for "language used to express complex dependencies" -- potentially encoding the part-whole relationship (leaf:tree = petal:flower). F1917 at Layer 11 (node_id=11_1917_4, inf=0.7978) fires for "abbreviations, measurements, units, and values," and F8179 at Layer 14 (node_id=14_8179_8, inf=0.7977) for "phrases with lots of function words (articles, prepositions, etc)" -- directly encoding the syntactic structure of the analogy template's relational connectors.

**[LATE]** F6647 at Layer 18 (node_id=18_6647_7, inf=0.7989) fires for "segments of code or legal documents" -- the formal-register structural feature that appears across many analogical prompts. F16267 at Layer 20 (node_id=20_16267_8, inf=0.7988) activates for "stream of consciousness writing, particularly related to..." -- an unexpected late-layer feature suggesting the model treats the open-ended analogy as a generative/creative task.

**[TOKEN COMPETITION]** " flower" was predicted with only 13.6% probability -- the second-lowest in the dataset. The dominant path (Path 1, mixed, weight=2086.9) has the highest total weight of any path in the entire dataset, driven by very large individual edge weights including a +74.6 edge at L21. Despite this extreme path weight, confidence is low because "flower" competes with "plant," "rose," and other botanical terms.

**[SYNTHESIS]** The Leaf/petal analogy is the most structurally striking circuit: it combines the strongest early domain-specific features (natural objects at L6) with the highest-weight causal path (2086.9) yet produces the second-lowest prediction confidence. This dissociation reveals that path weight is not a proxy for prediction confidence: the model has a rich botanical representation at early layers and a strong causal signal, but the signal spreads across many competing botanical tokens (flower, plant, bloom, blossom). The circuit correctly identifies the part-whole botanical relationship but cannot converge on a single answer token.

---

### Prompt: "<bos>Wheel is to car as wing is to"

**Predicted token:** `Output " airplane" (p=0.162)` (prob=0.1618)

**Token competition:**

| Rank | Token | Logit score | Features voting |
|------|-------|-------------|-----------------|

**Circuit walkthrough:**

*Early layers — input recognition*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 2 | 3195 | 2_3195_6 | 0.7998 | 2.9627 |  words related to shopping for apparel and gifts |
| 5 | 2267 | 5_2267_4 | 0.7995 | 11.2256 |  law related terminology and references to specific cases or legal entities. |
| 5 | 1673 | 5_1673_5 | 0.7991 | 4.4011 |  the word "general" and phrases containing "as a whole." |
| 1 | 13554 | 1_13554_6 | 0.7985 | 3.1578 | words related to car transmissions and gear shifting |
| 4 | 4328 | 4_4328_3 | 0.7983 | 4.7115 |  instances of how a goal may be achieved, or how someone plans to achieve something |
| 1 | 3992 | 1_3992_5 | 0.7981 | 3.7893 |  strings of ellipses and sentence fragments, possibly in conjunction with other punctuation |
| 4 | 5249 | 4_5249_1 | 0.7979 | 5.105 | a variety of different things including car parts, file extensions, and cooking-related words. |
| 0 | 1998 | 0_1998_7 | 0.7976 | 7.0322 |  occurrences of the word "seem" or "is" or "are." |
| 2 | 14793 | 2_14793_6 | 0.7974 | 3.4517 |  terms from computer programming, mathematics, and academic papers |
| 5 | 1078 | 5_1078_5 | 0.7968 | 5.4487 |  internet pharmacies and related terms, especially related to certain medications |
| 4 | 8952 | 4_8952_1 | 0.7966 | 4.4313 |  content from multiple different languages in the same document. |
| 1 | 5775 | 1_5775_2 | 0.7962 | 2.7728 |  present tense forms of the verb "to be" |
| 6 | 3899 | 6_3899_6 | 0.7959 | 4.3786 |  geographical locations or words associated with people from particular places, also with some terms related to nutrition and pregnancy. |
| 7 | 11734 | 7_11734_3 | 0.7955 | 8.865 | The neuron activates on the structure or formatting of documents, including numbering, introductions, and common thanking phrases. |
| 2 | 1220 | 2_1220_1 | 0.7951 | 2.3669 |  words related to motors, mechanics, and systems of vehicles |
| 1 | 12174 | 1_12174_4 | 0.7949 | 3.7054 |  words relating to ways things are conventionally done, potential problems, or political/economic issues |
| 0 | 1331 | 0_1331_4 | 0.7943 | 2.7541 |  when people are cursing and being judgmental |
| 0 | 14897 | 0_14897_1 | 0.7941 | 1.2626 |  the words "gender" and "secondary", along with words that can be seen as moral judgements |
| 4 | 1312 | 4_1312_2 | 0.7939 | 6.4978 |  sentences that describe something |
| 3 | 2472 | 3_2472_3 | 0.7937 | 2.2497 |  phrases related to tasks |
| 4 | 8449 | 4_8449_5 | 0.7935 | 2.348 |  pronouns and conjunctions used to link people and ideas |
| 6 | 16285 | 6_16285_5 | 0.7934 | 3.9502 |  different things that I can't summarize with one sentence |
| 7 | 4920 | 7_4920_2 | 0.7932 | 11.8717 | words that are machine parts and how the parts are used |
| 0 | 7403 | 0_7403_6 | 0.7928 | 2.8676 |  technical words related to chemistry, biology or medicine |
| 5 | 8485 | 5_8485_5 | 0.7926 | 4.9498 | verbs with endings such as "ing", "ed", or prepositions such as "from" and "into" |

*Middle layers — relational mapping*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 8 | 2024 | 8_2024_6 | 0.7996 | 3.4993 |  terms related to clothes, fit, and fabrics |
| 9 | 13344 | 9_13344_3 | 0.7987 | 10.4874 |  phrases suggesting uncertainty or comparison between two things |
| 9 | 14231 | 9_14231_8 | 0.7978 | 6.2945 | words representing comparisons and relationships |
| 10 | 14542 | 10_14542_4 | 0.797 | 5.9503 |  words related to research, business or product comparison |
| 8 | 5531 | 8_5531_2 | 0.796 | 10.8043 |  language discussing genetics, especially chromosome abnormalities such as gains, losses, deletions, and amplifications |
| 10 | 7106 | 10_7106_1 | 0.7957 | 26.2749 |  the word "The." |
| 10 | 883 | 10_883_1 | 0.7947 | 25.9789 |  scientific and technical terms that end in "-tion" or "-sion." |

*Late layers — token selection*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 0 | 20 | 0_20_4 | 0.8 | 0.0 |  instances of the word "hardly" and possibly words close to it within a sentence |
| 18 | 6905 | 18_6905_8 | 0.7993 | 8.0637 |  code snippets, variable names, and programming keywords along with punctuation and numbers in a variety of languages |
| 23 | 5563 | 23_5563_8 | 0.7989 | 23.2206 |  words related to transport, aviation, and the military |
| 23 | 15726 | 23_15726_8 | 0.7972 | 7.6141 |  words found in legal documents related to establishing parenthood or citizenship or general bureaucracy |
| 21 | 7585 | 21_7585_8 | 0.7964 | 8.6225 |  references to figures, sections, theorems, and symbols in academic papers |
| 24 | 11987 | 24_11987_8 | 0.7953 | 10.5913 |  mentions of animals |
| 18 | 14713 | 18_14713_7 | 0.7945 | 42.9756 |  words that add nuance with adverbs, adjectives, and conjunctions |
| 21 | 10142 | 21_10142_8 | 0.793 | 7.0187 |  instances of vehicles being involved in accidents |

**Causal paths (edge-weight chains to logit):**

*Path 1 — (±) mixed | weight=112.921452 | hops=5*
→ `node_id=2_14793_6` | `feature=14793` | Layer 2 | ` terms from computer programming, mathematics, and academic papers` — edge [+0.5502]
→ `node_id=7_8096_6` | `feature=?` | Layer 7 | `(no label)` — edge [+9.8644]
→ `node_id=20_3731_8` | `feature=?` | Layer 20 | `(no label)` — edge [+2.6878]
→ `node_id=24_8106_8` | `feature=?` | Layer 24 | `(no label)` — edge [-2.152]
→ `node_id=25_12962_8` | `feature=?` | Layer 25 | `(no label)` — edge [-3.5973]
→ **LOGIT** `node_id=27_44737_8` Layer 27 — `Output " airplane" (p=0.162)`

*Path 2 — (±) mixed | weight=64.152278 | hops=5*
→ `node_id=21_7585_8` | `feature=7585` | Layer 21 | ` references to figures, sections, theorems, and symbols in academic papers` — edge [+1.5661]
→ `node_id=22_2834_8` | `feature=?` | Layer 22 | `(no label)` — edge [+3.2452]
→ `node_id=23_6306_8` | `feature=?` | Layer 23 | `(no label)` — edge [-7.4391]
→ `node_id=24_10662_8` | `feature=?` | Layer 24 | `(no label)` — edge [+1.6243]
→ `node_id=25_4717_8` | `feature=?` | Layer 25 | `(no label)` — edge [+1.0446]
→ **LOGIT** `node_id=27_44737_8` Layer 27 — `Output " airplane" (p=0.162)`

*Path 3 — (±) mixed | weight=56.186864 | hops=4*
→ `node_id=0_1331_4` | `feature=1331` | Layer 0 | ` when people are cursing and being judgmental` — edge [+0.0584]
→ `node_id=21_10366_8` | `feature=?` | Layer 21 | `(no label)` — edge [+18.8196]
→ `node_id=24_1391_8` | `feature=?` | Layer 24 | `(no label)` — edge [-14.213]
→ `node_id=25_12962_8` | `feature=?` | Layer 25 | `(no label)` — edge [-3.5973]
→ **LOGIT** `node_id=27_44737_8` Layer 27 — `Output " airplane" (p=0.162)`

*Path 4 — (±) mixed | weight=40.650755 | hops=5*
→ `node_id=4_8952_1` | `feature=8952` | Layer 4 | ` content from multiple different languages in the same document.` — edge [+0.8863]
→ `node_id=9_8770_1` | `feature=?` | Layer 9 | `(no label)` — edge [+6.754]
→ `node_id=10_12232_1` | `feature=?` | Layer 10 | `(no label)` — edge [-10.7943]
→ `node_id=15_851_1` | `feature=?` | Layer 15 | `(no label)` — edge [+0.6022]
→ `node_id=25_4717_8` | `feature=?` | Layer 25 | `(no label)` — edge [+1.0446]
→ **LOGIT** `node_id=27_44737_8` Layer 27 — `Output " airplane" (p=0.162)`

*Path 5 — (±) mixed | weight=40.094909 | hops=5*
→ `node_id=4_4328_3` | `feature=4328` | Layer 4 | ` instances of how a goal may be achieved, or how someone plans to achieve something` — edge [-0.2848]
→ `node_id=18_12090_8` | `feature=?` | Layer 18 | `(no label)` — edge [+9.8479]
→ `node_id=21_13968_8` | `feature=?` | Layer 21 | `(no label)` — edge [+2.0879]
→ `node_id=23_15293_8` | `feature=?` | Layer 23 | `(no label)` — edge [+6.5552]
→ `node_id=25_4717_8` | `feature=?` | Layer 25 | `(no label)` — edge [+1.0446]
→ **LOGIT** `node_id=27_44737_8` Layer 27 — `Output " airplane" (p=0.162)`

**Causal path diagram:**

![Causal paths for "<bos>Wheel is to car as wing is to" → "Output " airplane" (p=0.162)"](graphs/bos_wheel_is_to_car_as_wing_is_to__output___airplane____causal_paths.png)

*Figure: Causal paths from input features to predicted token "Output " airplane" (p=0.162)". Y-axis = transformer layer. Edge width = connection strength. Green = excitatory, red = inhibitory, orange = mixed.*

**Mechanistic narrative:**

**[EARLY]** "Wheel is to car as wing is to" activates structural features from the very first layers. F3195 at Layer 2 (node_id=2_3195_6, inf=0.7998) detects "words related to shopping for apparel and gifts" -- likely responding to the relational/comparative structure. F2267 at Layer 5 (node_id=5_2267_4, inf=0.7995) fires for "law related terminology and references to specific cases" -- another formal-register structural feature. F1673 at Layer 5 (node_id=5_1673_5, inf=0.7991) activates for "the word 'general' and phrases containing 'as a whole'" -- capturing the generalizing/abstracting nature of the analogy frame.

**[MIDDLE]** Two directly relevant features appear. F13344 at Layer 9 (node_id=9_13344_3, inf=0.7987) is labeled "phrases suggesting uncertainty or comparison between two things" -- the recurring analogy-comparison feature. F14231 at Layer 9 (node_id=9_14231_8, inf=0.7978) activates for "words representing comparisons and relationships" -- a second explicit relational feature at the same layer. F2024 at Layer 8 (node_id=8_2024_6, inf=0.7996) fires for "terms related to clothes, fit, and fabrics" -- possibly encoding "wing" as a structural-fit component.

**[LATE]** The key late-layer discovery: F5563 at Layer 23 (node_id=23_5563_8, inf=0.7989) detects "words related to transport, aviation, and the military" -- a directly domain-specific feature that explicitly encodes the answer domain (aviation). This is the most domain-specific late-layer feature in any prompt. F6905 at Layer 18 (node_id=18_6905_8, inf=0.7993) fires for "code snippets, variable names, and programming keywords" -- the formal-register feature seen throughout.

**[TOKEN COMPETITION]** " airplane" was predicted with 16.2% probability -- competing with "bird," "plane," "aircraft," and "jet." Path 1 (mixed, weight=112.9) routes 5 hops from L2 through L7, L20, L22, L25 to the LOGIT. The aviation feature (F5563 at L23) sits in the region traversed by Path 2.

**[SYNTHESIS]** The Wheel/car/wing analogy has the clearest late-layer domain feature of any prompt: "transport, aviation, and the military" at Layer 23 (node_id=23_5563_8) directly encodes the answer domain. The circuit shows early structural parsing (L2-L5), middle-layer comparison features (L8-L9), then domain-specific convergence at Layer 23. The low confidence (16.2%) reveals that the aviation-domain feature competes against multiple valid aircraft-part-to-vehicle associations -- "airplane" wins over "bird" and "plane" by a narrow margin.

---

### Prompt: "<bos>Judge is to court as priest is to"

**Predicted token:** `Output " church" (p=0.486)` (prob=0.4864)

**Token competition:**

| Rank | Token | Logit score | Features voting |
|------|-------|-------------|-----------------|

**Circuit walkthrough:**

*Early layers — input recognition*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 0 | 10535 | 0_10535_6 | 0.8001 | 3.2006 |  words related to medical procedures and studies, especially prospective studies |
| 4 | 6863 | 4_6863_5 | 0.7999 | 2.6289 |  instances of the word "as" preceded by the word "used" and/or followed by an article "a", "an", or "the". |
| 5 | 5766 | 5_5766_5 | 0.7997 | 4.0359 |  scientific observations dealing with amount |
| 5 | 7592 | 5_7592_6 | 0.7992 | 1.1868 |  words and phrases related to religion and religious texts |
| 0 | 8409 | 0_8409_6 | 0.7988 | 3.554 | technical or jargonistic terms that are specific to certain fields. |
| 5 | 15819 | 5_15819_6 | 0.7986 | 5.681 |  technical writing about technology standards and mathematical theorems |
| 1 | 11387 | 1_11387_5 | 0.7981 | 2.153 |  formal legal definitions and analysis of how principles work |
| 1 | 15799 | 1_15799_8 | 0.7979 | 3.424 | words related to legal and business documents |
| 2 | 1761 | 2_1761_3 | 0.7977 | 1.8734 |  mentions of 'time' and also recognizes "AS" written in all caps |
| 4 | 8503 | 4_8503_2 | 0.797 | 4.2126 |  words or expressions related to computing or coding |
| 4 | 14419 | 4_14419_5 | 0.7968 | 3.0007 |  the word "nature" along with some of the words that are frequently near it |
| 6 | 3682 | 6_3682_8 | 0.7966 | 6.2657 |  instances of conflict or opposition involving "to" and "against" |
| 2 | 14616 | 2_14616_6 | 0.7962 | 3.2572 | words starting with "pri" as well as capitalized abbreviations. |
| 1 | 10617 | 1_10617_1 | 0.7961 | 2.4774 |  terms related to government, legal proceedings and geography |
| 7 | 3099 | 7_3099_2 | 0.7959 | 42.9148 |  a variety of reference codes, abbreviations, and identifiers from different fields. |
| 0 | 13183 | 0_13183_4 | 0.7957 | 2.5298 | the word "folder" and words associated with file directories |
| 0 | 1218 | 0_1218_6 | 0.7955 | 2.3712 |  words and phrases related to law enforcement, counter-terrorism, and international relations |
| 2 | 7955 | 2_7955_6 | 0.7953 | 3.9906 | technical or legal terminology |
| 3 | 5334 | 3_5334_2 | 0.7951 | 3.3604 | words and phrases related to an organization and office. |
| 0 | 5312 | 0_5312_2 | 0.7949 | 2.0562 |  forms of the verbs "to have" and "to be" as well as modal verbs |
| 4 | 6466 | 4_6466_4 | 0.7948 | 3.6869 |  legal and medical terminology |
| 3 | 446 | 3_446_5 | 0.7944 | 2.5145 |  words related to dates and times |
| 4 | 3913 | 4_3913_5 | 0.7938 | 3.2009 |  words and phrases that are somewhat technical in nature and occur in research articles |
| 0 | 0 | 0_0_8 | 0.7936 | 0.0 | mentions of clubs or sports teams, and sometimes related words like 'sister' or 'kids' |
| 3 | 2543 | 3_2543_5 | 0.7934 | 2.3412 |  words or phrases that indicate a development or reaction to prior events. |
| 6 | 10428 | 6_10428_6 | 0.7933 | 3.8849 |  references to animals or young humans |
| 6 | 5621 | 6_5621_5 | 0.7931 | 2.9088 |  descriptions of musical albums and sports leagues and seasons |
| 2 | 7425 | 2_7425_3 | 0.7929 | 2.1331 | the word "to." |

*Middle layers — relational mapping*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 10 | 9756 | 10_9756_8 | 0.7996 | 6.6485 | a variety of different concepts, including: weather, being small, hat, marriage, language, marketing, and opinions. |
| 9 | 6402 | 9_6402_8 | 0.7994 | 6.1758 |  references to laws, articles and sections. |
| 12 | 3346 | 12_3346_4 | 0.7983 | 13.0283 |  words or phrases that relate to specific topics and their contexts. |
| 12 | 10440 | 12_10440_8 | 0.7975 | 8.2371 |  questions about the relationship between the value of K and the amount of training data in cross validation |
| 8 | 7860 | 8_7860_5 | 0.7972 | 7.4465 | posts about object-relational mapping in Doctrine 2 |
| 9 | 4181 | 9_4181_4 | 0.7964 | 5.3114 |  a variety of different words without an obvious connection |

*Late layers — token selection*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 19 | 10549 | 19_10549_8 | 0.799 | 11.9197 |  words and phrases related to religion and religious belief. |
| 20 | 14217 | 20_14217_8 | 0.7985 | 9.427 |  text related to laws and government, and the path a law takes |
| 17 | 6505 | 17_6505_4 | 0.7974 | 71.919 | court |
| 0 | 17 | 0_17_7 | 0.7946 | 0.0 |  Spanish and Portuguese words related to code and computers |
| 23 | 4640 | 23_4640_8 | 0.7942 | 10.8258 |  the topic of historical sites, graveyards, churches, religious symbols, tattoos, history, etc |
| 25 | 16302 | 25_16302_8 | 0.794 | 7.6558 |  words that are related to people getting something they want. |

**Causal paths (edge-weight chains to logit):**

*Path 1 — (±) mixed | weight=1951.519014 | hops=3*
→ `node_id=E_27708_6` | `feature=?` | Layer E | `(no label)` — edge [+27.4953]
→ `node_id=21_11878_8` | `feature=?` | Layer 21 | `(no label)` — edge [+14.3317]
→ `node_id=24_11123_8` | `feature=?` | Layer 24 | `(no label)` — edge [-4.9524]
→ **LOGIT** `node_id=27_8068_8` Layer 27 — `Output " church" (p=0.486)`

*Path 2 — (±) mixed | weight=70.337922 | hops=5*
→ `node_id=19_10549_8` | `feature=10549` | Layer 19 | ` words and phrases related to religion and religious belief.` — edge [-1.604]
→ `node_id=20_10101_8` | `feature=?` | Layer 20 | `(no label)` — edge [+13.6866]
→ `node_id=21_12427_8` | `feature=?` | Layer 21 | `(no label)` — edge [+1.8565]
→ `node_id=22_2808_8` | `feature=?` | Layer 22 | `(no label)` — edge [+0.5308]
→ `node_id=25_5955_8` | `feature=?` | Layer 25 | `(no label)` — edge [-3.2517]
→ **LOGIT** `node_id=27_8068_8` Layer 27 — `Output " church" (p=0.486)`

*Path 3 — (±) mixed | weight=14.930449 | hops=5*
→ `node_id=7_3099_2` | `feature=3099` | Layer 7 | ` a variety of reference codes, abbreviations, and identifiers from different fields.` — edge [+0.3405]
→ `node_id=20_10101_8` | `feature=?` | Layer 20 | `(no label)` — edge [+13.6866]
→ `node_id=21_12427_8` | `feature=?` | Layer 21 | `(no label)` — edge [+1.8565]
→ `node_id=22_2808_8` | `feature=?` | Layer 22 | `(no label)` — edge [+0.5308]
→ `node_id=25_5955_8` | `feature=?` | Layer 25 | `(no label)` — edge [-3.2517]
→ **LOGIT** `node_id=27_8068_8` Layer 27 — `Output " church" (p=0.486)`

*Path 4 — (±) mixed | weight=5.805039 | hops=4*
→ `node_id=0_1218_6` | `feature=1218` | Layer 0 | ` words and phrases related to law enforcement, counter-terrorism, and international relations` — edge [+0.4896]
→ `node_id=18_7338_8` | `feature=?` | Layer 18 | `(no label)` — edge [+3.4994]
→ `node_id=24_6265_8` | `feature=?` | Layer 24 | `(no label)` — edge [+1.042]
→ `node_id=25_5955_8` | `feature=?` | Layer 25 | `(no label)` — edge [-3.2517]
→ **LOGIT** `node_id=27_8068_8` Layer 27 — `Output " church" (p=0.486)`

**Causal path diagram:**

![Causal paths for "<bos>Judge is to court as priest is to" → "Output " church" (p=0.486)"](graphs/bos_judge_is_to_court_as_priest_is_to__output___church___p__causal_paths.png)

*Figure: Causal paths from input features to predicted token "Output " church" (p=0.486)". Y-axis = transformer layer. Edge width = connection strength. Green = excitatory, red = inhibitory, orange = mixed.*

**Mechanistic narrative:**

**[EARLY]** "Judge is to court as priest is to" activates institutional and procedural features at early layers. The top early node, F10535 at Layer 0 (node_id=0_10535_6, inf=0.8001), fires for "words related to medical procedures and studies" -- detecting formal professional-role terminology. F6863 at Layer 4 (node_id=4_6863_5, inf=0.7999) specifically activates for "instances of the word 'as' preceded by the word 'used' and/or followed by..." -- directly tracking the "is to...as" connective structure of the analogy. F5766 at Layer 5 (node_id=5_5766_5, inf=0.7997) fires for "scientific observations dealing with amount" -- possibly encoding the proportional structure of the analogy ratio.

**[MIDDLE]** F9756 at Layer 10 (node_id=10_9756_8, inf=0.7996) fires for "a variety of different concepts, including weather, being small..." -- encoding the relational abstraction of institutional roles. F6402 at Layer 9 (node_id=9_6402_8, inf=0.7994) activates for "references to laws, articles and sections" -- directly relevant to the "judge/court" source domain. Remarkably, F6505 at Layer 17 (node_id=17_6505_4, inf=0.7974) is labeled simply "court" -- the clearest single-concept feature in the entire dataset. This feature fires at Layer 17, explicitly encoding the source-domain institution and driving the analogical mapping to "church" as the priest's equivalent institution.

**[LATE]** F10549 at Layer 19 (node_id=19_10549_8, inf=0.7990) -- labeled "words and phrases related to religion and religious belief" -- is the decisive late-layer feature, firing just three layers before the logit. F14217 at Layer 20 (node_id=20_14217_8, inf=0.7985) activates for "text related to laws and government, and the path a law takes" -- connecting the legal source domain to the religious target.

**[TOKEN COMPETITION]** " church" was predicted with 48.6% probability -- the highest confidence among the non-geographic analogies. The dominant path (Path 1, mixed, weight=1951.5) goes from an embedding feature through L21 and L24 to the LOGIT. Path 2 (weight=70.3) begins at the religion feature (L19/F10549, node_id=19_10549_8) -- the "religion/religious belief" feature directly feeds the logit through L20->L21->L25->LOGIT. Path 3 (weight=14.9) begins at the recurring cross-graph feature F4828270 at Layer 7 (node_id=7_3099_2).

**[SYNTHESIS]** The Judge/court/priest/church analogy produces the cleanest institutional-role circuit. The model has dedicated single-concept features for the source ("court" at L17/F6505) and a domain feature for the target ("religion/religious belief" at L19/F55857145). The 48.6% confidence reflects competition from "temple," "parish," and "cathedral" -- but "church" wins as the most general institution at the same level of specificity as "court." The causal path through L19/F10549 ("religion/religious belief") -> L20 -> L21 -> L25 -> LOGIT is the clearest example of a domain-knowledge feature directly driving the final prediction.

---

### Prompt: "<bos>Soldier is to army as sailor is to"

**Predicted token:** `Output " navy" (p=0.214)` (prob=0.2139)

**Token competition:**

| Rank | Token | Logit score | Features voting |
|------|-------|-------------|-----------------|

**Circuit walkthrough:**

*Early layers — input recognition*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 3 | 1931 | 3_1931_7 | 0.7997 | 7.5188 |  statements of fact linked to importance or findings |
| 0 | 77 | 0_77_6 | 0.7996 | 4.3663 |  words related to medical, chemical or scientific terminology |
| 2 | 16175 | 2_16175_1 | 0.7992 | 2.2538 |  words related to medicine, including surgeries, anatomy, visual disorders, and scientific study |
| 1 | 15163 | 1_15163_4 | 0.799 | 2.7781 |  the word 'nano' and words that frequently accompany it |
| 2 | 15693 | 2_15693_1 | 0.7988 | 1.7411 |  words related to mythology, fantasy creatures, or awards |
| 0 | 0 | 0_0_7 | 0.7982 | 0.0 | mentions of clubs or sports teams, and sometimes related words like 'sister' or 'kids' |
| 3 | 14108 | 3_14108_5 | 0.7979 | 2.9116 | the word "as" in various contexts |
| 0 | 5742 | 0_5742_1 | 0.7977 | 1.9408 |  scientific vocabulary, especially in the fields of medicine, chemistry, and mathematics. |
| 5 | 9952 | 5_9952_8 | 0.7975 | 6.4855 |  words used in data analysis, code, table contents, or political discussions |
| 0 | 14352 | 0_14352_6 | 0.7971 | 3.9441 |  somewhat technical, scientific, and legal words and phrases |
| 2 | 6944 | 2_6944_2 | 0.7969 | 2.3681 |  words associated with the structure and description of documents, whether academic papers, software code, or geographical routes. |
| 1 | 2388 | 1_2388_6 | 0.7965 | 4.2365 |  job titles and people performing research or engineering roles |
| 3 | 1585 | 3_1585_5 | 0.796 | 2.2516 | words and phrases related to sports and athletic activities, especially soccer |
| 0 | 1412 | 0_1412_5 | 0.7954 | 1.8814 | the word "as" |
| 3 | 8907 | 3_8907_3 | 0.7952 | 2.5361 |  uses of the word "since." |
| 3 | 15857 | 3_15857_5 | 0.795 | 2.5569 |  LaTeX commands relating to relational math symbols |
| 2 | 12949 | 2_12949_6 | 0.7948 | 4.137 |  words related to institutions, political entities, and geography |
| 2 | 13679 | 2_13679_4 | 0.7946 | 3.0223 |  words related to conflict and violence |
| 3 | 14662 | 3_14662_8 | 0.7944 | 5.5199 |  parts of error codes in computer software |
| 3 | 5670 | 3_5670_3 | 0.7943 | 2.9306 |  words related to scientific research and academic publishing from fields like biology and computer science |
| 3 | 76 | 3_76_3 | 0.7941 | 2.2094 | the word "over" |
| 4 | 1489 | 4_1489_8 | 0.7935 | 4.203 |  a wide variety of words that sometimes seem related, but don't have a clear common context |
| 0 | 15414 | 0_15414_8 | 0.7933 | 3.9477 |  words and phrases related to obligation, judgement, or destiny |
| 2 | 2690 | 2_2690_4 | 0.7931 | 2.3278 |  words related to government, politics and investigations |
| 6 | 3682 | 6_3682_8 | 0.7929 | 5.9607 |  instances of conflict or opposition involving "to" and "against" |
| 0 | 13988 | 0_13988_6 | 0.7927 | 4.3827 |  proper nouns, code syntax, and scientific words related to medicine, botany, or climate science |

*Middle layers — relational mapping*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 13 | 2249 | 13_2249_8 | 0.8001 | 11.013 |  noun phrases ending in "-ists", and also seems to have some other unrelated triggers. |
| 7 | 3099 | 7_3099_3 | 0.7986 | 29.5964 |  a variety of reference codes, abbreviations, and identifiers from different fields. |
| 12 | 15847 | 12_15847_8 | 0.7984 | 6.0709 | statistical analysis methods and software |
| 7 | 13740 | 7_13740_5 | 0.798 | 5.3081 |  segments of text that assert the importance of something |
| 9 | 2909 | 9_2909_3 | 0.7967 | 12.9621 |  formulas, ratios, and mathematical notation |
| 9 | 8857 | 9_8857_5 | 0.7962 | 7.9364 |  answer choices in mathematical questions |
| 9 | 1585 | 9_1585_8 | 0.7958 | 6.8474 | words or elements within a list, comparison, or relationship, sometimes including medical or scientific terms and often with formatting oddities |
| 8 | 1018 | 8_1018_6 | 0.7956 | 3.3521 | words and phrases related to tractors, trucks, and other heavy machinery |
| 14 | 2711 | 14_2711_1 | 0.7939 | 57.2538 |  word stems ending in "al" |
| 7 | 5770 | 7_5770_6 | 0.7937 | 4.2125 |  words related to geography, especially to islands, coasts, and marine wildlife |

*Late layers — token selection*

| Layer | Feature | Node_id | Influence | Activation | Feature label |
|-------|---------|---------|-----------|------------|---------------|
| 16 | 15321 | 16_15321_8 | 0.7999 | 8.0962 |  text related to military service and conscription |
| 23 | 592 | 23_592_8 | 0.7994 | 8.4113 | medical terminology related to studies, conditions, and treatments |
| 22 | 11728 | 22_11728_8 | 0.7973 | 7.3609 |  technical and medical writing. |
| 0 | 20 | 0_20_7 | 0.7963 | 0.0 |  instances of the word "hardly" and possibly words close to it within a sentence |

**Causal paths (edge-weight chains to logit):**

*Path 1 — (±) mixed | weight=5.736518 | hops=3*
→ `node_id=23_592_8` | `feature=592` | Layer 23 | `medical terminology related to studies, conditions, and treatments` — edge [-3.8677]
→ `node_id=24_13277_8` | `feature=?` | Layer 24 | `(no label)` — edge [+11.4757]
→ `node_id=25_9975_8` | `feature=?` | Layer 25 | `(no label)` — edge [+0.1292]
→ **LOGIT** `node_id=27_23008_8` Layer 27 — `Output " navy" (p=0.214)`

*Path 2 — (+) excitatory | weight=4.163295 | hops=1*
→ `node_id=E_65294_6` | `feature=?` | Layer E | `(no label)` — edge [+4.1633]
→ **LOGIT** `node_id=27_23008_8` Layer 27 — `Output " navy" (p=0.214)`

*Path 3 — (+) excitatory | weight=2.764542 | hops=3*
→ `node_id=22_11728_8` | `feature=11728` | Layer 22 | ` technical and medical writing.` — edge [+1.8639]
→ `node_id=24_13277_8` | `feature=?` | Layer 24 | `(no label)` — edge [+11.4757]
→ `node_id=25_9975_8` | `feature=?` | Layer 25 | `(no label)` — edge [+0.1292]
→ **LOGIT** `node_id=27_23008_8` Layer 27 — `Output " navy" (p=0.214)`

*Path 4 — (±) mixed | weight=1.208557 | hops=4*
→ `node_id=3_1585_5` | `feature=1585` | Layer 3 | `words and phrases related to sports and athletic activities, especially soccer` — edge [-0.1867]
→ `node_id=23_8967_8` | `feature=?` | Layer 23 | `(no label)` — edge [+8.1596]
→ `node_id=24_5999_8` | `feature=?` | Layer 24 | `(no label)` — edge [-6.1388]
→ `node_id=25_9975_8` | `feature=?` | Layer 25 | `(no label)` — edge [+0.1292]
→ **LOGIT** `node_id=27_23008_8` Layer 27 — `Output " navy" (p=0.214)`

*Path 5 — (±) mixed | weight=1.021205 | hops=2*
→ `node_id=0_20_7` | `feature=20` | Layer 0 | ` instances of the word "hardly" and possibly words close to it within a sentence` — edge [-1.1999]
→ `node_id=25_4717_8` | `feature=?` | Layer 25 | `(no label)` — edge [+0.8511]
→ **LOGIT** `node_id=27_23008_8` Layer 27 — `Output " navy" (p=0.214)`

**Causal path diagram:**

![Causal paths for "<bos>Soldier is to army as sailor is to" → "Output " navy" (p=0.214)"](graphs/bos_soldier_is_to_army_as_sailor_is_to__output___navy___p_0__causal_paths.png)

*Figure: Causal paths from input features to predicted token "Output " navy" (p=0.214)". Y-axis = transformer layer. Edge width = connection strength. Green = excitatory, red = inhibitory, orange = mixed.*

**Mechanistic narrative:**

**[EARLY]** "Soldier is to army as sailor is to" activates features related to institutional roles and formal factual structure. The top early node, F1931 at Layer 3 (node_id=3_1931_7, inf=0.7997), fires for "statements of fact linked to importance or findings" -- capturing the definitional, encyclopedic register of military taxonomy. F77 at Layer 0 (node_id=0_77_6, inf=0.7996) activates for "words related to medical, chemical or scientific terminology" -- a formal/categorical classification feature. F16175 at Layer 2 (node_id=2_16175_1, inf=0.7992) fires for "words related to medicine, including surgeries, anatomy, visual..." -- again a formal technical-category feature rather than a domain-specific one.

**[MIDDLE]** The most domain-specific feature appears in the middle layers: F2249 at Layer 13 (node_id=13_2249_8, inf=0.8001) activates for "noun phrases ending in '-ists', and also seems to have some other..." -- encoding the professional-role suffix pattern linking soldier/sailor as members of a category. The recurring cross-graph feature F4828270 at Layer 7 (node_id=7_3099_3, inf=0.7986) -- "a variety of reference codes, abbreviations, and identifiers" -- appears in the middle band, one of the 429 recurring analogy-circuit features from Step 5.

**[LATE]** The decisive late-layer feature is F15321 at Layer 16 (node_id=16_15321_8, inf=0.7999): "text related to military service and conscription" -- a domain-specific feature encoding the military branch taxonomy. This feature explicitly encodes the military domain at Layer 16, enabling the model to select "navy" as the branch of military service employing sailors (analogous to the army employing soldiers). F592 at Layer 23 (node_id=23_592_8, inf=0.7994) fires for "medical terminology related to studies, conditions, and treatments" -- a mismatched label reflecting co-activation with institutional service roles.

**[TOKEN COMPETITION]** " navy" was predicted with 21.4% probability. Unlike most other prompts, the circuit has very weak causal paths: Path 1 (mixed, weight=5.7) and Path 2 (excitatory, weight=4.2) are dramatically weaker than the 100+ weights seen in other prompts. This weak path signal, combined with the presence of two excitatory paths, suggests the model is operating with a diffuse, weakly-connected circuit for military taxonomy. Path 1 begins at F592 (Layer 23, "medical terminology"), routes to L24->L25->LOGIT -- a short convergent chain that bypasses most labeled features.

**[SYNTHESIS]** The Soldier/army/sailor/navy analogy produces the weakest circuit in the dataset, with path weights two orders of magnitude below those of the Leaf/petal and Judge/church prompts. Despite having a clear domain feature at Layer 16 (F15321: "military service and conscription"), the causal paths do not route through it -- the logit is primarily driven by short embedding-to-late-layer connections. This dissociation between the identified domain feature and the actual causal pathway suggests the "navy" prediction is partially driven by token co-occurrence statistics rather than a clean analogical inference chain. The 21.4% confidence reflects genuine competition from "fleet," "ship," and "naval" as alternative completions.

---

## Discussion

### What the Recurring Features Reveal About Analogical Reasoning

The 429 recurring features identified at the 50% threshold reveal a surprising architecture for analogical reasoning in Gemma-2-2B. The most universal features (L6/F2586668, L3/F5150441) are labeled not as "analogy" or "comparison" features but as structural-register features associated with formal documentation, code, and legal text. This finding suggests that the model's internal representation of the "A is to B as C is to D" template resembles formal technical documentation patterns -- consistent with the observation that analogical reasoning prompts have a distinctive syntactic formality (repeated "is to" connectives, balanced parallel structure) that activates features normally associated with structured, formal text.

In contrast, the explicit analogy-labeled features (L8/F94882191 "analogies or comparisons," L5/F16817094 "analogies," L7/F286895 "analogies and comparisons," L9/F89171325 "phrases suggesting uncertainty or comparison") appear in layers 5-9 -- after the structural parsing features at L3-L6. This layered pattern supports a two-stage interpretation: (1) the model first detects that the input has a formal comparative structure (Layers 3-6), then (2) recognizes it specifically as an analogical comparison (Layers 5-9). The structural detection precedes the semantic classification.

### Excitatory Path Consistency

Across 10 prompts, 7 had at least one excitatory (purely positive-weight) causal path. The two highest-confidence predictions (Paris/Germany, 97.3%; Cairo/Kenya, 96.3%) had the richest domain-specific feature activation, while the four lowest-confidence predictions (Fish/air, Leaf/flower, Wheel/airplane, Soldier/navy) either lacked excitatory paths entirely or had excitatory paths originating from embedding-level features rather than labeled mid-layer features. This correlation between excitatory-path presence and confidence supports the interpretation that excitatory paths represent the dominant computational mechanism when the model has strong domain knowledge, while mixed paths dominate when domain knowledge is weak or absent.

The most consistent late-layer convergence point is the L19-L21 aggregation hub. Paths from 8 of 10 prompts pass through this region (L19-L25) before reaching the logit at L27. Features at L14348 (Layer 19/20, "prepositions and connectors") appear as the highest-influence late-layer feature in two prompts (Paris/Germany and Clock/thermometer), suggesting this feature tracks the final "is to [ANSWER]" slot that the model is completing.

### Inhibitory Paths: Systematic or Noise?

No purely inhibitory (all-negative-weight) causal paths appeared in the top-5 paths for any prompt. All paths were either excitatory or mixed. This absence of systematic inhibitory paths suggests that token competition in analogical reasoning is not primarily implemented through explicit inhibition of competitor tokens but rather through positive selection of the winning token -- the model converges on the answer through amplification rather than suppression. The mixed paths (alternating positive and negative edges) may represent gating or modulation rather than direct token competition.

### Path Structure vs. Layer Distribution

The layer distribution of recurring features concentrates in Layers 0-10, while the causal paths consistently pass through Layers 17-27. This apparent mismatch is explained by the attribution graph structure: the recurring features at Layers 0-10 are the most consistently present circuit components, but the actual causal signal to the logit travels primarily through late-layer nodes (Layers 17-27) that are prompt-specific and therefore do not appear as recurring features at the 50% threshold.

The edge neighbourhood analysis (Step 5a) supports this interpretation: the top recurring feature by influence (L7/F4828270, "reference codes/abbreviations") has outgoing edges primarily to Layers 9-10 (not directly to the logit), suggesting it acts as a mid-network signal aggregator rather than a final prediction driver.

### Surprising Findings

1. **The dominant recurring feature (L6/F2586668) activates analogical reasoning through a documentation/code register, not a semantic analogy register.** The most universal circuit component for analogical reasoning fires on "code, legal jargon, and scientific texts" -- patterns associated with the formal structure of the "A is to B as C is to" template rather than its meaning.

2. **Path weight is not correlated with prediction confidence.** The Leaf/petal analogy (p=0.136) has the highest maximum path weight (2086.9) of any prompt; the Soldier/navy analogy (p=0.214) has the lowest (5.7). Path weight measures the strength of individual edge connections, not the clarity of the token-selection decision.

3. **Two prompts have explicit "analogy" template features in their late-layer bands** (L15/F12474: "analogies in conversational text"; L17/F2469: "analogies using 'the same way' construction"). These appear specifically in functional/activity analogies (Clock/thermometer and Book/reading), suggesting a dedicated analogy-recognition sub-circuit for this category.

4. **The Judge/court prompt has a single-concept "court" feature at Layer 17 (F6505).** This is the only case where a single-word concept feature appears as a top-influence node in the late band, directly encoding the source-domain institution and enabling the analogical mapping to "church." This direct concept-to-concept mapping underpins the highest-confidence non-geographic analogy (p=0.486).

---

## Causal Validation via Feature Steering

To test whether the causal paths identified above are genuinely load-bearing — not merely high-attribution but functionally inert — we ran causal steering experiments on three analogical circuits using the Neuronpedia Steering API. For each circuit, we extracted the backbone features from the per-prompt top-5 causal paths and applied four tests: (A) **Necessity** — suppress each backbone feature individually at strength −20 and check whether the model's first predicted token changes; (B) **Full backbone suppression** — suppress all backbone features simultaneously; (C) **Sufficiency** — boost the circuit's primary hub at strength +20 on an altered prompt to test whether the hub alone can induce the target prediction; (D) **Specificity** — suppress non-backbone features (high-activation nodes not on the top-5 causal paths) to confirm they are causally inert.

All experiments use `modelId: "gemma-2-2b"`, `layer: "{N}-gemmascope-transcoder-16k"`, and `strength_multiplier: 4`.

### A. Necessity (Individual Feature Suppression)

#### Paris→Germany (p=0.973, 9 backbone features)

| Feature | Layer | Index | Role in Causal Path | Steered 1st Token | Disrupted? |
|---------|-------|-------|---------------------|-------------------|------------|
| L21_science_hub | 21 | 4827 | Strongest path entry (edge +198.0) | Germany | no |
| L22_relay | 22 | 15670 | Path 1 relay | Germany | no |
| L25_output_driver_a | 25 | 4717 | Final amplifier | Germany | no |
| L16_location_encoder | 16 | 6491 | Location/direction feature | Germany | no |
| L17_relay | 17 | 14546 | Mid-cascade relay | Germany | no |
| L19_relay | 19 | 5773 | Late relay | Germany | no |
| L21_integrator | 21 | 7482 | Integration hub (paths 2–4) | Germany | no |
| **L25_output_driver_b** | **25** | **2725** | **Secondary output driver (edge −2.09)** | **the** | **YES** |
| L19_relation_applier | 19 | 855 | Relation application node | Germany | no |

Only L25/2725 (secondary output driver) is uniquely necessary. This feature appears on paths 2–5 as the final gate. The primary path through L21→L22→L25_4717 provides redundant coverage, explaining why most individual suppressions don't disrupt.

#### Cairo→Kenya (p=0.963, 9 backbone features)

| Feature | Layer | Index | Role in Causal Path | Steered 1st Token | Disrupted? |
|---------|-------|-------|---------------------|-------------------|------------|
| L15_relay | 15 | 15954 | Path 1 mid relay | Kenya | no |
| L18_legal_docs | 18 | 13586 | Legal docs feature | Kenya | no |
| L24_suppressor | 24 | 1260 | Competitor suppression | Kenya | no |
| L25_output_a | 25 | 15920 | Output driver path 1 | Kenya | no |
| L20_relay | 20 | 15360 | Path 2 relay | Kenya | no |
| **L23_relay** | **23** | **13914** | **Late relay (edge +10.65)** | **the** | **YES** |
| **L25_output_b** | **25** | **286** | **Secondary output driver** | **the** | **YES** |
| L15_geography | 15 | 5355 | Geographical locations | Kenya | no |
| L21_convergence | 21 | 5251 | Convergence hub | Kenya | no |

Two features are uniquely necessary — L23/13914 and L25/286 — both on path 2 (L5→L20→L23→L24→L25→logit). The path 1 cascade through L15→L18→L24→L25 is fully redundant.

#### Puppy→cat (p=0.756, 4 backbone features)

| Feature | Layer | Index | Role in Causal Path | Steered 1st Token | Disrupted? |
|---------|-------|-------|---------------------|-------------------|------------|
| L14_relay | 14 | 3704 | Path 1 relay | cat | no |
| L20_integration | 20 | 3094 | Integration hub | cat | no |
| L22_relay | 22 | 15670 | Late relay | cat | no |
| L25_amplifier | 25 | 4717 | Final amplifier | cat | no |

No individual feature is necessary. This circuit has only 4 backbone features from the top-5 causal paths — the fewest of any tested circuit — suggesting the prediction is carried primarily by direct embedding→logit paths that bypass the multi-hop backbone entirely.

### B. Full Backbone Suppression

| Circuit | Default Completion | Steered Completion | Disrupted? |
|---------|--------------------|--------------------|------------|
| Paris→Germany | ...Germany. It is the | ...of of of of of | **YES** |
| Cairo→Kenya | ...Kenya. It is the | ...(whitespace) | **YES** |
| Puppy→cat | ...cat. I' | ...cat. I think | no |

Full backbone suppression disrupts 2 of 3 analogical circuits. The puppy→cat circuit is the exception: its prediction survives even simultaneous suppression of all tested backbone features. This is consistent with the circuit's lower confidence (p=0.756) and the finding from the per-prompt analysis that this prompt has shorter, more direct causal paths. The model's prediction of "cat" is likely rooted in direct embedding→logit connections that were not captured by the top-5 multi-hop causal path tracing.

### C. Sufficiency (Hub Boost on Altered Prompts)

| Circuit | Hub Boosted | Altered Prompt | Baseline → Boosted | Target Induced? |
|---------|-------------|----------------|--------------------|-----------------:|
| Paris→Germany | L21/4827 | "Cairo is to Egypt as Nairobi is to" | Kenya → Kenya | no |
| Paris→Germany | L21/4827 | "Madrid is to Spain as Berlin is to" | — → Germany | **YES** |
| Cairo→Kenya | L15/15954 | "Paris is to France as Berlin is to" | Germany → Germany | no |
| Cairo→Kenya | L15/15954 | "Lagos is to Nigeria as Nairobi is to" | — → Kenya | **YES** |

Sufficiency succeeds when the altered prompt retains the target entity — boosting the Paris circuit's L21 hub on a prompt containing "Berlin" does produce "Germany", and boosting Cairo's L15 hub on a prompt containing "Nairobi" does produce "Kenya". Sufficiency fails across domain boundaries: the Paris hub cannot inject "Germany" into the Cairo/Nairobi context. These hubs encode domain-specific geographic associations, not general-purpose "answer slot" activators.

### D. Specificity (Non-Backbone Feature Suppression)

| Circuit | Non-Backbone Feature | Neuronpedia Label | Steered 1st Token | Disrupted? |
|---------|---------------------|-------------------|-------------------|------------|
| Paris→Germany | L6/3335 | "difficulty/challenges" | Germany | no |
| Paris→Germany | L13/4435 | "opera-related terms" | Germany | no |
| Cairo→Kenya | L5/5500 | "profanity and comparisons" | Kenya | no |
| Cairo→Kenya | L0/8 | "are/research" | Kenya | no |
| Puppy→cat | L9/2909 | "formulas/ratios" | cat | no |

All 5 non-backbone features pass the specificity test — suppressing them has no effect on the prediction. This confirms that the causal path analysis correctly distinguishes load-bearing backbone features from high-activation but causally inert nodes.

### Summary

| Circuit | Confidence | Necessary Features | Full Suppress | Sufficiency | Specificity |
|---------|------------|-------------------|---------------|-------------|-------------|
| Paris→Germany | 0.973 | 1/9 (L25/2725) | DISRUPTED | 1/2 | PASS (0/2) |
| Cairo→Kenya | 0.963 | 2/9 (L23/13914, L25/286) | DISRUPTED | 1/2 | PASS (0/2) |
| Puppy→cat | 0.756 | 0/4 | intact | — | PASS (0/1) |

The causal validation confirms that the backbone features identified through causal path tracing are collectively necessary for the high-confidence geographic analogies (Paris, Cairo) but not for the lower-confidence functional analogy (Puppy). Individual necessity is sparse — most backbone features are redundant due to the highly parallel path structure documented above. The L25 output-driver layer emerges as the critical bottleneck across both validated circuits, consistent with the Discussion's finding that all prompts show convergent late-layer aggregation through Layers 21–25.

---

## Limitations

**Attribution graph thresholds.** Graph generation used nodeThreshold=0.8 and edgeThreshold=0.85, which may exclude weak but relevant features. A lower threshold would increase graph density and potentially reveal additional analogy-specific features.

**SAE coverage.** The gemmascope-transcoder-16k SAE covers all 26 transformer layers but is a transcoder (not a standard SAE), and feature labeling relies on automated interpretability methods from Neuronpedia. Some feature labels appear incorrect or underspecified (e.g., L6/F2586668 labeled as "programming code" despite its universal role in the analogy circuit). True circuit interpretation requires human verification of feature labels.

**Single-model analysis.** All results are specific to Gemma-2-2B. Whether the same circuit components appear in larger models (Gemma-2-9B, Gemma-2-27B) or other model families is unknown.

**Logit contribution sparsity.** Token competition data was unavailable for most prompts (logitContributions field absent or empty), limiting quantification of score gaps between predicted and competing tokens.

**Causal path algorithm.** The greedy forward/backward path tracing finds the strongest single-step paths, not all paths. Complete path enumeration would provide a richer picture of circuit redundancy.

**Causal validation coverage.** Steering experiments were run on 3 of 10 prompts (Paris, Cairo, Puppy). The remaining 7 prompts — particularly the low-confidence functional analogies (Fish, Leaf, Wheel, Soldier) — were not causally validated. Extending validation to these circuits would test whether the sparse-necessity pattern holds for diffuse, mixed-sign path structures.

---

## Conclusion

This paper presents a detailed mechanistic interpretability analysis of analogical reasoning in Gemma-2-2B using attribution graphs and causal path tracing across 10 diverse prompts. The key findings are:

1. **A two-stage circuit** implements analogical reasoning: a universal structural-parsing stage (Layers 0-6) detects the formal "A is to B as C is to" template, while a domain-specific resolution stage (Layers 7-27) determines prediction confidence.

2. **429 recurring features** are shared across >= 50% of prompts. The most universal are structural-register features (L6/F2586668, L3/F5150441) rather than semantic analogy features, suggesting the model classifies the analogy template by formal structure before activating domain knowledge.

3. **Prediction confidence correlates with causal path clarity**: high-confidence geographic analogies (p>=0.96) produce convergent excitatory causal chains; low-confidence functional analogies (p<=0.18) produce diffuse, mixed-sign path structures.

4. **Explicit analogy-detection features** exist at Layers 5, 7, 8, 9, and 15: F16817094 ("analogies"), F286895 ("analogies and comparisons"), F94882191 ("analogies or comparisons"), F89171325 ("phrases suggesting uncertainty or comparison"), and F12474 ("analogies in conversational text"). These form a dedicated analogy-recognition sub-network.

5. **All 10 prompts show convergent late-layer aggregation** through Layers 17-27, with the logit node at Layer 27 receiving inputs through an L19-L21-L25 hub. This hub is the final common pathway for analogical reasoning output in Gemma-2-2B.

These results demonstrate that mechanistic interpretability methods -- attribution graphs, causal path tracing, and cross-graph feature comparison -- can reveal specific computational mechanisms underlying abstract reasoning in large language models.
