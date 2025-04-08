# src/visualization_adv.py

import torch
import torch.nn.functional as F
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def generate_gradcam(activation, gradients):
    weights = torch.mean(gradients, dim=(1, 2))
    cam = torch.zeros(activation.shape[1:], dtype=torch.float32)
    for i, w in enumerate(weights):
        cam += w * activation[i]
    cam = F.relu(cam)
    cam_np = cam.cpu().numpy()
    cam_np -= cam_np.min()
    if cam_np.max() != 0:
        cam_np /= cam_np.max()
    return cam_np


def generate_integrated_gradients(input_tensor, model, steps=50):
    baseline = torch.zeros_like(input_tensor)
    scaled_inputs = [(baseline + (float(i) / steps) * (input_tensor - baseline)).detach().requires_grad_()
                     for i in range(steps + 1)]

    target_class = model(input_tensor).argmax().item()
    grads_sum = torch.zeros_like(input_tensor)

    for input_scaled in scaled_inputs:
        output = model(input_scaled)
        model.zero_grad()
        output[0, target_class].backward()
        grads_sum += input_scaled.grad

    avg_gradients = grads_sum / steps
    integrated_gradients = (input_tensor - baseline) * avg_gradients
    return integrated_gradients.cpu().detach().numpy()


def generate_comparative_view(activation_list):
    n = len(activation_list)
    cols = min(n, 3)
    rows = (n + cols - 1) // cols
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=[f"View {i + 1}" for i in range(n)])
    for idx, act in enumerate(activation_list):
        row = idx // cols + 1
        col = idx % cols + 1
        trace = go.Heatmap(z=act, colorscale='Viridis', showscale=False)
        fig.add_trace(trace, row=row, col=col)
    fig.update_layout(title="Comparative Activation Views", height=300 * rows)
    return fig


def generate_advanced_visualization(act_data, selected_channel, view_mode, model=None, gradients=None, input_tensor=None):
    """
    Generate a visualization based on view mode.
    """
    if view_mode == "gradcam":
        if gradients is None:
            fig = px.imshow(np.zeros(act_data.shape[1:]), color_continuous_scale="Viridis")
            fig.update_layout(title="Grad-CAM not available (no gradients)")
            return fig
        cam = generate_gradcam(act_data, gradients)
        fig = px.imshow(cam, color_continuous_scale="Viridis")
        fig.update_layout(title="Grad-CAM")
        return fig

    elif view_mode == "integrated_gradients":
        if model is None or input_tensor is None:
            fig = px.imshow(np.zeros(act_data.shape[1:]), color_continuous_scale="Viridis")
            fig.update_layout(title="Integrated Gradients not available (missing model/input)")
            return fig
        ig = generate_integrated_gradients(input_tensor, model)
        ig_avg = ig[0].mean(axis=0)
        fig = px.imshow(ig_avg, color_continuous_scale="Viridis")
        fig.update_layout(title="Integrated Gradients")
        return fig

    elif view_mode == "comparative":
        act_np = act_data.cpu().numpy()
        heatmaps = [act_np.mean(axis=0), act_np.max(axis=0)]
        return generate_comparative_view(heatmaps)

    else:
        fig = px.imshow(act_data[selected_channel].cpu().numpy(), color_continuous_scale="Viridis")
        fig.update_layout(title=f"Channel {selected_channel} Activation")
        return fig
