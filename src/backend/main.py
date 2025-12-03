# backend/main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image
import io, base64
from model import OrganoidModel
from preprocessing import enhance_image
from embeddings import get_similar_images
import numpy as np
import cv2

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/static/images", StaticFiles(directory="data/images/index_images"), name="static_images")

model = OrganoidModel()

def pil_to_base64(pil_img, fmt='JPEG'):
    buff = io.BytesIO()
    pil_img.save(buff, format=fmt)
    return "data:image/jpeg;base64," + base64.b64encode(buff.getvalue()).decode('utf-8')

def make_mask(img_pil):
    # very simple mask via grayscale threshold (placeholder for segmentation)
    img = np.array(img_pil.convert('L'))
    _, thr = cv2.threshold(img, 0, 255, cv2.THRESH_OTSU)
    mask = Image.fromarray(thr).convert('RGBA')
    # colorize mask
    mask_arr = np.array(mask)
    # make red mask with alpha
    color_mask = np.zeros((*mask_arr.shape[:2], 4), dtype=np.uint8)
    color_mask[...,0] = 255
    color_mask[...,3] = (mask_arr[...,0] > 0) * 120
    return Image.fromarray(color_mask)

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    img = Image.open(io.BytesIO(await file.read())).convert("RGB")
    enhanced = enhance_image(img)
    cls_idx, conf = model.predict(enhanced)

    # for readability, map to label names (adjust to your classes)
    label_map = {0: "healthy", 1: "treated"}
    label = label_map.get(cls_idx, str(cls_idx))

    # get similar images (as base64 thumbnails)
    similar = get_similar_images(enhanced, topk=3)

    # build mask (simple placeholder)
    mask_img = make_mask(enhanced)

    return {
        "class_label": label,
        "confidence": conf,
        "original_base64": pil_to_base64(enhanced),
        "mask_base64": pil_to_base64(mask_img, fmt='PNG'),
        "similar_images": similar
    }
