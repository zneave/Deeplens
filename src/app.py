# src/app.py
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State

from model import run_model, activations
from input_handler import process_image
from visualization import generate_activation_figure
from dashboard_info import get_dashboard_info
from model_utils import is_image_activation, compute_channel_statistics

run_model()

available_layers = list(activations.keys())

external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server

dashboard_modal = get_dashboard_info()

navbar = dbc.NavbarSimple(
    brand="DeepLens Dashboard",
    brand_href="/",
    color="primary",
    dark=True,
    children=[
        dbc.NavItem(dbc.NavLink("Visualization", href="/")),
        dbc.NavItem(dbc.NavLink("Documentation", href="/documentation")),
        dbc.Button("Learn More", id="open-info", color="light", size="sm", n_clicks=0)
    ],
)

visualization_layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Input & Controls"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(
                            dcc.Upload(
                                id='upload-image',
                                children=html.Div(['Drag and Drop or ', html.A('Select an Image')]),
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
                            xs=12
                        )
                    ], style={'marginBottom': '20px'}),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Select Layer:"),
                            dcc.Dropdown(
                                id='layer-dropdown',
                                options=[{'label': layer, 'value': layer} for layer in available_layers],
                                value=available_layers[0] if available_layers else None,
                                clearable=False
                            )
                        ], xs=12, sm=6),
                        dbc.Col([
                            html.Label("View Mode:"),
                            dcc.RadioItems(
                                id='view-mode',
                                options=[
                                    {'label': 'Single', 'value': 'single'},
                                    {'label': 'Grid', 'value': 'grid'}
                                ],
                                value='single',
                                labelStyle={'display': 'inline-block', 'marginRight': '10px'}
                            )
                        ], xs=12, sm=6)
                    ], style={'marginBottom': '20px'}),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Select Channel (-1 for average):"),
                            dcc.Slider(
                                id='channel-slider',
                                min=-1,
                                max=0,
                                step=1,
                                value=-1,
                                marks={-1: 'Average'}
                            )
                        ], xs=12)
                    ])
                ])
            ]),
            width=12
        )
    ], style={'marginTop': '20px'}),
    dbc.Row(
        dbc.Col(
            dcc.Graph(id='activation-heatmap', style={'height': '600px'}),
            width=12
        ),
        style={'marginTop': '20px', 'marginBottom': '20px'}
    ),
    dbc.Row(
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Activation Statistics"),
                dbc.CardBody(html.Div(id='activation-stats'))
            ]),
            width=12
        )
    )
], fluid=True)

documentation_layout = dbc.Container([
    dbc.Row(
        dbc.Col([
            html.H3("Documentation"),
            html.P(
                "This dashboard visualizes the internal activations of a pretrained ResNet18 model using PyTorch. "
                "Upload an image to get custom activations, choose a model layer, pick a view mode (Single or Grid), "
                "and select a channel (when in Single view) to see the heatmap."
            ),
            html.H5("User Controls"),
            html.Ul([
                html.Li("File Upload: Provide an image to process through the model."),
                html.Li("Layer Dropdown: Select the target layer for activation visualization."),
                html.Li("View Mode: Toggle between a single channel (or average) view and a grid view of all channels."),
                html.Li("Channel Slider: When in Single view, select a channel or average (-1)."),
                html.Li("Learn More: Opens a modal with detailed help.")
            ]),
            dcc.Link("← Back to Visualization", href="/", style={'fontWeight': 'bold'})
        ], width=12)
    )
], fluid=True)

app.layout = dbc.Container([
    dcc.Location(id="url", refresh=False),
    navbar,
    dashboard_modal,
    html.Div(id="page-content")
], fluid=True)

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    return documentation_layout if pathname == "/documentation" else visualization_layout

@app.callback(
    Output('channel-slider', 'max'),
    Output('channel-slider', 'marks'),
    Input('layer-dropdown', 'value'),
    Input('upload-image', 'contents')
)
def update_slider_properties(selected_layer, upload_contents):
    if upload_contents is not None:
        img_tensor = process_image(upload_contents)
        run_model(img_tensor)
    act = activations.get(selected_layer)
    if act is None or not (is_image_activation(act)):
        return 0, {0: 'N/A'}
    channels = act.shape[1]
    if channels <= 1:
        return 0, {0: 'N/A'}
    max_channel = channels - 1
    marks = {-1: 'Average'}
    for i in range(channels):
        marks[i] = str(i)
    return max_channel, marks

@app.callback(
    Output('activation-heatmap', 'figure'),
    Output('activation-stats', 'children'),
    Input('layer-dropdown', 'value'),
    Input('channel-slider', 'value'),
    Input('upload-image', 'contents'),
    Input('view-mode', 'value')
)
def update_activation_map(selected_layer, selected_channel, upload_contents, view_mode):
    if upload_contents is not None:
        img_tensor = process_image(upload_contents)
        run_model(img_tensor)
    act = activations.get(selected_layer)
    if act is None:
        return {
            "data": [],
            "layout": {"title": f"No activations for layer '{selected_layer}'"}
        }, "No statistics available."
    stats = ""
    if is_image_activation(act):
        from model_utils import compute_channel_statistics
        stat_dict = compute_channel_statistics(act)
        stats_list = [f"Ch {i}: mean={stat['mean']:.3f}, std={stat['std']:.3f}, min={stat['min']:.3f}, max={stat['max']:.3f}"
                      for i, stat in stat_dict.items()]
        stats = html.Ul([html.Li(item) for item in stats_list])
    else:
        stats = "Activation shape not suitable for statistical summary."

    if not is_image_activation(act):
        return {
            "data": [],
            "layout": {"title": f"Layer '{selected_layer}' has unsupported shape: {act.shape}"}
        }, stats

    act_data = act[0]
    fig = generate_activation_figure(act_data, selected_channel, view_mode=view_mode)
    fig.update_layout(title=f"{selected_layer}: {fig.layout.title.text}")
    return fig, stats

@app.callback(
    Output("modal-info", "is_open"),
    [Input("open-info", "n_clicks"), Input("close-info", "n_clicks")],
    [State("modal-info", "is_open")]
)
def toggle_modal(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open

if __name__ == '__main__':
    app.run(debug=True)
