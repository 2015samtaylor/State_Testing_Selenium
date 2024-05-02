from config import username, password
from modules.login_module import logIn, launch_to_homescreen, create_directory
from modules.download_files_module import request_report_process, download_loop_missing, download_process,  move_files_over, unzip_xlsx_file, unzip_files_in_same_dir, move_xlsx_files
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
formatted_month_day = today_date.strftime("%m_%d")
pd.set_option('display.max_columns', None)



cast = pd.read_csv('cast.csv')
elpac = pd.read_csv('elpac.csv')
sbac_final = pd.read_csv('sbac.csv')


elpac = Clean(elpac, 'elpac')
elpac_clean = elpac.clean_up_rotating_file()

file = elpac_clean
file_name = 'ELPAC'


dtypes, table_cols = SQL_query.get_dtypes(file, 'DataTeamSandbox', f'{file_name}_Scores')
file.to_sql(f'{file_name}_Scores', schema='dbo', con = SQL_query.engine, if_exists = 'replace', index = False, dtype=dtypes)

#debug again to see why the dtypes are being changes