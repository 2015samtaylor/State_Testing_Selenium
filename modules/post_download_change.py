import pandas as pd
import datetime

def get_elpac_cols(df, testname):

    rename_cols = {'CALPADSDistrictName': 'Abbreviation',
                    'schoolID'	: 'SchoolID',
                    'MasterSchoolID' : '',
                    'LocalStudentID': 'StudentNumber', 	
                    'StudentID' : '',
                    'SSID' : 'SSID',
                    'GradeAssessed': 'TestGrade',
                    'testdate'	: '',
                    'displaydate': '',
                    'testtype'	: '',
                    'testperiod': '',	
                    'testscoretype'	: '',
                    'testname'	: '',
                    'scalescore' : '',	
                    'plscore'	: '',
                    'proficiencylevelcode': ''
    }

    df = df.rename(columns = rename_cols)

    insert_blanks = ['SchoolID', 'MasterSchoolID', 'StudentID', 'DisplayDate', 'TestType','TestDate', 'StudentID', 'DisplayDate', 'TestPeriod', 'TestScoreType']

    for column_name in insert_blanks:
        df[column_name] = ''

    df['TestType'] = testname

    df['TestDate'] = pd.to_datetime(datetime.date.today()) + pd.offsets.MonthEnd(0)

    subsidize_cols = ['Abbreviation', 'SchoolID', 'MasterSchoolID', 'StudentNumber', 'StudentID','SSID', 'TestGrade', 'ELStatus', 'TestDate', 'DisplayDate', 'TestType', 'TestPeriod', 'TestScoreType', 'OverallScaleScore', 'OralLanguageScaleScore' , 'WrittenLanguageScaleScore', 'OverallPL', 'OralLanguagePL', 'WrittenLanguagePL', 'ListeningPL', 'SpeakingPL', 'ReadingPL' , 'WritingPL' ]
    df = df[subsidize_cols]

    return(df)

# -----------------------------

def get_sbac_cols(df, testname):


    df = df.loc[(df['RecordType'] == 1) | (df['RecordType'] == 2)]

    print(df['RecordType'].unique())

    rename_cols = {'CALPADSDistrictName': 'Abbreviation',
                    'schoolID'	: 'SchoolID',
                    'MasterSchoolID' : '',
                    'LocalStudentID': 'StudentNumber', 	
                    'StudentID' : '',
                    'SSID' : 'SSID',
                    'GradeAssessed': 'TestGrade',
                    'testdate'	: '',
                    'displaydate': '',
                    'testtype'	: '',
                    'testperiod': '',	
                    'testscoretype'	: '',
                    'testname'	: '',
                    'scalescore' : '',	
                    'plscore'	: '',
                    'proficiencylevelcode': '',
                    'RecordType': 'TestSubjectGroup'
    }

    df = df.rename(columns = rename_cols)

    insert_blanks = ['SchoolID', 'MasterSchoolID', 'StudentID', 'DisplayDate', 'TestType','TestDate', 'StudentID', 'DisplayDate', 'TestPeriod', 'TestScoreType']

    for column_name in insert_blanks:
        df[column_name] = ''

    df['TestSubjectGroup'] = df['TestSubjectGroup'].map({1: 'ELA', 2: 'Math'})


    df['TestSubject'] = df['TestSubjectGroup'] + '- Overall'

    df['TestName'] = 'SBAC-' +  df['TestSubject'] 
    df['TestName'] = df['TestName'].str.replace(r'(ELA|Math)-', r'\1')


    df['AssessmentName'] = df.apply(lambda row: f"Grade {row['TestGrade']} {row['TestSubjectGroup']} Summative", axis=1)

    df['RawScore'] = df['ScaleScore']

    df['TestType'] = testname

    df['TestDate'] = pd.to_datetime(datetime.date.today()) + pd.offsets.MonthEnd(0)

    subsidize_cols = ['Abbreviation', 'SchoolID', 'MasterSchoolID',  'StudentID','SSID', 'TestDate', 'TestType',  'TestPeriod', 'TestSubjectGroup', 'TestSubject', 'TestGrade', 'TestName', 'TestScoreType', 'AssessmentName', 'RawScore', 'ScaleScore' ]
    df = df[subsidize_cols]


    return(df)





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



def get_SS_frame(e_original):

    ss_columns = ['OverallScaleScore', 'OralLanguageScaleScore','WrittenLanguageScaleScore']
    remaining_columns = [col for col in e_original.columns if col not in ss_columns]
    e_scale_score = pd.melt(e_original, id_vars = remaining_columns, value_vars= ss_columns, value_name='ScaleScore')


    e_scale_score['testname'] = e_scale_score['variable'].map(decode_test_name)
    e_scale_score = e_scale_score.drop(columns = ['OverallPL','OralLanguagePL','WrittenLanguagePL','ListeningPL','SpeakingPL','ReadingPL','WritingPL', 'variable'])

    return(e_scale_score)


def get_pl_frame(e_original):

    pl_columns = [ 'OverallPL','OralLanguagePL', 'WrittenLanguagePL', 'ListeningPL', 'SpeakingPL', 'ReadingPL', 'WritingPL']
    remaining_columns = [col for col in e_original.columns if col not in pl_columns]
    e_pl_score = pd.melt(e_original, id_vars = remaining_columns, value_vars= pl_columns, value_name='PLScore')

    e_pl_score['testname'] = e_pl_score['variable'].map(decode_test_name)

    e_pl_score = e_pl_score.drop(columns = [ 'OverallScaleScore', 'OralLanguageScaleScore', 'WrittenLanguageScaleScore', 'variable'])

    return(e_pl_score)



def get_cast_cols(df, testname):


    df = df.loc[ (df['RecordType'] == 6)]

    print(df['RecordType'].unique())

    rename_cols = {'CALPADSDistrictName': 'Abbreviation',
                    'schoolID'	: 'SchoolID',
                    'MasterSchoolID' : '',
                    'LocalStudentID': 'StudentNumber', 	
                    'StudentID' : '',
                    'SSID' : 'SSID',
                    'GradeAssessed': 'TestGrade',
                    'testdate'	: '',
                    'displaydate': '',
                    'testtype'	: '',
                    'testperiod': '',	
                    'testscoretype'	: '',
                    'testname'	: '',
                    'scalescore' : '',	
                    'plscore'	: '',
                    'proficiencylevelcode': '',
                    'RecordType': 'TestSubjectGroup'
    }

    df = df.rename(columns = rename_cols)

    insert_blanks = ['SchoolID', 'MasterSchoolID', 'StudentID', 'DisplayDate', 'TestType','TestDate', 'StudentID', 'DisplayDate', 'TestPeriod', 'TestScoreType']

    for column_name in insert_blanks:
        df[column_name] = ''

    df['TestSubjectGroup'] = 'Science'

    df['TestSubject'] = df['TestSubjectGroup'] + '- Overall'

    df['TestName'] = 'CAST-Overall'
    
    df['TestType'] = testname

    df['AssessmentName'] = df.apply(lambda row: f"Grade {row['TestGrade']} {row['TestType']}", axis=1)

    df['RawScore'] = df['ScaleScore']

    df['TestDate'] = pd.to_datetime(datetime.date.today()) + pd.offsets.MonthEnd(0)


    subsidize_cols = ['Abbreviation', 'SchoolID', 'MasterSchoolID',  'StudentID','SSID', 'TestDate', 'TestType',  'TestPeriod', 'TestSubjectGroup', 'TestSubject', 'TestGrade', 'TestName', 'TestScoreType', 'AssessmentName', 'RawScore', 'ScaleScore' ]
    df = df[subsidize_cols]

    return(df)

  

def get_elpac_import(elpac):

       e_original = get_elpac_cols(elpac, 'ELPAC')
       e_scale_score = get_SS_frame(e_original)
       e_pl_score = get_pl_frame(e_original)

       #The merge is occurs on testname, and SSID together. THis keeps rows unique
       e = pd.merge(e_pl_score, e_scale_score, left_on=['SSID', 'testname'], right_on = ['SSID', 'testname'], suffixes= ['', '_SS'], how='left')
       cols = list(e_pl_score.columns)
       cols.append('ScaleScore')

       #re-arrange order
       col_order = ['Abbreviation', 'SchoolID', 'MasterSchoolID', 'StudentNumber',
              'StudentID', 'SSID', 'TestGrade', 'ELStatus', 'TestDate', 'DisplayDate',
              'TestType', 'TestPeriod', 'TestScoreType',  'testname',
              'ScaleScore', 'PLScore']

       e = e[col_order]

       pl_decode = {4.0: 'WelDev', 
        3.0: 'WelDev', 
        2.0: 'Som-ModDev',
        1.0: 'MinDev', 
        '': 'No Score', 
        'NS': 'No Score'}

       e['ProficiencyLevelCode'] = e['PLScore'].map(pl_decode)

       return(e)

