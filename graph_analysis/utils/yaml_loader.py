"""Load and resolve YAML experiment configs into runtime objects.

Parses YAML experiment files and resolves supernodes, graph layouts,
and interventions into the types defined in intervention_types.py.
Does NOT load models or run interventions -- just builds the objects.
"""

import yaml

from circuit_tracer.utils.demo_utils import extract_supernode_features

from graph_analysis.utils.intervention_types import (
    Feature,
    Supernode,
    Intervention,
)


def load_experiment_config(yaml_path: str) -> dict:
    """Load and validate a YAML experiment config file.

    Required top-level keys: model, prompts, supernodes, experiments.
    Optional: graphs, graph_layout.

    Returns the parsed YAML dict.
    """
    with open(yaml_path) as f:
        config = yaml.safe_load(f)

    required_keys = ["model", "prompts", "supernodes", "experiments"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required key '{key}' in {yaml_path}")

    model_cfg = config["model"]
    for key in ["name", "transcoder", "backend"]:
        if key not in model_cfg:
            raise ValueError(f"Missing required model key '{key}' in {yaml_path}")

    return config


def resolve_supernode_features(
    sn_def: dict,
    graph_urls: dict[str, str],
    extracted_cache: dict[str, dict],
) -> list[Feature] | None:
    """Resolve a supernode's features from its YAML definition.

    Handles three cases:
    1. features: null or key absent with no features_from -> None (embedding node)
    2. features: [{layer, pos, feature_idx}, ...] -> list[Feature]
    3. features_from: {graph, groups} -> extracted from URL, groups merged

    Args:
        sn_def: YAML dict for one supernode.
        graph_urls: Mapping of graph_key -> URL string.
        extracted_cache: Cache of graph_key -> extract_supernode_features() result.
            Populated on first access to avoid redundant URL parsing.
    """
    # Case 1: explicit features list
    if "features" in sn_def:
        raw = sn_def["features"]
        if raw is None:
            return None
        return [Feature(layer=f["layer"], pos=f["pos"], feature_idx=f["feature_idx"]) for f in raw]

    # Case 3: features_from
    if "features_from" in sn_def:
        spec = sn_def["features_from"]
        graph_key = spec["graph"]
        groups = spec["groups"]

        if graph_key not in extracted_cache:
            if graph_key not in graph_urls:
                raise ValueError(
                    f"Graph '{graph_key}' referenced in features_from but not defined in graphs"
                )
            extracted_cache[graph_key] = extract_supernode_features(graph_urls[graph_key])

        extracted = extracted_cache[graph_key]
        features = []
        for group_name in groups:
            if group_name not in extracted:
                available = list(extracted.keys())
                raise ValueError(
                    f"Group '{group_name}' not found in graph '{graph_key}'. "
                    f"Available: {available}"
                )
            features.extend(extracted[group_name])
        return features

    # Case 1 fallback: no features key and no features_from -> embedding node
    return None


def build_supernodes(
    config: dict,
    extracted_cache: dict[str, dict],
) -> tuple[dict[str, Supernode], dict[str, int]]:
    """Build all Supernode objects from YAML config.

    Two-pass approach:
    1. Create all Supernode objects (without children)
    2. Wire up children references

    Returns:
        (supernodes, pos_offsets) where:
        - supernodes: dict mapping supernode_key -> Supernode
        - pos_offsets: dict mapping supernode_key -> offset (only for nodes with pos_offset)
    """
    graph_urls = config.get("graphs", {})
    sn_defs = config["supernodes"]

    # Pass 1: create Supernode objects
    supernodes = {}
    pos_offsets = {}
    for key, sn_def in sn_defs.items():
        features = resolve_supernode_features(sn_def, graph_urls, extracted_cache)
        supernodes[key] = Supernode(name=key, features=features)

        if "pos_offset" in sn_def:
            pos_offsets[key] = sn_def["pos_offset"]

    # Pass 2: wire children
    for key, sn_def in sn_defs.items():
        if "children" in sn_def:
            children_keys = sn_def["children"]
            for child_key in children_keys:
                if child_key not in supernodes:
                    raise ValueError(
                        f"Supernode '{key}' references child '{child_key}' which is not defined"
                    )
            supernodes[key].children = [supernodes[ck] for ck in children_keys]

    return supernodes, pos_offsets


def resolve_graph_layout(
    config: dict,
    experiment_config: dict,
    supernodes: dict[str, Supernode],
) -> list[list[Supernode]]:
    """Resolve graph_layout into list of lists of Supernode objects.

    Uses experiment-level graph_layout if present, otherwise falls back
    to top-level graph_layout.
    """
    layout_def = experiment_config.get("graph_layout") or config.get("graph_layout")
    if layout_def is None:
        raise ValueError(
            "No graph_layout defined at experiment or top level"
        )

    ordered_nodes = []
    for row in layout_def:
        node_row = []
        for key in row:
            if key not in supernodes:
                raise ValueError(
                    f"graph_layout references supernode '{key}' which is not defined"
                )
            node_row.append(supernodes[key])
        ordered_nodes.append(node_row)
    return ordered_nodes


def resolve_interventions(
    intervention_def: dict,
    supernodes: dict[str, Supernode],
) -> tuple[list[Intervention], dict[str, Supernode] | None]:
    """Resolve a single intervention set from experiment config.

    Args:
        intervention_def: dict with 'actions' and optional 'replacements'.
        supernodes: resolved supernode objects.

    Returns:
        (interventions, replacements) where:
        - interventions: list of Intervention namedtuples
        - replacements: dict mapping target_name -> replacement Supernode, or None
    """
    interventions = []
    for action in intervention_def["actions"]:
        node_key = action["node"]
        scale = action["scale"]
        if node_key not in supernodes:
            raise ValueError(
                f"Intervention references node '{node_key}' which is not defined"
            )
        interventions.append(Intervention(supernodes[node_key], scale))

    replacements = None
    if "replacements" in intervention_def:
        replacements = {}
        for target_key, replacement_key in intervention_def["replacements"].items():
            if target_key not in supernodes:
                raise ValueError(
                    f"Replacement target '{target_key}' not found in supernodes"
                )
            if replacement_key not in supernodes:
                raise ValueError(
                    f"Replacement source '{replacement_key}' not found in supernodes"
                )
            replacements[supernodes[target_key].name] = supernodes[replacement_key]

    return interventions, replacements