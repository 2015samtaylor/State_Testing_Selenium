from config import username, password
from modules.login_module import *
from modules.download_files_module import *
from modules.unit_testing import TestFileProcessing
from modules.data_transformation import *
from modules.post_download_change import *
from modules.sql_query_module import *


from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoSuchWindowException
from selenium.webdriver.common.action_chains import ActionChains
import os
import pandas as pd
import logging
import time
from datetime import datetime
from modules.sql_query_module import SQL_query
import urllib
import sqlalchemy
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
today_date = datetime.now()
formatted_month_day_year = today_date.strftime("%m_%d_%y")
download_directory = os.getcwd() + f'\\file_downloads\\elpac\\{formatted_month_day_year}'
pd.set_option('display.max_columns', None)

logging.basicConfig(filename='ELPAC_SBAC_results.log', level=logging.INFO,
                   format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',force=True)
logging.info('\n\n-------------ELPAC_SBAC_results new instance log')

#create file_download dir, and establish download directory
create_directory('file_downloads')

#clear out donwload directories prior in the case or re-runs
# Example usage
sbac_dir = f'file_downloads\\sbac\\{formatted_month_day_year}'
elpac_dir = f'file_downloads\\elpac\\{formatted_month_day_year}'

empty_directory(sbac_dir)
empty_directory(elpac_dir)
create_directory(sbac_dir)
create_directory(elpac_dir)

# Set up Chrome options
chrome_options = webdriver.ChromeOptions()
prefs = {'download.default_directory' : download_directory,
         'profile.default_content_setting_values.automatic_downloads': 1,
         'profile.content_settings.exceptions.automatic_downloads.*.setting': 1}
chrome_options.add_experimental_option('prefs', prefs)
driver = webdriver.Chrome(ChromeDriverManager().install(), options = chrome_options)


def selenium_process(SY):

    logIn(username, password, driver)
    launch_to_homescreen(driver)

    # ---------------------------------------SBAC & ELPAC Files Request and Download-------
    # Call the function, school report names variable is called for just school name. MUst occur in this order for Selenium
    #Equivalent of Student Score Data File
    SBAC_output = SBAC_package_func(driver, SY, 'Tested', formatted_month_day_year)
    ELPAC_output = ELPAC_package_func(driver, SY, 'Tested', formatted_month_day_year)

    return(SBAC_output, ELPAC_output)

SBAC_output, ELPAC_output = selenium_process('2024')

# --------------------------------Unzip the XLSX Files and Move them to the P-Drive, Additional Unit Test---------------
# Path - 'P:\Knowledge Management\Ellevation\Data Sent 2023-24\State Testing'

# SBAC_output = unzip_move_and_unit(SBAC_output, 'sbac', formatted_month_day_year)
# ELPAC_output = unzip_move_and_unit(ELPAC_output, 'elpac', formatted_month_day_year)

# # ---------------------------------POST SELENIUM PROCESS, STACKING & SENDING FILES----------------------------------

# directory_path = r'P:\Knowledge Management\Ellevation\Data Sent 2023-24\State Testing'

# directory_path_sbac = os.path.join(directory_path, f'sbac_{formatted_month_day_year}')
# sbac_stack = stack_files(directory_path_sbac)

# directory_path_elpac = os.path.join(directory_path, f'elpac_{formatted_month_day_year}')
# elpac_stack = stack_files(directory_path_elpac)

# elpac_stack = filter_on_full_cds_code(elpac_stack, 'CALPADSSchoolCode')
# sbac_stack = filter_on_full_cds_code(sbac_stack, 'CALPADSSchoolCode')
# # elpac_stack = pd.read_csv('file_downloads\elpac_stack.csv') #For testing purposes to start from this point
# # sbac_stack = pd.read_csv('file_downloads\sbac_stack.csv')

# # -----------------------------Where the normalization of the dataframes occur, column changing & mapping------------------
# elpac = get_elpac_import(elpac_stack, 'ELPAC')
# sbac = get_sbac_import(sbac_stack, 'SBAC')  #For some reason, raw ELPAC file does not have LocalStudentID or studentnumber present for SBAC ELA & Math overall 
# cast = get_cast_import(sbac_stack, 'CAST')

# #For Helens Ellevation Pickup, send to same dir as individual files the stack in stacked_files dir
# send_stacked_csv(elpac, 'ELPAC', directory_path, formatted_month_day_year) 
# send_stacked_csv(sbac, 'SBAC', directory_path, formatted_month_day_year)
# send_stacked_csv(cast, 'CAST', directory_path, formatted_month_day_year)

# # -----------------------------------------------Send over new records------------------------

# def send_to_sql(frame, file_name):
#     dtypes, table_cols = SQL_query.get_dtypes(frame, 'DataTeamSandbox', f'{file_name}_Scores')

#     # Reference the DataTeamSandbox master tables before they are fully replaced with today's update in order to find the incoming records
#     #These are populated within the dictionary before the master table is updated. Therefore they are good. 
#     new_records = {
#         'CAST': grab_new_records(cast, 'CAST'),
#         'ELPAC': grab_new_records(elpac, 'ELPAC'),
#         'SBAC': grab_new_records(sbac, 'SBAC')
#     }
    
#     #Update the master table with a full replace, after assessing todays incoming records by each table
#     try:
#         frame.to_sql(f'{file_name}_Scores', schema='dbo', con = SQL_query.engine, if_exists = 'replace', index = False, dtype=dtypes)
#         logging.info(f"Sent data - {len(frame)} records to master table {file_name}_Scores")
#     except Exception as e:
#         logging.info(f'Unable to send data to {file_name}_Scores due to \n {e}')

#     #Update the table with append of only new records, and timestamp it within new_records func
#     try:
#         new_records[file_name].to_sql(f'{file_name}_New_Scores', schema='dbo', con = SQL_query.engine, if_exists = 'append', index = False, dtype=dtypes)
#         logging.info(f"Sent data to {file_name}_New_Scores, by appending {len(new_records[file_name])} new records")
#     except Exception as e:
#         logging.info(f'Unable to send data to {file_name}_New_Scores due to \n {e}')


#  # OBTAINING NEW RECORDS PROCESS
# # The master tables get a full replace with todays data files, however this does not occur until todays data files
# # is compared to the master tables. 

# #Whatever is strictly coming in on the merge from the new frame from these 4 columns will be sent to new scores table
# # ['SSID', 'TestType', 'TestName', 'ScaleScore']

# #After new scores table is appended with new records with last_update timestamp, the master table gets a full replace of
# #todays data files. 


# send_to_sql(elpac, 'ELPAC')
# send_to_sql(sbac, 'SBAC')
# send_to_sql(cast, 'CAST')