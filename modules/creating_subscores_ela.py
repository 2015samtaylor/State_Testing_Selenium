from .post_download_change import assimilate_frames, insert_blanks_cols
from .sql_query_module import SQL_query
import pandas as pd
from .creating_subscores_cast import columns


def melt_domains(frame, comp_or_PL):

    if comp_or_PL == 'PL':
        domains = ['SmarterCompClaim1PL','SmarterCompClaim2PL']
        value_name = 'PLScoreLast'
        var_name = 'CompClaimPL'

    elif comp_or_PL == 'Comp':
        domains = ['SmarterCompClaim1Score','SmarterCompClaim2Score']     
        value_name = 'RawScoreLast'  
        var_name = 'CompClaimRaw'


    elif comp_or_PL == 'WE':
        domains = ['WERPOR', 'WERDEVEEL', 'WERCOV']
        value_name = 'PLScoreWE'
        var_name = 'CompClaimRaw'


    df = pd.melt(frame, id_vars=[col for col in frame.columns if col not in domains],
            value_vars=domains,
            var_name=var_name,
            value_name=value_name)
    
    return(df)


def get_ela_subscores(df, testname):

    df = assimilate_frames(df, testname)
    df = insert_blanks_cols(df, testname)

     #Trim frame down to ELA for SBAC
    df = df.loc[(df['TestSubjectGroup'] == 1)] #1 is for ELA TestSubjectGroup and RecordType
    df['TestSubjectGroup'] = df['TestSubjectGroup'].map({1: 'ELA'}) 
    df['RecordType'] = '01'
    df['TestSubject'] = df['TestSubjectGroup'] + '- Overall'   
    df['TestName'] = 'SBAC - ' +  df['TestSubject'] 
    df['TestName'] = df['TestName'].str.replace(r'(ELA|Math)-', r'\1')
    df['RawScore'] = df['ScaleScore']
    df['PLScore'] = df['PLScore'].astype(str)
 
    df['TestScoreType'] = ''
    df['ProficiencyLevelCode'] = ''

    return(df)



def melt_special_ela(raw_df):

    #passing in raw frame. Then doing seperate melts followed by a merge. 
    #If double merge on the same frame, there will be unwanted rows. 


    t = melt_domains(raw_df, 'PL')
    t = t.rename(columns={'PLScoreLast': 'PLScore',
                          'CompClaimPL': 'Levels'})
    
    t_2 = melt_domains(raw_df, 'Comp')
    t_2 = t_2.rename(columns={'RawScoreLast': 'RawScore',
                              'CompClaimRaw': 'Levels'})
    
    merge_mapping = {'SmarterCompClaim1PL' : 'one',
                'SmarterCompClaim1Score' : 'one',
                'SmarterCompClaim2PL': 'two',
                'SmarterCompClaim2Score': 'two'}
    
    t['Levels'] = t['Levels'].map(merge_mapping)
    t_2['Levels'] = t_2['Levels'].map(merge_mapping)
    
    t_2 = t_2.drop(columns=['SmarterCompClaim1PL', 'SmarterCompClaim2PL'])
    t = t.drop(columns = ['SmarterCompClaim1Score',	'SmarterCompClaim2Score'])

    merged_df = pd.merge(t, t_2, on=['SSID', 'Levels'], how='left', suffixes=('', 'right'))
    merged_df = merged_df[[col for col in merged_df.columns if 'right' not in col]]

    return(merged_df)

    #SmarterCompClaim1Score	SmarterCompClaim2Score are not tehcnically needed after melting down PLs




def get_ela_subscores_read_write(df, test_name):

    df = get_ela_subscores(df, test_name)
  
    #call sql query to re-organize cols
    sbac_cols = SQL_query.get_cols_only('TestScores', 'SBAC_Import', 90)
    sbac_cols = list(sbac_cols['COLUMN_NAME'])

    #Bring in CompClaims specific to subscores
    comp_claims = ['SmarterCompClaim1Score', 'SmarterCompClaim1PL', 'SmarterCompClaim2Score', 'SmarterCompClaim2PL', 'RecordType']
    sbac_cols.extend(comp_claims)

    raw_df = df[sbac_cols]
    raw_df = raw_df.drop(columns=['PLScore','RawScore', 'ScaleScore'])

    df = melt_special_ela(raw_df)

    test_name = ''

    df = mapping(df, test_name)

    return(df)



def get_ela_subscores_essay(df, test_name):

    df = get_ela_subscores(df, test_name)
  
    #call sql query to re-organize cols
    sbac_cols = SQL_query.get_cols_only('TestScores', 'SBAC_Import', 90)
    sbac_cols = list(sbac_cols['COLUMN_NAME'])


    #Bring in CompClaims specific to subscores
    comp_claims = ['WERDEVEEL', 'WERCOV', 'WERPOR', 'RecordType', 'Genre']
    sbac_cols.extend(comp_claims)


    raw_df = df[sbac_cols]
    raw_df = raw_df.drop(columns=['PLScore','RawScore', 'ScaleScore'])

    df = melt_domains(raw_df, 'WE')

    df = df.rename(columns={ 'PLScoreWE': 'PLScore'}) 

    df['RawScore'] = None
    df['ScaleScore'] = None

    test_name = 'essay'

    df = mapping(df, test_name)

    return(df)



def mapping(df, test_name):
    
    essay_mapping = {'WERPOR' : 'SBAC ELA Essay - Organization and Purpose',
                'WERDEVEEL' : 'SBAC ELA Essay - Development/Evidence and Elaboration',
                'WERCOV' : 'SBAC ELA Essay - Conventions'}
    
    levels_mapping = {'one': 'SBAC ELA - Reading and Listening',
                      'two': 'SBAC ELA - Writing and Research'
                    }
    

    pl_decode = {1.0:'STNM',
                2.0:'STNL',
                3.0:'STMT',
                4.0:'STEX'}
    
    genre_mapping = {'EXPL': 'Explanatory Essay',
                 'ARGU': 'Argumentative Essay',
                 'NARR': 'Narrative',
                 '': 'Essay'}
    
    #Particular to read & write
    try:
        df['TestName'] = df['Levels'].map(levels_mapping)
    except KeyError:
        pass

    #Particular to essay
    try:
        df['TestName'] = df['CompClaimRaw'].map(essay_mapping)
    except KeyError:
        pass

    df['TestSubject'] = df['TestName']
    df['ScaleScore'] = df['RawScore']

    #One off for ELA subscores essay
    if test_name == 'essay':
        df['TestSubject'] = df['Genre'].map(genre_mapping)
    else:
        pass

    df['TestScoreType'] = 'Subscore'
    df['ProficiencyLevelCode'] = df['PLScore'].map(pl_decode)

    df = df[columns]

    return(df)