from collections import defaultdict

def calculate_in_degree(links: list[dict]) -> dict[str, int]:
    """Calculate in-degree for each node."""
    in_degree = defaultdict(int)
    for link in links:
        in_degree[link['target']] += 1
    return in_degree