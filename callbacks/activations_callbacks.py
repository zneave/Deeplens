import dash
from dash import Input, Output, State, ctx
import dash_bootstrap_components as dbc
import numpy as np
from dash import html
from src.models.model import model, activations, run_model
from src.utils.input_handler import process_image, get_preset_image
from src.models.model_utils import compute_channel_statistics
from src.visualization.activation import generate_activation_figure
import base64
import plotly.graph_objs as go

def register_callbacks(app):

    @app.callback(
        Output("channel-slider", "max"),
        Output("channel-slider", "marks"),
        Output("layer-dropdown", "options"),
        Output("layer-dropdown", "value"),
        Output("activation-heatmap", "figure"),
        Output("activation-stats", "children"),
        Output("input-image", "src"),
        Output("shared-upload-image", "data"),
        Input("upload-image", "contents"),
        Input("use-preset-btn", "n_clicks"),
        Input("layer-dropdown", "value"),
        Input("channel-slider", "value"),
        Input("view-mode", "value"),
        prevent_initial_call=True
    )
    def unified_activation_handler(upload_contents, n_clicks, layer_name, channel_idx, view_mode):
        print("\n=== [Activations] unified_activation_handler ===")
        triggered_id = ctx.triggered_id
        print("Triggered by:", triggered_id)

        if triggered_id in ["upload-image", "use-preset-btn"]:
            if triggered_id == "use-preset-btn":
                upload_contents = get_preset_image()

            if upload_contents is None:
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

            img_tensor = process_image(upload_contents)
            run_model(img_tensor)

            available_layers = list(activations.keys())
            first_layer = available_layers[0] if available_layers else None

            act = activations.get(first_layer)
            act_data = act[0]
            fig = generate_activation_figure(act_data, -1, view_mode="single")

            stats = compute_channel_statistics(act)
            stat_list = html.Ul([
                html.Li(f"Ch {i}: mean={s['mean']:.3f}, std={s['std']:.3f}, min={s['min']:.3f}, max={s['max']:.3f}")
                for i, s in stats.items()
            ])

            marks = {i: str(i) for i in range(len(act))}
            marks[-1] = "Avg"

            return (
                len(act) - 1,
                marks,
                [{'label': l, 'value': l} for l in available_layers],
                first_layer,
                fig,
                stat_list,
                upload_contents,
                upload_contents
            )

        elif layer_name and channel_idx is not None:
            img_tensor = process_image(upload_contents or get_preset_image())
            run_model(img_tensor)

            act = activations.get(layer_name)
            act_data = act[0]
            fig = generate_activation_figure(act_data, channel_idx, view_mode=view_mode)

            stats = compute_channel_statistics(act)
            stat_list = html.Ul([
                html.Li(f"Ch {i}: mean={s['mean']:.3f}, std={s['std']:.3f}, min={s['min']:.3f}, max={s['max']:.3f}")
                for i, s in stats.items()
            ])

            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, fig, stat_list, dash.no_update, dash.no_update

        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
