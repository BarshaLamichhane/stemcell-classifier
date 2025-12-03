import os
import kaggle
from .config import DATASET_NAME, DATA_TARGET_DIR


def download():
    os.makedirs(TARGET_DIR, exist_ok=True)
    print("📥 Downloading dataset from Kaggle...")
    kaggle.api.dataset_download_files(DATASET_NAME, path=TARGET_DIR, unzip=True)
    print("✅ Dataset downloaded and extracted to:", TARGET_DIR)

if __name__ == "__main__":
    download()
