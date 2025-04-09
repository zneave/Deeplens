from dash import html, dcc
import dash_bootstrap_components as dbc

def get_eval_tab():
    return html.Div([
        html.H4("Model Evaluation"),
        html.P("Upload a dataset and evaluate the model on accuracy, precision, recall, and more."),

        dbc.Row([
            dbc.Col([
                html.H6("Upload Test Dataset"),
                dcc.Upload(
                    id="upload-eval-data",
                    children=html.Div([
                        "Drag and drop a folder or ", html.A("select one")
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
                html.Br(),
                dbc.Button("Run Evaluation", id="run-eval-btn", color="primary", n_clicks=0)
            ], md=4),

            dbc.Col([
                html.H6("Evaluation Results"),
                dcc.Loading(
                    dcc.Graph(id="eval-results-graph")
                ),
                html.Div(id="eval-metrics-summary", className="mt-3")
            ], md=8)
        ])
    ])