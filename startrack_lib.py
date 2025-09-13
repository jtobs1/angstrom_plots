import numpy as np
import glob
import matplotlib.pyplot as plt
from collections import defaultdict
import sys, os


def loc_identifier(arr1, arr2, background_value):
    '''Identifies the locations (i,j) for each "star" common among both scenes
    The "working code" for object_identifier.
    Returns:
        dictionary with keys=star-number, 
            and associated (i,j) location.
    '''
    count = 0
    star_loc_dict = defaultdict(list)
    for i in range(arr1.shape[0]-1):
        for j in range(arr1.shape[1]-1):
            if ((arr1[i, j] > 2*background_value) & (arr2[i, j] > 2*background_value)):
                star_loc_dict[count].append((i,j))
                count += 1  
    return star_loc_dict

# the Star Counter algorithm!
def object_identifier(fdir, background_value=2e2):
    '''Identifies all "stars" common among all images
    args:
        fdir - directory of .png images.
        background_value - float value of background pixels
            Scaled to the plotting code's vmin value.
    returns:
        dictionary of all "stars" and associated values (a 3x3 pixel box around a bright pixel).
    '''
    # Make the assumption that two images contain all information of constant objects
    # this will extract the (i,j) locations of each star, 
    # to simplify further star identification
    images = sorted(glob.glob(os.path.join(fdir, '*npy')))
    im1 = np.load(images[5], allow_pickle=True) # 1st image
    im2 = np.load(images[7], allow_pickle=True) # 2nd image

    # Just look through the first and second image
    # and identify every consistent "object"
    star_loc_dict = loc_identifier(im1, im2, background_value=background_value)

    # Create a new dictionary of array "boxes" around each star
    star_dict = defaultdict(list, {k: [] for k in star_loc_dict}) # same size as star_loc_dict
    for i in images:
        image = np.load(i, allow_pickle=True)
        for j in star_dict:
            il, jl = star_loc_dict[j][0]
            try:
                star_box = image[il-3:il+3, jl-3:jl+3]
                star_dict[j].append(star_box)
            except:
                star_dict[j].append(0)

    return star_dict, star_loc_dict

def sliding_window(arr, s):
    '''Creates a Sliding Windown that averages arr over a window size s.
    args:
        s - sliding window size
        arr - array to be smoothened
    '''
    steps = len(arr) / s # analagous to n_points
    arr = np.array(arr)
    arr1 = np.zeros((int(steps)))

    for i, j in zip(range(0, len(arr), s), range(0, len(arr1))):
        if (i+s <= len(arr)):
            arr1[j] = np.mean(arr[i: i+s])
        else:
            break

    return arr1

def line_fit(x, y, deg=1):
    '''Uses numpy.polyfit to return a least-squares line fit
    '''
    coeffs = np.polyfit(x, y, 1) # returns 1st-degree coefficients
    poly = np.poly1d(coeffs)
    return coeffs, poly

def langley_plot(star_dict):
    '''Creates the Langley Plots for stars within the range of star_dict'''

    # at some point, link t to actual times

    # This can range from 0 to roughly 2500 (depending on cloud cover)
    # All you have to do is count the stars.
    coefficients = [] # cummulative tracker of slopes
    start_val = 80
    incr = 10
    for j in range(start_val, start_val+incr): # Controls how many stars to analyze and plot.
        star_val = []
        
        for t, i in enumerate(star_dict[j]):
            # instead of taking "star" index value,
            # could take the average box?
            try:
                i = i[3, 3]
            except:
                i = 0
            star_val.append(i)
        
        # The FIT should be applied before the sliding window! (if its not too noisy)

        # apply sliding_window to star_val to smoothen them jawns
        s = 20
        smoothen = True
        if smoothen:
            star_val = sliding_window(star_val, s=s)

        ts = np.arange(0, len(star_val))
        plt.plot(ts, star_val, label=f'star {j}', linewidth='1', marker='.', linestyle=':')

        coeffs, poly = line_fit(ts, star_val, deg=1)
        plt.plot(ts, poly(ts), '--', label='')
        coefficients.append(coeffs[0])
        print(coeffs)

    average_slope = np.round(np.mean(np.array(coefficients)), 4)
    
    plt.ylim(0, 2500)
    plt.title(f'520nm Star "Brightnesses": Average Slope={average_slope}')
    plt.ylabel('Digital Number')
    plt.xlabel('Time (unadjusted)')
    plt.savefig(f'./test_langley_plots/star{start_val}-{start_val+incr}_smoothed{s}.png')
    plt.show()
    plt.close()
