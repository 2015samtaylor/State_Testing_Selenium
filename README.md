**README.md**

# Automated State Testing Data Retrieval and Processing

This Python script automates the retrieval and processing of state testing data for the ELPAC (English Language Proficiency Assessments for California) and SBAC (Smarter Balanced Assessment Consortium). The script utilizes Selenium for web automation to log in to the testing portal, request specific reports, and download the corresponding data files. Once file are downloaded as zip files, the necessary data is extracted stacked and strictly new records are appended to the tables ELPAC_Scores, SBAC_Scores, CAST_Scores

## Overview

- **Log In and Navigation:** The script begins by logging in to the testing portal and navigating to the home screen.

- **Directory Setup:** It creates a directory structure for file downloads based on the current date, differentiating between ELPAC and SBAC data.

- **Chrome Options:** Chrome options are set for Selenium to manage download preferences and establish a specific download directory.

- **Request and Download Process:**
  - **SBAC:** The script requests the 'CAASPP Student Score Data Extract Report' for CAASPP coordinators, then downloads and processes the data files.
  - **ELPAC:** It requests the 'Student Score Data Extract Report' for ELPAC coordinators, then downloads and processes the corresponding data files.

- **Download Loop for Missing Files:** A loop is implemented to reattempt downloading in case of any missing files.

- **Unzipping and File Movement:** The script unzips the downloaded files and moves the XLSX files to the 'P:\Knowledge Management\Ellevation\Data Sent 2023-24\State Testing' directory.

## Usage

1. **Dependencies Installation:**
   - Install the required dependencies using `pip install -r requirements.txt`.

2. **Configuration:**
   - Provide your credentials in the `config.py` file (username, password).
   - Ensure the ChromeDriverManager is installed using `pip install webdriver_manager`.

3. **Run the Script:**
   - Execute the script by running the main Python file.

4. **Output:**
   - The script logs its activities in 'ELPAC_SBAC_results.log'.
   - Downloaded files are stored in 'file_downloads' directory.
   - Unzipped and processed files are moved to 'P:\Knowledge Management\Ellevation\Data Sent 2023-24\State Testing'.

## Notes

- The script ensures that unique school names are considered when passing names into the requested reports.
- Directories are created dynamically based on the current date to organize downloaded files.

## Running Schedule

- 2022-23 Data
January 25
February 29
March 28
April 25
May 23
June 27
 
- 2023-24 Data
May 9
May 16
May 23
May 30
June 6
June 13
June 20
June 27


General Notes
Abbreviation - map on CALPADSDIstrictName
schoolid blank
MasterSchoolID blank
StudentNumber - LocalStudentId
StudentID blank
SSID - SSID
TestGrade - GradeAssessed
ELStatus Blank
TestDate - End of the month for the month uploaded
DisplayDate blank
testtype - 21 (General ELPAC) 23(ALT ELPAC)
testperiod blank
testscoretype blank
testname ListeningPL	SpeakingPL	ReadingPL	WritingPL 
scalescore and plscore melt down
proficiencylevelcode is hard mapping

How often do you need this done?
People dont start asking until end of the testing window, but want a monthly pull. As we lose enrollments of students, we lose access to their scores
#End of the month from Feb through May. Last day of Feb.

Prioritize ELPAC pulldowns are Feb-May. 
SBAC is April - June (mid) (End of April for SBAC/CAST)

CAST has recordtypes that are taken apart within the SBAC file. 

What table do they send it to?
ELPAC [TestScores].[dbo].[vw_rpt_ELPACScores]
CAST  [TestScores].[dbo].[CASTScores]
SBAC: ELA/Math [TestScores].[dbo].[vw_rpt_SBACScores]