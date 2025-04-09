import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def generate_activation_figure(act_data, selected_channel, view_mode="single"):
    """
    Generates a Plotly heatmap of the selected channel from activation data.

    Parameters:
        act_data: numpy.array of shape (channels, H, W)
        selected_channel: int (-1 = average of all channels)
        view_mode: "single", "grid", "comparative"

    Returns:
        A Plotly figure
    """
    if view_mode == "single":
        if selected_channel == -1:
            heatmap = act_data.mean(axis=0)
            title = "Average Activation Map"
        else:
            heatmap = act_data[selected_channel]
            title = f"Channel {selected_channel} Activation"

        fig = px.imshow(heatmap, color_continuous_scale="Viridis")
        fig.update_layout(title=title, margin=dict(t=30, b=10, l=10, r=10))
        return fig

    elif view_mode == "grid":
        num_channels = act_data.shape[0]
        fig = make_subplots(
            rows=int(np.ceil(num_channels / 4)), cols=4,
            subplot_titles=[f"Channel {i}" for i in range(num_channels)]
        )

        for i in range(num_channels):
            row = i // 4 + 1
            col = i % 4 + 1
            fig.add_trace(
                go.Heatmap(z=act_data[i], colorscale="Viridis"),
                row=row, col=col
            )

        fig.update_layout(title="Activation Map Grid", height=300 * int(np.ceil(num_channels / 4)))
        return fig

    elif view_mode == "comparative":
        fig = go.Figure()
        for i in range(act_data.shape[0]):
            fig.add_trace(go.Heatmap(z=act_data[i], colorscale="Viridis", showscale=False))

        fig.update_layout(title="Comparative Activation Maps")
        return fig
