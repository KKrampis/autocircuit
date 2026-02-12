"""Direct feature-level interventions: zero, scale, or swap individual features.

Use this when you want to intervene on specific features (layer, pos, feature_idx)
rather than on named supernodes. Useful for:
- Zeroing language features to change output language
- Swapping features between prompts (e.g., French -> Spanish)
- Open-ended generation with feature interventions

Usage:
    # Zero out a Spanish language feature on a Spanish prompt
    python -m graph_analysis.feature_intervention \
        --target_prompt "Hecho: Michael Jordan juega al" \
        --zero 20,-1,341

    # Swap language: zero French feature, activate Spanish feature from source prompt
    python -m graph_analysis.feature_intervention \
        --target_prompt "Fait: Michael Jordan joue au" \
        --zero 20,-1,1454 \
        --source_prompt "Hecho: Michael Jordan juega al" \
        --activate 20,-1,341 \
        --scale 10

    # Open-ended generation with intervention
    python -m graph_analysis.feature_intervention \
        --target_prompt "Fait: Michael Jordan joue au" \
        --zero 20,-1,1454 \
        --source_prompt "Hecho: Michael Jordan juega al" \
        --activate 20,-1,341 \
        --scale 10 \
        --generate
"""

import argparse
import json

import torch

from graph_analysis.utils import load_model, get_top_outputs, print_top_outputs


def parse_feature_spec(spec: str) -> tuple[int, int, int]:
    """Parse 'layer,pos,feature_idx' string into tuple."""
    parts = spec.split(",")
    return int(parts[0]), int(parts[1]), int(parts[2])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Direct feature-level interventions.")
    parser.add_argument("--target_prompt", required=True, help="Prompt to run intervention on")
    parser.add_argument(
        "--zero", nargs="+", default=[],
        help="Features to zero out as 'layer,pos,feature_idx' (e.g., '20,-1,1454')"
    )
    parser.add_argument("--source_prompt", help="Prompt to get activation values from (for --activate)")
    parser.add_argument(
        "--activate", nargs="+", default=[],
        help="Features to activate (from source_prompt) as 'layer,pos,feature_idx'"
    )
    parser.add_argument("--scale", type=float, default=1.0, help="Scale factor for activated features")
    parser.add_argument("--generate", action="store_true", help="Run open-ended generation instead of single-step")
    parser.add_argument("--model_name", default="google/gemma-2-2b")
    parser.add_argument("--transcoder_name", default="gemma")
    parser.add_argument("--backend", default="transformerlens", choices=["transformerlens", "nnsight"])
    parser.add_argument("--top_k", type=int, default=5, help="Number of top outputs to show")
    parser.add_argument("--json_output", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    if args.activate and not args.source_prompt:
        parser.error("--source_prompt required when using --activate")

    # Load model
    print(f"Loading model: {args.model_name}")
    model = load_model(args.model_name, args.transcoder_name, args.backend)

    # Get source activations if needed
    source_activations = None
    if args.source_prompt:
        print(f"Getting activations for source: {args.source_prompt!r}")
        _, source_activations = model.get_activations(args.source_prompt, sparse=True)

    # Build intervention tuples
    intervention_tuples = []

    # Zero interventions
    for spec in args.zero:
        layer, pos, feat_idx = parse_feature_spec(spec)
        intervention_tuples.append((layer, pos, feat_idx, 0.0))
        print(f"  Zero: layer={layer}, pos={pos}, feature_idx={feat_idx}")

    # Activate interventions (using source activations scaled)
    for spec in args.activate:
        layer, pos, feat_idx = parse_feature_spec(spec)
        act_value = float(source_activations[layer, pos, feat_idx]) * args.scale
        intervention_tuples.append((layer, pos, feat_idx, act_value))
        print(f"  Activate: layer={layer}, pos={pos}, feature_idx={feat_idx}, value={act_value:.4f}")

    if args.generate:
        # Open-ended generation with intervention
        sequence_length = len(model.tokenizer(args.target_prompt).input_ids)
        original_pos = sequence_length - 1
        open_ended_slice = slice(original_pos, None, None)

        open_ended_tuples = []
        for layer, pos, feat_idx, value in intervention_tuples:
            open_ended_tuples.append((layer, open_ended_slice, feat_idx, value))

        print(f"\nGenerating with interventions on: {args.target_prompt!r}")
        pre_gen = model.feature_intervention_generate(
            args.target_prompt, [], do_sample=False, verbose=False
        )[0]
        post_gen = model.feature_intervention_generate(
            args.target_prompt, open_ended_tuples, do_sample=False, verbose=False
        )[0]

        if args.json_output:
            print(json.dumps({
                "target_prompt": args.target_prompt,
                "pre_intervention_generation": pre_gen,
                "post_intervention_generation": post_gen,
            }, indent=2))
        else:
            print(f"\nPre-intervention generation:  {pre_gen}")
            print(f"Post-intervention generation: {post_gen}")
    else:
        # Single-step intervention
        print(f"\nRunning intervention on: {args.target_prompt!r}")
        with torch.inference_mode():
            original_logits, _ = model.feature_intervention(args.target_prompt, [])
            new_logits, _ = model.feature_intervention(args.target_prompt, intervention_tuples)

        original_top = get_top_outputs(original_logits, model.tokenizer, k=args.top_k)
        new_top = get_top_outputs(new_logits, model.tokenizer, k=args.top_k)

        if args.json_output:
            print(json.dumps({
                "target_prompt": args.target_prompt,
                "original_top_outputs": original_top,
                "intervention_top_outputs": new_top,
            }, indent=2, default=str))
        else:
            print_top_outputs(original_top, label="Original top outputs")
            print_top_outputs(new_top, label="Post-intervention top outputs")
