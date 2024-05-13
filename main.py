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

SY = '2024'
logIn(username, password, driver)
launch_to_homescreen(driver)

# ---------------------------------------SBAC Files Request and Download-------

# Call the function, school report names variable is called for just school name
#Equivalent of Student Score Data File
request_report_process(driver, 'SBAC', 'CAASPP_Student_Score_Data_Extract_Report', caaspp_coordinators, SY)
download_process(school_report_names, f'{SY} CAASPP Student Score Data File By Enrolled LEA', driver) 

#This is here three times to see if anything got skipped the first time. Initial dir is set at ELPAC only to move the files over to SBAC dir
#Will run 5 times

time.sleep(10) #implemented to give time for files to download, removed pending tag
download_loop_missing(f'elpac\\{formatted_month_day_year}', f'{SY} CAASPP Student Score Data File By Enrolled LEA', driver)

#This moves the files from ELPAC  timestamp dir to SBAC timestamp dir. 
#This is because the download dir cannot be changed in Selenium
move_files_over()

# --------------------------------------------ELPAC Files Request and Download

driver.switch_to.default_content() #switch out of iframe
request_report_process(driver, 'ELPAC', 'Student_Results_Report_Student_Score_Data_Extract', elpac_coordinators, SY)
download_process(school_report_names, f'{SY} Summative ELPAC and Summative Alternate ELPAC Student Score Data File By Enrolled LEA', driver) 

time.sleep(10) #implemented to give time for files to download
#This is here three times to see if anything got skipped the first time. 
#Dir remains ELPAC for constant download directory
download_loop_missing(f'elpac\\{formatted_month_day_year}', f'{SY} Summative ELPAC and Summative Alternate ELPAC Student Score Data File By Enrolled LEA', driver)

#Close out driver window once done
driver.close()

#Takes 14 mins to run up to this point
# -----------------------------------------Unzip the Files and Move them to the P-Drive in this location 'P:\Knowledge Management\Ellevation\Data Sent 2023-24\State Testing'
unzip_files_in_same_dir('elpac')
unzip_files_in_same_dir('sbac')

#Keeps raw zip files in the same dir. Only moves over xlsx files
try:
    move_xlsx_files('sbac')
    logging.info('Moved SBAC XLSX files to p-drive')
except:
    logging.info('Unable to move SBAC XLSX files to the p-drive, must be connected to the VPN')
try:
    move_xlsx_files('elpac')
    logging.info('Moved ELPAC XLSX files to p-drive')
except:
    logging.info('Unable to move ELPAC XLSX files to the p-drive, must be connected to the VPN')


#Unit test for school count that also interacts with the log 
test_instance = TestFileProcessing()
test_instance.test_file_processing('sbac')
test_instance.test_file_processing('elpac')

# #Takes roughly 25 mins to download and send
# #Must be connected to the p-drive


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

# -----------------------------Where the normailization of the dataframes occur, column changing & mapping------------------
elpac = get_elpac_import(elpac_stack, 'ELPAC')
sbac = get_sbac_import(sbac_stack, 'SBAC')  #For some reason, raw ELPAC file does not have LocalStudentID or studentnumber present for SBAC ELA & Math overall 
cast = get_cast_import(sbac_stack, 'CAST')

#For Helens Ellevation Pickup.
send_stacked_csv(elpac, 'ELPAC', directory_path, formatted_month_day_year) 
send_stacked_csv(sbac, 'SBAC', directory_path, formatted_month_day_year)
send_stacked_csv(cast, 'CAST', directory_path, formatted_month_day_year)

# -----------------------------------------------Send over new records------------------------
#used in combination with obtain_new and clean class to cleanse dtypes, merge and find new records
def final(frame, frame_name, append_or_replace):
    new_records_elpac = grab_new_records(frame, frame_name) #will return original frame first time
    SQL_query.send_to_SQL(new_records_elpac, frame_name, append_or_replace) #dtypes is acquired within function

final(elpac, 'ELPAC', 'append')
final(cast, 'CAST', 'append')
final(sbac, 'SBAC', 'append')

