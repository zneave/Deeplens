# src/model_utils.py

def get_activation_shape(selected_layer, activations):
    """
    Returns the shape of the activation for the given layer or None.
    """
    act = activations.get(selected_layer)
    return act.shape if act is not None else None

def is_image_activation(act):
    """
    Returns True if the activation tensor is 4D
    (expected shape: [batch, channels, height, width]).
    """
    return act is not None and len(act.shape) == 4

def compute_channel_statistics(act):
    """
    Computes per-channel statistics for an image-like activation.
    Assumes act is 4D and processes the first sample in the batch.
    Returns a dict mapping channel indices to a dict of statistics.
    """
    if act is None or not is_image_activation(act):
        return {}
    stats = {}
    channels = act.shape[1]
    for i in range(channels):
        channel_data = act[0, i]
        stats[i] = {
            "mean": float(channel_data.mean().item()),
            "std": float(channel_data.std().item()),
            "min": float(channel_data.min().item()),
            "max": float(channel_data.max().item())
        }
    return stats
