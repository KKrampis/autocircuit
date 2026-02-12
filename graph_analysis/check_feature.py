"""Inspect a transcoder feature: activation range, top logits, and example activations.

Usage:
    python -m graph_analysis.check_feature --layer 20 --feature_idx 1454
    python -m graph_analysis.check_feature --layer 20 --feature_idx 1454 --hf_repo mwhanna/gemma-scope-transcoders
"""

import argparse
import gzip
import json
import os
import struct
import zlib

import requests
from huggingface_hub import hf_hub_download


HF_ENDPOINT = os.environ.get("HF_ENDPOINT", "https://huggingface.co")


def fetch_feature_data(layer: int, feat_idx: int, hf_repo: str = "mwhanna/gemma-scope-transcoders") -> dict:
    """Fetch feature data from HuggingFace.

    Returns dict with keys: act_min, act_max, top_logits, bottom_logits, examples_quantiles.
    """
    index_path = hf_hub_download(repo_id=hf_repo, filename="features/index.json.gz")
    with open(index_path, "rb") as f:
        index = json.loads(gzip.decompress(f.read()))

    layer_meta = index[layer] if layer in index else index[str(layer)]
    bin_filename = layer_meta["filename"]
    offsets = layer_meta["offsets"]

    start, end = offsets[feat_idx], offsets[feat_idx + 1]

    url = f"{HF_ENDPOINT}/{hf_repo}/resolve/main/features/{bin_filename}"
    resp = requests.get(url, headers={"Range": f"bytes={start}-{end - 1}"})
    resp.raise_for_status()
    chunk = resp.content

    data_len = struct.unpack_from("<I", chunk, 0)[0]
    return json.loads(zlib.decompress(chunk[4 : 4 + data_len], wbits=47))


def print_feature_summary(layer: int, feat_idx: int, feat_data: dict):
    """Print a summary of feature data."""
    print(f"=== Feature {feat_idx} @ layer {layer} ===")
    print(f"act_min:       {feat_data.get('act_min')}")
    print(f"act_max:       {feat_data.get('act_max')}")
    print(f"Top logits:    {feat_data.get('top_logits', [])[:10]}")
    print(f"Bottom logits: {feat_data.get('bottom_logits', [])[:10]}")

    for quantile in feat_data.get("examples_quantiles", []):
        print(f"\n-- {quantile['quantile_name']} --")
        for ex in quantile["examples"][:2]:
            tokens = ex["tokens"]
            acts = ex["tokens_acts_list"]
            highlighted = [f"[{t}]" if a > 0 else t for t, a in zip(tokens, acts)]
            print("  " + "".join(highlighted))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect a transcoder feature from HuggingFace.")
    parser.add_argument("--layer", type=int, required=True, help="Transformer layer")
    parser.add_argument("--feature_idx", type=int, required=True, help="Feature index")
    parser.add_argument("--hf_repo", default="mwhanna/gemma-scope-transcoders", help="HuggingFace repo ID")
    args = parser.parse_args()

    feat_data = fetch_feature_data(args.layer, args.feature_idx, args.hf_repo)
    print_feature_summary(args.layer, args.feature_idx, feat_data)
