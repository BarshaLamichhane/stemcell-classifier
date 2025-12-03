import os
import kaggle
from config import ORGANOID_MINI


def download():
    os.makedirs(ORGANOID_MINI["TARGET_DIR"], exist_ok=True)
    print("📥 Downloading dataset from Kaggle...")
    kaggle.api.dataset_download_files(ORGANOID_MINI["DATASET_NAME"], path=ORGANOID_MINI["DATA_TARGET_DIR"], unzip=True)
    print("✅ Dataset downloaded and extracted to:", ORGANOID_MINI["DATA_TARGET_DIR"])

if __name__ == "__main__":
    download()
