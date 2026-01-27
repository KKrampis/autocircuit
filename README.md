# AutoCircuit: Automated Discovery of Interpretable Reasoning Patterns in Large Language Models

Project no.24 in [AI Safety Camp 2025](https://www.aisafety.camp/)

## Summary

This project systematically discovers interpretable reasoning circuits in large language models by data mining attribution graphs from Neuronpedia's circuit tracer, based on [Anthropic's circuit tracing publication](https://transformer-circuits.pub/2025/attribution-graphs/methods.html).

Our approach uses LLM agents to automatically collect, process, and analyze attribution graphs across diverse prompt categories. The system identifies recurring subgraph patterns that represent stable computational circuits—reusable reasoning pathways that models consistently employ across similar tasks.

### Key Components

1. **Automated graph collection** via Neuronpedia's API across systematically varied prompts
2. **Graph simplification** to extract core computational structures while filtering noise
3. **Pattern recognition** to identify circuit motifs across multiple contexts
4. **Validation** through targeted interventions on discovered circuits

## Project Structure

```
autocircuit/
├── graph_analysis/          # Analysis tools for Neuronpedia graphs
│   ├── circuit_analysis.py  # Structure analysis
│   ├── analyze_hubs.py      # Hub node detection
│   ├── top_n_nodes.py       # Node sampling by metric
│   ├── do_subgraph_save.py  # Save subgraphs to API
│   ├── utils/               # Shared utilities
│   └── api/                 # API interaction code
├── .claude/skills/          # Agent skills for Claude Code
│   └── neuronpedia-graph/   # Graph analysis skill
└── .tmp/graphs/             # Downloaded graph JSON files
```

## Quick Start

```bash
# Analyze a graph
python -m graph_analysis.circuit_analysis --graph_file .tmp/graphs/your-graph.json --tasks print_metadata analyze_supernodes

# Find hub nodes
python -m graph_analysis.analyze_hubs --graph_file .tmp/graphs/your-graph.json --tasks total_degree weighted_in
```

For detailed usage, see the `neuronpedia-graph` skill in `.claude/skills/`.

## Project Plan

### Phase 1: Automated Circuit Discovery
Implement automated feature interpretation using cross-layer transcoder methodology. Validate through feature patching interventions using [Neuronpedia's steering API](https://www.neuronpedia.org/api-doc#tag/steering).

### Phase 2: Systematic Circuit Validation
Mine attribution graphs to identify multi-step causal chains. Use LLM agents to analyze adjacency matrix patterns and propose circuit hypotheses. Upload pruned graphs to Neuronpedia for collaborative annotation.

### Phase 3: Cross-Model Pattern Analysis
Compare attribution graphs across model architectures to identify universal computational patterns. Implement monitoring for deviations from baseline circuit patterns.

## Scope

**Included:**
- Automated feature annotation using attribution graph analysis
- Circuit discovery and hypothesis generation
- Validation through mechanistic interventions
- Cross-model comparison for safety-relevant patterns
- Integration with Neuronpedia and circuit-tracer

**Excluded:**
- New transcoder training methodologies
- Novel model architectures
- Regulatory policy development
- Non-transformer architectures

## Output

All discovered circuits will be published on Neuronpedia. Code is open source under MIT License. Research paper planned for submission.

## Team

**Project Lead:** Konstantinos Krampis ([CV](https://kkrampis.github.io/blog/curriculum-vitae/index.html))

**Size:** 3-5 people, EST/CET timezone, minimum 10 hours/week

**Skills:** Python, APIs, graph data structures. Familiarity with [TransformerLens](https://transformerlensorg.github.io/TransformerLens/), [Anthropic papers](https://transformer-circuits.pub/), or [Neel Nanda's guides](https://www.neelnanda.io/mechanistic-interpretability/quickstart-old) helpful.

## Resources

- [Anthropic Circuit Tracing](https://transformer-circuits.pub/2025/attribution-graphs/methods.html)
- [Neuronpedia API](https://www.neuronpedia.org/api-doc)
- [Neuronpedia Graph Visualization](http://neuronpedia.org/gemma-2-2b/graph)

## License

MIT License - see [LICENSE](LICENSE) for details.
