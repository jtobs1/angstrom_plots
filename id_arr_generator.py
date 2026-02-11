import pandas as pd
import numpy as np
import sys

def id_array_generator(dataframe):
    """
    Parameters:
        dataframe: The DataFrame created by parse_ids.py
    Returns:
        DataFrame of equal size for all identified star ID's
        Columns:
            Star magnitude; Total DN value; Total area value
    """
    
    # find all valid IDs in the dataframe
    id_arr_list = []
    
    # Loop through the "hr" column to find valid IDs
    for i in range(len(dataframe)):
        for l in dataframe.at[i, 'hr']:
            
            # Check to see if ID isn't already in the list
            if l not in id_arr_list:
                id_arr_list.append(l)
    id_arr_list = np.array(id_arr_list)
            
    # Now, loop through the 'mag' and 'total_DN' columns and
    # match the IDs to the corresponding values
    # Do this with a DataFrame:
    # Columns: ID (~36 columns)
    # Rows: mag_list, total_DN_list (360 rows)
    id_df = pd.DataFrame(np.nan, columns=id_arr_list, index=range(360))
    id_df = id_df.astype(object)

    # Go through each frame
    for i in range(len(dataframe)): # 360 rows / frames
    
        # Loop through each ID:
        # Check to see if the ID exists in the current frame,
        # and which index of the 'hr' array it is located at
        # IF the ID doesn't exits, keep it as a np.nan
        for id in id_arr_list:
            if id in dataframe.at[i, 'hr']:
    
                idx = np.where(dataframe.at[i, 'hr'] == id)[0][0]
                
                # Now, get the corresponding mag and total_DN values
                mag_value = dataframe.at[i, 'mag'][idx][0]
                total_DN_value = dataframe.at[i, 'total_DN'][idx][0]
                total_area_value = dataframe.at[i, 'area'][idx][0]
                elevation = dataframe.at[i, 'el'][idx][0]
                
                # Assign to the DataFrame
                id_df.at[i, id] = (mag_value, total_DN_value, total_area_value, elevation)
    
    return id_df 


