import os
import tempfile
import unittest
from unittest.mock import patch

import yaml

from graph_analysis.utils.intervention_types import Feature, Supernode, Intervention
from graph_analysis.utils.yaml_loader import (
    load_experiment_config,
    resolve_supernode_features,
    build_supernodes,
    resolve_graph_layout,
    resolve_interventions,
)


MINIMAL_CONFIG = {
    "model": {"name": "test-model", "transcoder": "test", "backend": "transformerlens"},
    "prompts": {"test_prompt": "Hello world"},
    "supernodes": {
        "node_a": {"features": [{"layer": 1, "pos": 0, "feature_idx": 100}]},
    },
    "experiments": {
        "exp1": {
            "prompt": "test_prompt",
            "initialize": {"test_prompt": ["node_a"]},
            "interventions": [{"actions": [{"node": "node_a", "scale": -2}]}],
        }
    },
}


def write_yaml(config: dict) -> str:
    """Write config to a temp YAML file and return the path."""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    with os.fdopen(fd, "w") as f:
        yaml.dump(config, f)
    return path


class TestLoadExperimentConfig(unittest.TestCase):
    def test_loads_valid_config(self):
        path = write_yaml(MINIMAL_CONFIG)
        try:
            config = load_experiment_config(path)
            self.assertIn("model", config)
            self.assertIn("experiments", config)
        finally:
            os.unlink(path)

    def test_rejects_missing_model(self):
        bad = {k: v for k, v in MINIMAL_CONFIG.items() if k != "model"}
        path = write_yaml(bad)
        try:
            with self.assertRaises(ValueError) as ctx:
                load_experiment_config(path)
            self.assertIn("model", str(ctx.exception))
        finally:
            os.unlink(path)

    def test_rejects_missing_experiments(self):
        bad = {k: v for k, v in MINIMAL_CONFIG.items() if k != "experiments"}
        path = write_yaml(bad)
        try:
            with self.assertRaises(ValueError) as ctx:
                load_experiment_config(path)
            self.assertIn("experiments", str(ctx.exception))
        finally:
            os.unlink(path)

    def test_rejects_missing_model_keys(self):
        bad = dict(MINIMAL_CONFIG)
        bad["model"] = {"name": "test"}  # missing transcoder, backend
        path = write_yaml(bad)
        try:
            with self.assertRaises(ValueError) as ctx:
                load_experiment_config(path)
            self.assertIn("transcoder", str(ctx.exception))
        finally:
            os.unlink(path)


class TestResolveSuperonodeFeatures(unittest.TestCase):
    def test_null_features_returns_none(self):
        result = resolve_supernode_features({"features": None}, {}, {})
        self.assertIsNone(result)

    def test_no_features_key_returns_none(self):
        result = resolve_supernode_features({}, {}, {})
        self.assertIsNone(result)

    def test_manual_features(self):
        sn_def = {
            "features": [
                {"layer": 23, "pos": 10, "feature_idx": 12237},
                {"layer": 19, "pos": 10, "feature_idx": 9209},
            ]
        }
        result = resolve_supernode_features(sn_def, {}, {})
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], Feature(23, 10, 12237))
        self.assertEqual(result[1], Feature(19, 10, 9209))

    @patch("graph_analysis.utils.yaml_loader.extract_supernode_features")
    def test_features_from_single_group(self, mock_extract):
        mock_extract.return_value = {
            "Texas": [Feature(20, 9, 15589), Feature(16, 9, 25)],
            "capital": [Feature(15, 4, 4494)],
        }
        sn_def = {"features_from": {"graph": "dallas", "groups": ["Texas"]}}
        graph_urls = {"dallas": "https://example.com/graph"}
        cache = {}

        result = resolve_supernode_features(sn_def, graph_urls, cache)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], Feature(20, 9, 15589))
        mock_extract.assert_called_once_with("https://example.com/graph")

    @patch("graph_analysis.utils.yaml_loader.extract_supernode_features")
    def test_features_from_merged_groups(self, mock_extract):
        mock_extract.return_value = {
            "California": [Feature(22, 10, 4367)],
            "California (2)": [Feature(6, 9, 13909), Feature(8, 9, 14641)],
        }
        sn_def = {"features_from": {"graph": "oakland", "groups": ["California", "California (2)"]}}
        graph_urls = {"oakland": "https://example.com/graph2"}
        cache = {}

        result = resolve_supernode_features(sn_def, graph_urls, cache)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], Feature(22, 10, 4367))
        self.assertEqual(result[1], Feature(6, 9, 13909))

    @patch("graph_analysis.utils.yaml_loader.extract_supernode_features")
    def test_features_from_uses_cache(self, mock_extract):
        mock_extract.return_value = {"Texas": [Feature(20, 9, 15589)]}
        graph_urls = {"dallas": "https://example.com/graph"}
        cache = {}

        sn_def = {"features_from": {"graph": "dallas", "groups": ["Texas"]}}
        resolve_supernode_features(sn_def, graph_urls, cache)
        resolve_supernode_features(sn_def, graph_urls, cache)

        # Should only call extract once due to caching
        mock_extract.assert_called_once()

    def test_features_from_missing_graph(self):
        sn_def = {"features_from": {"graph": "nonexistent", "groups": ["Texas"]}}
        with self.assertRaises(ValueError) as ctx:
            resolve_supernode_features(sn_def, {}, {})
        self.assertIn("nonexistent", str(ctx.exception))

    @patch("graph_analysis.utils.yaml_loader.extract_supernode_features")
    def test_features_from_missing_group(self, mock_extract):
        mock_extract.return_value = {"Texas": [Feature(20, 9, 15589)]}
        sn_def = {"features_from": {"graph": "dallas", "groups": ["NonExistent"]}}
        graph_urls = {"dallas": "https://example.com"}
        cache = {}

        with self.assertRaises(ValueError) as ctx:
            resolve_supernode_features(sn_def, graph_urls, cache)
        self.assertIn("NonExistent", str(ctx.exception))


class TestBuildSupernodes(unittest.TestCase):
    def test_manual_features_and_children(self):
        config = {
            "graphs": {},
            "supernodes": {
                "child": {"features": [{"layer": 1, "pos": 0, "feature_idx": 100}]},
                "parent": {
                    "features": [{"layer": 2, "pos": 0, "feature_idx": 200}],
                    "children": ["child"],
                },
            },
        }
        supernodes, pos_offsets = build_supernodes(config, {})
        self.assertIn("child", supernodes)
        self.assertIn("parent", supernodes)
        self.assertEqual(len(supernodes["parent"].children), 1)
        self.assertEqual(supernodes["parent"].children[0].name, "child")
        self.assertEqual(pos_offsets, {})

    def test_embedding_node(self):
        config = {
            "graphs": {},
            "supernodes": {
                "target": {"features": [{"layer": 1, "pos": 0, "feature_idx": 100}]},
                "emb": {"features": None, "children": ["target"]},
            },
        }
        supernodes, _ = build_supernodes(config, {})
        self.assertIsNone(supernodes["emb"].features)
        self.assertEqual(len(supernodes["emb"].children), 1)

    def test_pos_offset_returned(self):
        config = {
            "graphs": {},
            "supernodes": {
                "synonym": {
                    "features": [{"layer": 3, "pos": 3, "feature_idx": 15891}],
                    "pos_offset": -1,
                },
            },
        }
        supernodes, pos_offsets = build_supernodes(config, {})
        self.assertEqual(pos_offsets["synonym"], -1)
        # Features are NOT shifted yet (shift happens in runner after initialize_node)
        self.assertEqual(supernodes["synonym"].features[0].pos, 3)

    def test_missing_child_raises(self):
        config = {
            "graphs": {},
            "supernodes": {
                "parent": {
                    "features": [{"layer": 1, "pos": 0, "feature_idx": 100}],
                    "children": ["nonexistent"],
                },
            },
        }
        with self.assertRaises(ValueError) as ctx:
            build_supernodes(config, {})
        self.assertIn("nonexistent", str(ctx.exception))


class TestResolveGraphLayout(unittest.TestCase):
    def test_uses_top_level_layout(self):
        supernodes = {
            "a": Supernode(name="a", features=[Feature(1, 0, 100)]),
            "b": Supernode(name="b", features=[Feature(2, 0, 200)]),
        }
        config = {"graph_layout": [["a"], ["b"]]}
        exp_config = {}

        layout = resolve_graph_layout(config, exp_config, supernodes)
        self.assertEqual(len(layout), 2)
        self.assertEqual(layout[0][0].name, "a")
        self.assertEqual(layout[1][0].name, "b")

    def test_experiment_layout_overrides(self):
        supernodes = {
            "a": Supernode(name="a", features=[Feature(1, 0, 100)]),
            "b": Supernode(name="b", features=[Feature(2, 0, 200)]),
        }
        config = {"graph_layout": [["a"], ["b"]]}
        exp_config = {"graph_layout": [["b", "a"]]}

        layout = resolve_graph_layout(config, exp_config, supernodes)
        self.assertEqual(len(layout), 1)
        self.assertEqual(layout[0][0].name, "b")
        self.assertEqual(layout[0][1].name, "a")

    def test_missing_layout_raises(self):
        with self.assertRaises(ValueError):
            resolve_graph_layout({}, {}, {})

    def test_missing_node_in_layout_raises(self):
        config = {"graph_layout": [["nonexistent"]]}
        with self.assertRaises(ValueError) as ctx:
            resolve_graph_layout(config, {}, {})
        self.assertIn("nonexistent", str(ctx.exception))


class TestResolveInterventions(unittest.TestCase):
    def test_single_ablation(self):
        sn = Supernode(name="texas", features=[Feature(20, 9, 15589)])
        supernodes = {"texas": sn}
        intervention_def = {"actions": [{"node": "texas", "scale": -2}]}

        interventions, replacements = resolve_interventions(intervention_def, supernodes)
        self.assertEqual(len(interventions), 1)
        self.assertEqual(interventions[0].supernode.name, "texas")
        self.assertEqual(interventions[0].scaling_factor, -2)
        self.assertIsNone(replacements)

    def test_multiple_actions(self):
        texas = Supernode(name="texas", features=[Feature(20, 9, 15589)])
        california = Supernode(name="california", features=[Feature(22, 10, 4367)])
        supernodes = {"texas": texas, "california": california}
        intervention_def = {
            "actions": [
                {"node": "texas", "scale": -2},
                {"node": "california", "scale": 2},
            ]
        }

        interventions, replacements = resolve_interventions(intervention_def, supernodes)
        self.assertEqual(len(interventions), 2)
        self.assertEqual(interventions[0].scaling_factor, -2)
        self.assertEqual(interventions[1].scaling_factor, 2)

    def test_replacements(self):
        texas = Supernode(name="texas", features=[Feature(20, 9, 15589)])
        california = Supernode(name="california", features=[Feature(22, 10, 4367)])
        supernodes = {"texas": texas, "california": california}
        intervention_def = {
            "actions": [{"node": "texas", "scale": -2}],
            "replacements": {"texas": "california"},
        }

        interventions, replacements = resolve_interventions(intervention_def, supernodes)
        self.assertIsNotNone(replacements)
        self.assertIn("texas", replacements)
        self.assertEqual(replacements["texas"].name, "california")

    def test_missing_node_in_action_raises(self):
        intervention_def = {"actions": [{"node": "nonexistent", "scale": -2}]}
        with self.assertRaises(ValueError) as ctx:
            resolve_interventions(intervention_def, {})
        self.assertIn("nonexistent", str(ctx.exception))

    def test_missing_replacement_target_raises(self):
        sn = Supernode(name="texas", features=[Feature(20, 9, 15589)])
        intervention_def = {
            "actions": [{"node": "texas", "scale": -2}],
            "replacements": {"nonexistent": "texas"},
        }
        with self.assertRaises(ValueError) as ctx:
            resolve_interventions(intervention_def, {"texas": sn})
        self.assertIn("nonexistent", str(ctx.exception))


class TestLoadRealYamlFiles(unittest.TestCase):
    """Test that the actual experiment YAML files load successfully."""

    def _get_yaml_path(self, filename):
        # tests/run_intervention/ -> repo root
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(base, "experiments", "run_intervention", filename)

    def test_capital_cities_loads(self):
        path = self._get_yaml_path("capital_cities.yaml")
        if not os.path.exists(path):
            self.skipTest("capital_cities.yaml not found")
        config = load_experiment_config(path)
        self.assertIn("ablate_say_capital", config["experiments"])
        self.assertIn("ablate_texas", config["experiments"])

    def test_capital_cities_cross_prompt_loads(self):
        path = self._get_yaml_path("capital_cities_cross_prompt.yaml")
        if not os.path.exists(path):
            self.skipTest("capital_cities_cross_prompt.yaml not found")
        config = load_experiment_config(path)
        self.assertIn("swap_texas_california", config["experiments"])

    def test_multilingual_small_big_loads(self):
        path = self._get_yaml_path("multilingual_small_big.yaml")
        if not os.path.exists(path):
            self.skipTest("multilingual_small_big.yaml not found")
        config = load_experiment_config(path)
        self.assertIn("turn_off_french", config["experiments"])

    def test_multilingual_antonym_synonym_loads(self):
        path = self._get_yaml_path("multilingual_antonym_synonym.yaml")
        if not os.path.exists(path):
            self.skipTest("multilingual_antonym_synonym.yaml not found")
        config = load_experiment_config(path)
        self.assertIn("replace_small_with_big", config["experiments"])
        # Verify pos_offset is present on synonym node
        self.assertEqual(config["supernodes"]["synonym"]["pos_offset"], -1)


if __name__ == "__main__":
    unittest.main()