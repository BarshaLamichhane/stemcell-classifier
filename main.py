from src.backend import dataset_downloader
from src.backend import preprocessing
from src import config
import os



""""def main():
    print("1. Train model")
    print("2. Predict image")
    choice = input("Enter choice: ")

    if choice == "1":
        train.train()
    elif choice == "2":
        img = input("Enter image path: ")
        predict.predict(img)
    else:
        print("Invalid choice!")"""

def main():
    """dataset_downloader.download()"""
    
    """preprocessing.read_image_pil(config.ORGANOID_MINI["TRAIN_DIR"])"""
    preprocessing.read_image_pil("data/Training/After/3402-input.png")
    ##print(os.listdir("data/Training/After/"))
    preprocessing.simple_enhance(preprocessing.read_image_pil("data/Training/After/3402-input.png"))

if __name__ == "__main__":
    main()
