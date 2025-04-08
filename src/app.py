import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State

from ui.layout import (
    get_master_layout,
    get_visualization_layout,
    get_documentation_layout,
    get_theme_style
)
from ui.landing import get_landing_page
from ui.dashboard_info import get_dashboard_info

from models.model import run_model, activations, model, gradients
from utils.input_handler import process_image, get_preset_image
from models.model_utils import is_image_activation, compute_channel_statistics

external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server

run_model()
available_layers = list(activations.keys())

app.layout = html.Div(
    id="main-container",
    style=get_theme_style(is_dark=False),
    children=[
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="preset-store", data=False),
        get_master_layout(available_layers)
    ]
)

@app.callback(
    Output("main-container", "style"),
    Input("toggle-dark", "n_clicks")
)
def toggle_dark_mode(n_clicks):
    if n_clicks and n_clicks % 2 == 1:
        return get_theme_style(is_dark=True)
    return get_theme_style(is_dark=False)

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname == "/" or pathname is None:
        return get_landing_page()
    elif pathname == "/dashboard":
        return get_visualization_layout(available_layers)
    elif pathname == "/documentation":
        return get_documentation_layout()
    else:
        return html.Div(
            [
                html.H3("404"),
                html.P("Page not found. Please use the navigation links.")
            ],
            className="text-center mt-5"
        )

@app.callback(
    Output("preset-store", "data"),
    Input("use-preset-btn", "n_clicks"),
    prevent_initial_call=True
)
def set_preset(n_clicks):
    if n_clicks:
        return True
    return False

@app.callback(
    Output("channel-slider", "max"),
    Output("channel-slider", "marks"),
    Input("layer-dropdown", "value"),
    Input("upload-image", "contents"),
    Input("preset-store", "data")
)
def update_slider_properties(selected_layer, upload_contents, preset_flag):
    if upload_contents is None and preset_flag:
        upload_contents = get_preset_image()
    if upload_contents is not None:
        img_tensor = process_image(upload_contents)
        run_model(img_tensor)
    act = activations.get(selected_layer)
    if act is None or not is_image_activation(act):
        return 0, {0: "N/A"}
    channels = act.shape[1]
    if channels <= 1:
        return 0, {0: "N/A"}
    max_channel = channels - 1
    marks = {-1: "Average"}
    if channels > 5:
        marks[0] = "0"
        marks[max_channel] = str(max_channel)
        mid = max_channel // 2
        marks[mid] = str(mid)
    else:
        for i in range(channels):
            marks[i] = str(i)
    return max_channel, marks

@app.callback(
    Output("activation-heatmap", "figure"),
    Output("activation-stats", "children"),
    Input("layer-dropdown", "value"),
    Input("channel-slider", "value"),
    Input("upload-image", "contents"),
    Input("preset-store", "data"),
    Input("view-mode", "value")
)
def update_activation_map(selected_layer, selected_channel, upload_contents, preset_flag, view_mode):
    if upload_contents is None and not preset_flag:
        empty_fig = {"data": [], "layout": {"title": "No image provided. Please upload an image or use a preset image."}}
        return empty_fig, "No statistics available."
    if upload_contents is None and preset_flag:
        upload_contents = get_preset_image()
    if upload_contents is not None:
        img_tensor = process_image(upload_contents)
        run_model(img_tensor)
    else:
        return {"data": [], "layout": {"title": "No input image"}}, "No statistics available."

    act = activations.get(selected_layer)
    if act is None:
        return {"data": [], "layout": {"title": f"No activations for layer '{selected_layer}'"}}, "No statistics available."

    if not is_image_activation(act):
        empty_fig = {"data": [], "layout": {"title": f"Layer '{selected_layer}' has unsupported shape: {act.shape}"}}
        return empty_fig, "Unsupported activation shape for statistics."

    stats = ""
    stat_dict = compute_channel_statistics(act)
    stats_list = [
        f"Ch {i}: mean={stat['mean']:.3f}, std={stat['std']:.3f}, min={stat['min']:.3f}, max={stat['max']:.3f}"
        for i, stat in stat_dict.items()
    ]
    stats = html.Ul([html.Li(item) for item in stats_list])

    act_data = act[0]

    if view_mode in ["gradcam", "integrated_gradients", "comparative"]:
        from visualization_adv import generate_advanced_visualization
        fig = generate_advanced_visualization(
            act_data,
            selected_channel,
            view_mode,
            model=model,
            gradients=gradients.get(selected_layer),
            input_tensor=img_tensor
        )
    else:
        from visualization import generate_activation_figure
        fig = generate_activation_figure(act_data, selected_channel, view_mode="single")

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

if __name__ == "__main__":
    app.run(debug=True)
