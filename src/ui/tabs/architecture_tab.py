from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import dash
from dash.dependencies import Input, Output, State
from src.models.model import model
import torch.nn as nn

cyto.load_extra_layouts()

layout_options = [
    {"label": "Dagre (default)", "value": "dagre"},
    {"label": "Breadthfirst", "value": "breadthfirst"},
    {"label": "Grid", "value": "grid"},
    {"label": "Circle", "value": "circle"},
]

layer_type_filters = [
    {"label": "Conv2d", "value": "Conv2d"},
    {"label": "Linear", "value": "Linear"},
    {"label": "ReLU", "value": "ReLU"},
    {"label": "MaxPool2d", "value": "MaxPool2d"},
    {"label": "AdaptiveAvgPool2d", "value": "AdaptiveAvgPool2d"},
    {"label": "BatchNorm2d", "value": "BatchNorm2d"}
]

def get_architecture_tab():
    return dbc.Container([
        dbc.Row(
            dbc.Col(html.H4("Neural Network Architecture", className="text-center fw-bold mb-4"))
        ),

        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Label("Select Layout:", className="fw-bold me-2"),
                    dcc.Dropdown(
                        id="layout-selector",
                        options=layout_options,
                        value="dagre",
                        clearable=False,
                        style={"width": "200px"}
                    ),
                    dbc.Button("Zoom to Fit", id="zoom-fit-btn", className="ms-3 btn-sm", color="secondary")
                ], className="d-flex align-items-center mb-2"),

                html.Div([
                    html.Label("Toggle Layer Types:", className="fw-bold me-2"),
                    dcc.Checklist(
                        id="layer-filter-checklist",
                        options=layer_type_filters,
                        value=[f["value"] for f in layer_type_filters],
                        inline=True,
                        labelStyle={"marginRight": "10px"},
                        inputStyle={"marginRight": "5px"}
                    )
                ], className="mb-3")
            ])
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Model Architecture Tree"),
                    dbc.CardBody([
                        cyto.Cytoscape(
                            id="architecture-tree",
                            layout={"name": "dagre"},
                            style={"width": "100%", "height": "600px"},
                            elements=[],
                            zoom=1,
                            minZoom=0.25,
                            maxZoom=2,
                            userZoomingEnabled=True,
                            userPanningEnabled=True,
                            boxSelectionEnabled=False,
                            stylesheet=[
                                {
                                    "selector": "node",
                                    "style": {
                                        "label": "data(label)",
                                        "text-wrap": "wrap",
                                        "text-max-width": 150,
                                        "shape": "round-rectangle",
                                        "background-color": "data(color)",
                                        "color": "white",
                                        "font-size": "10px",
                                        "text-valign": "center",
                                        "text-halign": "center",
                                        "padding": "10px",
                                        "width": "label",
                                        "height": "label"
                                    }
                                },
                                {
                                    "selector": "edge",
                                    "style": {
                                        "curve-style": "bezier",
                                        "target-arrow-shape": "triangle",
                                        "line-color": "#ccc",
                                        "target-arrow-color": "#ccc",
                                        "width": 1.5
                                    }
                                }
                            ]
                        )
                    ])
                ])
            ], md=8),

            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Layer Details"),
                    dbc.CardBody(html.Div(id="layer-info", children="Click a layer to view details."))
                ], className="mb-4"),

                dbc.Card([
                    dbc.CardHeader("Model Summary"),
                    dbc.CardBody(html.Div(id="model-summary"))
                ])
            ], md=4)
        ])
    ], fluid=True)


def get_color_by_type(layer_type):
    colors = {
        "Conv2d": "#28a745",
        "Linear": "#17a2b8",
        "ReLU": "#ffc107",
        "MaxPool2d": "#fd7e14",
        "AdaptiveAvgPool2d": "#6f42c1",
        "BatchNorm2d": "#20c997",
    }
    return colors.get(layer_type, "#6c757d")


def build_architecture_elements(filter_types):
    elements = []
    parent_stack = [("root", model)]

    while parent_stack:
        parent_id, module = parent_stack.pop()

        for name, child in module.named_children():
            child_id = f"{parent_id}/{name}"
            layer_type = child._get_name()
            label = f"{name}\n({layer_type})"

            if layer_type not in filter_types:
                continue

            elements.append({
                "data": {
                    "id": child_id,
                    "label": label,
                    "details": str(child),
                    "color": get_color_by_type(layer_type),
                    "type": layer_type
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
