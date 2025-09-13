import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os
import sys 
import glob
import subprocess
import startrack_lib

# predir = '520nm_08212025/'
predir = '450nm_09112025/'
# fdir = '/Users/jacksontobin/Local_Documents/Angstrom_data/08212025/'
# f1 = '/Users/jacksontobin/Local_Documents/Angstrom_data/08212025/520nm_08212025/Band_520nm_BFS-PGE-16S7M_SN22011988_Frame00001_UTC022211.tiff'
fdir = '/Users/jacksontobin/Local_Documents/Angstrom_data/09112025/'
# f1 = '/Users/jacksontobin/Local_Documents/Angstrom_data/09112025/520nm_08212025/Band_520nm_BFS-PGE-16S7M_SN22011988_Frame00001_UTC022211.tiff'

load_images = False
if load_images:
    for num, i in enumerate(os.listdir(fdir+predir)):
        image_file = fdir + predir + i
        try:
            # Image.open will run into errors with the .tiff files sometimes.
            # just exclude those images...
            image = Image.open(image_file)
            image_array = np.array(image)
            np.save(f'./450nm/file_{num}', image_array, allow_pickle=True)
        except:
            print("Error")
            # break

# Creates a loop of the images
# image_dir = '/Users/jacksontobin/Local_Documents/coding_shenanigans/520nm/'
image_dir = '/Users/jacksontobin/Local_Documents/coding_shenanigans/450nm/'
# images = sorted(glob.glob(os.path.join(image_dir, '*png')))
# subprocess.run(
#     ['convert','-delay','20','-loop','180',*images,os.path.join(image_dir,'loop.gif')]
# )

star_dict, star_loc_dict = startrack_lib.object_identifier(image_dir, background_value=2e2)

startrack_lib.langley_plot(star_dict=star_dict)