
# backend/model.py
import torch
import torch.nn as nn
from torchvision.models import mobilenet_v2

class OrganoidClassifier(nn.Module):
    def __init__(self, num_classes=3):
        super().__init__()
        base = mobilenet_v2(weights="DEFAULT")
        base.features[0][0].in_channels = 1  
        base.classifier[1] = nn.Linear(1280, num_classes)
        self.model = base

    def forward(self, x):
        return self.model(x)

    def extract_features(self, x):
        x = self.model.features(x)
        x = nn.functional.adaptive_avg_pool2d(x, (1,1))
        return x.view(x.size(0), -1)
