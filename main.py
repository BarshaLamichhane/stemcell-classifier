from src.backend import dataset_downloader



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
    dataset_downloader.download()
if __name__ == "__main__":
    main()
