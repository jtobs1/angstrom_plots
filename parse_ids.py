import scipy.io as sp
import pandas as pd
import numpy as np

def ids_dataframe(fname):
    ids = sp.loadmat(fname)

    id_arr = ids['star_id'][0]
    # The Yale Bright Star Catalogue... reduced?
    star_cat_reduced = ids['star_cat_reduced'][0]
    # projective_transform = ids['projective_transform'][0]

    df = pd.DataFrame()

    # Names for id_arr deconstruction
    names1 = ['frame','hr','x','y',
             'x_predicted','y_predicted','el',
             'az','mag','ra','dec','area','major_axis_len',
             'minor_axis_len','orientation','diameter','total_DN']
    for name in names1:
        df[name] = []
        df[name] = df[name].astype(object)
    
    names2 = ['Az','El','Name',
             'Mag','RA','Dec','HR',
             'frame','utc_dtime',
             'x_predicted','y_predicted']
    for name in names2:
        df[name] = []
        df[name] = df[name].astype(object)

    # Deconstruct the id_arr and add to the DataFrame
    for num, i in enumerate(id_arr):
        for l, name  in zip(i, names1):
            idx = np.uint16(num)
            if name == 'frame':
                pass
            else:
                df.at[idx, name] = l.T
    
    # Add star_cat_reduced info to the DataFrame
    for num ,j in enumerate(star_cat_reduced):
        for k, name in zip(i, names2):
            idx = np.uint16(num)
            if name == 'frame':
                pass
            else:
                df.at[idx, name] = k.T
    
    # Drop duplicate columns
    df = df.drop(columns=['x_predicted','y_predicted'])

    return df
