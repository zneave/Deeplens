import dash
from dash import Input, Output, State, ctx
import plotly.graph_objects as go
import numpy as np

from src.visualization.xai import (
    generate_gradcam,
    generate_integrated_gradients,
    generate_base64_overlay,
    generate_xai_figure
)
from src.models.model import activations, model, run_model, get_gradients
from src.utils.input_handler import process_image, get_preset_image


def register_callbacks(app):

    @app.callback(
        Output("xai-layer-dropdown", "options"),
        Output("xai-layer-dropdown", "value"),
        Output("xai-channel-slider", "max"),
        Output("xai-channel-slider", "marks"),
        Input("xai-upload-image", "contents"),
        Input("xai-use-preset-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def handle_xai_layer_controls(upload_contents, n_clicks):
        print("\n[XAI LOG] --> In handle_xai_layer_controls callback")

        triggered_id = ctx.triggered_id
        print(f"[XAI LOG] Triggered by: {triggered_id}")

        if triggered_id == "xai-use-preset-btn" or (upload_contents is None and n_clicks):
            print("[XAI LOG] Preset button triggered or upload missing; using preset image.")
            upload_contents = get_preset_image()

        if upload_contents is None:
            print("[XAI LOG] No image available after preset check. Exiting callback.")
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update

        print("[XAI LOG] Processing image for layer controls...")
        try:
            img_tensor = process_image(upload_contents)
            run_model(img_tensor)
        except Exception as e:
            print(f"[XAI LOG] Error during image processing or model run: {e}")
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update

        available_layers = list(activations.keys())
        if not available_layers:
            print("[XAI LOG] No activations found after running model.")
            return [], None, 0, {}

        first_layer = available_layers[0]
        act = activations.get(first_layer)
        channels = act.shape[1] if act is not None else 0
        print(f"[XAI LOG] Available layers: {available_layers}")
        print(f"[XAI LOG] First layer: {first_layer} with {channels} channels.")

        marks = {-1: "Avg"}
        if channels > 5:
            marks[0] = "0"
            marks[channels // 2] = str(channels // 2)
            marks[channels - 1] = str(channels - 1)
        else:
            for i in range(channels):
                marks[i] = str(i)

        layer_options = [{'label': l, 'value': l} for l in available_layers]
        print(f"[XAI LOG] Layer dropdown options set.")

        return layer_options, first_layer, channels - 1, marks

    @app.callback(
        Output("xai-heatmap", "figure"),
        Output("xai-preview-img", "src"),
        Output("xai-heatmap", "style"),
        Output("xai-preview-img", "style"),
        Input("xai-view-mode", "value"),
        Input("xai-layer-dropdown", "value"),
        Input("xai-channel-slider", "value"),
        Input("xai-image-scale-slider", "value"),
        State("xai-upload-image", "contents"),
        State("xai-use-preset-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def generate_xai_visualization(view_mode, layer_name, channel_idx, scale_value, upload_contents, n_clicks):
        print("\n[XAI LOG] --> In generate_xai_visualization callback")
        print(f"[XAI LOG] View mode: {view_mode}, Selected Layer: {layer_name}, Channel: {channel_idx}, Scale: {scale_value}")
        print(f"[XAI LOG] Triggered by: {ctx.triggered_id}")

        if ctx.triggered_id == "xai-use-preset-btn" or (upload_contents is None and n_clicks):
            print("[XAI LOG] Using preset image...")
            upload_contents = get_preset_image()

        if upload_contents is None or layer_name is None:
            print("[XAI LOG] Missing upload image or layer selection. Exiting callback.")
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update

        try:
            print("[XAI LOG] Processing image and running model...")
            img_tensor = process_image(upload_contents)
            run_model(img_tensor)
        except Exception as e:
            print(f"[XAI LOG] Error during processing/model run: {e}")
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update

        act = activations.get(layer_name)
        if act is None:
            print(f"[XAI LOG] No activations found for layer: {layer_name}")
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update

        if view_mode == "gradcam":
            print("[XAI LOG] Generating Grad-CAM...")
            gradients = get_gradients(layer_name)
            if gradients is None:
                print("[XAI LOG] No gradients available.")
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update

            activation = act[0]
            grads = gradients[0]
            heatmap = generate_gradcam(activation, grads, input_tensor=img_tensor)

        elif view_mode == "integrated_gradients":
            print("[XAI LOG] Generating Integrated Gradients...")
            ig = generate_integrated_gradients(img_tensor, model)
            heatmap = ig.mean(axis=0)

        else:
            print("[XAI LOG] Invalid view mode.")
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update

        if isinstance(heatmap, np.ndarray) and heatmap.ndim == 3:
            print("[XAI LOG] Detected RGB overlay image. Returning base64 preview.")
            return go.Figure(), generate_base64_overlay(heatmap), {"display": "none"}, {
                "display": "block",
                "width": f"{scale_value}%",
                "height": "auto",
                "margin": "0 auto",
                "borderRadius": "8px"
            }
        else:
            print("[XAI LOG] Returning Plotly heatmap.")
            fig = generate_xai_figure(heatmap)
            return fig, "", {"display": "block"}, {"display": "none"}
