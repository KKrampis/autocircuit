#!/usr/bin/env python3
"""Circuit Analysis Agent Tools

Provides 18 tools for an LLM agent to explore pruned attribution graphs
and discover circuits in neural networks. Tools are invoked via CLI and
return JSON to stdout.

Usage:
    python circuit_analysis_tools.py --graph <path.json> <tool_name> [--arg value ...]

Categories:
    Graph Queries (fully implemented):
        get_node_info, get_neighbors, find_paths, get_subgraph, get_top_nodes, search_nodes
    Model Interventions (stubs):
        patch_node, patch_edge, ablate_nodes, run_model, test_circuit_faithfulness
    Component Inspection (stubs):
        get_attention_pattern, logit_lens, get_max_activating_examples, get_node_activation
    State Management (fully implemented):
        note, get_notes, get_progress
"""

import argparse
import heapq
import json
import os
import sys
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class NodeInfo:
    id: str
    feature: int | None = None
    layer: int | None = None
    head_index: int | None = None
    feature_index: int | None = None
    position: int | None = None
    node_type: str = "unknown"
    label: str | None = None
    attribution_score: float = 0.0
    ctx_idx: int | None = None
    in_degree: int = 0
    out_degree: int = 0
    extra: dict = field(default_factory=dict)


@dataclass
class Edge:
    source: str
    target: str
    weight: float = 0.0


# ---------------------------------------------------------------------------
# Node type inference
# ---------------------------------------------------------------------------

def _infer_node_type(node_raw: dict) -> str:
    """Heuristic to determine node type from Neuronpedia JSON fields."""
    nid = node_raw.get("id", "")
    # Embedding nodes typically start with "E" or contain "embed"
    if nid.startswith("E") or "embed" in nid.lower():
        return "embedding"
    # Attention heads: look for head_index or "H" in id like "L9H1"
    if node_raw.get("head_index") is not None:
        return "attention_head"
    if "H" in nid and "L" in nid:
        return "attention_head"
    # MLP nodes
    if "mlp" in nid.lower() or "MLP" in nid:
        return "mlp_layer"
    # SAE features: have feature field
    if node_raw.get("feature") is not None:
        return "sae_feature"
    # Residual
    if "resid" in nid.lower():
        return "residual"
    return "sae_feature"  # default for Neuronpedia graphs


# ---------------------------------------------------------------------------
# Core class
# ---------------------------------------------------------------------------

class CircuitAnalysisTools:
    """Holds the loaded graph and provides all 18 tool methods."""

    def __init__(self, graph_path: str):
        self.graph_path = graph_path
        self.graph_dir = str(Path(graph_path).parent)

        # Core indexes
        self.nodes_by_id: dict[str, NodeInfo] = {}
        self.adj_out: dict[str, list[Edge]] = defaultdict(list)
        self.adj_in: dict[str, list[Edge]] = defaultdict(list)
        self.nodes_sorted_by_attr: list[NodeInfo] = []
        self.metadata: dict = {}

        # State tracking
        self.nodes_inspected: set[str] = set()
        self.nodes_patched: set[str] = set()
        self.total_tool_calls: int = 0
        self.notes: list[dict] = []

        self._load_graph(graph_path)
        self._load_state()

    # ------------------------------------------------------------------
    # Graph loading
    # ------------------------------------------------------------------

    def _load_graph(self, path: str) -> None:
        with open(path, "r") as f:
            data = json.load(f)

        self.metadata = data.get("metadata", {})

        # Parse nodes — handle both Neuronpedia format and simplified format
        for n in data.get("nodes", []):
            nid = n.get("id") or n.get("node_id")
            if nid is None:
                continue

            # Parse layer (may be string like "E" for embeddings, or "27")
            raw_layer = n.get("layer")
            if raw_layer == "E" or raw_layer is None:
                parsed_layer = None
            else:
                try:
                    parsed_layer = int(raw_layer)
                except (ValueError, TypeError):
                    parsed_layer = None

            # Resolve node type
            feature_type = n.get("feature_type", "")
            node_type = n.get("node_type") or feature_type or _infer_node_type(n)

            # Resolve label: try label, description, clerp
            label = n.get("label") or n.get("description") or n.get("clerp") or None
            if label == "":
                label = None

            # Resolve attribution score: try influence, weight, attribution_score
            attr = n.get("influence") or n.get("weight") or n.get("attribution_score") or 0.0

            node = NodeInfo(
                id=nid,
                feature=n.get("feature"),
                layer=parsed_layer,
                head_index=n.get("head_index"),
                feature_index=n.get("feature_index") or n.get("feature"),
                position=n.get("position") or n.get("ctx_idx"),
                node_type=node_type,
                label=label,
                attribution_score=attr,
                ctx_idx=n.get("ctx_idx"),
            )
            # Store any extra fields
            known_keys = {
                "id", "node_id", "feature", "layer", "head_index", "feature_index",
                "position", "node_type", "feature_type", "label", "description",
                "clerp", "weight", "influence", "attribution_score", "ctx_idx",
            }
            node.extra = {k: v for k, v in n.items() if k not in known_keys}
            self.nodes_by_id[nid] = node

        # Parse edges — try "edges" then "links"
        edges_raw = data.get("edges") or data.get("links") or []
        for e in edges_raw:
            src = e["source"]
            tgt = e["target"]
            w = e.get("weight", 0.0)
            edge = Edge(source=src, target=tgt, weight=w)
            self.adj_out[src].append(edge)
            self.adj_in[tgt].append(edge)

        # Compute degrees
        for nid, node in self.nodes_by_id.items():
            node.out_degree = len(self.adj_out.get(nid, []))
            node.in_degree = len(self.adj_in.get(nid, []))

        # Pre-sort nodes by attribution
        self.nodes_sorted_by_attr = sorted(
            self.nodes_by_id.values(),
            key=lambda n: abs(n.attribution_score),
            reverse=True,
        )

    # ------------------------------------------------------------------
    # State persistence (notes + progress tracking)
    # ------------------------------------------------------------------

    def _state_path(self) -> str:
        return os.path.join(self.graph_dir, "agent_state.json")

    def _load_state(self) -> None:
        p = self._state_path()
        if os.path.exists(p):
            with open(p, "r") as f:
                state = json.load(f)
            self.notes = state.get("notes", [])
            self.nodes_inspected = set(state.get("nodes_inspected", []))
            self.nodes_patched = set(state.get("nodes_patched", []))
            self.total_tool_calls = state.get("total_tool_calls", 0)

    def _save_state(self) -> None:
        state = {
            "notes": self.notes,
            "nodes_inspected": sorted(self.nodes_inspected),
            "nodes_patched": sorted(self.nodes_patched),
            "total_tool_calls": self.total_tool_calls,
        }
        with open(self._state_path(), "w") as f:
            json.dump(state, f, indent=2)

    # ------------------------------------------------------------------
    # Helper: track inspected nodes
    # ------------------------------------------------------------------

    def _track(self, *node_ids: str) -> None:
        for nid in node_ids:
            if nid and nid in self.nodes_by_id:
                self.nodes_inspected.add(nid)

    def _track_patched(self, *node_ids: str) -> None:
        for nid in node_ids:
            if nid and nid in self.nodes_by_id:
                self.nodes_patched.add(nid)
                self.nodes_inspected.add(nid)

    # ==================================================================
    # CATEGORY 1: GRAPH QUERIES (fully implemented)
    # ==================================================================

    def get_node_info(self, node_id: str) -> dict:
        """Look up metadata for a single node in the attribution graph."""
        self.total_tool_calls += 1
        self._track(node_id)

        node = self.nodes_by_id.get(node_id)
        if node is None:
            return {"error": f"Node '{node_id}' not found in graph"}

        return {
            "id": node.id,
            "type": node.node_type,
            "layer": node.layer,
            "head_index": node.head_index,
            "feature_index": node.feature_index,
            "position": node.position,
            "label": node.label,
            "attribution_score": node.attribution_score,
            "in_degree": node.in_degree,
            "out_degree": node.out_degree,
        }

    def get_neighbors(
        self,
        node_id: str,
        direction: str = "downstream",
        top_k: int = 10,
        min_weight: float = 0.0,
    ) -> dict:
        """Get the highest-attribution neighbors of a node."""
        self.total_tool_calls += 1
        self._track(node_id)

        if node_id not in self.nodes_by_id:
            return {"error": f"Node '{node_id}' not found in graph"}

        if direction == "upstream":
            edges = self.adj_in.get(node_id, [])
            neighbor_key = "source"
        elif direction == "downstream":
            edges = self.adj_out.get(node_id, [])
            neighbor_key = "target"
        else:
            return {"error": f"Invalid direction '{direction}'. Use 'upstream' or 'downstream'."}

        # Filter by min_weight, sort by absolute weight descending
        filtered = [e for e in edges if abs(e.weight) >= min_weight]
        filtered.sort(key=lambda e: abs(e.weight), reverse=True)
        filtered = filtered[:top_k]

        results = []
        for rank, e in enumerate(filtered, 1):
            neighbor_id = getattr(e, neighbor_key)
            neighbor_node = self.nodes_by_id.get(neighbor_id)
            self._track(neighbor_id)
            results.append({
                "node_id": neighbor_id,
                "node_type": neighbor_node.node_type if neighbor_node else "unknown",
                "layer": neighbor_node.layer if neighbor_node else None,
                "label": neighbor_node.label if neighbor_node else None,
                "edge_weight": e.weight,
                "edge_rank": rank,
            })

        return {"node_id": node_id, "direction": direction, "neighbors": results}

    def find_paths(
        self,
        source: str,
        target: str,
        top_k: int = 5,
        max_hops: int = 4,
    ) -> dict:
        """Find the highest-attribution paths between two nodes.

        Uses a priority-queue BFS that maximizes the product of absolute
        edge weights along each path (equivalently, minimizes the sum of
        -log|weight|). Bounded by max_hops.
        """
        self.total_tool_calls += 1
        self._track(source, target)

        if source not in self.nodes_by_id:
            return {"error": f"Source node '{source}' not found"}
        if target not in self.nodes_by_id:
            return {"error": f"Target node '{target}' not found"}

        # Priority queue: (-log_product, path_list)
        # We want to maximize product of |weights|, so minimize sum of -log|w|
        import math

        found_paths: list[dict] = []
        # (cost, path)
        pq: list[tuple[float, list[str]]] = [(0.0, [source])]
        visit_counts: dict[str, int] = defaultdict(int)
        # Allow each node to be expanded at most top_k times (Yen's-style bound)
        max_visits = top_k + 5

        while pq and len(found_paths) < top_k:
            cost, path = heapq.heappop(pq)
            current = path[-1]

            if len(path) > max_hops + 1:
                continue

            visit_counts[current] += 1
            if visit_counts[current] > max_visits:
                continue

            if current == target and len(path) > 1:
                # Reconstruct path info
                attr_product = math.exp(-cost) if cost < 700 else 0.0
                edges_in_path = []
                bottleneck_weight = float("inf")
                bottleneck_edge = None
                for i in range(len(path) - 1):
                    s, t = path[i], path[i + 1]
                    # Find the edge weight
                    w = 0.0
                    for e in self.adj_out.get(s, []):
                        if e.target == t:
                            w = e.weight
                            break
                    edges_in_path.append({"source": s, "target": t, "weight": w})
                    if abs(w) < bottleneck_weight:
                        bottleneck_weight = abs(w)
                        bottleneck_edge = {"source": s, "target": t, "weight": w}

                found_paths.append({
                    "path": path,
                    "path_attribution": round(attr_product, 6),
                    "hop_count": len(path) - 1,
                    "bottleneck": bottleneck_edge,
                })
                continue

            # Expand neighbors
            for e in self.adj_out.get(current, []):
                if e.target in path:
                    continue  # no cycles
                w = abs(e.weight)
                if w <= 0:
                    continue
                edge_cost = -math.log(min(w, 1.0))  # clamp to avoid negative costs for w>1
                heapq.heappush(pq, (cost + edge_cost, path + [e.target]))

        # Track all nodes in found paths
        for p in found_paths:
            for nid in p["path"]:
                self._track(nid)

        return {"source": source, "target": target, "paths": found_paths}

    def get_subgraph(
        self,
        node_ids: list[str],
        depth: int = 1,
        min_weight: float = 0.01,
    ) -> dict:
        """Get the local neighborhood around a set of nodes via BFS."""
        self.total_tool_calls += 1

        # Validate seed nodes
        valid_seeds = [nid for nid in node_ids if nid in self.nodes_by_id]
        if not valid_seeds:
            return {"error": "None of the provided node_ids were found in the graph"}

        # BFS
        visited: set[str] = set()
        frontier = [(nid, 0) for nid in valid_seeds]
        collected_nodes: set[str] = set()
        collected_edges: list[dict] = []
        seen_edges: set[tuple[str, str]] = set()

        while frontier:
            next_frontier = []
            for nid, d in frontier:
                if nid in visited:
                    continue
                visited.add(nid)
                collected_nodes.add(nid)
                self._track(nid)

                if d < depth:
                    # Expand outgoing
                    for e in self.adj_out.get(nid, []):
                        if abs(e.weight) >= min_weight:
                            edge_key = (e.source, e.target)
                            if edge_key not in seen_edges:
                                seen_edges.add(edge_key)
                                collected_edges.append({
                                    "source": e.source,
                                    "target": e.target,
                                    "weight": e.weight,
                                })
                            collected_nodes.add(e.target)
                            if e.target not in visited:
                                next_frontier.append((e.target, d + 1))
                    # Expand incoming
                    for e in self.adj_in.get(nid, []):
                        if abs(e.weight) >= min_weight:
                            edge_key = (e.source, e.target)
                            if edge_key not in seen_edges:
                                seen_edges.add(edge_key)
                                collected_edges.append({
                                    "source": e.source,
                                    "target": e.target,
                                    "weight": e.weight,
                                })
                            collected_nodes.add(e.source)
                            if e.source not in visited:
                                next_frontier.append((e.source, d + 1))
            frontier = next_frontier

        # Build node list
        nodes_out = []
        layers = []
        for nid in collected_nodes:
            node = self.nodes_by_id.get(nid)
            if node:
                nodes_out.append({
                    "id": node.id,
                    "type": node.node_type,
                    "layer": node.layer,
                    "attribution": node.attribution_score,
                    "label": node.label,
                })
                if node.layer is not None:
                    layers.append(node.layer)

        num_nodes = len(nodes_out)
        num_edges = len(collected_edges)
        max_possible_edges = num_nodes * (num_nodes - 1) if num_nodes > 1 else 1
        density = num_edges / max_possible_edges if max_possible_edges > 0 else 0.0

        return {
            "nodes": nodes_out,
            "edges": collected_edges,
            "stats": {
                "num_nodes": num_nodes,
                "num_edges": num_edges,
                "layer_span": [min(layers), max(layers)] if layers else None,
                "density": round(density, 4),
            },
        }

    def get_top_nodes(
        self,
        top_k: int = 20,
        layer: int | None = None,
        layer_range: list[int] | None = None,
        node_type: str | None = None,
        position: int | None = None,
        sort_by: str = "attribution",
    ) -> dict:
        """Get the most important nodes in the graph, optionally filtered."""
        self.total_tool_calls += 1

        candidates = list(self.nodes_sorted_by_attr)

        # Apply filters
        if layer is not None:
            candidates = [n for n in candidates if n.layer == layer]
        if layer_range is not None and len(layer_range) == 2:
            lo, hi = layer_range
            candidates = [n for n in candidates if n.layer is not None and lo <= n.layer <= hi]
        if node_type is not None:
            candidates = [n for n in candidates if n.node_type == node_type]
        if position is not None:
            candidates = [n for n in candidates if n.position == position or n.ctx_idx == position]

        # Sort
        if sort_by == "in_degree":
            candidates.sort(key=lambda n: n.in_degree, reverse=True)
        elif sort_by == "out_degree":
            candidates.sort(key=lambda n: n.out_degree, reverse=True)
        # else: already sorted by attribution

        candidates = candidates[:top_k]

        results = []
        for n in candidates:
            self._track(n.id)
            score = n.attribution_score
            if sort_by == "in_degree":
                score = n.in_degree
            elif sort_by == "out_degree":
                score = n.out_degree
            results.append({
                "node_id": n.id,
                "type": n.node_type,
                "layer": n.layer,
                "score": score,
                "label": n.label,
            })

        return {"nodes": results, "total_matching": len(candidates)}

    def search_nodes(
        self,
        query: str,
        top_k: int = 10,
    ) -> dict:
        """Search for nodes by substring match on auto-interp labels."""
        self.total_tool_calls += 1

        query_lower = query.lower()
        query_terms = query_lower.split()

        scored: list[tuple[float, NodeInfo]] = []
        for node in self.nodes_by_id.values():
            label = node.label
            if not label:
                continue
            label_lower = label.lower()

            # Score: fraction of query terms found in label
            matches = sum(1 for term in query_terms if term in label_lower)
            if matches == 0:
                continue
            match_score = matches / len(query_terms)

            # Boost exact substring match
            if query_lower in label_lower:
                match_score = 1.0

            scored.append((match_score, node))

        # Sort by match score descending, then by attribution descending
        scored.sort(key=lambda x: (x[0], abs(x[1].attribution_score)), reverse=True)
        scored = scored[:top_k]

        results = []
        for score, node in scored:
            self._track(node.id)
            results.append({
                "node_id": node.id,
                "type": node.node_type,
                "layer": node.layer,
                "label": node.label,
                "match_score": round(score, 3),
                "attribution": node.attribution_score,
            })

        return {"query": query, "results": results}

    # ==================================================================
    # CATEGORY 2: MODEL INTERVENTIONS (stubs)
    # ==================================================================

    def patch_node(
        self,
        node_id: str,
        clean_input: str,
        corrupted_input: str,
        metric: str = "logit_diff",
        target_tokens: list[str] | None = None,
    ) -> dict:
        """Activation patching: run corrupted input, but swap in this node's activation from clean.

        # TODO: Wire up TransformerLens / nnsight
        # Implementation: Two forward passes with hooks.
        #   Pass 1: run clean_input, cache activation at node_id.
        #   Pass 2: run corrupted_input, substitute cached clean activation at node_id.
        # Return recovery = (patched - corrupted) / (clean - corrupted).
        """
        self.total_tool_calls += 1
        self._track_patched(node_id)
        raise NotImplementedError(
            "patch_node requires a model (TransformerLens/nnsight). "
            "Not yet wired up — graph-only mode."
        )

    def patch_edge(
        self,
        source: str,
        target: str,
        clean_input: str,
        corrupted_input: str,
        metric: str = "logit_diff",
        target_tokens: list[str] | None = None,
    ) -> dict:
        """Path patching: patch only the information flowing along one specific edge.

        # TODO: Wire up TransformerLens / nnsight
        # Implementation: Patch only the component of target's input that comes
        # from source. For attention heads, patch that head's contribution to
        # the residual stream at the target's input.
        """
        self.total_tool_calls += 1
        self._track_patched(source, target)
        raise NotImplementedError(
            "patch_edge requires a model (TransformerLens/nnsight). "
            "Not yet wired up — graph-only mode."
        )

    def ablate_nodes(
        self,
        node_ids: list[str],
        input_text: str,
        method: str = "mean",
        metric: str = "logit_diff",
        target_tokens: list[str] | None = None,
    ) -> dict:
        """Knock out a set of nodes and measure the damage.

        # TODO: Wire up TransformerLens / nnsight
        # Implementation: Single forward pass with hooks that replace activations
        # at specified nodes with zero / precomputed dataset mean / random sample.
        """
        self.total_tool_calls += 1
        for nid in node_ids:
            self._track_patched(nid)
        raise NotImplementedError(
            "ablate_nodes requires a model (TransformerLens/nnsight). "
            "Not yet wired up — graph-only mode."
        )

    def run_model(
        self,
        input_text: str,
        top_k: int = 10,
        target_tokens: list[str] | None = None,
    ) -> dict:
        """Run the model and see what it predicts.

        # TODO: Wire up TransformerLens / nnsight
        # Implementation: Single forward pass, read output logits.
        """
        self.total_tool_calls += 1
        raise NotImplementedError(
            "run_model requires a model (TransformerLens/nnsight). "
            "Not yet wired up — graph-only mode."
        )

    def test_circuit_faithfulness(
        self,
        circuit_nodes: list[str],
        input_text: str,
        metric: str = "logit_diff",
        target_tokens: list[str] | None = None,
    ) -> dict:
        """Ablate everything OUTSIDE the proposed circuit to test if it alone reproduces the behavior.

        # TODO: Wire up TransformerLens / nnsight
        # Implementation: Mean-ablate every node NOT in circuit_nodes,
        # run forward pass, compute metric.
        """
        self.total_tool_calls += 1
        for nid in circuit_nodes:
            self._track_patched(nid)
        raise NotImplementedError(
            "test_circuit_faithfulness requires a model (TransformerLens/nnsight). "
            "Not yet wired up — graph-only mode."
        )

    # ==================================================================
    # CATEGORY 3: COMPONENT INSPECTION (stubs)
    # ==================================================================

    def get_attention_pattern(
        self,
        head: str,
        input_text: str,
        top_k_per_position: int = 5,
    ) -> dict:
        """Get the attention pattern for a specific head on a specific input.

        # TODO: Wire up TransformerLens / nnsight
        # Implementation: Forward pass with attention weight caching.
        # cache["attn_weights", layer]. Detect pattern_type heuristic
        # (previous_token, bos, induction, content).
        """
        self.total_tool_calls += 1
        self._track(head)
        raise NotImplementedError(
            "get_attention_pattern requires a model (TransformerLens/nnsight). "
            "Not yet wired up — graph-only mode."
        )

    def logit_lens(
        self,
        layer: int,
        position: int,
        input_text: str,
        top_k: int = 10,
    ) -> dict:
        """What is the residual stream 'predicting' at this point in the network?

        # TODO: Wire up TransformerLens / nnsight
        # Implementation: Extract residual stream at (layer, position),
        # apply unembedding matrix and final LayerNorm, get logits.
        """
        self.total_tool_calls += 1
        raise NotImplementedError(
            "logit_lens requires a model (TransformerLens/nnsight). "
            "Not yet wired up — graph-only mode."
        )

    def get_max_activating_examples(
        self,
        node_id: str,
        k: int = 10,
        dataset: str = "default",
    ) -> dict:
        """What inputs make this component fire the most?

        # TODO: Wire up precomputed activation index
        # Implementation: Requires a precomputed index — run model on dataset,
        # cache activations at all nodes, sort by activation per node.
        """
        self.total_tool_calls += 1
        self._track(node_id)
        raise NotImplementedError(
            "get_max_activating_examples requires a precomputed activation index. "
            "Not yet wired up — graph-only mode."
        )

    def get_node_activation(
        self,
        node_id: str,
        input_text: str,
    ) -> dict:
        """Get this node's activation on a specific input.

        # TODO: Wire up TransformerLens / nnsight
        # Implementation: Forward pass, extract activation, compare to
        # precomputed dataset stats for that node.
        """
        self.total_tool_calls += 1
        self._track(node_id)
        raise NotImplementedError(
            "get_node_activation requires a model (TransformerLens/nnsight). "
            "Not yet wired up — graph-only mode."
        )

    # ==================================================================
    # CATEGORY 4: STATE MANAGEMENT (fully implemented)
    # ==================================================================

    def note(self, content: str, tags: list[str] | None = None) -> dict:
        """Write a note to persistent storage (the agent's lab notebook)."""
        self.total_tool_calls += 1

        note_id = len(self.notes)
        entry = {
            "note_id": note_id,
            "content": content,
            "tags": tags or [],
        }
        self.notes.append(entry)
        return {"note_id": note_id}

    def get_notes(
        self,
        tags: list[str] | None = None,
        last_n: int | None = None,
    ) -> dict:
        """Retrieve previous notes, optionally filtered by tags or recency."""
        self.total_tool_calls += 1

        results = list(self.notes)

        if tags:
            tag_set = set(tags)
            results = [n for n in results if tag_set & set(n.get("tags", []))]

        if last_n is not None:
            results = results[-last_n:]

        return {"notes": results}

    def get_progress(self) -> dict:
        """What has the agent looked at so far?"""
        self.total_tool_calls += 1

        # Top-50 nodes by attribution that haven't been inspected
        unvisited = [
            n.id
            for n in self.nodes_sorted_by_attr[:50]
            if n.id not in self.nodes_inspected
        ]

        return {
            "nodes_inspected": sorted(self.nodes_inspected),
            "nodes_patched": sorted(self.nodes_patched),
            "total_nodes_inspected": len(self.nodes_inspected),
            "total_nodes_patched": len(self.nodes_patched),
            "total_tool_calls": self.total_tool_calls,
            "graph_total_nodes": len(self.nodes_by_id),
            "graph_total_edges": sum(len(v) for v in self.adj_out.values()),
            "high_attribution_not_visited": unvisited,
        }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

TOOL_REGISTRY = {
    # Graph queries
    "get_node_info": {
        "method": "get_node_info",
        "args": [("--node_id", str, True)],
    },
    "get_neighbors": {
        "method": "get_neighbors",
        "args": [
            ("--node_id", str, True),
            ("--direction", str, False, "downstream"),
            ("--top_k", int, False, 10),
            ("--min_weight", float, False, 0.0),
        ],
    },
    "find_paths": {
        "method": "find_paths",
        "args": [
            ("--source", str, True),
            ("--target", str, True),
            ("--top_k", int, False, 5),
            ("--max_hops", int, False, 4),
        ],
    },
    "get_subgraph": {
        "method": "get_subgraph",
        "args": [
            ("--node_ids", str, True),  # JSON list
            ("--depth", int, False, 1),
            ("--min_weight", float, False, 0.01),
        ],
    },
    "get_top_nodes": {
        "method": "get_top_nodes",
        "args": [
            ("--top_k", int, False, 20),
            ("--layer", int, False, None),
            ("--layer_range", str, False, None),  # JSON list
            ("--node_type", str, False, None),
            ("--position", int, False, None),
            ("--sort_by", str, False, "attribution"),
        ],
    },
    "search_nodes": {
        "method": "search_nodes",
        "args": [
            ("--query", str, True),
            ("--top_k", int, False, 10),
        ],
    },
    # Model interventions (stubs)
    "patch_node": {
        "method": "patch_node",
        "args": [
            ("--node_id", str, True),
            ("--clean_input", str, True),
            ("--corrupted_input", str, True),
            ("--metric", str, False, "logit_diff"),
            ("--target_tokens", str, False, None),  # JSON list
        ],
    },
    "patch_edge": {
        "method": "patch_edge",
        "args": [
            ("--source", str, True),
            ("--target", str, True),
            ("--clean_input", str, True),
            ("--corrupted_input", str, True),
            ("--metric", str, False, "logit_diff"),
            ("--target_tokens", str, False, None),
        ],
    },
    "ablate_nodes": {
        "method": "ablate_nodes",
        "args": [
            ("--node_ids", str, True),  # JSON list
            ("--input", str, True),
            ("--method", str, False, "mean"),
            ("--metric", str, False, "logit_diff"),
            ("--target_tokens", str, False, None),
        ],
    },
    "run_model": {
        "method": "run_model",
        "args": [
            ("--input", str, True),
            ("--top_k", int, False, 10),
            ("--target_tokens", str, False, None),
        ],
    },
    "test_circuit_faithfulness": {
        "method": "test_circuit_faithfulness",
        "args": [
            ("--circuit_nodes", str, True),  # JSON list
            ("--input", str, True),
            ("--metric", str, False, "logit_diff"),
            ("--target_tokens", str, False, None),
        ],
    },
    # Component inspection (stubs)
    "get_attention_pattern": {
        "method": "get_attention_pattern",
        "args": [
            ("--head", str, True),
            ("--input", str, True),
            ("--top_k_per_position", int, False, 5),
        ],
    },
    "logit_lens": {
        "method": "logit_lens",
        "args": [
            ("--layer", int, True),
            ("--position", int, True),
            ("--input", str, True),
            ("--top_k", int, False, 10),
        ],
    },
    "get_max_activating_examples": {
        "method": "get_max_activating_examples",
        "args": [
            ("--node_id", str, True),
            ("--k", int, False, 10),
            ("--dataset", str, False, "default"),
        ],
    },
    "get_node_activation": {
        "method": "get_node_activation",
        "args": [
            ("--node_id", str, True),
            ("--input", str, True),
        ],
    },
    # State management
    "note": {
        "method": "note",
        "args": [
            ("--content", str, True),
            ("--tags", str, False, None),  # JSON list
        ],
    },
    "get_notes": {
        "method": "get_notes",
        "args": [
            ("--tags", str, False, None),  # JSON list
            ("--last_n", int, False, None),
        ],
    },
    "get_progress": {
        "method": "get_progress",
        "args": [],
    },
}


def _parse_json_arg(val: str | None) -> Any:
    """Parse a CLI argument that might be a JSON list/object."""
    if val is None:
        return None
    try:
        return json.loads(val)
    except (json.JSONDecodeError, TypeError):
        return val


def _dispatch(tools: CircuitAnalysisTools, tool_name: str, raw_args: list[str]) -> str:
    """Parse args for a single tool call and return JSON string."""
    tool_spec = TOOL_REGISTRY.get(tool_name)
    if tool_spec is None:
        return json.dumps({"error": f"Unknown tool '{tool_name}'. Available: {', '.join(TOOL_REGISTRY)}"})

    tool_parser = argparse.ArgumentParser(prog=tool_name, exit_on_error=False)
    for arg_def in tool_spec["args"]:
        name = arg_def[0]
        atype = arg_def[1]
        required = arg_def[2]
        default = arg_def[3] if len(arg_def) > 3 else None
        tool_parser.add_argument(name, type=atype, required=required, default=default)

    try:
        tool_args = tool_parser.parse_args(raw_args)
    except (argparse.ArgumentError, SystemExit) as e:
        return json.dumps({"error": f"Bad arguments for {tool_name}: {e}"})

    method = getattr(tools, tool_spec["method"])
    kwargs = {}
    for arg_def in tool_spec["args"]:
        param_name = arg_def[0].lstrip("-")
        val = getattr(tool_args, param_name)

        if param_name in ("node_ids", "circuit_nodes", "tags", "target_tokens", "layer_range"):
            val = _parse_json_arg(val)

        if param_name == "input" and tool_spec["method"] in (
            "ablate_nodes", "run_model", "test_circuit_faithfulness",
            "get_attention_pattern", "logit_lens", "get_node_activation",
        ):
            param_name = "input_text"

        kwargs[param_name] = val

    try:
        result = method(**kwargs)
        tools._save_state()
        return json.dumps(result, indent=2)
    except NotImplementedError as e:
        tools._save_state()
        return json.dumps({"error": str(e), "status": "not_implemented"})
    except Exception as e:
        tools._save_state()
        return json.dumps({"error": str(e), "type": type(e).__name__})


def repl(tools: CircuitAnalysisTools) -> None:
    """Interactive REPL. One command per line, JSON response per line.

    Usage (from an agent via Bash):
        echo 'get_top_nodes --top_k 5' | python3 circuit_analysis_tools.py --graph data.json repl

    Or multi-command:
        printf 'get_top_nodes --top_k 5\\nget_node_info --node_id 9_300_5\\n' | python3 ... repl

    Reads stdin line-by-line. Each line is: tool_name [--arg val ...]
    Prints one JSON object per line to stdout.
    Sends "READY" on stderr when waiting for input (agents can ignore this).
    """
    import shlex

    print(json.dumps({
        "status": "repl_started",
        "graph_nodes": len(tools.nodes_by_id),
        "graph_edges": sum(len(v) for v in tools.adj_out.values()),
        "available_tools": list(TOOL_REGISTRY.keys()),
    }))
    sys.stdout.flush()

    for line in sys.stdin:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line in ("quit", "exit"):
            break

        try:
            parts = shlex.split(line)
        except ValueError as e:
            print(json.dumps({"error": f"Parse error: {e}"}))
            sys.stdout.flush()
            continue

        tool_name = parts[0]
        raw_args = parts[1:]
        print(_dispatch(tools, tool_name, raw_args))
        sys.stdout.flush()

    tools._save_state()


def main():
    parser = argparse.ArgumentParser(
        description="Circuit Analysis Agent Tools",
        usage="%(prog)s --graph <path.json> <tool_name> [--arg value ...]\n       %(prog)s --graph <path.json> repl",
    )
    parser.add_argument("--graph", required=True, help="Path to Neuronpedia-format graph JSON")
    parser.add_argument("tool", help="Tool to invoke, or 'repl' for interactive mode")

    args, remaining = parser.parse_known_args()

    # Load graph (once)
    try:
        tools = CircuitAnalysisTools(args.graph)
    except FileNotFoundError:
        print(json.dumps({"error": f"Graph file not found: {args.graph}"}))
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON in graph file: {e}"}))
        sys.exit(1)

    # REPL mode
    if args.tool == "repl":
        repl(tools)
        return

    # Single-command mode
    print(_dispatch(tools, args.tool, remaining))


if __name__ == "__main__":
    main()
