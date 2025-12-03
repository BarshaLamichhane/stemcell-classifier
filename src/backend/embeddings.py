# backend/embeddings.py
import faiss
import numpy as np
import json
import base64
from io import BytesIO
from PIL import Image
from torchvision import transforms, models
import torch
import os

INDEX_PATH = "data/index.faiss"
META_PATH = "data/index_meta.json"
IMAGES_DIR = "data/images/index_images"   # images used in index
DEVICE = "mps" if torch.backends.mps.is_available() else ("cpu" if torch.cuda.is_available() else "cpu")

# load index + meta
index = None
meta = []
if os.path.exists(INDEX_PATH):
    index = faiss.read_index(INDEX_PATH)
if os.path.exists(META_PATH):
    with open(META_PATH, 'r') as f:
        meta = json.load(f)

# feature extractor (same as build script)
model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
model.classifier = torch.nn.Identity()
model = model.to(DEVICE).eval()

transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
])

def img_to_embedding(pil_img):
    x = transform(pil_img).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        feat = model(x)
    return feat.cpu().numpy().astype('float32').reshape(-1)

def get_similar_images(pil_img, topk=3):
    if index is None or len(meta) == 0:
        return []
    q = img_to_embedding(pil_img).reshape(1, -1)
    D, I = index.search(q, k=topk)
    results = []
    for idx in I[0]:
        if idx < 0 or idx >= len(meta):
            continue
        fname = meta[idx]
        # return URL path (frontend will prefix) OR base64:
        # base64:
        path = os.path.join(IMAGES_DIR, fname)
        try:
            with open(path, 'rb') as f:
                b64 = base64.b64encode(f.read()).decode('utf-8')
                results.append("data:image/jpeg;base64," + b64)
        except:
            results.append(fname)  # fallback
    return results

