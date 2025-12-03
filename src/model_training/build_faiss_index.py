# model_training/build_faiss_index.py
import os
import numpy as np
import faiss
import torch
from torchvision import transforms, models
from PIL import Image
import json

DATA_DIR = "../backend/data/images/index_images"  # a folder with many images
INDEX_OUT = "../backend/data/index.faiss"
META_OUT = "../backend/data/index_meta.json"
DEVICE = "mps" if torch.backends.mps.is_available() else ("cpu" if torch.cuda.is_available() else "cpu")

transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
])

# Load model (feature extractor)
model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
# remove classifier
model.classifier = torch.nn.Identity()
model = model.to(DEVICE).eval()

filenames = []
embs = []
for fname in sorted(os.listdir(DATA_DIR)):
    path = os.path.join(DATA_DIR, fname)
    try:
        img = Image.open(path).convert('RGB')
    except:
        continue
    x = transform(img).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        feat = model(x)
    feat = feat.cpu().numpy().reshape(-1)
    embs.append(feat)
    filenames.append(fname)

embs = np.stack(embs).astype('float32')
d = embs.shape[1]
index = faiss.IndexFlatL2(d)
index.add(embs)
faiss.write_index(index, INDEX_OUT)

with open(META_OUT, 'w') as f:
    json.dump(filenames, f)

print(f"Built FAISS index with {len(filenames)} vectors. saved to {INDEX_OUT}")
