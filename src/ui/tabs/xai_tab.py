import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

def get_xai_tab():
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    html.H4("🧠 XAI (Explainable AI) Visualizations", className="mb-4 fw-bold text-center")
                )
            ),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Step 0: Upload or Use a Preset Image"),
                        dbc.CardBody([
                            dcc.Upload(
                                id="xai-upload-image",
                                children=html.Div(["Drag and Drop or ", html.A("Select an Image")]),
                                style={
                                    'width': '100%',
                                    'height': '60px',
                                    'lineHeight': '60px',
                                    'borderWidth': '1px',
                                    'borderStyle': 'dashed',
                                    'borderRadius': '5px',
                                    'textAlign': 'center'
                                },
                                multiple=False
                            ),
                            html.Div(
                                dbc.Button("Use Preset Image", id="xai-use-preset-btn", color="info", size="sm", n_clicks=0),
                                className="text-center mt-3"
                            )
                        ])
                    ])
                ])
            ]),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Step 1: Select View Mode"),
                        dbc.CardBody([
                            html.Label("Choose XAI Visualization Type:"),
                            dcc.RadioItems(
                                id="xai-view-mode",
                                options=[
                                    {"label": "Grad-CAM", "value": "gradcam"},
                                    {"label": "Integrated Gradients", "value": "integrated_gradients"},
                                ],
                                value="gradcam",
                                labelStyle={"display": "inline-block", "marginRight": "10px"}
                            )
                        ])
                    ], className="mb-4")
                ], md=6),

                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Step 2: Adjust Channel & Layer"),
                        dbc.CardBody([
                            html.Label("Select Layer:"),
                            dcc.Dropdown(
                                id="xai-layer-dropdown",
                                options=[],
                                value=None,
                                clearable=False
                            ),
                            html.Label("Select Channel (-1 for average):"),
                            dcc.Slider(
                                id="xai-channel-slider",
                                min=-1,
                                max=0,
                                step=1,
                                value=-1,
                                marks={-1: "Avg"},
                                tooltip={"placement": "bottom"}
                            ),
                        ])
                    ], className="mb-4")
                ], md=6)
            ]),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("XAI Visualization Output"),
                        dbc.CardBody([
                            dcc.Graph(
                                id="xai-heatmap",
                                style={"height": "400px", "display": "none"}
                            ),
                            html.Img(
                                id="xai-preview-img",
                                style={
                                    "width": "100%",
                                    "maxWidth": "800px",
                                    "height": "auto",
                                    "margin": "0 auto",
                                    "display": "none",
                                    "borderRadius": "8px"
                                }
                            ),
                            html.Div([
                                html.Label("🔍 Image Scale:"),
                                dcc.Slider(
                                    id="xai-image-scale-slider",
                                    min=50,
                                    max=150,
                                    step=10,
                                    value=100,
                                    marks={i: f"{i}%" for i in range(50, 160, 25)},
                                    tooltip={"placement": "bottom"}
                                )
                            ], className="mt-4")
                        ])
                    ])
                ])
            ])
        ],
        fluid=True
    )
