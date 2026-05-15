import pandas as pd
import numpy as np

def summarize(dataframe) -> pd.DataFrame:
    """
    Creates a summary of the star tracks.
    Returns a pdDataFrame the is sorted by the mean digital number!
    """
    
    # Group by the star track IDs
    g = dataframe.groupby('track_id')

    sum = pd.DataFrame({
        'n_frames_present': g['frame'].count(),
        'frame1': g['frame'].min(),
        'framef': g['frame'].max(),
        'mean_dn': g['dn'].mean(),
        'std_dn': g['dn'].std(),
        'mean_dist': g['match_dist'].mean() 
    }).reset_index()

    span = (sum['framef'] - sum['frame1'] + 1).clip(lower=1)
    sum['completeness'] = sum['n_frames_present'] / span
    sum['gap'] = span - sum['n_frames_present']

    return sum.sort_values('mean_dn', ascending=False).reset_index(drop=True)
