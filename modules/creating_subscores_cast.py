from .post_download_change import assimilate_frames, insert_blanks_cols
from .sql_query_module import SQL_query
import pandas as pd


columns = [
    'RecordType',
    'Abbreviation',
    'schoolid',
    'MasterSchoolID',
    'StudentID',
    'SSID',
    'TestDate',
    'DisplayDate',
    'TestType',
    'TestPeriod',
    'TestSubjectGroup',
    'TestSubject',
    'TestName',
    'TestScoreType',
    'RawScore',
    'ScaleScore',
    'PLScore'
]




def melt_domains(frame):

    domains = ['Domain1Level', 'Domain2Level', 'Domain3Level']

    df = pd.melt(frame, id_vars=[col for col in frame.columns if col not in domains],
            value_vars=domains,
            var_name='DomainLevel',
            value_name='PLScoreLast')
    
    return(df)


def mapping(df):

    domain_mapping = {'Domain1Level': 'CAST - Life Sciences',
                'Domain2Level': 'CAST - Physical Sciences',
                'Domain3Level': 'CAST - Earth and Life Sciences'}

    df['TestSubject'] = df['DomainLevel'].map(domain_mapping)
    df['TestName'] = df['DomainLevel'].map(domain_mapping)

    #mapping
    TestScoreType_Decode = {
    'CAST - Overall': 'Test',
    'CAST - Life Sciences': 'Subscore',
    'CAST - Physical Sciences' : 'Subscore',
    'CAST - Earth and Life Sciences': 'Subscore'} #Earth and Space Sciences was prior

    pl_decode = {
    '1.0':'STNM',
    '2.0':'STNL',
    '3.0':'STMT',
    '4.0':'STEX'}

    df['PLScore'] = df['PLScore'].astype(str)

    df['TestScoreType'] = df['TestName'].map(TestScoreType_Decode)
    df['ProficiencyLevelCode'] = df['PLScore'].map(pl_decode)

    return(df)



def get_cast_subscores(df, testname):

    df = assimilate_frames(df, testname)
    df = insert_blanks_cols(df, testname)

    #Trim frame down to Science
    df = df.loc[(df['TestSubjectGroup'] == 6)]

    df['TestSubjectGroup'] = 'CAST' 
    df['TestSubject'] = df['TestSubjectGroup'] 
    df['TestName'] = df['TestSubjectGroup'] 
    df['RawScore'] = df['ScaleScore'].astype(str)
    df['RecordType'] = '06'
    df['TestScoreType'] = ''
    df['ProficiencyLevelCode'] = ''


    # #call sql query to re-organize cols
    cast_cols = SQL_query.get_cols_only('TestScores', 'CAS_Import', 90)
    cast_cols = list(cast_cols['COLUMN_NAME'])

    #Bring in domains specific to subscores
    domains = ['Domain1Level', 'Domain2Level', 'Domain3Level', 'RecordType']
    cast_cols.extend(domains)

    df = df[cast_cols]

    df = melt_domains(df)

    df = mapping(df)

    df = df.drop(columns=['PLScore'])

    df = df.rename(columns={'PLScoreLast': 'PLScore'})

    df = df[columns]

    df['RawScore'] = None
    df['ScaleScore'] = None

    return(df)





    #RawScore ScaleScore are Null
    #Melt down DomainLevels
    #Add in domain level columns to cast_cols list here 