import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import weighted_average

def langley_plot(dataframe):
    els  = dataframe.applymap(lambda x: x[3] if isinstance(x, tuple) else np.nan)
    area = dataframe.applymap(lambda x: x[2] if isinstance(x, tuple) else np.nan)
    # mags = dataframe.applymap(lambda x: x[2] if isinstance(x, tuple) else np.nan)
    dns  = dataframe.applymap(lambda x: x[1] if isinstance(x, tuple) else np.nan)
    
    # Get camera exposure time
    texp = 10000.0 # ms
    texp = texp / 1000

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 6))

    n = len(dataframe.columns)
    colors = plt.cm.jet(np.linspace(0, 1, n))

    # Loop through each star and plot
    slope_arr = []
    weight_arr = []

    for num, col in enumerate(dataframe.columns):
        star_dn = dns[col]
        star_ar = area[col]
        star_el = els[col]

        # Normalized the DNs
        star_dn_normalized = star_dn 
        # star_dn_normalized = star_dn / star_ar

        # x-axis is sec(zenith): zenith = 90 - elevation
        # y-axis is ln(DN/t_exp)
        zenith = np.deg2rad(90 - star_el) # NOTE Check this range!!!!
        x = 1 / np.cos( zenith )
        y = np.log( star_dn_normalized / texp )
        
        print(np.rad2deg(zenith), zenith)

        # Add a best-fit line
        m, b = np.polyfit( x[ ~dns[col].isna() ], y[ ~dns[col].isna() ], 1)
        ax.plot(x, m*x+b, linestyle='-', linewidth=1.2, c=colors[num])

        # Plot the data
        # ax.scatter(x, y, marker=',', s=1, c=colors[num])
        ax.plot(x, y, linewidth=0.5, c=colors[num])

        slope_arr.append(m)

        # Compute the weighted variance in the slope:
        # Should I do this by:
        #   1) the range of cos(vza), or
        #   2) the temporal range of the data?
        cond = ~dns[col].isna()
        dat = dataframe.index # For the temporal range
        # dat = y # for the cos(vza) range
        sigma_m = weighted_average.weight(dat[ cond ], y)
        weight_arr.append(sigma_m)

    # ax.set_xlim(-10,10)
    plt.tight_layout()
    ax.set_xlabel('1/cos(za)')
    ax.set_ylabel('ln(DN/t_exp)')
    plt.grid()
    ax.plot()

    print(f'Average slope:      {np.mean(slope_arr)}')
    print(f'Median slope:       {np.median(slope_arr)}')
    print(f'Standard-dev slope: {np.std(slope_arr)}')

    print()

    # Compute the weighted mean slope:
    num_sum = 0
    den_sum = 0
    for m, w in zip(slope_arr, weight_arr):
        weight = 1 / w**2
        num_sum += ( m * weight )
        den_sum += ( weight )
    weighted_slope = num_sum / den_sum

    print(f'Weighted-average slope: {weighted_slope}')
    print()