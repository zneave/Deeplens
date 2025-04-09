# src/input_handler.py
import io
import base64
from PIL import Image
import torch
import torchvision.transforms as transforms

def process_image(contents):
    """
    Process an uploaded image in base64 format and convert it into a tensor.
    The tensor is resized to 224x224 and normalized for ResNet input.
    """
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    image = Image.open(io.BytesIO(decoded)).convert('RGB')
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])
    tensor = transform(image).unsqueeze(0)
    return tensor

def get_preset_image():
    """
    Load a preset image from disk, encode it in base64, and return a data URI.
    Make sure the preset image exists at the given path.
    """
    with open("docs/images/preset_image.jpg", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return "data:image/jpeg;base64," + encoded_string
