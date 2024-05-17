from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoSuchWindowException
from selenium.webdriver.common.action_chains import ActionChains
import logging
import pandas as pd
import time
from datetime import datetime
import shutil
import os
import zipfile
from modules.unit_testing import TestFileProcessing
today_date = datetime.now()
formatted_month_day = today_date.strftime("%m_%d_%y")

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


def change_login_role(school_coord_text, driver):

    # Find the toms-header-container 
    header_container = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'toms-header-container'))
    )

    # Find the role_dropdown element
    role_dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'selectedRoleOrg'))
    )

    # Scroll into view
    ActionChains(driver).move_to_element(header_container).perform()

    # Now, try clicking on role_dropdown again
    role_dropdown.click()

    #This is where the coordinator role is changed
    option_element = WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.XPATH, f'//option[@class="myTOMS_roleselect_option" and text()="{school_coord_text}"]'))
    )
    option_element.click()


# 'CAASPP_Student_Score_Data_Extract_Report'
def request_report(driver, test_type, Enrolled_or_Tested, actual_test, SY):

    # Wait for the button to be clickable based on text
    LEA_Reports = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, f'//button[text()="LEA Reports"]'))
    )

    try:
        # Click the button
        LEA_Reports.click()
        logging.info('LEA Reports clicked')
    except:
        logging.info('LEA reports not clicked')

    iframe = WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.ID, 'theFrame'))
    )
    #must switch to iframe, HTML page built on encapsulation. 
    try:
        driver.switch_to.frame(iframe)
        logging.info('Switched to iframe')
    except:
        logging.info('Unable to switch to iframe')

    if test_type == 'SBAC':
        # 'CAASPP_Student_Score_Data_Extract_Report'
        caaspp_student_score_data_file = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, f'//option[@value="{actual_test}"]'))
        )
        try:
            caaspp_student_score_data_file.click()
            logging.info('CAASPP Student Score Data Extract Report Clicked')
        except:
            logging.info('CAASPP Student Score Data Extract Report NOT Clicked')

        dropdown_2 = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="caasppschoolYear"]'))
        )
        try:
            dropdown_2.click()
            logging.info('Dropdown Administration Year Selected')
        except:
            logging.info('Unable to select administration year')
   
    elif test_type == 'ELPAC':
        
        elpac_file = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, f'//option[@value="{actual_test}"]'))
        )
        try:
            elpac_file.click()
            logging.info('ELPAC Data File Clicked')
        except:
            logging.info('ELPAC Data File Not Clicked')

        dropdown_2 = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="schoolYear"]'))
        )
        try:
            dropdown_2.click()
            logging.info('Dropdown Administration Year Selected')
        except:
            logging.info('Unable to select administration year')


    else:
        print('Wrong test type')

    #Does not matter on the test type. Must occur for both
    try:
        #select SY from second drop down
        schoolyear = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, f'//option[@value="{SY}"]'))
        )
        try:
            schoolyear.click()
            logging.info(f'SY {SY} Selected')
        except:
            logging.info(f'SY {SY} not selected')

        dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'caasppldrleaidInput'))
        )
        try:
            dropdown.click()
            logging.info('Org Dropdown clicked')
        except:
            logging.info('Org Dropdown not clicked')
        
        # Locate and click on the hidden input element, does not need to be done on the first try
        organization = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "cnum1"))
        )
        organization.click()
        logging.info('Organization selected')
    except:
        logging.info('Organization was not selected')

    
    enrolled = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, f'//option[@value="{Enrolled_or_Tested}"]'))
    )
    try:
        enrolled.click()
        logging.info(f'{Enrolled_or_Tested} selected')
    except:
        logging.info(f'{Enrolled_or_Tested} not selected')

    if test_type == 'SBAC':
        
        #These date inputs only exists for 2023-2024
        if SY == '2024':
            try:
                start_date_input = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.ID, 'caasppLeaDownloadableRptstartdate'))
                )
                try:
                    start_date_input.click()
                    logging.info('Start date input selected')
                except:
                    logging.info('Start date input not selected')

                start_date_input.clear()
                start_date = f"02/01/{SY}"
                start_date_input.send_keys(start_date)
                logging.info(f'Start date sent over of {start_date}')
            except:
                logging.info(f'Unable to send over start_date of {start_date} ')

            try:

           
                end_date_input = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.ID, 'caasppLeaDownloadableRptenddate'))
                )
                try:
                    end_date_input.click()
                    logging.info('End date input selected')
                except:
                    logging.info('End date input not selected')

                formatted_month = today_date.strftime("%m/%d/")
                end_date = formatted_month + SY
                end_date_input.send_keys(end_date)
                logging.info(f'End date sent over of {end_date}')
            except:
                logging.info(f'Unable to send over end_date of {end_date}')

        else:
            pass

        request_file = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="caasppScoreExRep"]'))
        )
        try:
            request_file.click()
            logging.info('Request file clicked on')
        except:
            logging.info('Request file unable to be clicked')

        try:
            file_download_warning = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "filedownloadwarning"))
            )
            logging.info("File download warning message found, ending request_report function: {}".format(file_download_warning.text)) #if this was available during the 10 seconds it means the file was not available

            driver.back()

            return('No files')

        except TimeoutException:
            logging.info("File is available for download")
                    

    elif test_type == 'ELPAC':

        #These date inputs only exists for 2023-2024
        if SY == '2024':

            try:
                start_date_input = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.ID, 'leaDwnRptstartdate'))
                )

                try:
                    start_date_input.click()
                    logging.info('Start date input selected')
                except:
                    logging.info('Start date input not selected')

                start_date_input.clear()
                start_date = f"04/15/{SY}"
                start_date_input.send_keys(start_date)
                logging.info(f'Start date sent over of {start_date}')
            except:
                logging.info(f'Unable to send over start_date of {start_date} ')

            try:

                end_date_input = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.ID, 'leaDwnRptenddate'))
                )

                try:
                    end_date_input.click()
                    logging.info('End date input selected')
                except:
                    logging.info('End date input not selected')
            
                formatted_month = today_date.strftime("%m/%d/")
                end_date = formatted_month + SY
                end_date_input.send_keys(end_date)
                logging.info(f'End date sent over of {end_date}')
            except:
                logging.info(f'Unable to send over end_date of {end_date}')

        else:
            pass

        request_file = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="ldrDownloadReport"]'))
        )
        try:
            request_file.click()
            logging.info('Request file clicked on')
        except:
            logging.info('Request file unable to be clicked')

        try:
            file_download_warning = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "filedownloadwarning"))
            )
            logging.info("File download warning message found, ending request_report function: {}".format(file_download_warning.text)) #if this was available during the 10 seconds it means the file was not available

            driver.back()

            return('No files')
        except TimeoutException:
            logging.info("File is available for download")
                    
    driver.back()
    try:
        driver.switch_to.default_content()
        logging.info('Out of iframe')
    except:
        logging.info('Still in iframe')

    try:
        driver.refresh()
    except TimeoutException:
        logging.info('Website did not refresh properly')
        driver.refresh



def whats_missing(dir_path):

    # School IDs dictionary
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

    # School names dictionary
    school_names = {'LCK': 'Alain Leroy Locke College Preparatory Academy',
                    'CHA': 'Animo City of Champions Charter High',
                    'CMP': 'Animo Compton Charter',
                    'AEO': 'Animo Ellen Ochoa Charter Middle',
                    'FLO': 'Animo Florence-Firestone Charter Middle',
                    'ING': 'Animo Inglewood Charter High',
                    'ROB': 'Animo Jackie Robinson High',
                    'JAM': 'Animo James B. Taylor Charter Middle',
                    'JMS': 'Animo Jefferson Charter Middle',
                    'LEA': 'Animo Leadership High',
                    'LGC': 'Animo Legacy Charter Middle',
                    'MAE': 'Animo Mae Jemison Charter Middle',
                    'BRW': 'Animo Pat Brown',
                    'BUN': 'Animo Ralph Bunche Charter High',
                    'SLA': 'Animo South Los Angeles Charter',
                    'VEN': 'Animo Venice Charter High',
                    'WAT': 'Animo Watts College Preparatory Academy',
                    'DLH': 'Oscar De La Hoya Animo Charter High'}

    # Create DataFrames
    df_ids = pd.DataFrame(list(school_ids.items()), columns=['Acronym', 'School_ID'])
    df_names = pd.DataFrame(list(school_names.items()), columns=['Acronym', 'School_Name'])

    # Merge DataFrames on the common 'Acronym'
    result_df = pd.merge(df_ids, df_names, on='Acronym')

    time.sleep(3)  #This is here so file_downloads can be regsitered properly

    # Get today's date
    today_date = datetime.now()
    # Format the month and day
    formatted_month_day = today_date.strftime("%m_%d_%y")

    dir_path = os.getcwd() + f'\\file_downloads\\{dir_path}'
    file_list = [file for file in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, file))]
    files = pd.DataFrame(file_list, columns = ['files'])
    files['files'] = files['files'].str[0:7]
    files['files'] = files['files'].astype(int).astype(str)  #remove leading zeros

    #merge them all together
    all_files = pd.merge(result_df, files, how='left',  left_on='School_ID', right_on='files')
    return(all_files)


def download_files(school_name, test_type, driver):
    
    print(school_name)

   # Find the element with the school name & the test_type
    school_element = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, f"//tr[td[text()='{test_type}' and following-sibling::td[text()='{school_name}']]]"))
    )

    try:                                                                                                           
        download_button = school_element.find_element(By.XPATH, './/input[contains(@class, "wcag_694 primarybtn left wcag_110")]')
        # Scroll into view
        ActionChains(driver).move_to_element(download_button).perform()
        logging.info(f'ActionChains scrolled to school {school_name}')

    except Exception as e:
        logging.info(f'Exception raised when downloading files {e}')

    # Click the Download button
    try:
        download_button.click()
        logging.info(f'Download occured for {school_name}')
    except Exception as e:
        logging.error(f'Error occurred for {school_name}: {str(e)}')
        pass



def download_process(what_schools, test_type, driver):
    driver.switch_to.default_content() #only has to happen on reruns technically

    for index, school_name in enumerate(what_schools):

        if index == 0:

            # Wait for the button to be clickable based on text
            Requested_Reports = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, f'//button[text()="Requested Reports"]'))
            )
            # Click the button
            try:
                Requested_Reports.click()
                logging.info('Requested reports section clicked into')
            except:
                pass
                logging.info('Requested reports did not get clicked into')


            try:
                WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "iframe.applicationContentFrame[style*='display: block']")))
                logging.info('Spinner has dissapeared on Requested Reports Page')
            except:
                logging.info('Spinner never dissapeared on Requested Reports Page')


            iframe = WebDriverWait(driver, 30).until(
                            EC.element_to_be_clickable((By.ID, 'theFrame'))
                            )

            try:
                driver.switch_to.frame(iframe)
                logging.info('Switched to iframe within downloads section')
            except:
                logging.info('Failed to switch to iframe within downloads section')
                pass
        else:
            pass

        download_files(school_name, test_type, driver)



def request_report_process(driver, test_type, Enrolled_or_Tested, actual_test, schools_list, SY):
    for idx, school_coord in enumerate(schools_list):
        
        if idx == 0 and test_type == 'SBAC':
            pass  #LCK is already selected as the initial for SBAC
        else:
            # Change login role for each school_coord
            change_login_role(school_coord, driver)
            logging.info(f'Switched to {school_coord}')
            print(school_coord)
        
        #See if this needs to be here
        reports = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="menu_Reports"]')))
        reports.click()
        
        # Call the function to request a report
        indicator = request_report(driver, test_type, Enrolled_or_Tested, actual_test, SY)
        logging.info(f'Here is the indicator {indicator}')
  
        if indicator == 'No files':
            logging.info('No files available for download request_report_process ended prematurely')
            return('No files')
        


def download_loop_missing(dir_path, test_type, driver, max_attempts=5):
    attempt_count = 0

    while attempt_count < max_attempts:
        files = whats_missing(dir_path)

        if files.loc[files['files'].isna()].empty:
            logging.info(f'All files are downloaded for {test_type}')
            print(f'All files are downloaded for {test_type}')
            break
        else:
            logging.info(f"These schools are missing {files.loc[files['files'].isna()]['School_Name'].values}")
            missing_frame = files.loc[files['files'].isna()]
            missing_schools = list(missing_frame['School_Name'])
            print(f'These schools are missing - {missing_schools}')

            try:
                download_process(missing_schools, test_type, driver)
            except Exception as e:
                print(e)

            attempt_count += 1

    if attempt_count == max_attempts:
        logging.warning(f"Max attempts ({max_attempts}) reached, some files are still missing")
        print(f"Max attempts ({max_attempts}) reached, some files are still missing")


def move_files_over():
    source_directory = os.getcwd() + f'\\file_downloads\\elpac\\{formatted_month_day}'
    destination_directory = os.getcwd() + f'\\file_downloads\\sbac\\{formatted_month_day}'

    print(source_directory)

    # List all files in the source directory
    files = os.listdir(source_directory)

    # Move each file to the destination directory
    for file in files:
        source_path = os.path.join(source_directory, file)
        destination_path = os.path.join(destination_directory, file)
        shutil.move(source_path, destination_path)

    logging.info(f'Files moved successfully to {destination_directory}')
    print(f"Files moved successfully to {destination_directory}.")


#This unzips individual files in the same dir. Then called in a loop under the func unzip_files_in_same_dir
def unzip_xlsx_file(zip_file, elpac_or_sbac):
    # Get the current working directory
    current_directory = os.getcwd()  + f'\\file_downloads\\{elpac_or_sbac}\\{formatted_month_day}'

    # Create the full path for the zip file
    zip_path = os.path.join(current_directory, zip_file)

    # Extract the first file with a '.xlsx' extension from the zip archive
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        xlsx_files = [f for f in zip_ref.namelist() if f.endswith('.xlsx')]

        if xlsx_files:
            xlsx_file_to_extract = xlsx_files[0]
            zip_ref.extract(xlsx_file_to_extract, current_directory)
            print(f"File '{xlsx_file_to_extract}' extracted from '{zip_file}'.")
        else:
            print("No .xlsx file found in the zip archive.")


def unzip_files_in_same_dir(elpac_or_sbac):

    files = os.listdir(os.getcwd()  + f'\\file_downloads\\{elpac_or_sbac}\\{formatted_month_day}')
    file_zips = [file for file in files if file.endswith('.zip')]

    for file in file_zips:
        unzip_xlsx_file(file, elpac_or_sbac)


def move_xlsx_files(elpac_or_sbac, formatted_month_day_year):
    
    destination_directory = r'P:\Knowledge Management\Ellevation\Data Sent 2023-24\State Testing' +  f"\\{elpac_or_sbac + '_' +  formatted_month_day_year}"
    # Ensure the destination directory exists, create it if not
    try:
        os.makedirs(destination_directory, exist_ok=True)
    except Exception as e:
        logging.CRITICAL(f'Unable to create dir {destination_directory} due to \n {e}')


    source_directory = os.getcwd() + f'\\file_downloads\\{elpac_or_sbac}\\{formatted_month_day_year}'

    # List all files in the source directory
    files = os.listdir(source_directory)

    # Filter files with '.xlsx' extension
    xlsx_files = [file for file in files if file.endswith('.xlsx')]

    # Move each '.xlsx' file to the destination directory
    for xlsx_file in xlsx_files:
        source_path = os.path.join(source_directory, xlsx_file)
        destination_path = os.path.join(destination_directory, xlsx_file)
        shutil.copy2(source_path, destination_path)
        print(f"Moved '{xlsx_file}' to '{destination_directory}'.")


def SBAC_package_func(driver, SY, Enrolled_or_Tested, formatted_month_day_year):

    indicator = request_report_process(driver, 'SBAC', Enrolled_or_Tested, 'CAASPP_Student_Score_Data_Extract_Report', caaspp_coordinators, SY)

    if indicator != 'No files':

    #if at any time there is a report that showed not available given date params. It ends the func and returns a string value of 'No files'
        try:                                   
            download_process(school_report_names, f'{SY} CAASPP Student Score Data File By {Enrolled_or_Tested} LEA', driver) 
        except TimeoutException:
            logging.info(f'CAASPP Student Score Data File by {Enrolled_or_Tested} LEA is not available for {SY}')
            return('No files')
    else:
        logging.info('No files to download within SBAC_package_func\n\n')

        return('No files')
    

    #This is here three times to see if anything got skipped the first time. Initial dir is set at ELPAC only to move the files over to SBAC dir
    #Will run 5 times

    time.sleep(10) #implemented to give time for files to download, removed pending tag
    download_loop_missing(f'elpac\\{formatted_month_day_year}', f'{SY} CAASPP Student Score Data File By {Enrolled_or_Tested} LEA', driver)

    #This moves the files from ELPAC  timestamp dir to SBAC timestamp dir. 
    #This is because the download dir cannot be changed in Selenium
    move_files_over()


def ELPAC_package_func(driver, SY, Enrolled_or_Tested, formatted_month_day_year):
    driver.switch_to.default_content() #switch out of iframe
    indicator = request_report_process(driver, 'ELPAC', Enrolled_or_Tested, 'Student_Results_Report_Student_Score_Data_Extract', elpac_coordinators, SY)

    if indicator != 'No files':

        try:
            download_process(school_report_names, f'{SY} Summative ELPAC and Summative Alternate ELPAC Student Score Data File By {Enrolled_or_Tested} LEA', driver) 
        except:    
            logging.info(f'ELPAC Student Score Data File by {Enrolled_or_Tested} LEA is not available for {SY}')
            return('No files')
    else:
        logging.info('No files to download within ELPAC_package_func\n\n')
        
        return('No files')

    time.sleep(10) #implemented to give time for files to download
    #This is here three times to see if anything got skipped the first time. 
    #Dir remains ELPAC for constant download directory
    download_loop_missing(f'elpac\\{formatted_month_day_year}', f'{SY} Summative ELPAC and Summative Alternate ELPAC Student Score Data File By {Enrolled_or_Tested} LEA', driver)

    #Close out driver window once done
    driver.close()



def unzip_move_and_unit(SBAC_ELPAC_output, test_name, formatted_month_day_year):
    if SBAC_ELPAC_output != 'No files':
        unzip_files_in_same_dir(test_name)

        #Keeps raw zip files in the same dir. Only moves over xlsx files
        try:
            move_xlsx_files(test_name, formatted_month_day_year)
            logging.info(f'Moved {test_name} XLSX files to p-drive')

            test_instance = TestFileProcessing() #unit test
            test_instance.test_file_processing(test_name)
        except:
            logging.info(f'Unable to move {test_name} XLSX files to the p-drive, must be connected to the VPN')
    else:
        return('No files')


#Coded out piece, used for manual checks.

# files = os.listdir(r'C:\Users\samuel.taylor\OneDrive - Green Dot Public Schools\Desktop\Git_Directory\ELPAC_SBAC_results_selenium\file_downloads\elpac\01_05')
# files = pd.DataFrame(files, columns = ['raw'])
# files['dupe'] = files['raw'].str[:7]
# files['dupe'] = files['dupe'].astype(str).str.lstrip('0')

# school_ids = {'CHA': '136119',
#                 'ING': '1996586',
#                 'LEA': '1996313',
#                 'DLH': '101675',
#                 'SLA': '102434',
#                 'VEN': '106831',
#                 'BRW': '106849',
#                 'BUN': '111575',
#                 'ROB': '111583',
#                 'LCK': '118588',
#                 'JMS': '122481',
#                 'AEO': '123992',
#                 'LGC': '124016',
#                 'MAE': '129270',
#                 'FLO': '134023',
#                 'WAT': '111625',
#                 'JAM': '124008',
#                 'CMP': '137984'}


# all_ = pd.DataFrame(list(school_ids.values()), columns = ['All Schools'])
# pd.merge(files, all_, left_on='dupe', right_on='All Schools', how = 'outer', indicator=True)

  

