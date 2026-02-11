import scipy.io as sp # for reading MatLab binary files
import pandas as pd
import numpy as np
import sys

def centroid_dataframe(fname):
    centroids = sp.loadmat(fname)

    cur_cam = centroids['cur_cam'][0]
    data_files = centroids['data_files'] # shape (360,1)
    # Most of the data stored here:
    centroid = centroids['centroid'][0] # of shape (360,): one for each frame for the hour
    centroid_count = centroids['centroid_count'][0]

    df = pd.DataFrame()

    # Now split the 'centroid' sub-arrays and create their own columns in the DataFrame
    names = ['frame','x','y','area','major_axis_len','minor_axis_len','orientation','diameter','radii','total_DN']
    # Add names to df
    for name in names:
        df[name] = []
        df[name] = df[name].astype(object) # set to objects to allow input of arrays as elements
        
    for l in centroid: # loop through 360 frames
        for i, name in zip(l, names): # loop through each data entry
            # Assign the dataframe index to appropriate row:
            if name == 'frame':
                idx = i[0,0] - 1 # frame number starts at 1
            else: # idx has been assigned: add data to appropriate column
                df.at[idx, name] = i
    
    df['data_file'] = [data_files[i][0] for i in range(len(data_files))]
    df['centroid_count'] = centroid_count[0]
    # Remove the 'frame' column
    df = df.drop(columns=['frame'])

    return df

