# src/model.py
import torch
import torchvision.models as models

activations = {}

def get_pretrained_model():
    model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
    model.eval()

    def get_activation(name):
        def hook(model, input, output):
            activations[name] = output.detach()
        return hook

    model.layer1.register_forward_hook(get_activation('layer1'))
    model.layer2.register_forward_hook(get_activation('layer2'))
    model.layer3.register_forward_hook(get_activation('layer3'))
    model.layer4.register_forward_hook(get_activation('layer4'))
    return model

model = get_pretrained_model()

def run_model(input_tensor=None):
    global activations
    if input_tensor is None:
        input_tensor = torch.randn(1, 3, 224, 224)
    with torch.no_grad():
        _ = model(input_tensor)
    return activations
