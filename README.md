# Stem Cell Image Classification (CNN + PyTorch)

This project basically trains a Convolutional Neural Network (CNN) on a Kaggle dataset of cancer stem-cell images for binary image classification.

## Features
- Downloads Kaggle dataset automatically
- Simple CNN architecture
- Training + validation loop
- Prediction script
- Fully reproducible environment using `requirements.txt`
-DATASET_NAME = "daelamyyusuf/cancer-stem-cell-image-clasification-datasets"

## Clone the project
```bash 
git clone https://github.com/BarshaLamichhane/stemcell-classifier.git
```
## Go to the cloned repository**
```bash cd path/to/stemcell-classifier```
**Create virtual environment**
`python3 -m venv venv`
**Activate virtual environment**
`source venv/bin/activate` => mac or linux
`venv\bin\activate` => windows
**Install all the libararies**
`pip install -r requirements.txt`
## Download kaggle Dataset (from cli)
open seperate terminal, Terminal 2 out of virtual environment and 
### install kaggle
`pip install kaggle`

### set up kaggle API
- go to Kaggle => Account Settings => API => create Legacy API credentials
It will download `kaggle.json` file automatically in download folder

###  save `kaggle.json` API token inside:**
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

### Download datasets
Go to the first terminal, terminal 1, where virtual environment is activated.
run the script 
```bash
python dataset_downloader.py

```
Which is inside `src/dataset_downloader.py`

