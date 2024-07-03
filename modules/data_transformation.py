import os
import pandas as pd
from zipfile import BadZipFile
import logging


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

def stack_files(directory_path, str_matching, filter_schools=None):
    # Get a list of all files in the directory
    file_list = [os.path.join(directory_path, file) for file in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, file))]

    filtered_list = [file for file in file_list if str_matching in file]
    logging.info(f'Stacking {len(filtered_list)} files that have {str_matching} string in them')

    # Initialize an empty list to store DataFrames
    dataframes = []

    # Loop through each file and read it into a DataFrame
    for file in filtered_list:

        try:
            # Adjust the read_excel parameters based on your file format (e.g., header, delimiter, encoding)
            data = pd.read_excel(file, header=1, engine='openpyxl')
            dataframes.append(data)
        except BadZipFile:
            print(f'Issue iwth BadZipFile when reading excel file: {file}')


    # Use pd.concat to concatenate all DataFrames in the list
    combined_data = pd.concat(dataframes, ignore_index=True)

    combined_data['CALPADSSchoolCode'] = combined_data['CALPADSSchoolCode'].astype(str).str[7:]

    # Only filter on full CDS code if filter_schools has a value
    if filter_schools:
        combined_data = filter_on_full_cds_code(combined_data, 'CALPADSSchoolCode')
        logging.info('Schools were filtered on full cds code')

    return(combined_data)

