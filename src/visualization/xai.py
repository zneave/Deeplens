import torch
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import cv2


def generate_gradcam(activation, gradients, input_tensor=None):
    """
    Generate a Grad-CAM heatmap for a single image.

    Parameters:
        activation: torch.Tensor [C, H, W] or [1, C, H, W]
        gradients: torch.Tensor [C, H, W] or [1, C, H, W]
        input_tensor: Optional torch.Tensor [1, 3, H, W] to overlay

    Returns:
        A 2D numpy array or RGB overlay image
    """
    if activation.dim() == 4:
        activation = activation.squeeze(0)
    if gradients.dim() == 4:
        gradients = gradients.squeeze(0)

    if activation.dim() != 3 or gradients.dim() != 3:
        raise ValueError(f"[XAI ERROR] Expected [C,H,W] activation. Got {activation.shape}")

    weights = torch.mean(gradients, dim=(1, 2))

    cam = torch.zeros_like(activation[0])
    for i, w in enumerate(weights):
        cam += w * activation[i]

    cam = torch.relu(cam)
    cam_np = cam.cpu().detach().numpy()
    cam_np -= cam_np.min()
    cam_np /= (cam_np.max() + 1e-6)

    if input_tensor is not None:
        return overlay_heatmap_on_image(cam_np, input_tensor)
    return cam_np


def generate_integrated_gradients(input_tensor, model, baseline=None, steps=50):
    """
    Generates Integrated Gradients for the input image.

    Parameters:
        input_tensor: torch.Tensor of shape [1, C, H, W]
        model: The model (assumed to be in eval mode)
        baseline: Optional baseline tensor
        steps: Interpolation steps

    Returns:
        Numpy array of integrated gradients [C, H, W]
    """
    if baseline is None:
        baseline = torch.zeros_like(input_tensor)

    input_tensor = input_tensor.detach()
    baseline = baseline.detach()

    scaled_inputs = [baseline + (i / steps) * (input_tensor - baseline) for i in range(steps + 1)]
    scaled_inputs = torch.cat(scaled_inputs, dim=0).requires_grad_()

    output = model(scaled_inputs)
    target_class = output[0].argmax()

    grads = []
    for i in range(steps + 1):
        model.zero_grad()
        output[i, target_class].backward(retain_graph=True)
        grads.append(scaled_inputs.grad[i].unsqueeze(0))
        scaled_inputs.grad.zero_()

    grads_tensor = torch.cat(grads, dim=0)
    avg_gradients = grads_tensor.mean(dim=0)

    integrated_gradients = (input_tensor - baseline) * avg_gradients
    return integrated_gradients[0].cpu().detach().numpy()


def generate_xai_figure(heatmap):
    """
    Generates a Plotly heatmap from a numpy array.

    Parameters:
        heatmap: A 2D numpy array (H, W) or RGB (H, W, 3)

    Returns:
        A Plotly figure
    """
    if heatmap.ndim == 3 and heatmap.shape[2] == 3:
        from PIL import Image
        import io
        import base64

        img = Image.fromarray(heatmap.astype(np.uint8))
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        src = "data:image/png;base64," + img_str

        fig = go.Figure()
        fig.add_layout_image(
            dict(
                source=src,
                xref="x",
                yref="y",
                x=0,
                y=0,
                sizex=1,
                sizey=1,
                sizing="stretch",
                opacity=1,
                layer="below"
            )
        )
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        fig.update_layout(title="XAI Visualization", height=500)
        return fig
    else:
        fig = go.Figure(data=go.Heatmap(z=heatmap, colorscale='Viridis', showscale=True))
        fig.update_layout(title="XAI Visualization", height=500)
        return fig


def overlay_heatmap_on_image(heatmap, input_tensor):
    """
    Overlays a heatmap on top of an input image.

    Parameters:
        heatmap: 2D numpy array (H, W), values 0–1
        input_tensor: torch.Tensor [1, 3, H, W]

    Returns:
        RGB image with overlay (numpy array, dtype=uint8)
    """

    img = input_tensor.squeeze().detach().cpu().permute(1, 2, 0).numpy()
    img = (img - img.min()) / (img.max() - img.min())
    img = (img * 255).astype(np.uint8)

    heatmap_resized = cv2.resize(heatmap, (img.shape[1], img.shape[0]))

    if heatmap_resized.ndim == 3 and heatmap_resized.shape[2] == 1:
        heatmap_resized = heatmap_resized.squeeze()

    heatmap_uint8 = np.uint8(255 * heatmap_resized)

    if heatmap_uint8.ndim != 2:
        raise ValueError(f"[XAI ERROR] Expected heatmap to be 2D. Got shape: {heatmap_uint8.shape}")

    heatmap_color = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)

    overlay = cv2.addWeighted(img, 0.6, heatmap_color, 0.4, 0)
    return overlay


def generate_base64_overlay(heatmap_rgb):
    from PIL import Image
    import io
    import base64

    image = Image.fromarray(heatmap_rgb.astype(np.uint8))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"
