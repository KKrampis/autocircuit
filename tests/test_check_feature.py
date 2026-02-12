import unittest
from unittest.mock import patch, MagicMock
import json
import gzip
import struct
import zlib

from graph_analysis.check_feature import fetch_feature_data, print_feature_summary


class TestFetchFeatureData(unittest.TestCase):
    @patch("graph_analysis.check_feature.requests.get")
    @patch("graph_analysis.check_feature.hf_hub_download")
    def test_fetch_feature_data(self, mock_hf_download, mock_requests_get):
        # Create a fake index.json.gz
        index_data = {
            "20": {
                "filename": "layer_20.bin",
                "offsets": [0, 100, 200],  # feature 0: bytes 0-99, feature 1: bytes 100-199
            }
        }
        index_gz_path = "/tmp/test_index.json.gz"
        with open(index_gz_path, "wb") as f:
            f.write(gzip.compress(json.dumps(index_data).encode()))
        mock_hf_download.return_value = index_gz_path

        # Create fake feature data (compressed JSON with 4-byte length prefix)
        feature_data = {"act_min": 0.0, "act_max": 5.0, "top_logits": ["hello"]}
        compressed = zlib.compress(json.dumps(feature_data).encode(), level=9)
        # wbits=47 in decompress means gzip format, so compress with gzip
        import io
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
            gz.write(json.dumps(feature_data).encode())
        compressed = buf.getvalue()
        chunk = struct.pack("<I", len(compressed)) + compressed

        mock_response = MagicMock()
        mock_response.content = chunk
        mock_response.raise_for_status = MagicMock()
        mock_requests_get.return_value = mock_response

        result = fetch_feature_data(20, 1, "fake/repo")
        self.assertEqual(result["act_min"], 0.0)
        self.assertEqual(result["act_max"], 5.0)
        self.assertEqual(result["top_logits"], ["hello"])


class TestPrintFeatureSummary(unittest.TestCase):
    def test_prints_without_error(self):
        """Smoke test that print_feature_summary doesn't crash."""
        feat_data = {
            "act_min": 0.0,
            "act_max": 5.0,
            "top_logits": [["hello", 0.9]],
            "bottom_logits": [["world", -0.5]],
            "examples_quantiles": [
                {
                    "quantile_name": "top",
                    "examples": [
                        {"tokens": ["The", " cat"], "tokens_acts_list": [0.0, 1.5]}
                    ],
                }
            ],
        }
        # Should not raise
        print_feature_summary(20, 1454, feat_data)


if __name__ == "__main__":
    unittest.main()
