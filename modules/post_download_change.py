import pandas as pd
import datetime
import numpy as np
import os
import logging
from .sql_query_module import SQL_query


decode_test_name = {
'OverallScaleScore': 'ELPAC-Overall', 
'OralLanguageScaleScore': 'ELPAC-Oral Language',
'WrittenLanguageScaleScore':'ELPAC-Writing',
'OverallPL': 'ELPAC-Overall',
'OralLanguagePL': 'ELPAC-Oral Language',
'WrittenLanguagePL': 'ELPAC-Written Language',    
'ListeningPL': 'ELPAC-Listening',
'SpeakingPL': 'ELPAC-Speaking',
'ReadingPL': 'ELPAC-Reading',
'WritingPL': 'ELPAC-Writing'
}



rename_cols = {'CALPADSDistrictName': 'Abbreviation',
                'CALPADSSchoolCode': 'schoolid',
                # 'MasterSchoolID': '' blank insert
                'LocalStudentID': 'studentnumber',
                # 'StudentID': '', blank insert
                'SSID' : 'SSID',

                'TestDate'	: 'TestDate', #inserted manually
                # 'DisplayDate': '', blank insert
                'TestType'	: 'TestType', #inserted manually
                'TestPeriod': 'TestPeriod', #inserted manually	
                'RecordType': 'TestSubjectGroup', #blank insert only on ELPAC
                # 'TestSubject : '' blank insert
                'GradeAssessed' : 'TestGradeLevel',
                'TestName': 'TestName', #decoded by the decode_test_name dictionary within ScaleScore & PLScore generation
                # 'TestScoreType': '' blank insert
                # 'RawScore' : '' blank insert
                'ScaleScore': 'ScaleScore', #generated in get_SS_frame 
                'PLScore': 'PLScore' #generate in get_PL_score
                #  'ProficiencyLevelCode': '' mapped in get_elpac_import based on the PLScore generation
                }

all_blanks = ['MasterSchoolID', 'StudentID', 'DisplayDate', 'TestSubjectGroup', 'TestSubject',  'RawScore', 'ProficiencyLevelCode']


def get_SS_frame(e_original):

    ss_columns = ['OverallScaleScore', 'OralLanguageScaleScore','WrittenLanguageScaleScore']
    remaining_columns = [col for col in e_original.columns if col not in ss_columns]
    e_scale_score = pd.melt(e_original, id_vars = remaining_columns, value_vars= ss_columns, value_name='ScaleScore')


    e_scale_score['TestName'] = e_scale_score['variable'].map(decode_test_name)
    e_scale_score = e_scale_score.drop(columns = ['OverallPL','OralLanguagePL','WrittenLanguagePL','ListeningPL','SpeakingPL','ReadingPL','WritingPL', 'variable'])

    return(e_scale_score)


def get_pl_frame(e_original):

    pl_columns = [ 'OverallPL','OralLanguagePL', 'WrittenLanguagePL', 'ListeningPL', 'SpeakingPL', 'ReadingPL', 'WritingPL']
    remaining_columns = [col for col in e_original.columns if col not in pl_columns]
    e_pl_score = pd.melt(e_original, id_vars = remaining_columns, value_vars= pl_columns, value_name='PLScore')

    e_pl_score['TestName'] = e_pl_score['variable'].map(decode_test_name)

    e_pl_score = e_pl_score.drop(columns = [ 'OverallScaleScore', 'OralLanguageScaleScore', 'WrittenLanguageScaleScore', 'variable'])

    return(e_pl_score)




def assimilate_frames(df, testname):


    #bring down the elpac frame to proper columns with renaming standards then pass that into the melting functions then bring the two together
    original = df.rename(columns = rename_cols)
    original['TestType'] = testname
    original['TestPeriod'] = 'SPR'
    original['TestDate'] = pd.to_datetime(datetime.date.today()) + pd.offsets.MonthEnd(0)

    scale_score = get_SS_frame(original) #melting down the scale score to be merged back together by SSID and TestName
    pl_score = get_pl_frame(original) #melting down the PL score to be merged back together by SSID and TestaName

    #The merge is occurs on testname, and SSID together. THis keeps rows unique
    output = pd.merge(pl_score, scale_score, left_on=['SSID', 'TestName'], right_on = ['SSID', 'TestName'], suffixes= ['', '_SS'], how='left')

    print(rename_cols.values())

    #cut down cols
    output = output[list(rename_cols.values())]

    return(output)




def get_elpac_import(df, testname):


    df = assimilate_frames(df, testname)

    
    pl_decode = {4.0: 'WelDev', 
    3.0: 'WelDev', 
    2.0: 'Som-ModDev',
    1.0: 'MinDev', 
    '': 'No Score', 
    'NS': 'No Score'}

    #PLScore is not showing for ELPAC import
    df['ProficiencyLevelCode'] = df['PLScore'].map(pl_decode)


    TestScoreType_Decode = {'ELPAC-Overall':'Test',
                            'ELPAC-Oral Language':'Subscore',
                            'ELPAC-Written Language':'Subscore',
                            'ELPAC-Listening':'Subscore',
                            'ELPAC-Speaking':'Subscore',
                            'ELPAC-Reading':'Subscore',
                            'ELPAC-Writing':'Subscore'}

    df['TestScoreType'] = df['TestName'].map(TestScoreType_Decode)

    # Insert blank columns
    for col_name in all_blanks:
        try:
            df.insert(loc=len(df.columns), column=col_name, value=None)
        except ValueError as e:
            print(e)


    #call sql query to re-organize cols
    elpac_cols = SQL_query.get_cols_only('TestScores', 'ELPAC_Import', 90)
    elpac_cols = list(elpac_cols['COLUMN_NAME'])

    df = df[elpac_cols]
    # "['TestSubject', 'RawScore'] not in index"

    return(df)






# -----------------------------SBAC section---------------------------------------------------

def get_sbac_import(df, testname):

    df = assimilate_frames(df, testname)

    # #pop TestSubjectGroup from the list because if differs from ELPAC. Alters the original list permamnently
    # all_blanks.remove('TestSubjectGroup')
    # all_blanks.remove('TestSubject')
    # all_blanks.remove('RawScore')
    # try except should bypass this

     # Insert blank columns
    for col_name in all_blanks:
        try:
            df.insert(loc=len(df.columns), column=col_name, value=None)
        except ValueError as e:
            print(e)

 
    
    # #Trim frame down to ELA & Match for SBAC
    df = df.loc[(df['TestSubjectGroup'] == 1) | (df['TestSubjectGroup'] == 2)]
    df['TestSubjectGroup'] = df['TestSubjectGroup'].map({1: 'ELA', 2: 'Math'}) 
    df['TestSubject'] = df['TestSubjectGroup'] + '- Overall'   
    df['TestName'] = 'SBAC - ' +  df['TestSubject'] 
    df['TestName'] = df['TestName'].str.replace(r'(ELA|Math)-', r'\1')
    df['RawScore'] = df['ScaleScore']
       
    #mapping
    TestScoreType_Decode = {'SBAC - Math Overall':'Test',
                            'SBAC - ELA Overall':'Test'}

    df['TestScoreType'] = df['TestName'].map(TestScoreType_Decode)


    # #call sql query to re-organize cols
    sbac_cols = SQL_query.get_cols_only('TestScores', 'SBAC_Import', 90)
    sbac_cols = list(sbac_cols['COLUMN_NAME'])

    df = df[sbac_cols]
    return(df)




def get_cast_import(df, testname):

    df = assimilate_frames(df, testname)

     # Insert blank columns
    for col_name in all_blanks:
        try:
            df.insert(loc=len(df.columns), column=col_name, value=None)
        except ValueError as e:
            print(e)


    #Trim frame down to Science
    df = df.loc[(df['TestSubjectGroup'] == 6)]
    df['TestSubjectGroup'] = 'Science'
    df['TestSubject'] = df['TestSubjectGroup'] + ' - Overall'
    df['TestName'] = 'CAST - Overall'
    df['RawScore'] = df['ScaleScore']
    df['TestDate'] = pd.to_datetime(datetime.date.today()) + pd.offsets.MonthEnd(0)

    #mapping
    TestScoreType_Decode = {'CAST - Overall': 'Test',
                            'CAST - Life Sciences': 'Subscore',
                            'CAST - Physical Sciences' : 'Subscore',
                            'CAST - Earth and Space Sciences': 'Subscore'}

    df['TestScoreType'] = df['TestName'].map(TestScoreType_Decode)

    
    # #call sql query to re-organize cols
    cast_cols = SQL_query.get_cols_only('TestScores', 'CAS_Import', 90)
    cast_cols = list(cast_cols['COLUMN_NAME'])
    df = df[cast_cols]

    return(df)

  




def send_stacked_csv(file, file_name, directory_path, formatted_month_day_year):
    stacked_dir = os.path.join(directory_path, 'Stacked_Files')
    os.makedirs(stacked_dir, exist_ok=True)  # Create directory if it doesn't exist

    file_path = os.path.join(stacked_dir, f'{file_name}_STACKED_{formatted_month_day_year}.csv')
    
    try:
        file.to_csv(file_path, index=False)
        logging.info(f'{file_name} sent to {file_path} for Ellevation pickup')
    except Exception as e:
        logging.error(f'Error sending {file_name} to {file_path}: {e}')


# ----------------------------------------Steps to get new records---------------------------------------


    # SSID if incoming files is int64
    #ScaleScore is a float64
    #Confirm this in db query

    #The query has NS and NaN inside the dw. Clean it up rather than catering to it. 
    #Write a unit test to ensure it.

    #ScaleScore is coming across as varchar(150) need to set it up to be a float in MS-SQL

    #Test out isin

    #elpac_clean has no zeros for ssid


class Clean:

    # query_cols = ['Abbreviation',  'StudentNumber', 'SSID', 'TestGrade', 'ELStatus', 'TestDate',
    # 'TestType', 'TestName', 'ScaleScore','PLScore', 'ProficiencyLevelCode']

    # blank_cols = ['SchoolID', 'MasterSchoolID', 'StudentID', 'DisplayDate', 'TestPeriod', 'TestScoreType']


    def __init__(self, file, file_name):
        self.file = file
        self.file_name = file_name


    def clean_up_rotating_file(self):

        #Filter down given file to prepare for a merge, get rid of blank cols
        # file = self.file[Clean.query_cols]

        clean_cols_float = ['ScaleScore', 'PLScore']

        for col in clean_cols_float:

            # Replace 'NS' and '' values with a NaN
            self.file[col] = self.file[col].replace(['NS', ''], np.nan)
            # Convert the column to float
            print(col)
            self.file[col] = self.file[col].astype(float)
           

        self.file['TestGradeLevel'] = self.file['TestGradeLevel'].astype(int)
        self.file['TestDate'] = pd.to_datetime(self.file['TestDate'])

        return(self.file)
    

#Comes after the File Clean, instantiate a Clean class within the function with file, clean the column dtypes, and return new records if any. 

def grab_new_records(file, file_name):

    file_obj = Clean(file, file_name) #This is going to need to have some exceptions based on each file
    file_obj_clean = file_obj.clean_up_rotating_file()

    #query can be done here & clean up rotating fil emaybe

    merging_cols = ['SSID', 'TestType', 'TestName', 'ScaleScore'] #These should work for all 3 files
    new_records = SQL_query.obtain_new(file_obj_clean, file_name, merging_cols)

    return(new_records)






#--------------------------------------Notes
#ELPAC
#Differing decoding method on ELPAC. Refer to message with Abi
# ss_decode = {4.0: 'WelDev', 
#                 3.0: 'ModDev', 
#                 2.0: 'SomDev',
#                 1.0: 'MinDev', 
#                 '': 'No Score', 
#                 'NS': 'No Score'}

#SBAC
#Missing PLScore Column and ProficiencyLevelCode Mapping
# PL Score 1	STNM
# PL Score 2	STNL
# PL Score 3	STMT
# PL Score 4	STEX

#CAST
# # PL Score 1	BLST
# # PL Score 2	ANST
# # PL Score 3	ABST




#Issue was that studentnumber is blank for sbac frame
#as confirmed studentnumber is good in elpac