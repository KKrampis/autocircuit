---
title: "Mechanistic Interpretability of Analogical Reasoning in Gemma-2-2B"
subtitle: "A Sparse Autoencoder Attribution Graph Analysis"
date: "March 2026"
model: "Gemma-2-2B"
sae: "gemmascope-transcoder-16k"
authors:
  - name: "Olalekan Alagbe"
    url: "https://www.linkedin.com/in/olalekanjoshuaalagbe1000/"
  - name: "Joseph Lawrence"
    url: ""
  - name: "Anish Maheshwar"
    url: ""
  - name: "Konstantinos Krampis"
    url: "https://www.linkedin.com/in/kkrampis/"
links:
  - label: "PDF"
    icon: "fa-solid fa-file-pdf"
    url: "paper.pdf"
  - label: "Supplementary"
    icon: "fa-solid fa-file-lines"
    url: "supplementary.html"
  - label: "Code"
    icon: "fab fa-github"
    url: "https://github.com/kkrampis/autocircuit"
  - label: "Presentation"
    icon: "fa-solid fa-display"
    url: "presentation.html"
tldr: >
  We identify a shared 119-feature analogical reasoning circuit in Gemma-2-2B
  that generalizes across geographic and semantic analogies, including a dedicated
  `L5 SAE#5793` feature labeled simply *"analogies"* — direct evidence of a
  reusable relational reasoning primitive.
bibtex: |
  @article{alagbe2026analogical,
    title   = {Mechanistic Interpretability of Analogical Reasoning in {Gemma-2-2B}:
               A Sparse Autoencoder Attribution Graph Analysis},
    author  = {Alagbe, Olalekan and Lawrence, Joseph and Maheshwar, Anish and Krampis, Konstantinos},
    year    = {2026},
    month   = {March},
    note    = {Neuronpedia API gemmascope-transcoder-16k SAE analysis}
  }
supplementary:
  - label: "Supplementary Material"
    icon: "fa-solid fa-file-lines"
    url: "supplementary.html"
    description: "Full supplementary document: all inference prompts, agent pipeline prompts used by Olalekan, links to all five Neuronpedia attribution graphs, and tooling reference."
    sublinks:
      - label: "PDF version"
        url: "supplementary.pdf"
        desc: "Downloadable PDF of the supplementary material"
  - label: "Interactive Presentation"
    icon: "fa-solid fa-display"
    url: "presentation.html"
    description: "20-slide reveal.js presentation with GitHub dark theme, circuit flow diagrams, feature tables, and layer-by-layer analysis."
  - label: "Live Attribution Graphs"
    icon: "fa-solid fa-brain"
    url: "https://www.neuronpedia.org/gemma-2-2b/graph?slug=analog_berlin"
    description: "Interactive Neuronpedia attribution graph viewer for all five prompts. Full graph list with prompts in Supplementary Material."
    sublinks:
      - label: "analog_berlin"
        url: "https://www.neuronpedia.org/gemma-2-2b/graph?slug=analog_berlin"
        desc: "Paris:France::Berlin:?"
      - label: "analog_rome"
        url: "https://www.neuronpedia.org/gemma-2-2b/graph?slug=analog_rome"
        desc: "Paris:France::Rome:?"
      - label: "analog_tokyo"
        url: "https://www.neuronpedia.org/gemma-2-2b/graph?slug=analog_tokyo"
        desc: "Paris:France::Tokyo:?"
      - label: "analog_teacher"
        url: "https://www.neuronpedia.org/gemma-2-2b/graph?slug=analog_teacher"
        desc: "Doctor:hospital::teacher:?"
      - label: "analog_bird"
        url: "https://www.neuronpedia.org/gemma-2-2b/graph?slug=analog_bird"
        desc: "Fish:water::bird:?"
---


## Abstract

We present a mechanistic analysis of analogical reasoning in Gemma-2-2B using Neuronpedia attribution graphs and Sparse Autoencoder (SAE) features. By generating and comparing five attribution graphs across structurally distinct analogical prompts, covering geographic analogies (*Paris - France → Berlin - ?*, *Rome - ?*, *Tokyo - ?*) and semantic role analogies (*Doctor - hospital → teacher - ?*, *Fish - water → bird - ?*), we identify a shared **analogical reasoning circuit** comprising 119 features active across all five prompts and 490 features active across at least three. Each feature is identified by a fixed *(layer, feature index)* pair, identifying circuits as lists of recurring internal model feature activation patterns that retain similar structure across analogical prompts.

We discover dedicated analogy-encoding features at layers 5, 8, 9, and 13, including a feature at layer 5 labeled literally as **"analogies"** and a layer 8 feature encoding **"analogies or comparisons"** appearing across all graphs with high confidence. Early layers (0–4) contain circuit patterns tracking the "X is to Y as Z is to" pattern, while mid-to-late layers (5–13) house increasingly semantic representations of the relational structure. The circuit spans 21 of the model's 26 transformer layers and exhibits cross-domain generalization, with the same core features activating for both geographic and semantic role analogies. Causal validation via feature steering shows that ablating the 180-feature circuit — but not a size- and strength-matched random control — collapses the model to the bare analogy template across all five prompts; that this effect is not reducible to deletion of input-token features and reproduces on held-out analogies; and that Phase 2 features collectively implement the relational-transfer operation at the computational core of analogical reasoning.

---

<!-- slide: What Is Analogical Reasoning? -->

## 1. Introduction

<!-- figure:fig-analogy-task -->

**Figure 1:** The analogy task structure: a known pair (Paris → France, linked by "capital-of") given alongside a query pair (Berlin → Germany?) to be completed by the same relation.

Analogical reasoning, the ability to recognize a structural relationship between one pair of concepts and apply it to another, is a foundational cognitive ability underlying language understanding and abstract problem solving. The analogy task, *"Paris is to France as Berlin is to \_\_\_\_,"* tests whether a model can identify the capital-city relationship abstractly and apply it to a new country. Large language models (LLMs) exhibit striking competence on such tasks [1], yet the internal computational mechanisms remain poorly understood.

Mechanistic interpretability research has made significant progress in understanding factual recall circuits [2], indirect object identification [3], and syntactic processing [4]. Sparse autoencoders (SAEs) have emerged as a central tool in this effort, learning sparse, interpretable decompositions of model activations [5, 6] that can be applied at scale across all layers and sublayers of large models [7]. The Neuronpedia platform [8] operationalizes this infrastructure, providing public APIs for attribution graph generation and feature steering that democratize circuit-level analysis beyond institutions with direct model access.

However, analogical reasoning presents a distinct challenge beyond prior circuit analyses: it requires not merely retrieving a stored fact, but recognizing a **relational structure** and applying it compositionally to novel inputs. The relation type is never named in the prompt — the model must infer *capital-of* from the example alone, hold it as a variable, and transfer it to a new argument pair. Prior work has documented that LLMs exhibit apparently emergent analogical reasoning [1] and identified internal attention-head mechanisms supporting abstract reasoning [9], yet a feature-level, causally-validated circuit account has been absent.

We address this gap using attribution graphs generated from the `gemmascope-transcoder-16k` SAE suite [7], which provides cross-layer transcoder features for every layer of Gemma-2-2B. Our analysis identifies interpretable features that explicitly encode analogical structure, sorts them into three functional groups, and validates their causal role through feature steering. This contributes an SAE-level account of analogical reasoning in a large language model.

<!-- slide: Research Questions -->

### 1.1 Research Questions

1. Does Gemma-2-2B employ a **shared circuit** for analogical reasoning, or does it use different mechanisms for different analogy types?
2. Which SAE features — identified by stable *(layer, feature index)* pairs — are most **consistently activated** across diverse analogical prompts?
3. Are there interpretable, semantically meaningful circuits that encode the **abstract relational structure** of analogies, and how are they discovered?
4. Can the circuit's causal role be confirmed by feature steering?

---

## 2. Methodology

<!-- slide: Prompt Selection -->

### 2.1 Prompt Selection

We selected five prompts spanning two structural analogy types to ensure cross-domain coverage:

**Table 1:** The five prompts used to generate attribution graphs, with each prompt's ID, full text, expected completion, and analogy type.

| ID | Prompt | Expected | Type |
|---|---|---|---|
| `analog_berlin` | *"Paris is to France as Berlin is to"* | Germany | Capital |
| `analog_rome` | *"Paris is to France as Rome is to"* | Italy | Capital |
| `analog_tokyo` | *"Paris is to France as Tokyo is to"* | Japan | Capital |
| `analog_teacher` | *"Doctor is to hospital as teacher is to"* | school | Semantic role |
| `analog_bird` | *"Fish is to water as bird is to"* | air / sky | Semantic role |

<!-- slide: Attribution Graph Generation -->

### 2.2 Attribution Graph Generation

Attribution graphs were generated using the Neuronpedia API [8] with Gemma-2-2B and the gemmascope-transcoder-16k SAE [7], a 26-layer cross-layer transcoder with 16,384 features per layer. Each graph request returns a JSON object containing nodes (the active SAE features, with their layer, index, influence score, and activation magnitude) and the weighted connections between them (attribution scores). Graphs were generated with Neuronpedia's default parameters.

### 2.3 Feature Identification and Cross-Graph Analysis

#### 2.3.1 Feature Identity via Fixed (Layer, Feature Index) Pairs

Each feature in the attribution graphs is identified by a (layer, feature index) pair. For example, (5, 5793) refers to feature 5793 in the layer 5 transcoder. These identifiers are fixed properties of the trained SAE [7]: once the SAE is trained, a feature keeps the same (layer, feature index) pair across every prompt, session, and API call.

Cross-graph feature overlap was computed by finding which *(layer, feature index)* pairs appear in more than one graph. We have five prompts, so each feature can appear in anywhere from 1 to 5 of the graphs. For a threshold $k$, we keep a feature if it appears in at least $k$ of the five graphs:

$$\mathcal{C}_k = \left\{ f \;\middle|\; \sum_{i=1}^{5} \mathbf{1}[f \in G_i] \geq k \right\}$$

We analyze three values of $k$. At $k=3$, we keep features appearing in at least 3 of the 5 graphs (490 features). At $k=4$, at least 4 of 5 (210 features). At $k=5$, a feature must appear in all five graphs (119 features). The 119-feature circuit at $k=5$ is the focus of our analysis: these are the features that recur across all five prompts, whether the analogy is geographic or semantic. We ranked the 119 features by influence, a score that reflects how much each feature contributes to the model's final output, and retrieved Neuronpedia labels [8] for the top 50. Every feature named in the following sections is drawn from this labeled set.

### 2.4 Three Functional Feature Groups: How the Grouping Was Identified

The interpretable core features sort into three functional groups. We did not impose this grouping in advance; it emerged from the content of the Neuronpedia labels.

**Semantic label analysis.** After retrieving Neuronpedia automated labels for the top recurring features, a consistent pattern emerged across layer depth. Features in layers 0–4 carry structural labels: "the word 'to'", "'to' followed by a verb", "the phrase 'it is to'". Features in layers 5–9 carry explicitly relational-semantic labels: "analogies", "analogies or comparisons", "comparison between two things". Features in layers 10–13 carry integrative labels: "comparisons between disciplines and relationships between concepts". The groups therefore emerge from the content of the labels rather than an arbitrary partition of layers; the associated layer ranges describe where each group concentrates, not sharp boundaries. This organization mirrors the emergent symbolic architecture documented by Webb et al. [9] for abstract reasoning more broadly, where early layers abstract tokens into relational variables, intermediate layers perform induction over those variables, and later layers retrieve the answer.

**Table 2:** The three functional feature groups. Each row is one group; the columns give the layer range where the group concentrates and its functional role. Group membership is defined by feature-label content, not by layer boundaries.

| Group | Layer range | Role |
| --- | --- | --- |
| Structural | L0–L4 | Parsing the shape and format of the analogy |
| Relational | L5–L9 | Recognizing the relational concept itself |
| Integration | L10–L13 | Combining relation with domain knowledge |

**Causal validation.** Group boundaries were then tested causally via collective suppression experiments (§3.4), which confirmed that each group is collectively necessary and that earlier groups are prerequisites for later ones.

### 2.5 Discovery of Analogy-Concept Features

After the cross-graph overlap analysis, once the intersection of features across all graphs was computed, each feature's automated Neuronpedia explanation [8] was retrieved. Two of the recurring features returned labels that directly named the task: L5 SAE#5793 was labeled "analogies" and L8 SAE#13766 was labeled "analogies or comparisons." These were not features we set out to find; they surfaced from the overlap analysis on their own.

The significance of these labels is their **domain-independence**. Both features appear in attribution graphs for Berlin, Rome, and Tokyo (geographic capital analogies) and for teacher and bird (semantic role analogies). This is consistent with the broader finding in the analogical reasoning literature that LLMs encode relational information in a domain-general manner [10, 11], and extends that behavioral finding to a specific, causally-validated internal feature.

### 2.6 Functional Group 2 Definition

Group 2 is defined by two jointly applied criteria: **layer position (5–9)** and **feature label content**. Features in this layer range whose Neuronpedia labels explicitly reference analogies, comparisons, or relational structure constitute Group 2. The four members are:

**Table 3:** The four features defining Functional Group 2, with their Neuronpedia labels.

| Feature | Label |
|---|---|
| L5 SAE#5793 | "analogies" |
| L5 SAE#2141 | "comparisons of people or figures using well-known public figures" |
| L8 SAE#13766 | "analogies or comparisons" |
| L9 SAE#13344 | "phrases suggesting uncertainty or comparison between two things" |

This grouping is validated causally: suppressing all four Group 2 features simultaneously collapses all five circuits, with capital analogies producing "France" — the source-pair answer — rather than the target country. An arbitrary group definition would not produce such a consistent and semantically meaningful failure mode.

### 2.7 Causal Validation via Feature Steering

The cross-graph analysis (§2.3) identifies the 180-feature shared circuit as a *common* object: these features recur across all five analogy graphs. Recurrence does not establish that the circuit *causes* the model's answers — a recurring feature could be a passenger that co-activates with the computation without driving it. We test causation by intervening on the circuit with the Neuronpedia `/api/steer` endpoint [8] (`modelId: "gemma-2-2b"`, `strength_multiplier: 4`, `temperature: 0`, `seed: 42`).

One methodological fact governs the whole validation. The per-feature `strength` we set (−20 for ablation) is scaled by the global `strength_multiplier` of 4, so the effective intervention is **−80** per feature — a large perturbation. At that magnitude, removing *any* sizable feature set derails the model, so the bare observation "the output changed" (necessity) is necessary but **not sufficient** evidence that a particular circuit is responsible. The discriminating evidence is of two kinds: (i) a **matched contrast** — does ablating the circuit break the task differently from ablating a size- and strength-matched *random* set? — and (ii) a **predicted failure mode** — does the model fail in the specific way the circuit's claimed role implies? Our design is built on these rather than on necessity alone:

1. **Circuit necessity vs. a matched null (primary).** For each of the five analogy prompts, run two ablations of identical size (180 features) and strength (−20): (a) all 180 circuit features, and (b) 180 random *non*-circuit features drawn from the same prompt's graph. The evidence is the contrast between them.
2. **Internal structure (individual necessity).** Ablate each of the 180 features one at a time to locate the individually necessary members.
3. **Robustness.** Layer-stratified ablation (is the effect just deletion of L0 token features?), a strength titration (is it an artifact of the large −80 magnitude?), and held-out analogy prompts the circuit was never derived from (does it generalize?).
4. **Architecture.** Collective suppression of the Group 1 and Group 2 features (§2.4) to test the three-group organization.
5. **Single-feature side-tests.** A sufficiency probe (boost the highest-influence hub) and an individual non-circuit specificity scan, reported as supplementary single-feature controls.

Across these paradigms the validation comprises **218 individual steering API calls**.

---

## 3. Results

<!-- slide: Attribution Graph Structure -->

### 3.1 Graph Structure

All five attribution graphs exhibited a consistent structural pattern, with features activated across all 26 layers (0–25):

**Table 4:** Structural statistics for each of the five attribution graphs — node count, edge count, and the maximum influence score observed.

| Graph | Prompt | Nodes | Edges | Max Influence |
|---|---|---|---|---|
| `analog_berlin` | Paris - France → Berlin - ? | 930 | 25,915 | 0.8001 |
| `analog_rome` | Paris - France → Rome - ? | 963 | 27,608 | 0.8002 |
| `analog_tokyo` | Paris - France → Tokyo - ? | 905 | 22,414 | 0.8001 |
| `analog_teacher` | Doctor - hospital → teacher - ? | 1,040 | 35,481 | 0.8001 |
| `analog_bird` | Fish - water → bird - ? | 1,071 | 38,741 | 0.8000 |



<!-- slide: Core Circuit Identification -->

### 3.2 The Core Analogical Reasoning Circuit

<!-- figure:fig-layer-distribution -->

**Figure 2:** Bar chart of core features (active in all 5/5 graphs) by layer group.

Cross-graph feature overlap analysis over the stable *(layer, feature index)* identifier space revealed a substantial shared circuit:

**Table 5:** Number of features surviving each cross-graph recurrence threshold.

| Threshold | Features Found |
|---|---|
| Active in ≥3/5 graphs | **490 features** |
| Active in ≥4/5 graphs | **210 features** |
| Active in all 5 graphs | **119 features** |

<!-- slide: Multi-step Reasoning Evidence -->

### 3.3 The Three-Group Analogical Reasoning Circuit

<!-- figure:fig-circuit-flow -->

**Figure 3:** Flow diagram of the three-group circuit, showing the input prompt, the representative features of Group 1, Group 2, and Group 3 with their Neuronpedia labels, and the model's output.

We provide evidence that Gemma-2-2B performs **genuine multi-step analogical reasoning internally**. The attribution graph reveals a three-group computational process that activates for both geographic and semantic role analogies — evidence of a domain-independence relational reasoning mechanism. This three-stage organization parallels the symbolic architecture identified by Webb et al. [9] through causal mediation analysis and the internal representation findings of Lee et al. [10].

---

**Group 1 · layers 0–4 · Circuit Template Parsing**

**Table 6:** The five Group 1 features and their Neuronpedia labels.

| Feature | Label |
|---|---|
| L0 SAE#11651 | *"the word 'to'"* |
| L1 SAE#11356 | *"the word 'to' followed by a verb"* |
| L2 SAE#11475 | *"the word 'refers' and related words"* |
| L4 SAE#10752 | *"uses of the verb 'to be' preceded by 'to'"* |
| L5 SAE#9672 | *"the phrase 'it is to'"* |

These features encode the syntactic skeleton of the analogy prompt. Their progression from individual tokens to multi-word patterns reflects hierarchical parsing of the relational connective. These are *structural* features — they fire on any text with this grammatical form, not specifically on analogical content.

---

**Group 2 · layers 5–9 · Analogy Recognition Hub**

**Table 7:** The four Group 2 features and their Neuronpedia labels, with L5 #5793 flagged as the dedicated analogy concept feature and L8 #13766 annotated with its activation count and average influence.

| Feature | Label |
|---|---|
| L5 SAE#5793 | *"analogies"* ← dedicated analogy concept feature |
| L5 SAE#2141 | *"comparisons of people or figures using well-known public figures"* |
| L8 SAE#13766 | *"analogies or comparisons"* (21 activations across 5 graphs, influence 0.533) |
| L9 SAE#13344 | *"phrases suggesting uncertainty or comparison between two things"* |

This is where circuit template processing gives way to semantic recognition of the *relational concept itself*. The presence of L5 SAE#5793, labeled "analogies" by Neuronpedia's automated SAE feature explanation system [8], is particularly significant: it activates consistently for both capital-city and semantic role analogies. It is not a geographic feature — it fires equally for "Doctor - hospital → teacher - ?". This is direct evidence of the kind of abstract relational representation that prior behavioral work [1, 11] has hypothesized but not directly observed inside a model.

---

**Group 3 · layers 10–13 · Relational Integration**

**Table 8:** The two Group 3 features and their Neuronpedia labels.

| Feature | Label |
|---|---|
| L11 SAE#15947 | *"references to historical or social change"* |
| L13 SAE#10969 | *"comparisons between disciplines and relationships between concepts"* |

L13 SAE#10969 serves an integrative role, combining the recognized relational structure from Group 2 with domain-specific knowledge to produce the final completion. layers 14–25 then handle domain-specific knowledge retrieval and output token formatting, analogous to the factual recall circuits identified by Meng et al. [2].

---

> **Note:** This diagram simplifies the true mechanisms considerably. The attribution graph for any single prompt contains hundreds of features; the circuit shown represents the semantically interpretable core.

<!-- slide: Feature Analysis -->

### 3.4 Top Recurring Features

**Table 9: Directly analogical features** (Neuronpedia labels explicitly reference analogical reasoning or comparison):

| Feature | Appearances | Avg Influence | Label |
|---|---|---|---|
| L5 #5793 | 11/5 | 0.590 | "analogies" |
| L8 #13766 | 21/5 | 0.533 | "analogies or comparisons" |
| L9 #13344 | 14/5 | 0.681 | "comparison between two things" |
| L5 #2141 | 12/5 | 0.647 | "comparisons of public figures" |
| L13 #10969 | 11/5 | 0.676 | "comparisons between disciplines" |

**Table 10: Circuit templates** (encode the "X is to Y as Z is to" scaffold):

| Feature | Appearances | Avg Influence | Label |
|---|---|---|---|
| L0 #11651 | 10/5 | 0.633 | "the word 'to'" |
| L1 #11356 | 10/5 | 0.609 | "'to' followed by a verb" |
| L2 #11475 | 10/5 | 0.638 | "the word 'refers'" |
| L4 #10752 | 10/5 | 0.626 | "'to be' preceded by 'to'" |
| L5 #9672 | 12/5 | 0.579 | "the phrase 'it is to'" |

**Table 11: High-recurrence formal text features** (labels unrelated to analogical reasoning):

| Feature | Appearances | Avg Influence | Label |
|---|---|---|---|
| L4 #14857 | 22/5 | 0.681 | "code snippets and license agreements" |
| L6 #2267 | 20/5 | 0.724 | "words in programming code, legal jargon, or scientific texts" |
| L3 #3205 | 20/5 | 0.670 | "code snippets and documentation references" |

These formal-text features have higher raw appearance counts than the explicitly analogical features. Causal steering (§3.7.6) confirms they are inert for all high-confidence circuits, consistent with their role as detectors of syntactic formality rather than relational semantics. The polysemanticity of neurons in large models [6] is precisely why SAE-based feature decomposition [5, 6, 7] is necessary to distinguish these classes of activation.

<!-- slide: Cross-Domain Generalization -->

### 3.5 Cross-Domain Generalization

<!-- figure:fig-venn -->

**Figure 4:** Venn diagram of feature overlap between capital analogies (Berlin, Rome, Tokyo) and semantic role analogies (Teacher, Bird), showing the 490-, 210-, and 119-feature recurrence thresholds and the two named analogy-concept features within the 119-feature core.

The consistent activation of L5 SAE#5793 ("analogies") and L8 SAE#13766 ("analogies or comparisons") across both capital-city and semantic role analogy types provides the most direct evidence for a **domain-general analogical reasoning mechanism**. The 119 features active in all five graphs form the stable intersection of the two analogy type families, and this intersection includes the core analogy-concept features at L5 and L8.

The slightly larger graphs for semantic role analogies (teacher, bird: 1,040–1,071 nodes) relative to capital analogies (Berlin, Rome, Tokyo: 905–963 nodes) may reflect that semantic role completions require broader world-knowledge access — knowing that teachers work in schools, or that birds inhabit air — rather than purely relational computation over a discrete, well-encoded geographic fact [2].

### 3.6 Circuit Stability Across Scaled and Syntactically Diverse Prompts

To validate that the shared circuit identified in §3.1 is not an artifact of using only five similar prompts, an extensive scaling experiment was performed. The central question: if we keep adding new analogical prompts — including versions phrased very differently from the original format — do the same features keep showing up?

The experiment generated attribution graphs for 50 prompts in total. Crucially, from the second batch onward, the prompts were not just new examples of the same template — they were rephrased into three syntactically distinct surface forms alongside the original:

**Table 12:** The four surface forms used in the scaling experiment, with an example prompt for each.

| Surface Form | Example |
|---|---|
| Standard X-to-Y | `Paris is to France as Berlin is to` |
| Diverse-A (Just as…) | `Just as Paris is the capital of France, Berlin is the capital of` |
| Diverse-B (Found in…) | `Doctors are found in hospitals. Teachers are found in` |
| Diverse-C (The way…) | `The way a fish lives in water, a bird lives in` |

These four forms look very different on the surface — different word order, different connectives, no shared "is to … as" string. If the circuit from §3.1 were merely tracking surface tokens, it would fall apart when these diverse forms were introduced.

At each milestone (N = 5, 10, 20, 30, 40, 50), the strictest possible threshold was applied: a feature must appear in **every single** attribution graph at that point.

**Table 13:** Number of features recurring across all N attribution graphs at each scaling milestone, and the drop from the previous milestone.

| N | Recurring features (k = ALL) | Drop from previous |
|---|---|---|
| 5 | **119** | — |
| 10 | **116** | −3 (−2.5 %) |
| 20 | **86** | −30 (−25.9 %) |
| 30 | **77** | −9 (−10.5 %) |
| 40 | **70** | −7 (−9.1 %) |
| 50 | **67** | −3 (−4.3 %) |

![Figure 5: Scaling curve showing the number of features that recur across ALL N attribution graphs as N grows from 5 to 50. The curve drops steeply at first — removing features that only appeared by coincidence in the small prompt set — then nearly plateaus, converging to a stable floor of 67 features.](scaling_curve.png)

The curve stays nearly flat from N = 5 to N = 10 (119 to 116), then contracts sharply from N = 10 to N = 20, losing 30 features (−25.9%) as the syntactically diverse prompts are introduced. These are features that had persisted across the template-only prompts by coincidence or through the shared "is to … as" string, and do not survive once the phrasing changes. From N = 20 onward the curve nearly plateaus: only 19 more features are lost across the next 30 prompts, and just 3 in the final step, so by N = 50 it has essentially stopped moving.
This settling is the key result. These 67 features appeared in every one of the 50 prompts. The prompts covered two different kinds of analogy (geographic and semantic) and four different ways of phrasing them, and a feature was only counted if it showed up in every single prompt. Features that appear by chance do not survive this kind of variation. So these 67 are not a coincidence. They are a real, stable set of features the model uses for analogies.

**The five directly analogical features all survive.** Within the 67-feature core, five features carry Neuronpedia labels that explicitly describe analogical or comparative reasoning. Every one of them appears in all 50 attribution graphs:

**Table 14:** The five directly analogical features that survive the full 50-prompt scaling filter, with their appearance counts, average influence, and Neuronpedia labels.

| Feature | Appearances | Avg. Influence | Label |
|---|---|---|---|
| L13 #10969 | 62 | 0.713 | "comparisons between disciplines and relationships between concepts" |
| L9 #13344 | 116 | 0.683 | "phrases suggesting uncertainty or comparison between two things" |
| L9 #14231 | 53 | 0.683 | "words representing comparisons and relationships" |
| L7 #749 | 80 | 0.652 | "analogies and comparisons" |
| L5 #2141 | 62 | 0.639 | "comparisons of people or figures using well-known public figures" |

Three of these — L13 #10969, L9 #13344, and L5 #2141 — were already identified in the original five-prompt analysis (§3.4). The scaling experiment adds two new ones: L9 #14231 ("words representing comparisons and relationships") and L7 #749 ("analogies and comparisons"), which only become visible once the prompt set is large and diverse enough to filter out coincidental co-activations. All five span the analogy recognition and relational integration groups (§3.4–3.5).

Despite the 50 prompts being phrased four different ways, the model consistently activated the same five semantic features. This confirms that the circuit is not reading a surface token pattern — it is recognising the underlying relational structure of an analogy, regardless of how that structure is expressed in words.

### 3.7 Causal Validation via Feature Steering

The preceding results are correlational. The attribution graphs indicate which features are active and influential when the model produces an answer, but not whether those features cause it. In this section we intervene on the features directly, suppressing and boosting them, to test whether the paper's structural findings hold causally.

Suppression is performed with the Neuronpedia steering API, which intervenes on a feature by adding a multiple of its direction to the residual stream at that feature's layer; a negative multiple pushes the feature's contribution down and thereby ablates it. The size of the push is set by a per-feature `strength`, which the API then scales by a global `strength_multiplier`. We used a strength of −20 and the default multiplier of 4, so the coefficient applied to each feature was −80. This is a large intervention: the core circuit features have typical activation magnitudes between roughly 1.5 and 16 (§2.4), so a −80 coefficient pushes them well outside their normal operating range and effectively removes them from the computation.

This magnitude governs how every result below should be read (§2.7). Because the intervention is strong, ablating any sufficiently large set of features disrupts the model, so the fact that the output changed does not by itself identify the responsible circuit. We therefore rely on two forms of discriminating evidence. The first is a matched contrast, in which ablation of the circuit is compared against ablation of a random feature set of the same size and strength. The second is a predicted failure mode, in which we ask whether the model fails in the specific way the circuit's hypothesized role implies rather than in an arbitrary way.

#### 3.7.1 Is the Recurring Circuit Causally Load-Bearing?

We tested whether the 180-feature shared circuit (§2.3) drives the answer or merely co-activates with it. For each prompt we ran two ablations of identical size (180 features) and strength (−20), differing only in which features were removed: (A) all 180 circuit features, and (B) 180 random non-circuit features drawn from the same prompt's graph (seed 7). Because the circuit is defined by its recurrence across the five prompts, we ran both ablations on all five.

We call condition (B) the *matched null*. It is a control group of features, built to match the circuit in every respect that could trivially disrupt the model — the same number of features (180), the same steering strength, and features drawn from the same attribution graph — but composed of randomly chosen features instead of the recurring circuit. Its purpose is to answer one question: is the circuit *specifically* responsible for the answer, or would removing any 180 features do the same? The matched null is the negative control, or placebo, against which condition (A) is measured. It stands for the null hypothesis that the circuit is not special, so the circuit earns a causal interpretation only if ablating it produces an effect that ablating the null does not.

If the circuit implements the analogical computation, removing it should leave the model unable to complete "X is to Y as Z is to ___." The model would then fall back on the template structure it can still represent and repeat the connective "to" rather than produce an answer. A random ablation has no reason to fail in this way.

| Prompt | Baseline: model's answer | (A) Ablate the circuit (180 feat.) | (B) Ablate a matched random set (180 feat.) |
|---|---|---|---|
| Paris - France → Berlin - ? | Germany (96%) | **to (97%)** | Kyrie (6%, a name) |
| Paris - France → Rome - ? | Italy (96%) | **to (97%)** | autorytatywna (44%, Polish) |
| Paris - France → Tokyo - ? | Japan (98%) | **to (97%)** | to (14%) |
| Doctor - hospital → teacher - ? | school (56%) | **to (97%)** | initComponents (45%, code) |
| Fish - water → bird - ? | air (8%) | **to (97%)** | espère (73%, French) |

*Table 15: How the two ablations fail. Both remove the model's correct answer, but ablating the circuit collapses every prompt to the same connective token "to" at ≈97% confidence, whereas ablating a matched random set produces a different idiosyncratic token each time (a name, a Polish word, a code identifier, a French word).*

Two observations follow. First, both ablations remove the correct answer on all five prompts, confirming that at this strength the removal of 180 features of any kind disrupts the model and that necessity alone does not distinguish the circuit from a random set. Second, the two ablations fail in different ways. Circuit ablation produces a near-deterministic collapse to the connective "to" at the same confidence on every prompt (97%), for both geographic and semantic-role analogies. The matched null, applied to the same prompts at the same strength, produces a different idiosyncratic out-of-distribution token on each prompt, with no token shared across prompts and lower average confidence (26%); only one null run (Tokyo) reaches "to," and only at 14% confidence versus the circuit's 97%. Because the removed feature set is the only variable differing between (A) and (B), the structured collapse is attributable to the circuit rather than to the size of the intervention.

One caveat should be stated directly. All five prompts end in the word "to" (for example, "…as Berlin is to"), and ablating the circuit makes the model output "to" — which is also the final word of the prompt. Two different explanations therefore predict the same token, and the output alone cannot separate them: the model may have lost the analogical computation and fallen back to the template connective "to" (the reading we intend), or it may simply be echoing the last word it was shown, as a broken model often does. What breaks the tie is the matched null, which faces the same "to"-final prompts but does not echo "to," emitting unrelated tokens instead. Ending in "to" is therefore not enough on its own to produce the collapse, so the effect is better explained by a loss of relational completion than by trivial token repetition.

We also examined the internal distribution of the effect by ablating each of the 180 features individually on the Berlin prompt. Only 24 of 180 features (13.3%) shift the prediction on their own, and these concentrate at the embedding layer (17 of 24 at L0; 42.5% of the L0 features tested, compared with 5.0% at L1 and above). The circuit is therefore internally redundant: necessity is a property of the set rather than of most individual members, and the individually necessary features are early template features such as L0/11651 ("the word 'to'").

#### 3.7.2 Robustness: Layer, Magnitude, and Generalization

We first considered whether the effect is only the deletion of L0 token features. Forty of the 180 features lie at L0, the embedding layer, so suppressing them approximates deleting the entity tokens. If this accounted for the full effect, ablating only the L0 features would remove the answer. It does not. Ablating the circuit one layer band at a time gives:

| Prompt | L0 only (40) | L1–L4 (67) | L5–L9 (50) | L10+ (23) | All non-L0 (140) |
|---|---|---|---|---|---|
| Berlin | ` Germany` ✓ | broke | broke | broke | broke |
| Rome | ` Italy` ✓ | broke | broke | broke | broke |
| Tokyo | ` Japan` ✓ | broke | broke | broke | broke |
| Bird | ` air` ✓ | broke (→ water) | broke | broke | broke |
| Teacher | broke | broke | broke | broke | broke |

*Table 16: Layer-band ablation of the circuit across the five prompts. Ablating only the 40 L0 embedding features leaves the answer intact on 4/5; the exception, teacher, has a weak baseline (p = 0.56).* Necessity is carried by the L1-and-above features, so the token-deletion explanation is insufficient: the causal weight lies in the relational mid- and late-layer features rather than the input-token representations. The bird prompt illustrates this further, in that L0 alone leaves "air" intact but the L1–L4 band reverts the answer to "water," the source-domain completion.

We next considered whether the effect is an artifact of the large −80 magnitude. A strength titration on Berlin and Tokyo sweeps the per-feature `strength` across −2, −5, −10, −20, and −40 — effective coefficients of −8 to −160 once the multiplier of 4 is applied — bracketing the −80 used above; the table below shows the two extremes:

**Table 17:** Model output and confidence for the circuit vs. matched-null ablation on the Berlin and Tokyo prompts, at the two extremes of the strength titration (per-feature −2 and −40).

| per-feature strength (effective) | Berlin circuit | Berlin null | Tokyo circuit | Tokyo null |
|---|---|---|---|---|
| −2 (−8) | to (97%) | similar (54%) | to (97%) | onPostExecute (33%) |
| −40 (−160) | to (97%) | similar (50%) | to (97%) | onPostExecute (30%) |

The collapse to "to" is already complete at the weakest setting tested (−2, an effective −8), and the circuit-versus-null distinction holds unchanged across the full 20× range. The effect is therefore not specific to the −80 intervention, though the flatness of the response across that range also indicates the behavioral readout saturates well below it.

Finally, we tested whether the circuit generalizes beyond its defining prompts. The 180 features were derived from five specific prompts. We applied the fixed circuit to three held-out analogies from which it was not derived:

**Table 18:** Baseline completions and circuit-ablation outputs for three held-out analogy prompts not used to derive the circuit.

| Held-out prompt | Baseline | Circuit ablation |
|---|---|---|
| Lisbon…Vienna is to | Austria | to (97%) |
| Athens…Oslo is to | Norway | to (97%) |
| Pen…knife is to | cutting | to (97%) |

The same collapse to "to" (97%) appears on all three prompts, indicating that the circuit signature is not specific to the defining set.

#### 3.7.3 The Three-Group Architecture

Sections 3.7.1 and 3.7.2 establish that the recurring circuit causally drives the model's answer, rather than merely co-occurring with it. A separate claim (§2.4) is that the circuit is organized into three groups. We tested this with group-level suppression of the representative features from each group, across all five prompts.

Suppressing the nine key group features one at a time (45 tests) shows that the Group 2 "analogy" features are individually redundant on high-confidence prompts. A Group 1 template feature, L0/11651 ("the word 'to'"), is individually necessary in four of five circuits: suppressing it makes the capital analogies emit the city name itself rather than complete the analogy.

Collective group suppression provides the main architecture test:

**Table 19:** Model output for each of the five prompts under collective suppression of the Group 2 features, the Group 1 features, and both groups combined.

| Experiment | Features | Berlin | Rome | Tokyo | Teacher | Bird |
|---|---|---|---|---|---|---|
| All Group 2 (4 feat.) | L5/5793, L5/2141, L8/13766, L9/13344 | **France** | **France** | **France** | be | fish |
| All Group 1 (5 feat.) | L0/11651, L1/11356, L4/10752, L5/9672, L2/11475 | (empty) | (empty) | (empty) | to | to |
| Group 1+2 (9 feat.) | All Group 1 + Group 2 | : | : | : | : | : |

*Collective group suppression at strength −20. Suppressing both groups together degenerates the output to bare punctuation on all five prompts. Full results: `graph-analysis/anish/exp7_remaining_analogy_validation/collective_steering_results.json`.*

Suppressing all four Group 2 features makes the three capital analogies output "France," the source country. The model retains the factual association "Paris is to France" but loses the relational transfer "as Berlin is to ___." This is the failure mode predicted if Group 2 implements relational transfer, and it is the strongest single piece of architecture evidence. Group 1 suppression produces a more severe failure, an empty output for the capital prompts, consistent with Group 1 being a prerequisite for Group 2. Together these results indicate an ordered hierarchy: Group 1 (template) precedes Group 2 (relational transfer), which precedes answer retrieval in the later layers.

#### 3.7.4 The Causal Validation Ledger

The interventions above bear on the paper's structural claims with different degrees of strength. Four claims meet the matched-contrast or predicted-failure-mode standard and we regard as demonstrated: that the 180 recurring features drive the analogy rather than ride along with it (§3.7.1); that the effect is not merely deletion of the L0 entity tokens (§3.7.2); that it is not an artifact of the −80 steering magnitude (§3.7.2); and that the circuit is organized into the ordered three-group hierarchy of §3.3, with the four Group 2 features collectively implementing relational transfer (§3.7.3). The dedicated analogy features at layers 5, 8, 9, and 13 participate causally as a group, although individually they are redundant.

Two further claims are supported but lack a full matched control. The circuit's collapse signature reproduces on three held-out analogies (§3.7.2) and on the two semantic-role prompts, extending the account across domains; the teacher and bird baselines are weak, however (the model is only 56% and 8% confident at baseline, and on the bird prompt " air" is only marginally the argmax, effectively tied with the blank-filling token " ____"), so cross-domain generalization rests on fewer confident cases than the geographic analogies. Finally, the high-recurrence formal-text features (§3.4) were not steered as a group and appear causally inert, so their role remains descriptive rather than demonstrated.

Three bounds should be stated explicitly:

1. **Sufficiency.** We show that the circuit is necessary and fails in the predicted way, but not that it is sufficient to produce the answer in isolation. The single-feature sufficiency probe, which boosts the highest-influence hub, is largely negative, inducing the target only when the target entity is already present in the prompt.
2. **Surgical necessity.** Because −80 is a strong intervention, single-feature necessity is layer-dependent, so the strongest claims rest on the matched contrast rather than on any individual ablation.
3. **Mediation.** The group experiments show that each group is collectively necessary, but establishing that information flows along the Group 1 → Group 2 edge requires path patching on the model weights, which the steering API does not expose. This remains future work.

Within these bounds, the steering evidence supports the paper's central structural claims: a recurring circuit that causally drives the answer across five prompts and three held-out analogies, not reducible to token deletion or to the intervention magnitude, organized into the three groups of §3.3, and shared between geographic and semantic-role analogies.

---

<!-- slide: Discussion -->

## 4. Discussion

### 4.1 The Analogical Reasoning Circuit in Gemma-2-2B

**Overall synthesis.** The results establish that Gemma-2-2B performs analogical reasoning through a stable, three-group distributed circuit rather than any single mechanism or layer. The convergence of structural, semantic, and causal evidence — across 218 steering experiments, a 50-prompt scaling study, cross-domain generalization testing, and held-out analogies — provides a mechanistic account at a level of specificity and causal resolution that prior behavioral work on LLM analogical reasoning could not reach. The core argument of this paper is not merely that recurring features exist, but that the recurring features identified through graph overlap are causally load-bearing, and that different groups of the circuit play functionally distinct and experimentally separable roles.

**The three-group architecture in context.** The three-group organization — structural template parsing (L0–L4), analogy recognition (L5–L9), and relational integration (L10–L13) — mirrors the abstract reasoning architecture documented by Webb et al. [9] through causal mediation analysis, where early layers abstract tokens into relational variables, intermediate layers perform induction over those variables, and later layers retrieve answers. The present results extend that framework in two important ways: by identifying specific SAE features at each group rather than working at the attention head level, and by providing direct causal evidence through feature steering that each group is collectively necessary for the circuit to function. Crucially, the group boundaries were not imposed a priori — they emerged from the content of Neuronpedia automated labels naturally clustering by layer depth, with a convergent gradient in activation magnitudes — rising from 1.5–6.4 in Group 1 to 9.1–16.3 in Group 3 (§2.4) — confirming the same partition through a second independent line of evidence.

This is qualitatively distinct from multi-hop factual reasoning. Analogical reasoning requires extracting an unnamed relation type, holding it as a variable, and applying it to a new argument pair. The Group 2 collective suppression experiment demonstrates that this extraction and transfer are implemented by identifiable internal components whose removal causes the model to echo the source-pair answer rather than transfer the relation — consistent with the "missing relational information" failure mode documented by Lee et al. [10] at the behavioral level. Our work provides a feature-level causal account of this phenomenon.

Prior behavioral evidence [1] established that LLMs can match human performance on analogical tasks; Webb et al. [9] identified emergent symbolic mechanisms supporting abstract reasoning through causal mediation of attention heads. The present work extends these findings to the SAE feature level: the relational reasoning primitive is not just a pattern of attention head behavior but a specifically labeled feature that plays a causal role in the SAE's learned decomposition of residual stream activations.

### 4.2 Circuit Stability Across Scaling and Surface Forms

**Circuit stability across surface forms.** Perhaps the most theoretically significant finding outside the steering results is the convergence of the feature set to a stable 67-feature core across 50 prompts phrased in four syntactically distinct surface forms (§3.6). The initial 119-feature circuit, identified from five prompts sharing the "X is to Y as Z is to" template, is nearly unchanged through N = 10 before contracting sharply — losing 33 features (28%) by N = 20 — but then plateaus, with only 19 further features lost across the subsequent 30 prompts, and just 3 in the final step. This two-phase scaling behaviour has a clear interpretation: the first contraction eliminates features that were coincidental artifacts of the shared surface template, while the plateau identifies features that activate because of the underlying relational structure, regardless of how that structure is expressed in words. All five directly analogical features survive the full 50-prompt filter. This is strong evidence against a surface-token explanation of the circuit and in favour of a genuine, abstract relational representation inside the model — independent evidence from the same direction as the held-out-prompt generalization result in §3.7.2.

**Cross-domain generalization.** The cross-domain generalization finding reinforces this interpretation. The shared circuit — and the stable 67-feature core — includes features that activate for both geographic capital analogies and semantic role analogies. The analogy-concept features at L5 and L8 fire equally for "Paris is to France as Berlin is to" and for "Doctor is to hospital as teacher is to", despite these prompts sharing no surface tokens related to analogy. This is consistent with the behavioral finding of Wijesiriwardene et al. [11] that LLMs encode relational information in a domain-general manner, and constitutes the first identification of specific internal features implementing that domain-generality at the feature level. The slightly larger attribution graphs for semantic role analogies (1,040–1,071 nodes) relative to capital analogies (905–963 nodes) may reflect that semantic roles require broader world-knowledge access rather than retrieval of a discrete, well-encoded fact — an interpretation consistent with the ROME findings of Meng et al. [2] on the compactness of factual storage for geographic entities.

### 4.3 The Role of Formal Text Features

The high-recurrence "code and legal text" features present an interpretive puzzle best understood through the lens of polysemanticity and superposition [6]. Two complementary explanations:

**Functional hypothesis:** These features detect formal, template-driven text patterns generally. The analogy syntax "X is to Y as Z is to" is highly structured, resembling legal definitions, code comments, and mathematical notation. The model reuses a general "formal syntax" detector.

**Training data hypothesis:** The analogy format appears frequently in SAT preparation and educational materials — which also contain code examples and legal definitions — creating a statistical association between formal-text features and analogy-completion contexts.

Both are compatible with the causal steering data. The formal features process the syntactic surface of the template while the analogy features process the relational semantics; only the latter are collectively necessary for relational transfer. The SAE-based decomposition [5, 6] is what makes this functional distinction visible — raw neuron activations would not cleanly separate these roles.

### 4.4 Comparison with the Capital City Recall Circuit

Comparison with the capital city *factual recall* circuit (prompt: "The capital of X is") reveals:

- **Overlap:** Formal-text features (L4/#14857, L6/#2267) appear with high frequency in both circuits, activated by the formal definitional structure of both prompt types. This is analogous to the shared MLP modules Meng et al. [2] identified across different factual recall tasks.
- **Divergence:** The L5 "analogies" feature and L8 "analogies or comparisons" feature appear to be specific to the analogical task — they were not among the top recurring features in the factual recall circuit — supporting the interpretation that these features are selectively activated by relational structure recognition.

### 4.5 Relation to Anthropic's Attribution Graph Methodology

The present work is in direct methodological continuity with Anthropic's *On the Biology of a Large Language Model* [12], which applied attribution graphs to Claude 3.5 Haiku using cross-layer transcoders. Both papers find that models implement multi-step, staged computation rather than direct input-to-output pattern matching, and both validate circuit hypotheses through feature steering. Anthropic's paper groups related features into manually curated "supernodes" to present a cleaner narrative; the present work uses automated cross-graph intersection, which is more scalable and less susceptible to confirmation bias but produces a less narratively refined picture of any single circuit. The two approaches are complementary.

### 4.6 Redundancy as a Property of Well-Learned Computation

Single-feature ablation of the 180-feature circuit leaves the Berlin prediction intact in 156/180 cases (§3.7.1): necessity is a property of the *set*, not of most individual members, and the few individually necessary features concentrate at the embedding layer. Yet the circuit is collectively decisive — removing it collapses every prompt to the analogy template, while a size- and strength-matched random ablation does not. This combination — individually redundant, collectively necessary — suggests well-learned associations are protected by redundant parallel encodings rather than single critical features. It aligns with the circuit redundancy findings in [12] and may reflect a general property of how transformers distribute robust computations across many partially-redundant components.

---

<!-- slide: Limitations & Future Work -->

## 5. Limitations

1. **SAE-feature-level intervention only.** Steering operates at the SAE feature level, not the attention head or residual stream level. The causal role of non-SAE circuit components is not assessed.
2. **SAE coverage.** The `gemmascope-transcoder-16k` SAE [7] covers only cross-layer transcoder features. Attention head contributions and residual stream features are not captured.
3. **Threshold sensitivity.** Results are sensitive to node and edge thresholds (0.80/0.85). Lower thresholds would reveal more features; higher thresholds would produce sparser, more focused circuits.
4. **Label quality.** Neuronpedia [8] automated feature explanations are LLM-generated and may not perfectly capture feature semantics.
5. **Prompt set size.** Five defining prompts (plus three held-out) are sufficient for circuit identification and a generalization check but too few to claim statistical robustness. A larger prompt set covering arithmetic, cross-lingual, and abstract relational analogies [13] would strengthen conclusions.
6. **Sufficiency not established.** The steering evidence shows the circuit is necessary and fails in the predicted way, but not that it is *sufficient* to produce the answer in isolation. The single-feature sufficiency probe is largely negative — the highest-influence hub induces the target only when the target entity is already present in the prompt.
7. **Large-magnitude intervention.** Steering at effective −80 per feature is a strong perturbation; the strongest claims rest on the circuit-vs-matched-null contrast and on the strength titration (the effect is already present at effective −8), not on any single surgical ablation. Establishing edge-level mediation (Group 1 → Group 2) requires activation/path patching on the model weights, which the steering API does not expose.

**Future work:** activation patching at the attention head level, replication with benchmark prompt sets, and cross-model comparison.

---

<!-- slide: Conclusions -->

## 6. Conclusions

We have identified a shared analogical reasoning circuit in Gemma-2-2B comprising 119 features active across five initial prompts, converging to a stable 67-feature core across 50 prompts phrased in four syntactically distinct surface forms. The circuit is organized into three groups: Group 1 (L0–L4) parses the structural format of the analogy prompt; Group 2 (L5–L9) recognises the relational concept itself through features explicitly labeled "analogies" and "analogies or comparisons"; and Group 3 (L10–L13) integrates the relation with domain-specific knowledge. The same core features activate for both geographic capital analogies and semantic role analogies, confirming a domain-agnostic relational reasoning mechanism rather than separate topic-specific circuits.

1. **A stable shared circuit exists, identified by common feature IDs.** 119 features — identified by stable *(layer, feature index)* pairs — appear in all five independently generated attribution graphs.
2. **Dedicated analogy features exist at layers 5, 8, 9, and 13.** These features have Neuronpedia explanations explicitly referencing analogies, comparisons, and relational concepts — providing direct SAE-level evidence of interpretable analogy-concept features in a large language model.
3. **The circuit exhibits a three-group architecture, identified by label semantics and validated causally.** Circuit template parsing (L0–L4), analogy recognition (L5–L9), and relational integration (L10–L13), with activation magnitude increasing through the sequence.
4. **Cross-domain generalization is confirmed.** The same core features, including L5 SAE#5793 ("analogies"), activate for both geographic and semantic role analogies — a domain-agnostic relational reasoning primitive consistent with behavioral findings [1, 10, 11].
5. **Group 2 implements relational transfer, collectively but not individually.** Simultaneous suppression collapses every circuit; capital analogies revert to the source-pair answer.
6. **The validation is robust to the obvious confounds.** Ablating the circuit — but not a matched random control — collapses all five prompts to the analogy template; the effect survives excluding the embedding layer (so it is not mere token deletion), holds from the weakest steering strength tested, and reproduces on held-out analogies the circuit was never derived from. Sufficiency and edge-level mediation remain open (§5).

---

## Attribution Graphs

The five Neuronpedia attribution graphs generated for this study are publicly available for interactive exploration. Full graph descriptions, inference prompts, and the agent pipeline methodology are documented in the [Supplementary Material](supplementary.html).

**Table 20:** The five prompts and links to their corresponding live Neuronpedia attribution graphs.

| Prompt | Neuronpedia Graph |
|--------|------------------|
| Paris is to France as Berlin is to | [analog\_berlin](https://www.neuronpedia.org/gemma-2-2b/graph?slug=analog_berlin) |
| Paris is to France as Rome is to | [analog\_rome](https://www.neuronpedia.org/gemma-2-2b/graph?slug=analog_rome) |
| Paris is to France as Tokyo is to | [analog\_tokyo](https://www.neuronpedia.org/gemma-2-2b/graph?slug=analog_tokyo) |
| Doctor is to hospital as teacher is to | [analog\_teacher](https://www.neuronpedia.org/gemma-2-2b/graph?slug=analog_teacher) |
| Fish is to water as bird is to | [analog\_bird](https://www.neuronpedia.org/gemma-2-2b/graph?slug=analog_bird) |

---

## References

[1] Webb, T., Holyoak, K.J., & Lu, H. (2023). Emergent analogical reasoning in large language models. *Nature Human Behaviour*, 7, 1526–1541. arXiv: https://arxiv.org/abs/2212.09196

[2] Meng, K., Bau, D., Andonian, A., & Belinkov, Y. (2022). Locating and editing factual associations in GPT. *NeurIPS 2022*. https://arxiv.org/abs/2202.05262

[3] Wang, K., Variengien, A., Conmy, A., Shlegeris, B., & Steinhardt, J. (2022). Interpretability in the wild: a circuit for indirect object identification in GPT-2 small. *ICLR 2023*. https://arxiv.org/abs/2211.00593

[4] Conmy, A., Mavor-Parker, A., Lynch, A., Heimersheim, S., & Garriga-Alonso, A. (2023). Towards automated circuit discovery for mechanistic interpretability. *NeurIPS 2023*. https://arxiv.org/abs/2304.14997

[5] Cunningham, H., Ewart, A., Riggs, L., Huben, R., & Sharkey, L. (2023). Sparse autoencoders find highly interpretable features in language models. *ICLR 2024*. https://arxiv.org/abs/2309.08600

[6] Bricken, T., Templeton, A., Batson, J., Chen, B., Jermyn, A., Conerly, T., et al. (2023). Towards monosemanticity: Decomposing language models with dictionary learning. *Transformer Circuits Thread*. https://transformer-circuits.pub/2023/monosemantic-features

[7] Lieberum, T., Rajamanoharan, S., Conmy, A., Smith, L., Sonnerat, N., Varma, V., Kramár, J., Dragan, A., Shah, R., & Nanda, N. (2024). Gemma Scope: Open sparse autoencoders everywhere all at once on Gemma 2. https://arxiv.org/abs/2408.05147

[8] Lin, J., & Bloom, J. (2023). Neuronpedia: Interactive platform for sparse autoencoder research and feature steering. https://www.neuronpedia.org

[9] Webb, T.W., Frankland, S.M., Altabaa, A., Segert, S., Krishnamurthy, K., Campbell, D., Russin, J., Giallanza, T., O'Reilly, R., Lafferty, J., & Cohen, J.D. (2025). Emergent symbolic mechanisms support abstract reasoning in large language models. https://arxiv.org/abs/2502.20332

[10] Lee, T., et al. (2025). The curious case of analogies: Investigating analogical reasoning in large language models. https://arxiv.org/abs/2511.20344

[11] Wijesiriwardene, T., et al. (2025). Analogical reasoning inside large language models: Concept vectors and the limits of abstraction. https://arxiv.org/abs/2503.03666

[12] Lindsey, J., Gurnee, W., Ameisen, E., Chen, B., Pearce, A., Turner, N.L., et al. (2025). On the biology of a large language model. *Transformer Circuits Thread*. https://transformer-circuits.pub/2025/attribution-graphs/biology.html

[13] Turney, P.D. (2006). Similarity of semantic relations. *Computational Linguistics*, 32(3), 379–416. [Foundational work on relational similarity benchmarks underlying analogy tasks.]

[14] Allen, C., & Hospedales, T. (2019). Analogies explained: Towards understanding word embeddings. *ICML 2019*. https://arxiv.org/abs/1901.09813

[15] Marks, S., Rager, C., Michaud, E.J., Belinkov, Y., Bau, D., & Mueller, A. (2024). Sparse feature circuits: Discovering and editing interpretable causal graphs in language models. https://arxiv.org/abs/2403.19647

---

## Supplementary Materials

**Interactive Presentation:** 20-slide reveal.js presentation with circuit flow diagrams, feature tables, and layer-by-layer analysis.  
https://kkrampis.github.io/autocircuit/presentation.html

**Live Attribution Graphs:**

- [`analog_berlin`](https://www.neuronpedia.org/gemma-2-2b/graph?slug=analog_berlin) — Paris - France → Berlin - ?
- [`analog_rome`](https://www.neuronpedia.org/gemma-2-2b/graph?slug=analog_rome) — Paris - France → Rome - ?
- [`analog_tokyo`](https://www.neuronpedia.org/gemma-2-2b/graph?slug=analog_tokyo) — Paris - France → Tokyo - ?
- [`analog_teacher`](https://www.neuronpedia.org/gemma-2-2b/graph?slug=analog_teacher) — Doctor - hospital → teacher - ?
- [`analog_bird`](https://www.neuronpedia.org/gemma-2-2b/graph?slug=analog_bird) — Fish - water → bird - ?

**Code:** https://github.com/kkrampis/autocircuit

---

```bibtex
@article{alagbe2026analogical,
  title   = {Mechanistic Interpretability of Analogical Reasoning in {Gemma-2-2B}:
             A Sparse Autoencoder Attribution Graph Analysis},
  author  = {Alagbe, Olalekan and Lawrence, Joseph and Maheshwar, Anish and Krampis, Konstantinos},
  year    = {2026},
  month   = {March},
  note    = {Neuronpedia API \texttt{gemmascope-transcoder-16k} SAE analysis}
}
```
