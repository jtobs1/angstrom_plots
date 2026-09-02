import numpy as np
import requests
import matplotlib.pyplot as plt
import pandas as pd
import datetime, sys


def tau_rs(wavelength, pressure):
    """
    Inputs:
        wavelength: in µm.
        pressure: in kPa
    Output:
        Rayleigh Scattering optical depth.
    """
    p0 = 1013.25 # [kPa]
    pr = pressure/p0
    tau = 0.0021520*pr * ((1.0455996-341.29061*wavelength**(-2)-0.90230850*wavelength**2) / 
                        (1+0.002705988*wavelength**(-2)-85.968563*wavelength**2))
    return tau

def get_pressure(lat, lon, stime, etime):
    """
    Queries the Open-Meteo API for relevant cloud-cover data;
        https://open-meteo.com/ 
    Preferably, you'll input an hour range to prevent query overloading (10,000 / day)
    Returns a DataFrame because why not...
    """
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude":lat,
        'longitude':lon,
        'start_date':stime,
        'end_date':etime,
        'hourly':['surface_pressure'],
        # 'timezone':'UTC',
    }

    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()['hourly']
    df = pd.DataFrame(data)
    df['time'] = pd.to_datetime(df['time'])
    df.set_index('time')
    return df

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
        print(f'Opening:            {f.name}')
        wave = []
        tran = []
        for line in f:
            data = line.split(' ')
            wave.append(float(data[0]))
            tran.append(float(data[1].replace('\n','')))
    wave = np.array(wave)
    tran = np.array(tran)
    return wave, tran


if __name__=='__main__':
    # Default pressure in hPa
    pressure = int(input('Pressure [hPa]: '))
    band = int(input('Band number: '))
    # Get the range of airmasses
    # Could also use VZA instead...
    airmasses = np.linspace(start=2.0, stop=4.0, num=20)
    print('Input Variable --------------------')
    print(f"local pressure:     {pressure}hPa")
    print(f'angstrom band:      {band}nm')
    print('-----------------------------------')

    # -----------------------------
    # Preallocate arrays
    # -----------------------------
    # wavelengths in µm
    wavelengths = np.arange(350, 1101, step=1)*10**(-3)

    # MidOpt wavelengths and SRF at 10nm incriments
    wave_midopt, tran_midopt = plot_midopt_bn(band)
    # interpolate to 1nm incriments
    x_og = np.arange(len(wave_midopt))
    x_new = np.linspace(0, len(wave_midopt)-1, num=(1101-350))
    wave_interp = np.flip(np.interp(x_new, x_og, wave_midopt))*10**(-3) # should match "wavelengths"
    tran_interp = np.flip(np.interp(x_new, x_og, tran_midopt) / 100) # convert to fraction

    # get the RS ODs at 1nm incriments:
    rs_od = [tau_rs(w, pressure) for w in wavelengths]
    
    print('')
    print(f"iterable wavelengths:  {wavelengths[0:3]}")
    print(f'interp. wavelengths:   {wave_interp[0:3]}')
    print(f'inter. trans.:         {tran_interp[0:3]}')
    print('')

    # -----------------------------
    # Loop through the airmasses
    # -----------------------------
    tau_eff = []
    # Surrounding wavelengths
    wave_cond = np.where((wavelengths<(band+100)/1000) & 
                            (wavelengths>(band-100)/1000))
    wave_range = wavelengths[wave_cond]
    print(f"Looping from {wave_range.min():.3f}µm to {wave_range.max():.3f}µm")
    for m in airmasses:
        # Loop through the wavelengths
        numerator = []
        denominator = []
        for n, w in enumerate(wavelengths):
            numerator.append(tran_interp[n] * np.exp(-rs_od[n]*m))
            denominator.append(tran_interp[n])
        tau_eff.append(-(1 / m) * np.log(sum(numerator) /
                                          sum(denominator)))

    print('')
    print(f'Average RS OD with MidOpt: {np.mean(tau_eff):.5f}')
    print(f'Central RS OD:             {tau_rs(band/1000, pressure):.5f}')
    
    # ---------------------------
    # Plot the outputs
    # ---------------------------
    # RS OD vs Airmass
    # fig, ax = plt.subplots()
    # ax.plot(airmasses, tau_eff, marker='o', color='red')
    # ax.set_xlabel("Airmass [sec(VZA)]")
    # ax.set_ylabel("RS OD")
    # ax.set_title(f'MidOpt BN{band} SRF-corrected Rayleigh OD')
    # ax.grid(linestyle='--', alpha=0.3)
    # plt.tight_layout()
    # plt.savefig(f'./od_midopt_rs_{pressure}hPa_{band}nm.png',dpi=150)
    # plt.close()

    fig, ax = plt.subplots()
    ax.plot(wavelengths, rs_od/np.amax(rs_od), label='RS OD', color='red', linestyle='--')
    ax.plot(wavelengths, tran_interp/np.amax(tran_interp), label='MidOpt Transmittion', color='black')
    ax.axvline(band/1000, color='green', linestyle='-.', label=f'Band {band}nm')
    ax.set_xlabel('Wavelength [µm]')
    ax.set_ylabel('Normalized Values')
    ax.set_title(f'MidOpt BN{band} Transmittion & Rayleigh Optical Depth at {pressure}hPa\nConvolved OD: {np.mean(tau_eff):.5f}; Central OD: {tau_rs(band/1000, pressure):.5f}')
    ax.legend()
    ax.grid(linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'./midopt_rs_{pressure}hPa_{band}nm.png', dpi=1500)
    plt.close()

    # fig, ax = plt.subplots()
    # ax.plot(wavelengths, tran_interp, color='red')
    # ax.set_xlabel("Wavelength [µm]")
    # ax.set_ylabel("Transmittion")
    # ax.set_title(f'MidOpt BN{band} Transmittion')
    # ax.grid(linestyle='--', alpha=0.3)
    # plt.tight_layout()
    # plt.savefig(f'./midopt_trans_{pressure}hPa_{band}nm.png',dpi=150)
    # plt.close()