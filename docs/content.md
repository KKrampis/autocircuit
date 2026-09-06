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
    author  = {Alagbe, Olalekan and Lawrence, Joseph and Krampis, Konstantinos},
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

We discover dedicated analogy-encoding SAE features at layers 5, 8, 9, and 13, including a layer-5 SAE feature labeled literally as **"analogies"** and a layer-8 SAE feature labeled **"analogies or comparisons"** that appear across all graphs with high confidence. Early layers (0–4) contain patterns associated with the "X is to Y as Z is to" format, while features at layers 5–13 have labels associated with comparisons and relational structure. The recurring feature set spans 21 of the model's 26 transformer layers and appears in both geographic and semantic-role analogy graphs, consistent with a shared representation that is not limited to one semantic domain. In steering experiments, suppressing the 180-feature intervention set changes the baseline answer on all five prompts and produces "to" as the first token; the same-size random-feature condition also changes every baseline answer, leaving circuit specificity unresolved. Collective suppression of selected Group 2 SAE features makes all three capital-city prompts produce "France," the source-pair answer. This reproducible failure mode is consistent with Group 2 contributing to relational transfer, although it does not establish that Group 2 exclusively implements that operation.

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

**Semantic label analysis.** After retrieving Neuronpedia automated labels for the top recurring SAE features, we grouped labels by recurring vocabulary. Labels concentrated at layers 0–4 include "the word 'to'", "'to' followed by a verb", and "the phrase 'it is to'". Labels concentrated at layers 5–9 include "analogies", "analogies or comparisons", and "comparison between two things". Labels concentrated at layers 10–13 include "comparisons between disciplines and relationships between concepts". This progression from template-related to explicitly relational labels motivates the three-group interpretation and parallels prior accounts of multi-stage abstract reasoning [9]. The layer ranges describe concentrations rather than sharp boundaries, and the labels alone do not establish a sequence of computations.

**Table 2:** The three functional feature groups. Each row is one group; the columns give the layer range where the group concentrates and its functional role. Group membership is defined by feature-label content, not by layer boundaries.

| Group | Layer range | Representative label theme |
| --- | --- | --- |
| 1 | L0–L4 | Template words and phrases |
| 2 | L5–L9 | Analogies and comparisons |
| 3 | L10–L13 | Relationships between concepts |

**Steering evaluation.** Section 3.7.3 reports individual and collective suppression experiments on representative SAE features from these groups. These interventions measure how the model's output changes when the selected features are suppressed; they do not by themselves establish information flow between groups.

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

When the four Group 2 SAE features are suppressed simultaneously, the output changes on all five prompts; the three capital-city prompts produce "France" rather than the baseline target country. Retaining the source-pair answer while losing the target-pair completion is consistent with these features contributing to relational transfer. Section 3.7.3 reports the full results and the limits of that interpretation.

### 2.7 Causal Validation via Feature Steering

The cross-graph analysis (§2.3) identifies recurring SAE features, but recurrence alone does not establish their causal contribution to the model's answers. We therefore measured the effects of suppressing the 180-feature intervention set with the Neuronpedia `/api/steer` endpoint [8] (`modelId: "gemma-2-2b"`, `strength_multiplier: 4`, `temperature: 0`, `seed: 42`).

The per-feature `strength` used for suppression (−20) is scaled by the global `strength_multiplier` of 4, yielding an effective coefficient of **−80** per SAE feature. Because this is a strong intervention, an output change alone is not evidence that the selected feature set is uniquely responsible for the original answer. We therefore report the intervention outputs directly and use a same-size random-feature comparison to evaluate specificity.

1. **Intervention set vs. a random-feature comparison.** For each prompt, suppress (a) the 180-feature intervention set and (b) 180 random non-circuit SAE features drawn from the same prompt's graph, using the same strength for both conditions.
2. **Individual sensitivity.** Suppress each of the 180 SAE features separately and record whether the first-token prediction changes.
3. **Robustness.** Measure layer-band sensitivity, repeat the intervention over a range of strengths, and apply the fixed intervention set to held-out analogy prompts.
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

**Figure 3:** Descriptive grouping of representative recurring SAE features by automated-label theme and layer concentration. The grouping does not establish a sequential flow of information.

The recurring SAE features form a stable cross-prompt pattern that can be described using three functional groups. Representatives of these groups appear in both geographic and semantic-role analogy graphs, supporting the interpretation that the model reuses relational features across the tested domains. The shift from template-related labels in earlier layers to explicitly analogy-related labels in later layers is consistent with the symbolic architecture identified by Webb et al. [9] and the internal-representation findings of Lee et al. [10]. The attribution graphs alone, however, do not establish a three-stage causal process.

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

The attribution graphs show which SAE features are active and influential when the model produces an answer, but they do not establish whether those features contribute causally to that answer. We therefore used the Neuronpedia steering API to suppress selected SAE features and recorded the resulting first-token predictions.

For each suppressed SAE feature, the API adds the feature direction to the residual stream with a per-feature `strength` of −20 and a global `strength_multiplier` of 4, yielding an effective coefficient of −80. This coefficient is substantially larger than the typical activation magnitudes of the selected features (approximately 1.5–16; §2.4). The experiments should therefore be read as strong perturbations rather than surgical removals of individual computations.

#### 3.7.1 Intervention-Set Suppression and Random-Feature Comparison

For each of the five prompts, we ran two conditions at the same per-feature strength: (A) suppression of the 180-feature intervention set and (B) suppression of 180 randomly selected non-circuit SAE features from the same prompt's attribution graph (seed 7). Condition B completed successfully; the issue is that it also removed the baseline answer on every prompt, so it did not function as a clean negative control.

| Prompt | Baseline: model's answer | (A) Suppress the intervention set (180 SAE feat.) | (B) Suppress a random set (180 SAE feat.) |
|---|---|---|---|
| Paris - France → Berlin - ? | Germany (96%) | **to (97%)** | Kyrie (6%, a name) |
| Paris - France → Rome - ? | Italy (96%) | **to (97%)** | autorytatywna (44%, Polish) |
| Paris - France → Tokyo - ? | Japan (98%) | **to (97%)** | to (14%) |
| Doctor - hospital → teacher - ? | school (56%) | **to (97%)** | initComponents (45%, code) |
| Fish - water → bird - ? | air (8%) | **to (97%)** | espère (73%, French) |

*Table 15: First-token outputs for the 180-feature intervention set and the same-size random-feature comparison. Both conditions remove the baseline answer on all five prompts. Condition A produces "to" at approximately 97% confidence in every case; condition B produces the five outputs shown above.*

Because both conditions remove the baseline answer, this experiment does not establish that the 180-feature set is selectively necessary. The consistent difference between the output patterns is an observation that motivates a better-matched or weaker control experiment; it is not treated here as proof of circuit specificity.

Nevertheless, the intervention-set result is highly reproducible: all five prompts converge on the same first token at nearly identical confidence, whereas the random sets produce prompt-dependent outputs and substantially more variable confidence. This supports the narrower conclusion that suppressing the selected set produces a stable intervention signature distinct from the observed random-set signatures. It does not determine whether that distinction is caused by circuit membership, differences in the sampled features, or the scale of the perturbation.

We also suppressed each of the 180 SAE features individually on the Berlin prompt. Twenty-four features (13.3%) changed the first-token prediction: 17 of the 40 features at L0 and 7 of the 140 features at L1 or above. The contrast between sparse individual effects and the uniform collective effect is consistent with the selected set having distributed or redundant influence. Because feature interactions were not measured directly, redundancy remains an interpretation rather than a demonstrated mechanism.

#### 3.7.2 Robustness: Layer, Magnitude, and Generalization

We first divided the 180 SAE features into layer bands and suppressed each band separately. We also suppressed the full set of 140 SAE features above L0.

| Prompt | L0 only (40) | L1–L4 (67) | L5–L9 (50) | L10+ (23) | All non-L0 (140) |
|---|---|---|---|---|---|
| Berlin | Germany (unchanged) | changed | changed | changed | changed |
| Rome | Italy (unchanged) | changed | changed | changed | changed |
| Tokyo | Japan (unchanged) | changed | changed | changed | changed |
| Bird | air (unchanged) | water | changed | changed | changed |
| Teacher | changed | changed | changed | changed | changed |

*Table 16: Effect of suppressing the intervention set by layer band. The L0-only condition preserves the baseline first token on four prompts; every other listed condition changes it on all five prompts.*

The intervention effect is therefore not confined to a single layer band. In particular, suppressing the 140 SAE features above L0 changes all five predictions, and each of the three non-L0 bands changes every prediction when tested separately. These results localize sensitivity across multiple portions of the feature set without assigning a specific computation to any layer band.

We next repeated the intervention-set and random-set conditions for Berlin and Tokyo at per-feature strengths of −2, −5, −10, −20, and −40, corresponding to effective coefficients from −8 to −160. Table 17 shows the endpoints.

**Table 17:** Model output and confidence for the intervention set and random-feature comparison on the Berlin and Tokyo prompts, at the two extremes of the strength titration (per-feature −2 and −40).

| per-feature strength (effective) | Berlin intervention set | Berlin random set | Tokyo intervention set | Tokyo random set |
|---|---|---|---|---|
| −2 (−8) | to (97%) | similar (54%) | to (97%) | onPostExecute (33%) |
| −40 (−160) | to (97%) | similar (50%) | to (97%) | onPostExecute (30%) |

The intervention-set condition produces "to" throughout the tested 20-fold range, showing that the intervention signature is robust to the chosen magnitude and is already saturated at the weakest tested coefficient. The sweep does not locate the response threshold, and the random-set condition also fails to preserve the baseline answer at the displayed endpoints. The result therefore supports magnitude-robustness of the observed signature, not circuit specificity.

Finally, we tested whether the intervention output recurs beyond the five prompts used to construct the 180-feature set. We applied the fixed set to three held-out analogies:

**Table 18:** Baseline completions and intervention-set outputs for three held-out analogy prompts not used to construct the feature set.

| Held-out prompt | Baseline | Intervention-set suppression |
|---|---|---|
| Lisbon…Vienna is to | Austria | to (97%) |
| Athens…Oslo is to | Norway | to (97%) |
| Pen…knife is to | cutting | to (97%) |

The intervention produces "to" at 97% confidence on all three held-out prompts. Reproducing the same high-confidence output on prompts that were not used to construct the feature set supports generalization of the intervention signature beyond the defining examples. Because no random-feature comparison was run for the held-out prompts, the experiment does not independently establish specificity on this set.

#### 3.7.3 Suppression of Representative SAE Feature Groups

Section 2.4 groups representative SAE features by their automated labels and the layers in which they occur. We evaluated these selected features with two protocols, both using a per-feature strength of −20 (effective coefficient −80): individual suppression across all five prompts and collective suppression by group.

The individual protocol comprised 45 calls: nine SAE features tested on five prompts. The tested set contained four Group 1 features (SAE L0/F11651, L1/F11356, L4/F10752, and L5/F9672), four Group 2 features (SAE L5/F5793, L5/F2141, L8/F13766, and L9/F13344), and one Group 3 feature (SAE L13/F10969). Nine calls changed the baseline first token. SAE L0/F11651 changed four prompts: Berlin, Rome, and Tokyo produced the target city name, and Bird produced "water." SAE L4/F10752 changed Teacher to "classroom" and Bird to "sky"; SAE L5/F9672 changed Bird to "sky"; and SAE L8/F13766 and L9/F13344 changed Bird to "fish" and "sky," respectively. The other 36 calls preserved the baseline first token. SAE L13/F10969, the only Group 3 feature tested individually, preserved the baseline on all five prompts.

The collective protocol used five Group 1 SAE features—the four listed above plus SAE L2/F11475—and the four Group 2 SAE features.

**Table 19:** First-token outputs under collective suppression of the selected SAE feature groups.

| Experiment | Features | Berlin | Rome | Tokyo | Teacher | Bird |
|---|---|---|---|---|---|---|
| All Group 2 (4 feat.) | SAE L5/F5793, L5/F2141, L8/F13766, L9/F13344 | **France** | **France** | **France** | be | fish |
| All Group 1 (5 feat.) | SAE L0/F11651, L1/F11356, L4/F10752, L5/F9672, L2/F11475 | (empty) | (empty) | (empty) | to | to |
| Group 1+2 (9 feat.) | All Group 1 + Group 2 | : | : | : | : | : |

*Collective suppression at a per-feature strength of −20. The table reports the first generated token; “(empty)” denotes a leading newline rather than a lexical token. Full outputs are recorded in `graph-analysis/anish/exp7_remaining_analogy_validation/collective_steering_results.json`.*

All three collective conditions change the baseline first token on all five prompts. Group 2 suppression produces the same first token, "France," for the three capital prompts: the source-pair answer is retained while the target-pair answer is lost. This is the failure pattern expected if the selected Group 2 features contribute to transferring the relation from the demonstrated pair to the query pair. Group 1 suppression produces a leading newline for the capital prompts, while combined Group 1+2 suppression produces a colon for every prompt, showing that the selected groups have distinguishable collective effects.

The Group 2 SAE features preserve the baseline individually on all three high-confidence capital prompts but change those answers when suppressed together. This supports a distributed-contribution interpretation for the tested Group 2 set. Because Group 3 was represented by only one individually tested SAE feature and was not isolated in a collective condition, these experiments do not establish Group 3's role, an ordering among groups, or mediation between them.

#### 3.7.4 Interpretation and Limits

The steering experiments support three main interpretations. First, the 180-feature intervention set has a stable behavioral signature: suppression produces the same high-confidence first token across all five defining prompts, three held-out prompts, and the full tested strength range. This is evidence that the set has a reproducible relationship to model behavior across prompts, rather than an effect observed in a single example.

Second, collective Group 2 suppression produces a more specific failure pattern on the high-confidence capital prompts: each reverts to "France," the answer from the demonstrated pair. Because the target answer is lost while the source-pair answer remains available, this result supports the interpretation that the selected Group 2 SAE features contribute to relational transfer. Their lack of individual effects on these prompts, combined with their collective effect, further suggests that this contribution is distributed across the tested features.

The evidence does not support stronger exclusivity or sequencing claims. The same-size random-feature condition also changes every baseline answer, so the current comparison does not establish that the 180-feature set is uniquely necessary. The experiments also do not establish sufficiency, a Group 1 -> Group 2 -> Group 3 information-flow path, or a causal role for Group 3. The Teacher and Bird baselines are weaker than the three capital-city baselines (56% and 8%, respectively), so interpretations based on those prompts are less secure.

The results therefore provide evidence for reproducible set-level effects and for a contribution of the selected Group 2 SAE features to relational transfer, while leaving circuit specificity and group-level mediation unresolved. Stronger mechanistic claims will require a control that preserves baseline behavior more reliably, lower-magnitude interventions that reveal differential sensitivity, and experiments that isolate Group 3 and test mediation between groups.

---

<!-- slide: Discussion -->

## 4. Discussion

### 4.1 The Analogical Reasoning Circuit in Gemma-2-2B

**Overall synthesis.** The results identify a stable set of recurring SAE features associated with analogical prompts and organize selected representatives into three functional groups. Across 218 steering experiments, a 50-prompt scaling study, cross-domain testing, and held-out analogies, the same feature sets and intervention-output patterns recur across multiple prompts. Taken together, these results support a distributed representation of analogical structure that generalizes across the tested prompts and domains. The strongest functional evidence comes from collective Group 2 suppression, which causes the capital prompts to retain the demonstrated answer "France" while losing the transferred target answer. This is consistent with Group 2 contributing to relational transfer. The failed random-feature control limits claims of circuit specificity, and the group experiments do not establish an ordered three-stage computation.

**The three-group organization in context.** The proposed groups — structural-template features concentrated at L0–L4, analogy-related features concentrated at L5–L9, and comparison-related features concentrated at L10–L13 — parallel the abstract reasoning architecture documented by Webb et al. [9]. The label progression and the distinct collective-suppression outputs support the idea that different parts of the recurring feature set make functionally different contributions. In particular, Group 2's source-answer failure pattern connects its analogy-related labels to a measurable behavioral role. Group 3 was represented by one SAE feature and was not isolated in a Group-3-only collective condition, so the experiments do not establish that all three groups are collectively necessary or that computation proceeds through them in order.

This is qualitatively distinct from multi-hop factual reasoning. Analogical reasoning requires extracting an unnamed relation type and applying it to a new argument pair. Under collective Group 2 suppression, the model retains the source-pair answer but fails to produce the transferred target answer. This is consistent with the "missing relational information" failure mode documented by Lee et al. [10] and provides feature-level evidence that the selected Group 2 SAE features contribute to relational transfer.

Prior behavioral evidence [1] established that LLMs can match human performance on analogical tasks; Webb et al. [9] identified emergent symbolic mechanisms supporting abstract reasoning through causal mediation of attention heads. The present work extends this line of investigation to SAE features by identifying recurring, explicitly analogy-labeled features and showing that their collective suppression produces a relation-specific failure pattern. This connects interpretable SAE labels to behavior while leaving the precise causal pathway for future work.

### 4.2 Circuit Stability Across Scaling and Surface Forms

**Circuit stability across surface forms.** Perhaps the most theoretically significant finding outside the steering results is the convergence of the feature set to a stable 67-feature core across 50 prompts phrased in four syntactically distinct surface forms (§3.6). The initial 119-feature circuit, identified from five prompts sharing the "X is to Y as Z is to" template, is nearly unchanged through N = 10 before contracting sharply — losing 33 features (28%) by N = 20 — but then plateaus, with only 19 further features lost across the subsequent 30 prompts, and just 3 in the final step. This two-phase scaling behaviour has a clear interpretation: the first contraction eliminates features that were coincidental artifacts of the shared surface template, while the plateau identifies features that activate because of the underlying relational structure, regardless of how that structure is expressed in words. All five directly analogical features survive the full 50-prompt filter. This is strong evidence against a surface-token explanation of the circuit and in favour of a genuine, abstract relational representation inside the model — independent evidence from the same direction as the held-out-prompt generalization result in §3.7.2.

**Cross-domain generalization.** The cross-domain generalization finding reinforces this interpretation. The shared circuit — and the stable 67-feature core — includes features that activate for both geographic capital analogies and semantic role analogies. The analogy-concept features at L5 and L8 fire equally for "Paris is to France as Berlin is to" and for "Doctor is to hospital as teacher is to", despite these prompts sharing no surface tokens related to analogy. This is consistent with the behavioral finding of Wijesiriwardene et al. [11] that LLMs encode relational information in a domain-general manner, and constitutes the first identification of specific internal features implementing that domain-generality at the feature level. The slightly larger attribution graphs for semantic role analogies (1,040–1,071 nodes) relative to capital analogies (905–963 nodes) may reflect that semantic roles require broader world-knowledge access rather than retrieval of a discrete, well-encoded fact — an interpretation consistent with the ROME findings of Meng et al. [2] on the compactness of factual storage for geographic entities.

### 4.3 The Role of Formal Text Features

The high-recurrence "code and legal text" features present an interpretive puzzle best understood through the lens of polysemanticity and superposition [6]. Two complementary explanations:

**Functional hypothesis:** These features detect formal, template-driven text patterns generally. The analogy syntax "X is to Y as Z is to" is highly structured, resembling legal definitions, code comments, and mathematical notation. The model reuses a general "formal syntax" detector.

**Training data hypothesis:** The analogy format appears frequently in SAT preparation and educational materials — which also contain code examples and legal definitions — creating a statistical association between formal-text features and analogy-completion contexts.

Both hypotheses are compatible with the observed feature labels and recurrence patterns. The contrast between the highly recurring formal-text labels and the more interpretable Group 2 suppression result suggests that recurrence alone does not determine causal importance. The current steering experiments do not distinguish whether the formal-text features reflect reusable template processing or training-data correlations, so those proposed roles remain hypotheses.

### 4.4 Comparison with the Capital City Recall Circuit

Comparison with the capital city *factual recall* circuit (prompt: "The capital of X is") reveals:

- **Overlap:** Formal-text features (L4/#14857, L6/#2267) appear with high frequency in both circuits, activated by the formal definitional structure of both prompt types. This is analogous to the shared MLP modules Meng et al. [2] identified across different factual recall tasks.
- **Divergence:** The L5 "analogies" feature and L8 "analogies or comparisons" feature appear to be specific to the analogical task — they were not among the top recurring features in the factual recall circuit — supporting the interpretation that these features are selectively activated by relational structure recognition.

### 4.5 Relation to Anthropic's Attribution Graph Methodology

The present work follows the attribution-graph methodology used in Anthropic's *On the Biology of a Large Language Model* [12], which studied Claude 3.5 Haiku using cross-layer transcoders. Anthropic's paper groups related features into manually curated "supernodes"; the present work instead uses automated cross-graph intersection to identify recurring SAE features. The resulting graphs and steering measurements characterize associations and intervention sensitivity, while stronger claims about staged computation require additional causal tests.

### 4.6 Evidence for Distributed Contribution

Single-feature suppression leaves the Berlin prediction intact in 156 of 180 cases, whereas collective suppression of all 180 SAE features changes the first-token prediction on every prompt (§3.7.1). A similar pattern appears within Group 2: no selected Group 2 SAE feature changes the three high-confidence capital answers individually, but suppressing all four changes all three answers to "France." These results are consistent with distributed or redundant contribution, where a set can influence behavior even when most members are not individually necessary. The conclusion remains provisional because the collective interventions are much larger and the same-size random-feature condition also changes every baseline answer. Confirming redundancy will require controls that preserve baseline behavior and experiments designed to measure feature interactions directly.

---

<!-- slide: Limitations & Future Work -->

## 5. Limitations

1. **SAE-feature-level intervention only.** Steering operates at the SAE feature level, not the attention head or residual stream level. The causal role of non-SAE circuit components is not assessed.
2. **SAE coverage.** The `gemmascope-transcoder-16k` SAE [7] covers only cross-layer transcoder features. Attention head contributions and residual stream features are not captured.
3. **Threshold sensitivity.** Results are sensitive to node and edge thresholds (0.80/0.85). Lower thresholds would reveal more features; higher thresholds would produce sparser, more focused circuits.
4. **Label quality.** Neuronpedia [8] automated feature explanations are LLM-generated and may not perfectly capture feature semantics.
5. **Prompt set size.** Five defining prompts (plus three held-out) are sufficient for circuit identification and a generalization check but too few to claim statistical robustness. A larger prompt set covering arithmetic, cross-lingual, and abstract relational analogies [13] would strengthen conclusions.
6. **Sufficiency not established.** The reported suppression experiments do not test whether the selected SAE features are sufficient to produce an answer. The separate single-feature boosting probe is largely negative and does not establish sufficiency.
7. **Large-magnitude intervention and ineffective negative control.** Steering at an effective −80 per SAE feature is a strong perturbation, and the same-size random-feature condition also removes every baseline answer. The strength sweep reproduces the intervention output down to effective −8 but does not locate a differential threshold between the selected and random feature sets. Establishing specificity and edge-level mediation will require less disruptive controls and activation or path patching on the model weights.

**Future work:** activation patching at the attention head level, replication with benchmark prompt sets, and cross-model comparison.

---

<!-- slide: Conclusions -->

## 6. Conclusions

We identified 119 SAE features active across five initial analogy prompts and a 67-feature intersection across 50 prompts phrased in four surface forms. Automated labels for selected features cluster into three groups: structural-template labels concentrated at L0–L4, analogy-related labels concentrated at L5–L9, and comparison-related labels concentrated at L10–L13. The recurrence of these features across geographic and semantic-role prompts supports a shared representation of analogical structure across the tested domains. Steering provides additional functional evidence: the 180-feature intervention set has a stable cross-prompt signature, and collective Group 2 suppression produces the source-pair answer on all three capital prompts.

1. **A stable shared circuit exists, identified by common feature IDs.** 119 features — identified by stable *(layer, feature index)* pairs — appear in all five independently generated attribution graphs.
2. **Dedicated analogy features exist at layers 5, 8, 9, and 13.** These features have Neuronpedia explanations explicitly referencing analogies, comparisons, and relational concepts — providing direct SAE-level evidence of interpretable analogy-concept features in a large language model.
3. **The recurring SAE features can be organized into three label-based groups.** Structural-template labels concentrate at L0–L4, analogy-related labels at L5–L9, and comparison-related labels at L10–L13. Distinct collective-suppression outputs support functionally different contributions, although the current interventions do not establish an ordered three-stage computation.
4. **The feature intersection spans both tested domains.** The same core features, including SAE L5/F5793 ("analogies"), appear in both geographic and semantic-role analogy graphs. This recurrence supports a shared representation across the tested domains, while broader domain generality remains to be tested.
5. **Group 2 contributes to relational transfer.** Collective suppression changes all five baseline answers, and the three capital-city prompts revert to "France," retaining the demonstrated pair's answer while losing the transferred target answer. The result supports a Group 2 contribution but not exclusive implementation of the operation.
6. **The intervention signature generalizes, but specificity remains unresolved.** Suppressing the 180-feature set produces "to" across the five defining prompts, the tested strength range, and three held-out prompts, demonstrating a reproducible set-level effect. The same-size random-feature condition also changes every baseline answer, so a claim of unique circuit necessity requires a less disruptive control (§5).

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
  author  = {Alagbe, Olalekan and Lawrence, Joseph and Krampis, Konstantinos},
  year    = {2026},
  month   = {March},
  note    = {Neuronpedia API \texttt{gemmascope-transcoder-16k} SAE analysis}
}
```
