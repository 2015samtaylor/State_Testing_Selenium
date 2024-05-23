#Debug get_elpac_import
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


directory_path = r'P:\Knowledge Management\Ellevation\Data Sent 2023-24\State Testing'

directory_path_sbac = os.path.join(directory_path, f'sbac_{formatted_month_day_year}')
sbac_stack = stack_files(directory_path_sbac)

directory_path_elpac = os.path.join(directory_path, f'elpac_{formatted_month_day_year}')
elpac_stack = stack_files(directory_path_elpac)

elpac_stack = filter_on_full_cds_code(elpac_stack, 'CALPADSSchoolCode')
sbac_stack = filter_on_full_cds_code(sbac_stack, 'CALPADSSchoolCode')

# -----------------------------Where the normalization of the dataframes occur, column changing & mapping------------------
elpac = get_elpac_import(elpac_stack, 'ELPAC')

print(elpac)
