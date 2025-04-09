import dash
from dash import Input, Output, State, ctx
from src.models.model import model
import torch.nn as nn
import re


def get_color_by_type(layer_type):
    colors = {
        "Conv2d": "#28a745",
        "Linear": "#17a2b8",
        "ReLU": "#ffc107",
        "MaxPool2d": "#fd7e14",
        "AdaptiveAvgPool2d": "#6f42c1",
        "BatchNorm2d": "#20c997",
        "Module": "#6c757d"
    }
    return colors.get(layer_type, "#6c757d")


def build_architecture_elements(filter_types):
    elements = []
    module_nodes = {}
    parent_stack = [("root", model)]

    while parent_stack:
        parent_id, module = parent_stack.pop()

        for name, child in module.named_children():
            child_id = f"{parent_id}/{name}"
            layer_type = child._get_name()

            if layer_type not in filter_types:
                continue

            label = f"{name}\n({layer_type})"
            elements.append({
                "data": {
                    "id": child_id,
                    "label": label,
                    "details": str(child),
                    "color": get_color_by_type(layer_type),
                    "type": layer_type,
                    "parent": parent_id if parent_id != "root" else None
                }
            })
            elements.append({
                "data": {
                    "source": parent_id,
                    "target": child_id
                }
            })

            if isinstance(child, nn.Module):
                parent_stack.append((child_id, child))

    elements.append({
        "data": {
            "id": "root",
            "label": model.__class__.__name__,
            "details": str(model),
            "color": "#007bff",
            "type": "Model"
        }
    })

    return elements


def register_callbacks(app):

    @app.callback(
        Output("architecture-tree", "elements"),
        Output("architecture-tree", "layout"),
        Output("model-summary", "children"),
        Input("layout-selector", "value"),
        Input("zoom-fit-btn", "n_clicks"),
        Input("layer-filter-checklist", "value"),
        prevent_initial_call=True
    )
    def update_tree(layout_value, zoom_clicks, filter_types):
        print("[ARCH CALLBACK] Updating tree layout and filters")

        elements = build_architecture_elements(filter_types)

        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        frozen_params = total_params - trainable_params

        summary_text = dash.html.Ul([
            dash.html.Li(f"Total Parameters: {total_params:,}"),
            dash.html.Li(f"Trainable Parameters: {trainable_params:,}"),
            dash.html.Li(f"Frozen Parameters: {frozen_params:,}")
        ])

        layout = {"name": layout_value or "dagre"}
        return elements, layout, summary_text

    @app.callback(
        Output("layer-info", "children"),
        Input("architecture-tree", "tapNodeData"),
        prevent_initial_call=True
    )
    def display_layer_info(node_data):
        if node_data is None:
            return dash.no_update

        return (
            f"<b>ID:</b> {node_data['id']}<br>"
            f"<b>Label:</b> {node_data['label']}<br>"
            f"<b>Type:</b> {node_data.get('type', 'N/A')}<br>"
            f"<b>Details:</b><br><code style='font-size: 0.85em;'>{node_data['details']}</code>"
        )
