"""SVG graph visualization for intervention graphs.

Renders InterventionGraph + top outputs as an SVG string.
Ported from demo/graph_visualization.py to remove the demo dependency.
"""

import math
import html

from IPython.display import SVG


def calculate_node_positions(nodes):
    """Calculate positions for all nodes including replacements."""
    container_width = 600
    container_height = 250
    node_width = 100

    node_data = {}

    for row_index in range(len(nodes)):
        row = nodes[row_index]
        row_y = container_height - (row_index * (container_height / (len(nodes) + 0.5)))

        for col_index in range(len(row)):
            node = row[col_index]
            row_width = len(row) * node_width + (len(row) - 1) * 50
            start_x = (container_width - row_width) / 2
            node_x = start_x + col_index * (node_width + 50)

            node_data[node.name] = {"x": node_x, "y": row_y, "node": node}

    all_nodes = set()
    for layer in nodes:
        for node in layer:
            all_nodes.add(node)
            if node.replacement_node:
                all_nodes.add(node.replacement_node)

    for node in all_nodes:
        if node.replacement_node and node.replacement_node.name not in node_data:
            original_pos = node_data.get(node.name)
            if original_pos:
                node_data[node.replacement_node.name] = {
                    "x": original_pos["x"] + 30,
                    "y": original_pos["y"] - 35,
                    "node": node.replacement_node,
                }

    return node_data


def get_node_center(node_data, node_name):
    """Get center coordinates of a node."""
    node = node_data.get(node_name)
    if not node:
        return {"x": 0, "y": 0}
    return {
        "x": node["x"] + 50,
        "y": node["y"] + 17.5,
    }


def create_connection_svg(node_data, connections):
    """Generate SVG elements for all connections."""
    svg_parts = []

    for conn in connections:
        from_center = get_node_center(node_data, conn["from"])
        to_center = get_node_center(node_data, conn["to"])

        if from_center["x"] == 0 or to_center["x"] == 0:
            continue

        if conn.get("replacement"):
            stroke_color = "#D2691E"
            stroke_width = "4"
        else:
            stroke_color = "#8B4513"
            stroke_width = "3"

        svg_parts.append(
            f'<line x1="{from_center["x"]}" y1="{from_center["y"]}" '
            f'x2="{to_center["x"]}" y2="{to_center["y"]}" '
            f'stroke="{stroke_color}" stroke-width="{stroke_width}"/>'
        )

        dx = to_center["x"] - from_center["x"]
        dy = to_center["y"] - from_center["y"]
        length = math.sqrt(dx * dx + dy * dy)

        if length > 0:
            dx_norm = dx / length
            dy_norm = dy / length

            arrow_size = 8
            arrow_tip_x = to_center["x"]
            arrow_tip_y = to_center["y"]

            base_x = arrow_tip_x - arrow_size * dx_norm
            base_y = arrow_tip_y - arrow_size * dy_norm

            perp_x = -dy_norm * (arrow_size / 2)
            perp_y = dx_norm * (arrow_size / 2)

            left_x = base_x + perp_x
            left_y = base_y + perp_y
            right_x = base_x - perp_x
            right_y = base_y - perp_y

            svg_parts.append(
                f'<polygon points="{arrow_tip_x},{arrow_tip_y} {left_x},{left_y} {right_x},{right_y}" '
                f'fill="{stroke_color}"/>'
            )

    return "\n".join(svg_parts)


def create_nodes_svg(node_data):
    """Generate SVG elements for all nodes."""
    svg_parts = []

    replacement_nodes = set()
    for data in node_data.values():
        node = data["node"]
        if node.replacement_node:
            replacement_nodes.add(node.replacement_node.name)

    for name, data in node_data.items():
        node = data["node"]
        x = data["x"]
        y = data["y"]

        is_low_activation = node.activation is not None and node.activation <= 0.25
        has_negative_intervention = node.intervention and "-" in node.intervention
        is_replacement = name in replacement_nodes

        if is_low_activation or has_negative_intervention:
            fill_color = "#f0f0f0"
            text_color = "#bbb"
            stroke_color = "#ddd"
        elif is_replacement:
            fill_color = "#FFF8DC"
            text_color = "#333"
            stroke_color = "#D2691E"
        else:
            fill_color = "#e8e8e8"
            text_color = "#333"
            stroke_color = "#999"

        svg_parts.append(
            f'<rect x="{x}" y="{y}" width="100" height="35" '
            f'fill="{fill_color}" stroke="{stroke_color}" stroke-width="2" rx="8"/>'
        )

        text_x = x + 50
        text_y = y + 22
        escaped_name = html.escape(name)
        svg_parts.append(
            f'<text x="{text_x}" y="{text_y}" text-anchor="middle" '
            f'fill="{text_color}" font-family="Arial, sans-serif" font-size="12" font-weight="bold">{escaped_name}</text>'
        )

        if node.activation is not None:
            activation_pct = round(node.activation * 100)
            label_x = x - 15
            label_y = y - 5

            svg_parts.append(
                f'<rect x="{label_x}" y="{label_y}" width="30" height="16" '
                f'fill="white" stroke="#ccc" stroke-width="1" rx="4"/>'
            )

            svg_parts.append(
                f'<text x="{label_x + 15}" y="{label_y + 12}" text-anchor="middle" '
                f'fill="#8B4513" font-family="Arial, sans-serif" font-size="10" font-weight="bold">{activation_pct}%</text>'
            )

        if node.intervention:
            intervention_x = x - 20
            intervention_y = y - 5

            text_width = len(node.intervention) * 8 + 10
            escaped_intervention = html.escape(node.intervention)

            svg_parts.append(
                f'<rect x="{intervention_x}" y="{intervention_y}" width="{text_width}" height="16" '
                f'fill="#D2691E" stroke="none" rx="12"/>'
            )

            svg_parts.append(
                f'<text x="{intervention_x + text_width / 2}" y="{intervention_y + 12}" text-anchor="middle" '
                f'fill="white" font-family="Arial, sans-serif" font-size="10" font-weight="bold">{escaped_intervention}</text>'
            )

    return "\n".join(svg_parts)


def build_connections_data(nodes):
    """Build connection data from node relationships."""
    connections = []

    all_nodes = set()

    def add_node_and_related(node):
        all_nodes.add(node)
        if node.replacement_node:
            add_node_and_related(node.replacement_node)
        for child in node.children:
            add_node_and_related(child)

    for layer in nodes:
        for node in layer:
            add_node_and_related(node)

    replacement_nodes = set()
    for node in all_nodes:
        if node.replacement_node:
            replacement_nodes.add(node.replacement_node.name)

    for node in all_nodes:
        for child in node.children:
            if node.replacement_node:
                continue

            is_replacement = node.name in replacement_nodes

            connection = {"from": node.name, "to": child.name}
            if is_replacement:
                connection["replacement"] = True

            connections.append(connection)

    return connections


def wrap_text_for_svg(text, max_width=80):
    """Simple text wrapping for SVG."""
    if len(text) <= max_width:
        return [text]

    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        if len(current_line + " " + word) <= max_width:
            current_line = current_line + " " + word if current_line else word
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def create_graph_visualization(intervention_graph, top_outputs):
    """Create an SVG graph visualization.

    Args:
        intervention_graph: InterventionGraph with ordered_nodes and prompt.
        top_outputs: list of (token, probability) tuples.

    Returns:
        IPython.display.SVG object.
    """
    nodes = intervention_graph.ordered_nodes
    prompt = intervention_graph.prompt

    node_data = calculate_node_positions(nodes)
    connections = build_connections_data(nodes)

    connections_svg = create_connection_svg(node_data, connections)
    nodes_svg = create_nodes_svg(node_data)

    output_y_start = 350
    output_items_svg = []
    current_x = 40

    for i, (text, percentage) in enumerate(top_outputs):
        if i >= 6:
            break

        display_text = text if text else "(empty)"
        escaped_display_text = html.escape(display_text)
        percentage_text = f"{round(percentage * 100)}%"

        item_width = len(display_text) * 8 + len(percentage_text) * 6 + 20
        output_items_svg.append(
            f'<rect x="{current_x}" y="{output_y_start}" width="{item_width}" height="20" '
            f'fill="#e8e8e8" stroke="none" rx="6"/>'
        )

        output_items_svg.append(
            f'<text x="{current_x + 5}" y="{output_y_start + 14}" '
            f'fill="#333" font-family="Arial, sans-serif" font-size="11" font-weight="bold">'
            f'{escaped_display_text} <tspan fill="#555" font-size="10">{percentage_text}</tspan></text>'
        )

        current_x += item_width + 10

    output_items_svg_str = "\n".join(output_items_svg)

    escaped_prompt = html.escape(prompt)
    prompt_lines = wrap_text_for_svg(escaped_prompt, max_width=80)

    prompt_text_svg = []
    for i, line in enumerate(prompt_lines):
        y_offset = 325 + (i * 15)
        prompt_text_svg.append(
            f'<text x="40" y="{y_offset}" fill="#333" font-family="Arial, sans-serif" font-size="12">{line}</text>'
        )

    prompt_text_svg_str = "\n".join(prompt_text_svg)

    svg_content = f"""<svg width="700" height="400" xmlns="http://www.w3.org/2000/svg">
    <!-- Background -->
    <rect width="700" height="400" fill="#f5f5f5"/>
    <rect x="20" y="20" width="660" height="360" fill="white" stroke="none" rx="12"/>

    <!-- Title -->
    <text x="40" y="45" fill="#666" font-family="Arial, sans-serif" font-size="14" font-weight="bold"
          text-transform="uppercase" letter-spacing="1px">Graph &amp; Interventions</text>

    <!-- Graph area (moved up significantly) -->
    <g transform="translate(50, 0)">
        {connections_svg}
        {nodes_svg}
    </g>

    <!-- Prompt section -->
    <line x1="40" y1="290" x2="660" y2="290" stroke="#ddd" stroke-width="1"/>
    <text x="40" y="310" fill="#666" font-family="Arial, sans-serif" font-size="12" font-weight="bold"
          text-transform="uppercase" letter-spacing="0.5px">Prompt</text>

    <!-- Prompt text (GitHub-compatible) -->
    {prompt_text_svg_str}

    <!-- Top outputs section -->
    <text x="40" y="350" fill="#666" font-family="Arial, sans-serif" font-size="10" font-weight="bold"
          text-transform="uppercase" letter-spacing="0.5px">Top Outputs</text>

    <!-- Output items -->
    <g transform="translate(0, 5)">
        {output_items_svg_str}
    </g>
</svg>"""

    return SVG(svg_content)