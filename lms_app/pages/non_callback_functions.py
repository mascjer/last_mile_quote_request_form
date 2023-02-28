#for functions used on multiple pages
from datetime import datetime
import re
import pytz
import pandas as pd
import numpy as np
import time
from pages.dataframe_builder import *
from database_functions import *


### USED iN SHARED_CALLBACKS, AIR_EUV_CALLBACKS, FIRST_FINAL_CALLBACKS ###
def valid_input(value):
    if value is None:
        return False
    else:
        if type(value) == bool:
            if value == '':
                return False
            else:
                return True
        else:
            value = value.strip()
            if value == '':
                return False
            elif value is None:
                return False
            else:
                return True


### USED iN SHARED_CALLBACKS ###
def valid_numeric_input(value):
    if value is None:
        return False
    elif value == '':
        return False
    else:
        if value.isnumeric():
            return True
        else:
            return False


### USED iN SHARED_CALLBACKS ###
def create_false_list(quantity_exists, weight_exists, length_exists, width_exists, height_exists):
    false_list = []
    if quantity_exists == False:
        false_list.append('Quantity')
    if weight_exists == False:
        false_list.append('Weight')
    if length_exists == False:
        false_list.append('Length')
    if width_exists == False:
        false_list.append('Width')
    if height_exists == False:
        false_list.append('Height')

    return false_list


### USED AIR_EUV_CALLBACKS, FIRST_FiNAL_CALLBACKS ###
def parse_scopes(scope, other):
    scope_list = []
    if scope is not None:
        for i in range(len(scope)):
            item = scope[i]
            scope_list.append(item)

        if other is not None and 'Other' in scope:
            scope_list.append('Other: ' + other)
            scope_list.remove('Other')

        return scope_list

    else:
        return None


### USED AIR_EUV_CALLBACKS, FIRST_FINAL_CALLBACKS ###
def check_zip_code(S):

    if S is None:
        return False
    elif S == '':
        return False
    else:
        S = S.strip()
        if S =='':
            return False
        elif S is None:
            return False
        else:
            spaceless = S.replace(' ','')
            if not re.match('^(\d{5})([- ])?(\d{4})?$', spaceless):
                return False
            else:
                return True


### USED SHARED_CALLBACKS ###
def check_email_string(S):
    print(S)
    if S is None:
        return False
    elif S == '':
        return False
    else:
        S = S.strip()
        if S =='':
            return False
        elif S is None:
            return False
        else:
            spaceless = S.replace(' ','')
            if not re.match('[^@]+@[^@]+\.[^@]+', spaceless):
                return False
            else:
                return True


### USED AIR_EUV_CALLBACKS, FIRST_FINAL_CALLBACKS ###
def check_for_invalids(item_df):
    item_list = item_df.values.tolist()
    true_list = []
    for i in range(len(item_list)):
        t_f = '***Invalid***' in item_list[i]
        if t_f == True:
            true_list.append(i)
    
    if true_list:
        return True
    else:
        return False


### USED AIR_EUV_CALLBACKS, FIRST_FINAL_CALLBACKS ###
def wait_for_codes(request_df, ccode, empcode):
    if ccode == '':
        ccode = None
    if empcode == '':
        empcode = None

    if ccode is not None:
        ccode = ccode.upper()
    if empcode is not None:
        empcode = empcode.upper()

    ccode_set = request_df.CUSTOMER_CODE[0] == ccode
    empcode_set = request_df.SEVEN_LETTER[0] == empcode


    if ccode_set == True:
        if empcode_set == True:
            return request_df
        else:
            time.sleep(0.1)
            return wait_for_codes(send_request_df(), ccode, empcode)
    else:
        time.sleep(0.1)
        return wait_for_codes(send_request_df(), ccode, empcode)


### USED AIR_EUV_CALLBACKS ###
def create_date_strings(date, time, am_pm, timezone):
    str_fmt = '%Y-%m-%d %I:%M %p'
    date_str = date + ' ' + time + ' ' + am_pm

    date_str_obj = datetime.strptime(date_str, str_fmt)

    utc_date_str_obj = timezone_adjust(date_str_obj, timezone)

    return utc_date_str_obj


### USED AIR_EUV_CALLBACKS ###
def timezone_adjust(date_obj, timezone):
    tz = pytz.timezone(timezone)
    utc_tz = pytz.timezone('UTC')

    datetime = tz.localize(date_obj)

    utc_datetime = datetime.astimezone(utc_tz)

    return utc_datetime


### USED AIR_EUV_CALLBACKS ###
def create_time_false_list(time_exists, am_pm_exists, tz_exists):
    false_list = []

    if time_exists == False:
        false_list.append('Time')
    if am_pm_exists == False:
        false_list.append('AM/PM')
    if tz_exists == False:
        false_list.append('Timezone')

    return false_list


### USED FIRST_FiNAL_CALLBACKS ###
def check_phone_number(S):
    if S is None:
        return False
    elif S == '':
        return False
    else:
        S = S.strip()
        if S =='':
            return False
        elif S is None:
            return False
        else:
            spaceless = S.replace(' ','')
            if re.match('^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}$', spaceless):
                return True
            elif re.match('^[0-9]{10}$', spaceless):
                return True
            else:
                return False


### USED FIRST_FiNAL_CALLBACKS ###
def remove_false_others(scope_df):
    other_flag = 0
    other_entry = 0

    for i in range(len(scope_df)):
        scope = scope_df.scope.iloc[i]
        
        if scope == 'Other':
            other_flag = 1

        if 'Other: ' in scope:
            other_entry = 1

    if other_flag == 1 and other_entry == 1:
        scope_df = scope_df[scope_df.scope != 'Other']
    else:
        scope_df = scope_df[scope_df.scope != 'Other']
        scope_df = scope_df[scope_df.scope.str.contains('Other:') == False]

    return scope_df


### USED IN WAREHOUSING_CALLBACKS, FIRST_FINAL_CALLBACKS, AIR_EUV_CALLBACKS
def check_trans_mode_service(request_df):
    trans_mode = request_df['TRANSPORTATION_MODE'][0]

    if trans_mode is not None:
        if trans_mode == 'air_expedite' or trans_mode == 'exclusive_use_vehicle':
            return True
        else:
            service = request_df['SERVICE'][0]

            if service is not None:
                return True
            else:
                return False
    else:
        return False