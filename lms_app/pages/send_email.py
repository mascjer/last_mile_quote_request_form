import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib
from dateutil import tz
import string
import urllib.parse
import os
from os.path import basename
import tempfile
import base64
import mimetypes
from typing import Optional

from database_functions import *
from pages.non_callback_functions import *
from pages.dataframe_builder import *
from pages.send_email import *


### removes _ and replaces with a space, capitalizes
### first letter of each word
def prettify_outputs(value):
    if isinstance(value, str):
        value = value.replace('_', ' ')
        value = string.capwords(value)
        return value
    else:
        return value


### makes df two columns, first column is the questions, the
### second column is the answers to those questions
def prettify_df(df, trans_mode):
    df = df.T
    df = df.dropna()

    new_header = df.iloc[0] #grab the first row for the header
    df = df[1:] #take the data less the header row
    df.columns = new_header #set the header row as the df header

    return df


### does the same as prettify values, but for pandas column names
def prettify_columns(df):
    """
    Renames Pandas DataFrame columns by replacing underscores with spaces and capitalizing the first letter of each word.
    """
    # Get the current column names
    current_columns = df.columns
    
    # Replace underscores with spaces and capitalize first letter of each word
    new_columns = [col.replace('_', ' ').title() for col in current_columns]
    
    # Rename the columns in the DataFrame
    df.columns = new_columns
    
    # Return the renamed DataFrame
    return df


### determines who the email is going to
def determine_recipient(trans_mode):
    print(trans_mode)
    if trans_mode == 'air_expedite':
        return 'Airdomestic@chrobinson.com'
    elif trans_mode == 'exclusive_use_vehicle':
        return 'Airdomestic@chrobinson.com'
    elif trans_mode == 'first_mile':
        return 'Lastmilequotes@chrobinson.com'
    elif trans_mode == 'final_mile':
        return 'Lastmilequotes@chrobinson.com'
    elif trans_mode == 'local_pick_and_delivery':
        return 'Lastmilequotes@chrobinson.com'
    else:
        return 'mascjer@chrobinson.com'


### removes the columns that include False by request of
### the business (Addtional Support, Line Down)
def remove_false_column(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    # check if the specified column contains any False values
    if False in df[column_name].values:
        # if so, remove the column from the dataframe
        df = df.drop(columns=[column_name])
    
    return df


### fixes dollar amounts
def format_as_dollar_amount(series: pd.Series) -> pd.Series:
    def format_amount(x: Optional[float]) -> str:
        if x is None:
            return None
        elif pd.isna(x):
            return None
        else:
            return '${:,.2f}'.format(x)
        
    return series.map(format_amount)


### sends the email for first or final mile
def send_quote_email(final_store, item_store, scope_store, additional_contacts, additional_cust_info):
    email_df = pd.DataFrame.from_dict([final_store])
    email_scope_df = pd.DataFrame.from_dict([scope_store])
    email_item_df = pd.DataFrame.from_dict(item_store)
    email_scope_df = explode_scope_data(email_scope_df)

    requestor = email_df['SEVEN_LETTER'][0] + '@chrobinson.com'
    trans_mode = email_df['TRANSPORTATION_MODE'][0]
    recipient = determine_recipient(trans_mode)
    quote_id = email_item_df['QUOTE_ID'][0]
    city = email_df['WAREHOUSE_CITY'][0]
    state = email_df['WAREHOUSE_STATE'][0]

    email_df = build_first_final_email(email_df, email_item_df, additional_contacts, additional_cust_info)

    email_df = prettify_df(email_df, trans_mode)

    email_scope_df = email_scope_df.drop(columns=['QUOTE_ID'])
    email_scope_df = replace_pd(email_scope_df)
    email_scope_df = email_scope_df.applymap(lambda x: prettify_outputs(x))
    email_item_df = email_item_df.drop(columns=['QUOTE_ID'])
    email_scope_df = prettify_columns(email_scope_df)
    email_item_df = prettify_columns(email_item_df)

    email(email_df, email_item_df, email_scope_df, recipient, requestor, trans_mode, city, state, quote_id)


### sends the email for air exp/euv
def send_air_euv_email(final_store, item_store, pick_scope_store, drop_scope_store, additional_contacts, 
                       pickup_additional_input, drop_additional_input, pick_open, pick_close, drop_open, drop_close):
    email_df = pd.DataFrame.from_dict([final_store])
    email_pick_scope_df = pd.DataFrame.from_dict([pick_scope_store])
    email_drop_scope_df = pd.DataFrame.from_dict([drop_scope_store])
    email_item_df = pd.DataFrame.from_dict(item_store)

    email_pick_scope_df = explode_scope_data(email_pick_scope_df)
    email_drop_scope_df = explode_scope_data(email_drop_scope_df)

    email_scope_df = pd.concat([email_pick_scope_df, email_drop_scope_df], ignore_index=True)

    requestor = email_df['SEVEN_LETTER'][0] + '@chrobinson.com'
    trans_mode = email_df['TRANSPORTATION_MODE'][0]
    recipient = determine_recipient(trans_mode)
    quote_id = email_item_df['QUOTE_ID'][0]
    city = email_df['ORIGIN_CITY'][0]
    state = email_df['ORIGIN_STATE'][0]

    email_df = build_air_email_df(email_df, email_item_df, pick_open, pick_close, drop_open, drop_close, 
                                    additional_contacts, pickup_additional_input, drop_additional_input)

    email_df = prettify_df(email_df, trans_mode)

    email_scope_df = email_scope_df.drop(columns=['QUOTE_ID'])
    email_scope_df = replace_pd(email_scope_df)
    email_scope_df = email_scope_df.applymap(lambda x: prettify_outputs(x))
    email_item_df = email_item_df.drop(columns=['QUOTE_ID'])
    email_scope_df = prettify_columns(email_scope_df)
    email_item_df = prettify_columns(email_item_df)

    email(email_df, email_item_df, email_scope_df, recipient, requestor, trans_mode, city, state, quote_id)


### sends the email for first AND final mile
def send_pd_quote_email(final_data_storage_display, item_storage, pick_scope_storage, drop_scope_storage, 
                                    additional_contacts, pick_additional_cust_info, drop_additional_cust_info, pick_local_time, drop_local_time):
    email_df = pd.DataFrame.from_dict([final_data_storage_display])
    email_pick_scope_df = pd.DataFrame.from_dict([pick_scope_storage])
    email_drop_scope_df = pd.DataFrame.from_dict([drop_scope_storage])
    email_item_df = pd.DataFrame.from_dict(item_storage)

    email_pick_scope_df = explode_scope_data(email_pick_scope_df)
    email_drop_scope_df = explode_scope_data(email_drop_scope_df)

    email_scope_df = pd.concat([email_pick_scope_df, email_drop_scope_df], ignore_index=True)

    requestor = email_df['SEVEN_LETTER'][0] + '@chrobinson.com'

    trans_mode = email_df['TRANSPORTATION_MODE'][0]
    recipient = determine_recipient(trans_mode)
    quote_id = email_item_df['QUOTE_ID'][0]
    city = email_df['PICKUP_WAREHOUSE_CITY'][0]
    state = email_df['PICKUP_WAREHOUSE_STATE'][0]

    email_df =  build_first_and_final_email(email_df, email_item_df, additional_contacts, pick_additional_cust_info, 
                                drop_additional_cust_info, pick_local_time, drop_local_time)

    email_df = prettify_df(email_df, trans_mode)
    email_scope_df = email_scope_df.drop(columns=['QUOTE_ID'])
    email_scope_df = replace_pd(email_scope_df)
    email_scope_df = email_scope_df.applymap(lambda x: prettify_outputs(x))
    email_item_df = email_item_df.drop(columns=['QUOTE_ID'])
    email_scope_df = prettify_columns(email_scope_df)
    email_item_df = prettify_columns(email_item_df)

    email(email_df, email_item_df, email_scope_df, recipient, requestor, trans_mode, city, state, quote_id)


### returns the total weight of the items in the item df
def total_weight(email_item_df):
    temp_item_df = email_item_df[['QUANTITY', 'WEIGHT']]
    temp_item_df['ROW_WEIGHT'] = temp_item_df['QUANTITY'].astype(float) * temp_item_df['WEIGHT'].astype(float)
    total_weight = temp_item_df['ROW_WEIGHT'].sum()

    total_weight_str = str(total_weight) + " lbs"
    return total_weight_str


### pretty self explainitory, for email df
def replace_bool(df):
    df = df.replace({True: 'Yes', False: 'No'})
    return df


### Replaces P/D in the email scope df with Pickup and Delivery
def replace_pd(df):
    df = df.replace({'P': 'Pickup', 'D': 'Delivery', 'first_final': 'First or Final'})
    return df


### builds/formats the air exp/euv email
def build_air_email_df(email_df, email_item_df, pick_open, pick_close, drop_open, drop_close, 
                       additional_contacts, pickup_additional_input, drop_additional_input):
    
    email_df['QUOTE_DATE'] = email_df['QUOTE_DATE'].apply(lambda x: convert_utc_to_central_string(pd.to_datetime(x)))
    email_df['ORIGIN_OPEN_TIME'][0] = pick_open
    email_df['ORIGIN_CLOSE_TIME'][0] = pick_close
    email_df['DESTINATION_OPEN_TIME'][0] = drop_open
    email_df['DESTINATION_CLOSE_TIME'][0] = drop_close

    email_df['TOTAL_WEIGHT'] = total_weight(email_item_df)

    email_df['ADDITIONAL_CONTACTS'] = additional_contacts
    email_df['ADDITIONAL_PICKUP_INFORMATION'] = pickup_additional_input
    email_df['ADDITIONAL_DELIVERY_INFORMATION'] = drop_additional_input

    email_df = email_df[['QUOTE_ID', 'TRANSPORTATION_MODE', 'SERVICE', 'CUSTOMER_CODE', 'SEVEN_LETTER', 'ADDITIONAL_CONTACTS',
                        'LOAD_NUM', 'QUOTE_OR_ON_HAND', 'ORIGIN_CITY', 'ORIGIN_STATE', 'ORIGIN_ZIP', 'REQUESTED_PICKUP_DATE',
                        'ADDITIONAL_PICKUP_INFORMATION', 'ORIGIN_OPEN_TIME', 'ORIGIN_CLOSE_TIME', 'DESTINATION_CITY',
                        'DESTINATION_STATE', 'DESTINATION_ZIP', 'REQUESTED_DELIVERY_DATE', 'ADDITIONAL_DELIVERY_INFORMATION',
                        'DESTINATION_OPEN_TIME', 'DESTINATION_CLOSE_TIME', 'IS_PALLETIZED', 'PACKAGING', 'IS_STACKABLE',
                        'ADDITIONAL_INSURANCE', 'VALUE', 'COMMODITY', 'IS_HAZ_MAT', 'UN_NUMBER', 'CLASS_NUMBER', 'PACKING_GROUP_NUMBER',
                        'CAUSE_LINE_DOWN', 'CAN_BREAKDOWN', 'TOTAL_WEIGHT', 'ADDITIONAL_SUPPORT_NEEDED', 'QUOTE_DATE']]
    
    email_df = remove_false_column(email_df, 'ADDITIONAL_SUPPORT_NEEDED')
    email_df = remove_false_column(email_df, 'CAUSE_LINE_DOWN')
    
    email_df = replace_bool(email_df)
    
    email_df['TRANSPORTATION_MODE'] = email_df['TRANSPORTATION_MODE'].apply(prettify_outputs)
    email_df['QUOTE_OR_ON_HAND'] = email_df['QUOTE_OR_ON_HAND'].apply(prettify_outputs)
    email_df['VALUE'] = format_as_dollar_amount(email_df['VALUE'])
    
    email_df = prettify_columns(email_df)

    email_df = email_df.rename(columns={
                                'Quote Id': 'Quote ID',
                                'Additional Contacts': 'Additional Seven-Letters/Email Groups',
                                'Load Num': 'Load Number',
                                'Quote Or On Hand': 'Quote Only Or Freight On Hand?',
                                'Is Palletized': 'Is Freight Palletized?',
                                'Packaging': 'If Not Palletized, How is Freight Packaged?',
                                'Is Stackable': 'Is Freight Stackable?',
                                'Additional Insurance':'Is Additional Insurance Needed?',
                                'Value':'If Additional Insurance Is Needed, What Is The Value?',
                                'Is Haz Mat' : 'Is Haz Mat?',
                                'Un Number' : 'If Haz Mat, What Is The UN #?',
                                'Class Number' : 'If Haz Mat, What Is The Class #?',
                                'Packing Group Number' : 'If Haz Mat, What Is The Packing Group #?',
                                'Cause Line Down' : 'Will A Delay Cause Line-Down Situation?',
                                'Can Breakdown': 'Can Freight Breakdown?'
                                })

    return email_df


### builds/formats the first or final email
def build_first_final_email(email_df, email_item_df, additional_contacts, additional_cust_info):
    email_df['QUOTE_DATE'] = email_df['QUOTE_DATE'].apply(lambda x: convert_utc_to_central_string(pd.to_datetime(x)))

    email_df['TOTAL_WEIGHT'] = total_weight(email_item_df)
    email_df['ADDITIONAL_CONTACTS'] = additional_contacts
    email_df['ADDITIONAL_DATE_INFORMATION'] = additional_cust_info

    email_df = email_df [['QUOTE_ID', 'TRANSPORTATION_MODE', 'SERVICE', 'CUSTOMER_CODE', 'SEVEN_LETTER','ADDITIONAL_CONTACTS',
                          'WAREHOUSE_CODE', 'WAREHOUSE_ADDRESS', 'WAREHOUSE_CITY', 'WAREHOUSE_STATE', 'WAREHOUSE_ZIP',
                          'CONTACT_NAME', 'CONTACT_PHONE', 'CONTACT_EMAIL', 'TIME_EXPECTATION', 'ADDITIONAL_DATE_INFORMATION',
                          'QUOTE_OR_ON_HAND', 'COMMODITY', 'IS_PALLETIZED', 'PACKAGING', 'IS_HAZ_MAT', 'UN_NUMBER', 'CLASS_NUMBER', 
                          'PACKING_GROUP_NUMBER', 'ADDITIONAL_INSURANCE', 'VALUE', 'FIRST_FLOOR_PICKUP', 'HAS_FREIGHT_ELEVATOR',
                          'TOTAL_WEIGHT', 'ADDITIONAL_SUPPORT_NEEDED', 'QUOTE_DATE']]
    
    email_df = remove_false_column(email_df, 'ADDITIONAL_SUPPORT_NEEDED')
    email_df = remove_false_column(email_df, 'ADDITIONAL_INSURANCE')
    email_df = remove_false_column(email_df, 'IS_HAZ_MAT')

    email_df = replace_bool(email_df)
    
    email_df['TRANSPORTATION_MODE'] = email_df['TRANSPORTATION_MODE'].apply(prettify_outputs)
    email_df['QUOTE_OR_ON_HAND'] = email_df['QUOTE_OR_ON_HAND'].apply(prettify_outputs)
    email_df['SERVICE'] = email_df['SERVICE'].apply(prettify_outputs)
    email_df['VALUE'] = format_as_dollar_amount(email_df['VALUE'])
    
    email_df = prettify_columns(email_df)

    email_df = email_df.rename(columns={
                                'Quote Id': 'Quote ID',
                                'Additional Contacts': 'Additional Seven-Letters/Email Groups',
                                'Quote Or On Hand': 'Quote Only Or Freight On Hand?',
                                'Is Palletized': 'Is Freight Palletized?',
                                'Packaging': 'If Not Palletized, How is Freight Packaged?',
                                'Is Stackable': 'Is Freight Stackable?',
                                'Additional Insurance':'Is Additional Insurance Needed?',
                                'Value':'If Additional Insurance Is Needed, What Is The Value?',
                                'Is Haz Mat' : 'Is Haz Mat?',
                                'Un Number' : 'If Haz Mat, What Is The UN #?',
                                'Class Number' : 'If Haz Mat, What Is The Class #?',
                                'Packing Group Number' : 'If Haz Mat, What Is The Packing Group #?',
                                'Time Expectation': 'Date or Time Expectation',
                                'First Floor Pickup': 'Is This A First Floor Pickup?',
                                'Has Freight Elevator': 'If Not First Floor Pickup, Is There a Freight Elevator?',
                                })


    return email_df


def build_first_and_final_email(email_df, email_item_df, additional_contacts, pick_additional_cust_info, 
                                drop_additional_cust_info, pick_local_time, drop_local_time):
    
    email_df['QUOTE_DATE'] = email_df['QUOTE_DATE'].apply(lambda x: convert_utc_to_central_string(pd.to_datetime(x)))
    email_df['TOTAL_WEIGHT'] = total_weight(email_item_df)

    email_df['ADDITIONAL_CONTACTS'] = additional_contacts
    email_df['PICKUP_ADDITIONAL_DATE_INFORMATION'] = pick_additional_cust_info
    email_df['DELIVERY_ADDITIONAL_DATE_INFORMATION'] = drop_additional_cust_info
    email_df['PICKUP_TIME_EXPECTATION_TIME'][0] = pick_local_time
    email_df['DELIVERY_TIME_EXPECTATION_TIME'][0] = drop_local_time

    email_df = email_df [['QUOTE_ID', 'TRANSPORTATION_MODE', 'SERVICE', 'CUSTOMER_CODE', 'SEVEN_LETTER','ADDITIONAL_CONTACTS',
                          'PICKUP_WAREHOUSE_CODE', 'PICKUP_WAREHOUSE_ADDRESS', 'PICKUP_WAREHOUSE_CITY', 'PICKUP_WAREHOUSE_STATE',
                          'PICKUP_WAREHOUSE_ZIP', 'PICKUP_CONTACT_NAME', 'PICKUP_CONTACT_PHONE', 'PICKUP_CONTACT_EMAIL',
                          'PICKUP_TIME_EXPECTATION', 'PICKUP_TIME_EXPECTATION_TIME','PICKUP_ADDITIONAL_DATE_INFORMATION', 
                          'DELIVERY_WAREHOUSE_CODE', 'DELIVERY_WAREHOUSE_ADDRESS', 'DELIVERY_WAREHOUSE_CITY', 'DELIVERY_WAREHOUSE_STATE', 
                          'DELIVERY_WAREHOUSE_ZIP', 'DELIVERY_CONTACT_NAME', 'DELIVERY_CONTACT_PHONE', 'DELIVERY_CONTACT_EMAIL',
                          'DELIVERY_TIME_EXPECTATION', 'DELIVERY_TIME_EXPECTATION_TIME', 'DELIVERY_ADDITIONAL_DATE_INFORMATION',
                          'QUOTE_OR_ON_HAND', 'COMMODITY', 'IS_PALLETIZED', 'PACKAGING', 'IS_HAZ_MAT', 'UN_NUMBER', 'CLASS_NUMBER', 
                          'PACKING_GROUP_NUMBER', 'ADDITIONAL_INSURANCE', 'VALUE', 'FIRST_FLOOR_PICKUP', 'PICKUP_HAS_FREIGHT_ELEVATOR',
                          'FIRST_FLOOR_DELIVERY', 'DELIVERY_HAS_FREIGHT_ELEVATOR','TOTAL_WEIGHT', 'ADDITIONAL_SUPPORT_NEEDED', 'QUOTE_DATE']]

    email_df = remove_false_column(email_df, 'ADDITIONAL_SUPPORT_NEEDED')
    email_df = remove_false_column(email_df, 'ADDITIONAL_INSURANCE')
    email_df = remove_false_column(email_df, 'IS_HAZ_MAT')

    email_df = replace_bool(email_df)

    email_df['TRANSPORTATION_MODE'] = email_df['TRANSPORTATION_MODE'].apply(prettify_outputs)
    email_df['QUOTE_OR_ON_HAND'] = email_df['QUOTE_OR_ON_HAND'].apply(prettify_outputs)
    email_df['SERVICE'] = email_df['SERVICE'].apply(prettify_outputs)
    email_df['PICKUP_TIME_EXPECTATION'] = email_df['PICKUP_TIME_EXPECTATION'].apply(prettify_outputs)
    email_df['DELIVERY_TIME_EXPECTATION'] = email_df['DELIVERY_TIME_EXPECTATION'].apply(prettify_outputs)
    email_df['VALUE'] = format_as_dollar_amount(email_df['VALUE'])

    email_df = prettify_columns(email_df)

    email_df = email_df.rename(columns={
                                'Quote Id': 'Quote ID',
                                'Additional Contacts': 'Additional Seven-Letters/Email Groups',
                                'Quote Or On Hand': 'Quote Only Or Freight On Hand?',
                                'Is Palletized': 'Is Freight Palletized?',
                                'Packaging': 'If Not Palletized, How is Freight Packaged?',
                                'Is Stackable': 'Is Freight Stackable?',
                                'Additional Insurance':'Is Additional Insurance Needed?',
                                'Value':'If Additional Insurance Is Needed, What Is The Value?',
                                'Is Haz Mat' : 'Is Haz Mat?',
                                'Un Number' : 'If Haz Mat, What Is The UN #?',
                                'Class Number' : 'If Haz Mat, What Is The Class #?',
                                'Packing Group Number' : 'If Haz Mat, What Is The Packing Group #?',
                                'Pickup Time Expectation': 'Pickup Date Expectation',
                                'Pickup Time Expectation Time': 'Pickup Time Expectation',
                                'Delivery Time Expectation': 'Delivery Date Expectation',
                                'Delivery Time Expectation Time': 'Delivery Time Expectation',
                                'First Floor Pickup': 'Is This A First Floor Pickup?',
                                'Pickup Has Freight Elevator': 'If Not First Floor Pickup, Is There A Freight Elevator?',
                                'First Floor Delivery': 'Is This A First Floor Delivery?',
                                'Delivery Has Freight Elevator': 'If Not First Floor Delivery, Is There A Freight Elevator?'
                                })

    return email_df



### sends the email
def email(email_df, email_item_df, email_scope_df, recipient, requestor, trans_mode, city, state, quote_id):
    msg = MIMEMultipart()
    html = """\
    <html>
    <head>
    </head>
    <body>
        Quote Request
        {0}
        Items
        {1}
        Scope
        {2}
    </body>
    </html>
    """.format(email_df.to_html(), email_item_df.to_html(index=False), email_scope_df.to_html(index=False))

    part1 = MIMEText(html, 'html')
    msg.attach(part1)

    recipients = [recipient,requestor]

    msg["Subject"] = "{} Quote Request Form Submission Out of {}, {} (Quote ID: {})".format(prettify_outputs(trans_mode), city, state, quote_id)
    msg["From"] = requestor
    msg["To"] = ", ".join(recipients)
    msg['X-Priority'] = '1'

    smtp_obj = smtplib.SMTP("mail.chrobinson.com", 25)
    smtp_obj.sendmail(msg["From"], msg["To"], msg.as_string())
    smtp_obj.quit()