import torch
from circuit_tracer import ReplacementModel


def load_model(
    model_name: str = "google/gemma-2-2b",
    transcoder_name: str = "gemma",
    backend: str = "transformerlens",
    dtype: torch.dtype = torch.bfloat16,
) -> ReplacementModel:
    """Load a ReplacementModel with transcoders."""
    return ReplacementModel.from_pretrained(
        model_name, transcoder_name, dtype=dtype, backend=backend
    )


def get_top_outputs(
    logits: torch.Tensor, tokenizer, k: int = 5
) -> list[tuple[str, float]]:
    """Get top-k token predictions from logits.

    Returns list of (token_str, probability) tuples.
    """
    top_probs, top_token_ids = logits.squeeze(0)[-1].softmax(-1).topk(k)
    top_tokens = [tokenizer.decode(token_id) for token_id in top_token_ids]
    return list(zip(top_tokens, top_probs.tolist()))


def print_top_outputs(top_outputs: list[tuple[str, float]], label: str = "Top outputs"):
    """Print top outputs in a readable format."""
    print(f"\n{label}:")
    for token, prob in top_outputs:
        print(f"  {token!r}: {prob:.4f}")
