# backend/preprocessing.py
import cv2
import numpy as np
from PIL import Image
from torchvision import transforms

# Use standard ImageNet normalization (3-channel) for convenience with pretrained MobileNet
IMG_SIZE = 224

preprocess_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

def read_image_pil(path_or_bytes):
    """
    Accept either a filesystem path or raw bytes and return a PIL RGB image.
    """
    if isinstance(path_or_bytes, (bytes, bytearray)):
        from io import BytesIO
        return Image.open(BytesIO(path_or_bytes)).convert("RGB")
    return Image.open(path_or_bytes).convert("RGB")

def preprocess_pil(pil_img):
    """
    Input: PIL Image (RGB)
    Output: tensor ready for model (unsqueezed batch)
    """
    return preprocess_transform(pil_img).unsqueeze(0)

def simple_enhance(pil_img):
    """
    Lightweight enhancement using OpenCV: CLAHE contrast on L channel.
    Returns PIL Image (RGB).
    """
    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    merged = cv2.merge((cl, a, b))
    final = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
    print(Image.fromarray(cv2.cvtColor(final, cv2.COLOR_BGR2RGB)))
    return Image.fromarray(cv2.cvtColor(final, cv2.COLOR_BGR2RGB))
