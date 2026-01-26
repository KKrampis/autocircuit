def print_metadata(metadata: dict):
    print(f"Model: {metadata['scan']}")
    print(f"Prompt Tokens: {metadata['prompt_tokens']}")
    print(f"Prompt: {metadata['prompt']}")

    print(f"Max number of logits nodes to attribute from: {metadata['generation_settings']['max_n_logits']}")
    print(f"Cumulative probability threshold for top logits: {metadata['generation_settings']['desired_logit_prob']}")
    print(f"Batch size for backward passes: {metadata['generation_settings']['batch_size']}")
    print(f"Maximum number of feature nodes: {metadata['generation_settings']['max_feature_nodes']}")

    print(f"Keeps minimum nodes with cumulative influence >= threshold: {metadata['pruning_settings']['node_threshold']}")
    print(f"Keeps minimum edges with cumulative influence >= threshold: {metadata['pruning_settings']['edge_threshold']}")
    print(f"The set of transcoders to use for attribution: {metadata['info']['transcoder_set']}")