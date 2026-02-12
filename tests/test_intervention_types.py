import unittest

import torch

from graph_analysis.utils.intervention_types import (
    Feature,
    Supernode,
    InterventionGraph,
    Intervention,
)


class TestFeature(unittest.TestCase):
    def test_create_feature(self):
        f = Feature(layer=20, pos=10, feature_idx=1454)
        self.assertEqual(f.layer, 20)
        self.assertEqual(f.pos, 10)
        self.assertEqual(f.feature_idx, 1454)

    def test_feature_as_tuple_index(self):
        """Feature can be used as an index into a 3D tensor."""
        f = Feature(layer=2, pos=1, feature_idx=3)
        tensor = torch.zeros(5, 5, 5)
        tensor[2, 1, 3] = 42.0
        self.assertEqual(tensor[f], 42.0)


class TestSupernode(unittest.TestCase):
    def test_create_basic(self):
        sn = Supernode(name="Texas")
        self.assertEqual(sn.name, "Texas")
        self.assertIsNone(sn.features)
        self.assertEqual(sn.children, [])
        self.assertIsNone(sn.activation)
        self.assertIsNone(sn.default_activations)

    def test_create_with_features(self):
        features = [Feature(20, 9, 15589), Feature(16, 9, 25)]
        sn = Supernode(name="Texas", features=features)
        self.assertEqual(len(sn.features), 2)

    def test_children_default_no_shared_list(self):
        """Ensure default children list is not shared between instances."""
        sn1 = Supernode(name="A")
        sn2 = Supernode(name="B")
        sn1.children.append(sn2)
        self.assertEqual(len(sn1.children), 1)
        self.assertEqual(len(sn2.children), 0)

    def test_repr(self):
        child = Supernode(name="child")
        sn = Supernode(name="parent", features=[Feature(1, 2, 3)], children=[child])
        r = repr(sn)
        self.assertIn("parent", r)
        self.assertIn("child", r)


class TestInterventionGraph(unittest.TestCase):
    def setUp(self):
        self.features_a = [Feature(1, 0, 100), Feature(2, 0, 200)]
        self.features_b = [Feature(3, 1, 300)]
        self.node_a = Supernode(name="A", features=self.features_a)
        self.node_b = Supernode(name="B", features=self.features_b)
        self.graph = InterventionGraph(
            ordered_nodes=[[self.node_a, self.node_b]],
            prompt="test prompt",
        )
        # Create a fake activations tensor
        self.activations = torch.zeros(5, 5, 500)
        self.activations[1, 0, 100] = 2.0
        self.activations[2, 0, 200] = 4.0
        self.activations[3, 1, 300] = 6.0

    def test_initialize_node(self):
        self.graph.initialize_node(self.node_a, self.activations)
        self.assertIn("A", self.graph.nodes)
        self.assertIsNotNone(self.node_a.default_activations)
        self.assertEqual(self.node_a.default_activations[0], 2.0)
        self.assertEqual(self.node_a.default_activations[1], 4.0)

    def test_initialize_node_no_features(self):
        node_emb = Supernode(name="Emb")
        self.graph.initialize_node(node_emb, self.activations)
        self.assertIsNone(node_emb.default_activations)

    def test_set_activation_fractions(self):
        self.graph.initialize_node(self.node_a, self.activations)
        self.graph.initialize_node(self.node_b, self.activations)
        self.graph.set_node_activation_fractions(self.activations)
        # Same activations -> 100%
        self.assertAlmostEqual(self.node_a.activation, 1.0)
        self.assertAlmostEqual(self.node_b.activation, 1.0)

    def test_set_activation_fractions_halved(self):
        self.graph.initialize_node(self.node_a, self.activations)
        halved = self.activations * 0.5
        self.graph.set_node_activation_fractions(halved)
        self.assertAlmostEqual(self.node_a.activation, 0.5)

    def test_get_activation_summary(self):
        self.graph.initialize_node(self.node_a, self.activations)
        self.graph.initialize_node(self.node_b, self.activations)
        self.graph.set_node_activation_fractions(self.activations)
        summary = self.graph.get_activation_summary()
        self.assertIn("A", summary)
        self.assertIn("B", summary)
        self.assertAlmostEqual(summary["A"], 1.0)


class TestIntervention(unittest.TestCase):
    def test_create(self):
        sn = Supernode(name="Texas")
        iv = Intervention(supernode=sn, scaling_factor=-2)
        self.assertEqual(iv.supernode.name, "Texas")
        self.assertEqual(iv.scaling_factor, -2)


if __name__ == "__main__":
    unittest.main()
