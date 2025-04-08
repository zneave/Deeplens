import dash_bootstrap_components as dbc
from dash import dcc, html
from ui.dashboard_info import get_dashboard_info
from helpers.config_parser import load_ui_config

# Load UI configuration from YAML.
ui_config = load_ui_config("config/ui_config.yaml")
theme_config = ui_config.get("theme", {})

# Define branding colors using config values (or fallbacks).
BRAND_COLORS = {
    "primary": theme_config.get("primary", "#1dd74e"),
    "light_bg": theme_config.get("light_bg", "#ffffff"),
    "dark_bg": theme_config.get("dark_bg", "#343a40"),
    "text_light": theme_config.get("text_light", "#ecf0f1"),
    "text_dark": theme_config.get("text_dark", "#212529"),
}

# Define a button color variable.
BUTTON_COLOR = theme_config.get("button", BRAND_COLORS["primary"])

# Define inline style dictionaries for light and dark modes.
LIGHT_MODE_STYLE = {
    'backgroundColor': BRAND_COLORS["light_bg"],
    'color': BRAND_COLORS["text_dark"],
    'transition': 'background-color 0.5s ease'
}

DARK_MODE_STYLE = {
    'backgroundColor': BRAND_COLORS["dark_bg"],
    'color': BRAND_COLORS["text_light"],
    'transition': 'background-color 0.5s ease'
}

def get_theme_style(is_dark=False):
    return DARK_MODE_STYLE if is_dark else LIGHT_MODE_STYLE

def get_navbar():
    return dbc.NavbarSimple(
        brand="DeepLens Dashboard",
        brand_href="/",
        color=BRAND_COLORS["primary"],
        dark=True,
        children=[
            dbc.NavItem(dbc.NavLink("Visualization", href="/dashboard")),
            dbc.NavItem(dbc.NavLink("Documentation", href="/documentation")),
            dbc.Button("Learn More", id="open-info", color="light", size="sm", n_clicks=0,
                       style={"backgroundColor": BUTTON_COLOR, "borderColor": BUTTON_COLOR}),
            dbc.NavItem(
                dbc.Button("Toggle Dark Mode", id="toggle-dark", color="secondary", size="sm", n_clicks=0,
                           style={'marginLeft': '20px'})
            )
        ],
    )

def get_sidebar(available_layers):
    """Returns a sidebar with controls in a responsive column."""
    return dbc.Col(
        [
            dbc.Card(
                [
                    dbc.CardHeader("Controls"),
                    dbc.CardBody(
                        [
                            # File Upload control.
                            html.Div(
                                dcc.Upload(
                                    id='upload-image',
                                    children=html.Div(['Drag & Drop or ', html.A('Select an Image')]),
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
                                className="mb-3"
                            ),
                            # Preset Image Button.
                            html.Div(
                                dbc.Button("Use Preset Image", id="use-preset-btn", color="info", size="sm", n_clicks=0,
                                           style={"backgroundColor": BUTTON_COLOR, "borderColor": BUTTON_COLOR}),
                                className="mb-3 text-center"
                            ),
                            # Layer Dropdown.
                            html.Div(
                                [
                                    html.Label("Select Layer:", style={'marginBottom': '5px'}),
                                    dcc.Dropdown(
                                        id='layer-dropdown',
                                        options=[{'label': layer, 'value': layer} for layer in available_layers],
                                        value=available_layers[0] if available_layers else None,
                                        clearable=False
                                    )
                                ],
                                className="mb-3"
                            ),
                            # View Mode Toggle with advanced options.
                            html.Div(
                                [
                                    html.Label("View Mode:", style={'marginBottom': '5px'}),
                                    dcc.RadioItems(
                                        id='view-mode',
                                        options=[
                                            {'label': 'Single', 'value': 'single'},
                                            {'label': 'Grid', 'value': 'grid'},
                                            {'label': 'Grad-CAM', 'value': 'gradcam'},
                                            {'label': 'Integrated Gradients', 'value': 'integrated_gradients'},
                                            {'label': 'Comparative', 'value': 'comparative'}
                                        ],
                                        value='single',
                                        labelStyle={'display': 'inline-block', 'marginRight': '10px'}
                                    )
                                ],
                                className="mb-3"
                            ),
                            # Channel Slider.
                            html.Div(
                                [
                                    html.Label("Select Channel (-1 for average):", style={'marginBottom': '5px'}),
                                    dcc.Slider(
                                        id='channel-slider',
                                        min=-1,
                                        max=0,  # Updated via callback.
                                        step=1,
                                        value=-1,
                                        marks={-1: 'Average'},
                                        tooltip={"placement": "bottom", "always_visible": False}
                                    )
                                ],
                                className="mb-3"
                            ),
                        ]
                    )
                ],
                body=True,
                className="mb-4",
                style={'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'borderRadius': '8px'}
            )
        ],
        xs=12,
        md=4
    )

def get_main_content():
    """Returns main content area with input image display, graph, and statistics card."""
    # Card for displaying the input image.
    input_image_card = dbc.Card(
        [
            dbc.CardHeader("Input Image"),
            dbc.CardBody(
                html.Img(id="input-image", style={"width": "100%", "maxHeight": "300px"})
            )
        ],
        className="mb-3",
        style={'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'borderRadius': '8px'}
    )
    graph_content = dbc.Col(
        [
            dcc.Loading(
                id="loading-graph",
                type="default",
                children=dcc.Graph(id="activation-heatmap", style={"height": "600px"})
            )
        ],
        xs=12,
        md=8
    )
    stats_card = dbc.Col(
        dbc.Card(
            [
                dbc.CardHeader("Activation Statistics"),
                dbc.CardBody(html.Div(id="activation-stats"))
            ],
            style={'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'borderRadius': '8px'}
        ),
        xs=12,
        md=4
    )
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(input_image_card, className="d-flex justify-content-center")
            ),
            dbc.Row(
                [graph_content, stats_card],
                className="mt-4 mb-4 justify-content-center"
            )
        ],
        fluid=True,
        className="text-center"
    )

def get_visualization_layout(available_layers):
    """Main visualization layout with sidebar and main content."""
    return dbc.Container(
        [
            dbc.Row(
                [get_sidebar(available_layers)],
                className="justify-content-center"
            ),
            dbc.Row(
                [get_main_content()],
                className="justify-content-center"
            )
        ],
        fluid=True,
        className="text-center"
    )

def get_documentation_layout():
    """Layout for the documentation page."""
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    html.Div(
                        [
                            html.H3("Documentation"),
                            html.P(
                                "DeepLens visualizes internal activations of a pretrained ResNet18 model using PyTorch. "
                                "Upload your image (or use a preset image), choose a layer, select a view mode, and use the channel slider for details."
                            ),
                            html.H5("User Controls"),
                            html.Ul(
                                [
                                    html.Li("File Upload: Provide an image to analyze."),
                                    html.Li("Use Preset Image: Load a default image for testing."),
                                    html.Li("Layer Dropdown: Choose a specific layer."),
                                    html.Li("View Mode: Toggle between single channel/average view and grid view, or use advanced modes like Grad-CAM."),
                                    html.Li("Channel Slider: When in Single view, select a channel or average.")
                                ]
                            ),
                            html.A("← Back to Dashboard", href="/dashboard", style={'fontWeight': 'bold'})
                        ]
                    ),
                    width=12
                )
            )
        ],
        fluid=True
    )

def get_master_layout(available_layers):
    """Master layout that aggregates the navbar, dashboard info modal, and a container for page content."""
    return html.Div(
        [
            get_navbar(),
            get_dashboard_info(),
            html.Div(id="page-content")
        ]
    )
