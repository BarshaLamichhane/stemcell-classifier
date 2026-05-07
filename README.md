# Blood  Cell Image Classification (Python, Pytorch, CNN, Angualr )

This project is a small end to end demo for blood cell image classification using Python and Pytorch. It uses simple angular based web interface which allows user to uplaod a blood cell image and view the predicted class. 
The goal of the project is to demonstrate how a machine learning model can be integarted into a usable application, even for non machine learning user rather than on developing a novel model architecture.

## Features
- Downloads Kaggle dataset automatically (`paultimothymooney/blood-cells/data`)
- Trains a Convolutional Neural Network (CNN) using PyTorch
- Saves the trained model for future inference and reuse
- Supports resuming training from a saved model checkpoint
- Evaluates the trained model on a test dataset
- Fully reproducible environment using `requirements.txt`
- Includes a simple Angular-based web interface to:
    - upload a single blood cell image
    - Display the predicted blood cell class

## Instructions to run the project

### Clone the project
```bash 
git clone https://github.com/BarshaLamichhane/stemcell-classifier.git
```
### Go to the cloned repository
```bash 
cd path/to/stemcell-classifier
```
### Create virtual environment

```bash 
python3 -m venv venv
```
### Activate virtual environment
***For mac/linux run***
```bash
source venv/bin/activate 
```
***For windows run***

```bash
venv\bin\activate 
```
**Install all the libararies**
```bash
pip install -r requirements.txt
```
### Download kaggle Dataset (from cli)
open seperate terminal, Terminal 2 out of virtual environment and 
**install kaggle**
`pip install kaggle`

**set up kaggle API**
- go to Kaggle => Account Settings => API => create Legacy API credentials
It will download `kaggle.json` file automatically in download folder

**save `kaggle.json` API token inside:**
Windows: C:\Users\<you>\.kaggle\kaggle.json
Mac/Linux: ~/.kaggle/kaggle.json

```bash 
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

if `~/.kaggle/` you do not find kaggle folder while doing `mv ~/Downloads/kaggle.json ~/.kaggle/` then create kaggle folder first by 
```bash
mkdir -p ~/.kaggle
``` 

### Run
 
```bash
python src/backend/backend_blood_cell_classification.py --train train
```
This will train and save the model inside `model/blood_cell_classification` as `blood_cell_model.pth` 

```bash
python src/backend/backend_blood_cell_classification.py --resume resume
```
This will resume training of the model `blood_cell_model.pth` from `model/blood_cell_classification` saved initially.

```bash
python src/backend/backend_blood_cell_classification.py --test test
```
This will test the model. If you want to predict the model in backend only then run:

```bash
python src/backend/backend_blood_cell_classification.py --predict predict
```
This will predict blood cell image. 


### Run the FastAPI backend for prediction before using frontend/UI
```bash
uvicorn src/backend.backend_blood_cell_classification__Corontis:app --reload
```
or 
```bash
python3 src/backend/backend_blood_cell_classification_Corontis.py --serve serve 
```
```bash
uvicorn src/backend.backend_blood_cell_classification:app --reload
```
or 
```bash
python3 src/backend/backend_blood_cell_classification_Corontis.py --serve serve 
```
You can open for testing

http://localhost:8000/docs

You will see:

/predict

### Run frontend
## open another new terminal
**1. go inside the project directory**
**2. go inside src/frontend/organoid-ui/src and run**
```bash
ng serve
```
and open  http://localhost:4200/
***NOTE: 4200 is a port but your port number can be anything***

## Limitations
- Model trained on a limited dataset
- web interface doesn't support multiple prediction at a time. The UI is intended as a functional demo, not a production-ready UI.
- Not optimized for a real-world deployment

## References & Acknowledgements
This project was inspired from this notebook: 
https://www.kaggle.com/code/drindeng/blood-cell-image-classification-by-pytorch#Training

The CNN architecture and training pipeline were adapted and refactored into modular Python and PyTorch functions. The project was extended with a simple Angular based frontend to demonstrate prediction of the blood cell.

### Other learning references:
***PyTorch Model Save And Load***
1. https://machinelearningmastery.com/save-and-load-your-pytorch-models/
2. https://www.geeksforgeeks.org/deep-learning/extracting-loss-and-accuracy-from-pytorch-lightning-logger/
3. https://www.geeksforgeeks.org/deep-learning/monitoring-model-training-in-pytorch-with-callbacks-and-logging/
4. https://www.geeksforgeeks.org/python/creating-first-rest-api-with-fastapi/
5. https://machinelearningmastery.com/save-and-load-your-pytorch-models/

***Blood Cell Image Classification by PyTorch*** 
1. https://www.kaggle.com/code/drindeng/blood-cell-image-classification-by-pytorch#Libraries
2. https://www.kaggle.com/datasets/paultimothymooney/blood-cells
3. https://www.kaggle.com/datasets/paultimothymooney/blood-cells/data

***Others***
1. https://www.kaggle.com/code/tirendazacademy/cats-dogs-classification-with-pytorch/notebook
2. https://www.nature.com/articles/s41698-025-01082-6#:~:text=A%20major%20challenge%20in%20effective,approach%20to%20predict%20clinical%20outcome.



## Author
Barsha Lamichhane
barshalamichhane.bl@gmail.com

## License
This project is solely intended for educational and demonstration purpose only.