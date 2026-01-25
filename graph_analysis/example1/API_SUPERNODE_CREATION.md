# Creating Supernodes via Neuronpedia API

## Overview

Yes! The Neuronpedia API **does support creating supernodes programmatically** through the `/api/graph/subgraph/save` endpoint. Based on the [API documentation](https://www.neuronpedia.org/api-doc), supernodes can be created and saved as part of a "subgraph" configuration.

## API Architecture

The Neuronpedia graph system has two levels:

1. **Base Graph** - The original full circuit graph (1,193 nodes, 35,075 edges)
   - Accessed via: `/api/graph/{modelId}/{slug}`
   - Cannot be modified after creation

2. **Subgraph** - A user-defined view of the base graph with:
   - **Supernodes** - Grouped nodes with custom labels
   - **Pinned nodes** - Highlighted important nodes
   - **Pruning settings** - Custom visibility thresholds
   - Saved via: `/api/graph/subgraph/save`

## Current Graph State

Our graph currently has:
```json
{
  "qParams": {
    "pinnedIds": [],
    "supernodes": [],    // <-- Empty, ready to populate!
    "linkType": "both",
    "clickedId": "",
    "sg_pos": ""
  }
}
```

---

## API Call Sequence

### Step 1: Get Graph Metadata

**Endpoint:** `GET /api/graph/{modelId}/{slug}`

**Request:**
```bash
curl -X GET \
  "https://www.neuronpedia.org/api/graph/gemma-2-2b/dnastandsfordeox-1767880345293" \
  -H "x-api-key: sk-np-xM8SydJfvJjlyFg7hZPEPpqWB3Bcqpx8O0mIM4P5BmQ0"
```

**Response:**
```json
{
  "id": "cmk5ibfay0013ylwa040doizc",
  "modelId": "gemma-2-2b",
  "slug": "dnastandsfordeox-1767880345293",
  "prompt": "<bos>DNA stands for deoxyribonucleic",
  "promptTokens": ["<bos>", "DNA", " stands", " for", " deoxy", "ri", "bonucleic"],
  "url": "https://neuronpedia-attrib.s3.us-east-1.amazonaws.com/...",
  "userId": "cm7zchuzj0000k39abdgecnhp",
  "createdAt": "2026-01-08T13:52:33.850Z"
}
```

**Purpose:** Verify graph exists and get model/slug for subsequent API calls

---

### Step 2: Download Full Graph Data

**Endpoint:** S3 direct download (URL from Step 1)

**Request:**
```bash
curl -s -X GET \
  "https://neuronpedia-attrib.s3.us-east-1.amazonaws.com/user-graphs/cm7zchuzj0000k39abdgecnhp/dnastandsfordeox-1767880345293.json" \
  -o graph_data.json
```

**Response:** 3 MB JSON file containing:
```json
{
  "metadata": { /* graph settings */ },
  "qParams": { /* current view state */ },
  "nodes": [ /* 1,193 feature nodes */ ],
  "links": [ /* 35,075 edges */ ]
}
```

**Purpose:** Get complete node list to identify which nodes belong in each supernode

---

### Step 3: Group Nodes into Supernodes

**Process:** Analyze nodes and create supernode definitions

Based on the circuit analysis, we group nodes by **(Layer, Context Position)**:

**Supernode Format (inferred from web UI behavior):**
```json
{
  "id": "supernode-L0-C1",
  "label": "L0_C1: DNA Token Processing",
  "description": "93 features processing DNA token in layer 0",
  "nodeIds": [
    "0_177_1",
    "0_253_1",
    "0_355_1",
    // ... all 93 nodes from L0 at context position 1
  ],
  "color": "#FF6B6B",  // Optional custom color
  "position": {        // Optional custom layout position
    "x": 100,
    "y": 200
  }
}
```

**Example Supernodes to Create:**

1. **Early Processing Supernodes (L0-L5)**
   - `L0_C1` - 93 features at DNA token
   - `L0_C2` - 72 features at "stands" token
   - `L0_C6` - 80 features at target position
   - ... (continue for all layer-context pairs)

2. **Middle Routing Supernodes (L6-L15)**
   - `L8_C6` - Features routing to target
   - `L10_C6` - Middle-layer integration

3. **Decision Module Supernodes (L22-L25)**
   - `L22_C6` - 15 features, initial output preparation
   - `L23_C6` - 26 features, major decision hub
   - `L24_C6` - 22 features, penultimate refinement
   - `L25_C6` - 30 features, final transformation

---

### Step 4: Create Supernode Subgraph

**Endpoint:** `POST /api/graph/subgraph/save`

**Request:**
```bash
curl -X POST \
  "https://www.neuronpedia.org/api/graph/subgraph/save" \
  -H "x-api-key: sk-np-xM8SydJfvJjlyFg7hZPEPpqWB3Bcqpx8O0mIM4P5BmQ0" \
  -H "Content-Type: application/json" \
  -d '{
    "modelId": "gemma-2-2b",
    "slug": "dnastandsfordeox-1767880345293",
    "supernodes": [
      {
        "id": "L0_C1_DNA",
        "label": "L0_C1: DNA Token (93 features)",
        "description": "Initial processing of DNA token - domain detection",
        "nodeIds": [
          "0_177_1", "0_253_1", "0_355_1", "0_548_1", "0_710_1",
          "0_993_1", "0_1001_1", "0_1052_1", "0_1148_1", "0_1219_1"
          // ... (all 93 node IDs from L0, ctx_idx=1)
        ]
      },
      {
        "id": "L0_C2_STANDS",
        "label": "L0_C2: Stands Token (72 features)",
        "description": "Processing verb in definitional structure",
        "nodeIds": [
          "0_253_2", "0_482_2", "0_671_2", "0_984_2"
          // ... (all 72 node IDs from L0, ctx_idx=2)
        ]
      },
      {
        "id": "L23_C6_DECISION",
        "label": "L23_C6: Decision Hub (26 features)",
        "description": "Major integration hub with 610+ incoming edges",
        "nodeIds": [
          "23_6638_6", "23_5764_6", "23_5917_6", "23_10894_6",
          "23_13877_6", "23_15454_6"
          // ... (all 26 node IDs from L23, ctx_idx=6)
        ]
      },
      {
        "id": "L25_C6_OUTPUT",
        "label": "L25_C6: Final Output (30 features)",
        "description": "Final transformation before logit prediction",
        "nodeIds": [
          "25_10681_6", "25_4717_6", "25_12923_6", "25_14744_6",
          "25_3204_6", "25_15920_6", "25_13822_6"
          // ... (all 30 node IDs from L25, ctx_idx=6)
        ]
      }
      // ... continue for all 88 supernodes
    ],
    "pinnedIds": [
      "23_6638_6",    // Highest in-degree hub
      "0_15651_1",    // Highest influence in L0_C1
      "27_6898_6"     // Output logit
    ],
    "pruningThreshold": 0.8,
    "densityThreshold": 0.85
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "subgraphId": "subgraph-abc123xyz",
  "message": "Subgraph saved successfully",
  "url": "https://neuronpedia.org/gemma-2-2b/dnastandsfordeox-1767880345293?subgraph=subgraph-abc123xyz"
}
```

**Purpose:** Save supernode configuration to Neuronpedia, making it viewable in web UI

---

### Step 5: List User's Subgraphs

**Endpoint:** `POST /api/graph/subgraph/list`

**Request:**
```bash
curl -X POST \
  "https://www.neuronpedia.org/api/graph/subgraph/list" \
  -H "x-api-key: sk-np-xM8SydJfvJjlyFg7hZPEPpqWB3Bcqpx8O0mIM4P5BmQ0" \
  -H "Content-Type: application/json" \
  -d '{
    "modelId": "gemma-2-2b",
    "slug": "dnastandsfordeox-1767880345293"
  }'
```

**Expected Response:**
```json
{
  "subgraphs": [
    {
      "id": "subgraph-abc123xyz",
      "name": "Hierarchical Supernodes (Layer-Context Grouping)",
      "createdAt": "2026-01-14T09:30:00.000Z",
      "supernodeCount": 88,
      "pinnedNodeCount": 3
    }
  ]
}
```

**Purpose:** Verify subgraph was created and get ID for future updates

---

### Step 6: View in Web UI

**URL Format:**
```
https://neuronpedia.org/gemma-2-2b/dnastandsfordeox-1767880345293?subgraph=subgraph-abc123xyz
```

**Result:**
- Graph visualization shows 88 supernodes instead of 1,193 individual nodes
- Each supernode labeled with layer and context position
- Edges between supernodes show aggregate flow
- Click supernode to expand and see constituent features

---

## Complete Supernode Definitions

Based on circuit_description.md analysis, here are all 88 supernodes:

### Early Layers (L0-L5) - 35 supernodes

| Supernode ID | Label | Node Count | Avg Influence | Description |
|-------------|--------|-----------|--------------|-------------|
| L0_C1 | L0_C1: DNA Token | 93 | 0.628 | DNA token processing, domain detection |
| L0_C2 | L0_C2: Stands Token | 72 | 0.661 | Verb processing in definitional structure |
| L0_C3 | L0_C3: For Token | 16 | 0.720 | Preposition in definitional frame |
| L0_C4 | L0_C4: Deoxy Token | 59 | 0.722 | Chemical prefix detection |
| L0_C5 | L0_C5: Ri Token | 15 | 0.724 | Partial morpheme processing |
| L0_C6 | L0_C6: Target Token | 80 | 0.672 | Early target position processing |
| L1_C1 | L1_C1: DNA Layer 1 | 50 | 0.655 | DNA token refinement |
| ... | ... | ... | ... | ... |

### Middle Layers (L6-L15) - 38 supernodes

| Supernode ID | Label | Node Count | Avg Influence | Description |
|-------------|--------|-----------|--------------|-------------|
| L6_C6 | L6_C6: Target Routing | 27 | 0.692 | Information routing to target |
| L8_C6 | L8_C6: Integration Start | 22 | 0.670 | Begin evidence integration |
| L10_C6 | L10_C6: Mid Integration | 23 | 0.710 | Middle-layer integration |
| ... | ... | ... | ... | ... |

### Late Layers (L16-L25) - 15 supernodes

| Supernode ID | Label | Node Count | Avg Influence | Description |
|-------------|--------|-----------|--------------|-------------|
| L22_C6 | L22_C6: Output Prep | 15 | 0.501 | Initial output preparation |
| L23_C6 | L23_C6: Decision Hub | 26 | 0.544 | Major decision integration hub |
| L24_C6 | L24_C6: Refinement | 22 | 0.562 | Penultimate refinement |
| L25_C6 | L25_C6: Final Output | 30 | 0.537 | Final transformation |

---

## Automated Script

Here's a Python script to generate the supernode configuration:

```python
#!/usr/bin/env python3
"""
Generate supernode configuration for Neuronpedia API
"""
import json
import requests
from collections import defaultdict

# Load graph data
with open('graph_data.json', 'r') as f:
    graph_data = json.load(f)

# Group nodes by (layer, context_position)
supernodes_data = defaultdict(list)
for node in graph_data['nodes']:
    if node['feature_type'] == 'cross layer transcoder':
        key = (node['layer'], node['ctx_idx'])
        supernodes_data[key].append(node['node_id'])

# Create supernode definitions
supernodes = []
token_names = {
    0: "BOS", 1: "DNA", 2: "Stands", 3: "For",
    4: "Deoxy", 5: "Ri", 6: "Target"
}

for (layer, ctx_idx), node_ids in sorted(supernodes_data.items()):
    token = token_names.get(ctx_idx, f"C{ctx_idx}")
    supernode = {
        "id": f"L{layer}_C{ctx_idx}",
        "label": f"L{layer}_C{ctx_idx}: {token} ({len(node_ids)} features)",
        "description": f"Layer {layer}, context position {ctx_idx} ({token} token)",
        "nodeIds": node_ids
    }
    supernodes.append(supernode)

# Prepare API request
payload = {
    "modelId": "gemma-2-2b",
    "slug": "dnastandsfordeox-1767880345293",
    "supernodes": supernodes,
    "pinnedIds": [
        "23_6638_6",   # Top hub
        "0_15651_1",   # High influence
        "27_6898_6"    # Output
    ],
    "pruningThreshold": 0.8,
    "densityThreshold": 0.85
}

# Save to file for inspection
with open('supernode_config.json', 'w') as f:
    json.dump(payload, f, indent=2)

print(f"Created {len(supernodes)} supernodes")
print(f"Total nodes covered: {sum(len(s['nodeIds']) for s in supernodes)}")
print("Configuration saved to: supernode_config.json")

# Optional: Send to API (uncomment to execute)
# response = requests.post(
#     "https://www.neuronpedia.org/api/graph/subgraph/save",
#     headers={
#         "x-api-key": "sk-np-xM8SydJfvJjlyFg7hZPEPpqWB3Bcqpx8O0mIM4P5BmQ0",
#         "Content-Type": "application/json"
#     },
#     json=payload
# )
# print(f"API Response: {response.json()}")
```

---

## Expected Results

### After Creating Supernodes:

1. **Web UI View:**
   - Graph shows 88 supernodes instead of 1,193 nodes
   - Each supernode has custom label showing layer and token
   - Edges aggregate to show layer-to-layer flows
   - Hovering shows node count and description

2. **Simplified Analysis:**
   - Can see high-level circuit structure at a glance
   - Easy to identify: Early processing → Routing → Decision → Output
   - Click to expand any supernode to see individual features

3. **Information Flow Clarity:**
   - Strong flow L23_C6 → L25_C6 visible as thick edge
   - Skip connections L0 → L22-L25 clearly visible
   - Funnel pattern evident (many early supernodes → few late supernodes)

---

## API Limitations & Notes

**Current Limitations:**
- ⚠️ **Authentication Required:** Must use valid API key
- ⚠️ **Supernode format not fully documented:** Format inferred from web UI behavior
- ⚠️ **No batch operations:** Must create all supernodes in single API call
- ⚠️ **No supernode-to-supernode edges:** Must be computed client-side from constituent nodes

**Best Practices:**
- ✅ Group by semantic criteria (layer-context, functional role, etc.)
- ✅ Limit to 50-100 supernodes for visualization clarity
- ✅ Use descriptive labels with feature counts
- ✅ Pin important hub nodes for reference
- ✅ Save multiple subgraph views for different analysis levels

---

## Alternative: Manual Web UI Creation

If API access is limited, supernodes can be created manually:

1. Open graph: https://neuronpedia.org/gemma-2-2b/dnastandsfordeox-1767880345293
2. Hold `G` key
3. Click nodes to group them into supernode
4. Release `G` and click supernode label to annotate
5. Repeat for all 88 supernodes

*Note: Manual creation is tedious for 88 supernodes - API automation recommended*

---

## Sources

- [Neuronpedia API Documentation](https://www.neuronpedia.org/api-doc)
- [Neuronpedia Docs: API and Exports](https://docs.neuronpedia.org/api)
- [Circuit-Tracer GitHub](https://github.com/safety-research/circuit-tracer)
- [Neuronpedia GitHub](https://github.com/hijohnnylin/neuronpedia/)
