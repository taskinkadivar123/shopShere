import torch
import torchvision.transforms as transforms
from torchvision.models import resnet18, ResNet18_Weights
from PIL import Image
import numpy as np
import os
from app.models import Product  # adjust to your app
import pickle

# Load resnet18 with updated weights syntax
model = resnet18(weights=ResNet18_Weights.DEFAULT)
model = torch.nn.Sequential(*(list(model.children())[:-1]))  # Remove classifier
model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

def get_embedding(image_path):
    image = Image.open(image_path).convert('RGB')
    image = transform(image).unsqueeze(0)
    with torch.no_grad():
        embedding = model(image)
    return embedding.squeeze().numpy()

embeddings = {}

for product in Product.objects.all():
    if product.product_image:  # Corrected field name
        path = product.product_image.path
        embeddings[product.id] = get_embedding(path)

with open('product_embeddings.pkl', 'wb') as f:
    pickle.dump(embeddings, f)
