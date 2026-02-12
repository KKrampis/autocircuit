# %%

import gzip
import json
import os
import struct
import zlib
import requests
from huggingface_hub import hf_hub_download

# %%

HF_ENDPOINT = os.environ.get("HF_ENDPOINT", "https://huggingface.co")

LAYER = 20
FEATURE_IDX = 1454

# %%

def fetch_feature_data(layer, feat_idx, hf_repo="mwhanna/gemma-scope-transcoders"):
    # 1. Download index.json.gz via huggingface_hub (cached to disk automatically)
    index_path = hf_hub_download(repo_id=hf_repo, filename="features/index.json.gz")
    with open(index_path, "rb") as f:
        index = json.loads(gzip.decompress(f.read()))

    # index is keyed by layer as int or str
    layer_meta = index[layer] if layer in index else index[str(layer)]
    bin_filename = layer_meta["filename"]
    offsets = layer_meta["offsets"]

    start, end = offsets[feat_idx], offsets[feat_idx + 1]

    # 2. Range-request just the bytes for this feature from the .bin file
    url = f"{HF_ENDPOINT}/{hf_repo}/resolve/main/features/{bin_filename}"
    resp = requests.get(url, headers={"Range": f"bytes={start}-{end - 1}"})
    resp.raise_for_status()
    chunk = resp.content

    # 3. Parse: 4-byte LE length prefix + compressed JSON (matches pako.inflate in JS)
    data_len = struct.unpack_from("<I", chunk, 0)[0]
    return json.loads(zlib.decompress(chunk[4 : 4 + data_len], wbits=47))

feat_data = fetch_feature_data(LAYER, FEATURE_IDX)

print(f"=== Feature {FEATURE_IDX} @ layer {LAYER} ===")
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

# %%