import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State

from ui.layouts.layout import get_master_layout
from ui.layouts.landing import get_landing_page
from ui.tabs.activations_tab import get_activations_tab
from ui.tabs.xai_tab import get_xai_tab
from ui.tabs.eval_tab import get_eval_tab
from ui.tabs.dashboard_tab import get_dashboard_tab
from ui.tabs.architecture_tab import get_architecture_tab

from callbacks.activations_callbacks import register_callbacks as register_activation_callbacks
from callbacks.xai_callbacks import register_callbacks as register_xai_callbacks
from callbacks.architecture_callbacks import register_callbacks as register_architecture_callbacks

external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div(
    id="main-container",
    children=[
        dcc.Location(id="url", refresh=False),
        get_master_layout()
    ]
)

register_activation_callbacks(app)
register_xai_callbacks(app)
register_architecture_callbacks(app)

print("=== Registered Callback Outputs ===")
for cb in app.callback_map:
    print(" -", cb)

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname == "/":
        return get_landing_page()
    elif pathname == "/dashboard":
        return get_dashboard_tab()
    elif pathname == "/dashboard/activations":
        return get_activations_tab()
    elif pathname == "/dashboard/xai":
        return get_xai_tab()
    elif pathname == "/dashboard/evaluation":
        return get_eval_tab()
    elif pathname == "/dashboard/architecture":
        return get_architecture_tab()
    else:
        return html.Div([
            html.H3("404"),
            html.P("Page not found. Please use the navigation links.")
        ], className="text-center mt-5")

@app.callback(
    Output("modal-info", "is_open"),
    [Input("open-info", "n_clicks"), Input("close-info", "n_clicks")],
    [State("modal-info", "is_open")]
)
def toggle_modal(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open

if __name__ == "__main__":
    app.run(debug=True)
