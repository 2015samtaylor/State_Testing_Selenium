from config import username, password
print(password)
from modules.login_module import logIn, launch_to_homescreen, create_directory
from modules.download_files_module import request_report_process, download_loop_missing, download_process,  move_files_over, unzip_xlsx_file, unzip_files_in_same_dir, move_xlsx_files
from modules.unit_testing import TestFileProcessing
from modules.data_transformation import *
from modules.post_download_change import *


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
pd.set_option('display.max_columns', None)

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
download_process(school_report_names, '2024 CAASPP Student Score Data File By Enrolled LEA', driver) 

#This is here three times to see if anything got skipped the first time. Initial dir is set at ELPAC only to move the files over to SBAC dir
#Will run 5 times

time.sleep(10) #implemented to give time for files to download
download_loop_missing(f'elpac\\{formatted_month_day}', '2024 CAASPP Student Score Data File By Enrolled LEA', driver)

#This moves the files from ELPAC  timestamp dir to SBAC timestamp dir. 
#This is because the download dir cannot be changed in Selenium
move_files_over()

# # --------------------------------------------ELPAC Files Request and Download

# driver.switch_to.default_content()
request_report_process(driver, 'ELPAC', 'Student_Results_Report_Student_Score_Data_Extract', elpac_coordinators)
# download_process(school_report_names, '2024 Summative ELPAC and Summative Alternate ELPAC Student Score Data File By Enrolled LEA', driver) 

# time.sleep(10) #implemented to give time for files to download
# #This is here three times to see if anything got skipped the first time. 
# #Dir remains ELPAC for constant download directory
# download_loop_missing(f'elpac\\{formatted_month_day}', '2024 Summative ELPAC and Summative Alternate ELPAC Student Score Data File By Enrolled LEA', driver)

# #Close out driver window once done
# driver.close()

# #Takes 14 mins to run up to this point
# # -----------------------------------------Unzip the Files and Move them to the P-Drive in this location 'P:\Knowledge Management\Ellevation\Data Sent 2023-24\State Testing'
# unzip_files_in_same_dir('elpac')
# unzip_files_in_same_dir('sbac')

# #Keeps raw zip files in the same dir. Only moves over xlsx files
# try:
#     move_xlsx_files('sbac')
#     logging.info('Moved SBAC XLSX files to p-drive')
# except:
#     logging.info('Unable to move SBAC XLSX files to the p-drive, must be connected to the VPN')
# try:
#     move_xlsx_files('elpac')
#     logging.info('Moved ELPAC XLSX files to p-drive')
# except:
#     logging.info('Unable to move ELPAC XLSX files to the p-drive, must be connected to the VPN')




# #Checks these dirs, for all files being there
# # P:\Knowledge Management\Ellevation\Data Sent 2023-24\State Testing\sbac_01_16
# # P:\Knowledge Management\Ellevation\Data Sent 2023-24\State Testing\elpac_01_16
# test_instance = TestFileProcessing()
# test_instance.test_file_processing('sbac')
# test_instance.test_file_processing('elpac')

# #Takes roughly 25 mins
# #Must be connected to the p-drive

# # ---------------------------------STACKING & SENDING FILES----------------------------------

# directory_path = r'P:\Knowledge Management\Ellevation\Data Sent 2023-24\State Testing'
# formatted_month_day_year = today_date.strftime("%m_%d_%y")


# directory_path_sbac = os.path.join(directory_path, f'sbac_{formatted_month_day_year}')
# sbac = stack_files(directory_path_sbac)
# sbac['CALPADSSchoolCode'] = sbac['CALPADSSchoolCode'].astype(str).str[7:]


# directory_path_elpac = os.path.join(directory_path, f'elpac_{formatted_month_day_year}')
# elpac = stack_files(directory_path_elpac)
# elpac['CALPADSSchoolCode'] = elpac['CALPADSSchoolCode'].astype(str).str[7:]

# sbac = filter_on_full_cds_code(sbac, 'CALPADSSchoolCode')
# elpac = filter_on_full_cds_code(elpac, 'CALPADSSchoolCode')


# # -------------------------------------------get_elpac_import------------------

# def get_elpac_import():

#        e_original = get_elpac_cols(elpac, 'ELPAC')
#        e_scale_score = get_SS_frame(e_original)
#        e_pl_score = get_pl_frame(e_original)

#        #The merge is occurs on testname, and SSID together. THis keeps rows unique
#        e = pd.merge(e_pl_score, e_scale_score, left_on=['SSID', 'testname'], right_on = ['SSID', 'testname'], suffixes= ['', '_SS'], how='left')
#        cols = list(e_pl_score.columns)
#        cols.append('ScaleScore')

#        #re-arrange order
#        col_order = ['Abbreviation', 'SchoolID', 'MasterSchoolID', 'StudentNumber',
#               'StudentID', 'SSID', 'TestGrade', 'ELStatus', 'TestDate', 'DisplayDate',
#               'TestType', 'TestPeriod', 'TestScoreType',  'testname',
#               'ScaleScore', 'PLScore']

#        e = e[col_order]

#        pl_decode = {4.0: 'WelDev', 
#         3.0: 'WelDev', 
#         2.0: 'Som-ModDev',
#         1.0: 'MinDev', 
#         '': 'No Score', 
#         'NS': 'No Score'}

#        e['ProficiencyLevelCode'] = e['PLScore'].map(pl_decode)

#        return(e)

# elpac = get_elpac_import()
# directory_path_elpac = os.path.join(directory_path, f'ELPAC_STACKED_{formatted_month_day_year}.csv')
# elpac.to_csv(directory_path_elpac, index=False)


# #Differing decoding method. Refer to message with Abi
# # ss_decode = {4.0: 'WelDev', 
# #                 3.0: 'ModDev', 
# #                 2.0: 'SomDev',
# #                 1.0: 'MinDev', 
# #                 '': 'No Score', 
# #                 'NS': 'No Score'}

# # -------------------------------Get SBAC import-------------------------

# #Missing PLScore Column and ProficiencyLevelCode Mapping
# sbac_final = get_sbac_cols(sbac, 'SBAC')
# directory_path_sbac = os.path.join(directory_path, f'SBAC_STACKED_{formatted_month_day_year}.csv')
# sbac_final.to_csv(directory_path_sbac, index=False)

# # PL Score 1	STNM
# # PL Score 2	STNL
# # PL Score 3	STMT
# # PL Score 4	STEX

# # ------------------------------Get CAST import-------------------------

# cast = get_cast_cols(sbac, 'CAST')
# directory_path_cast = os.path.join(directory_path, f'CAST_STACKED_{formatted_month_day_year}.csv')
# cast.to_csv(directory_path_cast, index=False)

# # PL Score 1	BLST
# # PL Score 2	ANST
# # PL Score 3	ABST


# #Confirm these are 2024 files