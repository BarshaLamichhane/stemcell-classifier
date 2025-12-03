import cv2
import numpy as np
from PIL import Image

def enhance_image(img: Image.Image):
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    img_cv = cv2.GaussianBlur(img_cv, (3, 3), 0)
    img_cv = cv2.convertScaleAbs(img_cv, alpha=1.2, beta=10)
    return Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
