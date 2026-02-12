"""Fetch graph metadata from Neuronpedia API.

Usage:
    python -m graph_analysis.api.graph.graph_get --url "https://www.neuronpedia.org/gemma-2-2b/graph?slug=gemma-michael-jordan-es"

    python -m graph_analysis.api.graph.graph_get --model_id gemma-2-2b --slug gemma-michael-jordan-es
"""

import argparse
import json
from urllib.parse import urlparse, parse_qs

import requests


def parse_neuronpedia_url(url: str) -> tuple[str, str]:
    """Extract model_id and slug from a Neuronpedia graph URL.

    Args:
        url: e.g. "https://www.neuronpedia.org/gemma-2-2b/graph?slug=gemma-michael-jordan-es&..."

    Returns:
        (model_id, slug) tuple.
    """
    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")
    model_id = parts[0]
    query = parse_qs(parsed.query)
    slug = query["slug"][0]
    return model_id, slug


def fetch_graph_metadata(model_id: str, slug: str) -> dict:
    """Fetch graph metadata from Neuronpedia API.

    GET https://www.neuronpedia.org/api/graph/{modelId}/{slug}

    Returns dict with keys: id, modelId, slug, prompt, promptTokens, url, etc.
    """
    api_url = f"https://www.neuronpedia.org/api/graph/{model_id}/{slug}"
    resp = requests.get(api_url)
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch graph metadata from Neuronpedia API.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="Neuronpedia graph URL")
    group.add_argument("--model_id", help="Model ID (use with --slug)")
    parser.add_argument("--slug", help="Graph slug (use with --model_id)")
    args = parser.parse_args()

    if args.url:
        model_id, slug = parse_neuronpedia_url(args.url)
    else:
        if not args.slug:
            parser.error("--slug required when using --model_id")
        model_id, slug = args.model_id, args.slug

    metadata = fetch_graph_metadata(model_id, slug)
    print(json.dumps(metadata, indent=2))
