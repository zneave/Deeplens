import torch
import torch.nn as nn
import numpy as np

class ModelInfo:
    def __init__(self, name, layers):
        self.name = name
        self.layers = layers

def count_params(module):
    return sum(p.numel() for p in module.parameters() if p.requires_grad)

def get_module_info(name, module):
    try:
        shape = list(module.weight.shape) if hasattr(module, 'weight') else None

        activation = None
        if isinstance(module, nn.ReLU):
            activation = "ReLU"
        elif isinstance(module, nn.Sigmoid):
            activation = "Sigmoid"
        elif isinstance(module, nn.Tanh):
            activation = "Tanh"
        elif isinstance(module, nn.Softmax):
            activation = "Softmax"

        weight_stats = None
        if hasattr(module, 'weight'):
            weights = module.weight.detach().numpy()
            weight_stats = {
                "mean": np.mean(weights),
                "std": np.std(weights),
                "min": np.min(weights),
                "max": np.max(weights),
            }

        params = count_params(module)

        return {
            "name": name,
            "type": type(module).__name__,
            "shape": shape,
            "activation": activation,
            "weight_stats": weight_stats,
            "params": params
        }
    except Exception as e:
        print(f"Error in getting module info: {e}")
        return {}

def load_pytorch_model(model_or_path):
    if isinstance(model_or_path, nn.Module):
        model = model_or_path
    else:
        model = torch.load(model_or_path, map_location=torch.device('cpu'), weights_only=False)
        if isinstance(model, dict) and "model" in model:
            model = model["model"]

    if not isinstance(model, nn.Module):
        raise TypeError("Model must be an nn.Module")

    modules = []
    for name, module in model.named_modules():
        if name == "":
            continue
        modules.append(get_module_info(name, module))

    return ModelInfo(model.__class__.__name__, modules)
