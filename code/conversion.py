import os
import h5py
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from skimage import transform
from skimage import exposure
from skimage import io


READ_PATH = Path(__file__).parent 
WRITE_PATH = Path(__file__).parent

def convert_file(read_path, write_path, csv_string):
    df = pd.read_csv(str(read_path) + '/' + csv_string)
    print(df.head())
    data_array = []
    labels = []
    for index, row in df.iterrows():
        filepath = row["Path"]
        file = os.path.join(read_path, filepath)
        x1 = row["Roi.X1"]
        x2 = row["Roi.X2"]
        y1 = row["Roi.Y1"]
        y2 = row["Roi.Y2"]
        curr_image = io.imread(file)
        curr_image = curr_image[y1:(y2 + 1), x1:(x2 + 1), :]
        curr_image = transform.resize(curr_image, (32, 32))
        curr_image = exposure.equalize_adapthist(curr_image, clip_limit=0.1)
        label = row["ClassId"]
        labels.append(label)
        data_array.append(curr_image)
        if index % 1000 == 0:
            print("[INFO] processed {} total images".format(index))
    

    hf = h5py.File(str(write_path), 'w')
    hf.create_dataset('Data', data=data_array)
    hf.create_dataset('Labels', data=labels)
    hf.close()



WRITE_PATH = os.path.join(WRITE_PATH, "Train.h5")
convert_file(READ_PATH, WRITE_PATH, 'Train.csv')
# WRITE_PATH = os.path.join(WRITE_PATH, "Test.h5")
# convert_file(READ_PATH, WRITE_PATH, "Test.csv")
