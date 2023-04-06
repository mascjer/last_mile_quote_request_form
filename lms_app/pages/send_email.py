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

from database_functions import *
from pages.non_callback_functions import *
from pages.dataframe_builder import *
from pages.send_email import *



def prettify_outputs(value):
    if isinstance(value, str):
        value = value.replace('_', ' ')
        value = string.capwords(value)
        return value
    else:
        return value


def prettify_df(df, trans_mode):
    df = df.T
    df = df.dropna()

    new_header = df.iloc[0] #grab the first row for the header
    df = df[1:] #take the data less the header row
    df.columns = new_header #set the header row as the df header

    return df


def determine_recipient(trans_mode):
    if trans_mode == 'Air Expedite':
        return 'Airdomestic@chrobinson.com'
    elif trans_mode == 'Exclusive Use Vehicle':
        return '530EUV@chrobinson.com'
    elif trans_mode == 'First Mile':
        return 'Lastmilequotes@chrobinson.com'
    else:
        return 'Lastmilequotes@chrobinson.com'


def send_quote_email(final_store, item_store, scope_store, additional_contacts, additional_cust_info):

    email_df = pd.DataFrame.from_dict([final_store])
    email_scope_df = pd.DataFrame.from_dict([scope_store])
    email_item_df = pd.DataFrame.from_dict(item_store)

    email_scope_df = explode_scope_data(email_scope_df)

    requestor = email_df['SEVEN_LETTER'][0] + '@chrobinson.com'
    email_df = email_df.applymap(lambda x: prettify_outputs(x))
    trans_mode = email_df['TRANSPORTATION_MODE'][0]
    recipient = determine_recipient(trans_mode)
    quote_id = email_item_df['QUOTE_ID'][0]
    city = email_df['WAREHOUSE_CITY'][0]
    state = email_df['WAREHOUSE_STATE'][0]

    email_df['TOTAL_WEIGHT'] = total_weight(email_item_df)

    email_df['ADDITIONAL_CONTACTS'] = additional_contacts
    email_df['ADDITIONAL_DATE_INFORMATION'] = additional_cust_info

    email_df = prettify_df(email_df, trans_mode)
    email_scope_df = email_scope_df.applymap(lambda x: prettify_outputs(x))

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

    msg["Subject"] = "{} Quote Request Form Submission Out of {}, {}, (Quote ID: {})".format(trans_mode, city, state, quote_id)
    msg["From"] = requestor
    msg["To"] = ", ".join(recipients)
    msg['X-Priority'] = '1'

    smtp_obj = smtplib.SMTP("mail.chrobinson.com", 25)
    smtp_obj.sendmail(msg["From"], msg["To"], msg.as_string())
    smtp_obj.quit()


def send_air_euv_email(final_store, item_store, pick_scope_store, drop_scope_store, additional_contacts, pickup_additional_input, drop_additional_input):
    email_df = pd.DataFrame.from_dict([final_store])
    email_pick_scope_df = pd.DataFrame.from_dict([pick_scope_store])
    email_drop_scope_df = pd.DataFrame.from_dict([drop_scope_store])
    email_item_df = pd.DataFrame.from_dict(item_store)

    email_pick_scope_df = explode_scope_data(email_pick_scope_df)
    email_drop_scope_df = explode_scope_data(email_drop_scope_df)

    email_scope_df = pd.concat([email_pick_scope_df, email_drop_scope_df], ignore_index=True)

    requestor = email_df['SEVEN_LETTER'][0] + '@chrobinson.com'
    email_df = email_df.applymap(lambda x: prettify_outputs(x))
    trans_mode = email_df['TRANSPORTATION_MODE'][0]
    recipient = determine_recipient(trans_mode)
    quote_id = email_item_df['QUOTE_ID'][0]
    city = email_df['ORIGIN_CITY'][0]
    state = email_df['ORIGIN_STATE'][0]

    email_df['TOTAL_WEIGHT'] = total_weight(email_item_df)

    email_df['ADDITIONAL_CONTACTS'] = additional_contacts
    email_df['ADDITIONAL_PICKUP_INFORMATION'] = pickup_additional_input
    email_df['ADDITIONAL_DELIVERY_INFORMATION'] = drop_additional_input
    
    email_df = prettify_df(email_df, trans_mode)
    email_scope_df = email_scope_df.applymap(lambda x: prettify_outputs(x))

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

    msg["Subject"] = "{} Quote Request Form Submission Out of {}, {}, (Quote ID: {})".format(trans_mode, city, state, quote_id)
    msg["From"] = requestor
    msg["To"] = ", ".join(recipients)
    msg['X-Priority'] = '1'

    smtp_obj = smtplib.SMTP("mail.chrobinson.com", 25)
    smtp_obj.sendmail(msg["From"], msg["To"], msg.as_string())
    smtp_obj.quit()


def total_weight(email_item_df):
    temp_item_df = email_item_df[['QUANTITY', 'WEIGHT']]
    temp_item_df['ROW_WEIGHT'] = temp_item_df['QUANTITY'].astype(float) * temp_item_df['WEIGHT'].astype(float)
    total_weight = temp_item_df['ROW_WEIGHT'].sum()
    return total_weight