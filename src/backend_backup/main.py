
# backend/main.py
from fastapi import FastAPI, UploadFile
import uvicorn
import numpy as np
import torch
from preprocessing import preprocess_image
from model import OrganoidClassifier

import faiss

app = FastAPI()

model = OrganoidClassifier()
model.load_state_dict(torch.load("saved_models/model.pt"))
model.eval()

index = faiss.read_index("saved_models/faiss.index")
paths = np.load("saved_models/image_paths.npy", allow_pickle=True)

@app.post("/predict")
async def predict(file: UploadFile):
    img_path = "temp.jpg"
    with open(img_path, "wb") as f:
        f.write(await file.read())

    img = preprocess_image(img_path)

    with torch.no_grad():
        logits = model(img)
        prob = torch.softmax(logits, dim=1)[0]
        cls = torch.argmax(prob).item()

        embedding = model.extract_features(img).numpy().astype("float32")
        D, I = index.search(embedding, 3)

    similar = [paths[i] for i in I[0]]

    return {
        "class": int(cls),
        "probabilities": prob.tolist(),
        "similar_images": similar
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
