#!/usr/bin/env python3
"""Deep validation suite — the experiments a top-conference reviewer will ask for.

Builds on cross_prompt_validation.py. Four stages, each targeting a specific
reviewer objection to the §3.7 circuit-ablation result.

STAGE A — Layer-stratified ablation ("is it just L0 token deletion?")
    The single biggest objection: 40/180 circuit features are at L0 (the
    embedding layer), so suppressing them ~ deleting the input-token
    representations of the entities. The " to" collapse could then be "the model
    parrots the connective once you erase the content words," NOT evidence of a
    relational-reasoning circuit. We localize the necessity by ablating the
    circuit one layer-band at a time, and — decisively — ablate the circuit with
    L0 EXCLUDED (140 features at L1+). If the collapse survives without L0, the
    token-deletion explanation fails and mid/late features carry real causal
    weight. We also ablate an L1+-matched random null to keep the contrast.
    Bands map onto the paper's 3-phase architecture (Phase1 L0-L4, Phase2 L5-L9).

STAGE B — Strength titration ("is the effect an artifact of the blunt -80?")
    Reviewers expect dose-response, not one large hammer. We sweep |strength| for
    the full circuit vs. the matched null. If the circuit collapses at a LOWER
    strength than the null, it is more load-bearing (easier to break).

STAGE C-proxy — Behavioral interaction ("is Phase 1 upstream of Phase 2?")
    True path patching is not available via the steering API (it needs direct
    model access). As a weaker proxy we test whether the marginal effect of
    suppressing Phase 2 (L5-L9) DEPENDS on whether Phase 1 (L1-L4) is intact.
    If Phase 1 is upstream, suppressing it should change what Phase 2 does.
    NOT path patching; reported as a behavioral interaction only.

STAGE D — Held-out prompts ("n=5 is small; does the circuit generalize?")
    The 180-feature circuit was defined from 5 specific prompts. We apply the
    SAME fixed circuit to NEW analogy prompts it was never derived from. If
    ablation reproduces the connective collapse on held-out analogies, the
    circuit generalizes beyond its defining set. (No per-prompt graph exists for
    these, so no matched null here — specificity was established on the 5
    defining prompts; this stage tests generalization of the signature.)

~54 API calls. Crash-safe (saves after every call), resumable (skips completed),
handles 429 (waits) and transient 500 (retries with backoff).
"""

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "exp2_steering"))
from run_steering import make_feature, steer  # noqa: E402
from run_validation import sample_non_circuit_features, parse_node_id  # noqa: E402

RATE_LIMIT_WINDOW = 65 * 60
DELAY = 2.0
NULL_SEED = 11  # distinct from cross_prompt (7) and specificity (42)

CIRCUIT_JSON = HERE / "analogical_circuit_180features.json"
OUTPUT = HERE / "deep_validation_results.json"
EXP4 = HERE.parent / "exp4_scale" / "circuits"
EXP7 = HERE.parent / "exp7_remaining_analogy_validation" / "graphs"

# 5 defining prompts (graphs available)
PROMPTS = {
    "analog_berlin":  ("Paris is to France as Berlin is to", "Germany", EXP4 / "analogy_graph.json"),
    "analog_rome":    ("Paris is to France as Rome is to",   "Italy",   EXP7 / "analog_rome.json"),
    "analog_tokyo":   ("Paris is to France as Tokyo is to",  "Japan",   EXP7 / "analog_tokyo.json"),
    "analog_teacher": ("Doctor is to hospital as teacher is to", "school", EXP7 / "analog_teacher.json"),
    "analog_bird":    ("Fish is to water as bird is to",     "air",     EXP7 / "analog_bird.json"),
}

# Stage D: held-out analogies (NOT used to define the circuit), same template
HELDOUT = {
    "heldout_vienna": ("Lisbon is to Portugal as Vienna is to", "Austria"),
    "heldout_oslo":   ("Athens is to Greece as Oslo is to",     "Norway"),
    "heldout_knife":  ("Pen is to writing as knife is to",      "cutting"),
    "heldout_ant":    ("Bee is to hive as ant is to",           "colony"),
}


def is_error(r):  return isinstance(r, dict) and "error" in r
def is_429(r):    return is_error(r) and "429" in str(r.get("error", ""))
def is_500(r):    return is_error(r) and "500" in str(r.get("error", ""))


def is_transient(r):
    """500 or a network-level error (timeout / connection reset) — worth retrying."""
    if not is_error(r):
        return False
    e = str(r.get("error", "")).lower()
    return ("500" in e or "timed out" in e or "timeout" in e
            or "urlopen" in e or "connection" in e or "reset" in e)


def safe_steer(prompt, features, strength_multiplier=4, label="", max_retries=6):
    n = 0
    while True:
        r = steer(prompt, features, strength_multiplier=strength_multiplier)
        if is_429(r):
            print(f"  [{label}] 429; sleeping {RATE_LIMIT_WINDOW}s...", flush=True)
            time.sleep(RATE_LIMIT_WINDOW); continue
        if is_transient(r) and n < max_retries:
            n += 1; w = 10 * n
            print(f"  [{label}] transient err ({r.get('error')!r}) try {n}/{max_retries}; "
                  f"retry in {w}s...", flush=True)
            time.sleep(w); continue
        return r


def load_circuit():
    d = json.load(open(CIRCUIT_JSON))
    feats, pairs = [], set()
    for f in d["features"]:
        l, i, _ = parse_node_id(f["node_ids"][0])
        feats.append({"layer": l, "index": i}); pairs.add((l, i))
    return feats, pairs


def in_band(layer, band):
    if band == "L0":        return layer == 0
    if band == "L1-L4":     return 1 <= layer <= 4
    if band == "L5-L9":     return 5 <= layer <= 9
    if band == "L10+":      return layer >= 10
    if band == "L1+":       return layer >= 1
    if band == "L1-L9":     return 1 <= layer <= 9
    raise ValueError(band)


def sample_null_in_layers(graph_path, circuit_set, layers_pred, n, seed):
    """Sample n non-circuit features whose layer satisfies layers_pred."""
    pool = sample_non_circuit_features(graph_path, circuit_set, n=10_000, seed=seed)
    filtered = [f for f in pool if layers_pred(f["layer"])]
    return filtered[:n]


def tok(r):  return None if is_error(r) else r.get("first_steered_token")
def lp(r):   return None if is_error(r) else r.get("first_steered_logprob")
def disrupted(r, expected):
    if is_error(r): return None
    return (r.get("first_steered_token") or "").strip().lower() != expected.strip().lower()


def save(results): json.dump(results, open(OUTPUT, "w"), indent=2)


def main():
    circuit, circuit_set = load_circuit()
    by_band = {b: [f for f in circuit if in_band(f["layer"], b)]
               for b in ["L0", "L1-L4", "L5-L9", "L10+", "L1+", "L1-L9"]}
    print("Circuit band sizes:", {b: len(v) for b, v in by_band.items()}, "\n", flush=True)

    results = json.load(open(OUTPUT)) if OUTPUT.exists() else {"A": {}, "B": {}, "C": {}, "D": {}}
    for k in ("A", "B", "C", "D"): results.setdefault(k, {})

    # ---------- STAGE A: layer-stratified ablation ----------
    print("="*72, "\nSTAGE A — layer-stratified ablation\n", "="*72, flush=True)
    A_BANDS = ["L0", "L1-L4", "L5-L9", "L10+", "L1+"]
    for pname, (prompt, expected, graph) in PROMPTS.items():
        results["A"].setdefault(pname, {})
        for band in A_BANDS:
            key = f"circuit:{band}"
            if key in results["A"][pname] and not is_error(results["A"][pname][key]["result"]):
                continue
            feats = [make_feature(f["layer"], f["index"], -20) for f in by_band[band]]
            r = safe_steer(prompt, feats, label=f"A {pname} {band}")
            results["A"][pname][key] = {"band": band, "n": len(feats), "result": r,
                                        "disrupted": disrupted(r, expected)}
            print(f"  [A] {pname:15s} circuit {band:6s} (n={len(feats):3d}) -> "
                  f"{tok(r)!r:16s} lp={lp(r)}  disrupt={disrupted(r, expected)}", flush=True)
            save(results); time.sleep(DELAY)
        # L1+-matched null (140 random non-circuit L1+ features)
        if "null:L1+" not in results["A"][pname] or is_error(results["A"][pname]["null:L1+"]["result"]):
            sampled = sample_null_in_layers(graph, circuit_set, lambda L: L >= 1,
                                            n=len(by_band["L1+"]), seed=NULL_SEED)
            feats = [make_feature(f["layer"], f["index"], -20) for f in sampled]
            r = safe_steer(prompt, feats, label=f"A {pname} null:L1+")
            results["A"][pname]["null:L1+"] = {"band": "L1+_null", "n": len(feats), "result": r,
                                               "disrupted": disrupted(r, expected),
                                               "sampled": [(f["layer"], f["index"]) for f in sampled]}
            print(f"  [A] {pname:15s} NULL    L1+    (n={len(feats):3d}) -> "
                  f"{tok(r)!r:16s} lp={lp(r)}  disrupt={disrupted(r, expected)}", flush=True)
            save(results); time.sleep(DELAY)

    # ---------- STAGE B: strength titration ----------
    print("\n", "="*72, "\nSTAGE B — strength titration\n", "="*72, flush=True)
    STRENGTHS = [-2, -5, -10, -20, -40]
    for pname in ["analog_berlin", "analog_tokyo"]:
        prompt, expected, graph = PROMPTS[pname]
        results["B"].setdefault(pname, {})
        null_full = sample_non_circuit_features(graph, circuit_set, n=180, seed=NULL_SEED)
        for s in STRENGTHS:
            for cond, feats_src in [("circuit", circuit), ("null", null_full)]:
                key = f"{cond}:{s}"
                if key in results["B"][pname] and not is_error(results["B"][pname][key]["result"]):
                    continue
                feats = [make_feature(f["layer"], f["index"], s) for f in feats_src]
                r = safe_steer(prompt, feats, label=f"B {pname} {cond} s={s}")
                results["B"][pname][key] = {"cond": cond, "strength": s, "result": r,
                                            "disrupted": disrupted(r, expected)}
                print(f"  [B] {pname:13s} {cond:7s} s={s:>3} -> {tok(r)!r:16s} "
                      f"lp={lp(r)}  disrupt={disrupted(r, expected)}", flush=True)
                save(results); time.sleep(DELAY)

    # ---------- STAGE C-proxy: Phase1 x Phase2 interaction ----------
    print("\n", "="*72, "\nSTAGE C-proxy — Phase1 x Phase2 interaction (behavioral, NOT path patching)\n",
          "="*72, flush=True)
    p1 = by_band["L1-L4"]; p2 = by_band["L5-L9"]
    for pname in ["analog_berlin", "analog_rome"]:
        prompt, expected, graph = PROMPTS[pname]
        results["C"].setdefault(pname, {})
        conds = {
            "none":  [],
            "P1":    p1,
            "P2":    p2,
            "P1+P2": p1 + p2,
        }
        for cname, feats_src in conds.items():
            if cname in results["C"][pname] and not is_error(results["C"][pname][cname]["result"]):
                continue
            if cname == "none":  # baseline read from any steered default; skip dedicated call
                continue
            feats = [make_feature(f["layer"], f["index"], -20) for f in feats_src]
            r = safe_steer(prompt, feats, label=f"C {pname} {cname}")
            results["C"][pname][cname] = {"cond": cname, "n": len(feats), "result": r,
                                          "disrupted": disrupted(r, expected),
                                          "baseline_text": r.get("default_text") if not is_error(r) else None}
            print(f"  [C] {pname:13s} {cname:6s} (n={len(feats):3d}) -> {tok(r)!r:16s} "
                  f"lp={lp(r)}  disrupt={disrupted(r, expected)}", flush=True)
            save(results); time.sleep(DELAY)

    # ---------- STAGE D: held-out prompts ----------
    print("\n", "="*72, "\nSTAGE D — held-out analogies (fixed circuit, never used to define it)\n",
          "="*72, flush=True)
    full_circuit = [make_feature(f["layer"], f["index"], -20) for f in circuit]
    for pname, (prompt, expected) in HELDOUT.items():
        if pname in results["D"] and not is_error(results["D"][pname]["result"]):
            continue
        r = safe_steer(prompt, full_circuit, label=f"D {pname}")
        results["D"][pname] = {"prompt": prompt, "expected": expected, "result": r,
                               "disrupted": disrupted(r, expected),
                               "baseline_text": r.get("default_text") if not is_error(r) else None}
        bt = "ERR" if is_error(r) else r.get("first_default_token")
        print(f"  [D] {pname:15s} baseline={bt!r:12s} circuit-ablation -> "
              f"{tok(r)!r:12s} lp={lp(r)}  disrupt={disrupted(r, expected)}", flush=True)
        save(results); time.sleep(DELAY)

    print("\nDONE. Results in", OUTPUT, flush=True)


if __name__ == "__main__":
    main()
