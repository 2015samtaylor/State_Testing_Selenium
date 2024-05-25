#!/usr/bin/env python
# coding: utf-8

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoSuchWindowException
import logging
import os

 
def logIn(username, password, driver):
    driver.get('https://ca.tide.cambiumast.com/Common/DashBoard')
    driver.maximize_window()
    windowSize = driver.get_window_size()

    username_input = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, "username"))
    )
    username_input.send_keys(username)

    password_input = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, "password"))
    )
    password_input.send_keys(password)

    login_1 = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, "kc-login"))
    )
    login_1.click()

    try:
        emailcode = input('What is the Email code: ')
        # driver.find_element(By.ID, "emailcode").send_keys(emailcode)

        email_code_input = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, "emailcode"))
        )
        email_code_input.send_keys(emailcode)

        login_2 = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.ID, "kc-login"))
                )
        login_2.click()

        # driver.find_element(By.ID, 'kc-login').click()
        logging.info('Email Code submitted - {}'.format(emailcode))

    except Exception as e:
        print(e)



def launch_to_homescreen(driver):
    #click on image
    dropdown = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="uH-systemSwitcher"]/a/span/span'))
    )

    dropdown.click()

    TOMS_option = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="clsSubMenu"]/ul/li[1]/a'))
    )

    TOMS_option.click()

    initial_school = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="roleOrgSelect"]/option[2]'))
    )

    initial_school.click()

    logon = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="okButton"]'))
    )

    logon.click()



def create_directory(directory_path):
    # Convert the given path to an absolute path
    absolute_path = os.path.abspath(directory_path)

    if not os.path.exists(absolute_path):
        try:
            os.makedirs(absolute_path)
            print(f"Directory '{directory_path}' created successfully.")
            logging.info(f"Directory '{directory_path}' created successfully.")
        except OSError as e:
            print(f"Error creating directory '{directory_path}': {e}")
            logging.error(f"Error creating directory '{directory_path}': {e}")
    else:
        print(f"Directory '{directory_path}' already exists.")
        logging.info(f"Directory '{directory_path}' already exists.")




    

#Automated Login to Scrape Password
# import imaplib
# import email

# username = 'gdtestingcoordinator@greendot.org'

# imap_server = imaplib.IMAP4_SSL('imap-mail.outlook.com')

# # Login to the server
# imap_server.login(username, password)
