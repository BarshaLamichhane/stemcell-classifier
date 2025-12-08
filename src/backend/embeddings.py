# backend/embeddings.py
import os
import faiss
import numpy as np
import torch
from preprocessing import preprocess_image
from model import OrganoidClassifier

def build_embedding_index(img_dir="data/train"):
    model = OrganoidClassifier()
    model.load_state_dict(torch.load("saved_models/model.pt"))
    model.eval()

    embeddings = []
    paths = []

    for root, _, files in os.walk(img_dir):
        for f in files:
            if f.endswith(".png") or f.endswith(".jpg"):
                p = os.path.join(root, f)
                img = preprocess_image(p)
                with torch.no_grad():
                    emb = model.extract_features(img).numpy()
                embeddings.append(emb)
                paths.append(p)

    embeddings = np.vstack(embeddings).astype("float32")
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, "saved_models/faiss.index")
    np.save("saved_models/image_paths.npy", np.array(paths))

    print("Embedding index built.")

if __name__ == "__main__":
    build_embedding_index()
