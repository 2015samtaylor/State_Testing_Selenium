import os
import pandas as pd
from zipfile import BadZipFile


def stack_files(directory_path):
    # Get a list of all files in the directory
    file_list = [os.path.join(directory_path, file) for file in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, file))]

    # Initialize an empty list to store DataFrames
    dataframes = []

    # Loop through each file and read it into a DataFrame
    for file in file_list:

        try:
            # Adjust the read_excel parameters based on your file format (e.g., header, delimiter, encoding)
            data = pd.read_excel(file, header=1, engine='openpyxl')
            dataframes.append(data)
        except BadZipFile:
            print(f'Issue iwth BadZipFile when reading excel file: {file}')


    # Use pd.concat to concatenate all DataFrames in the list
    combined_data = pd.concat(dataframes, ignore_index=True)
    return(combined_data)

# -----------------------------------------------------------

def filter_on_full_cds_code(df, column):

    school_ids = {'CHA': '0136119',
                    'ING': '1996586',
                    'LEA': '1996313',
                    'DLH': '0101675',
                    'SLA': '0102434',
                    'VEN': '0106831',
                    'BRW': '0106849',
                    'BUN': '0111575',
                    'ROB': '0111583',
                    'LCK': '0118588',
                    'JMS': '0122481',
                    'WMS': '0122499',
                    'AEO': '0123992',
                    'LGC': '0124016',
                    'MAE': '0129270',
                    'FLO': '0134023',
                    'WAT': '0111625',
                    'JAM': '0124008',
                    'CMP': '0137984'}
                    
    
    #ensure column looking up is also a string
    df[column] = df[column].astype(str)
        
    # Create a list of school_ids values
    school_ids_values = list(school_ids.values())

    # Search for rows in the DataFrame where the 'school_id' column matches any of the values
    GD = df[df[column].isin(school_ids_values)]

    GD = GD.fillna('')
    GD = GD.replace('*', '')

    return(GD)



