import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "rerun_corrected_analysis.py"
SPEC = importlib.util.spec_from_file_location("corrected_overlap_analysis", MODULE_PATH)
TOOLS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TOOLS)


def make_graph(slug, occurrences):
    return {
        "metadata": {"slug": slug},
        "nodes": [
            {
                "node_id": f"5_5793_{context_index}",
                "layer": 5,
                "feature": 5793,
                "feature_type": "cross layer transcoder",
                "influence": influence,
                "activation": activation,
            }
            for context_index, influence, activation in occurrences
        ],
        "links": [],
    }


def test_repeated_contexts_in_one_graph_do_not_count_as_multiple_graphs():
    berlin = make_graph(
        "analog_berlin",
        [(index, 0.5, 10.0) for index in range(5)],
    )

    features, thresholds = TOOLS.corrected_overlap({"berlin": berlin})

    assert features[0]["graph_count"] == 1
    assert thresholds["5"] == []


def test_threshold_counts_distinct_graphs_and_preserves_occurrence_count():
    berlin = make_graph("analog_berlin", [(1, 0.2, 4.0), (4, 0.6, 8.0)])
    rome = make_graph("analog_rome", [(1, 0.8, 12.0)])
    tokyo = make_graph("analog_tokyo", [(1, 0.4, 10.0), (6, 0.4, 14.0)])

    _, thresholds = TOOLS.corrected_overlap(
        {"berlin": berlin, "rome": rome, "tokyo": tokyo}
    )
    result = thresholds["3"]

    assert len(result) == 1
    feature = result[0]
    assert feature["graph_count"] == 3
    assert feature["occurrence_count"] == 5
    assert feature["graph_slugs"] == [
        "berlin",
        "rome",
        "tokyo",
    ]
    # Per-graph means are 0.4, 0.8, and 0.4, so prompts receive equal weight.
    assert feature["avg_influence"] == 0.533333
    assert feature["avg_activation"] == 10.0


def test_mapping_keys_keep_independent_graphs_distinct():
    graph_a = make_graph(None, [(1, 0.2, 4.0)])
    graph_b = make_graph(None, [(1, 0.8, 12.0)])

    features, _ = TOOLS.corrected_overlap({"graph_a": graph_a, "graph_b": graph_b})
    result = [
        feature
        for feature in features
        if feature["graph_count"] >= 2
    ]

    assert len(result) == 1
    assert result[0]["graph_count"] == 2
    assert result[0]["graph_slugs"] == ["graph_a", "graph_b"]
