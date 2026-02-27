import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from weighted_average import weight as weight
import sys

def plot_id_array(id_df, plot_val, star_id=None):
    """
    Plots all stars in the ID Array,
    Should be a scatter plot with connected points for each star ID.
    Parameters:
        id_df (pd.DataFrame): DataFrame where each column is a star ID and each row corresponds to a frame.
                    Each cell contains a tuple of (magnitude, total_DN, area) or np.nan if the star is not present.
        plot_val:
            1: Raw magnitudes
            2: Area-normalized magnitudes
            3: Digital Number
            4: Area-normalized digital number
    """

    fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(10, 13))

    df_mags = id_df.applymap(lambda x: x[0] if isinstance(x, tuple) else np.nan)
    df_dn = id_df.applymap(lambda x: x[1] if isinstance(x, tuple) else np.nan)
    df_area = id_df.applymap(lambda x: x[2] if isinstance(x, tuple) else np.nan)

    slope_arr = []
    weight_arr = []

    n = len(id_df.columns)
    colors = plt.cm.jet(np.linspace(0,1,n))

    for num, col in enumerate(id_df.columns):

        if plot_val == 1:
            data = df_mags[col] # Raw magnitudes
            ylabel = 'Magnitudes'
        elif plot_val == 2:
            data = df_mags[col] / df_area[col] # Area-normalized magnitudes
            ylabel = 'Area-normalized Magnitudes'
        elif plot_val == 3:
            data = df_dn[col] # Digital Number
            ylabel = 'Digital Number'
        elif plot_val == 4:
            data = df_dn[col] / df_area[col] # Area-normalized Digital Number
            ylabel = 'Area-normalized Digital Number'
        else:
            print("Incorrect plot_val: \n 1: Raw magnitudes \n 2: Area-normalized magnitudes ..." \
            " \n 3: Digital Number \n 4: Area-normalized digital number")
            sys.exit()

        # Alternatively, fit to raw magnitudes:
        if plot_val == 1 or plot_val == 2:
            # WARNING NOTE
            #   This DOES NOT correctly get the slopes based on nan values!
            m, b = np.polyfit(id_df.index[~df_mags[col].isna()], data[~df_mags[col].isna()], 1)
            # Get the weight (weighted-average by # of datapoints) of this star:
            sigmam = weight(id_df.index[~df_mags[col].isna()], data[~df_mags[col].isna()])
        else:
            m, b = np.polyfit(id_df.index[~df_dn[col].isna()], data[~df_dn[col].isna()], 1)
            # Get the weight (weighted-average by # of datapoints) of this star:
            sigmam = weight(id_df.index[~df_dn[col].isna()], data[~df_dn[col].isna()])

        weights = 1 / sigmam**2

        # Plot all the stars 
        if star_id == None:
            ax[0].plot(id_df.index, m*id_df.index + b, linestyle='-', linewidth=0.5, label=f'ID {col} Trend', c=colors[num])
            
            ax[1].plot(id_df.index, data, marker=',', linestyle='-', linewidth=0.5, label=f'ID {col}', c=colors[num])
        # Plot one select star
        elif star_id != None:
            id = star_id
            if id in id_df.columns:
                ax[0].plot(id_df.index, m*id_df.index + b, linestyle='-', linewidth=0.5, label=f'ID {id} Trend', c=colors[num])
                ax[1].plot(id_df.index, data, marker=',', linestyle='-', linewidth=0.5, label=f'ID {id}', c=colors[num])
            else:
                print(f"Star ID {id} not found in the DataFrame.")
                sys.exit()

        # plot the distribution of slopes
        slope_arr.append(m)
        weight_arr.append(weights)

    # Compute the weighted mean slope:
    num_sum = 0
    den_sum = 0
    for m, w in zip(slope_arr, weight_arr):
        # print(w, m)
        num_sum += m * w
        den_sum += w
    weighted_slope = num_sum / den_sum

    fig.suptitle(f'Mean Slope: {weighted_slope:.6f}')
    
    ax[1].set_xlabel('Frame Number')
    ax[1].set_ylabel(ylabel)
    ax2_ylim = ax[1].get_ylim()
    ax[1].set_title(f'{ylabel} Outputs from Angstrom')

    ax[0].set_ylabel(ylabel)
    ax[0].set_ylim(ax2_ylim)
    ax[0].set_title(f'{ylabel} Best-Fit Lines')

    plt.tight_layout()

