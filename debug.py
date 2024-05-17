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
create_directory(f'file_downloads\\sbac\\{formatted_month_day_year}')
create_directory(f'file_downloads\\elpac\\{formatted_month_day_year}')

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

    # -----------------------------------------Unzip the Files and Move them to the P-Drive in this location 'P:\Knowledge Management\Ellevation\Data Sent 2023-24\State Testing'
    SBAC_output = unzip_move_and_unit(SBAC_output, 'sbac')
    ELPAC_output = unzip_move_and_unit(ELPAC_output, 'elpac')

selenium_process('2024')


# ---------------------------------POST SELENIUM PROCESS, STACKING & SENDING FILES----------------------------------

directory_path = r'P:\Knowledge Management\Ellevation\Data Sent 2023-24\State Testing'

directory_path_sbac = os.path.join(directory_path, f'sbac_{formatted_month_day_year}')
sbac_stack = stack_files(directory_path_sbac)

directory_path_elpac = os.path.join(directory_path, f'elpac_{formatted_month_day_year}')
elpac_stack = stack_files(directory_path_elpac)

elpac_stack = filter_on_full_cds_code(elpac_stack, 'CALPADSSchoolCode')
sbac_stack = filter_on_full_cds_code(sbac_stack, 'CALPADSSchoolCode')
# elpac_stack = pd.read_csv('file_downloads\elpac_stack.csv') #For testing purposes to start from this point
# sbac_stack = pd.read_csv('file_downloads\sbac_stack.csv')

# -----------------------------Where the normalization of the dataframes occur, column changing & mapping------------------
elpac = get_elpac_import(elpac_stack, 'ELPAC')
sbac = get_sbac_import(sbac_stack, 'SBAC')  #For some reason, raw ELPAC file does not have LocalStudentID or studentnumber present for SBAC ELA & Math overall 
cast = get_cast_import(sbac_stack, 'CAST')

#For Helens Ellevation Pickup.
send_stacked_csv(elpac, 'ELPAC', directory_path, formatted_month_day_year) 
send_stacked_csv(sbac, 'SBAC', directory_path, formatted_month_day_year)
send_stacked_csv(cast, 'CAST', directory_path, formatted_month_day_year)

# -----------------------------------------------Send over new records------------------------

def send_to_sql(frame, file_name):
    dtypes, table_cols = SQL_query.get_dtypes(frame, 'DataTeamSandbox', f'{file_name}_Scores')
    
    try:
        frame.to_sql(f'{file_name}_Scores', schema='dbo', con = SQL_query.engine, if_exists = 'replace', index = False, dtype=dtypes)
        logging.info('Sent data to f{file_name}_Scores')
    except:
        logging.info(f'Unable to send data to {file_name}_Scores')
        
send_to_sql(elpac, 'ELPAC')
send_to_sql(sbac, 'SBAC')
send_to_sql(cast, 'CAST')