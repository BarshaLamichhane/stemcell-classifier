# backend/train.py
import torch
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder
import torch.optim as optim
import torch.nn as nn

from preprocessing import preprocess_transform
from model import OrganoidClassifier

def load_dataset():
    train = ImageFolder("data/train", transform=preprocess_transform)
    val = ImageFolder("data/test", transform=preprocess_transform)
    return train, val

def train_model():
    train_ds, val_ds = load_dataset()
    train_dl = DataLoader(train_ds, batch_size=16, shuffle=True)
    val_dl = DataLoader(val_ds, batch_size=16)

    model = OrganoidClassifier()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.0005)

    for epoch in range(3):  # Keep it small for laptop
        model.train()
        for img, label in train_dl:
            optimizer.zero_grad()
            out = model(img)
            loss = criterion(out, label)
            loss.backward()
            optimizer.step()

        print(f"Epoch {epoch} Loss: {loss.item():.4f}")

    torch.save(model.state_dict(), "saved_models/model.pt")
    print("Model saved.")

if __name__ == "__main__":
    train_model()
