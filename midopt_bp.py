import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

"""
This script attempts to model the MidOpt BN450,470,490,520 filters.
A basic model simplifies the SRF to a box, where the FWHM is the width.
The full model incorperates the midopt_bnXXX.txt files, which contain
the transmition (%) as a function of wavelength (nm; intervals of 10nm)

Created: Jackson Tobin 09/01/2026
"""

def plot_midopt_bn(wavelength):
    """wavelength: in [nm]"""
    if isinstance(wavelength, str):
        pass
    elif isinstance(wavelength, float):
        wavelength = str(np.round(wavelength,0))
    elif isinstance(wavelength, int):
        wavelength = str(wavelength)
    # Read the txt file
    with open(f'midopt_bn{wavelength}.txt','r') as f:
        wave = []
        tran = []
        for line in f:
            data = line.split(' ')
            wave.append(float(data[0]))
            tran.append(float(data[1].replace('\n','')))
    wave = np.array(wave)
    tran = np.array(tran)

    # Plot the data
    fig, ax = plt.subplots(figsize=(8,4))
    ax.plot(wave, tran, color='red')
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_xlabel('Wavelength [nm]')
    ax.set_ylabel('Transmittion [%]')
    ax.set_xlim(350, 1100)
    ax.set_ylim(0, 100)
    ax.set_title(f'MidOpt BN{wavelength}nm SRF')
    plt.tight_layout()
    plt.savefig(f'./midopt_bn{wavelength}.png',dpi=150)
    plt.close()

plot_midopt_bn(450)
plot_midopt_bn(470)
plot_midopt_bn(490)
plot_midopt_bn(520)
        