import unittest
from unittest.mock import MagicMock, patch

import torch

from graph_analysis.run_intervention import (
    build_supernodes_from_url,
    supernode_intervention,
    parse_intervention_spec,
    print_intervention_results,
    url_has_pinned_ids,
    get_prompt_from_url,
)
from graph_analysis.utils.intervention_types import (
    Feature,
    Supernode,
    InterventionGraph,
    Intervention,
)


class TestParseInterventionSpec(unittest.TestCase):
    def test_basic(self):
        name, factor = parse_intervention_spec("Texas:-2")
        self.assertEqual(name, "Texas")
        self.assertEqual(factor, -2.0)

    def test_positive(self):
        name, factor = parse_intervention_spec("California:2")
        self.assertEqual(name, "California")
        self.assertEqual(factor, 2.0)

    def test_float_factor(self):
        name, factor = parse_intervention_spec("French:-0.5")
        self.assertEqual(name, "French")
        self.assertAlmostEqual(factor, -0.5)

    def test_name_with_spaces_and_colons(self):
        """Name can contain spaces but colon separates from factor."""
        name, factor = parse_intervention_spec("say big / large:-2")
        self.assertEqual(name, "say big / large")
        self.assertEqual(factor, -2.0)


class TestSupernodeIntervention(unittest.TestCase):
    def test_returns_structured_results(self):
        # Setup: create supernodes, graph, mock model
        features = [Feature(1, 0, 100), Feature(2, 0, 200)]
        sn = Supernode(name="Texas", features=features)

        activations = torch.zeros(5, 5, 500)
        activations[1, 0, 100] = 2.0
        activations[2, 0, 200] = 4.0

        graph = InterventionGraph(ordered_nodes=[[sn]], prompt="test prompt")
        graph.initialize_node(sn, activations)
        graph.set_node_activation_fractions(activations)

        # Mock model
        mock_model = MagicMock()
        # feature_intervention returns (logits, activations)
        mock_logits = torch.randn(1, 5, 100)
        mock_logits[0, -1, 42] = 10.0  # make token 42 the top prediction
        mock_model.feature_intervention.return_value = (mock_logits, activations * 0.5)
        mock_model.tokenizer.decode = lambda x: f"tok_{x}"

        results = supernode_intervention(
            model=mock_model,
            intervention_graph=graph,
            interventions=[Intervention(sn, -2)],
        )

        # Check structure
        self.assertIn("top_outputs", results)
        self.assertIn("node_activations", results)
        self.assertIn("interventions_applied", results)
        self.assertEqual(len(results["top_outputs"]), 5)
        self.assertEqual(results["interventions_applied"][0]["supernode"], "Texas")
        self.assertEqual(results["interventions_applied"][0]["scaling_factor"], -2)

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

        # Verify the intervention values passed to model
        call_args = mock_model.feature_intervention.call_args
        prompt_arg = call_args[0][0]
        intervention_values = call_args[0][1]
        self.assertEqual(prompt_arg, "test")
        # Should be (1, 0, 100, -2 * 3.0) = (1, 0, 100, -6.0)
        self.assertEqual(intervention_values[0][0], 1)
        self.assertEqual(intervention_values[0][1], 0)
        self.assertEqual(intervention_values[0][2], 100)
        self.assertAlmostEqual(intervention_values[0][3], -6.0)


class TestPrintInterventionResults(unittest.TestCase):
    def test_prints_without_error(self):
        results = {
            "top_outputs": [("Austin", 0.95), ("Texas", 0.03)],
            "node_activations": {"Texas": None, "Say Austin": 0.18},
            "interventions_applied": [{"supernode": "Texas", "scaling_factor": -2}],
        }
        # Should not raise
        print_intervention_results(results)


class TestUrlHasPinnedIds(unittest.TestCase):
    def test_url_with_pinned_ids(self):
        url = "https://www.neuronpedia.org/gemma-2-2b/graph?slug=test&pinnedIds=27_22605_10%2C20_15589_10"
        self.assertTrue(url_has_pinned_ids(url))

    def test_url_without_pinned_ids(self):
        url = "https://www.neuronpedia.org/gemma-2-2b/graph?slug=test"
        self.assertFalse(url_has_pinned_ids(url))

    def test_url_with_empty_pinned_ids(self):
        url = "https://www.neuronpedia.org/gemma-2-2b/graph?slug=test&pinnedIds="
        self.assertFalse(url_has_pinned_ids(url))


class TestGetPromptFromUrl(unittest.TestCase):
    @patch("graph_analysis.run_intervention.fetch_graph_metadata")
    def test_fetches_prompt(self, mock_fetch):
        mock_fetch.return_value = {"prompt": "<bos>The capital of Texas is"}
        url = "https://www.neuronpedia.org/gemma-2-2b/graph?slug=test-slug"
        prompt = get_prompt_from_url(url)
        self.assertEqual(prompt, "<bos>The capital of Texas is")
        mock_fetch.assert_called_once_with("gemma-2-2b", "test-slug")


if __name__ == "__main__":
    unittest.main()
