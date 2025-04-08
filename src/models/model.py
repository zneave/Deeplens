# src/models/model.py

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

    model.layer1.register_forward_hook(get_activation('layer1'))
    model.layer2.register_forward_hook(get_activation('layer2'))
    model.layer3.register_forward_hook(get_activation('layer3'))
    model.layer4.register_forward_hook(get_activation('layer4'))

    model.layer1.register_full_backward_hook(get_gradient('layer1'))
    model.layer2.register_full_backward_hook(get_gradient('layer2'))
    model.layer3.register_full_backward_hook(get_gradient('layer3'))
    model.layer4.register_full_backward_hook(get_gradient('layer4'))

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

    return activations
