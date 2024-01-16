%load_ext autoreload
%autoreload 2
from config import username, password
print(password)
from modules.login_module import logIn, launch_to_homescreen, create_directory
from modules.download_files_module import request_report_process, download_loop_missing, download_process,  move_files_over, unzip_xlsx_file, unzip_files_in_same_dir, move_xlsx_files
from modules.unit_testing import TestFileProcessing

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
today_date = datetime.now()
formatted_month_day = today_date.strftime("%m_%d")

logging.basicConfig(filename='ELPAC_SBAC_results.log', level=logging.INFO,
                   format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',force=True)
logging.info('\n\n-------------ELPAC_SBAC_results new instance log')

#create file_download dir, and establish download directory
create_directory('file_downloads')
create_directory(f'file_downloads\\sbac\\{formatted_month_day}')
create_directory(f'file_downloads\\elpac\\{formatted_month_day}')

# Set up Chrome options
download_directory = os.getcwd() + f'\\file_downloads\\elpac\\{formatted_month_day}'
chrome_options = webdriver.ChromeOptions()
prefs = {'download.default_directory' : download_directory,
         'profile.default_content_setting_values.automatic_downloads': 1,
         'profile.content_settings.exceptions.automatic_downloads.*.setting': 1}
chrome_options.add_experimental_option('prefs', prefs)
driver = webdriver.Chrome(ChromeDriverManager().install(), options = chrome_options)

logIn(username, password, driver)
launch_to_homescreen(driver)

coord_list = ['LEA CAASPP Coordinator at Alain Leroy Locke College Preparatory Academy',
 'LEA CAASPP Coordinator at Animo City of Champions Charter High',
 'LEA CAASPP Coordinator at Animo Compton Charter',
 'LEA CAASPP Coordinator at Animo Ellen Ochoa Charter Middle',
 'LEA CAASPP Coordinator at Animo Florence-Firestone Charter Middle',
 'LEA CAASPP Coordinator at Animo Inglewood Charter High',
 'LEA CAASPP Coordinator at Animo Jackie Robinson High',
 'LEA CAASPP Coordinator at Animo James B. Taylor Charter Middle',
 'LEA CAASPP Coordinator at Animo Jefferson Charter Middle',
 'LEA CAASPP Coordinator at Animo Leadership High',
 'LEA CAASPP Coordinator at Animo Legacy Charter Middle',
 'LEA CAASPP Coordinator at Animo Mae Jemison Charter Middle',
 'LEA CAASPP Coordinator at Animo Pat Brown',
 'LEA CAASPP Coordinator at Animo Ralph Bunche Charter High',
 'LEA CAASPP Coordinator at Animo South Los Angeles Charter',
 'LEA CAASPP Coordinator at Animo Venice Charter High',
 'LEA CAASPP Coordinator at Animo Watts College Preparatory Academy',
 'LEA CAASPP Coordinator at Oscar De La Hoya Animo Charter High',
 'LEA ELPAC Coordinator at Alain Leroy Locke College Preparatory Academy',
 'LEA ELPAC Coordinator at Animo City of Champions Charter High',
 'LEA ELPAC Coordinator at Animo Compton Charter',
 'LEA ELPAC Coordinator at Animo Ellen Ochoa Charter Middle',
 'LEA ELPAC Coordinator at Animo Florence-Firestone Charter Middle',
 'LEA ELPAC Coordinator at Animo Inglewood Charter High',
 'LEA ELPAC Coordinator at Animo Jackie Robinson High',
 'LEA ELPAC Coordinator at Animo James B. Taylor Charter Middle',
 'LEA ELPAC Coordinator at Animo Jefferson Charter Middle',
 'LEA ELPAC Coordinator at Animo Leadership High',
 'LEA ELPAC Coordinator at Animo Legacy Charter Middle',
 'LEA ELPAC Coordinator at Animo Mae Jemison Charter Middle',
 'LEA ELPAC Coordinator at Animo Pat Brown',
 'LEA ELPAC Coordinator at Animo Ralph Bunche Charter High',
 'LEA ELPAC Coordinator at Animo South Los Angeles Charter',
 'LEA ELPAC Coordinator at Animo Venice Charter High',
 'LEA ELPAC Coordinator at Animo Watts College Preparatory Academy',
 'LEA ELPAC Coordinator at Oscar De La Hoya Animo Charter High']

elpac_coordinators = [coord for coord in coord_list if 'ELPAC' in coord]
caaspp_coordinators = [coord for coord in coord_list if 'CAASPP' in coord]

#This exists when passing names into the requested reports, as a subset. Change list into a set to only retain unique schools
school_report_names = [entry.split(' at ', 1)[1] for entry in elpac_coordinators]
school_report_names = list(set(school_report_names))

# ---------------------------------------SBAC Files Request and Download

# Call the function, school report names variable is called for just school name
request_report_process(driver, 'SBAC', 'CAASPP_Student_Score_Data_Extract_Report', caaspp_coordinators)
download_process(school_report_names, '2023 CAASPP Student Score Data File By Enrolled LEA', driver) 

#This is here three times to see if anything got skipped the first time. Initial dir is set at ELPAC only to move the files over to SBAC dir
#Will run 5 times

time.sleep(10) #implemented to give time for files to download
download_loop_missing(f'elpac\\{formatted_month_day}', '2023 CAASPP Student Score Data File By Enrolled LEA', driver)

#This moves the files from ELPAC  timestamp dir to SBAC timestamp dir. 
#This is because the download dir cannot be changed in Selenium
move_files_over()

# --------------------------------------------ELPAC Files Request and Download

driver.switch_to.default_content()
request_report_process(driver, 'ELPAC', 'Student_Results_Report_Student_Score_Data_Extract', elpac_coordinators)
download_process(school_report_names, '2023 Summative ELPAC and Summative Alternate ELPAC Student Score Data File By Enrolled LEA', driver) 

time.sleep(10) #implemented to give time for files to download
#This is here three times to see if anything got skipped the first time. 
#Dir remains ELPAC for constant download directory
download_loop_missing(f'elpac\\{formatted_month_day}', '2023 Summative ELPAC and Summative Alternate ELPAC Student Score Data File By Enrolled LEA', driver)

#Takes 14 mins to run up to this point
# -----------------------------------------Unzip the Files and Move them to the P-Drive in this location 'P:\Knowledge Management\Ellevation\Data Sent 2023-24\State Testing'
unzip_files_in_same_dir('elpac')
unzip_files_in_same_dir('sbac')

#Keeps raw zip files in the same dir. Only moves over xlsx files
try:
    move_xlsx_files('sbac')
    logging.info('Moved SBAC XLSX files to p-drive')
except:
    logging.info('Unable to move SBAC XLSX files to the p-drive')
try:
    move_xlsx_files('elpac')
    logging.info('Moved ELPAC XLSX files to p-drive')
except:
    logging.info('Unable to move ELPAC XLSX files to the p-drive')


#Close out driver window once done
driver.close()

#Checks these dirs, for all files being there
# P:\Knowledge Management\Ellevation\Data Sent 2023-24\State Testing\sbac_01_16
# P:\Knowledge Management\Ellevation\Data Sent 2023-24\State Testing\elpac_01_16
test_instance = TestFileProcessing()
test_instance.test_file_processing('sbac')
test_instance.test_file_processing('elpac')

#Takes roughly 25 mins
#Must be connected to the p-drive