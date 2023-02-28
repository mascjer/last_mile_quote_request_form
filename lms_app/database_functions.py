#External Libraries
import pandas as pd
import time
from datetime import datetime

#Internal Libraries
from connections import get_snowflake_connection


def check_c_codes(ccode):
    if ccode is None:
        ccode = ''
    c_string = "SELECT CUSTOMER_PARTY_CODE FROM SANDBOX_ENTERPRISE_REFERENCE_DOMAIN.BROKER.REF_CUSTOMER WHERE CUSTOMER_PARTY_CODE = '" + ccode + "'"
    c_codes = pd.read_sql(c_string, get_snowflake_connection())

    if c_codes.empty:
        return False
    else:
        return True


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

    w_codes = pd.read_sql(wcode_string, get_snowflake_connection()).dropna()

    if w_codes.empty:
        return False
    else:
        return True


def check_emp_codes(empcode):
    if empcode is None:
        empcode = ''
    emp_string = "SELECT SEVEN_LETTER FROM SANDBOX_ENTERPRISE_REFERENCE_DOMAIN.BROKER.REF_WORKER WHERE SEVEN_LETTER ='" + empcode + "'"
    emp_codes = pd.read_sql(emp_string, get_snowflake_connection())

    if emp_codes.empty:
        return False
    else:
        return True


def write_to_lms_quote_scope(dataframe):
    #dataframe=configure_dataframe_for_upload(dataframe)
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


def write_to_lms_quote_items(dataframe):
    dataframe=configure_quote_items_dataframe(dataframe)
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


def configure_quote_items_dataframe(dataframe):
    exploded_df = pd.DataFrame([
                                    row # select the full row
                                    for row in dataframe.to_dict(orient="records") # for each row in the dataframe
                                    for _ in range(int(row["QUANTITY"])) # and repeat the row for row["duration"] times
                                ])

    exploded_df = exploded_df.drop(columns=['QUANTITY'])

    return exploded_df


def write_to_lms_quote(dataframe):
    #dataframe=configure_dataframe_for_upload(dataframe)
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


def configure_dataframe_for_upload(dataframe):
    dataframe = dataframe.rename(columns ={
                                                        'Customer Code':'CUSTOMER_CODE',
                                                        'Warehouse Code':'WAREHOUSE_CODE',
                                                        'Fin Locked':'FIN_LOCKED',
                                                        'Load Status':'LOAD_STATUS',
                                                        'Start Date':'START_DATE',
                                                        'End Date':'END_DATE',
                                                        'Entered By':'ENTERED_BY',
                                                        'Entered Date':'ENTERED_DATE',
                                                        'Updated By':'UPDATED_BY',
                                                        'Updated Date':'UPDATED_DATE',
        })

    dataframe.WAREHOUSE_CODE.replace(to_replace = '', value = None , inplace=True)
    dataframe.FIN_LOCKED.replace(to_replace = '', value = 0, inplace=True)
    dataframe.LOAD_STATUS.replace(to_replace = '', value = None , inplace=True)
    dataframe.START_DATE.replace(to_replace = '', value = None, inplace=True)
    dataframe.END_DATE.replace(to_replace = '', value = None, inplace=True)

    return dataframe


def check_if_combo_exists(ccode, wcode):

    ccode = "'" + ccode + "'"
    if wcode == '':
        wcode = ' is NULL'
    else:
        wcode = " = '" + wcode + "'"

    string = "SELECT CUSTOMER_CODE, WAREHOUSE_CODE FROM SANDBOX_NAST_LTL_DOMAIN.BASE.LMS_CCODE_WCODE WHERE CUSTOMER_CODE = " + ccode + " AND WAREHOUSE_CODE" + wcode 
    codes = pd.read_sql(string, get_snowflake_connection())

    if codes.empty:
        return False
    else:
        return True


def create_new_quote_id():
    string = "SELECT max(QUOTE_ID) as QUOTE_ID FROM SANDBOX_NAST_LTL_DOMAIN.BASE.LMS_QUOTE"
    old_max_quote_id = pd.read_sql(string, get_snowflake_connection())

    old_max_quote_id = old_max_quote_id.iloc[0]['QUOTE_ID']

    if old_max_quote_id is None:
        old_max_quote_id = 0

    return old_max_quote_id + 1


def update_value(value, col, ccode, wcode, entered_by, entered_date, empcode):
    utc_time = datetime.utcnow()
    utc_time_string = utc_time.strftime('%Y-%m-%d %H:%M:%S')

    value = parse_main_insert(value)
    ccode = parse_entries(ccode)
    wcode = parse_entries(wcode)
    entered_by = parse_entries(entered_by)
    entered_date = parse_entries(entered_date)
    updated_by = parse_entries(empcode)
    updated_date = parse_entries(utc_time_string)

    string = f"UPDATE SANDBOX_NAST_LTL_DOMAIN.BASE.LMS_CCODE_WCODE SET {col} {value}, UPDATED_BY {updated_by}, UPDATED_DATE {updated_date} WHERE CUSTOMER_CODE {ccode} AND WAREHOUSE_CODE {wcode} AND ENTERED_BY {entered_by} AND ENTERED_DATE {entered_date}"
    print(string)
    pd.read_sql(string, get_snowflake_connection())


def parse_entries(value):
    if value is None:
        value = ' is NULL'
    elif value == True:
        value = ' = True'
    elif value == False:
        value = ' = False'
    else:
        value = " = '" + value + "'"
    
    return value


def parse_main_insert(value):
    if value is None:
        value = ' = NULL'
    elif value == True:
        value = ' = True'
    elif value == False:
        value = ' = False'
    else:
        value = " = '" + value + "'"
    
    return value
