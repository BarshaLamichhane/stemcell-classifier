
"""Run the backend server using:

    python3 src/backend/backend_blood_cell_classification.py --serve serve 
    or directly do using uvicorn:
    uvicorn src/backend.backend_blood_cell_classification:app --reload
For training the model:
    python3 src/backend/backend_blood_cell_classification.py --train train
For testing the model:
    python3 src/backend/backend_blood_cell_classification.py --test test
For predicting using the model:
    python3 src/backend/backend_blood_cell_classification.py --predict predict
    This project is for Dopple SA and is developed by Barsha Lamichhane.
"""
from matplotlib.dates import MO
import numpy as np
import pandas as pd
import sys
import os
import csv
import time
import json

##LIBRARIES

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
import kaggle




IMAGE_WIDTH = 64
IMAGE_HEIGHT = 64
IMAGE_SIZE = (IMAGE_WIDTH, IMAGE_HEIGHT)
MODEL_DIRECTORY = "model/blood_cell_classification"
MODEL_NAME = "blood_cell_model.pth"
MODEL_PATH = os.path.join(MODEL_DIRECTORY, MODEL_NAME)
MODEL_METRICS_DIRECTORY = "metrics/blood_cell_classification"
MODEL_METRICS_NAME = "training_blood_cell_log.csv"
MODEL_METRICS_PATH = os.path.join(MODEL_METRICS_DIRECTORY, MODEL_METRICS_NAME)
TEST_FOLDER_NAME = "TEST_SIMPLE"
TEST_DATA_PATH = os.path.join("data/blood-cells/dataset2-master/dataset2-master/images", TEST_FOLDER_NAME)

##DATASET
# Download dataset from Kaggle
# !kaggle datasets download paultimothymooney/blood-cells -p ../input/blood-cells/
def download():
    if( not os.path.exists("data/blood-cells")):
        os.makedirs("data/blood-cells", exist_ok=True)
        ##kaggle.api.authenticate()
        print("Downloading blood-cell dataset from https://www.kaggle.com/datasets/paultimothymooney/blood-cells/data")
        kaggle.api.dataset_download_files("paultimothymooney/blood-cells", path="data/blood-cells", unzip=True)
        print("Dataset downloaded and extracted to:", "data/blood-cells")
    else:
        print("Dataset already exists.")

def create_train_path():
    train_path = 'data/blood-cells/dataset2-master/dataset2-master/images/TRAIN'
    return train_path

def create_test_path():
    test_path = 'data/blood-cells/dataset2-master/dataset2-master/images/TEST'
    return test_path

def create_data_transforms():
    data_transforms = transforms.Compose([
        transforms.Resize(size=IMAGE_SIZE),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    return data_transforms

#creating training  or testing dataset
def create_datasets(train_or_test_path, data_transforms):
    dataset = torchvision.datasets.ImageFolder(root=train_or_test_path, transform=data_transforms)
    return dataset

#Create dataloaders to load the data in batches
def create_dataloaders(dataset, batch_size, to_shuffle):
    train_or_test_dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=to_shuffle)
    return train_or_test_dataloader

## Defining the model
class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 8, 3, padding=1)
        self.pool1 = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(8, 16, 3, padding=1)
        self.pool2 = nn.MaxPool2d(2, 2)
        self.conv3 = nn.Conv2d(16, 32, 3, padding=1)
        self.pool3 = nn.MaxPool2d(2, 2)
        self.conv4 = nn.Conv2d(32, 64, 3, padding=1)
        self.pool4 = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 4 * 4, 256)
        self.fc2 = nn.Linear(256, 4) # 4 classes: EOSINOPHIL, LYMPHOCYTE, MONOCYTE, NEUTROPHIL

    def forward(self, x):
        x = self.pool1(F.relu(self.conv1(x)))
        x = self.pool2(F.relu(self.conv2(x)))
        x = self.pool3(F.relu(self.conv3(x)))
        x = self.pool4(F.relu(self.conv4(x)))
        x = x.view(-1, 64 * 4 * 4)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Main function to run the training process
def train_model(model, train_dataset, test_dataset, num_epochs, batch_size):
    print("Starting training...")
    logger = CSVLogger(MODEL_METRICS_PATH)

     # Get the list of label names
    label_names = test_dataset.classes
    label_names_train = train_dataset.classes

    print("Training label names:", label_names_train)

    # Get the dataloaders to load the data in batches
    train_dataloader = create_dataloaders(train_dataset, batch_size=batch_size, to_shuffle=True)

    # Check if GPU is available
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print(f"Using device: {device}")
   
    # Define loss function and optimizer
    loss_function = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    losses = []

    # Training loop
    for epoch in range(num_epochs):  # Number of epochs
        model.train()
        for input_images, labels in train_dataloader:
            input_images = input_images.to(device)
            labels = labels.to(device)
            logits = model(input_images)
            loss = loss_function(logits, labels)

            # Zero the gradients
            optimizer.zero_grad()

            loss.backward()
            optimizer.step()

        #Append loss for each epoch to the losses list
        losses.append(loss.item())
        print("print loss:", loss.item())
        #os.makedirs(MODEL_METRICS_DIRECTORY, exist_ok=True)
        #save_logged_metrics(self,loss.item(), MODEL_METRICS_PATH)
        logger.log(epoch+1, f"{loss.item():.4f}")
        print(f"Training metrics saved to {MODEL_METRICS_PATH}")
        # Print loss for each epoch
        print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}")

    print("Training complete.")
    os.makedirs(MODEL_DIRECTORY, exist_ok=True)
    save_trained_model(model, MODEL_PATH)
    print(f"Trained model saved to {MODEL_PATH}")


    #return losses
class CSVLogger:
    def __init__(self, filepath):
        self.filepath = filepath
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Create file with header if it doesn't exist
        if not os.path.exists(filepath):
            with open(filepath, mode="w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["epoch", "train_loss"])

    def log(self, epoch, train_loss):
        with open(self.filepath, mode="a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([epoch, train_loss])


def save_logged_metrics(self, metrics, path):
    print("metrics to save:", metrics)
    ##df = pd.DataFrame(metrics, columns=['loss'])
    ##df.to_csv(path, index=False)
    self.log(path, metrics, on_epoch=True, prog_bar=True, logger=True)
    print(f"Metrics saved to {path}")

def save_trained_model(model, path):
    torch.save(model.state_dict(), path)
    print(f"Model saved to {path}")

def plot_losses(losses):

    import matplotlib.pyplot as plt

    plt.plot(losses)
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training Loss over Epochs')
    plt.show()

def test_and_evaluate_model(model, test_dataloader, device):

    from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

    # Set model to evaluation mode
    model.eval()

    # Initialize lists to store true labels and predicted labels
    true_labels = []
    pred_probs = []  # store predicted probabilities instead of labels

    # Iterate through the test data
    with torch.no_grad():
        for inputs, labels in test_dataloader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            logits = model(inputs)
            probs = torch.softmax(logits, dim=1)  # calculate probabilities

            # Add true labels and predicted probabilities to lists
            true_labels.extend(labels.tolist())
            pred_probs.extend(probs.tolist())

    # Convert lists to numpy arrays
    true_labels = np.array(true_labels)
    pred_probs = np.array(pred_probs)

    # Calculate accuracy, F1 score, and AUC score
    acc = accuracy_score(true_labels, np.argmax(pred_probs, axis=1))
    f1 = f1_score(true_labels, np.argmax(pred_probs, axis=1), average='macro')
    auc = roc_auc_score(true_labels, pred_probs, multi_class='ovo')

    # Print results
    print(f'Test accuracy: {acc:.4f}')
    print(f'Test F1 score: {f1:.4f}')
    print(f'Test AUC score: {auc:.4f}')

def predict_image(model, test_image_path, device, label_names):
    from PIL import Image
    # Load the image and preprocess it
    print("Predicting for image:", test_image_path)
    image = Image.open(test_image_path)
    #image.show()
    
    preprocess = create_data_transforms()
    image = preprocess(image)

    # Convert the image to a PyTorch tensor and send it to the device
    image = image.unsqueeze(0).to(device)

    # Make the prediction
    with torch.no_grad():
        logits = model(image)
        probs = torch.softmax(logits, dim=1)
        pred_label = torch.argmax(probs, dim=1)

    # Print the prediction
    print(f'Predicted label: {pred_label.item()}')

    # Map the predicted label to the corresponding class name
    predicted_class_name = label_names[pred_label.item()]

    # Print the predicted class name
    print(f'Predicted class name: {predicted_class_name}')

    return {"predicted_class_name": predicted_class_name,
            "predicted_label": pred_label.item(),
            "confidence_scores": float(probs[0][pred_label.item()])}

def arg_param():
    import argparse 

    parser = argparse.ArgumentParser(description="Script description here") 
    parser.add_argument("--train", help="Trains the model", type=str) 
    parser.add_argument("--test", help="Tests the model", type=str)
    parser.add_argument("--predict", help="Makes predictions", type=str)
    parser.add_argument("--serve", help="Serves the model", type=str)
    args = parser.parse_args() 
    return args

def main():
    import time
    start_time = time.time()
    download()
    # Get the datasets
    train_path = create_train_path()
    test_path = create_test_path()
    data_transforms = create_data_transforms()
    train_dataset = create_datasets(train_path, data_transforms)
    test_dataset = create_datasets(test_path, data_transforms)
    test_dataloader = create_dataloaders(test_dataset, batch_size=64, to_shuffle=False)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    num_epochs=18
    label_names = test_dataset.classes
    print("Label names:", label_names)

    if(len(sys.argv)>1):
        args = arg_param()
        if(args.train):
            if( not os.path.exists(MODEL_PATH)):
                print("Training the model...")
                model = CNN().to(device)
                train_model(model,train_dataset, test_dataset, num_epochs, batch_size=64)
            else:
                print("Model already trained and saved at model/blood_cell_classification/blood_cell_model.pth")
            end_time = time.time()
            print(f"Execution time: {end_time - start_time:.2f} seconds")  
        elif(args.test):
            if( not os.path.exists(MODEL_PATH)):
                print("Model not trained yet! Please train the model first using --train argument.")
                return
            print("Testing the model...")
            model = CNN()
            model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
            model = model.to(device)
            print("Loaded trained model from model/blood_cell_classification/blood_cell_model.pth and testing now...")
            test_and_evaluate_model(model, test_dataloader, device)
        elif(args.predict):
            if( not os.path.exists(MODEL_PATH)):
                print("Model not trained yet! Please train the model first using --train argument.")
                return
            print("Predicting...")
            model = CNN()
            model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
            model = model.to(device)
            print("Loaded trained model from model/blood_cell_classification/blood_cell_model.pth and predicting now...")
            #print(os.listdir("data/blood-cells/dataset2-master/dataset2-master/images/TEST/MONOCYTE")[:2])
            for test_image_path in os.listdir("data/blood-cells/dataset2-master/dataset2-master/images/TEST/MONOCYTE")[:2]:
                print("Test image path:", test_image_path)
                test_image_path = os.path.join("data/blood-cells/dataset2-master/dataset2-master/images/TEST/MONOCYTE", test_image_path)
                predict_image(model, test_image_path, device, label_names)
        elif(args.serve):
            print("Starting FastAPI server...")
            import uvicorn
            uvicorn.run(app, host="0.0.0.0", port=8000)

        else:
            print("Invalid argument! Use --train, --test, or --predict.")
        return
    else:
        print("No arguments provided! Use --train, --test, or --predict.")
        return
    

from pydantic import BaseModel
from typing import List
from fastapi.staticfiles import StaticFiles



class FilterRequest(BaseModel):
    cell_type: str
    threshold: float

from fastapi import FastAPI
from fastapi import FastAPI, UploadFile, File
BASE_IMAGES_PATH = "data/blood-cells/dataset2-master/dataset2-master/images"
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.mount("/images", StaticFiles(directory=BASE_IMAGES_PATH), name="images")
#app.mount("/images", StaticFiles(directory=TEST_DATA_PATH), name="images")



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/predict")
async def predict(file: UploadFile = ...):
    test_temp_path = None
    #if( not os.path.exists("backend_v2_trained_model/model.pth")):
    #test_temp_path = os.path.join("data/blood-cells/dataset2-master/dataset2-master/images/TEST/LYMPHOCYTE", file.filename)
    #test_temp_path = os.path.join("data/blood-cells/dataset2-master/dataset2-master/images/TEST/blood_cell_test/Sample_A", file.filename)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    ##with open(test_temp_path, "wb") as f:
    model = CNN()
    model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    model = model.to(device)
    label_names = ['EOSINOPHIL', 'LYMPHOCYTE', 'MONOCYTE', 'NEUTROPHIL']
    #test_file_names = ['SAMPLE-EOSINOPHIL', 'SAMPLE-LYMPHOCYTE', 'SAMPLE-MONOCYTE', 'SAMPLE-NEUTROPHIL']
    for label in label_names:
        test_temp_path = os.path.join(TEST_DATA_PATH, label, file.filename)
        if os.path.exists(test_temp_path):
            test_temp_path = test_temp_path
            break
    if test_temp_path is None:
        raise FileNotFoundError(
            f"{file.filename} not found in any of {label_names}"
        )
    # Make the prediction
    predicted_result = predict_image(model, test_temp_path, device, label_names)
    return {"predictions": predicted_result}

@app.post("/filter")
async def filter_cells(request: FilterRequest):
    device = "cuda" if torch.cuda.is_available() else "cpu"

    model = CNN()
    model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    model = model.to(device)

    label_names = ['EOSINOPHIL', 'LYMPHOCYTE', 'MONOCYTE', 'NEUTROPHIL']

    selected_type = request.cell_type
    threshold = request.threshold

    results = []

    # 👇 Your LIST A (example: scan TEST folder)
    for label in label_names:
        folder_path = os.path.join(TEST_DATA_PATH, label)

        for file in os.listdir(folder_path):
            img_path = os.path.join(folder_path, file)
            print(f"Processing {img_path}, {img_path}")
            pred = predict_image(model, img_path, device, label_names)
            print("selected type:", selected_type, "threshold:", threshold)
            if (
                pred["predicted_class_name"] == selected_type
                and pred["confidence_scores"] >= threshold
                and pred ["confidence_scores"] < 100
            ):
                results.append({
                    "file": file,
                    "predicted_class": pred["predicted_class_name"],
                    "confidence": pred["confidence_scores"],
                    #"image_url": f"http://localhost:8000/images/TEST_SIMPLE/{label}/{file}"
                    "image_url": f"http://localhost:8000/images/{TEST_FOLDER_NAME}/{label}/{file}"
                })
            
            
    return {
        "selected_type": selected_type,
        "threshold": threshold,
        "matched_files": results[:3]   #for showing only 3 results in the frontend, you can remove this slicing to show all results
    }

from fastapi.responses import StreamingResponse
import csv
import time

@app.get("/metrics/stream")
def stream_metrics():

    def event_stream():
        with open(MODEL_METRICS_PATH, "r") as f:
            reader = csv.DictReader(f)

            loss_history = []

            for row in reader:
                epoch = int(row["epoch"])
                loss = float(row["train_loss"])

                loss_history.append(loss)

                data = {
                    "epoch": epoch,
                    "total_epochs": 18,  # or len(csv)
                    "loss": loss,
                    "loss_history": loss_history,
                    "status": "replaying"
                }

                yield f"data: {json.dumps(data)}\n\n"
                time.sleep(1)  # simulate real-time playback

        # send completed event
        yield f"data: {json.dumps({'status': 'completed'})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
if  __name__ == "__main__":
    main()