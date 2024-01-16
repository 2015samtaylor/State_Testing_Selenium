import unittest
import os
import pandas as pd
import logging
from datetime import datetime
today_date = datetime.now()
formatted_month_day = today_date.strftime("%m_%d")

logging.basicConfig(filename='ELPAC_SBAC_results.log', level=logging.INFO,
                   format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',force=True)


class TestFileProcessing(unittest.TestCase):

    def test_file_processing(self, SBAC_ELPAC):
        # Define the directory path for testing
        test_directory = rf'P:\Knowledge Management\Ellevation\Data Sent 2023-24\State Testing\{SBAC_ELPAC}_{formatted_month_day}'

        # Your original file processing logic
        files = os.listdir(test_directory)
        files_df = pd.DataFrame(files, columns=['raw'])
        files_df['dupe'] = files_df['raw'].str[:7]
        files_df['dupe'] = files_df['dupe'].astype(str).str.lstrip('0')

        school_ids = {'CHA': '136119',
                      'ING': '1996586',
                      'LEA': '1996313',
                      'DLH': '101675',
                      'SLA': '102434',
                      'VEN': '106831',
                      'BRW': '106849',
                      'BUN': '111575',
                      'ROB': '111583',
                      'LCK': '118588',
                      'JMS': '122481',
                      'AEO': '123992',
                      'LGC': '124016',
                      'MAE': '129270',
                      'FLO': '134023',
                      'WAT': '111625',
                      'JAM': '124008',
                      'CMP': '137984'}

        expected_schools = pd.DataFrame(list(school_ids.values()), columns=['All Schools'])
        
        # Your merging logic
        merged_df = pd.merge(files_df, expected_schools, left_on='dupe', right_on='All Schools', how='outer', indicator=True)

        # Assertions based on your expected outcomes
        try:
            self.assertEqual(len(merged_df), len(files_df), "Lengths do not match, indicating missing or extra schools.")
            logging.info(f'Success, all schools are here for {SBAC_ELPAC}')
        except:
            logging.info(f"Lengths do not match, indicating missing or extra schools for {SBAC_ELPAC}.")
        try:
            self.assertTrue(all(merged_df['_merge'] == 'both'), "Merging failed for some schools.")
            logging.info(f'Success, merging worked for all schools {SBAC_ELPAC}')
        except:
            logging.info(f"Merging failed for some schools {SBAC_ELPAC}.")



