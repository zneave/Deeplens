import dash_bootstrap_components as dbc
from dash import dcc, html
from ui.layout import BUTTON_COLOR

def get_landing_page():
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    html.H1("Welcome to DeepLens"),
                    className="text-center mt-5"
                )
            ),
            dbc.Row(
                dbc.Col(
                    html.P(
                        "DeepLens is an interactive dashboard that lets you explore neural network internals. "
                        "Click the button below to enter the dashboard and start exploring activations!",
                        className="text-center"
                    )
                )
            ),
            dbc.Row(
                dbc.Col(
                    dbc.Button(
                        "Enter Dashboard",
                        id="enter-dashboard",
                        color=BUTTON_COLOR,
                        size="lg",
                        href="/dashboard"
                    ),
                    className="text-center mt-4"
                )
            )
        ],
        fluid=True,
        className="mt-5"
    )
