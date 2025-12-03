import torch
from PIL import Image
from torchvision import transforms
from src.model import StemCellCNN
from src.dataset import get_data_loaders

def predict(image_path):
    _, _, classes = get_data_loaders()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = StemCellCNN(num_classes=len(classes))
    model.load_state_dict(torch.load("stemcell_cnn.pth", map_location=device))
    model.to(device)
    model.eval()

    transform = transforms.Compose([
        transforms.Resize((128, 128)),
        transforms.ToTensor(),
        transforms.Normalize([0.5,0.5,0.5],[0.5,0.5,0.5])
    ])

    img = Image.open(image_path).convert("RGB")
    img_tensor = transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(img_tensor)
        _, pred = torch.max(output, 1)
    print("Predicted class:", classes[pred.item()])
    return classes[pred.item()]
