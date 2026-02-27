import numpy as np

def weight(idx, data):
    """
    Takes in a data array and returns the Weight (credence) of that data
    based on the # of valid datapoints
    """

    # NOTE: N data points collected over a larger time is MORE constrained
    sigmax = np.std(idx) # standard deviation in time
    N = len(data[~data.isna()]) # number of data points over the time
    sigmay = np.std(data) # standard deviation in data (mags or DN)

    # Compute the standard deviation in the slope
    sigmam = sigmay / (np.sqrt(N) * sigmax)
    
    return sigmax, sigmay, sigmam
    