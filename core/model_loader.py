import torch
import torch.nn as nn

class ModelInfo:
    def __init__(self, name, layers):
        self.name = name
        self.layers = layers  # List of dicts: [{name, type, shape, params}, ...]

def count_params(module):
    return sum(p.numel() for p in module.parameters() if p.requires_grad)

def get_module_info(name, module):
    try:
        shape = list(module.weight.shape)
    except AttributeError:
        shape = None
    return {
        "name": name,
        "type": type(module).__name__,
        "shape": shape,
        "params": count_params(module)
    }

def load_pytorch_model(path):
    try:
        model = torch.load(path, map_location=torch.device('cpu'))
        if isinstance(model, dict) and "model" in model:
            model = model["model"]

        if hasattr(model, 'state_dict') and not isinstance(model, nn.Module):
            raise TypeError("Loaded object is not a torch.nn.Module")

        if isinstance(model, nn.Module):
            modules = []
            for name, module in model.named_modules():
                if name == "":
                    continue
                modules.append(get_module_info(name, module))
            return ModelInfo("PyTorch Model", modules)
        else:
            raise Exception("Model file does not contain a nn.Module.")
    except Exception as e:
        raise RuntimeError(f"Failed to load PyTorch model: {e}")
