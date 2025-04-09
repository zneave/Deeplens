import torch
import torchvision.models as models

activations = {}
gradients = {}

def get_pretrained_model():
    model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
    model.eval()

    def get_activation(name):
        def hook(module, input, output):
            activations[name] = output.detach()
        return hook

    def get_gradient(name):
        def hook(module, grad_input, grad_output):
            gradients[name] = grad_output[0].detach()
        return hook

    for name, module in model.named_modules():
        if any(layer in name for layer in ['layer1', 'layer2', 'layer3', 'layer4']):
            if isinstance(module, torch.nn.Conv2d):
                print(f"Registering hook for: {name}")
                module.register_forward_hook(get_activation(name))
                module.register_full_backward_hook(get_gradient(name))

    return model

model = get_pretrained_model()

def run_model(input_tensor=None):
    global activations, gradients
    activations.clear()
    gradients.clear()

    if input_tensor is None:
        input_tensor = torch.randn(1, 3, 224, 224)

    input_tensor.requires_grad_()
    output = model(input_tensor)

    top_class = output.argmax(dim=1)
    loss = output[0, top_class]
    loss.backward(retain_graph=True)

    print("Activations loaded:", list(activations.keys()))
    return activations

def get_model_layers(model):
    layers = []
    def recursive_find_layers(model, prefix=''):
        for name, module in model.named_children():
            full_name = prefix + name
            if isinstance(module, torch.nn.ModuleList):
                recursive_find_layers(module, full_name + ".")
            else:
                layers.append(full_name)
    recursive_find_layers(model)
    return layers

def get_gradients(layer_name):
    return gradients.get(layer_name, None)
