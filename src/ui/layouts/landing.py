import dash_bootstrap_components as dbc
from dash import dcc, html
from ui.layouts.layout import BUTTON_COLOR

def get_landing_page():
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    html.Div([
                        html.H1("Welcome to DeepLens", className="display-4 fw-bold mb-3"),
                        html.P(
                            "DeepLens is an interactive dashboard that lets you explore neural network internals. "
                            "Use the tabs above to switch between activation maps, XAI visualizations, and evaluation views.",
                            className="lead"
                        ),
                        dbc.Button(
                            "Enter Dashboard",
                            id="enter-dashboard",
                            href="/dashboard",
                            color="success",
                            size="lg",
                            className="mt-4 px-5",
                            style={"backgroundColor": BUTTON_COLOR, "borderColor": BUTTON_COLOR}
                        )
                    ], className="text-center p-4")
                ),
                className="justify-content-center"
            )
        ],
        fluid=True,
        className="pt-5"
    )