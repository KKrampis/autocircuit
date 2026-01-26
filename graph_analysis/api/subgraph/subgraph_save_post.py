import requests

def do_subgraph_save_post(body: dict, api_key: str) -> dict:
    """
    Send supernode configuration to Neuronpedia API.

    Returns:
        API response as dictionary
    """
    url = "https://www.neuronpedia.org/api/graph/subgraph/save"
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()

    return response.json()


def create_subgraph_save_body(model_id: str, slug: str, displayName: str, node_threshold: float, edge_threshold: float, 
                              pinnedIds: list[str], supernodes: list[list[str]]) -> dict:
    """
    Create complete body for /api/graph/subgraph/save endpoint.

    Returns:
        Dictionary ready to send as JSON to API
    """
    body = {
        "modelId": model_id,
        "slug": slug,
        "pinnedIds": pinnedIds,
        "supernodes": supernodes,
        "clerps": [],
        "pruningThreshold": node_threshold,
        "densityThreshold": edge_threshold,
    }

    if displayName is not None:
        body['displayName'] = displayName

    return body
