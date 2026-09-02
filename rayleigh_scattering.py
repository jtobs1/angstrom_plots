import numpy as np
import requests
import pandas as pd
import datetime
"""
Computes the Rayleigh Scattering optical depth
using equation (30) from Bodhaine et al. 1999.
This method is correct to within 0.05% at 45ºN, 
and depends on:
    1) wavelength,
    2) local pressure.

You can retrieve the local pressure using a nearby METAR.
    
Created: Jackson Tobin 08/30/2026
"""

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

def tau_rs_metar(stime, etime):
    """
    Inputs:
        - stime & etime: datetime format.
    Returns:
        - tau: list of RS OD at 450,470,490,520nm

    To impliment:
        Integrate over a finite bandwidth. 
    """
    # Angstrom bands
    waves = [0.45, 0.47, 0.49, 0.52] # [µm]
    # Angstrom bandwidths (approximate)
    bw = [0.045, 0.045, 0.045, 0.045] # [µm]
    
    # Break up the stime, etime objects
    day = datetime.datetime.strftime(stime, '%Y-%m-%d')

    # Star photometer location
    lat, lon = 40.58776075373724, -105.14760680964913
    # Retrieve the pressure at "time"
    pressure = get_pressure(lat, lon, day, day)
    p_time = pressure[(pressure['time'] < etime) & (pressure['time'] > stime)]
    p_av = np.mean(p_time['surface_pressure'])
    p0 = 1013.25 # [kPa]
    pr = p_av/p0
    # Compute the rayleigh optical depth
    tau = []
    for i in waves:
        tau.append(0.0021520*pr * ((1.0455996-341.29061*i**(-2)-0.90230850*i**2) / 
                        (1+0.002705988*i**(-2)-85.968563*i**2)))
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

if __name__=="__main__":
    stime = datetime.datetime(year=2026,month=8,day=23,
                              hour=5,minute=30,second=0)
    etime = datetime.datetime(year=2026,month=8,day=23,
                              hour=6,minute=30,second=0)

    ans = tau_rs_metar(stime, etime)
    print(ans)
    # Get tau between certain times
