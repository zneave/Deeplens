# src/dashboard_info.py
import dash_bootstrap_components as dbc
from dash import html

def get_dashboard_info():
    """
    Returns a modal component containing detailed descriptions and usage info
    for the dashboard.
    """
    modal = dbc.Modal(
        [
            dbc.ModalHeader("Dashboard Overview"),
            dbc.ModalBody(
                [
                    html.H5("Purpose"),
                    html.P(
                        "This dashboard allows you to explore the internal activations of a "
                        "pretrained ResNet18 model from PyTorch. It helps you understand how features "
                        "are extracted at different layers."
                    ),
                    html.H5("File Upload"),
                    html.P(
                        "Upload an image to run through the model. The image will be pre-processed "
                        "to meet the model’s input size and normalization requirements."
                    ),
                    html.H5("Layer Selection"),
                    html.P(
                        "Select a model layer from the dropdown. Each layer captures different "
                        "features. The available layers are hooked to extract activations."
                    ),
                    html.H5("Channel Slider"),
                    html.P(
                        "Adjust the slider to pick a specific activation channel. Setting it to '-1' "
                        "will show the average over all channels."
                    ),
                    html.H5("Visualization"),
                    html.P(
                        "Activation maps are displayed as heatmaps. Use the controls above to adjust "
                        "what you see, and use the Documentation tab for further details."
                    )
                ]
            ),
            dbc.ModalFooter(
                dbc.Button("Close", id="close-info", className="ml-auto", n_clicks=0)
            ),
        ],
        id="modal-info",
        is_open=False,
        size="lg",
    )
    return modal
