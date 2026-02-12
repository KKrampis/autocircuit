import unittest
from unittest.mock import MagicMock, patch

import torch

from graph_analysis.run_intervention import (
    supernode_intervention,
    print_intervention_results,
    url_valid_graph,
    get_prompt_from_url,
    run_experiment,
)
from graph_analysis.utils.intervention_types import (
    Feature,
    Supernode,
    InterventionGraph,
    Intervention,
)


class TestSupernodeIntervention(unittest.TestCase):
    def test_returns_structured_results(self):
        features = [Feature(1, 0, 100), Feature(2, 0, 200)]
        sn = Supernode(name="Texas", features=features)

        activations = torch.zeros(5, 5, 500)
        activations[1, 0, 100] = 2.0
        activations[2, 0, 200] = 4.0

        graph = InterventionGraph(ordered_nodes=[[sn]], prompt="test prompt")
        graph.initialize_node(sn, activations)
        graph.set_node_activation_fractions(activations)

        mock_model = MagicMock()
        mock_logits = torch.randn(1, 5, 100)
        mock_logits[0, -1, 42] = 10.0
        mock_model.feature_intervention.return_value = (mock_logits, activations * 0.5)
        mock_model.tokenizer.decode = lambda x: f"tok_{x}"

        results = supernode_intervention(
            model=mock_model,
            intervention_graph=graph,
            interventions=[Intervention(sn, -2)],
        )

        self.assertIn("top_outputs", results)
        self.assertIn("node_activations", results)
        self.assertIn("interventions_applied", results)
        self.assertIn("replacements_applied", results)
        self.assertEqual(len(results["top_outputs"]), 5)
        self.assertEqual(results["interventions_applied"][0]["supernode"], "Texas")
        self.assertEqual(results["interventions_applied"][0]["scaling_factor"], -2)
        self.assertEqual(results["replacements_applied"], [])

    def test_intervention_values_passed_to_model(self):
        features = [Feature(1, 0, 100)]
        sn = Supernode(name="A", features=features)

        activations = torch.zeros(5, 5, 500)
        activations[1, 0, 100] = 3.0

        graph = InterventionGraph(ordered_nodes=[[sn]], prompt="test")
        graph.initialize_node(sn, activations)
        graph.set_node_activation_fractions(activations)

        mock_model = MagicMock()
        mock_logits = torch.randn(1, 5, 100)
        mock_model.feature_intervention.return_value = (mock_logits, activations)
        mock_model.tokenizer.decode = lambda x: f"tok_{x}"

        supernode_intervention(mock_model, graph, [Intervention(sn, -2)])

        call_args = mock_model.feature_intervention.call_args
        prompt_arg = call_args[0][0]
        intervention_values = call_args[0][1]
        self.assertEqual(prompt_arg, "test")
        # Should be (1, 0, 100, -2 * 3.0) = (1, 0, 100, -6.0)
        self.assertEqual(intervention_values[0][0], 1)
        self.assertEqual(intervention_values[0][1], 0)
        self.assertEqual(intervention_values[0][2], 100)
        self.assertAlmostEqual(intervention_values[0][3], -6.0)

    def test_replacements_applied(self):
        sn_a = Supernode(name="A", features=[Feature(1, 0, 100)])
        sn_b = Supernode(name="B", features=[Feature(2, 0, 200)])

        activations = torch.zeros(5, 5, 500)
        activations[1, 0, 100] = 2.0
        activations[2, 0, 200] = 3.0

        graph = InterventionGraph(ordered_nodes=[[sn_a, sn_b]], prompt="test")
        graph.initialize_node(sn_a, activations)
        graph.initialize_node(sn_b, activations)
        graph.set_node_activation_fractions(activations)

        mock_model = MagicMock()
        mock_logits = torch.randn(1, 5, 100)
        mock_model.feature_intervention.return_value = (mock_logits, activations)
        mock_model.tokenizer.decode = lambda x: f"tok_{x}"

        results = supernode_intervention(
            mock_model, graph,
            [Intervention(sn_a, -2)],
            replacements={"A": sn_b},
        )

        self.assertEqual(len(results["replacements_applied"]), 1)
        self.assertEqual(results["replacements_applied"][0]["target"], "A")
        self.assertEqual(results["replacements_applied"][0]["replacement"], "B")


class TestPrintInterventionResults(unittest.TestCase):
    def test_prints_without_error(self):
        results = {
            "top_outputs": [("Austin", 0.95), ("Texas", 0.03)],
            "node_activations": {"Texas": None, "Say Austin": 0.18},
            "interventions_applied": [{"supernode": "Texas", "scaling_factor": -2}],
            "replacements_applied": [],
        }
        # Should not raise
        print_intervention_results(results)

    def test_prints_with_experiment_name(self):
        results = {
            "top_outputs": [("Austin", 0.95)],
            "node_activations": {"Texas": None},
            "interventions_applied": [{"supernode": "Texas", "scaling_factor": -2}],
            "replacements_applied": [],
        }
        print_intervention_results(results, experiment_name="test_exp")

    def test_prints_replacements(self):
        results = {
            "top_outputs": [("Sacramento", 0.97)],
            "node_activations": {"Texas": None},
            "interventions_applied": [{"supernode": "Texas", "scaling_factor": -2}],
            "replacements_applied": [{"target": "Texas", "replacement": "California"}],
        }
        print_intervention_results(results)


class TestUrlHasPinnedIds(unittest.TestCase):
    def test_url_valid(self):
        url = "https://www.neuronpedia.org/gemma-2-2b/graph?slug=test&pinnedIds=27_22605_10%2C20_15589_10&supernodes=%5B%5B%22capital%22%2C%2227_22605_10%22%2C%2220_15589_10%22%5D%5D"
        self.assertTrue(url_valid_graph(url))

    def test_url_without_pinned_ids(self):
        url = "https://www.neuronpedia.org/gemma-2-2b/graph?slug=test"
        self.assertFalse(url_valid_graph(url))

    def test_url_with_empty_pinned_ids(self):
        url = "https://www.neuronpedia.org/gemma-2-2b/graph?slug=test&pinnedIds="
        self.assertFalse(url_valid_graph(url))


class TestGetPromptFromUrl(unittest.TestCase):
    @patch("graph_analysis.run_intervention.fetch_graph_metadata")
    def test_fetches_prompt(self, mock_fetch):
        mock_fetch.return_value = {"prompt": "<bos>The capital of Texas is"}
        url = "https://www.neuronpedia.org/gemma-2-2b/graph?slug=test-slug"
        prompt = get_prompt_from_url(url)
        # <bos> prefix is stripped by get_prompt_from_url
        self.assertEqual(prompt, "The capital of Texas is")
        mock_fetch.assert_called_once_with("gemma-2-2b", "test-slug")

    @patch("graph_analysis.run_intervention.fetch_graph_metadata")
    def test_fetches_prompt_without_bos(self, mock_fetch):
        mock_fetch.return_value = {"prompt": "The capital of Texas is"}
        url = "https://www.neuronpedia.org/gemma-2-2b/graph?slug=test-slug"
        prompt = get_prompt_from_url(url)
        self.assertEqual(prompt, "The capital of Texas is")


class TestRunExperiment(unittest.TestCase):
    def _make_mock_model(self, activations):
        mock_model = MagicMock()
        mock_logits = torch.randn(1, 5, 100)
        mock_logits[0, -1, 42] = 10.0
        mock_model.get_activations.return_value = (mock_logits, activations)
        mock_model.feature_intervention.return_value = (mock_logits, activations * 0.5)
        mock_model.tokenizer.decode = lambda x: f"tok_{x}"
        return mock_model

    def test_single_ablation_experiment(self):
        activations = torch.zeros(5, 5, 500)
        activations[1, 0, 100] = 2.0

        config = {
            "prompts": {"test": "hello world"},
            "graph_layout": [["node_a"]],
            "experiments": {
                "exp1": {
                    "prompt": "test",
                    "initialize": {"test": ["node_a"]},
                    "interventions": [{"actions": [{"node": "node_a", "scale": -2}]}],
                }
            },
        }
        supernodes = {"node_a": Supernode(name="node_a", features=[Feature(1, 0, 100)])}
        model = self._make_mock_model(activations)
        cache = {}

        results = run_experiment(model, config, "exp1", supernodes, {}, cache)

        self.assertEqual(results["experiment"], "exp1")
        self.assertEqual(results["prompt"], "hello world")
        self.assertEqual(len(results["interventions"]), 1)
        self.assertIn("top_outputs", results["interventions"][0])

    def test_activations_caching(self):
        activations = torch.zeros(5, 5, 500)
        activations[1, 0, 100] = 2.0

        config = {
            "prompts": {"test": "hello"},
            "graph_layout": [["a"]],
            "experiments": {
                "exp1": {
                    "prompt": "test",
                    "initialize": {"test": ["a"]},
                    "interventions": [{"actions": [{"node": "a", "scale": -2}]}],
                }
            },
        }
        supernodes = {"a": Supernode(name="a", features=[Feature(1, 0, 100)])}
        model = self._make_mock_model(activations)
        cache = {}

        run_experiment(model, config, "exp1", supernodes, {}, cache)
        self.assertIn("test", cache)

        # Run again - model.get_activations should not be called again
        model.get_activations.reset_mock()
        run_experiment(model, config, "exp1", supernodes, {}, cache)
        model.get_activations.assert_not_called()

    def test_cross_prompt_experiment(self):
        act1 = torch.zeros(5, 5, 500)
        act1[1, 0, 100] = 2.0
        act2 = torch.zeros(5, 5, 500)
        act2[2, 0, 200] = 3.0

        logits = torch.randn(1, 5, 100)
        logits[0, -1, 42] = 10.0

        model = MagicMock()
        model.get_activations.side_effect = [(logits, act1), (logits, act2)]
        model.feature_intervention.return_value = (logits, act1 * 0.5)
        model.tokenizer.decode = lambda x: f"tok_{x}"

        config = {
            "prompts": {"prompt1": "hello", "prompt2": "world"},
            "graph_layout": [["a", "b"]],
            "experiments": {
                "exp1": {
                    "prompt": "prompt1",
                    "initialize": {
                        "prompt1": ["a"],
                        "prompt2": ["b"],
                    },
                    "interventions": [{
                        "actions": [
                            {"node": "a", "scale": -2},
                            {"node": "b", "scale": 2},
                        ],
                        "replacements": {"a": "b"},
                    }],
                }
            },
        }
        supernodes = {
            "a": Supernode(name="a", features=[Feature(1, 0, 100)]),
            "b": Supernode(name="b", features=[Feature(2, 0, 200)]),
        }

        results = run_experiment(model, config, "exp1", supernodes, {}, {})
        self.assertEqual(len(results["interventions"][0]["replacements_applied"]), 1)


if __name__ == "__main__":
    unittest.main()