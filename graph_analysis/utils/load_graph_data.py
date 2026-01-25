import json

def load_graph_data(filepath: str) -> dict:
    """Load graph data from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)