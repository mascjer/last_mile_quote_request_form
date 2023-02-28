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


def prettify_outputs(value):
    if isinstance(value, str):
        value = value.replace('_', ' ')
        value = string.capwords(value)
        return value
    else:
        return value


def prettify_df(df, trans_mode):
    if trans_mode== 'Air Expedite':
        df = df.drop(columns=['Pickup Scope', 'Delivery Scope'])
    elif trans_mode == 'Exclusive Use Vehicle':
        df = df.drop(columns=['Pickup Scope', 'Delivery Scope'])
    else:
        df = df.drop(columns=['Scope'])

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


def send_quote_email(request_df, item_df, scope_df, city, state):
    requestor = request_df['Seven Letter'][0] + '@chrobinson.com'
    scope_df = scope_df.drop(columns='INCLUDES_OTHER_SCOPE')
    request_df = request_df.applymap(lambda x: prettify_outputs(x))
    trans_mode = request_df['Transportation Mode'][0]
    recipient = determine_recipient(trans_mode)
    quote_id = item_df['QUOTE_ID'][0]


    request_df = prettify_df(request_df, trans_mode)
    scope_df = scope_df.applymap(lambda x: prettify_outputs(x))

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
    """.format(request_df.to_html(), item_df.to_html(index=False), scope_df.to_html(index=False))

    part1 = MIMEText(html, 'html')
    msg.attach(part1)


    msg["Subject"] = "{} Quote Request Form Submission Out of {}, {}, (Quote ID: {})".format(trans_mode, city, state, quote_id)
    msg["From"] = requestor
    msg["To"] = recipient
    msg['Cc'] = requestor
    msg['X-Priority'] = '1'

    smtp_obj = smtplib.SMTP("mail.chrobinson.com", 25)
    smtp_obj.sendmail(msg["From"], msg["To"], msg.as_string())
    smtp_obj.quit()


def send_warehousing_email(request_df):
    trans_mode = request_df['TRANSPORTATION_MODE'][0]
    recipient = determine_recipient(trans_mode)
    requestor = request_df['SEVEN_LETTER'][0] + '@chrobinson.com'
    quote_id = request_df['QUOTE_ID'][0]

    if trans_mode == 'first_mile':
        trans_mode = 'First Mile'
    elif trans_mode == 'final_mile':
        trans_mode = 'Final Mile'
    else:
        trans_mode = ''

    msg = MIMEMultipart()
    html = """\
    <html>
    <head>
    </head>
    <body>
        {0} is requesting a {1} warehousing quote request.
    </body>
    </html>
    """.format(requestor, trans_mode)

    part1 = MIMEText(html, 'html')
    msg.attach(part1)
            
    msg["Subject"] = "{} Warehousing Quote Request Form Submission, (Quote ID: {})".format(trans_mode, quote_id)
    msg["From"] = requestor
    msg["To"] = recipient
    msg['Cc'] = requestor

    smtp_obj = smtplib.SMTP("mail.chrobinson.com", 25)
    smtp_obj.sendmail(msg["From"], msg["To"], msg.as_string())
    smtp_obj.quit()