
# backend/preprocessing.py
import cv2
import numpy as np
from torchvision import transforms

preprocess_transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((128, 128)),
    transforms.Grayscale(num_output_channels=1),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5]),
])

def preprocess_image(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    img = cv2.equalizeHist(img)
    img = np.stack([img], axis=-1)  
    return preprocess_transform(img).unsqueeze(0)
