import pyodbc
import sqlalchemy
from sqlalchemy import create_engine, VARCHAR
from sqlalchemy.types import VARCHAR as vc
import pandas as pd
import numpy as np
import urllib
import logging
from pandas.io.sql import DatabaseError

class SQL_query:

    quoted = urllib.parse.quote_plus("Driver={SQL Server Native Client 11.0};"
                     "Server=10.0.0.89;"
                     "Database=DataTeamSandbox;"
                     "Trusted_Connection=yes;")

    engine = sqlalchemy.create_engine('mssql+pyodbc:///?odbc_connect={}'.format(quoted))

    @staticmethod
    def SQL_query_89(query):
        odbc_name = 'GD_DW_89'
        conn = pyodbc.connect(f'DSN={odbc_name};')
        df_SQL = pd.read_sql_query(query, con = conn)
        return(df_SQL)
    
    @staticmethod
    def SQL_query_90(query):
        odbc_name = 'GD_DW'
        conn = pyodbc.connect(f'DSN={odbc_name};')
        df_SQL = pd.read_sql_query(query, con = conn)
        conn.close()
        return(df_SQL)
    

# ----------------------------------------------------Identifies what VARCHAR values are not long enough and fixes----------------------

    def update_varchar_lengths(df, dtypes): 
            # Function 1: Get longest string lengths for each column in existing frame
            def get_longest_string_lengths(dataframe):
                max_lengths_df = pd.DataFrame(columns=['Column', 'Max_Length']) #create empty frame
                #iterate over each column in df
                for column in dataframe.columns: 
                    data_type = dtypes.get(column)
                    if type(data_type) == type(vc()):
                        max_length = dataframe[column].apply(lambda x: len(str(x))).max()

                        if max_length == 0:  #If the column has nothing in it give it a default value of varchar 150
                            max_length = 150
                        else:
                            pass
                            

                        max_lengths_df = pd.concat([max_lengths_df, pd.DataFrame([{'Column': column, 'Max_Length': max_length}])], ignore_index=True)
                    else:
                        pass
                return(max_lengths_df)

            # Function 2: Create the dataframe to make the modifications on the VARCHAR lengths that are not long enough
            def identify_max_lengths_frame(lengths, dtypes):
                dtypes_frame = pd.DataFrame.from_dict(dtypes, orient='index', columns=['dtype'])
                dtypes_frame['dtype'] = dtypes_frame['dtype'].astype(str)
                df.index.name = 'Column'
                dtypes_frame[['Type', 'Length']] = dtypes_frame['dtype'].str.extract(r'([a-zA-Z]+)\((\d+)?\)', expand=True)
                dtypes_frame = dtypes_frame.merge(lengths, left_index=True, right_on='Column')
                dtypes_frame = dtypes_frame.fillna(0)
                dtypes_frame['Length'] = dtypes_frame['Length'].astype(int)
                dtypes_frame['Max_Length'] = dtypes_frame['Max_Length'].astype(int)
                changes = dtypes_frame.loc[(dtypes_frame['Length'] < dtypes_frame['Max_Length']) & (dtypes_frame['dtype'] != 'INTEGER')]
                changes['Max_Length'] = changes['Max_Length'].apply(lambda x: np.ceil(x / 10) * 10)
                changes['Max_Length'] = changes['Max_Length'].astype(int)
                return(changes)

            # Function 3: Declare varchar update lengths throuhg iteration then update the original dictionary
            def declare_varchar_update_lengths(changes, dtypes):
                for index, row in changes.iterrows():
                    column_name = row['Column']
                    max_length = int(row['Max_Length'])
                    sql_alchemy_type = VARCHAR
                    dtypes[column_name] = sql_alchemy_type(length=max_length)
                    print(f'{column_name} column being updated as VARCHAR({max_length})')


            # Call the functions sequentially,
            lengths = get_longest_string_lengths(df)
            changes = identify_max_lengths_frame(lengths, dtypes)
            declare_varchar_update_lengths(changes, dtypes)

    # -----------------------------------------------------------------
    @classmethod
    def get_dtypes(cls, db , table_name_89, existing_frame):

        out = cls.SQL_query_89('''
        SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH 
        FROM {}.information_schema.columns
        WHERE table_name = '{}'
        '''.format(db, table_name_89))

        dtypes = {}
        
        #gets column name, data type, char length into a dict
        for _, row in out.iterrows():
            column_name = row['COLUMN_NAME']
            data_type = row['DATA_TYPE']
            length = row['CHARACTER_MAXIMUM_LENGTH']
            if data_type == 'varchar' or data_type == 'nvarchar':
                dtypes[column_name] = sqlalchemy.types.VARCHAR(length=int(length))

                #Needs to be a sub function here



            elif data_type == 'int':
                dtypes[column_name] = sqlalchemy.types.Integer()
            elif data_type == 'bigint':
                dtypes[column_name] = sqlalchemy.types.BigInteger()
            elif data_type == 'float':
                dtypes[column_name] = sqlalchemy.types.Float()
            elif data_type == 'datetime':
                dtypes[column_name] = sqlalchemy.types.DateTime()
            elif data_type == 'char':
                dtypes[column_name] = sqlalchemy.types.CHAR(length=int(length))
        
        #add in the last_update column which is not present in tables on the 90
        dtypes.update({'last_update': sqlalchemy.types.VARCHAR(length = 10)})
        col_names = list(dtypes.keys())

        # Identifies what VARCHAR values are not long enough and fixes on first send only
        if existing_frame is not None:
            cls.update_varchar_lengths(existing_frame, dtypes)

        return(dtypes, col_names)
    
    
    @staticmethod
    def obtain_new(file, file_name, merging_cols):

        query = f'''
        SELECT * FROM DataTeamSandbox.dbo.{file_name}_Scores
        '''

        try:
            prior = SQL_query.SQL_query_89(query)
        except DatabaseError as e:                   
            print(f"Error: {e}")
            logging.info(f"The {file_name} does not exist or there is an issue with the SQL query. Returning current file as is")
            print(f"The {file_name} does not exist or there is an issue with the SQL query. Returning current file as is")
            return(file) 
            #If the table is not created, return the entire frame 


        # print(f'There is {len(prior)} prior rows in SQL table {file_name}_Scores before the full replace')
        # logging.info(f'There is {len(prior)} prior rows in SQL table {file_name}_Scores before the full replace')

        merged_df = pd.merge(prior, file, on=merging_cols, how='outer', indicator=True, suffixes=('_prior', '_file'))

        merge_counts = merged_df['_merge'].value_counts()
        logging.info(f'Merge counts for {file_name} \n {merge_counts}')

        #Right only grabs everyting coming from the incoming file
        new_records = merged_df.loc[merged_df['_merge'] == 'right_only']
        #drop the merge col
        new_records = new_records.drop('_merge', axis=1)

        #Subset the frame down to _file columns
        file_columns = [col for col in list(new_records.columns) if col.endswith("_file")]
        file_columns.extend(merging_cols)
        new_records = new_records[file_columns]

        #rename the columns to original convention
        column_mapping = {col: col.replace('_file', '') for col in new_records.columns}
        new_records = new_records.rename(columns=column_mapping)

        return(new_records)

    def get_cols_only(db, table_name, which_server):
        
            query = f'''
                    SELECT COLUMN_NAME
                    FROM {db}.INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = '{table_name}'
                    AND TABLE_SCHEMA = 'dbo';
                    '''
            if which_server == 90:
                cols = SQL_query.SQL_query_90(query)  
            
            elif which_server == 89:
                cols = SQL_query.SQL_query_89(query)  # Pass only the query string

            else:
                print('Issue with which_server var')

            return(cols)
    





#  # OBTAINING NEW RECORDS PROCESS
# # The master tables get a full replace with todays data files, however this does not occur until todays data files
# # is compared to the master tables. 

# #Whatever is strictly coming in on the merge from the new frame from these 4 columns will be sent to new scores table
# # ['SSID', 'TestType', 'TestName', 'PLScore']

#BEGINNING
#Obtain new function only works once initially because it looks for incoming records of the new file. 
#Master table is empty therefore, new table recieves all new records but no dtypes. If running again it will then receive nothing and get datatypes dropping records
#Work on dtypes to be solved at the beginning
#Workaround send the initial load as replace to both tables, then revert back to new_records as append, but solve dtypes