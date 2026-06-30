#!/usr/bin/env python3
"""
Experiment 2: Full Causal Validation via Steering

Now that we know the API works, run systematic experiments:
1. Baseline (no steering)
2. Suppress each backbone feature individually (necessity)
3. Suppress all backbone features (full necessity)
4. Suppress non-backbone high-attribution features (specificity)
5. Boost hub on neutral/corrupted prompts (sufficiency)
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

def load_api_key():
    if os.environ.get("NEURONPEDIA_API_KEY"):
        return os.environ["NEURONPEDIA_API_KEY"]
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            if line.startswith("NEURONPEDIA_API_KEY="):
                return line.split("=", 1)[1].strip()
    sys.exit("No API key found")

API_KEY = load_api_key()
BASE_URL = "https://www.neuronpedia.org/api"
DELAY = 2.0  # seconds between API calls


def api_post(endpoint, data):
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json",
        "User-Agent": "AutoCircuit-Experiment/1.0",
    }
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")[:500]
        return {"error": f"HTTP {e.code}: {e.reason}", "body": err_body}
    except Exception as e:
        return {"error": str(e)}


def steer(prompt, features, strength_multiplier=4, n_tokens=5):
    """Run a steering experiment and return parsed result."""
    data = {
        "modelId": "gemma-2-2b",
        "prompt": prompt,
        "features": features,
        "temperature": 0,
        "n_tokens": n_tokens,
        "freq_penalty": 0,
        "seed": 42,
        "strength_multiplier": strength_multiplier,
    }
    raw = api_post("/steer", data)

    if "error" in raw:
        return {"error": raw["error"], "body": raw.get("body", "")}

    # Extract first token probabilities
    default_text = raw.get("DEFAULT", "")
    steered_text = raw.get("STEERED", "")

    # Get log probs for first steered token
    steered_lps = raw.get("steeredLogProbs", [])
    default_lps = raw.get("defaultLogProbs", [])

    first_steered_token = steered_lps[0] if steered_lps else {}
    first_default_token = default_lps[0] if default_lps else {}

    return {
        "default_text": default_text,
        "steered_text": steered_text,
        "first_steered_token": first_steered_token.get("token", "?"),
        "first_steered_logprob": first_steered_token.get("logprob", None),
        "first_steered_top5": first_steered_token.get("topLogprobs", []),
        "first_default_token": first_default_token.get("token", "?"),
        "first_default_logprob": first_default_token.get("logprob", None),
        "first_default_top5": first_default_token.get("topLogprobs", []),
    }


def make_feature(layer, index, strength):
    return {
        "modelId": "gemma-2-2b",
        "layer": f"{layer}-gemmascope-transcoder-16k",
        "index": index,
        "strength": strength,
    }


# ---------------------------------------------------------------------------
# Backbone features
# ---------------------------------------------------------------------------

BACKBONE = {
    "L16_hub":     {"layer": 16, "index": 11463, "role": "Central hub"},
    "L19_relay":   {"layer": 19, "index": 4063,  "role": "Cascade relay 1"},
    "L21_relay":   {"layer": 21, "index": 12675, "role": "Cascade relay 2"},
    "L22_relay":   {"layer": 22, "index": 9740,  "role": "Cascade relay 3"},
    "L22_inhib":   {"layer": 22, "index": 15670, "role": "Inhibitory pathway"},
    "L23_relay":   {"layer": 23, "index": 6638,  "role": "Cascade relay 4"},
    "L23_integ":   {"layer": 23, "index": 5917,  "role": "Late integrator"},
    "L25_amp":     {"layer": 25, "index": 4717,  "role": "Final amplifier"},
}

PROMPT = "DNA stands for deoxyribonucleic"
STRENGTH = -20


def run_experiments():
    results = []

    # ---- Experiment A: Individual suppression (necessity) ----
    print("=" * 60)
    print("A. Individual feature suppression (necessity tests)")
    print("=" * 60)

    for name, feat in BACKBONE.items():
        print(f"\n  Suppressing {name} ({feat['role']})...")
        features = [make_feature(feat["layer"], feat["index"], STRENGTH)]
        r = steer(PROMPT, features)
        r["experiment"] = f"suppress_{name}"
        r["description"] = f"Suppress {name} ({feat['role']})"
        results.append(r)

        if "error" not in r:
            print(f"    Default: ...{r['first_default_token']} | "
                  f"Steered: ...{r['first_steered_token']}")
            print(f"    Steered text: {r['steered_text']}")
        else:
            print(f"    ERROR: {r['error']}")
        time.sleep(DELAY)

    # ---- Experiment B: Full cascade suppression ----
    print(f"\n{'='*60}")
    print("B. Full cascade suppression")
    print("=" * 60)

    all_features = [make_feature(f["layer"], f["index"], STRENGTH)
                    for f in BACKBONE.values()]
    print(f"  Suppressing all {len(all_features)} backbone features...")
    r = steer(PROMPT, all_features)
    r["experiment"] = "suppress_all_backbone"
    r["description"] = f"Suppress all {len(BACKBONE)} backbone features"
    results.append(r)
    if "error" not in r:
        print(f"    Default: {r['default_text']}")
        print(f"    Steered: {r['steered_text']}")
    time.sleep(DELAY)

    # ---- Experiment C: Suppression strength sweep on hub ----
    print(f"\n{'='*60}")
    print("C. Hub suppression strength sweep")
    print("=" * 60)

    for strength in [-5, -10, -20, -40]:
        print(f"  Strength = {strength}...")
        features = [make_feature(16, 11463, strength)]
        r = steer(PROMPT, features)
        r["experiment"] = f"hub_strength_{strength}"
        r["description"] = f"Suppress hub at strength={strength}"
        results.append(r)
        if "error" not in r:
            print(f"    Steered first token: {r['first_steered_token']} "
                  f"(logprob: {r['first_steered_logprob']})")
        time.sleep(DELAY)

    # ---- Experiment D: Boost hub on corrupted prompt (sufficiency) ----
    print(f"\n{'='*60}")
    print("D. Hub boost on corrupted/neutral prompts (sufficiency)")
    print("=" * 60)

    sufficiency_prompts = [
        ("DNA stands for extraordinary", "corrupted (bonucleic → extraordinary)"),
        ("The chemical compound is", "neutral chemistry context"),
        ("The weather today is", "irrelevant context"),
    ]

    for prompt, desc in sufficiency_prompts:
        # First get baseline
        print(f"\n  Prompt: '{prompt}' ({desc})")
        print(f"    Baseline (no steering)...")
        r_base = steer(prompt, [])
        if "error" not in r_base:
            print(f"      → {r_base['steered_text']}")
        time.sleep(DELAY)

        # Then boost hub
        print(f"    Boosting hub (+20)...")
        features = [make_feature(16, 11463, 20)]
        r_boost = steer(prompt, features)
        r_boost["experiment"] = f"boost_hub_{prompt[:20].replace(' ','_')}"
        r_boost["description"] = f"Boost hub on: {desc}"
        r_boost["baseline_text"] = r_base.get("steered_text", r_base.get("default_text", "?"))
        results.append(r_boost)
        if "error" not in r_boost:
            print(f"      → {r_boost['steered_text']}")
        time.sleep(DELAY)

    # ---- Experiment E: Suppress non-backbone feature (specificity) ----
    print(f"\n{'='*60}")
    print("E. Suppress non-backbone features (specificity control)")
    print("=" * 60)

    # Pick features NOT in backbone but with high activation
    # L0 feature 9026 is in backbone, so use a different L0 feature
    # Use some arbitrary high-activation non-backbone features
    non_backbone = [
        {"layer": 0, "index": 9936, "desc": "L0 non-backbone feature"},
        {"layer": 7, "index": 100, "desc": "L7 arbitrary feature"},
    ]

    for feat in non_backbone:
        print(f"\n  Suppressing {feat['desc']} (L{feat['layer']}, idx {feat['index']})...")
        features = [make_feature(feat["layer"], feat["index"], STRENGTH)]
        r = steer(PROMPT, features)
        r["experiment"] = f"suppress_nonbackbone_L{feat['layer']}_{feat['index']}"
        r["description"] = f"Suppress {feat['desc']} (specificity control)"
        results.append(r)
        if "error" not in r:
            print(f"    Default: ...{r.get('first_default_token','?')} | "
                  f"Steered: ...{r['first_steered_token']}")
            print(f"    Steered text: {r['steered_text']}")
        time.sleep(DELAY)

    return results


def format_markdown(results):
    lines = [
        "# Experiment 2: Causal Validation via Steering",
        "",
        f"**Model**: gemma-2-2b",
        f"**Prompt**: \"{PROMPT}\"",
        f"**Default completion**: \"acid. It is a\"",
        f"**Suppression strength**: {STRENGTH} (unless noted)",
        "",
        "## A. Individual Feature Suppression (Necessity)",
        "",
        "| Feature | Role | Default 1st Token | Steered 1st Token | Steered Text | Acid Disrupted? |",
        "|---------|------|-------------------|-------------------|--------------|----------------|",
    ]

    for r in results:
        if not r.get("experiment", "").startswith("suppress_L"):
            continue
        name = r["experiment"].replace("suppress_", "")
        role = r.get("description", "").split("(")[-1].rstrip(")")
        if "error" in r:
            lines.append(f"| {name} | {role} | ERROR | ERROR | {r['error']} | ERROR |")
        else:
            dt = r.get("first_default_token", "?")
            st = r.get("first_steered_token", "?")
            text = r.get("steered_text", "?")
            # Remove the prompt prefix from steered text
            text_short = text.replace("<bos>DNA stands for deoxyribonucleic", "").strip()[:40]
            disrupted = "YES" if "acid" not in text.lower() else "no"
            lines.append(f"| {name} | {role} | {dt} | {st} | ...{text_short} | {disrupted} |")

    lines.append("")

    # Full cascade suppression
    lines.append("## B. Full Cascade Suppression")
    lines.append("")
    for r in results:
        if r.get("experiment") == "suppress_all_backbone":
            if "error" in r:
                lines.append(f"**Result**: ERROR — {r['error']}")
            else:
                lines.append(f"- **Default**: {r.get('default_text', '?')}")
                lines.append(f"- **Steered**: {r.get('steered_text', '?')}")
                disrupted = "acid" not in r.get("steered_text", "").lower()
                lines.append(f"- **Acid disrupted**: {'YES' if disrupted else 'no'}")
    lines.append("")

    # Strength sweep
    lines.append("## C. Hub Suppression Strength Sweep")
    lines.append("")
    lines.append("| Strength | 1st Steered Token | Logprob | Text |")
    lines.append("|----------|-------------------|---------|------|")
    for r in results:
        if not r.get("experiment", "").startswith("hub_strength"):
            continue
        s = r["experiment"].split("_")[-1]
        if "error" in r:
            lines.append(f"| {s} | ERROR | — | {r['error']} |")
        else:
            st = r.get("first_steered_token", "?")
            lp = r.get("first_steered_logprob", "?")
            text = r.get("steered_text", "?").replace("<bos>DNA stands for deoxyribonucleic", "").strip()[:40]
            lines.append(f"| {s} | {st} | {lp} | ...{text} |")
    lines.append("")

    # Sufficiency
    lines.append("## D. Hub Boost on Corrupted/Neutral Prompts (Sufficiency)")
    lines.append("")
    for r in results:
        if not r.get("experiment", "").startswith("boost_hub"):
            continue
        lines.append(f"### {r.get('description', '?')}")
        if "error" in r:
            lines.append(f"ERROR: {r['error']}")
        else:
            lines.append(f"- **Baseline**: {r.get('baseline_text', '?')}")
            lines.append(f"- **With hub boost**: {r.get('steered_text', '?')}")
        lines.append("")

    # Specificity
    lines.append("## E. Non-Backbone Suppression (Specificity Control)")
    lines.append("")
    for r in results:
        if not r.get("experiment", "").startswith("suppress_nonbackbone"):
            continue
        lines.append(f"### {r.get('description', '?')}")
        if "error" in r:
            lines.append(f"ERROR: {r['error']}")
        else:
            lines.append(f"- **Default**: {r.get('default_text', '?')}")
            lines.append(f"- **Steered**: {r.get('steered_text', '?')}")
            disrupted = "acid" not in r.get("steered_text", "").lower()
            lines.append(f"- **Acid disrupted**: {'YES' if disrupted else 'no'}")
        lines.append("")

    return "\n".join(lines)


def main():
    print("Experiment 2: Full Causal Validation via Steering\n")

    results = run_experiments()

    output_dir = Path(__file__).parent
    with open(output_dir / "full_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nRaw results saved to {output_dir / 'full_results.json'}")

    md = format_markdown(results)
    with open(output_dir / "results.md", "w") as f:
        f.write(md)
    print(f"Markdown saved to {output_dir / 'results.md'}")


if __name__ == "__main__":
    main()
