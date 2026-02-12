import unittest
from unittest.mock import patch, MagicMock

from graph_analysis.api.graph.graph_get import parse_neuronpedia_url, fetch_graph_metadata
from graph_analysis.api.subgraph.subgraph_list import fetch_subgraph_list


class TestParseNeuronpediaUrl(unittest.TestCase):
    def test_basic_url(self):
        url = "https://www.neuronpedia.org/gemma-2-2b/graph?slug=gemma-michael-jordan-es"
        model_id, slug = parse_neuronpedia_url(url)
        self.assertEqual(model_id, "gemma-2-2b")
        self.assertEqual(slug, "gemma-michael-jordan-es")

    def test_url_with_extra_params(self):
        url = "https://www.neuronpedia.org/gemma-2-2b/graph?slug=gemma-fact-dallas-austin&pinnedIds=27_22605_10%2C20_15589_10&supernodes=%5B%5D"
        model_id, slug = parse_neuronpedia_url(url)
        self.assertEqual(model_id, "gemma-2-2b")
        self.assertEqual(slug, "gemma-fact-dallas-austin")


class TestFetchGraphMetadata(unittest.TestCase):
    @patch("graph_analysis.api.graph.graph_get.requests.get")
    def test_fetch_returns_prompt(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "modelId": "gemma-2-2b",
            "slug": "test-slug",
            "prompt": "<bos>Test prompt here",
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = fetch_graph_metadata("gemma-2-2b", "test-slug")
        self.assertEqual(result["prompt"], "<bos>Test prompt here")
        mock_get.assert_called_once_with("https://www.neuronpedia.org/api/graph/gemma-2-2b/test-slug")


class TestFetchSubgraphList(unittest.TestCase):
    @patch("graph_analysis.api.subgraph.subgraph_list.requests.post")
    def test_fetch_returns_subgraphs(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "subgraphs": [
                {
                    "id": "sg1",
                    "displayName": "solution",
                    "pinnedIds": ["27_22605_10", "20_15589_10"],
                    "supernodes": [["Texas", "20_15589_9", "16_25_9"]],
                }
            ],
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        result = fetch_subgraph_list("gemma-2-2b", "test-slug", "fake-key")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["displayName"], "solution")
        self.assertEqual(len(result[0]["pinnedIds"]), 2)

    @patch("graph_analysis.api.subgraph.subgraph_list.requests.post")
    def test_fetch_empty_subgraphs(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "subgraphs": []}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        result = fetch_subgraph_list("gemma-2-2b", "no-subgraphs", "fake-key")
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
