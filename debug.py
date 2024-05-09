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
# formatted_month_day_year = today_date.strftime("%m_%d_%y")
formatted_month_day_year = '04_26_24'
pd.set_option('display.max_columns', None)

from config import username, password
from modules.login_module import logIn, launch_to_homescreen, create_directory
from modules.download_files_module import request_report_process, download_loop_missing, download_process,  move_files_over, unzip_xlsx_file, unzip_files_in_same_dir, move_xlsx_files
from modules.unit_testing import TestFileProcessing
from modules.data_transformation import *
from modules.post_download_change import *
from modules.sql_query_module import *

elpac_stack = pd.read_csv('file_downloads\elpac_stack.csv')
sbac_stack = pd.read_csv('file_downloads\sbac_stack.csv')

# -----------------------------Where the normailization of the dataframes occur, column changing & mapping------------------
elpac = get_elpac_import(elpac_stack, 'ELPAC')
sbac = get_sbac_import(sbac_stack, 'SBAC')  #For some reason, raw ELPAC file does not have LocalStudentID or studentnumber present for SBAC ELA & Math overall 
cast = get_cast_import(sbac_stack, 'CAST')


new_records_cast = grab_new_records(cast, 'CAST') 
dtypes, table_cols = SQL_query.get_dtypes(cast, 'DataTeamSandbox', f'CAST_Scores')
#Get new_records needs to be independent of the send
new_records_cast.to_sql(f'CAST_Scores', schema='dbo', con = SQL_query.engine, if_exists = 'append', index = False, dtype=dtypes)