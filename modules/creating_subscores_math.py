from .post_download_change import assimilate_frames, insert_blanks_cols
from .sql_query_module import SQL_query
import pandas as pd
from .creating_subscores_cast import columns
from .creating_subscores_ela import melt_special_ela


def melt_domains(frame, comp_or_PL):

    if comp_or_PL == 'comp':
        domains = ['SmarterCompClaim1PL','SmarterCompClaim2PL']
        value_name = 'PLScoreLast'
        var_name = 'CompClaimPL'

    elif comp_or_PL == 'PL':
        domains = ['SmarterCompClaim1Score','SmarterCompClaim2Score']     
        value_name = 'RawScoreLast'  
        var_name = 'CompClaimRaw'

    df = pd.melt(frame, id_vars=[col for col in frame.columns if col not in domains],
            value_vars=domains,
            var_name=var_name,
            value_name=value_name)
    
    return(df)


def get_math_subscores(df, testname):

    df = assimilate_frames(df, testname)
    df = insert_blanks_cols(df, testname)

     #Trim frame down to Math for SBAC
    df = df.loc[(df['TestSubjectGroup'] == 2)]
    df['TestSubjectGroup'] = df['TestSubjectGroup'].map({2: 'Math'}) 
    df['RecordType'] = '02'
    df['TestSubject'] = df['TestSubjectGroup'] + '- Overall'   
    df['TestName'] = 'SBAC - ' +  df['TestSubject'] 
    df['TestName'] = df['TestName'].str.replace(r'(ELA|Math)-', r'\1')
    df['RawScore'] = df['ScaleScore']
    df['PLScore'] = df['PLScore'].astype(str)
    df['TestScoreType'] = ''
    df['ProficiencyLevelCode'] = ''

    return(df)


def get_math_subscores_concepts_communicating(df, testname):

    df = get_math_subscores(df,testname)
  
    #call sql query to re-organize cols
    sbac_cols = SQL_query.get_cols_only('TestScores', 'SBAC_Import', 90)
    sbac_cols = list(sbac_cols['COLUMN_NAME'])

    #Bring in CompClaims specific to subscores
    comp_claims = ['SmarterCompClaim1Score', 'SmarterCompClaim1PL', 'SmarterCompClaim2Score', 'SmarterCompClaim2PL', 'RecordType']
    sbac_cols.extend(comp_claims)

    raw_df = df[sbac_cols]
    raw_df = raw_df.drop(columns=['PLScore','RawScore', 'ScaleScore'])

    df = melt_special_ela(raw_df)
    df = mapping(df)

    return(df)



def mapping(df):
    
    
    levels_mapping = {'one': 'SBAC Math - Concepts and Procedures',
                      'two': 'SBAC Math - Problem Solving, Communicating Reasoning, and Modeling and Data Analysis'
                    }


    pl_decode = {
    1.0:'STNM',
    2.0:'STNL',
    3.0:'STMT',
    4.0:'STEX'}
    
    df['TestName'] = df['Levels'].map(levels_mapping)
    df['TestSubject'] = df['TestName']
    df['ScaleScore'] = df['RawScore']

    df['TestScoreType'] = 'Subscore'
    df['ProficiencyLevelCode'] = df['PLScore'].map(pl_decode)

    df = df[columns]

    return(df)