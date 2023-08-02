#External Libraries
import pandas as pd
import time
from datetime import datetime

#Internal Libraries
from connections import get_snowflake_connection

### function to check if customer code exists 
def check_c_codes(ccode):
    if ccode is None:
        ccode = ''
    c_string = "SELECT CUSTOMER_PARTY_CODE FROM ENTERPRISE_REFERENCE_DOMAIN.BROKER.REF_CUSTOMER WHERE CUSTOMER_PARTY_CODE = '" + ccode + "'"
    
    con = get_snowflake_connection() #create connection
    c_codes = pd.read_sql(c_string, con)

    con.close() #close connection

    if c_codes.empty:
        return False
    else:
        return True


### function to check if w-code exists
def check_w_codes(wcode):
    if wcode == '' or wcode == None:
        wcode = 'NULL'
    else:
        wcode = "'" + wcode + "'"


    wcode_string = '''
    SELECT ORIGIN_WAREHOUSE_CODE AS w_code
    FROM NAST_LTL_DOMAIN.BASE.LOADS l
    WHERE ORIGIN_WAREHOUSE_CODE = ''' + wcode + '''
    UNION 
    SELECT DESTINATION_WAREHOUSE_CODE
    FROM NAST_LTL_DOMAIN.BASE.LOADS l
    WHERE DESTINATION_WAREHOUSE_CODE = ''' + wcode + '''
    '''
    con = get_snowflake_connection() #create connection

    w_codes = pd.read_sql(wcode_string, con).dropna()

    con.close() #close connection

    if w_codes.empty:
        return False
    else:
        return True


### function to check if emp-code (seven lette) exists
def check_emp_codes(empcode):
    if empcode is None:
        empcode = ''
    emp_string = "SELECT SEVEN_LETTER FROM ENTERPRISE_REFERENCE_DOMAIN.BROKER.REF_WORKER WHERE SEVEN_LETTER ='" + empcode + "'"

    con = get_snowflake_connection()

    emp_codes = pd.read_sql(emp_string, con)

    con.close()

    if emp_codes.empty:
        return False
    else:
        return True
    

### function to check if quote exusts
def quote_already_exists(quote_id, quote_date):
    if quote_id is None:
        quote_id = ''

    if quote_date is None:
        quote_date = ''
    
    query_string = "SELECT QUOTE_ID FROM SANDBOX_NAST_LTL_DOMAIN.BASE.LMS_QUOTE WHERE QUOTE_ID = '{}' AND QUOTE_DATE = '{}'".format(quote_id, quote_date)

    print(query_string)

    con = get_snowflake_connection()

    quotes = pd.read_sql(query_string, con)

    con.close()

    if quotes.empty:
        return False
    else:
        return True


### function used to write to LMS_QUOTE_SCOPE
def write_to_lms_quote_scope(dataframe):
    con = get_snowflake_connection()
    table_name = 'SANDBOX_NAST_LTL_DOMAIN.BASE.LMS_QUOTE_SCOPE'

    # Create a new cursor
    cursor = con.cursor()
    
    # Generate a list of column names and a list of placeholder strings
    column_names = ','.join(dataframe.columns)
    placeholders = ','.join(['%s'] * len(dataframe.columns))
    
    # Build the INSERT INTO statement
    insert_stmt = f'INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})'
    print(insert_stmt)
    
    # Execute the INSERT INTO statement
    cursor.executemany(insert_stmt, dataframe.values.tolist())

    # Commit the transaction
    con.commit()

    # Close the connection
    con.close()


### function used to write to LMS_QUOTE_ITEMS
def write_to_lms_quote_items(dataframe):
    dataframe=configure_quote_items_dataframe(dataframe) # cleans data, see documentation below

    con = get_snowflake_connection()
    table_name = 'SANDBOX_NAST_LTL_DOMAIN.BASE.LMS_QUOTE_ITEMS'
    # Create a new cursor
    cursor = con.cursor()
    
    # Generate a list of column names and a list of placeholder strings
    column_names = ','.join(dataframe.columns)
    placeholders = ','.join(['%s'] * len(dataframe.columns))
    
    # Build the INSERT INTO statement
    insert_stmt = f'INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})'
    print(insert_stmt)
    
    # Execute the INSERT INTO statement
    cursor.executemany(insert_stmt, dataframe.values.tolist())

    # Commit the transaction
    con.commit()
    
    # Close the connection
    con.close()


### function used to clean data for LMS_QUOTE_ITEMS
### Data input example:
### QUOTE_ID    QUANTITY    WEIGHT      LENGTH
### temp1       2           40          50
###
### Output:
### QUOTE_ID    WEIGHT      LENGTH
### temp1       40          50
### temp1       40          50
def configure_quote_items_dataframe(dataframe):
    exploded_df = pd.DataFrame([
                                    row # select the full row
                                    for row in dataframe.to_dict(orient="records") # for each row in the dataframe
                                    for _ in range(int(row["QUANTITY"])) # and repeat the row for row["duration"] times
                                ])

    exploded_df = exploded_df.drop(columns=['QUANTITY'])

    return exploded_df


### function used to write to LMS_QUOTE
def write_to_lms_quote(dataframe):
    con = get_snowflake_connection()
    table_name = 'SANDBOX_NAST_LTL_DOMAIN.BASE.LMS_QUOTE'

    # Create a new cursor
    cursor = con.cursor()
    
    # Generate a list of column names and a list of placeholder strings
    column_names = ','.join(dataframe.columns)
    placeholders = ','.join(['%s'] * len(dataframe.columns))
    
    # Build the INSERT INTO statement
    insert_stmt = f'INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})'
    print(insert_stmt)
    
    # Execute the INSERT INTO statement
    cursor.executemany(insert_stmt, dataframe.values.tolist())

    # Commit the transaction
    con.commit()

    # Close the connection
    con.close()
