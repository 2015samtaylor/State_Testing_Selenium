from config import username, password, ellevation_host, ellevation_username, ellevation_password
from modules.login_module import *
from modules.download_files_module import *
from modules.unit_testing import TestFileProcessing
from modules.data_transformation import *
from modules.post_download_change import *
from modules.sql_query_module import *
from modules.sftp_ops import *
from modules.logging_metadata import *

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
# formatted_month_day_year = '06_17_24' #temporarily in here for up to date send
download_directory = os.getcwd() + f'\\file_downloads\\elpac\\{formatted_month_day_year}'
pd.set_option('display.max_columns', None)

logger = JobLogger(process_name='ELPAC_SBAC_Results_Selenium', 
                   job_name='ELPAC_SBAC_Results_Selenium', 
                   job_type='python')

logging.basicConfig(filename='ELPAC_SBAC_results.log', level=logging.INFO,
                   format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',force=True)
logging.info('\n\n-------------ELPAC_SBAC_results new instance log')


# Set up Chrome options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
chrome_options = webdriver.ChromeOptions()
prefs = {'download.default_directory' : download_directory,
         'profile.default_content_setting_values.automatic_downloads': 1,
         'profile.content_settings.exceptions.automatic_downloads.*.setting': 1}
chrome_options.add_experimental_option('prefs', prefs)
# Specify the path to the manually downloaded ChromeDriver
chrome_driver_path = r"C:\Users\samuel.taylor\Desktop\chromedriver-win64\chromedriver.exe" # Google Chrome Version 128.0.6613.114 Official Build 64 bit
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)


#instantiate SFTP conn with Ellevation
sftp_conn_ellevation = SFTPConnection(
    host=ellevation_host,
    username=ellevation_username,
    password=ellevation_password,
    use_pool=False
)


def selenium_process(SY):

    logIn(username, password, driver)
    launch_to_homescreen(driver)

    # ---------------------------------------SBAC & ELPAC Files Request and Download-------
    # Call the function, school report names variable is called for just school name. MUst occur in this order for Selenium
    #Equivalent of Student Score Data File
    SBAC_output = SBAC_package_func(driver, SY, 'Tested', formatted_month_day_year)
    ELPAC_output = ELPAC_package_func(driver, SY, 'Tested', formatted_month_day_year)

    return(SBAC_output, ELPAC_output)


def main(SY):

    sbac_local_dir = os.getcwd() + fr'\file_downloads\sbac\{formatted_month_day_year}'
    elpac_local_dir = os.getcwd() + fr'\file_downloads\elpac\{formatted_month_day_year}'
    sbac_pdrive_dir = fr'P:\Knowledge Management\Ellevation\Data Sent 2023-24\State Testing\sbac_{formatted_month_day_year}'
    elpac_pdrive_dir = fr'P:\Knowledge Management\Ellevation\Data Sent 2023-24\State Testing\elpac_{formatted_month_day_year}'

    #clear out download directories prior in the case or re-runs. Checks at the end see if all files are downloaded. Refer to logs
    for i in [sbac_local_dir, elpac_local_dir]:
        empty_directory(i)
        create_directory(i)

    for i in [sbac_pdrive_dir, elpac_pdrive_dir]:
        create_directory(i) #Not deleting files already downloaded in the p-drive. Drop duplicates in stack function accounts for duplicate files

    SBAC_output, ELPAC_output = selenium_process(SY)
    # --------------------------------Unzip the XLSX Files and Move them to the P-Drive, Additional Unit Test---------------Path - 'P:\Knowledge Management\Ellevation\Data Sent 2023-24\State Testing'

    SBAC_output = unzip_move_and_unit(SBAC_output, 'sbac', formatted_month_day_year)
    ELPAC_output = unzip_move_and_unit(ELPAC_output, 'elpac', formatted_month_day_year)

    # # ---------------------------------POST SELENIUM PROCESS, STACKING & SENDING FILES----------------------------------
    sbac_stack = stack_files(sbac_pdrive_dir, 'CAASPP') #This is where files are raw and stacked before transformation
    elpac_stack = stack_files(elpac_pdrive_dir, 'ELPAC') #Green Dot Schools are pulled out of master file

    sbac_stack = downsize_sbac_cols(sbac_stack)
    elpac_stack = downsize_elpac_cols(elpac_stack)

    #Break cast and sbac apart. 
    cast_stack = sbac_stack.loc[sbac_stack['RecordType'] == 6]
    sbac_stack = sbac_stack.loc[sbac_stack['RecordType'].isin([1, 2])]

    #For Helens Ellevation Pickup, send to same dir as individual files the stack in stacked_files dir
    #Use this as route to drop raw files
    send_stacked_csv(elpac_stack, 'ELPAC', formatted_month_day_year) 
    send_stacked_csv(sbac_stack, 'SBAC', formatted_month_day_year)
    send_stacked_csv(cast_stack, 'CAST', formatted_month_day_year)

    specific_stack_files = [
    f"P:\Knowledge Management\Ellevation\Data Sent 2023-24\State Testing\Stacked_Files\SBAC_STACKED_{formatted_month_day_year}.csv",
    f"P:\Knowledge Management\Ellevation\Data Sent 2023-24\State Testing\Stacked_Files\CAST_STACKED_{formatted_month_day_year}.csv",
    f"P:\Knowledge Management\Ellevation\Data Sent 2023-24\State Testing\Stacked_Files\ELPAC_STACKED_{formatted_month_day_year}.csv",
    ]

    SFTP_export_files_to_SFTP(specific_stack_files,
                            remote_dir='/data',  #root dir on clevers sftp
                            sftp = sftp_conn_ellevation)
    
main('2024')
# main('2025')
    

try:
    main()
    logging.info('Process was a success')
    logger.log_job('Success')
    logger.send_frame_to_SQL()
except Exception as e:     
    logging.info(f'Process failed due to the following: {e}')
    logger.log_job('Failure')
    logger.send_frame_to_SQL()
