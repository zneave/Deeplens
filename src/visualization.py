# src/visualization.py
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def generate_activation_figure(activation_tensor, selected_channel, view_mode="single"):
    """
    Generates a Plotly figure from an activation tensor.

    :param activation_tensor: A tensor with shape [channels, height, width].
    :param selected_channel: Integer indicating which channel to display (-1 for average).
    :param view_mode: "single" for single channel/average or "grid" to display all channels.
    :return: A Plotly figure.
    """
    if activation_tensor is None:
        return {}

    if view_mode == "single":
        if selected_channel == -1:
            data = activation_tensor.mean(dim=0).cpu().numpy()
            title_text = "Channel Average"
        else:
            if selected_channel < activation_tensor.shape[0]:
                data = activation_tensor[selected_channel].cpu().numpy()
                title_text = f"Channel {selected_channel}"
            else:
                data = activation_tensor.mean(dim=0).cpu().numpy()
                title_text = "Channel Average"
        fig = px.imshow(
            data,
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            title=title_text,
            height=600,
            margin=dict(l=20, r=20, t=60, b=20),
            template="plotly_white",
            yaxis=dict(scaleanchor="x", scaleratio=1)
        )
        return fig

    elif view_mode == "grid":
        channels = activation_tensor.shape[0]
        cols = 4
        rows = (channels // cols) + (1 if channels % cols != 0 else 0)
        fig = make_subplots(
            rows=rows,
            cols=cols,
            subplot_titles=[f"Ch {i}" for i in range(channels)]
        )
        for i in range(channels):
            row = (i // cols) + 1
            col = (i % cols) + 1
            data = activation_tensor[i].cpu().numpy()
            trace = go.Heatmap(z=data, colorscale='Viridis', showscale=False)
            fig.add_trace(trace, row=row, col=col)
        fig.update_layout(
            title="Grid View of All Channels",
            height=600 * rows / 2,
            margin=dict(l=20, r=20, t=60, b=20),
            template="plotly_white"
        )
        return fig

    return {}
