import numpy as np
from PIL import Image
import os
import matplotlib.pyplot as plt
import glob
import warnings
import subprocess

class StarData_Reader(object):
    def __init__(self, fdir, band):
        self.fdir = fdir
        self.band = band

    def read_data(fdir, band):
        """
        fdir: where the original files are stored.
        band: (string) band number in nm; 450, 470, 490, 520
        """
        try:
            os.mkdir(f'./{band}_files/')
        except:
            print("Path already exists.")

        for num, i in enumerate(os.listdir(fdir)):
            image_file = fdir + 1
            try:
                image = Image.open(image_file)
                image_arr = np.array(image)
                np.save(f'./{band}/{band}_{num}', image_arr, allow_pickle=True)
            except:
               print(f"Error loading image {num}.")

    def make_plots(band, vmin=2e2, vmax=8e2, cmap='cubehelix'):
        """
        band: (string) band number in nm; 450, 470, 490, 520
        """
        try:
            os.mkdir(f'./{band}_images/')
        except:
            print("Path already exists.")

        for num, i in enumerate(os.listdir(f'./{band}_files/')):
            image = np.load(i)
            plt.imshow(image, vmin=vmin, vmax=vmax, cmap=cmap)
            plt.title(f'{band}: Image number {num}')
            plt.savefig(f'./{band}/im_{num}.png', format='png', dpi=150)
            plt.close()

    def make_loop(band):
        """
        Creates a .gif of the images created by make_plots().
        """
        images = sorted(glob.glob(os.path.join(f'./{band}_images/')))
        subprocess.run(
            ['convert','-delay','20','-loop','180',*images,os.path.join(f'./{band}_images/',f'loop_{band}.gif')]
        )