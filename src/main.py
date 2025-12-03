from src import train, predict

def main():
    print("1. Train model")
    print("2. Predict image")
    choice = input("Enter choice: ")

    if choice == "1":
        train.train()
    elif choice == "2":
        img = input("Enter image path: ")
        predict.predict(img)
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()
