import unittest

from graph_analysis.feature_intervention import parse_feature_spec


class TestParseFeatureSpec(unittest.TestCase):
    def test_basic(self):
        layer, pos, feat_idx = parse_feature_spec("20,-1,1454")
        self.assertEqual(layer, 20)
        self.assertEqual(pos, -1)
        self.assertEqual(feat_idx, 1454)

    def test_zero_values(self):
        layer, pos, feat_idx = parse_feature_spec("0,0,0")
        self.assertEqual(layer, 0)
        self.assertEqual(pos, 0)
        self.assertEqual(feat_idx, 0)


if __name__ == "__main__":
    unittest.main()
