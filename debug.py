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
from modules import sql_query_module
import urllib
import sqlalchemy


today_date = datetime.now()
# ---------------------------------STACKING & SENDING FILES----------------------------------

directory_path = r'P:\Knowledge Management\Ellevation\Data Sent 2023-24\State Testing'
formatted_month_day_year = today_date.strftime("%m_%d")


directory_path_sbac = os.path.join(directory_path, f'sbac_{formatted_month_day_year}')
sbac = stack_files(directory_path_sbac)
sbac['CALPADSSchoolCode'] = sbac['CALPADSSchoolCode'].astype(str).str[7:]


directory_path_elpac = os.path.join(directory_path, f'elpac_{formatted_month_day_year}')
elpac = stack_files(directory_path_elpac)
elpac['CALPADSSchoolCode'] = elpac['CALPADSSchoolCode'].astype(str).str[7:]

sbac = filter_on_full_cds_code(sbac, 'CALPADSSchoolCode')
elpac = filter_on_full_cds_code(elpac, 'CALPADSSchoolCode')


# -------------------------------------------get_elpac_import------------------
elpac = get_elpac_import(elpac)
elpac.name = 'ELPAC'
directory_path_elpac = os.path.join(directory_path, f'ELPAC_STACKED_{formatted_month_day_year}.csv')
try:
    elpac.to_csv(directory_path_elpac, index=False)
    logging.info(f'ELPAC sent to {directory_path} for ellevation pickup')
except:
    logging.info(f'ELPAC unable to send for ellevation pickup')


#Differing decoding method. Refer to message with Abi
# ss_decode = {4.0: 'WelDev', 
#                 3.0: 'ModDev', 
#                 2.0: 'SomDev',
#                 1.0: 'MinDev', 
#                 '': 'No Score', 
#                 'NS': 'No Score'}

# -------------------------------Get SBAC import-------------------------

#Missing PLScore Column and ProficiencyLevelCode Mapping
sbac_final = get_sbac_cols(sbac, 'SBAC')
sbac_final.name = 'SBAC'
directory_path_sbac = os.path.join(directory_path, f'SBAC_STACKED_{formatted_month_day_year}.csv')
try:
    sbac_final.to_csv(directory_path_sbac, index=False)
    logging.info(f'SBAC sent to {directory_path} for ellevation pickup')
except:
    logging.info(f'SBAC unable to send for ellevation pickup')

# PL Score 1	STNM
# PL Score 2	STNL
# PL Score 3	STMT
# PL Score 4	STEX

# ------------------------------Get CAST import-------------------------

cast = get_cast_cols(sbac, 'CAST')
cast.name = 'CAST'
directory_path_cast = os.path.join(directory_path, f'CAST_STACKED_{formatted_month_day_year}.csv')
try:
    cast.to_csv(directory_path_cast, index=False)
    logging.info(f'CAST sent to {directory_path} for ellevation pickup')
except:
    logging.info(f'CAST unable send for ellevation pickup')

# PL Score 1	BLST
# PL Score 2	ANST
# PL Score 3	ABST

# ------------------------------------------------------send to DataTeamSandbox on 89 server-----------------------------

# quoted = urllib.parse.quote_plus("Driver={SQL Server Native Client 11.0};"
#                      "Server=10.0.0.89;"
#                      "Database=DataTeamSandbox;"
#                      "Trusted_Connection=yes;")

# engine = sqlalchemy.create_engine('mssql+pyodbc:///?odbc_connect={}'.format(quoted))



# def send_to_SQL(file):
    
#     dtypes, table_cols = sql_query_module.SQL_query.get_dtypes(file, 'DataTeamSandbox', f'{file.name}_Scores')
#     elpac.to_sql(f'{file.name}_Scores', schema='dbo', con = engine, if_exists = 'replace', index = False, dtype=dtypes)
#     engine.dispose()


# send_to_SQL(elpac)
# send_to_SQL(sbac_final)
# send_to_SQL(cast)


#What about selecting the initial admin year when switching over Y2Y?


file = elpac

dtypes, col_names = sql_query_module.SQL_query.get_dtypes(file, 'DataTeamSandbox', f'{file.name}_Scores')