import pandas as pd
import datetime
import numpy as np
import os
import logging
from .sql_query_module import SQL_query


decode_test_name = {
'OverallScaleScore': 'ELPAC-Overall', 
'OverallPL': 'ELPAC-Overall',
'OralLanguageScaleScore': 'ELPAC-Oral Language',
'OralLanguagePL': 'ELPAC-Oral Language',
'WrittenLanguageScaleScore':'ELPAC-Written Language',
'WrittenLanguagePL': 'ELPAC-Written Language',    
'ListeningPL': 'ELPAC-Listening',
'SpeakingPL': 'ELPAC-Speaking',
'ReadingPL': 'ELPAC-Reading',
'WritingPL': 'ELPAC-Writing',
}


# So in other words the ScaleScore of ELPAC-Writing be matched up to the 'TestName'  ELPAC-Written Language rather than ELPAC-Writing
#This would result in the 'TestName' ELPAC-Writing with no ScaleScores and the 'TestName' ELPAC-Written Language would assume those ScaleScores. Does this sound right?

# oh got it yeah- I think it would be best practice to have nulls for scale score for ELPAC-Writing, ELPAC- Reading, ELPAC- Listening, and ELPAC Speaking

abbreviation_decode = {
'Animo Pat Brown': 'BRW',
'Animo Florence-Firestone Charter Middle': 'FLO',
'Alain Leroy Locke College Preparatory Academy': 'LCK',
'Animo Jefferson Charter Middle':'JMS',
'Animo Leadership High':'LEA',
'Animo Venice Charter High':'VEN',
'Oscar De La Hoya Animo Charter High':'DLH',
'Animo Ellen Ochoa Charter Middle':'AEO',
'Animo Jackie Robinson High':'ROB',
'Animo James B. Taylor Charter Middle': 'JAM',
'Animo South Los Angeles Charter':'SLA',
'Animo Ralph Bunche Charter High':'BUN',
'Animo Inglewood Charter High':'BUN',
'Animo Legacy Charter Middle':'LGC',
'Animo Mae Jemison Charter Middle':'MAE',
'Animo Compton Charter':'CMP',
'Animo City of Champions Charter High':'CHA',
'Animo Watts College Preparatory Academy':'WAT'
}



rename_cols = {
'CALPADSDistrictName': 'Abbreviation',
'CALPADSSchoolCode': 'schoolid',

'LocalStudentID': 'studentnumber', #blank insert only for SBAC

'SSID' : 'SSID',
'FinalTestCompletedDate':'TestDate', #allows TestDate to be transferred all the way. Due to assiliate frames

'TestType'	: 'TestType', #inserted manually
'TestPeriod': 'TestPeriod', #inserted manually	
'RecordType': 'TestSubjectGroup', #blank insert only on ELPAC

'GradeAssessed' : 'TestGradeLevel',
'ScaleScore': 'ScaleScore', #generated in get_SS_frame 
#'PLScore': 'PLScore', #generate in get_PL_score for ELPAC
'AchievementLevels': 'PLScore' #this is the PL_score column for SBAC

# 'MasterSchoolID': '' blank insert
# 'StudentID': '', blank insert
# 'DisplayDate': '', blank insert
# 'TestSubject : '' blank insert
# 'TestScoreType': '' blank insert
# 'RawScore' : '' blank insert
# 'ProficiencyLevelCode': '' mapped in get_elpac_import, get_sbac_import, get_cast_import based on the PLScore generation
}



def insert_blanks_cols(df, testname):

    all_blanks = ['MasterSchoolID', 'StudentID', 'DisplayDate']
    #TestSubject and TestName are creating in ELPAC through the melts

    # Insert blank columns beofre cutting down the cols. See if this is logical here
    for col_name in all_blanks:
        try:
            df.insert(loc=len(df.columns), column=col_name, value=None)
            logging.info(f'{col_name} inserted as a blank for {testname}')
        except ValueError as e:
            print(e)

    return(df)




def assimilate_frames(df, testname):


    #bring down the elpac frame to proper columns with renaming standards then pass that into the melting functions then bring the two together
    original = df.rename(columns = rename_cols)
    original['TestType'] = testname
    original['TestPeriod'] = 'SPR'
    #remove leading zero on the schoolid column, insert 3 letter abbreviation for schools
    original['schoolid'] = original['schoolid'].astype(str)

    original['schoolid'] = original['schoolid'].str.lstrip('0')
    original['Abbreviation'] = original['Abbreviation'].map(abbreviation_decode)

    # original['TestDate'] = pd.to_datetime(datetime.date.today()) + pd.offsets.MonthEnd(0)
    #Having TestDate be replaced with FinalTestCompletedDate
        
    return(original)


# -----------------------------SBAC section---------------------------------------------------

def get_sbac_import(df, testname):

    #get_pl_frame is not necessary for SBAC/CAST because AchievementLevels column functions as PLScore
    #get_SS_frame is also no necessary for SBAC/CAST because ScaleScore is already melted down

    df = assimilate_frames(df, testname)
    df = insert_blanks_cols(df, testname)


    # #Trim frame down to ELA & Math for SBAC
    df = df.loc[(df['TestSubjectGroup'] == 1) | (df['TestSubjectGroup'] == 2)]
    df['TestSubjectGroup'] = df['TestSubjectGroup'].map({1: 'ELA', 2: 'Math'}) 
    df['TestSubject'] = df['TestSubjectGroup'] + '- Overall'   
    df['TestName'] = 'SBAC - ' +  df['TestSubject'] 
    df['TestName'] = df['TestName'].str.replace(r'(ELA|Math)-', r'\1')
    df['RawScore'] = df['ScaleScore']
    df['PLScore'] = df['PLScore'].astype(str)
       
    #mapping
    TestScoreType_Decode = {
    'SBAC - Math Overall':'Test',
    'SBAC - ELA Overall':'Test'}

    pl_decode = {
    '1':'STNM',
    '2':'STNL',
    '3':'STMT',
    '4':'STEX'}

    df['TestScoreType'] = df['TestName'].map(TestScoreType_Decode)
    df['ProficiencyLevelCode'] = df['PLScore'].map(pl_decode)


    # #call sql query to re-organize cols
    sbac_cols = SQL_query.get_cols_only('TestScores', 'SBAC_Import', 90)
    sbac_cols = list(sbac_cols['COLUMN_NAME'])

    #temporary for sams enrolled request. 
    column_to_remove = 'studentnumber'

    # Create a new list without the specified column
    sbac_cols = [col for col in sbac_cols if col != column_to_remove]

    df = df[sbac_cols]

    return(df)




def get_cast_import(df, testname):
            
    #get_pl_frame is not necessary for SBAC/CAST because AchievementLevels column functions as PLScore
    #get_SS_frame is also no necessary for SBAC/CAST because ScaleScore is already melted down

    df = assimilate_frames(df, testname)
    df = insert_blanks_cols(df, testname)

    #Trim frame down to Science
    df = df.loc[(df['TestSubjectGroup'] == 6)]
    df['TestSubjectGroup'] = 'Science'
    df['TestSubject'] = df['TestSubjectGroup'] + ' - Overall'
    df['TestName'] = 'CAST - Overall'
    df['RawScore'] = df['ScaleScore']
    df['PLScore'] = df['PLScore'].astype(str)

    #mapping
    TestScoreType_Decode = {
    'CAST - Overall': 'Test',
    'CAST - Life Sciences': 'Subscore',
    'CAST - Physical Sciences' : 'Subscore',
    'CAST - Earth and Space Sciences': 'Subscore'}

    pl_decode = {
    '1':'STNM',
    '2':'STNL',
    '3':'STMT',
    '4':'STEX'}

    df['TestScoreType'] = df['TestName'].map(TestScoreType_Decode)
    df['ProficiencyLevelCode'] = df['PLScore'].map(pl_decode)

    # #call sql query to re-organize cols
    cast_cols = SQL_query.get_cols_only('TestScores', 'CAS_Import', 90)
    cast_cols = list(cast_cols['COLUMN_NAME'])

    #temporary for sams enrolled request. 
    column_to_remove = 'studentnumber'

    # Create a new list without the specified column
    cast_cols = [col for col in cast_cols if col != column_to_remove]

    df = df[cast_cols]

    return(df)

  



def get_SS_frame(e_original):

    #variable column is generated here. Columns are melted down, and variable becomes name of the ScaleScore column
    ss_columns = ['OverallScaleScore', 'OralLanguageScaleScore','WrittenLanguageScaleScore']
    remaining_columns = [col for col in e_original.columns if col not in ss_columns]
    e_scale_score = pd.melt(e_original, id_vars = remaining_columns, value_vars= ss_columns, value_name='ScaleScore')


    e_scale_score['TestName'] = e_scale_score['variable'].map(decode_test_name)
    # e_scale_score = e_scale_score.drop(columns = ['variable'])
    e_scale_score = e_scale_score.drop(columns = ['OverallPL','OralLanguagePL','WrittenLanguagePL','ListeningPL','SpeakingPL','ReadingPL','WritingPL', 'variable'])

    return(e_scale_score)


def get_PL_frame(e_original):

    pl_columns = [ 'OverallPL','OralLanguagePL', 'WrittenLanguagePL', 'ListeningPL', 'SpeakingPL', 'ReadingPL', 'WritingPL'] #For ELPAC raw file
    remaining_columns = [col for col in e_original.columns if col not in pl_columns]
    e_pl_score = pd.melt(e_original, id_vars = remaining_columns, value_vars= pl_columns, value_name='PLScore')

    e_pl_score['TestName'] = e_pl_score['variable'].map(decode_test_name)
    # e_pl_score = e_pl_score.drop(columns = [ 'variable'])

    e_pl_score = e_pl_score.drop(columns = [ 'OverallScaleScore', 'OralLanguageScaleScore', 'WrittenLanguageScaleScore', 'variable'])

    return(e_pl_score)


def map_proficiency_for_ELPAC(df):

    point_scale_4 = ['ELPAC-Overall', 'ELPAC-Oral Language', 'ELPAC-Written Language']
    point_scale_3 = ['ELPAC-Listening', 'ELPAC-Speaking', 'ELPAC-Writing', 'ELPAC-Reading']

    e_sub_4 = df[df['TestName'].isin(point_scale_4)]
    e_sub_3 = df[df['TestName'].isin(point_scale_3)]

    pl_decode_4_scale = {
    '4': 'WelDev', 
    '3': 'ModDev', 
    '2': 'Som-Dev',
    '1': 'MinDev', 
    '': 'No Score', 
    'NS': 'No Score'} 

    pl_decode_3_scale = {
    '3': 'WelDev', 
    '2': 'Som-ModDev',
    '1': 'MinDev', 
    '': 'No Score', 
    'NS': 'No Score'} 

    e_sub_4['ProficiencyLevelCode'] = e_sub_4['PLScore'].map(pl_decode_4_scale)
    e_sub_3['ProficiencyLevelCode'] = e_sub_3['PLScore'].map(pl_decode_3_scale)

    df = pd.concat([e_sub_4, e_sub_3], ignore_index=True)

    return(df)




def get_elpac_import(df, testname):

    #PLScore, and ScaleScores does not show for ELPAC import therefore must melt down certain columns. 
    df = assimilate_frames(df, testname)

    escale = get_SS_frame(df) #melting down the ScaleScore, and PLScore from raw frame to be merged back together by SSID and TestName
    epl = get_PL_frame(df)
    df = pd.merge(epl, escale, left_on=['SSID', 'TestName'], right_on = ['SSID', 'TestName'], suffixes= ['', '_SS'], how='left')

    # Insert blank columns beofre cutting down the cols. See if this is logical here
    df = insert_blanks_cols(df, testname)


    #No filter for TestSubjectGroup as it has all the TestSubjectGroups already
    df['TestSubjectGroup'] = 'ELPAC'
    df['TestSubject'] = 'ELA'
    df['RawScore'] = df['ScaleScore']
    df['PLScore'] = df['PLScore'].astype(str)

    df = map_proficiency_for_ELPAC(df)

    
    TestScoreType_Decode = {
    'ELPAC-Overall':'Test',
    'ELPAC-Oral Language':'Subscore',
    'ELPAC-Written Language':'Subscore',
    'ELPAC-Listening':'Subscore',
    'ELPAC-Speaking':'Subscore',
    'ELPAC-Reading':'Subscore',
    'ELPAC-Writing':'Subscore'}

    df['TestScoreType'] = df['TestName'].map(TestScoreType_Decode)

    
    #call sql query to re-organize cols
    elpac_cols = SQL_query.get_cols_only('TestScores', 'ELPAC_Import', 90)
    elpac_cols = list(elpac_cols['COLUMN_NAME'])
    df = df[elpac_cols]
  
    return(df)


# ----------------------------------------Steps to get new records---------------------------------------



def clean_up_rotating_file(file):


    clean_cols_float = ['ScaleScore', 'PLScore']

    for col in clean_cols_float:

        # Replace 'NS' and '' values with a NaN
        file[col] = file[col].replace(['NS', ''], np.nan)
        file[col] = file[col].astype(float)
        

    file['TestGradeLevel'] = file['TestGradeLevel'].astype(int)
    file['TestDate'] = pd.to_datetime(file['TestDate'])

    return(file)
    

#Comes after the File Clean, instantiate a Clean class within the function with file, clean the column dtypes, and return new records if any. 

def grab_new_records(file, file_name):

    file = clean_up_rotating_file(file)

    merging_cols = ['SSID', 'TestType', 'TestName', 'PLScore'] #These should work for all 3 files
    new_records = SQL_query.obtain_new(file, file_name, merging_cols)

    new_records['last_update'] = datetime.date.today().strftime('%Y-%m-%d')
    
    return(new_records)




def send_stacked_csv(file, file_name, formatted_month_day_year):

    stacked_dir = 'P:\Knowledge Management\Ellevation\Data Sent 2023-24\State Testing\Stacked_Files'

    try:
        os.makedirs(stacked_dir, exist_ok=True)  # Create directory if it doesn't exist
        logging.info(f'Directories created for {stacked_dir}')
    except:
        logging.info(f'Directories could not be created for {stacked_dir}')

    file_path = os.path.join(stacked_dir, f'{file_name}_STACKED_{formatted_month_day_year}.csv')
    
    try:
        file.to_csv(file_path, index=False)
        logging.info(f'{file_name} sent to {file_path} for Ellevation pickup')
    except Exception as e:
        logging.error(f'Error sending {file_name} to {file_path}: {e}')






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