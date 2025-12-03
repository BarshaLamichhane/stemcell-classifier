import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

class OrganoidModel:
    def __init__(self):
        self.device = "cpu"
        self.model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
        self.model.classifier[1] = nn.Linear(1280, 2)  # healthy / unhealthy example
        self.model.load_state_dict(torch.load("model.pth", map_location="cpu"))
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ])

    def predict(self, img: Image.Image):
        x = self.transform(img).unsqueeze(0)
        with torch.no_grad():
            logits = self.model(x)
            probs = torch.softmax(logits, dim=1)
            conf, cls = torch.max(probs, 1)
        return int(cls), float(conf)
