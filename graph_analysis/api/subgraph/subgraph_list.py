"""Fetch subgraph list from Neuronpedia API.

Usage:
    python -m graph_analysis.api.subgraph.subgraph_list --model_id gemma-2-2b --slug gemma-fact-dallas-austin --api_key $NEURONPEDIA_API_KEY
"""

import argparse
import json

import requests


def fetch_subgraph_list(model_id: str, slug: str, api_key: str) -> list[dict]:
    """Fetch subgraphs for a graph from Neuronpedia API.

    POST https://www.neuronpedia.org/api/graph/subgraph/list

    Returns list of subgraph dicts, each with keys:
        id, displayName, pinnedIds, supernodes, clerps,
        pruningThreshold, densityThreshold, etc.
    """
    url = "https://www.neuronpedia.org/api/graph/subgraph/list"
    resp = requests.post(
        url,
        headers={"x-api-key": api_key, "Content-Type": "application/json"},
        json={"modelId": model_id, "slug": slug},
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("subgraphs", [])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch subgraph list from Neuronpedia API.")
    parser.add_argument("--model_id", required=True, help="Model ID (e.g., gemma-2-2b)")
    parser.add_argument("--slug", required=True, help="Graph slug")
    parser.add_argument("--api_key", required=True, help="Neuronpedia API key")
    args = parser.parse_args()

    subgraphs = fetch_subgraph_list(args.model_id, args.slug, args.api_key)

    if not subgraphs:
        print(f"No subgraphs found for {args.model_id}/{args.slug}")
    else:
        print(f"Found {len(subgraphs)} subgraph(s):")
        print("node format: layer_featureidx_pos")
        for sg in subgraphs:
            print(f"\n  graphMetadataId: {sg['graphMetadataId']}")
            print(f"  displayName: {sg.get('displayName', '(none)')}")
            print(f"  pinnedIds: {len(sg['pinnedIds'])} nodes")
            print(f"  supernodes: {len(sg['supernodes'])} groups")
            for sn in sg["supernodes"]:
                print(f"    - {sn[0]}: {len(sn) - 1} nodes")
                for node_id in sn[1:]:
                    print(f"      - {node_id}")
