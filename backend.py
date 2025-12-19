import os
import sys
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import transforms, models, datasets
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import numpy as np
import uvicorn
import faiss


# ============================================================
# GLOBAL SETTINGS
# ============================================================

DATA_DIR = "data"
MODEL_PATH = "model.pth"
FAISS_PATH = "faiss.index"
LABEL_PATH = "labels.npy"
EMB_PATH = "embeddings.npy"

DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

class_names = ["After", "Before"]  # your dataset categories


# ============================================================
# TRANSFORMS
# ============================================================

preprocess_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])


# ============================================================
# MODEL
# ============================================================

class OrganoidClassifier(nn.Module):
    def __init__(self, num_classes=2):
        super().__init__()

        # NO pretrained weights → avoids SSL certificate errors
        self.base = models.mobilenet_v2(weights=None)

        # Replace final layer
        self.base.classifier[1] = nn.Linear(1280, num_classes)

    def forward(self, x):
        return self.base(x)

    def extract_features(self, x):
        x = self.base.features(x)
        x = torch.nn.functional.adaptive_avg_pool2d(x, 1)
        return torch.flatten(x, 1)


# ============================================================
# DATA LOADING
# ============================================================

def load_dataset():
    train = datasets.ImageFolder(f"{DATA_DIR}/training", transform=preprocess_transform)
    test = datasets.ImageFolder(f"{DATA_DIR}/testing", transform=preprocess_transform)
    return train, test


# ============================================================
# TRAIN FUNCTION
# ============================================================

def train_model():
    print("📌 Starting training...")

    train_data, test_data = load_dataset()

    train_loader = DataLoader(train_data, batch_size=16, shuffle=True)
    val_loader = DataLoader(test_data, batch_size=16)

    model = OrganoidClassifier(num_classes=2).to(DEVICE)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)

    EPOCHS = 5
    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0

        for imgs, labels in train_loader:
            
            imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)

            optimizer.zero_grad()
            outputs = model(imgs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        print(f"Epoch {epoch+1}/{EPOCHS} - Loss: {total_loss:.4f}")

    torch.save(model.state_dict(), MODEL_PATH)
    print(f"✅ Model saved to {MODEL_PATH}")


# ============================================================
# BUILD FAISS INDEX
# ============================================================

def build_index():
    print("📌 Building FAISS index...")

    if not os.path.exists(MODEL_PATH):
        print("❌ ERROR: model.pth not found. Run: python backend.py train ")
        return

    train_data, _ = load_dataset()
    loader = DataLoader(train_data, batch_size=16)

    # ===============================================
    # SAVE IMAGE PATHS FOR FETCHING /image/{idx}
    # ===============================================
    image_files = train_data.imgs              # list of (file_path, label)
    paths = [f[0] for f in image_files]        # extract only file paths
    np.save("image_paths.npy", np.array(paths))
    print("✅ Saved image_paths.npy")

    model = OrganoidClassifier(num_classes=2)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.eval().to(DEVICE)

    all_embeddings = []
    all_labels = []

    with torch.no_grad():
        for imgs, labels in loader:
            imgs = imgs.to(DEVICE)
            feats = model.extract_features(imgs)
            all_embeddings.append(feats.cpu().numpy())
            all_labels.append(labels.numpy())

    X = np.vstack(all_embeddings).astype("float32")
    Y = np.hstack(all_labels)

    np.save(EMB_PATH, X)
    np.save(LABEL_PATH, Y)

    index = faiss.IndexFlatL2(X.shape[1])
    index.add(X)
    faiss.write_index(index, FAISS_PATH)

    print(f"✅ FAISS index saved to {FAISS_PATH}")
    print(f"Total embeddings: {len(X)}")

# ============================================================
# FASTAPI SERVER
# ============================================================

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = None
faiss_index = None


@app.on_event("startup")
def load_all():
    global model, faiss_index

    if os.path.exists(MODEL_PATH):
        model = OrganoidClassifier(2)
        model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
        model.eval()
        print("✅ Model loaded")
    else:
        print("⚠️ model.pth not found. Prediction endpoint will not work.")

    if os.path.exists(FAISS_PATH):
        faiss_index = faiss.read_index(FAISS_PATH)
        print("✅ FAISS index loaded")
    else:
        print("⚠️ faiss.index not found. Similarity search will not work.")


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if model is None:
        return {"error": "Model not loaded. Train first."}

    image = Image.open(file.file).convert("RGB")
    x = preprocess_transform(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        logits = model(x)
        probs = torch.softmax(logits, dim=1)
        pred = torch.argmax(probs).item()

    return {"prediction": class_names[pred], "probabilities": probs.cpu().numpy().tolist()}


@app.post("/search")
async def search_similar(file: UploadFile = File(...)):
    if faiss_index is None:
        return {"error": "FAISS index not loaded. Build index first."}

    image = Image.open(file.file).convert("RGB")
    x = preprocess_transform(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        emb = model.extract_features(x).cpu().numpy().astype("float32")

    D, I = faiss_index.search(emb, k=5)
    return {"indices": I.tolist(), "distances": D.tolist()}

# ============================================================
# IMAGE FETCH ENDPOINT (returns actual image bytes)
# ============================================================

from fastapi.responses import StreamingResponse
import io

IMAGE_PATHS = "image_paths.npy"  # or saved_models/image_paths.npy depending on your project

@app.get("/image/{idx}")
def get_image(idx: int):
    import numpy as np

    if not os.path.exists(IMAGE_PATHS):
        return {"error": "image_paths.npy not found. Run build-index again."}

    paths = np.load(IMAGE_PATHS, allow_pickle=True)

    if idx < 0 or idx >= len(paths):
        return {"error": "index out of range"}

    img_path = paths[idx]

    # Load and return image
    pil = Image.open(img_path).convert("RGB")
    buf = io.BytesIO()
    pil.thumbnail((400, 400))
    pil.save(buf, format="JPEG")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/jpeg")

# ============================================================
# CLI ENTRY
# ============================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
Usage:
    python backend.py train
    python backend.py build-index
    python backend.py serve
""")
        exit()

    cmd = sys.argv[1]

    if cmd == "train":
        train_model()

    elif cmd == "build-index":
        build_index()

    elif cmd == "serve":
        uvicorn.run(app, host="0.0.0.0", port=8000)

    else:
        print("Unknown command")
