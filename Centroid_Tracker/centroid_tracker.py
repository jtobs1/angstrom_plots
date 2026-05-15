import scipy.spatial.kdtree as kdtree
import numpy as np
import matplotlib.pyplot as plt
import json, sys
from open_json import open_json as oj
from pathlib import Path
import scipy.io as sio
from load_mat import load_mat as lm
import posixpath
from core_tracker import track_centriods 
from summarize import summarize
from numpy.polynomial import Polynomial

"""
Star/centroid tracking algorithm that uses K-dimensional
nearest-neighbor object tracking (as opposed to a projective-transform
style star tracker).

User needs to run the I2R centriod generator: `run_angstrom_processing.m`
to create the centroid files. Then, input the centroid directory in 
the centroid_<MMddYYYY>.json file.

NOTE: Because this method does not use a star catalogue to confirm certain
variables, this will have to account for:
    Atmospheric properties:
        - Airmass. (y-location in frame).
    Optical properties:
        - Vignetting.
        - Spherical aberation.
        - "Lensing" effects near the edge (just remove edges?)

Created: Jackson Tobin 05/11/2026
"""

# Open and read the json file
centroid_files = oj('./centroids_04012026.json')

# Cycle through the centroid files
for i in centroid_files:
    print(f"\nPROCESSING: {posixpath.basename(i)}")

    # Read the matlab file
    # Contains a python dictionary of:
    #   frames[x,y,dn,area] (360frames=1hr), n_frames (360=1hr), raw mat file
    mat = lm(i.as_posix())

    # Core star tracking algorithm
    print("Beginning star tracking")
    rows = track_centriods(mat=mat, radius=3, max_gap=10)
    print('Done star tracking!')

    # Summarize the data
    summary = summarize(rows)
    print(summary.keys())

    fig, ax = plt.subplots(figsize=(8,6))
    for n, tid in enumerate(summary.loc[:,'track_id']):

        # Example plot of one star:
        star = rows[rows['track_id'] == tid].sort_values('frame')
        
        if (summary.loc[n,'std_dn'] <= 6000) & (summary.loc[n,'n_frames_present']>300):
            ax.scatter(star['frame'], star['dn'], marker=',', s=2, label=f'ID: {tid}', alpha=0.7)
            # add a linear fit:
            # P = Polynomial.fit(star['frame'], star['dn'], deg=1)
            # intercept, slope = P.convert().coef
            # ax.plot(star['frame'], star['frame']*slope+intercept)

    ax.set_title(f'Centroid ID {tid}: Digital Number')
    ax.set_xlabel('Frame Number')
    ax.set_ylim(0, 5e4)
    ax.set_ylabel('DN')
    ax.grid(True, color='grey', alpha=0.3, linestyle='--')
    plt.savefig('./testing_dnstar.png')
    plt.close()
    sys.exit()    


    