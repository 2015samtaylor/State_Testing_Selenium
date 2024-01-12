from config import username, password
from modules.login_module import logIn, launch_to_homescreen, create_directory
from modules.download_files_module import request_report_process, whats_missing, download_process

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
download_directory = os.getcwd() + f'\\file_downloads\\sbac\\{formatted_month_day}'
chrome_options = webdriver.ChromeOptions()
prefs = {'download.default_directory' : download_directory,
         'profile.default_content_setting_values.automatic_downloads': 1,
         'profile.content_settings.exceptions.automatic_downloads.*.setting': 1}
chrome_options.add_experimental_option('prefs', prefs)
driver = webdriver.Chrome(ChromeDriverManager().install(), options = chrome_options)

logIn(username, password, driver)
launch_to_homescreen(driver)

caaspp_list = ['LEA CAASPP Coordinator at Alain Leroy Locke College Preparatory Academy',
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
                'LEA CAASPP Coordinator at Oscar De La Hoya Animo Charter High']

#This exists when passing names into the requested reports. 
school_report_names = [entry.split(' at ', 1)[1] for entry in caaspp_list]

# Call the function
request_report_process(driver, caaspp_list)
download_process(school_report_names, driver)    

def download_for_missing(dir_path, driver):
    files = whats_missing(dir_path)
    if files.loc[files['files'].isna()].empty == True:
        logging.info('All files are downloaded')
    else:
        logging.info(f"These schools are missing {files.loc[files['files'].isna()]['School_Name'].values}")
        missing_frame = files.loc[files['files'].isna()]
        missing_schools = list(missing_frame['School_Name'])
        print(f'These schools are missing - {missing_schools}')

    try:
        for i in missing_schools:
            download_process(missing_schools, driver)
    except Exception as e:
        print(e)


download_for_missing(f'sbac\\{formatted_month_day}', driver)