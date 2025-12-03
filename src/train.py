import torch
from tqdm import tqdm
from src.model import StemCellCNN
from src.dataset import get_data_loaders

EPOCHS = 10
LR = 1e-3
MODEL_PATH = "stemcell_cnn.pth"

def train():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_loader, test_loader, classes = get_data_loaders()

    model = StemCellCNN(num_classes=len(classes)).to(device)
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)

    for epoch in range(EPOCHS):
        model.train()
        running_loss = 0

        for images, labels in tqdm(train_loader):
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {running_loss/len(train_loader):.4f}")

        # Validation accuracy
        model.eval()
        correct, total = 0, 0
        with torch.no_grad():
            for images, labels in test_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                _, pred = torch.max(outputs, 1)
                correct += (pred == labels).sum().item()
                total += labels.size(0)
        print(f"Validation Accuracy: {correct/total:.4f}")

    torch.save(model.state_dict(), MODEL_PATH)
    print("Model saved at:", MODEL_PATH)
