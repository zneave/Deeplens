from dash import html, dcc
import dash_bootstrap_components as dbc

def get_activations_tab():
    return dbc.Container([
        dbc.Row([
            dbc.Col(
                html.H4("🔍 Activation Explorer", className="mb-4 fw-bold text-center"),
                width=12
            )
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Step 1: Upload or Use a Preset Image"),
                    dbc.CardBody([
                        dcc.Upload(
                            id="upload-image",
                            children=html.Div([
                                "Drag and Drop or ", html.A("Select an Image")
                            ]),
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
                            dbc.Button("Use Preset Image", id="use-preset-btn", color="info", size="sm", n_clicks=0),
                            className="text-center mt-3"
                        )
                    ])
                ], className="mb-4")
            ], md=6),

            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Step 2: Select Layer & View Mode"),
                    dbc.CardBody([
                        html.Label("Select Layer"),
                        dcc.Dropdown(
                            id="layer-dropdown",
                            options=[],
                            value=None,
                            clearable=False
                        ),
                        html.Br(),
                        html.Label("View Mode"),
                        dcc.RadioItems(
                            id="view-mode",
                            options=[
                                {'label': 'Single', 'value': 'single'},
                                {'label': 'Grid', 'value': 'grid'},
                                {'label': 'Comparative', 'value': 'comparative'}
                            ],
                            value='single',
                            labelStyle={'display': 'inline-block', 'marginRight': '10px'}
                        )
                    ])
                ], className="mb-4")
            ], md=6)
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Step 3: Select Channel"),
                    dbc.CardBody([
                        html.Label("Channel Index (-1 = Average):"),
                        dcc.Slider(
                            id="channel-slider",
                            min=-1,
                            max=0,
                            step=1,
                            value=-1,
                            marks={-1: "Avg"},
                            tooltip={"placement": "bottom"}
                        )
                    ])
                ])
            ], md=12)
        ], className="mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Input Image & Activation Output"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col(html.Img(id="input-image", style={
                                "width": "100%",
                                "maxHeight": "300px",
                                "objectFit": "contain",
                                "borderRadius": "5px"
                            })),
                            dbc.Col([
                                html.Div(
                                    dcc.Graph(
                                        id="activation-heatmap",
                                        config={"responsive": True},
                                        style={
                                            "width": "100%",
                                            "height": "100%",
                                            "minHeight": "300px",
                                            "maxHeight": "600px",
                                            "objectFit": "contain"
                                        },
                                        className="activation-graph"
                                    ),
                                    style={
                                        "overflowY": "auto",
                                        "maxHeight": "620px"
                                    },
                                    className="activation-graph-wrapper"
                                )
                            ])
                        ])
                    ])
                ])
            ])
        ], className="mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Collapse(
                    dbc.Card([
                        dbc.CardHeader("Activation Statistics"),
                        dbc.CardBody(html.Div(id="activation-stats"))
                    ]),
                    id="collapse-stats",
                    is_open=False
                ),
                dbc.Button("Toggle Stats", id="toggle-stats-btn", color="secondary", className="mt-3")
            ])
        ])
    ], fluid=True)
