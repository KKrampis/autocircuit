from collections import defaultdict

def print_context_flow(nodes: dict, edges: dict, prompt_tokens: list[str]):
    print("\n\nCONTEXT POSITION FLOW (Token-level processing)")

    ctx_flow = defaultdict(lambda: {'count': 0, 'total_weight': 0})
    nodes_dict = {n['node_id']: n for n in nodes}

    for edge in edges:
        source_node = nodes_dict[edge['source']]
        target_node = nodes_dict[edge['target']]
        
        src_ctx = source_node['ctx_idx']
        tgt_ctx = target_node['ctx_idx']
        key = (src_ctx, tgt_ctx)
        ctx_flow[key]['count'] += 1
        ctx_flow[key]['total_weight'] += abs(edge['weight'])

    print("\nToken-to-Token Flow (by edge count):\n")
    max_token_len = max(len(t) for t in prompt_tokens)
    sorted_flow = sorted(ctx_flow.items(), key=lambda x: x[1]['count'], reverse=True)[:20]
    for i, ((src, tgt), stats) in enumerate(sorted_flow, 1):
        src_token = f"'{prompt_tokens[src]}'"
        tgt_token = f"'{prompt_tokens[tgt]}'"
        print(f"{i:02d}. C{src} ({src_token:>{max_token_len + 2}}) → C{tgt} ({tgt_token:>{max_token_len + 2}}): "
              f"{stats['count']:5d} edges, TotalWeight={stats['total_weight']:8.1f}")