from collections import namedtuple
import torch

Feature = namedtuple("Feature", ["layer", "pos", "feature_idx"])


class Supernode:
    name: str
    features: list[Feature] | None
    activation: float | None
    default_activations: torch.Tensor | None
    children: list["Supernode"]
    intervention: str | None
    replacement_node: "Supernode | None"

    def __init__(
        self,
        name: str,
        features: list[Feature] | None = None,
        children: list["Supernode"] | None = None,
        intervention: str | None = None,
        replacement_node: "Supernode | None" = None,
    ):
        self.name = name
        self.features = features
        self.activation = None
        self.default_activations = None
        self.children = children if children is not None else []
        self.intervention = intervention
        self.replacement_node = replacement_node

    def __repr__(self):
        return (
            f"Supernode(name={self.name}, activation={self.activation}, "
            f"features={len(self.features) if self.features else 0}, "
            f"children={[c.name for c in self.children]})"
        )


class InterventionGraph:
    prompt: str
    ordered_nodes: list[list[Supernode]]
    nodes: dict[str, Supernode]

    def __init__(self, ordered_nodes: list[list[Supernode]], prompt: str):
        self.ordered_nodes = ordered_nodes
        self.prompt = prompt
        self.nodes = {}

    def initialize_node(self, node: Supernode, activations: torch.Tensor):
        self.nodes[node.name] = node
        if node.features:
            node.default_activations = torch.tensor(
                [activations[feature] for feature in node.features]
            )
        else:
            node.default_activations = None

    def set_node_activation_fractions(self, current_activations: torch.Tensor):
        for node in self.nodes.values():
            if node.features:
                current = torch.tensor(
                    [current_activations[feature] for feature in node.features]
                )
                node.activation = (current / node.default_activations).mean().item()
            else:
                node.activation = None
            node.intervention = None
            node.replacement_node = None

    def get_activation_summary(self) -> dict[str, float | None]:
        """Return node name -> activation fraction for all nodes."""
        return {name: node.activation for name, node in self.nodes.items()}


Intervention = namedtuple("Intervention", ["supernode", "scaling_factor"])
